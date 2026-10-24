from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPlainTextEdit, QPushButton, QMessageBox
)

from managers import generate_receipt, save_receipt, print_receipt
from ui_common import make_title

# shows the receipt. the user can save it, print it, or start a new booking
class ReceiptScreen(QWidget):
    # tells main.py to reset everything and go back to the menu
    new_booking_requested = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.booking = None

        column = QWidget()
        column_layout = QVBoxLayout(column)
        column_layout.setContentsMargins(0, 0, 0, 0)

        title = make_title("Booking Receipt")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        column_layout.addWidget(title)

        self.text = QPlainTextEdit()
        self.text.setReadOnly(True)
        # monospace font so the columns line up
        self.text.setStyleSheet(
            'font-family: Consolas, "Courier New", monospace; font-size: 13px;'
        )
        # no wrapping so the lines don't break
        self.text.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        column_layout.addWidget(self.text, 1)

        buttons = QHBoxLayout()
        save = QPushButton("Save Receipt")
        print_button = QPushButton("Print Receipt")
        new_booking = QPushButton("New Booking")
        buttons.addWidget(save)
        buttons.addWidget(print_button)
        buttons.addStretch()
        buttons.addWidget(new_booking)
        column_layout.addLayout(buttons)

        layout = QVBoxLayout(self)
        layout.addWidget(column, 1, Qt.AlignmentFlag.AlignHCenter)

        save.clicked.connect(self.on_save)
        print_button.clicked.connect(self.on_print)
        new_booking.clicked.connect(self.new_booking_requested.emit)

    # shows the receipt and makes the box wide enough for it
    def show_receipt(self, booking):
        """booking is the dict returned by booking_manager.create_booking()."""
        self.booking = booking
        content = generate_receipt(booking)
        self.text.setPlainText(content)

        # find the longest line to know how wide the box should be
        longest = max((len(line) for line in content.splitlines()), default=40)
        char_width = self.text.fontMetrics().horizontalAdvance("0")
        self.text.setMinimumWidth(char_width * longest + 70)

    # saves the receipt as .txt and .json in the Receipts folder
    def on_save(self):
        if self.booking is None:
            return
        try:
            txt_path, json_path = save_receipt(self.booking)
        except OSError as error:
            QMessageBox.warning(self, "Receipt Error", str(error))
            return
        QMessageBox.information(
            self, "Receipt Saved", f"Saved to:\n{txt_path}\n{json_path}"
        )

    # saves the receipt then sends it to the printer
    def on_print(self):
        if self.booking is None:
            return
        try:
            print_receipt(self.booking)
        except OSError as error:
            QMessageBox.warning(self, "Print Error", str(error))
            return
        QMessageBox.information(self, "Print", "Receipt sent to the printer.")

    # clears the receipt for a new booking
    def reset(self):
        self.booking = None
        self.text.clear()
