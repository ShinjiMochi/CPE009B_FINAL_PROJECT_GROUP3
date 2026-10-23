from PyQt6.QtCore import pyqtSignal, QRegularExpression
from PyQt6.QtGui import QRegularExpressionValidator
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QFormLayout,
    QLabel, QComboBox, QLineEdit, QDoubleSpinBox
)

from logic import calculate_totals, format_when
from managers import get_payment_methods
from ui_common import make_title, make_nav_buttons

class PaymentScreen(QWidget):
    pay_requested = pyqtSignal(dict)    # {"method", "provider", "details"}
    back_requested = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.total = 0.0
        self.methods = get_payment_methods()

        # ----- summary -----
        summary_box = QGroupBox("Booking Summary")
        summary_layout = QVBoxLayout(summary_box)
        self.summary_label = QLabel()
        self.summary_label.setWordWrap(True)
        summary_layout.addWidget(self.summary_label)
        summary_layout.addStretch()

        # ----- payment form -----
        pay_box = QGroupBox("Payment Method (demo - always approved)")
        pay_layout = QVBoxLayout(pay_box)

        self.method_combo = QComboBox()
        self.method_combo.addItems(self.methods.keys())
        top = QFormLayout()
        top.addRow("Method:", self.method_combo)
        pay_layout.addLayout(top)

        self.provider_box = QWidget()
        provider_form = QFormLayout(self.provider_box)
        self.provider_combo = QComboBox()
        provider_form.addRow("Option:", self.provider_combo)
        pay_layout.addWidget(self.provider_box)

        self.cash_box = QWidget()
        cash_form = QFormLayout(self.cash_box)
        self.tendered_spin = QDoubleSpinBox()
        self.tendered_spin.setDecimals(2)
        self.tendered_spin.setRange(0, 100000000)
        self.tendered_spin.setPrefix("₱ ")
        cash_form.addRow("Amount tendered:", self.tendered_spin)
        pay_layout.addWidget(self.cash_box)

        self.card_box = QWidget()
        card_form = QFormLayout(self.card_box)
        self.card_number_input = QLineEdit()
        self.card_number_input.setPlaceholderText("Digits only (up to 16)")
        self.card_number_input.setMaxLength(16)
        self.card_number_input.setValidator(
            QRegularExpressionValidator(QRegularExpression("[0-9]*"))
        )
        self.card_holder_input = QLineEdit()
        self.card_holder_input.setPlaceholderText("Letters and spaces only")
        self.card_holder_input.setMaxLength(40)
        self.card_holder_input.setValidator(
            QRegularExpressionValidator(QRegularExpression(r"[\p{L} ]*"))
        )
        card_form.addRow("Card number:", self.card_number_input)
        card_form.addRow("Card holder:", self.card_holder_input)
        pay_layout.addWidget(self.card_box)
        pay_layout.addStretch()

        # ----- layout -----
        columns = QHBoxLayout()
        columns.addWidget(summary_box, 1)
        columns.addWidget(pay_box, 1)

        buttons, back, self.pay_button = make_nav_buttons(next_text="Pay")

        layout = QVBoxLayout(self)
        layout.addWidget(make_title("Payment"))
        layout.addLayout(columns)
        layout.addLayout(buttons)

        back.clicked.connect(self.back_requested.emit)
        self.pay_button.clicked.connect(self.on_pay)
        self.method_combo.currentTextChanged.connect(self.update_method_fields)
        self.update_method_fields()

    def update_method_fields(self, *args):
        method = self.method_combo.currentText()
        providers = self.methods.get(method, [])

        self.provider_combo.clear()
        self.provider_combo.addItems(providers)

        self.provider_box.setVisible(bool(providers))
        self.cash_box.setVisible(method == "Cash")
        self.card_box.setVisible(method == "Card")

    def set_summary(self, data):
        """data is the booking dict collected by main.py."""
        totals = calculate_totals(
            data["room_charge"],
            data["discount"]["discount_used"],
            data["services"],
            data["dining"]
        )
        discount = totals["discount"]
        self.total = totals["total"]

        customer = data["customer"]
        guests = data["guests"]
        unit = "hour(s)" if data["duration_type"] == "Hourly" else "day(s)"

        lines = [
            f"<b>Customer:</b> {customer['full_name']}",
            f"<b>Room:</b> {data['room'].room_type}",
            f"<b>Stay:</b> {data['duration']} {unit}",
            f"<b>Check-in:</b> {format_when(data.get('check_in'))}",
            f"<b>Check-out:</b> {format_when(data.get('check_out'))}",
            f"<b>Guests:</b> {guests['total_guests']}",
            "",
            f"Room charge: ₱{discount['room_charge']:,.2f}",
        ]
        if discount["discount_used"]:
            lines.append(f"Discount: -₱{discount['discount_amount']:,.2f}")
        for service in data["services"]:
            lines.append(f"{service['name']}: ₱{service['price']:,.2f}")
        for item in data["dining"]:
            amount = item["price"] * item["quantity"]
            lines.append(f"{item['quantity']} x {item['name']}: ₱{amount:,.2f}")
        lines += ["", f"<b>TOTAL: ₱{self.total:,.2f}</b>"]

        self.summary_label.setText("<br>".join(lines))
        self.tendered_spin.setValue(self.total)
        self.pay_button.setText(f"Pay ₱{self.total:,.2f}")

    def on_pay(self):
        method = self.method_combo.currentText()
        provider = self.provider_combo.currentText() or None
        details = {}

        if method == "Cash":
            details["amount_tendered"] = self.tendered_spin.value()
        elif method == "Card":
            details["card_number"] = self.card_number_input.text()
            details["card_holder"] = self.card_holder_input.text()

        self.pay_requested.emit({
            "method": method,
            "provider": provider,
            "details": details
        })

    def reset(self):
        self.method_combo.setCurrentIndex(0)
        self.card_number_input.clear()
        self.card_holder_input.clear()
        self.tendered_spin.setValue(0)
        self.summary_label.clear()
        self.pay_button.setText("Pay")
