import os
import shutil

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit,
    QPushButton, QLabel, QCheckBox, QFileDialog, QMessageBox, QScrollArea,
)

from nk_analysis.ui.styles import make_label, make_section_label, make_field_label, CheckBox
from nk_analysis.ui.widgets import BottomBar
from nk_analysis.export.docx_report import generate_docx
from nk_analysis.utils.constants import NAVY, WHITE, SURFACE, BORDER, MUTED, OK_FG
OCEAN = NAVY
CREAM = WHITE

class ExportPage(QWidget):

    def __init__(self, state, on_back=None):
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
        lay.setContentsMargins(28, 16, 28, 12)
        lay.setSpacing(10)

        lay.addWidget(make_label("Выгрузка протокола", big=True))
        lay.addWidget(make_label("Настройте содержимое протокола и сохраните DOCX.", muted=True))

        lay.addWidget(make_section_label("Исполнители"))

        def row(label, widget):
            r = QHBoxLayout()
            lbl = make_field_label(label)
            lbl.setFixedWidth(180)
            r.addWidget(lbl)
            r.addWidget(widget)
            lay.addLayout(r)

        self.f_e1f = QLineEdit(); self.f_e1f.setPlaceholderText("ФИО исполнителя 1")
        self.f_e1p = QLineEdit(); self.f_e1p.setPlaceholderText("Должность")
        self.f_e2f = QLineEdit(); self.f_e2f.setPlaceholderText("ФИО исполнителя 2")
        self.f_e2p = QLineEdit(); self.f_e2p.setPlaceholderText("Должность")
        row("Исполнитель 1, ФИО",       self.f_e1f)
        row("Исполнитель 1, должность", self.f_e1p)
        row("Исполнитель 2, ФИО",       self.f_e2f)
        row("Исполнитель 2, должность", self.f_e2p)

        lay.addWidget(make_section_label("Содержимое протокола"))
        self.chk_chart  = CheckBox("Включить графики")
        self.chk_stvol  = CheckBox("Результаты по стволу")
        self.chk_ne     = CheckBox("Результаты по конструкциям (не ствол)")
        self.chk_chart.setChecked(True)
        self.chk_stvol.setChecked(True)
        self.chk_ne.setChecked(True)
        lay.addWidget(self.chk_chart)
        lay.addWidget(self.chk_stvol)
        lay.addWidget(self.chk_ne)

        lay.addWidget(make_section_label("Сохранить"))
        btn_save = QPushButton("Сохранить протокол DOCX…")
        btn_save.setFixedWidth(260)
        btn_save.setFixedHeight(36)
        btn_save.setStyleSheet("background:#2C365A;color:#EEE8DF;font-weight:600;border-radius:4px;font-size:12px;border:none;")
        btn_save.clicked.connect(self._save)
        lay.addWidget(btn_save)

        self.lbl_status = QLabel("")
        self.lbl_status.setStyleSheet("font-size:12px;background:transparent;")
        lay.addWidget(self.lbl_status)
        lay.addStretch()

        scroll.setWidget(inner)
        root.addWidget(scroll, stretch=1)

        bar = BottomBar(on_back=on_back, on_next=None, next_text="")
        bar.btn_next.setVisible(False)
        root.addWidget(bar)

    def _save(self):
        meta = dict(self.state.get("meta", {}))
        meta["e1f"] = self.f_e1f.text()
        meta["e1p"] = self.f_e1p.text()
        meta["e2f"] = self.f_e2f.text()
        meta["e2p"] = self.f_e2p.text()

        path, _ = QFileDialog.getSaveFileName(
            self, "Сохранить протокол", "Протокол_НК.docx", "Word (*.docx)"
        )
        if not path:
            return

        try:
            tmp = generate_docx(
                self.state, meta,
                include_chart=self.chk_chart.isChecked(),
                include_stvol=self.chk_stvol.isChecked(),
                include_ne=self.chk_ne.isChecked(),
            )
            shutil.move(tmp, path)
            self.lbl_status.setText(f" Сохранено: {os.path.basename(path)}")
            self.lbl_status.setStyleSheet(f"font-size:12px;color:{OK_FG};background:transparent;")
            import subprocess, sys
            if sys.platform == "win32":
                os.startfile(path)
            elif sys.platform == "darwin":
                subprocess.call(["open", path])
            else:
                subprocess.call(["xdg-open", path])
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))
