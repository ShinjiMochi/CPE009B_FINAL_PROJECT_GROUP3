import os
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QGroupBox, QScrollArea,
    QLabel, QSpinBox, QCheckBox, QPushButton, QMessageBox
)

from logic import (
    MINIMUM_GUESTS, DISCOUNT_RATE,
    validate_guests, create_guest_info, calculate_totals
)
from ui_common import (
    ImageBox, BannerBox, IMAGE_FOLDER, make_title, make_secondary_button
)


class GuestOptions(QWidget):
    # emits: guests, discount, services
    continued = pyqtSignal(dict)
    back_requested = pyqtSignal()

    def __init__(self, services=None):
        super().__init__()

        self.services = services or {}
        self.service_checkboxes = {}
        self.room_name = ""
        self.room_charge = 0.0

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
        self.discount_check.toggled.connect(self.update_summary)
        for checkbox in self.service_checkboxes.values():
            checkbox.toggled.connect(self.update_summary)
        self.continue_button.clicked.connect(self.on_continue)
        self.back_button.clicked.connect(self.back_requested.emit)

        self.update_summary()

    def make_note(self, text):
        note = QLabel(text)
        note.setWordWrap(True)
        note.setObjectName("muted")
        return note

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

        grid = QGridLayout()
        grid.addWidget(QLabel("Number of guests:"), 0, 0)
        grid.addWidget(self.guest_spin, 0, 1)
        grid.addWidget(self.family_check, 1, 0, 1, 2)
        grid.addWidget(QLabel("Seniors:"), 2, 0)
        grid.addWidget(self.senior_spin, 2, 1)
        grid.addWidget(QLabel("Children:"), 3, 0)
        grid.addWidget(self.child_spin, 3, 1)
        grid.addWidget(self.make_note(
            f"Minimum of {MINIMUM_GUESTS} guests. Seniors and children "
            "are counted in the total."
        ), 4, 0, 1, 2)
        layout.addLayout(grid, 1)
        return box

    def make_discount_box(self):
        box = QGroupBox("Discount Account (optional)")
        layout = QHBoxLayout(box)
        layout.addWidget(
            ImageBox("images/discount", 70, 70),
            alignment=Qt.AlignmentFlag.AlignTop
        )

        self.discount_check = QCheckBox(
            f"Use discount account ({DISCOUNT_RATE * 100:.0f}% off room charges only)"
        )
        right = QVBoxLayout()
        right.addWidget(self.discount_check)
        right.addWidget(self.make_note(
            "Applies to the room charge only. Dining and additional services "
            "are not discounted."
        ))
        right.addStretch()
        layout.addLayout(right, 1)
        return box

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

            checkbox = QCheckBox("Add")
            self.service_checkboxes[name] = checkbox
            item.addWidget(checkbox, alignment=Qt.AlignmentFlag.AlignCenter)

            layout.addLayout(item, index // 3, index % 3)

        return box

    def make_summary_box(self):
        box = QGroupBox("Booking Summary")
        box.setMinimumWidth(240)
        layout = QVBoxLayout(box)

        self.summary_label = QLabel()
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

    def set_room_charge(self, room_charge, room_name=""):
        self.room_charge = room_charge
        self.room_name = room_name
        self.update_summary()

    def reset(self):
        self.guest_spin.setValue(MINIMUM_GUESTS)
        self.family_check.setChecked(False)
        self.discount_check.setChecked(False)
        for checkbox in self.service_checkboxes.values():
            checkbox.setChecked(False)
        self.room_charge = 0.0
        self.room_name = ""
        self.update_summary()

    def get_selected_services(self):
        return [
            {"name": name, "price": self.services[name]}
            for name, checkbox in self.service_checkboxes.items()
            if checkbox.isChecked()
        ]

    def update_summary(self, *args):
        totals = calculate_totals(
            self.room_charge,
            self.discount_check.isChecked(),
            self.get_selected_services()
        )
        discount = totals["discount"]

        self.summary_label.setText(
            f"Room: {self.room_name or '-'}\n"
            f"Guests: {self.guest_spin.value()}\n\n"
            f"Room charge: ₱{discount['room_charge']:,.2f}\n"
            f"Discount: -₱{discount['discount_amount']:,.2f}\n"
            f"Room after discount: ₱{discount['room_charge_after_discount']:,.2f}\n"
            f"Services: ₱{totals['services_total']:,.2f}\n\n"
            f"Total so far: ₱{totals['total']:,.2f}\n"
            "(dining is added later)"
        )

        errors = validate_guests(
            self.guest_spin.value(),
            self.family_check.isChecked(),
            self.senior_spin.value(),
            self.child_spin.value()
        )
        self.warning_label.setText("\n".join(errors))
        self.continue_button.setEnabled(not errors)

    def on_continue(self):
        try:
            guest_info = create_guest_info(
                self.guest_spin.value(),
                self.family_check.isChecked(),
                self.senior_spin.value(),
                self.child_spin.value()
            )
        except ValueError as error:
            QMessageBox.warning(self, "Invalid Guest Information", str(error))
            return

        services = self.get_selected_services()
        self.continued.emit({
            "guests": guest_info.to_dict(),
            "discount": calculate_totals(
                self.room_charge, self.discount_check.isChecked(), services
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
    screen.set_room_charge(1500, "Economy")
    screen.continued.connect(print)
    screen.resize(1100, 700)
    screen.show()
    sys.exit(app.exec())
