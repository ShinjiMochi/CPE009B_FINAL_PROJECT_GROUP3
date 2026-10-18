from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QRadioButton, QSpinBox, QPushButton
)

from BookingManager import booking_manager


class StayDuration(QWidget):
    continued = pyqtSignal(dict)     # duration_type, duration, room_charge
    back_requested = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.room = None

        layout = QVBoxLayout(self)

        title = QLabel("Stay Duration")
        title.setStyleSheet("font-size: 28px; font-weight: bold;")
        layout.addWidget(title)

        self.room_label = QLabel()
        self.room_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(self.room_label)

        self.description_label = QLabel()
        self.description_label.setWordWrap(True)
        layout.addWidget(self.description_label)

        self.rates_label = QLabel()
        layout.addWidget(self.rates_label)

        layout.addWidget(QLabel("Choose stay duration:"))
        self.hourly_radio = QRadioButton("Per Hour")
        self.daily_radio = QRadioButton("Per Day")
        self.daily_radio.setChecked(True)
        layout.addWidget(self.hourly_radio)
        layout.addWidget(self.daily_radio)

        row = QHBoxLayout()
        self.duration_label = QLabel("Number of days:")
        self.duration_spin = QSpinBox()
        self.duration_spin.setRange(1, 999)
        row.addWidget(self.duration_label)
        row.addWidget(self.duration_spin)
        row.addStretch()
        layout.addLayout(row)

        self.total_label = QLabel()
        self.total_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(self.total_label)
        layout.addStretch()

        buttons = QHBoxLayout()
        back = QPushButton("Back")
        self.continue_button = QPushButton("Continue")
        buttons.addWidget(back)
        buttons.addStretch()
        buttons.addWidget(self.continue_button)
        layout.addLayout(buttons)

        back.clicked.connect(self.back_requested.emit)
        self.continue_button.clicked.connect(self.on_continue)
        self.hourly_radio.toggled.connect(self.update_total)
        self.duration_spin.valueChanged.connect(self.update_total)

        self.update_total()

    def duration_type(self):
        return "Hourly" if self.hourly_radio.isChecked() else "Daily"

    def set_room(self, room):
        self.room = room
        self.room_label.setText(f"Selected Room: {room.room_type}")
        self.description_label.setText(room.description)
        self.rates_label.setText(
            f"Hourly rate: ₱{room.hourly_rate:,.2f}    "
            f"Daily rate: ₱{room.daily_rate:,.2f}"
        )
        self.update_total()

    def update_total(self, *args):
        self.duration_label.setText(
            "Number of hours:" if self.duration_type() == "Hourly"
            else "Number of days:"
        )

        if self.room is None:
            self.total_label.setText("Room charge: ₱0.00")
            self.continue_button.setEnabled(False)
            return

        total = booking_manager.calculate_price(
            self.room, self.duration_type(), self.duration_spin.value()
        )
        self.total_label.setText(f"Room charge: ₱{total:,.2f}")
        self.continue_button.setEnabled(True)

    def on_continue(self):
        if self.room is None:
            return
        room_charge = booking_manager.calculate_price(
            self.room, self.duration_type(), self.duration_spin.value()
        )
        self.continued.emit({
            "duration_type": self.duration_type(),
            "duration": self.duration_spin.value(),
            "room_charge": room_charge
        })

    def reset(self):
        self.daily_radio.setChecked(True)
        self.duration_spin.setValue(1)
        self.update_total()
