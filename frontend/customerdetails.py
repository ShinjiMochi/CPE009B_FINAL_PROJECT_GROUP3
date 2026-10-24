from PyQt6.QtCore import Qt, pyqtSignal, QRegularExpression
from PyQt6.QtGui import QRegularExpressionValidator
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QGroupBox, QScrollArea,
    QLabel, QLineEdit, QTextEdit, QPushButton
)

from logic import validate_customer, create_customer_info, calculate_totals, format_when
from ui_common import BannerBox, make_title, make_secondary_button


# screen where the user types their name, contact, email and address
# it uses the same layout as GuestOptions: banner + form on the left, summary on the right
class CustomerDetails(QWidget):
    # continued sends the customer info to main.py, back_requested tells it to go back
    continued = pyqtSignal(dict)
    back_requested = pyqtSignal()

    def __init__(self):
        super().__init__()

        self.name_input = QLineEdit()
        self.contact_input = QLineEdit()
        self.contact_input.setPlaceholderText("09XXXXXXXXX")
        self.contact_input.setMaxLength(11)   # digits only, 11 max
        # only lets the user type numbers
        self.contact_input.setValidator(
            QRegularExpressionValidator(QRegularExpression("[0-9]*"))
        )
        self.email_input = QLineEdit()
        self.address_input = QLineEdit()
        self.requests_input = QTextEdit()
        self.requests_input.setFixedHeight(100)

        # each field: key -> (label text, input box). the keys are the same ones logic.py uses for errors
        self.fields = {
            "full_name": ("Guest Name:", self.name_input),
            "contact_number": ("Contact Number:", self.contact_input),
            "email": ("Email:", self.email_input),
            "address": ("Address:", self.address_input),
            "special_requests": ("Special Requests (optional):", self.requests_input),
        }
        # a red label for each field to show its error
        self.error_labels = {}

        # left side is the form, put inside a scroll area (same as GuestOptions)
        form = QWidget()
        form_layout = QVBoxLayout(form)
        form_layout.addWidget(BannerBox("images/guest_banner", max_height=250))
        form_layout.addWidget(make_title("Guest Details"))
        form_layout.addWidget(self.make_details_box())
        form_layout.addStretch()

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(form)

        # form is 3 parts wide, summary is 1 part
        layout = QHBoxLayout(self)
        layout.addWidget(scroll, 3)
        layout.addWidget(self.make_summary_box(), 1)

        self.back_button.clicked.connect(self.back_requested.emit)
        self.continue_button.clicked.connect(self.on_continue)

    # box that holds all the input fields
    def make_details_box(self):
        box = QGroupBox("Guest Information")
        grid = QGridLayout(box)

        # each field takes 2 grid rows: the input, then its error message under it
        for index, (key, (text, widget)) in enumerate(self.fields.items()):
            row = index * 2
            label = QLabel(text)
            # the big text box label lines up with the top of the box
            if isinstance(widget, QTextEdit):
                grid.addWidget(label, row, 0, Qt.AlignmentFlag.AlignTop)
            else:
                grid.addWidget(label, row, 0)
            grid.addWidget(widget, row, 1)

            error = QLabel()
            error.setStyleSheet("color: red; font-weight: bold;")
            error.setWordWrap(True)
            self.error_labels[key] = error
            grid.addWidget(error, row + 1, 1)

        grid.setColumnStretch(1, 1)
        return box

    # right side: shows what was picked in the earlier steps, plus the buttons
    def make_summary_box(self):
        box = QGroupBox("Booking Summary")
        box.setMinimumWidth(240)
        layout = QVBoxLayout(box)

        self.summary_label = QLabel()
        layout.addWidget(self.summary_label)
        layout.addStretch()

        self.back_button = make_secondary_button("Back")
        self.continue_button = QPushButton("Continue")
        layout.addWidget(self.back_button)
        layout.addWidget(self.continue_button)
        return box

    # main.py calls this with the data collected so far so the summary can show it
    def set_summary(self, data):
        totals = calculate_totals(
            data["room_charge"],
            data["discount"]["discount_used"],
            data["services"]
        )
        discount = totals["discount"]
        unit = "hour(s)" if data["duration_type"] == "Hourly" else "day(s)"

        self.summary_label.setText(
            f"Room: {data['room'].room_type}\n"
            f"Stay: {data['duration']} {unit}\n"
            f"Check-in: {format_when(data.get('check_in'))}\n"
            f"Check-out: {format_when(data.get('check_out'))}\n"
            f"Guests: {data['guests']['total_guests']}\n\n"
            f"Room after discount: ₱{discount['room_charge_after_discount']:,.2f}\n"
            f"Services: ₱{totals['services_total']:,.2f}\n\n"
            f"Total so far: ₱{totals['total']:,.2f}\n"
            "(dining is added later)"
        )

    # gets what the user typed, in the same order that logic.py wants
    def values(self):
        return (
            self.name_input.text(),
            self.contact_input.text(),
            self.email_input.text(),
            self.address_input.text(),
            self.requests_input.toPlainText()
        )

    # checks the inputs. if there are errors show them, if not send the data to the next screen
    def on_continue(self):
        errors = validate_customer(*self.values())

        for key, label in self.error_labels.items():
            label.setText(errors.get(key, ""))

        if errors:
            return

        self.continued.emit(create_customer_info(*self.values()))

    # clears all the inputs, errors and the summary for a new booking
    def reset(self):
        for key, (_, widget) in self.fields.items():
            widget.clear()
            self.error_labels[key].clear()
        self.summary_label.clear()