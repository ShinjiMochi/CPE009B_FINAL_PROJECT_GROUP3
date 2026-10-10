from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QGridLayout,
    QLabel, QLineEdit, QTextEdit,
    QSpinBox, QPushButton
)

class CustomerDetails(QWidget):

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        title = QLabel("Customer Details")
        title.setStyleSheet(
            "font-size: 28px; font-weight: bold;"
        )

        layout.addWidget(title)
        form = QGridLayout()
        form.addWidget(
            QLabel("Full Name:"), 0, 0
        )
        form.addWidget(
            QLineEdit(), 0, 1
        )
        form.addWidget(
            QLabel("Contact Number:"), 1, 0
        )
        form.addWidget(
            QLineEdit(), 1, 1
        )
        form.addWidget(
            QLabel("Email:"), 2, 0
        )
        form.addWidget(
            QLineEdit(), 2, 1
        )
        form.addWidget(
            QLabel("Address:"), 3, 0
        )
        form.addWidget(
            QLineEdit(), 3, 1
        )
        form.addWidget(
            QLabel("Guests:"), 4, 0
        )
        form.addWidget(
            QSpinBox(), 4, 1
        )
        form.addWidget(
            QLabel("Special Requests:"), 5, 0
        )
        form.addWidget(
            QTextEdit(), 5, 1
        )
        layout.addLayout(form)
        layout.addWidget(
            QPushButton("Continue")
        )