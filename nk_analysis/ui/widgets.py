# Виджеты: StepBar (шкала шагов) и BottomBar (нижняя панель навигации)

from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt
from nk_analysis.utils.constants import OCEAN, CREAM, BEIGE, MUTED, WHITE, BORDER


class StepBar(QWidget):
    STEPS = ["1. Импорт", "2. Работа", "3. Выгрузка"]

    def __init__(self):
        super().__init__()
        self.setFixedHeight(36)
        self.setStyleSheet(f"background:{WHITE};border-bottom:1px solid {BORDER};")
        lay = QHBoxLayout(self)
        lay.setContentsMargins(20, 0, 20, 0)
        lay.setSpacing(0)
        self._labels = []
        for i, name in enumerate(self.STEPS):
            lbl = QLabel(name)
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl.setFixedHeight(36)
            lbl.setStyleSheet("font-size:12px;padding:0 16px;background:transparent;")
            lay.addWidget(lbl)
            self._labels.append(lbl)
            if i < len(self.STEPS) - 1:
                sep = QLabel("›")
                sep.setStyleSheet(f"color:{MUTED};background:transparent;font-size:14px;")
                lay.addWidget(sep)
        lay.addStretch()
        self.set_step(0)

    def set_step(self, idx):
        for i, lbl in enumerate(self._labels):
            if i == idx:
                lbl.setStyleSheet(
                    f"font-size:12px;font-weight:700;color:{OCEAN};"
                    f"border-bottom:2px solid {OCEAN};padding:0 16px;background:transparent;"
                )
            elif i < idx:
                lbl.setStyleSheet(
                    f"font-size:12px;color:{MUTED};padding:0 16px;background:transparent;"
                )
            else:
                lbl.setStyleSheet(
                    f"font-size:12px;color:{BEIGE};padding:0 16px;background:transparent;"
                )


class BottomBar(QWidget):
    def __init__(self, on_back=None, on_next=None,
                 back_text="← Назад", next_text="Далее →"):
        super().__init__()
        self.setFixedHeight(52)
        self.setStyleSheet(f"background:{WHITE};border-top:1px solid {BORDER};")
        lay = QHBoxLayout(self)
        lay.setContentsMargins(20, 8, 20, 8)

        self.btn_back = QPushButton(back_text)
        self.btn_back.setFixedWidth(110)
        self.btn_back.setStyleSheet("background:#2C365A;color:#EEE8DF;font-weight:600;border-radius:4px;font-size:12px;border:none;padding:6px 18px;")
        if on_back:
            self.btn_back.clicked.connect(on_back)

        self.btn_next = QPushButton(next_text)
        self.btn_next.setFixedWidth(110)
        self.btn_next.setStyleSheet("background:#2C365A;color:#EEE8DF;font-weight:600;border-radius:4px;font-size:12px;border:none;padding:6px 18px;")
        if on_next:
            self.btn_next.clicked.connect(on_next)

        lay.addWidget(self.btn_back)
        lay.addStretch()
        lay.addWidget(self.btn_next)
