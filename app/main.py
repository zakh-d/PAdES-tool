import os
import sys
from typing import Optional

from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QTextCursor
from PyQt6.QtWidgets import (
    QMainWindow,
    QApplication,
    QFileDialog,
    QDialog,
)
from PyQt6.uic import loadUi

from keys_loading import PrivateKey, PublicKey, PasswordDialog
from pendrive_detection import PenDriveFinder


class MainIU(QMainWindow):
    def __init__(self):
        super(MainIU, self).__init__()
        self.detector = PenDriveFinder()
        self.private_key = PrivateKey()
        self.public_key = PublicKey()
        ui_path = os.path.join(os.path.dirname(__file__), "design.ui")
        loadUi(ui_path, self)

        # implementation of buttons
        self.sign_button.clicked.connect(self.sign_click_handler)
        self.verification_button.clicked.connect(self.verify_click_handler)

        # implementation of actions in menu
        self.action_choose_pdf_file.triggered.connect(
            self.action_choose_pdf_file_handler
        )
        self.action_exit.triggered.connect(self.close)
        self.action_choose_public_key.triggered.connect(
            self.action_choose_public_key_handler
        )

        # implementation of pendrive detection
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.check_pendrive)
        self.timer.start(3000)

    def sign_click_handler(self) -> None:
        self.add_log("PDF has been signed")

    def verify_click_handler(self) -> None:
        self.add_log("PDF has been verified")

    def add_log(self, message: str) -> None:
        self.text_browser.append(message)
        cursor = self.text_browser.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.text_browser.setTextCursor(cursor)
        self.text_browser.ensureCursorVisible()

    def action_choose_pdf_file_handler(self) -> None:
        self.add_log(self.choose_file("PDF files(*.pdf)"))

    def action_choose_public_key_handler(self) -> None:
        self.add_log(self.choose_file("Public key files(*.pem)"))

    def check_pendrive(self) -> None:
        pen_drives = self.detector.find_all_pen_drives()

        if len(pen_drives) != 0:
            if self.private_key.value is None:
                self.add_log("Pendrive has been detected")

                pen_drive = self.detector.find_pen_drive_with_private_key(pen_drives)

                if pen_drive is None:
                    self.add_log("Private key has not been found")
                    self.private_key.reset_private_key()

                if pen_drive is not None:
                    if self.private_key.value is None:
                        self.add_log("Private key has been found")

                        dlg = PasswordDialog()
                        if dlg.exec() == QDialog.DialogCode.Accepted:
                            password = dlg.password
                            self.private_key.load_private_key(
                                self.detector.get_private_key_path(pen_drive), password
                            )

        else:
            self.add_log("Pendrive has not been detected")
            self.private_key.reset_private_key()


def choose_file(self, name_filter: str) -> Optional[str]:
    file_dialog = QFileDialog(self)
    file_dialog.setWindowTitle("Choose File")
    file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
    file_dialog.setViewMode(QFileDialog.ViewMode.Detail)
    file_dialog.setNameFilter(name_filter)

    if file_dialog.exec():
        selected_files = file_dialog.selectedFiles()
        return selected_files[0]


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ui = MainIU()
    ui.show()
    app.exec()
