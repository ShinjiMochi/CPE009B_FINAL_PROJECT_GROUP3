import os
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QGroupBox, QScrollArea,
    QLabel, QSpinBox, QCheckBox, QPushButton, QMessageBox, QComboBox, QLineEdit
)

from logic import (
    MINIMUM_GUESTS, DISCOUNT_TYPES,
    validate_guests, create_guest_info, calculate_totals,
    verify_discount, get_service_spec
)
from ui_common import (
    ImageBox, BannerBox, IMAGE_FOLDER, make_title, make_secondary_button
)

NO_DISCOUNT = "No discount"
OK_COLOR = "#2e7d32"
ERROR_COLOR = "red"


class GuestOptions(QWidget):
    # emits: guests, discount_info, discount, services
    continued = pyqtSignal(dict)
    back_requested = pyqtSignal()

    def __init__(self, services=None):
        super().__init__()

        self.services = services or {}
        self.service_checkboxes = {}
        self.room_name = ""
        self.room_charge = 0.0
        self.max_guests = 99          # set from the selected rooms
        self.discount_info = None     # filled in once the ID / voucher is verified

        form = QWidget()
        form_layout = QVBoxLayout(form)

        form_layout.addWidget(BannerBox("images/guest_banner", max_height=250))
        form_layout.addWidget(make_title("Guest Options"))
        form_layout.addWidget(self.make_guest_box())
        form_layout.addWidget(self.make_discount_box())
        form_layout.addWidget(self.make_services_box())
        form_layout.addStretch()

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(form)

        layout = QHBoxLayout(self)
        layout.addWidget(scroll, 3)
        layout.addWidget(self.make_summary_box(), 1)

        self.family_check.toggled.connect(self.toggle_family_fields)
        self.guest_spin.valueChanged.connect(self.update_summary)
        self.senior_spin.valueChanged.connect(self.update_summary)
        self.child_spin.valueChanged.connect(self.update_summary)
        for checkbox in self.service_checkboxes.values():
            checkbox.toggled.connect(self.update_summary)

        self.discount_combo.currentTextChanged.connect(self.on_discount_type_changed)
        self.holder_input.textChanged.connect(self.invalidate_discount)
        self.code_input.textChanged.connect(self.invalidate_discount)
        self.verify_button.clicked.connect(self.on_verify)

        self.continue_button.clicked.connect(self.on_continue)
        self.back_button.clicked.connect(self.back_requested.emit)

        self.refresh_guest_note()
        self.on_discount_type_changed(NO_DISCOUNT)
        self.update_summary()

    def make_note(self, text):
        note = QLabel(text)
        note.setWordWrap(True)
        note.setObjectName("muted")
        return note

    # ---------- guests ----------
    def make_guest_box(self):
        box = QGroupBox("Guests")
        layout = QHBoxLayout(box)

        self.guest_spin = QSpinBox()
        self.guest_spin.setMinimum(MINIMUM_GUESTS)
        self.guest_spin.setValue(MINIMUM_GUESTS)
        self.family_check = QCheckBox("This is a family booking")
        self.senior_spin = QSpinBox()
        self.child_spin = QSpinBox()
        self.senior_spin.setEnabled(False)
        self.child_spin.setEnabled(False)

        self.guest_note = self.make_note("")

        grid = QGridLayout()
        grid.addWidget(QLabel("Number of guests:"), 0, 0)
        grid.addWidget(self.guest_spin, 0, 1)
        grid.addWidget(self.family_check, 1, 0, 1, 2)
        grid.addWidget(QLabel("Seniors:"), 2, 0)
        grid.addWidget(self.senior_spin, 2, 1)
        grid.addWidget(QLabel("Children:"), 3, 0)
        grid.addWidget(self.child_spin, 3, 1)
        grid.addWidget(self.guest_note, 4, 0, 1, 2)
        layout.addLayout(grid, 1)
        return box

    def refresh_guest_note(self):
        limit = f"maximum of {self.max_guests} for the selected rooms" \
            if self.max_guests < 99 else "limited by the rooms you select"
        self.guest_note.setText(
            f"Minimum of {MINIMUM_GUESTS} guests, {limit}. Seniors and children "
            "are counted in the total. Each guest's name and contact number "
            "are entered on the Details screen."
        )

    # ---------- discount ----------
    def make_discount_box(self):
        box = QGroupBox("Discount (optional)")
        layout = QHBoxLayout(box)
        layout.addWidget(
            ImageBox("images/discount", 70, 70),
            alignment=Qt.AlignmentFlag.AlignTop
        )

        self.discount_combo = QComboBox()
        self.discount_combo.addItem(NO_DISCOUNT)
        self.discount_combo.addItems(DISCOUNT_TYPES.keys())

        self.holder_label = QLabel("ID holder's full name:")
        self.holder_input = QLineEdit()
        self.code_label = QLabel("ID number:")
        self.code_input = QLineEdit()
        self.verify_button = QPushButton("Verify")
        self.discount_status = QLabel()
        self.discount_status.setWordWrap(True)
        self.discount_details = self.make_note("")

        grid = QGridLayout()
        grid.addWidget(QLabel("Discount type:"), 0, 0)
        grid.addWidget(self.discount_combo, 0, 1)
        grid.addWidget(self.holder_label, 1, 0)
        grid.addWidget(self.holder_input, 1, 1)
        grid.addWidget(self.code_label, 2, 0)
        grid.addWidget(self.code_input, 2, 1)
        grid.addWidget(self.verify_button, 3, 0)
        grid.addWidget(self.discount_status, 3, 1)
        grid.addWidget(self.discount_details, 4, 0, 1, 2)
        grid.setColumnStretch(1, 1)
        layout.addLayout(grid, 1)
        return box

    def discount_overview(self):
        """Text for the 'No discount' state: every discount and its rules."""
        lines = [f"{name}: {info['description']}" for name, info in DISCOUNT_TYPES.items()]
        lines.append(
            "Only one discount per booking. Discounts apply to the room charge "
            "only. Dining and additional services are not discounted."
        )
        return "\n\n".join(lines)

    def on_discount_type_changed(self, name):
        for field in (self.holder_input, self.code_input):
            field.blockSignals(True)
            field.clear()
            field.blockSignals(False)
        self.discount_info = None
        self.discount_status.clear()

        info = DISCOUNT_TYPES.get(name)
        chosen = info is not None
        is_id = chosen and info["kind"] == "id"

        for widget in (self.code_label, self.code_input, self.verify_button):
            widget.setVisible(chosen)
        for widget in (self.holder_label, self.holder_input):
            widget.setVisible(is_id)

        if chosen:
            self.code_label.setText(f"{info['id_label']}:")
            self.discount_details.setText(
                f"{info['description']}\n"
                "Applies to the room charge only. Dining and additional services "
                "are not discounted."
            )
        else:
            self.discount_details.setText(self.discount_overview())

        self.update_summary()

    def invalidate_discount(self, *args):
        """Editing the ID or code after verifying means it must be verified again."""
        if self.discount_info is not None:
            self.discount_info = None
            self.discount_status.clear()
            self.update_summary()

    def on_verify(self):
        try:
            self.discount_info = verify_discount(
                self.discount_combo.currentText(),
                self.code_input.text(),
                self.holder_input.text(),
                self.room_charge
            )
        except ValueError as error:
            self.discount_info = None
            self.discount_status.setStyleSheet(f"font-weight: bold; color: {ERROR_COLOR};")
            self.discount_status.setText(str(error))
        else:
            rate = self.discount_info["rate"] * 100
            self.discount_status.setStyleSheet(f"font-weight: bold; color: {OK_COLOR};")
            self.discount_status.setText(f"Verified: {rate:.0f}% off the room charge.")
        self.update_summary()

    def discount_pending(self):
        """A discount type is chosen but not verified yet."""
        return self.discount_combo.currentText() != NO_DISCOUNT and self.discount_info is None

    # ---------- services ----------
    def make_services_box(self):
        box = QGroupBox("Additional Services")
        layout = QGridLayout(box)

        service_images = {
            "Airport Transfer": "airport_transfer",
            "Extra Bed": "extra_bed",
            "Extra Pillow & Blanket Set": "extra_pillow_blanket_set",
            "Late Check-out": "late_check_out",
            "Laundry Service": "laundry_service",
            "Spa Massage": "spa_massage",
        }

        if not self.services:
            layout.addWidget(QLabel("No services available yet."), 0, 0)

        for index, (name, price) in enumerate(self.services.items()):
            item = QVBoxLayout()

            image_name = service_images.get(name, "services")
            item.addWidget(
                ImageBox(image_name, 150, 100,
                         folder=os.path.join(IMAGE_FOLDER, "services")),
                alignment=Qt.AlignmentFlag.AlignCenter
            )
            item.addWidget(
                QLabel(f"{name} - ₱{price:,.2f}"),
                alignment=Qt.AlignmentFlag.AlignCenter
            )

            spec = self.make_note(get_service_spec(name))
            spec.setAlignment(Qt.AlignmentFlag.AlignCenter)
            item.addWidget(spec)

            checkbox = QCheckBox("Add")
            self.service_checkboxes[name] = checkbox
            item.addWidget(checkbox, alignment=Qt.AlignmentFlag.AlignCenter)

            layout.addLayout(item, index // 3, index % 3)

        return box

    # ---------- summary ----------
    def make_summary_box(self):
        box = QGroupBox("Booking Summary")
        box.setMinimumWidth(240)
        layout = QVBoxLayout(box)

        self.summary_label = QLabel()
        self.summary_label.setWordWrap(True)
        layout.addWidget(self.summary_label)

        self.warning_label = QLabel()
        self.warning_label.setStyleSheet("color: red; font-weight: bold;")
        self.warning_label.setWordWrap(True)
        layout.addWidget(self.warning_label)
        layout.addStretch()

        self.back_button = make_secondary_button("Back")
        self.continue_button = QPushButton("Continue")
        layout.addWidget(self.back_button)
        layout.addWidget(self.continue_button)
        return box

    def toggle_family_fields(self, checked):
        self.senior_spin.setEnabled(checked)
        self.child_spin.setEnabled(checked)
        if not checked:
            self.senior_spin.setValue(0)
            self.child_spin.setValue(0)
        self.update_summary()

    def set_booking(self, rooms_text, room_charge, max_guests):
        """Called by main.py with the rooms picked and the room charge."""
        if room_charge != self.room_charge:
            # the charge changed, so a voucher minimum may no longer be met
            self.discount_combo.setCurrentIndex(0)

        self.room_name = rooms_text
        self.room_charge = room_charge
        self.max_guests = max_guests

        self.guest_spin.setMaximum(max_guests)
        self.senior_spin.setMaximum(max_guests)
        self.child_spin.setMaximum(max_guests)
        self.refresh_guest_note()
        self.update_summary()

    def reset(self):
        """Clears the screen for a new booking."""
        self.guest_spin.setMaximum(99)
        self.guest_spin.setValue(MINIMUM_GUESTS)
        self.family_check.setChecked(False)
        self.discount_combo.setCurrentIndex(0)
        for checkbox in self.service_checkboxes.values():
            checkbox.setChecked(False)
        self.room_charge = 0.0
        self.room_name = ""
        self.max_guests = 99
        self.refresh_guest_note()
        self.update_summary()

    def get_selected_services(self):
        return [
            {"name": name, "price": self.services[name], "spec": get_service_spec(name)}
            for name, checkbox in self.service_checkboxes.items()
            if checkbox.isChecked()
        ]

    def update_summary(self, *args):
        totals = calculate_totals(
            self.room_charge,
            self.discount_info,
            self.get_selected_services()
        )
        discount = totals["discount"]

        if discount["discount_used"]:
            discount_line = (
                f"Discount ({discount['discount_type']}, "
                f"{discount['discount_rate'] * 100:.0f}%): "
                f"-₱{discount['discount_amount']:,.2f}\n"
            )
        else:
            discount_line = f"Discount: -₱{discount['discount_amount']:,.2f}\n"

        self.summary_label.setText(
            f"Rooms: {self.room_name or '-'}\n"
            f"Guests: {self.guest_spin.value()}\n\n"
            f"Room charge: ₱{discount['room_charge']:,.2f}\n"
            f"{discount_line}"
            f"Room after discount: ₱{discount['room_charge_after_discount']:,.2f}\n"
            f"Services: ₱{totals['services_total']:,.2f}\n\n"
            f"Total so far: ₱{totals['total']:,.2f}\n"
            "(dining is added later)"
        )

        errors = validate_guests(
            self.guest_spin.value(),
            self.family_check.isChecked(),
            self.senior_spin.value(),
            self.child_spin.value(),
            self.max_guests
        )
        if self.discount_pending():
            errors.append("Verify your discount, or choose 'No discount'.")
        self.warning_label.setText("\n".join(errors))
        self.continue_button.setEnabled(not errors)

    def on_continue(self):
        if self.discount_pending():
            QMessageBox.warning(
                self, "Discount not verified",
                "Verify your discount, or choose 'No discount'."
            )
            return

        try:
            guest_info = create_guest_info(
                self.guest_spin.value(),
                self.family_check.isChecked(),
                self.senior_spin.value(),
                self.child_spin.value(),
                self.max_guests
            )
        except ValueError as error:
            QMessageBox.warning(self, "Invalid Guest Information", str(error))
            return

        services = self.get_selected_services()
        self.continued.emit({
            "guests": guest_info.to_dict(),
            "discount_info": self.discount_info,
            "discount": calculate_totals(
                self.room_charge, self.discount_info, services
            )["discount"],
            "services": services
        })


if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication

    from logic import get_additional_services
    from ui_common import apply_theme

    app = QApplication(sys.argv)
    apply_theme(app)
    screen = GuestOptions(get_additional_services())
    screen.set_booking("1 x Economy", 1500, 2)
    screen.continued.connect(print)
    screen.resize(1100, 700)
    screen.show()
    sys.exit(app.exec())
