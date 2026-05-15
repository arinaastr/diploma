# Стили PyQt6 и вспомогательные фабрики виджетов

from PyQt6.QtWidgets import QLabel, QWidget, QHBoxLayout, QTableWidget, QHeaderView, QAbstractItemView
from PyQt6.QtCore import Qt
from nk_analysis.utils.constants import (
    CREAM, BEIGE, OCEAN, WHITE, MUTED, BORDER, TEXT_COLOR,
    OK_BG, OK_FG, WRN_BG, WRN_FG, BAD_BG, BAD_FG,
)

QSS = f"""
* {{ font-family: 'Segoe UI', Arial, sans-serif; color: {TEXT_COLOR}; }}
QMainWindow, QWidget {{ background: {CREAM}; }}
QPushButton {{
    background: {OCEAN}; color: {CREAM};
    border: none; border-radius: 4px;
    padding: 7px 20px; font-size: 12px; font-weight: 600;
}}
QPushButton:hover   {{ background: #3d4d7a; }}
QPushButton:pressed {{ background: #1e2840; }}
QPushButton:disabled {{ background: {BEIGE}; color: {MUTED}; }}
QPushButton[secondary="true"] {{
    background: transparent; color: {OCEAN};
    border: 1.5px solid {OCEAN};
}}
QPushButton[secondary="true"]:hover {{ background: #e8e4f0; }}
QLineEdit, QComboBox {{
    background: {WHITE}; border: 1.5px solid {BORDER};
    border-radius: 4px; padding: 5px 8px; font-size: 12px;
}}
QLineEdit:focus, QComboBox:focus {{ border-color: {OCEAN}; }}
QTabWidget::pane {{ border: 1px solid {BORDER}; background: {WHITE}; }}
QTabBar::tab {{
    background: {BEIGE}; padding: 5px 16px;
    border-top-left-radius: 4px; border-top-right-radius: 4px;
    margin-right: 2px;
}}
QTabBar::tab:selected {{ background: {WHITE}; font-weight: 600; }}
QTableWidget {{
    background: {WHITE}; gridline-color: {BORDER};
    border: 1px solid {BORDER};
}}
QHeaderView::section {{
    background: {OCEAN}; color: {CREAM};
    padding: 4px; font-size: 11px; font-weight: 600;
    border: none;
}}
QScrollBar:vertical {{
    width: 8px; background: {CREAM};
}}
QScrollBar::handle:vertical {{
    background: {BEIGE}; border-radius: 4px; min-height: 20px;
}}
QCheckBox {{ spacing: 6px; }}
QCheckBox::indicator {{
    width: 14px; height: 14px;
    border: 1.5px solid {BORDER}; border-radius: 3px;
    background: {WHITE};
}}
QCheckBox::indicator:checked {{
    background: {OCEAN}; border-color: {OCEAN};
}}
"""


def make_label(text, big=False, muted=False):
    lbl = QLabel(text)
    lbl.setWordWrap(True)
    if big:
        lbl.setStyleSheet(f"font-size:16px;font-weight:700;color:{OCEAN};background:transparent;")
    elif muted:
        lbl.setStyleSheet(f"font-size:11px;color:{MUTED};background:transparent;")
    else:
        lbl.setStyleSheet("font-size:12px;background:transparent;")
    return lbl


def make_field_label(text):
    lbl = QLabel(text)
    lbl.setStyleSheet(f"font-size:11px;font-weight:600;color:{MUTED};background:transparent;")
    return lbl


def make_section_label(text):
    lbl = QLabel(text)
    lbl.setStyleSheet(f"font-size:13px;font-weight:700;color:{OCEAN};background:transparent;margin-top:8px;")
    return lbl


def make_metric(value, label):
    card = QWidget()
    card.setStyleSheet(f"background:{WHITE};border:1px solid {BORDER};border-radius:6px;padding:4px;")
    lay = QHBoxLayout(card)
    lay.setContentsMargins(10, 6, 10, 6)
    v_lbl = QLabel(str(value))
    v_lbl.setStyleSheet(f"font-size:18px;font-weight:700;color:{OCEAN};background:transparent;")
    k_lbl = QLabel(label)
    k_lbl.setStyleSheet(f"font-size:10px;color:{MUTED};background:transparent;")
    lay.addWidget(v_lbl)
    lay.addSpacing(6)
    lay.addWidget(k_lbl)
    lay.addStretch()
    return card, v_lbl


def setup_table(tbl):
    tbl.setAlternatingRowColors(True)
    tbl.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
    tbl.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
    tbl.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
    tbl.verticalHeader().setVisible(False)
    tbl.setShowGrid(True)


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
            txt = "—" if (val is None or (isinstance(val, float) and np.isnan(val))) else str(val)
            tbl.setItem(r, c, QTableWidgetItem(txt))
