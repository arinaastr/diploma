import os
import pandas as pd
from nk_analysis.ui.widgets import BottomBar

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton,
    QTableWidget, QComboBox, QLabel, QFileDialog, QMessageBox,
    QTabWidget, QScrollArea, QFrame, QDialog, QCalendarWidget,
    QDialogButtonBox,
)
from PyQt6.QtCore import Qt, QDate

from nk_analysis.utils.constants import (
    NAVY, BLUE, WHITE, SURFACE, BORDER, MUTED, OK_FG, MIN_PAIRS
)
from nk_analysis.core.excel_import import load_all_files
from nk_analysis.ui.styles import (
    make_label, make_field_label, make_section_label,
    make_metric, setup_table, fill_table,
)

BETON_CLASS_LIST = [
    "B5","B7.5","B10","B12.5","B15","B17.5","B20","B22.5",
    "B25","B27.5","B30","B35","B40","B45","B50","B60",
]

class _ClickableLineEdit(QLineEdit):
    def __init__(self, placeholder, on_click, parent=None):
        super().__init__(parent)
        self.setPlaceholderText(placeholder)
        self._on_click = on_click
        self.setReadOnly(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def mousePressEvent(self, event):
        self._on_click()

class ImportPage(QWidget):

    def __init__(self, state, on_next=None):
        super().__init__()
        self.state   = state
        self.on_next = on_next

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        inner = QWidget()
        inner.setStyleSheet(f"background:{WHITE};")
        lay = QVBoxLayout(inner)
        lay.setContentsMargins(28, 20, 28, 16)
        lay.setSpacing(10)

        lay.addWidget(make_label("Импорт данных", big=True))
        lay.addWidget(make_label(
            "Загрузите .xlsx файлы. Данные «Ствол» и «Не ствол» обрабатываются раздельно.",
            muted=True,
        ))
        lay.addSpacing(4)

        file_card = QWidget()
        file_card.setStyleSheet(
            f"background:{SURFACE};border:none;border-radius:10px;"
        )
        fc_lay = QVBoxLayout(file_card)
        fc_lay.setContentsMargins(16, 14, 16, 14)
        fc_lay.setSpacing(8)

        fc_lay.addWidget(make_section_label("Файлы данных"))

        self.btn_load = QPushButton("  Выбрать файлы…")
        self.btn_load.setFixedHeight(38)
        self.btn_load.setStyleSheet(
            f"background:{NAVY};color:#FFFFFF;border:none;"
            f"border-radius:6px;font-size:13px;font-weight:600;"
            f"padding:0 18px;text-align:center;"
        )
        self.btn_load.clicked.connect(self._load_files)
        fc_lay.addWidget(self.btn_load)

        self.lbl_files = QLabel("Файлы не выбраны")
        self.lbl_files.setStyleSheet(
            f"font-size:12px;color:{MUTED};background:transparent;border:none;"
        )
        self.lbl_files.setAlignment(Qt.AlignmentFlag.AlignCenter)
        fc_lay.addWidget(self.lbl_files)

        lay.addWidget(file_card)

        lay.addWidget(make_section_label("Реквизиты объекта"))

        self.f_num    = QLineEdit(); self.f_num.setPlaceholderText("01/2026")
        self.f_obj    = QLineEdit(); self.f_obj.setPlaceholderText("Наименование объекта")
        self.f_addr   = QLineEdit(); self.f_addr.setPlaceholderText("Адрес")
        self.f_date   = QLineEdit(); self.f_date.setPlaceholderText("15.05.2026")
        self.f_period = _ClickableLineEdit("01.03.2026 – 31.03.2026", self._pick_period)
        self._period_widget = self.f_period
        self.f_dev    = QLineEdit(); self.f_dev.setPlaceholderText("Пульсар-1.1")
        self.f_ntd    = QLineEdit(); self.f_ntd.setPlaceholderText("ГОСТ 17624-2021")
        self.f_age    = QLineEdit(); self.f_age.setPlaceholderText("28")

        self.f_proj_cls = QComboBox()
        self.f_proj_cls.addItem("— не указан —")
        for c in BETON_CLASS_LIST:
            self.f_proj_cls.addItem(c)

        def field_row(pairs):
            """pairs = [(label, widget), ...]"""
            row = QHBoxLayout(); row.setSpacing(16)
            for lbl_text, widget in pairs:
                cell = QVBoxLayout(); cell.setSpacing(4)
                lbl = make_field_label(lbl_text)
                cell.addWidget(lbl)
                cell.addWidget(widget)
                row.addLayout(cell)
            return row

        lay.addLayout(field_row([("№ протокола", self.f_num),
                                  ("Объект",      self.f_obj)]))
        lay.addLayout(field_row([("Адрес",        self.f_addr),
                                  ("Дата",         self.f_date)]))
        lay.addLayout(field_row([("Период обследования", self.f_period),
                                  ("Приборы",             self.f_dev)]))
        lay.addLayout(field_row([("НТД",                  self.f_ntd),
                                  ("Возраст бетона, сут",  self.f_age)]))

        proj_row = QHBoxLayout(); proj_row.setSpacing(16)
        proj_cell = QVBoxLayout(); proj_cell.setSpacing(4)
        proj_cell.addWidget(make_field_label("Проектный класс бетона"))
        self.f_proj_cls.setMaximumWidth(260)
        proj_cell.addWidget(self.f_proj_cls)
        proj_row.addLayout(proj_cell)
        proj_row.addStretch()
        lay.addLayout(proj_row)

        lay.addSpacing(4)
        lay.addWidget(make_section_label("Данные в файлах"))
        mrow = QHBoxLayout(); mrow.setSpacing(8)
        m1, self.mv_files = make_metric("0",           "файлов")
        m2, self.mv_uzk   = make_metric("0",           "измерений УЗК")
        m3, self.mv_pairs = make_metric("С:0 / НС:0",  "парных точек")
        m4, self.mv_horiz = make_metric("0",           "горизонтов")
        for m in [m1, m2, m3, m4]:
            mrow.addWidget(m)
        lay.addLayout(mrow)

        lay.addSpacing(4)
        lay.addWidget(make_section_label("Предпросмотр данных"))
        tabs = QTabWidget()
        tabs.setStyleSheet("QTabWidget::pane { border-top: 1.5px solid #DDE5F0; }")
        self.tbl_s = QTableWidget(); setup_table(self.tbl_s)
        self.tbl_n = QTableWidget(); setup_table(self.tbl_n)
        tabs.addTab(self.tbl_s, "Ствол")
        tabs.addTab(self.tbl_n, "Конструкция")
        tabs.setMinimumHeight(180)
        lay.addWidget(tabs)
        lay.addStretch()

        scroll.setWidget(inner)
        root.addWidget(scroll, stretch=1)

        bar = BottomBar(on_next=self._go_next)
        bar.btn_back.setVisible(False)
        root.addWidget(bar)

    def _pick_period(self):
        dlg = QDialog(self)
        dlg.setWindowTitle("Выбор периода обследования")
        dlg.setMinimumWidth(520)
        dlg.setStyleSheet(f"background:#FFFFFF;font-size:13px;")

        lay = QVBoxLayout(dlg)
        lay.setContentsMargins(20, 16, 20, 16)
        lay.setSpacing(12)

        lbl = QLabel("Выберите начало и конец периода обследования")
        lbl.setStyleSheet(f"font-size:13px;color:#2C3E50;font-weight:600;")
        lay.addWidget(lbl)

        cals_row = QHBoxLayout()
        cals_row.setSpacing(16)

        start_block = QVBoxLayout()
        start_lbl = QLabel("Начало периода")
        start_lbl.setStyleSheet("font-size:11px;color:#7A90AA;font-weight:600;text-transform:uppercase;")
        self._cal_start = QCalendarWidget()
        self._cal_start.setGridVisible(True)
        self._cal_start.setStyleSheet("""
QCalendarWidget QWidget { background: #FFFFFF; color: #1C2B4A; }
QCalendarWidget QAbstractItemView {
    background: #FFFFFF;
    color: #1C2B4A;
    selection-background-color: #1C2B4A;
    selection-color: #FFFFFF;
    outline: 0;
}
QCalendarWidget QAbstractItemView:enabled { color: #1C2B4A; }
QCalendarWidget QAbstractItemView:disabled { color: #B0BFCF; }
QCalendarWidget QToolButton { color: #1C2B4A; background: transparent; font-size:13px; font-weight:600; padding:4px 8px; border:none; }
QCalendarWidget QToolButton:hover { background: #F4F6FA; border-radius:4px; }
QCalendarWidget QMenu { background: #FFFFFF; color: #1C2B4A; }
QCalendarWidget QSpinBox { color: #1C2B4A; background: #FFFFFF; font-size:13px; border:none; }
""")
        self._cal_start.setSelectedDate(QDate.currentDate().addMonths(-1).addDays(1 - QDate.currentDate().day()))
        start_block.addWidget(start_lbl)
        from PyQt6.QtGui import QPalette, QColor as _QColor
        _pal = self._cal_start.palette()
        _pal.setColor(QPalette.ColorRole.Highlight, _QColor("#1C2B4A"))
        _pal.setColor(QPalette.ColorRole.HighlightedText, _QColor("#FFFFFF"))
        _pal.setColor(QPalette.ColorRole.Base, _QColor("#FFFFFF"))
        _pal.setColor(QPalette.ColorRole.Text, _QColor("#1C2B4A"))
        self._cal_start.setPalette(_pal)
        start_block.addWidget(self._cal_start)

        end_block = QVBoxLayout()
        end_lbl = QLabel("Конец периода")
        end_lbl.setStyleSheet("font-size:11px;color:#7A90AA;font-weight:600;text-transform:uppercase;")
        self._cal_end = QCalendarWidget()
        self._cal_end.setGridVisible(True)
        self._cal_end.setStyleSheet("""
QCalendarWidget QWidget { background: #FFFFFF; color: #1C2B4A; }
QCalendarWidget QAbstractItemView {
    background: #FFFFFF;
    color: #1C2B4A;
    selection-background-color: #1C2B4A;
    selection-color: #FFFFFF;
    outline: 0;
}
QCalendarWidget QAbstractItemView:enabled { color: #1C2B4A; }
QCalendarWidget QAbstractItemView:disabled { color: #B0BFCF; }
QCalendarWidget QToolButton { color: #1C2B4A; background: transparent; font-size:13px; font-weight:600; padding:4px 8px; border:none; }
QCalendarWidget QToolButton:hover { background: #F4F6FA; border-radius:4px; }
QCalendarWidget QMenu { background: #FFFFFF; color: #1C2B4A; }
QCalendarWidget QSpinBox { color: #1C2B4A; background: #FFFFFF; font-size:13px; border:none; }
""")
        self._cal_end.setSelectedDate(QDate.currentDate())
        end_block.addWidget(end_lbl)
        _pal2 = self._cal_end.palette()
        _pal2.setColor(QPalette.ColorRole.Highlight, _QColor("#1C2B4A"))
        _pal2.setColor(QPalette.ColorRole.HighlightedText, _QColor("#FFFFFF"))
        _pal2.setColor(QPalette.ColorRole.Base, _QColor("#FFFFFF"))
        _pal2.setColor(QPalette.ColorRole.Text, _QColor("#1C2B4A"))
        self._cal_end.setPalette(_pal2)
        end_block.addWidget(self._cal_end)

        cals_row.addLayout(start_block)
        cals_row.addLayout(end_block)
        lay.addLayout(cals_row)

        btns = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        btns.button(QDialogButtonBox.StandardButton.Ok).setText("Применить")
        btns.button(QDialogButtonBox.StandardButton.Cancel).setText("Отмена")
        btns.button(QDialogButtonBox.StandardButton.Ok).setStyleSheet(
            "background:#1C2B4A;color:#FFFFFF;border:none;border-radius:6px;"
            "padding:7px 20px;font-size:13px;font-weight:600;"
        )
        btns.button(QDialogButtonBox.StandardButton.Cancel).setStyleSheet(
            "background:transparent;color:#1C2B4A;border:1.5px solid #DDE5F0;"
            "border-radius:6px;padding:7px 20px;font-size:13px;"
        )
        btns.accepted.connect(dlg.accept)
        btns.rejected.connect(dlg.reject)
        lay.addWidget(btns)

        if dlg.exec() == QDialog.DialogCode.Accepted:
            d1 = self._cal_start.selectedDate().toString("dd.MM.yyyy")
            d2 = self._cal_end.selectedDate().toString("dd.MM.yyyy")
            self.f_period.setText(f"{d1} – {d2}")
            # Визуальная фиксация выбранного периода: подсветка поля
            self.f_period.setStyleSheet(
                f"border: 2px solid #1C2B4A; border-radius: 6px; "
                f"background: #EEF3FA; color: #1C2B4A; "
                f"font-size: 13px; padding: 4px 8px;"
            )

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
        self.lbl_files.setText(f"  {names}")
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
                f"Нужно минимум {MIN_PAIRS} парных точек."
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
