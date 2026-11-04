from PyQt6.QtCore import Qt, pyqtSignal, QRegularExpression
from PyQt6.QtGui import QRegularExpressionValidator
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QGroupBox, QScrollArea,
    QLabel, QLineEdit, QTextEdit, QPushButton
)

from logic import (
    MINIMUM_GUESTS, MAX_SPECIAL_REQUESTS, validate_customer, create_customer_info,
    validate_guest_list, create_guest_list, validate_guests, calculate_totals,
    format_when, rooms_summary
)
from ui_common import BannerBox, make_title, make_secondary_button


class GuestRow(QWidget):
    """One additional guest: name + contact number + a Remove button."""
    removed = pyqtSignal(object)

    def __init__(self):
        super().__init__()
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(2)

        row = QHBoxLayout()
        self.label = QLabel()
        self.label.setFixedWidth(60)
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Full name")
        self.contact_input = QLineEdit()
        self.contact_input.setPlaceholderText("09XXXXXXXXX (optional)")
        self.contact_input.setMaxLength(11)
        self.contact_input.setValidator(
            QRegularExpressionValidator(QRegularExpression("[0-9]*"))
        )
        self.remove_button = make_secondary_button("Remove")
        self.remove_button.clicked.connect(lambda: self.removed.emit(self))

        row.addWidget(self.label)
        row.addWidget(self.name_input, 2)
        row.addWidget(self.contact_input, 1)
        row.addWidget(self.remove_button)
        outer.addLayout(row)

        self.error = QLabel()
        self.error.setStyleSheet("color: red; font-weight: bold;")
        self.error.setWordWrap(True)
        outer.addWidget(self.error)

    def set_number(self, number):
        self.label.setText(f"Guest {number}")

    def values(self):
        return {"name": self.name_input.text(), "contact": self.contact_input.text()}

    def show_errors(self, errors):
        self.error.setText(" ".join(errors.values()))


# screen where the user types the primary guest's details, adds the other
# guests, and any general requests (always the last box on the screen)
class CustomerDetails(QWidget):
    # continued sends the customer info to main.py, back_requested tells it to go back
    continued = pyqtSignal(dict)
    back_requested = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.data = None
        self.max_guests = 99
        self.guest_rows = []
        self._last_guest_count = None

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
        self.requests_input.setPlaceholderText(
            "Anything the hotel should know for the whole booking "
            "(late arrival, quiet floor, allergies, celebrations...)"
        )

        # key -> (label text, input box). Keys match the ones logic.py uses for errors
        self.fields = {
            "full_name": ("Full Name:", self.name_input),
            "contact_number": ("Contact Number:", self.contact_input),
            "email": ("Email:", self.email_input),
            "address": ("Address:", self.address_input),
        }
        self.error_labels = {}

        form = QWidget()
        form_layout = QVBoxLayout(form)
        form_layout.addWidget(BannerBox("images/guest_banner", max_height=250))
        form_layout.addWidget(make_title("Guest Details"))
        form_layout.addWidget(self.make_details_box())
        form_layout.addWidget(self.make_guests_box())
        form_layout.addWidget(self.make_requests_box())
        form_layout.addStretch()

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(form)

        layout = QHBoxLayout(self)
        layout.addWidget(scroll, 3)
        layout.addWidget(self.make_summary_box(), 1)

        self.back_button.clicked.connect(self.back_requested.emit)
        self.continue_button.clicked.connect(self.on_continue)
        self.add_guest_button.clicked.connect(self.add_guest_row)

    # ---------- Main guest ----------
    def make_details_box(self):
        box = QGroupBox("Primary Guest (the person booking)")
        grid = QGridLayout(box)

        # Shows the input field and the error message under when called
        for index, (key, (text, widget)) in enumerate(self.fields.items()):
            row = index * 2
            grid.addWidget(QLabel(text), row, 0)
            grid.addWidget(widget, row, 1)

            error = QLabel()
            error.setStyleSheet("color: red; font-weight: bold;")
            error.setWordWrap(True)
            self.error_labels[key] = error
            grid.addWidget(error, row + 1, 1)

        grid.setColumnStretch(1, 1)
        return box

    # ---------- Other guests ----------

    def make_guests_box(self):
        box = QGroupBox("Other Guests")
        layout = QVBoxLayout(box)

        self.limit_label = QLabel()
        self.limit_label.setObjectName("muted")
        self.limit_label.setWordWrap(True)
        layout.addWidget(self.limit_label)

        self.rows_layout = QVBoxLayout()
        layout.addLayout(self.rows_layout)

        self.guest_warning = QLabel()
        self.guest_warning.setStyleSheet("color: red; font-weight: bold;")
        self.guest_warning.setWordWrap(True)
        layout.addWidget(self.guest_warning)

        buttons = QHBoxLayout()
        self.add_guest_button = make_secondary_button("+ Add guest")
        buttons.addWidget(self.add_guest_button)
        buttons.addStretch()
        layout.addLayout(buttons)
        return box

    def total_guests(self):
        return 1 + len(self.guest_rows)

    def add_guest_row(self):
        if self.total_guests() >= self.max_guests:
            return
        row = GuestRow()
        row.removed.connect(self.remove_guest_row)
        self.guest_rows.append(row)
        self.rows_layout.addWidget(row)
        self.update_guest_controls()

    def remove_guest_row(self, row):
        if self.total_guests() <= MINIMUM_GUESTS:
            return
        self.guest_rows.remove(row)
        self.rows_layout.removeWidget(row)
        row.deleteLater()
        self.update_guest_controls()

    def update_guest_controls(self):
        total = self.total_guests()
        for number, row in enumerate(self.guest_rows, start=2):
            row.set_number(number)
            row.remove_button.setEnabled(total > MINIMUM_GUESTS)
        self.add_guest_button.setEnabled(total < self.max_guests)
        self.limit_label.setText(
            f"{total} of {self.max_guests} guests (the most the selected rooms hold). "
            "Name is required for every guest; a contact number is optional."
        )
        self.refresh_summary()

    # ---------- General requests ----------
    def make_requests_box(self):
        box = QGroupBox("General Booking Requests (optional)")
        layout = QVBoxLayout(box)
        layout.addWidget(self.requests_input)

        self.requests_error = QLabel()
        self.requests_error.setStyleSheet("color: red; font-weight: bold;")
        self.requests_error.setWordWrap(True)
        layout.addWidget(self.requests_error)
        return box

    # ---------- Summary box ----------
    def make_summary_box(self):
        box = QGroupBox("Booking Summary")
        box.setMinimumWidth(240)
        layout = QVBoxLayout(box)

        self.summary_label = QLabel()
        self.summary_label.setWordWrap(True)
        layout.addWidget(self.summary_label)
        layout.addStretch()

        self.back_button = make_secondary_button("Back")
        self.continue_button = QPushButton("Continue")
        layout.addWidget(self.back_button)
        layout.addWidget(self.continue_button)
        return box

    # main.py calls this with the data collected so far
    def set_summary(self, data):
        self.data = data
        self.max_guests = data.get("max_guests", 99)
        wanted = data["guests"]["total_guests"]

        if wanted != self._last_guest_count:
            self._last_guest_count = wanted
            target = max(wanted, MINIMUM_GUESTS) - 1
            while len(self.guest_rows) < target:
                self.add_guest_row()
            while len(self.guest_rows) > target:
                self.remove_guest_row(self.guest_rows[-1])
        self.update_guest_controls()

    def refresh_summary(self):
        data = self.data
        if data is None:
            self.summary_label.clear()
            return

        totals = calculate_totals(
            data["room_charge"], data.get("discount_info"), data["services"]
        )
        discount = totals["discount"]
        unit = "hour(s)" if data["duration_type"] == "Hourly" else "day(s)"

        discount_line = ""
        if discount["discount_used"]:
            discount_line = (
                f"Discount ({discount['discount_type']}): "
                f"-₱{discount['discount_amount']:,.2f}\n"
            )

        self.summary_label.setText(
            f"Rooms: {rooms_summary(data['rooms'])}\n"
            f"Stay: {data['duration']} {unit}\n"
            f"Check-in: {format_when(data.get('check_in'))}\n"
            f"Check-out: {format_when(data.get('check_out'))}\n"
            f"Guests: {self.total_guests()}\n\n"
            f"Room charge: ₱{discount['room_charge']:,.2f}\n"
            f"{discount_line}"
            f"Services: ₱{totals['services_total']:,.2f}\n\n"
            f"Total so far: ₱{totals['total']:,.2f}\n"
            "(dining is added later)"
        )

    # gets user input in the order logic.py needs
    def values(self):
        return (
            self.name_input.text(),
            self.contact_input.text(),
            self.email_input.text(),
            self.address_input.text(),
            self.requests_input.toPlainText()
        )

    # checks the inputs. if there are errors show them, if not send the data
    def on_continue(self):
        errors = validate_customer(*self.values())
        for key, label in self.error_labels.items():
            label.setText(errors.get(key, ""))
        self.requests_error.setText(errors.get("special_requests", ""))

        guest_values = [row.values() for row in self.guest_rows]
        guest_errors = validate_guest_list(guest_values)
        for index, row in enumerate(self.guest_rows):
            row.show_errors(guest_errors.get(index, {}))

        guests = (self.data or {}).get("guests", {})
        count_errors = validate_guests(
            self.total_guests(),
            guests.get("is_family", False),
            guests.get("seniors", 0),
            guests.get("children", 0),
            self.max_guests
        )
        self.guest_warning.setText("\n".join(count_errors))

        if errors or guest_errors or count_errors:
            return

        self.continued.emit({
            "customer": create_customer_info(*self.values()),
            "guest_list": create_guest_list(guest_values),
        })

    # Resets the booking app for when "New booking is pressed"
    def reset(self):
        for key, (_, widget) in self.fields.items():
            widget.clear()
            self.error_labels[key].clear()
        self.requests_input.clear()
        self.requests_error.clear()
        self.guest_warning.clear()

        for row in list(self.guest_rows):
            self.rows_layout.removeWidget(row)
            row.deleteLater()
        self.guest_rows.clear()

        self.data = None
        self.max_guests = 99
        self._last_guest_count = None
        self.summary_label.clear()
        self.limit_label.clear()
