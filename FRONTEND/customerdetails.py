from PyQt6.QtCore import pyqtSignal, QRegularExpression
from PyQt6.QtGui import QRegularExpressionValidator
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QGridLayout, QLabel, QLineEdit, QTextEdit
)

from logic import validate_customer, create_customer_info
from ui_common import make_title, make_nav_buttons


class CustomerDetails(QWidget):
    continued = pyqtSignal(dict)
    back_requested = pyqtSignal()

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.addWidget(make_title("Customer Details"))

        self.name_input = QLineEdit()
        self.contact_input = QLineEdit()
        self.contact_input.setPlaceholderText("09XXXXXXXXX")
        self.contact_input.setMaxLength(11)   # digits only, 11 max
        self.contact_input.setValidator(
            QRegularExpressionValidator(QRegularExpression("[0-9]*"))
        )
        self.email_input = QLineEdit()
        self.address_input = QLineEdit()
        self.requests_input = QTextEdit()
        self.requests_input.setFixedHeight(100)

        self.fields = {
            "full_name": ("Full Name:", self.name_input),
            "contact_number": ("Contact Number:", self.contact_input),
            "email": ("Email:", self.email_input),
            "address": ("Address:", self.address_input),
            "special_requests": ("Special Requests (optional):", self.requests_input),
        }
        self.error_labels = {}

        form = QGridLayout()
        for row, (key, (text, widget)) in enumerate(self.fields.items()):
            form.addWidget(QLabel(text), row, 0)
            form.addWidget(widget, row, 1)
            error = QLabel()
            error.setStyleSheet("color: red;")
            self.error_labels[key] = error
            form.addWidget(error, row, 2)
        form.setColumnStretch(1, 1)
        layout.addLayout(form)
        layout.addStretch()

        buttons, back, continue_button = make_nav_buttons()
        layout.addLayout(buttons)

        back.clicked.connect(self.back_requested.emit)
        continue_button.clicked.connect(self.on_continue)

    def values(self):
        return (
            self.name_input.text(),
            self.contact_input.text(),
            self.email_input.text(),
            self.address_input.text(),
            self.requests_input.toPlainText()
        )

    def on_continue(self):
        errors = validate_customer(*self.values())

        for key, label in self.error_labels.items():
            label.setText(errors.get(key, ""))

        if errors:
            return

        self.continued.emit(create_customer_info(*self.values()))

    def reset(self):
        for key, (_, widget) in self.fields.items():
            widget.clear()
            self.error_labels[key].clear()
