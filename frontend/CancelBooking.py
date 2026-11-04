from PyQt6.QtCore import Qt, pyqtSignal, QRegularExpression
from PyQt6.QtGui import QRegularExpressionValidator
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QGridLayout, QLabel,
    QLineEdit, QPlainTextEdit, QPushButton, QMessageBox
)

from logic import cancellation_policy_lines
from managers import (
    booking_manager, generate_cancellation_slip, generate_receipt,
    save_cancellation_slip
)
from ui_common import make_secondary_button, make_title


class CancelBookingScreen(QWidget):
    """Find a booking by number + contact number, see the cancellation fee,
    and cancel it."""
    back_requested = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.booking = None

        # everything sits in one centered column
        column = QWidget()
        column.setMaximumWidth(760)
        column_layout = QVBoxLayout(column)
        column_layout.setContentsMargins(0, 0, 0, 0)

        title = make_title("Manage Booking")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        column_layout.addWidget(title)

        # ----- find the booking -----
        find_box = QGroupBox("Find your booking")
        find_layout = QGridLayout(find_box)

        self.number_input = QLineEdit()
        self.number_input.setPlaceholderText("e.g. 00001")
        self.number_input.setMaxLength(8)
        self.number_input.setValidator(
            QRegularExpressionValidator(QRegularExpression("[0-9]*"))
        )
        self.contact_input = QLineEdit()
        self.contact_input.setPlaceholderText("09XXXXXXXXX (primary guest)")
        self.contact_input.setMaxLength(13)
        self.find_button = QPushButton("Find booking")

        find_layout.addWidget(QLabel("Booking number:"), 0, 0)
        find_layout.addWidget(self.number_input, 0, 1)
        find_layout.addWidget(QLabel("Contact number:"), 1, 0)
        find_layout.addWidget(self.contact_input, 1, 1)
        find_layout.addWidget(self.find_button, 2, 1, Qt.AlignmentFlag.AlignRight)
        find_layout.setColumnStretch(1, 1)
        column_layout.addWidget(find_box)

        self.message_label = QLabel()
        self.message_label.setWordWrap(True)
        self.message_label.setStyleSheet("font-weight: bold;")
        column_layout.addWidget(self.message_label)

        # ----- booking + fee -----
        self.text = QPlainTextEdit()
        self.text.setReadOnly(True)
        self.text.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        self.text.setStyleSheet(
            'font-family: Consolas, "Courier New", monospace; font-size: 13px;'
        )
        column_layout.addWidget(self.text, 1)

        policy = QLabel("Cancellation fees:\n" + "\n".join(cancellation_policy_lines()))
        policy.setObjectName("muted")
        column_layout.addWidget(policy)

        buttons = QHBoxLayout()
        back = make_secondary_button("Back to Menu")
        self.cancel_button = QPushButton("Cancel This Booking")
        self.cancel_button.setEnabled(False)
        buttons.addWidget(back)
        buttons.addStretch()
        buttons.addWidget(self.cancel_button)
        column_layout.addLayout(buttons)

        layout = QVBoxLayout(self)
        layout.addWidget(column, 1, Qt.AlignmentFlag.AlignHCenter)

        back.clicked.connect(self.back_requested.emit)
        self.find_button.clicked.connect(self.on_find)
        self.cancel_button.clicked.connect(self.on_cancel)

    def show_message(self, text, ok=False):
        color = "#2e7d32" if ok else "red"
        self.message_label.setStyleSheet(f"font-weight: bold; color: {color};")
        self.message_label.setText(text)

    def show_text(self, content):
        self.text.setPlainText(content)
        longest = max((len(l) for l in content.splitlines()), default=40)
        char_width = self.text.fontMetrics().horizontalAdvance("0")
        self.text.setMinimumWidth(min(740, char_width * longest + 70))

    def on_find(self):
        self.booking = None
        self.cancel_button.setEnabled(False)
        self.text.clear()

        if not self.number_input.text():
            self.show_message("Enter your booking number.")
            return

        try:
            booking = booking_manager.find_booking(
                int(self.number_input.text()), self.contact_input.text()
            )
        except (ValueError, OSError) as error:
            self.show_message(str(error))
            return

        content = generate_receipt(booking)
        self.booking = booking

        try:
            fee = booking_manager.preview_cancellation(booking)
        except ValueError as error:
            self.show_text(content)
            self.show_message(str(error))
            return

        content += (
            "\n\nIF YOU CANCEL NOW\n"
            f"Cancellation fee ({fee['fee_rate'] * 100:.0f}%): PHP {fee['fee']:,.2f}\n"
            f"Refund: PHP {fee['refund']:,.2f}"
        )
        self.show_text(content)
        self.show_message(
            f"Booking found. Cancelling now costs a PHP {fee['fee']:,.2f} fee "
            f"and refunds PHP {fee['refund']:,.2f}.", ok=True
        )
        self.cancel_button.setEnabled(True)

    def on_cancel(self):
        if self.booking is None:
            return

        try:
            fee = booking_manager.preview_cancellation(self.booking)
        except ValueError as error:
            self.show_message(str(error))
            self.cancel_button.setEnabled(False)
            return

        answer = QMessageBox.question(
            self, "Cancel booking",
            f"Cancel booking {self.booking['booking_number']:05d}?\n\n"
            f"Cancellation fee: PHP {fee['fee']:,.2f}\n"
            f"Refund: PHP {fee['refund']:,.2f}\n\n"
            "This cannot be undone."
        )
        if answer != QMessageBox.StandardButton.Yes:
            return

        try:
            cancelled = booking_manager.cancel_booking(
                self.booking["booking_number"], self.contact_input.text()
            )
        except (ValueError, OSError) as error:
            QMessageBox.warning(self, "Cancellation Error", str(error))
            return

        self.booking = None
        self.cancel_button.setEnabled(False)
        slip = generate_cancellation_slip(cancelled)
        self.show_text(slip)

        try:
            path = save_cancellation_slip(cancelled)
            self.show_message(f"Booking cancelled. Slip saved to {path}", ok=True)
        except OSError:
            self.show_message("Booking cancelled. (The slip could not be saved.)", ok=True)

    def reset(self):
        self.booking = None
        self.number_input.clear()
        self.contact_input.clear()
        self.message_label.clear()
        self.text.clear()
        self.cancel_button.setEnabled(False)
