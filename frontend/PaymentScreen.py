from html import escape

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QScrollArea, QLabel
)

from logic import (
    calculate_totals, cancellation_policy_lines, format_when, price_rooms,
    rooms_summary
)
from ui_common import make_title, make_nav_buttons, MUTED


def money(amount):
    return f"₱{amount:,.2f}"


def make_label():
    label = QLabel()
    label.setWordWrap(True)
    label.setAlignment(Qt.AlignmentFlag.AlignTop)
    label.setTextFormat(Qt.TextFormat.RichText)
    return label


def note_html(text):
    return f'<br><span style="color:{MUTED}; font-size:11px;">{escape(text)}</span>'


class PaymentScreen(QWidget):
    """Confirm step: shows the booking details and the full cost breakdown.
    The actual payment happens in a separate window (PaymentDialog) that
    main.py opens when the guest presses the confirm button."""
    confirm_requested = pyqtSignal()
    back_requested = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.total = 0.0

        # ----- left: booking details -----
        details_box = QGroupBox("Booking Details")
        details_layout = QVBoxLayout(details_box)
        self.details_label = make_label()
        details_layout.addWidget(self.details_label)
        details_layout.addStretch()

        # ----- right: cost breakdown -----
        cost_box = QGroupBox("Cost Breakdown")
        cost_layout = QVBoxLayout(cost_box)
        self.cost_label = make_label()
        cost_layout.addWidget(self.cost_label)
        cost_layout.addStretch()

        columns = QHBoxLayout()
        columns.addWidget(details_box, 1)
        columns.addWidget(cost_box, 1)
        content = QWidget()
        content.setLayout(columns)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(content)

        buttons, back, self.confirm_button = make_nav_buttons(next_text="Confirm & Pay")

        layout = QVBoxLayout(self)
        layout.addWidget(make_title("Confirm Booking"))
        layout.addWidget(scroll, 1)
        layout.addLayout(buttons)

        back.clicked.connect(self.back_requested.emit)
        self.confirm_button.clicked.connect(self.confirm_requested.emit)

    def set_summary(self, data):
        """data is the booking dict collected by main.py."""
        room_lines, room_charge = price_rooms(
            data["rooms"], data["duration_type"], data["duration"]
        )
        totals = calculate_totals(
            room_charge, data.get("discount_info"), data["services"], data["dining"]
        )
        discount = totals["discount"]
        self.total = totals["total"]

        unit = "hour(s)" if data["duration_type"] == "Hourly" else "day(s)"
        customer = data["customer"]
        guests = data["guests"]

        # ---------- booking details ----------
        lines = [
            f"<b>Primary guest:</b> {escape(customer['full_name'])}",
            f"<b>Contact:</b> {escape(customer['contact_number'])}",
            f"<b>Email:</b> {escape(customer['email'])}",
            f"<b>Address:</b> {escape(customer['address'])}",
            "",
            f"<b>Rooms:</b> {escape(rooms_summary(data['rooms']))}",
            f"<b>Stay:</b> {data['duration']} {unit}",
            f"<b>Check-in:</b> {format_when(data.get('check_in'))}",
            f"<b>Check-out:</b> {format_when(data.get('check_out'))}",
            "",
            f"<b>Guests ({guests['total_guests']}):</b> "
            f"adults {guests['adults']}, seniors {guests['seniors']}, "
            f"children {guests['children']}",
            f"1. {escape(customer['full_name'])} (primary) - {escape(customer['contact_number'])}",
        ]
        for number, guest in enumerate(data.get("guest_list", []), start=2):
            contact = guest["contact"] or "no contact number"
            lines.append(f"{number}. {escape(guest['name'])} - {escape(contact)}")

        if customer.get("special_requests"):
            lines += [
                "",
                "<b>General requests:</b>",
                escape(customer["special_requests"]).replace("\n", "<br>"),
            ]
        self.details_label.setText("<br>".join(lines))

        # ---------- cost breakdown ----------
        rows = []

        def add(label, amount, note="", bold=False):
            text = f"<b>{label}</b>" if bold else label
            value = f"<b>{amount}</b>" if bold else amount
            rows.append(
                f'<tr><td style="padding:3px 0;">{text}{note_html(note) if note else ""}</td>'
                f'<td align="right" valign="top" style="padding:3px 0;">{value}</td></tr>'
            )

        for room in room_lines:
            add(
                f"{room['quantity']} x {escape(room['room_type'])}",
                money(room["amount"]),
                f"{data['duration']} {unit} at {money(room['unit_charge'])} per room"
            )
        if len(room_lines) > 1 or room_lines[0]["quantity"] > 1:
            add("Room subtotal", money(discount["room_charge"]))

        if discount["discount_used"]:
            detail = f"{discount['discount_type']}, ID / voucher {discount['discount_reference']}"
            if discount.get("discount_holder"):
                detail += f" ({discount['discount_holder']})"
            add(
                f"Discount - {escape(discount['discount_type'])} "
                f"({discount['discount_rate'] * 100:.0f}%)",
                "-" + money(discount["discount_amount"]),
                detail + ". Room charge only."
            )

        for service in data["services"]:
            add(escape(service["name"]), money(service["price"]), service.get("spec", ""))

        for item in data["dining"]:
            add(
                f"{item['quantity']} x {escape(item['name'])}",
                money(item["price"] * item["quantity"]),
                f"{money(item['price'])} each"
            )

        add("TOTAL", money(self.total), bold=True)

        policy = "<br>".join(escape(text) for text in cancellation_policy_lines())
        self.cost_label.setText(
            '<table width="100%" cellspacing="0">' + "".join(rows) + "</table>"
            f'<br><b>Cancellation fees</b><br>'
            f'<span style="color:{MUTED}; font-size:11px;">{policy}</span>'
        )

        self.confirm_button.setText(f"Confirm && Pay {money(self.total)}")

    def reset(self):
        self.total = 0.0
        self.details_label.clear()
        self.cost_label.clear()
        self.confirm_button.setText("Confirm && Pay")
