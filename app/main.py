import os
import sys
from typing import Optional

from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import (
    QApplication,
    QFileDialog,
    QDialog,
)
from PyQt6.QtQml import QQmlApplicationEngine
from PyQt6.QtCore import QObject, pyqtSlot
from PyQt6.QtWidgets import QMessageBox

from keys_loading import PrivateKey, PublicKey, PasswordDialog
from pendrive_detection import PenDriveFinder
from pdf.pdf_signer import PDFSigner
from pdf.pdf_verifier import PDFVerifier
import logging

logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")


def choose_file(select_window_title: str, name_filter: str) -> Optional[str]:
    file_path, _ = QFileDialog.getOpenFileName(
        None, select_window_title, "", name_filter
    )
    return file_path


class Backend(QObject):
    def __init__(self, root: QObject):
        super().__init__()
        self.root = root

        self.detector = PenDriveFinder()
        self.private_key = PrivateKey()
        self.public_key = PublicKey()

        # implementation of pendrive detection
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.check_pendrive)
        self.timer.start(1000)

        self.selected_pdf: Optional[str] = None

    def _show_message_dialog(
        self, title: str, message: str, icon=QMessageBox.Icon.Information
    ):
        msg_box = QMessageBox()
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setIcon(icon)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.exec()

    @pyqtSlot()
    def handle_select_pdf(self):
        if self.root.property("pdfFileLoaded"):
            self.selected_pdf = None
            self.root.setProperty("pdfFileLoaded", False)
            self.root.setPdfFile("No PDF file selected")
            return
        file_path = choose_file("Select PDF File", "PDF files (*.pdf)")
        if file_path:
            self.selected_pdf = file_path
            self.root.setPdfFile("PDF file: " + file_path)
            self.root.append_log(f"Selected PDF: {file_path}")
            self.root.setProperty("pdfFileLoaded", True)

    @pyqtSlot()
    def handle_select_public_key(self):
        if self.root.property("publicKeyLoaded"):
            self.public_key.reset_public_key()
            self.root.setProperty("publicKeyLoaded", False)
            self.root.setPublicKeyFile("No Public Key file selected")
            return

        file_path = choose_file("Select Public Key File", "Public key files (*.pem)")
        if file_path and self.public_key.load_public_key(file_path):
            self.root.setPublicKeyFile("Verification key: " + file_path)
            self.root.append_log(f"Selected Public Key: {file_path}")
            self.root.setProperty("publicKeyLoaded", True)

    @pyqtSlot()
    def handle_sign_pdf(self):
        if self.private_key.value is None or self.selected_pdf is None:
            return
        self.root.setProperty("signingInProgress", True)
        pdf_signer = PDFSigner(self.private_key.value)
        try:
            pdf_signer.sign(self.selected_pdf)
            self.root.append_log(f"PDF signed successfully: {self.selected_pdf}")
            self._show_message_dialog(
                "Success",
                f"PDF signed successfully: {self.selected_pdf}",
                QMessageBox.Icon.NoIcon,
            )
        except Exception as e:
            self.root.append_log(f"Error signing PDF: {str(e)}")
            self._show_message_dialog(
                "Error", f"Failed to sign PDF: {str(e)}", QMessageBox.Icon.Critical
            )
        finally:
            self.root.setProperty("signingInProgress", False)

    @pyqtSlot()
    def handle_verify_pdf(self):
        if self.public_key.value is None or self.selected_pdf is None:
            return
        self.root.setProperty("verificationInProgress", True)
        pdf_verifier = PDFVerifier(self.public_key.value)
        try:
            if pdf_verifier.verify(self.selected_pdf):
                self.root.append_log(f"PDF verified successfully: {self.selected_pdf}")
                self._show_message_dialog(
                    "Success",
                    f"PDF verified successfully: {self.selected_pdf}",
                    QMessageBox.Icon.NoIcon,
                )
            else:
                self.root.append_log(f"PDF verification failed: {self.selected_pdf}")
                self._show_message_dialog(
                    "Error",
                    f"PDF verification failed: {self.selected_pdf}",
                    QMessageBox.Icon.Critical,
                )
        except Exception as e:
            self.root.append_log(f"Error verifying PDF: {str(e)}")
            self._show_message_dialog(
                "Error", f"Failed to verify PDF: {str(e)}", QMessageBox.Icon.Critical
            )
        finally:
            self.root.setProperty("verificationInProgress", False)

    def check_pendrive(self) -> None:
        pen_drives = self.detector.find_all_pen_drives()

        if not pen_drives:
            self.private_key.reset_private_key()
            self.root.setProperty("privateKeyLoaded", False)
            self.root.setProperty("usbConnected", False)
            return
        if self.private_key.value is not None:
            return

        self.root.setProperty("usbConnected", True)
        self.root.append_log("USB device has been detected")

        pen_drive = self.detector.find_pen_drive_with_private_key(pen_drives)
        if pen_drive is None:
            self.root.append_log("Private key has not been found")
            self.private_key.reset_private_key()
            self.root.setProperty("privateKeyLoaded", False)
            return

        self.root.append_log("Private key has been found")

        dlg = PasswordDialog()
        if dlg.exec() == QDialog.DialogCode.Accepted:
            password = dlg.password
            try:
                if self.private_key.load_private_key(
                    self.detector.get_private_key_path(pen_drive), password
                ):
                    self.root.append_log("Private key has been loaded successfully")
                    self.root.setProperty("privateKeyLoaded", True)
            except FileNotFoundError:
                self.root.append_log(
                    "USB drive has been removed unexpectedly or private key file was deleted"
                )


def main():
    app = QApplication(sys.argv)
    engine = QQmlApplicationEngine()
    main_qml_path = os.path.join(os.path.dirname(__file__), "qml/Main.qml")
    engine.load(main_qml_path)

    if not engine.rootObjects():
        sys.exit(-1)

    root = engine.rootObjects()[0]
    backend = Backend(root)

    # Connect QML signals to Python slots
    root.selectPdf.connect(backend.handle_select_pdf)
    root.selectPublicKey.connect(backend.handle_select_public_key)
    root.signPdf.connect(backend.handle_sign_pdf)
    root.verifyPdf.connect(backend.handle_verify_pdf)

    # Log boot messages
    root.append_log("Application started...")
    root.append_log("Detecting USB devices...")

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
