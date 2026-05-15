# Главное окно приложения НК Анализ

import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QVBoxLayout, QHBoxLayout, QLabel, QStackedWidget,
)

from nk_analysis.utils.constants import OCEAN, CREAM, BEIGE
from nk_analysis.ui import ImportPage, WorkPage, ExportPage, StepBar, QSS


class App(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("НК Анализ — Прочность бетонной крепи")
        self.setMinimumSize(1000, 660)
        self.resize(1200, 800)
        self.state = {}

        cw = QWidget()
        self.setCentralWidget(cw)
        ml = QVBoxLayout(cw)
        ml.setContentsMargins(0, 0, 0, 0)
        ml.setSpacing(0)

        # Заголовок
        hdr = QWidget()
        hdr.setStyleSheet(f"background:{OCEAN};")
        hdr.setFixedHeight(40)
        hl = QHBoxLayout(hdr)
        hl.setContentsMargins(20, 0, 20, 0)
        t = QLabel("НК Анализ")
        t.setStyleSheet(f"color:{CREAM};font-size:14px;font-weight:600;background:transparent;")
        s = QLabel("Прочность бетонной крепи · ГОСТ 17624-2021 · ГОСТ 18105-2018")
        s.setStyleSheet(f"color:{BEIGE};font-size:11px;background:transparent;")
        hl.addWidget(t); hl.addSpacing(16); hl.addWidget(s); hl.addStretch()
        ml.addWidget(hdr)

        # Шкала шагов
        self.step_bar = StepBar()
        ml.addWidget(self.step_bar)

        # Стек экранов
        self.stack = QStackedWidget()
        ml.addWidget(self.stack, stretch=1)

        self.pg_import = ImportPage(self.state, on_next=self._to_work)
        self.pg_work   = WorkPage(self.state,
                                  on_back=self._to_import,
                                  on_next=self._to_export)
        self.pg_export = ExportPage(self.state, on_back=self._to_work)

        self.stack.addWidget(self.pg_import)
        self.stack.addWidget(self.pg_work)
        self.stack.addWidget(self.pg_export)

        self._show(0)

    # --- навигация ---

    def _show(self, idx):
        self.stack.setCurrentIndex(idx)
        self.step_bar.set_step(idx)

    def _to_import(self):
        self._show(0)

    def _to_work(self):
        self._show(1)
        self.pg_work.refresh()

    def _to_export(self):
        self._show(2)


def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(QSS)
    win = App()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
