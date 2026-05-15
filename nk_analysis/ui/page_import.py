# Экран 1 — Импорт данных

import os
import pandas as pd

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton,
    QTableWidget, QComboBox, QLabel, QFileDialog, QMessageBox,
    QTabWidget, QScrollArea,
)
from PyQt6.QtCore import Qt

from nk_analysis.utils.constants import CREAM, OCEAN, WHITE, MUTED, OK_FG, BORDER, MIN_PAIRS
from nk_analysis.core.excel_import import load_all_files
from nk_analysis.ui.styles import (
    make_label, make_field_label, make_section_label,
    make_metric, setup_table, fill_table,
)

BETON_CLASS_LIST = [
    "B5", "B7.5", "B10", "B12.5", "B15", "B17.5", "B20", "B22.5",
    "B25", "B27.5", "B30", "B35", "B40", "B45", "B50", "B60",
]


class ImportPage(QWidget):

    def __init__(self, state, on_next=None):
        super().__init__()
        self.state   = state
        self.on_next = on_next

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Прокручиваемая область
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        inner = QWidget()
        inner.setStyleSheet(f"background:{CREAM};")
        lay = QVBoxLayout(inner)
        lay.setContentsMargins(28, 16, 28, 16)
        lay.setSpacing(8)

        lay.addWidget(make_label("Импорт данных", big=True))
        lay.addWidget(make_label(
            "Загрузите .xlsx файлы. Данные «Ствол» и «Не ствол» обрабатываются раздельно.",
            muted=True,
        ))

        # Файлы
        lay.addWidget(make_section_label("Файлы данных"))
        self.btn_load = QPushButton("Выбрать файлы…")
        self.btn_load.setFixedHeight(34)
        self.btn_load.setStyleSheet("background:#2C365A;color:#EEE8DF;font-weight:600;border-radius:4px;font-size:12px;border:none;padding:6px 18px;")
        self.btn_load.clicked.connect(self._load_files)
        lay.addWidget(self.btn_load)
        self.lbl_files = QLabel("Файлы не выбраны")
        self.lbl_files.setStyleSheet(f"font-size:12px;color:{MUTED};background:transparent;")
        lay.addWidget(self.lbl_files)

        # Реквизиты
        lay.addWidget(make_section_label("Реквизиты объекта"))

        def add_row(label_text, widget):
            r = QHBoxLayout()
            lbl = make_field_label(label_text)
            lbl.setFixedWidth(170)
            r.addWidget(lbl)
            r.addWidget(widget)
            lay.addLayout(r)

        self.f_num    = QLineEdit(); self.f_num.setPlaceholderText("Например: 01/2026")
        self.f_obj    = QLineEdit(); self.f_obj.setPlaceholderText("Наименование объекта")
        self.f_addr   = QLineEdit(); self.f_addr.setPlaceholderText("Адрес")
        self.f_date   = QLineEdit(); self.f_date.setPlaceholderText("15.05.2026")
        self.f_period = QLineEdit(); self.f_period.setPlaceholderText("01.03.2026 – 31.03.2026")
        self.f_dev    = QLineEdit(); self.f_dev.setPlaceholderText("Пульсар-1.1")
        self.f_ntd    = QLineEdit(); self.f_ntd.setPlaceholderText("ГОСТ 17624-2021")
        self.f_age    = QLineEdit(); self.f_age.setPlaceholderText("28")
        self.f_proj_cls = QComboBox()
        self.f_proj_cls.addItem("— не указан —")
        for c in BETON_CLASS_LIST:
            self.f_proj_cls.addItem(c)

        add_row("№ протокола",            self.f_num)
        add_row("Объект",                 self.f_obj)
        add_row("Адрес",                  self.f_addr)
        add_row("Дата",                   self.f_date)
        add_row("Период обследования",    self.f_period)
        add_row("Приборы",                self.f_dev)
        add_row("НТД",                    self.f_ntd)
        add_row("Возраст бетона, сут",    self.f_age)
        add_row("Проектный класс бетона", self.f_proj_cls)

        # Метрики
        lay.addWidget(make_section_label("Данные в файлах"))
        mrow = QHBoxLayout()
        mrow.setSpacing(10)
        m1, self.mv_files = make_metric("0",          "файлов")
        m2, self.mv_uzk   = make_metric("0",          "измерений УЗК")
        m3, self.mv_pairs = make_metric("С:0 / НС:0", "парных точек")
        m4, self.mv_horiz = make_metric("0",          "горизонтов")
        for m in [m1, m2, m3, m4]:
            mrow.addWidget(m)
        lay.addLayout(mrow)

        # Предпросмотр
        lay.addWidget(make_section_label("Предпросмотр данных"))
        tabs = QTabWidget()
        self.tbl_s = QTableWidget(); setup_table(self.tbl_s)
        self.tbl_n = QTableWidget(); setup_table(self.tbl_n)
        tabs.addTab(self.tbl_s, "Ствол")
        tabs.addTab(self.tbl_n, "Не ствол")
        tabs.setMinimumHeight(180)
        lay.addWidget(tabs)
        lay.addStretch()

        scroll.setWidget(inner)
        root.addWidget(scroll, stretch=1)

        # Нижняя панель — кнопка Далее
        bottom = QWidget()
        bottom.setFixedHeight(52)
        bottom.setStyleSheet(f"background:{WHITE};border-top:1px solid {BORDER};")
        bl = QHBoxLayout(bottom)
        bl.setContentsMargins(20, 8, 20, 8)
        bl.addStretch()
        btn_next = QPushButton("Далее →")
        btn_next.setFixedSize(130, 36)
        btn_next.setStyleSheet("background:#2C365A;color:#EEE8DF;font-weight:600;border-radius:4px;font-size:12px;")
        btn_next.clicked.connect(self._go_next)
        bl.addWidget(btn_next)
        root.addWidget(bottom)

    def _load_files(self):
        paths, _ = QFileDialog.getOpenFileNames(
            self, "Выберите файлы Excel", "", "Excel (*.xlsx *.xls)"
        )
        if not paths:
            return
        ds, dn, ps, pn, errors = load_all_files(paths)
        if errors:
            QMessageBox.warning(self, "Предупреждение", "\n".join(errors))

        self.state["ds"]          = ds
        self.state["dn"]          = dn
        self.state["pairs_stvol"] = ps
        self.state["pairs_ne"]    = pn

        names = ", ".join(os.path.basename(p) for p in paths)
        self.lbl_files.setText(f"✓  {names}")
        self.lbl_files.setStyleSheet(
            f"color:{OK_FG};font-size:12px;background:transparent;font-weight:500;"
        )
        nuk = 0
        if len(ds): nuk += int(ds["V"].notna().sum())
        if len(dn): nuk += int(dn["V"].notna().sum())
        self.mv_uzk.setText(str(nuk))
        self.mv_pairs.setText(f"С:{len(ps)} / НС:{len(pn)}")
        self.mv_horiz.setText(str(ds["Горизонт"].nunique()) if len(ds) else "0")
        self.mv_files.setText(str(len(paths)))
        fill_table(self.tbl_s, ds.head(50) if len(ds) else pd.DataFrame())
        fill_table(self.tbl_n, dn.head(30) if len(dn) else pd.DataFrame())

    def _go_next(self):
        if "pairs_stvol" not in self.state:
            QMessageBox.information(self, "Нет данных", "Сначала загрузите файлы.")
            return
        ps = self.state.get("pairs_stvol", [])
        pn = self.state.get("pairs_ne",    [])
        if len(ps) < MIN_PAIRS and len(pn) < MIN_PAIRS:
            QMessageBox.warning(
                self, "Мало данных",
                f"Нужно минимум {MIN_PAIRS} парных точек (ствол или не ствол)."
            )
            return
        proj = self.f_proj_cls.currentText()
        self.state["meta"] = {
            "num":      self.f_num.text(),
            "obj":      self.f_obj.text(),
            "addr":     self.f_addr.text(),
            "date":     self.f_date.text(),
            "period":   self.f_period.text(),
            "dev":      self.f_dev.text(),
            "ntd":      self.f_ntd.text(),
            "age":      self.f_age.text() or "—",
            "proj_cls": proj if proj != "— не указан —" else "—",
        }
        if self.on_next:
            self.on_next()
