from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt
from nk_analysis.utils.constants import NAVY, BLUE, WHITE, BORDER, MUTED

class StepBar(QWidget):
    STEPS = ["1. Импорт", "2. Работа", "3. Выгрузка"]

    def __init__(self):
        super().__init__()
        self.setFixedHeight(40)
        self.setStyleSheet(
            f"background:{WHITE};border-bottom:1px solid {BORDER};"
        )
        lay = QHBoxLayout(self)
        lay.setContentsMargins(20, 0, 20, 0)
        lay.setSpacing(0)
        self._labels = []
        for i, name in enumerate(self.STEPS):
            lbl = QLabel(name)
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl.setFixedHeight(40)
            lay.addWidget(lbl)
            self._labels.append(lbl)
            if i < len(self.STEPS) - 1:
                sep = QLabel("›")
                sep.setStyleSheet(
                    f"color:{MUTED};background:transparent;"
                    f"font-size:14px;padding:0 4px;"
                )
                lay.addWidget(sep)
        lay.addStretch()
        self.set_step(0)

    def set_step(self, idx):
        for i, lbl in enumerate(self._labels):
            if i == idx:
                lbl.setStyleSheet(
                    f"font-size:13px;font-weight:600;color:{NAVY};"
                    f"border-bottom:2px solid {NAVY};"
                    f"padding:0 16px;background:transparent;"
                )
            elif i < idx:
                lbl.setStyleSheet(
                    f"font-size:13px;color:{MUTED};"
                    f"padding:0 16px;background:transparent;"
                )
            else:
                lbl.setStyleSheet(
                    f"font-size:13px;color:#C5D0DE;"
                    f"padding:0 16px;background:transparent;"
                )

BTN_STYLE = (
    f"background:{NAVY};color:#FFFFFF;font-weight:600;"
    f"border-radius:6px;font-size:13px;border:none;padding:0 22px;"
)
BTN_BACK = (
    f"background:transparent;color:{NAVY};"
    f"border:1.5px solid {BORDER};border-radius:6px;"
    f"font-size:13px;font-weight:500;padding:0 22px;"
)

class BottomBar(QWidget):
    def __init__(self, on_back=None, on_next=None,
                 back_text="Назад", next_text="Далее"):
        super().__init__()
        self.setFixedHeight(54)
        self.setStyleSheet(
            f"background:{WHITE};border-top:1px solid {BORDER};"
        )
        lay = QHBoxLayout(self)
        lay.setContentsMargins(24, 8, 24, 8)

        self.btn_back = QPushButton(back_text)
        self.btn_back.setFixedSize(120, 36)
        self.btn_back.setStyleSheet(BTN_BACK)
        if on_back:
            self.btn_back.clicked.connect(on_back)

        self.btn_next = QPushButton(next_text)
        self.btn_next.setFixedSize(120, 36)
        self.btn_next.setStyleSheet(BTN_STYLE)
        if on_next:
            self.btn_next.clicked.connect(on_next)

        lay.addWidget(self.btn_back)
        lay.addStretch()
        lay.addWidget(self.btn_next)
