from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QFontDatabase
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPlainTextEdit, QPushButton, QMessageBox
)

from ReceiptManager import generate_receipt, save_receipt, print_receipt


class ReceiptScreen(QWidget):
    new_booking_requested = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.booking_number = None

        layout = QVBoxLayout(self)

        title = QLabel("Booking Receipt")
        title.setStyleSheet("font-size: 28px; font-weight: bold;")
        layout.addWidget(title)

        self.text = QPlainTextEdit()
        self.text.setReadOnly(True)
        self.text.setFont(QFontDatabase.systemFont(QFontDatabase.SystemFont.FixedFont))
        layout.addWidget(self.text)

        buttons = QHBoxLayout()
        save = QPushButton("Save Receipt")
        print_button = QPushButton("Print Receipt")
        new_booking = QPushButton("New Booking")
        buttons.addWidget(save)
        buttons.addWidget(print_button)
        buttons.addStretch()
        buttons.addWidget(new_booking)
        layout.addLayout(buttons)

        save.clicked.connect(self.on_save)
        print_button.clicked.connect(self.on_print)
        new_booking.clicked.connect(self.new_booking_requested.emit)

    def show_receipt(self, booking_number):
        self.booking_number = booking_number
        try:
            self.text.setPlainText(generate_receipt(booking_number))
        except (ValueError, OSError) as error:
            self.text.setPlainText("")
            QMessageBox.warning(self, "Receipt Error", str(error))

    def on_save(self):
        if self.booking_number is None:
            return
        try:
            path = save_receipt(self.booking_number)
        except (ValueError, OSError) as error:
            QMessageBox.warning(self, "Receipt Error", str(error))
            return
        QMessageBox.information(self, "Receipt Saved", f"Saved to {path}")

    def on_print(self):
        if self.booking_number is None:
            return
        try:
            print_receipt(self.booking_number)
        except (ValueError, OSError) as error:
            QMessageBox.warning(self, "Print Error", str(error))
            return
        QMessageBox.information(self, "Print", "Receipt sent to the printer.")

    def reset(self):
        self.booking_number = None
        self.text.clear()
