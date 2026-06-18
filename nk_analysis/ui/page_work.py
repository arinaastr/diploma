import io
import copy
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTabWidget,
    QTableWidget, QPushButton, QScrollArea, QCheckBox,
)
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtCore import Qt

from nk_analysis.utils.constants import NAVY, BLUE, WHITE, SURFACE, BORDER, MUTED, MIN_PAIRS
OCEAN = NAVY
CREAM = WHITE
from nk_analysis.core.math_engine import build_calibration, calculate_strength, get_beton_class
from nk_analysis.core.chart import draw_scatter
from nk_analysis.ui.styles import make_label, make_section_label, setup_table, fill_table, CheckBox
from nk_analysis.ui.widgets import BottomBar

BTN = "background:#2C365A;color:#EEE8DF;font-weight:600;border-radius:4px;font-size:12px;border:none;padding:6px 18px;"

def _render_chart(cal, title):
    fig, ax = plt.subplots(figsize=(9, 4))
    draw_scatter(ax, fig, cal, title=title)
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=120, bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    img = QImage.fromData(buf.read())
    return QPixmap.fromImage(img)

def _cal_without_outliers(cal):
    df_clean = cal["df"][cal["mask"]].reset_index(drop=True)
    from nk_analysis.core.math_engine import build_calibration
    pairs_clean = df_clean.rename(columns={"V": "V", "f": "f"})[["V", "f"]]
    cal_clean = build_calibration(pairs_clean)
    return cal_clean if cal_clean else cal

class _CalibBlock(QWidget):

    def __init__(self, label, state_key_cal, state_key_dc, state):
        super().__init__()
        self.setStyleSheet(f"background:{WHITE};")
        self._state         = state
        self._state_key_cal = state_key_cal
        self._state_key_dc  = state_key_dc
        self._cal_original  = None
        self._df_full       = None
        self._data_cols     = None
        self._title         = None

        lay = QVBoxLayout(self)
        lay.setContentsMargins(16, 12, 16, 12)
        lay.setSpacing(8)

        lay.addWidget(make_label(label, big=True))

        self.lbl_formula = QLabel("—")
        self.lbl_formula.setStyleSheet("font-size:13px;font-family:monospace;background:transparent;")
        lay.addWidget(self.lbl_formula)

        stats_row = QHBoxLayout()
        for attr, caption in [("lbl_a","a"), ("lbl_b","b"), ("lbl_st","S, МПа"), ("lbl_r","r"), ("lbl_sr","S/R"), ("lbl_cls","Класс бетона")]:
            card = QWidget()
            card.setStyleSheet(f"background:{SURFACE};border:1px solid {BORDER};border-radius:8px;")
            cl = QVBoxLayout(card)
            cl.setContentsMargins(10, 6, 10, 6)
            vl = QLabel("—")
            vl.setStyleSheet(f"font-size:16px;font-weight:700;color:{OCEAN};background:transparent;")
            kl = QLabel(caption)
            kl.setStyleSheet(f"font-size:10px;color:{MUTED};background:transparent;")
            cl.addWidget(vl); cl.addWidget(kl)
            setattr(self, attr, vl)
            stats_row.addWidget(card)
        lay.addLayout(stats_row)

        self.lbl_invalid = QLabel("ВНИМАНИЕ: Градуировочная зависимость НЕ ДОПУСТИМА (r < 0.7 или S/R > 0.15). Контроль прочности по данной зависимости не допускается.")
        self.lbl_invalid.setStyleSheet("color:#8B1A1A;font-size:12px;font-weight:600;background:#FDECEA;border-radius:6px;padding:6px 10px;")
        self.lbl_invalid.setWordWrap(True)
        self.lbl_invalid.setVisible(False)
        lay.addWidget(self.lbl_invalid)

        self.chk_outliers = CheckBox("Убрать выбросы (пересчитать без них)")
        self.chk_outliers.setStyleSheet("font-size:12px;background:transparent;")
        self.chk_outliers.stateChanged.connect(self._on_outlier_toggle)
        lay.addWidget(self.chk_outliers)

        self.lbl_chart = QLabel()
        self.lbl_chart.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_chart.setMinimumHeight(260)
        lay.addWidget(self.lbl_chart)

        lay.addWidget(make_section_label("Итерации отбраковки"))
        self.tbl_iters = QTableWidget()
        self.tbl_iters.setMaximumHeight(120)
        setup_table(self.tbl_iters)
        lay.addWidget(self.tbl_iters)

        lay.addWidget(make_section_label("Прочность по элементам"))
        self.tbl_data = QTableWidget()
        self.tbl_data.setMinimumHeight(180)
        setup_table(self.tbl_data)
        lay.addWidget(self.tbl_data)

        self.lbl_no_data = QLabel("Недостаточно данных для расчёта.")
        self.lbl_no_data.setStyleSheet(f"color:{MUTED};font-size:12px;background:transparent;")
        lay.addWidget(self.lbl_no_data)
        self.lbl_no_data.setVisible(False)

    def _on_outlier_toggle(self):
        if self._cal_original is None:
            return
        if self.chk_outliers.isChecked():
            cal = _cal_without_outliers(self._cal_original)
        else:
            cal = self._cal_original
        self._state[self._state_key_cal] = cal
        self._display(cal)

    def _display(self, cal):
        a0, a1 = cal["a0"], cal["a1"]
        b_str = f"+ {a0:.3f}" if a0 >= 0 else f"- {abs(a0):.3f}"
        self.lbl_formula.setText(f"R  =  {a1:.5f} · V  {b_str}")
        self.lbl_a.setText(str(round(a1, 5)))
        self.lbl_b.setText(str(round(a0, 3)))
        self.lbl_r.setText(str(round(cal["r"],  4)))
        self.lbl_st.setText(str(round(cal["S_T"], 3)))
        sr = cal.get("sr", float("nan"))
        self.lbl_sr.setText("—" if (sr != sr) else str(round(sr, 4)))  # NaN check

        sub = cal["df"][cal["mask"]]
        rm = (a0 + a1 * sub["V"]).mean() if len(sub) else float("nan")
        self.lbl_cls.setText(get_beton_class(rm))

        is_valid = cal.get("valid", True)
        self.lbl_invalid.setVisible(not is_valid)

        px = _render_chart(cal, self._title)
        self.lbl_chart.setPixmap(
            px.scaled(self.lbl_chart.width() or 800, 300,
                      Qt.AspectRatioMode.KeepAspectRatio,
                      Qt.TransformationMode.SmoothTransformation)
        )

        if cal["iters"]:
            fill_table(self.tbl_iters, pd.DataFrame(cal["iters"]))

        if self._df_full is not None and len(self._df_full):
            dc = calculate_strength(self._df_full, cal["a0"], cal["a1"])
            self._state[self._state_key_dc] = dc
            cols = [c for c in self._data_cols if c in dc.columns]
            fill_table(self.tbl_data, dc[cols])

    def load(self, cal, df_full, data_cols, chart_title):
        self._cal_original = cal
        self._df_full      = df_full
        self._data_cols    = data_cols
        self._title        = chart_title
        self.chk_outliers.blockSignals(True)
        self.chk_outliers.setChecked(False)
        self.chk_outliers.blockSignals(False)

        if cal is None:
            self.lbl_no_data.setVisible(True)
            return
        self.lbl_no_data.setVisible(False)
        self._display(cal)

class WorkPage(QWidget):

    def __init__(self, state, on_back=None, on_next=None):
        super().__init__()
        self.state = state

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)

        inner = QWidget()
        inner.setStyleSheet(f"background:{WHITE};")
        lay = QVBoxLayout(inner)
        lay.setContentsMargins(24, 16, 24, 12)
        lay.setSpacing(12)

        lay.addWidget(make_label("Расчёт и анализ", big=True))

        tabs = QTabWidget()
        self.block_s = _CalibBlock("Ствол",     "cal_s", "dc_stvol", state)
        self.block_n = _CalibBlock("Конструкция",  "cal_n", "dc_ne",    state)
        tabs.addTab(self.block_s, "Ствол")
        tabs.addTab(self.block_n, "Конструкция")
        lay.addWidget(tabs)

        scroll.setWidget(inner)
        root.addWidget(scroll, stretch=1)
        root.addWidget(BottomBar(on_back=on_back, on_next=on_next))

    def refresh(self):
        ps = self.state.get("pairs_stvol", pd.DataFrame())
        pn = self.state.get("pairs_ne",    pd.DataFrame())
        ds = self.state.get("ds",          pd.DataFrame())
        dn = self.state.get("dn",          pd.DataFrame())

        cal_s = build_calibration(ps) if len(ps) >= MIN_PAIRS else None
        cal_n = build_calibration(pn) if len(pn) >= MIN_PAIRS else None

        self.state["cal_s"] = cal_s
        self.state["cal_n"] = cal_n

        if cal_s and len(ds):
            self.state["dc_stvol"] = calculate_strength(ds, cal_s["a0"], cal_s["a1"])
        if cal_n and len(dn):
            self.state["dc_ne"] = calculate_strength(dn, cal_n["a0"], cal_n["a1"])

        cols_s = ["Горизонт", "Сторона", "V", "f_МО", "f_расч МПа", "Класс", "Статус"]
        cols_n = ["Участок", "V", "f_МО", "f_расч МПа", "Класс", "Статус"]

        self.block_s.load(cal_s, ds, cols_s, "Градуировочная зависимость — Ствол")
        self.block_n.load(cal_n, dn, cols_n, "Градуировочная зависимость — Конструкция")
