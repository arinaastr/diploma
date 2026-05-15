from PyQt6.QtWidgets import (QLabel, QWidget, QHBoxLayout, QVBoxLayout,
                              QTableWidget, QHeaderView, QAbstractItemView)
from PyQt6.QtCore import Qt

NAVY    = "#1C2B4A"
BLUE    = "#3A7BD5"
WHITE   = "#FFFFFF"
BG      = "#FFFFFF"
SURFACE = "#F5F8FC"
BORDER  = "#DDE5F0"
MUTED   = "#7A90AA"
TEXT    = "#1C2B4A"
OK_FG   = "#1E6B3C"
OK_BG   = "#E6F4EC"

import os as _os

def _make_qss():
    _check = _os.path.join(_os.path.dirname(__file__), "assets", "check.png").replace("\\", "/")
    return f"""
* {{
    font-family: 'Segoe UI', 'Inter', Arial, sans-serif;
    color: {TEXT};
    font-size: 13px;
}}

QMainWindow, QWidget {{
    background: {BG};
}}

/* ── Кнопки ── */
QPushButton {{
    background: {NAVY};
    color:
    border: none;
    border-radius: 6px;
    padding: 8px 22px;
    font-size: 13px;
    font-weight: 600;
}}
QPushButton:hover   {{ background:
QPushButton:pressed {{ background:
QPushButton:disabled {{ background:

QPushButton[accent="true"] {{
    background: {BLUE};
    color:
}}
QPushButton[accent="true"]:hover {{ background:

/* ── Поля ввода: только нижняя линия ── */
QLineEdit {{
    background: {SURFACE};
    border: 1px solid {BORDER};
    border-radius: 6px;
    padding: 7px 10px;
    font-size: 13px;
    color: {TEXT};
    selection-background-color: {BLUE};
}}
QLineEdit:focus {{
    background: {WHITE};
    border: 1.5px solid {BLUE};
    border-radius: 6px;
}}

/* ── Комбобокс: только нижняя линия ── */
QComboBox {{
    background: {SURFACE};
    border: 1px solid {BORDER};
    border-radius: 6px;
    padding: 7px 10px;
    font-size: 13px;
    color: {TEXT};
}}
QComboBox:focus {{
    background: {WHITE};
    border: 1.5px solid {BLUE};
    border-radius: 6px;
}}
QComboBox::drop-down {{
    border: none;
    width: 20px;
}}
QComboBox::down-arrow {{
    image: none;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 5px solid {MUTED};
    width: 0; height: 0;
    margin-right: 4px;
}}
QComboBox QAbstractItemView {{
    background: {WHITE};
    border: 1px solid {BORDER};
    border-radius: 6px;
    selection-background-color: {SURFACE};
    selection-color: {TEXT};
    outline: none;
    padding: 4px;
}}

/* ── Вкладки ── */
QTabWidget::pane {{
    border: none;
    border-top: 1.5px solid {BORDER};
    background: {WHITE};
}}
QTabBar::tab {{
    background: transparent;
    color: {MUTED};
    padding: 8px 18px;
    border: none;
    border-bottom: 2px solid transparent;
    font-size: 13px;
    margin-right: 2px;
}}
QTabBar::tab:selected {{
    color: {NAVY};
    font-weight: 600;
    border-bottom: 2px solid {NAVY};
}}
QTabBar::tab:hover:!selected {{
    color: {TEXT};
    border-bottom: 2px solid {BORDER};
}}

/* ── Таблицы ── */
QTableWidget {{
    background: {WHITE};
    gridline-color: {BORDER};
    border: 1px solid {BORDER};
    border-radius: 6px;
    alternate-background-color: {SURFACE};
    selection-background-color:
    selection-color: {TEXT};
    outline: none;
}}
QHeaderView::section {{
    background: {NAVY};
    color:
    padding: 6px 8px;
    font-size: 11px;
    font-weight: 600;
    border: none;
    border-right: 1px solid
}}
QHeaderView::section:last {{
    border-right: none;
}}

/* ── Скроллбар ── */
QScrollBar:vertical {{
    width: 6px;
    background: transparent;
    margin: 0;
}}
QScrollBar::handle:vertical {{
    background: {BORDER};
    border-radius: 3px;
    min-height: 24px;
}}
QScrollBar::handle:vertical:hover {{
    background:
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
}}
QScrollBar:horizontal {{
    height: 6px;
    background: transparent;
}}
QScrollBar::handle:horizontal {{
    background: {BORDER};
    border-radius: 3px;
    min-width: 24px;
}}

/* ── Чекбоксы ── */
QCheckBox {{
    spacing: 8px;
    color: {TEXT};
    font-size: 13px;
}}
QCheckBox::indicator {{
    width: 16px; height: 16px;
    border: 1.5px solid {BORDER};
    border-radius: 4px;
    background: {WHITE};
}}
QCheckBox::indicator:hover {{
    border-color: {BLUE};
}}
QCheckBox::indicator:checked {{
    background: {NAVY};
    border-color: {NAVY};
    image: url("{{_check}}");
}}

/* ── ScrollArea ── */
QScrollArea {{
    border: none;
    background: transparent;
}}
QScrollArea > QWidget > QWidget {{
    background: transparent;
}}
"""

QSS = _make_qss()

def make_label(text, big=False, muted=False):
    lbl = QLabel(text)
    lbl.setWordWrap(True)
    if big:
        lbl.setStyleSheet(
            f"font-size:20px;font-weight:500;color:{NAVY};background:transparent;"
        )
    elif muted:
        lbl.setStyleSheet(
            f"font-size:12px;color:{MUTED};background:transparent;"
        )
    else:
        lbl.setStyleSheet("font-size:13px;background:transparent;")
    return lbl

def make_field_label(text):
    lbl = QLabel(text)
    lbl.setStyleSheet(
        f"font-size:11px;font-weight:600;color:{MUTED};"
        f"background:transparent;text-transform:uppercase;letter-spacing:0.5px;"
    )
    return lbl

def make_section_label(text):
    lbl = QLabel(text)
    lbl.setStyleSheet(
        f"font-size:11px;font-weight:600;color:{NAVY};"
        f"background:transparent;text-transform:uppercase;"
        f"letter-spacing:0.6px;margin-top:6px;"
    )
    return lbl

def make_metric(value, label):
    """Карточка метрики: число + подпись, светлый фон."""
    card = QWidget()
    card.setStyleSheet(
        f"background:{SURFACE};border-radius:8px;border:none;"
    )
    lay = QVBoxLayout(card)
    lay.setContentsMargins(12, 10, 12, 10)
    lay.setSpacing(2)
    v_lbl = QLabel(str(value))
    v_lbl.setStyleSheet(
        f"font-size:22px;font-weight:500;color:{NAVY};"
        f"background:transparent;"
    )
    v_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
    k_lbl = QLabel(label)
    k_lbl.setStyleSheet(
        f"font-size:11px;color:{MUTED};background:transparent;"
    )
    k_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
    lay.addWidget(v_lbl)
    lay.addWidget(k_lbl)
    return card, v_lbl

def setup_table(tbl):
    tbl.setAlternatingRowColors(True)
    tbl.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
    tbl.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
    tbl.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
    tbl.verticalHeader().setVisible(False)
    tbl.setShowGrid(True)
    tbl.setFrameShape(QTableWidget.Shape.NoFrame)

def fill_table(tbl, df):
    from PyQt6.QtWidgets import QTableWidgetItem
    import numpy as np
    if df is None or len(df) == 0:
        tbl.setRowCount(0)
        tbl.setColumnCount(0)
        return
    cols = list(df.columns)
    tbl.setColumnCount(len(cols))
    tbl.setHorizontalHeaderLabels(cols)
    tbl.setRowCount(len(df))
    for r, (_, row) in enumerate(df.iterrows()):
        for c, col in enumerate(cols):
            val = row[col]
            txt = "—" if (val is None or (
                isinstance(val, float) and np.isnan(val))) else str(val)
            item = QTableWidgetItem(txt)
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            tbl.setItem(r, c, item)

from PyQt6.QtWidgets import QCheckBox as _QCheckBox
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush
from PyQt6.QtCore import QRect, Qt as _Qt

class CheckBox(_QCheckBox):
    """Чекбокс с тёмно-синим фоном и белой галочкой при выборе."""

    BOX   = 17
    NAVY  = QColor("#1C2B4A")
    EMPTY = QColor("#FFFFFF")
    BORD  = QColor("#DDE5F0")
    TEXT  = QColor("#2C3E50")

    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.setStyleSheet(
            "QCheckBox { spacing: 8px; font-size: 13px; background: transparent; }"
            "QCheckBox::indicator { width: 0px; height: 0px; }"
        )

    def paintEvent(self, event):
        super().paintEvent(event)
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        b = self.BOX
        y = (self.height() - b) // 2
        rect = QRect(0, y, b, b)

        if self.isChecked():
            p.setBrush(QBrush(self.NAVY))
            p.setPen(_Qt.PenStyle.NoPen)
            p.drawRoundedRect(rect, 4, 4)
            pen = QPen(QColor("#FFFFFF"))
            pen.setWidth(2)
            pen.setCapStyle(_Qt.PenCapStyle.RoundCap)
            pen.setJoinStyle(_Qt.PenJoinStyle.RoundJoin)
            p.setPen(pen)
            p.drawLine(
                int(b * 0.22), int(b * 0.52) + y,
                int(b * 0.44), int(b * 0.74) + y
            )
            p.drawLine(
                int(b * 0.44), int(b * 0.74) + y,
                int(b * 0.80), int(b * 0.26) + y
            )
        else:
            p.setBrush(QBrush(self.EMPTY))
            pen = QPen(self.BORD)
            pen.setWidth(1)
            p.setPen(pen)
            p.drawRoundedRect(rect, 4, 4)
        p.end()
