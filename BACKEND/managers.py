"""Payment, booking storage and receipts.
Merged from: PaymentManager, BookingManager, ReceiptManager.

Every booking is saved twice:   Bookings.txt  (readable log, appended)
                                Bookings.json (data file, the source of truth)
Every receipt is saved twice:   Receipts/Receipt_00001.txt and .json
Files live next to this script, so it works from any working folder."""

import json
import os
import random
import re
import subprocess
import sys
from datetime import datetime

from logic import calculate_price, calculate_totals, format_when

BASE_FOLDER = os.path.dirname(os.path.abspath(__file__))
RECEIPT_FOLDER = os.path.join(BASE_FOLDER, "Receipts")
CURRENCY = "PHP"
SEPARATOR = "-" * 40
WIDTH = 52


# =====================================================================
#                          Small file helper
# =====================================================================
def write_json(path, data):
    """Writes to a temp file first, so a crash can't leave half a file."""
    temp = path + ".tmp"
    with open(temp, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)
    os.replace(temp, path)


# =====================================================================
#                           Payment Logic
# =====================================================================
# method -> providers (empty list = no provider needed)
PAYMENT_METHODS = {
    "Cash": [],
    "E-Wallet / E-Banking": ["GCash", "Maya", "GrabPay", "Online Bank Transfer"],
    "Card": ["Credit Card", "Debit Card"],
}


def get_payment_methods():
    return {method: list(providers) for method, providers in PAYMENT_METHODS.items()}


def generate_reference():
    stamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"PAY-{stamp}-{random.randint(100, 999)}"


def process_payment(method, amount, provider=None, details=None):
    """
    method:   "Cash", "E-Wallet / E-Banking" or "Card"
    amount:   amount due in PHP
    provider: required for e-wallet and card (see PAYMENT_METHODS)
    details:  Cash: {"amount_tendered": 2000}
              Card: {"card_number": "4111111111111111", "card_holder": "Juan Dela Cruz"}
    Always returns an "Approved" payment record (demo), or raises ValueError.
    Only the last 4 digits of a card number are kept.
    """
    details = details or {}

    if method not in PAYMENT_METHODS:
        raise ValueError("Please choose a valid payment method.")

    if amount is None or amount <= 0:
        raise ValueError("Amount to pay must be greater than zero.")

    providers = PAYMENT_METHODS[method]
    if providers and provider not in providers:
        raise ValueError(f"Please choose a valid option for {method}.")

    payment = {
        "method": method,
        "provider": provider if providers else None,
        "amount": round(amount, 2),
        "currency": CURRENCY,
        "status": "Approved",
        "reference": generate_reference(),
        "paid_at": datetime.now().isoformat(timespec="seconds"),
    }

    if method == "Cash":
        tendered = details.get("amount_tendered")
        if tendered is None:
            tendered = amount
        try:
            tendered = float(tendered)
        except (TypeError, ValueError):
            raise ValueError("Amount tendered must be a number.")
        if tendered < amount:
            raise ValueError("Amount tendered is less than the amount due.")

        payment["amount_tendered"] = round(tendered, 2)
        payment["change"] = round(tendered - amount, 2)

    elif method == "Card":
        number = re.sub(r"[\s\-]", "", str(details.get("card_number", "")))
        if not number.isdigit() or not 13 <= len(number) <= 19:
            raise ValueError("Card number must be 13 to 19 digits.")
        holder = str(details.get("card_holder", "")).strip()
        if not holder:
            raise ValueError("Card holder name is required.")

        payment["card_last4"] = number[-4:]
        payment["card_holder"] = holder

    return payment


# =====================================================================
#                           Booking Logic
# =====================================================================
def booking_to_text(booking):
    """One readable block for Bookings.txt."""
    lines = [
        f"Booking Number: {booking['booking_number']}",
        f"Customer Name: {booking['customer_name']}",
    ]

    if booking.get("created_at"):
        lines.append(f"Date: {booking['created_at']}")
    if booking.get("contact_number"):
        lines.append(f"Contact Number: {booking['contact_number']}")
    if booking.get("email"):
        lines.append(f"Email: {booking['email']}")
    if booking.get("address"):
        lines.append(f"Address: {booking['address']}")
    if booking.get("special_requests"):
        # keep it on one line so the block stays easy to read
        lines.append(f"Special Requests: {' '.join(booking['special_requests'].split())}")

    lines.append(f"Room Type: {booking['room_type']}")
    lines.append(f"Duration: {booking['duration']} {booking['duration_type']}")
    if booking.get("check_in"):
        lines.append(f"Check-in: {booking['check_in']}")
    if booking.get("check_out"):
        lines.append(f"Check-out: {booking['check_out']}")

    guests = booking.get("guests")
    if guests:
        lines.append(f"Guests: {guests['total_guests']}")
        lines.append(f"Seniors: {guests['seniors']}")
        lines.append(f"Children: {guests['children']}")

    lines.append(f"Room Charge: PHP {booking['room_charge']:,.2f}")

    discount = booking.get("discount")
    if discount and discount["discount_used"]:
        lines.append(f"Discount Rate: {discount['discount_rate']}")
        lines.append(f"Discount: PHP {discount['discount_amount']:,.2f}")

    for service in booking.get("services", []):
        lines.append(f"Service: {service['name']} | {service['price']:.2f}")

    for item in booking.get("dining", []):
        lines.append(
            f"Dining: {item['name']} | {item['quantity']} | {item['price']:.2f}"
        )

    lines.append(f"Total Price: PHP {booking['total_price']:,.2f}")

    payment = booking.get("payment")
    if payment:
        lines.append(f"Payment Method: {payment['method']}")
        if payment.get("provider"):
            lines.append(f"Payment Provider: {payment['provider']}")
        lines.append(f"Payment Reference: {payment['reference']}")
        lines.append(f"Payment Status: {payment['status']}")
        if "amount_tendered" in payment:
            lines.append(f"Amount Tendered: {payment['amount_tendered']:.2f}")
            lines.append(f"Change: {payment['change']:.2f}")
        if payment.get("card_last4"):
            lines.append(f"Card Last4: {payment['card_last4']}")

    lines.append(SEPARATOR)
    return "\n".join(lines) + "\n"

class BookingManager:
    def __init__(self, folder=BASE_FOLDER):
        self.txt_file = os.path.join(folder, "Bookings.txt")
        self.json_file = os.path.join(folder, "Bookings.json")
        self.next_booking_number = self._highest_number() + 1

    # ---------- reading ----------
    def load_bookings(self):
        """Returns the list stored in Bookings.json ([] if there is no file)."""
        if not os.path.exists(self.json_file):
            return []
        try:
            with open(self.json_file, "r", encoding="utf-8") as file:
                data = json.load(file)
        except (OSError, ValueError) as error:
            raise OSError(f"Could not read Bookings.json: {error}")
        if not isinstance(data, list):
            raise OSError("Bookings.json is not a list of bookings.")
        return data

    def get_booking(self, booking_number):
        """Returns the booking dict, or None."""
        for booking in self.load_bookings():
            if booking.get("booking_number") == booking_number:
                return booking
        return None

    def _highest_number(self):
        """Highest booking number in the json (and the old txt log, if any)."""
        highest = 0

        try:
            highest = max(
                (b.get("booking_number", 0) for b in self.load_bookings()),
                default=0
            )
        except OSError:
            pass   # a broken json is reported when the next booking is saved

        if os.path.exists(self.txt_file):
            with open(self.txt_file, "r", encoding="utf-8") as file:
                for line in file:
                    if line.startswith("Booking Number: "):
                        try:
                            highest = max(highest, int(line.split(": ", 1)[1]))
                        except ValueError:
                            continue
        return highest

    # ---------- saving ----------
    def save_booking(self, booking):
        """Writes the booking to Bookings.json and Bookings.txt.""" ## I added json capability cuz why not
        bookings = self.load_bookings()    # raises OSError before anything is written
        bookings.append(booking)
        write_json(self.json_file, bookings)

        with open(self.txt_file, "a", encoding="utf-8") as file:
            file.write(booking_to_text(booking))

    # ---------- creating ----------
    def create_booking(
        self,
        customer,
        room,
        duration_type,
        duration,
        guests=None,
        use_discount=False,
        services=None,
        dining=None,
        payment_method=None,
        payment_provider=None,
        payment_details=None,
        check_in=None,
        check_out=None
    ):
        """
        customer: dict from logic.create_customer_info()
        guests:   GuestInfo.to_dict() result
        services: [{"name": ..., "price": ...}]
        dining:   [{"name": ..., "price": ..., "quantity": ...}]
        check_in, check_out: ISO strings like "2026-10-20T14:00"
        Returns the saved booking dict.
        """
        if not customer.get("full_name", "").strip():
            raise ValueError("Customer name cannot be empty.")

        if check_in is not None or check_out is not None:
            try:
                start = datetime.fromisoformat(str(check_in))
                end = datetime.fromisoformat(str(check_out))
            except ValueError:
                raise ValueError("Invalid check-in or check-out date.")
            if end <= start:
                raise ValueError("Check-out must be after check-in.")
            check_in = start.isoformat(timespec="minutes")
            check_out = end.isoformat(timespec="minutes")

        services = services or []
        dining_items = [
            {**d, "amount": round(d["price"] * d["quantity"], 2)}
            for d in (dining or [])
        ]

        room_charge = calculate_price(room, duration_type, duration)
        totals = calculate_totals(room_charge, use_discount, services, dining_items)

        # Pay first so a failed payment doesn't use up a booking number
        payment = None
        if payment_method is not None:
            payment = process_payment(
                payment_method, totals["total"], payment_provider, payment_details
            )

        booking = {
            "booking_number": self.next_booking_number,
            "created_at": datetime.now().isoformat(timespec="seconds"),
            "customer_name": customer["full_name"].strip(),
            "contact_number": customer.get("contact_number"),
            "email": customer.get("email"),
            "address": customer.get("address"),
            "special_requests": customer.get("special_requests", ""),
            "room_type": room.room_type,
            "duration_type": duration_type,
            "duration": duration,
            "check_in": check_in,
            "check_out": check_out,
            "guests": guests,
            "room_charge": room_charge,
            "discount": totals["discount"],
            "services": services,
            "dining": dining_items,
            "total_price": totals["total"],
            "payment": payment,
            "payment_status": "Paid" if payment else "Unpaid",
        }

        self.save_booking(booking)
        self.next_booking_number += 1     # only used up once it is really saved
        return booking


# One shared booking manager
booking_manager = BookingManager()


# =====================================================================
#                      Receipt Creation (REMADE)
# =====================================================================
def money(amount):
    return f"PHP {amount:,.2f}"

def line(label, amount):
    return f"{label:<{WIDTH - 18}}{amount:>18}"

def generate_receipt(booking):
    """Returns the receipt as text."""
    guests = booking.get("guests")
    discount = booking.get("discount") or {}
    payment = booking.get("payment")
    full = "%B %d, %Y %I:%M %p"

    unit = "hour(s)" if booking["duration_type"] == "Hourly" else "day(s)"

    out = [
        "=" * WIDTH,
        "HOTEL BOOKING SYSTEM".center(WIDTH),
        "OFFICIAL RECEIPT".center(WIDTH),
        "=" * WIDTH,
        f"Booking Number : {booking['booking_number']:05d}",
        f"Date           : {format_when(booking.get('created_at'), full)}",
        f"Customer       : {booking['customer_name']}",
    ]

    if booking.get("contact_number"):
        out.append(f"Contact        : {booking['contact_number']}")
    if booking.get("email"):
        out.append(f"Email          : {booking['email']}")
    if booking.get("address"):
        out.append(f"Address        : {booking['address']}")

    out += [
        f"Room           : {booking['room_type']}",
        f"Stay           : {booking['duration']} {unit}",
    ]

    if booking.get("check_in"):
        out.append(f"Check-in       : {format_when(booking['check_in'], full)}")
    if booking.get("check_out"):
        out.append(f"Check-out      : {format_when(booking['check_out'], full)}")

    if guests:
        out.append(
            f"Guests         : {guests.get('total_guests', '-')} "
            f"(adults {guests.get('adults', '-')}, seniors {guests.get('seniors', 0)}, "
            f"children {guests.get('children', 0)})"
        )

    out += ["-" * WIDTH, line("Room charge", money(booking["room_charge"]))]

    if discount.get("discount_used"):
        out.append(line(
            f"Discount ({discount['discount_rate'] * 100:.0f}%)",
            "-" + money(discount["discount_amount"])
        ))

    for service in booking["services"]:
        out.append(line(service["name"], money(service["price"])))

    for item in booking["dining"]:
        out.append(line(f"{item['quantity']} x {item['name']}", money(item["amount"])))

    out += ["-" * WIDTH, line("TOTAL", money(booking["total_price"])), "-" * WIDTH]

    if payment:
        out.append(f"Payment Method : {payment['method']}")
        if payment.get("provider"):
            out.append(f"Provider       : {payment['provider']}")
        if payment.get("card_last4"):
            out.append(f"Card           : **** **** **** {payment['card_last4']}")
        out.append(f"Reference      : {payment['reference']}")
        out.append(f"Status         : {payment['status']}")
        if "amount_tendered" in payment:
            out.append(line("Amount tendered", money(payment["amount_tendered"])))
            out.append(line("Change", money(payment["change"])))
    else:
        out.append("Payment Status : Unpaid")

    out += ["=" * WIDTH, "Thank you for staying with us!".center(WIDTH), "=" * WIDTH]
    return "\n".join(out)


def save_receipt(booking, folder=RECEIPT_FOLDER):
    """Writes Receipt_00001.txt and Receipt_00001.json. Returns (txt_path, json_path)."""
    os.makedirs(folder, exist_ok=True)
    name = f"Receipt_{booking['booking_number']:05d}"
    txt_path = os.path.join(folder, name + ".txt")
    json_path = os.path.join(folder, name + ".json")

    with open(txt_path, "w", encoding="utf-8") as file:
        file.write(generate_receipt(booking) + "\n")
    write_json(json_path, booking)

    return txt_path, json_path


def print_receipt(booking, folder=RECEIPT_FOLDER):
    """Saves the receipt, then sends the .txt to the default printer.
    Raises OSError on failure."""
    txt_path, _ = save_receipt(booking, folder)

    try:
        if sys.platform.startswith("win"):
            os.startfile(txt_path, "print")
        else:
            subprocess.run(["lp", txt_path], check=True)
    except (FileNotFoundError, subprocess.CalledProcessError) as error:
        raise OSError(f"Could not print the receipt: {error}")

    return txt_path
