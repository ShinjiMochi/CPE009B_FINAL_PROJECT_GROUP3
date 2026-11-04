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
import textwrap
from datetime import datetime

from logic import (
    MAX_ROOMS_PER_BOOKING, calculate_totals, cancellation_fee, format_when,
    get_service_spec, normalize_contact, price_rooms, rooms_summary,
    total_capacity, total_room_count,
)

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

## Accounts where payments are recieved online
PAYMENT_ACCOUNTS = {
    "GCash": {
        "account_name": "Aurevelle Hotel Corp.",
        "account_number": "0917 123 4567",
        "bank": "",
        "qr_image": "gcash",
    },
    "Maya": {
        "account_name": "Aurevelle Hotel Corp.",
        "account_number": "0918 765 4321",
        "bank": "",
        "qr_image": "maya",
    }, 
    "GrabPay": {
        "account_name": "Aurevelle Hotel Corp.",
        "account_number": "0919 246 8101",
        "bank": "",
        "qr_image": "grabpay",
    },
    "Online Bank Transfer": {
        "account_name": "Aurevelle Hotel Corp.",
        "account_number": "0012 3456 7890",
        "bank": "BDO Unibank",
        "qr_image": "bank",
    },
}

## Locations where cash can be payed
CASH_LOCATIONS = {
    "Front Desk (Main Lobby)":
        "Aurevelle Hotel, Ground Floor Main Lobby, 123 Sample Avenue, "
        "Quezon City. Open 24 hours.",
    "Cashier Counter (Mezzanine)":
        "Aurevelle Hotel, Mezzanine Level beside the Concierge Desk. "
        "Open 8:00 AM to 8:00 PM.",
}


def get_payment_accounts():
    return {name: dict(info) for name, info in PAYMENT_ACCOUNTS.items()}


def get_cash_locations():
    return dict(CASH_LOCATIONS)


def generate_reference():
    stamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"PAY-{stamp}-{random.randint(100, 999)}"


def process_payment(method, amount, provider=None, details=None):
    """
    method:   "Cash", "E-Wallet / E-Banking" or "Card"
    amount:   amount due in PHP
    provider: required for e-wallet and card (see PAYMENT_METHODS)
    details:  Cash: {"amount_tendered": 2000, "location": "Front Desk (Main Lobby)"}
              E-wallet / bank: {"reference_number": "the sender's transaction number"}
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

        location = details.get("location")
        if location not in CASH_LOCATIONS:
            raise ValueError("Please choose where you will pay in cash.")

        payment["amount_tendered"] = round(tendered, 2)
        payment["change"] = round(tendered - amount, 2)
        payment["location"] = location
        payment["location_address"] = CASH_LOCATIONS[location]

    elif method == "E-Wallet / E-Banking":
        account = PAYMENT_ACCOUNTS[provider]
        reference = str(details.get("reference_number", "")).strip()
        if len(reference) < 6:
            raise ValueError(
                "Enter the transaction / reference number of your payment "
                "(at least 6 characters)."
            )
        payment["receiver_name"] = account["account_name"]
        payment["receiver_number"] = account["account_number"]
        payment["receiver_bank"] = account["bank"]
        payment["transaction_reference"] = reference

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
        f"Status: {booking.get('status', 'Confirmed')}",
    ]

    if booking.get("created_at"):
        lines.append(f"Date: {booking['created_at']}")
    if booking.get("contact_number"):
        lines.append(f"Contact Number: {booking['contact_number']}")
    if booking.get("email"):
        lines.append(f"Email: {booking['email']}")
    if booking.get("address"):
        lines.append(f"Address: {booking['address']}")

    for number, guest in enumerate(booking.get("guest_list", []), start=1):
        lines.append(f"Guest {number}: {guest['name']} | {guest.get('contact') or '-'}")

    if booking.get("special_requests"):
        # keep it on one line so the block stays easy to read
        lines.append(f"General Requests: {' '.join(booking['special_requests'].split())}")

    lines.append(f"Rooms: {booking['room_type']}")
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

    for room in booking.get("rooms", []):
        lines.append(
            f"Room: {room['quantity']} x {room['room_type']} | "
            f"{room['unit_charge']:.2f} each | {room['amount']:.2f}"
        )
    lines.append(f"Room Charge: PHP {booking['room_charge']:,.2f}")

    discount = booking.get("discount")
    if discount and discount["discount_used"]:
        lines.append(f"Discount Type: {discount.get('discount_type') or '-'}")
        lines.append(f"Discount Reference: {discount.get('discount_reference') or '-'}")
        lines.append(f"Discount Rate: {discount['discount_rate']}")
        lines.append(f"Discount: PHP {discount['discount_amount']:,.2f}")

    for service in booking.get("services", []):
        lines.append(
            f"Service: {service['name']} | {service['price']:.2f} | "
            f"{service.get('spec', '')}"
        )

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
        if payment.get("location"):
            lines.append(f"Cash Payment Location: {payment['location']}")
        if payment.get("transaction_reference"):
            lines.append(f"Transaction Reference: {payment['transaction_reference']}")
        if "amount_tendered" in payment:
            lines.append(f"Amount Tendered: {payment['amount_tendered']:.2f}")
            lines.append(f"Change: {payment['change']:.2f}")
        if payment.get("card_last4"):
            lines.append(f"Card Last4: {payment['card_last4']}")

    lines.append(SEPARATOR)
    return "\n".join(lines) + "\n"


def cancellation_to_text(booking):
    """One readable block appended to Bookings.txt when a booking is cancelled."""
    cancel = booking["cancellation"]
    return "\n".join([
        f"Cancelled Booking Number: {booking['booking_number']}",
        f"Cancelled At: {cancel['cancelled_at']}",
        f"Cancellation Fee Rate: {cancel['fee_rate']}",
        f"Cancellation Fee: PHP {cancel['fee']:,.2f}",
        f"Refund: PHP {cancel['refund']:,.2f}",
        SEPARATOR,
    ]) + "\n"


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
        """Writes the booking to Bookings.json and Bookings.txt."""
        bookings = self.load_bookings()    # raises OSError before anything is written
        bookings.append(booking)
        write_json(self.json_file, bookings)

        with open(self.txt_file, "a", encoding="utf-8") as file:
            file.write(booking_to_text(booking))

    # ---------- creating ----------
    def create_booking(
        self,
        customer,
        rooms,
        duration_type,
        duration,
        guests=None,
        guest_list=None,
        discount=None,
        services=None,
        dining=None,
        payment_method=None,
        payment_provider=None,
        payment_details=None,
        check_in=None,
        check_out=None
    ):
        """
        customer:   dict from logic.create_customer_info() (the primary guest)
        rooms:      [{"room": Room, "quantity": n}]
        guests:     GuestInfo.to_dict() result
        guest_list: [{"name", "contact"}] for the guests after the primary one
        discount:   dict from logic.verify_discount(), or None
        services:   [{"name": ..., "price": ...}]
        dining:     [{"name": ..., "price": ..., "quantity": ...}]
        check_in, check_out: ISO strings like "2026-10-20T14:00"
        Returns the saved booking dict.
        """
        if not customer.get("full_name", "").strip():
            raise ValueError("Customer name cannot be empty.")

        if not rooms:
            raise ValueError("Select at least one room.")
        if total_room_count(rooms) > MAX_ROOMS_PER_BOOKING:
            raise ValueError(
                f"A booking can have at most {MAX_ROOMS_PER_BOOKING} rooms."
            )
        if guests and guests["total_guests"] > total_capacity(rooms):
            raise ValueError(
                f"The selected rooms fit up to {total_capacity(rooms)} guests."
            )

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

        services = [
            {**s, "spec": s.get("spec") or get_service_spec(s["name"])}
            for s in (services or [])
        ]
        dining_items = [
            {**d, "amount": round(d["price"] * d["quantity"], 2)}
            for d in (dining or [])
        ]

        room_lines, room_charge = price_rooms(rooms, duration_type, duration)
        totals = calculate_totals(room_charge, discount, services, dining_items)

        # Pay first so a failed payment doesn't use up a booking number
        payment = None
        if payment_method is not None:
            payment = process_payment(
                payment_method, totals["total"], payment_provider, payment_details
            )

        # everyone staying, primary guest first
        everyone = [{
            "name": customer["full_name"].strip(),
            "contact": customer.get("contact_number") or "",
            "primary": True,
        }] + [{**g, "primary": False} for g in (guest_list or [])]

        booking = {
            "booking_number": self.next_booking_number,
            "created_at": datetime.now().isoformat(timespec="seconds"),
            "status": "Confirmed",
            "customer_name": customer["full_name"].strip(),
            "contact_number": customer.get("contact_number"),
            "email": customer.get("email"),
            "address": customer.get("address"),
            "guest_list": everyone,
            "special_requests": customer.get("special_requests", ""),
            "room_type": rooms_summary(rooms),
            "rooms": room_lines,
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

    # ---------- finding and cancelling ----------
    def find_booking(self, booking_number, contact_number):
        """Booking whose number AND primary contact number match, else ValueError.
        The same message is used for both so nobody can probe for numbers."""
        booking = self.get_booking(booking_number)
        if (booking is None or
                normalize_contact(booking.get("contact_number")) !=
                normalize_contact(contact_number)):
            raise ValueError("No booking matches that booking number and contact number.")
        return booking

    def preview_cancellation(self, booking, now=None):
        """Fee and refund if cancelled now. Raises ValueError if not allowed."""
        if booking.get("status") == "Cancelled":
            raise ValueError("This booking is already cancelled.")
        return cancellation_fee(booking.get("check_in"), booking["total_price"], now)

    def cancel_booking(self, booking_number, contact_number, now=None):
        """Marks the booking Cancelled in Bookings.json, logs it in Bookings.txt
        and returns the updated booking."""
        bookings = self.load_bookings()
        target = None
        for booking in bookings:
            if booking.get("booking_number") == booking_number:
                target = booking
                break
        if (target is None or
                normalize_contact(target.get("contact_number")) !=
                normalize_contact(contact_number)):
            raise ValueError("No booking matches that booking number and contact number.")

        fee = self.preview_cancellation(target, now)
        payment = target.get("payment")

        target["status"] = "Cancelled"
        target["payment_status"] = "Refunded" if payment else "Unpaid"
        target["cancellation"] = {
            "cancelled_at": (now or datetime.now()).isoformat(timespec="seconds"),
            **fee,
            "refund_method": payment["method"] if payment else None,
        }

        write_json(self.json_file, bookings)
        with open(self.txt_file, "a", encoding="utf-8") as file:
            file.write(cancellation_to_text(target))
        return target


# One shared booking manager
booking_manager = BookingManager()


# =====================================================================
#                           Receipt Creation
# =====================================================================
def money(amount):
    return f"PHP {amount:,.2f}"


def line(label, amount):
    return f"{label:<{WIDTH - 18}}{amount:>18}"


def field(label, value):
    """'Label          : value', wrapped so it never goes past WIDTH."""
    parts = textwrap.wrap(str(value), WIDTH - 17) or [""]
    out = [f"{label:<15}: {parts[0]}"]
    out += [" " * 17 + part for part in parts[1:]]
    return out


def note(text, indent="   "):
    return [indent + part for part in textwrap.wrap(text, WIDTH - len(indent))]


def generate_receipt(booking):
    """Returns the receipt as text."""
    guests = booking.get("guests")
    discount = booking.get("discount") or {}
    payment = booking.get("payment")
    full = "%B %d, %Y %I:%M %p"

    unit = "hour(s)" if booking["duration_type"] == "Hourly" else "day(s)"
    cancelled = booking.get("status") == "Cancelled"

    out = [
        "=" * WIDTH,
        "HOTEL BOOKING SYSTEM".center(WIDTH),
        "OFFICIAL RECEIPT".center(WIDTH),
        "=" * WIDTH,
        f"Booking Number : {booking['booking_number']:05d}",
        f"Date           : {format_when(booking.get('created_at'), full)}",
    ]
    if cancelled:
        out.append("Status         : CANCELLED")
    out.append(f"Customer       : {booking['customer_name']}")

    if booking.get("contact_number"):
        out.append(f"Contact        : {booking['contact_number']}")
    if booking.get("email"):
        out += field("Email", booking["email"])
    if booking.get("address"):
        out += field("Address", booking["address"])

    out += field("Rooms", booking["room_type"])
    out.append(f"Stay           : {booking['duration']} {unit}")

    if booking.get("check_in"):
        out.append(f"Check-in       : {format_when(booking['check_in'], full)}")
    if booking.get("check_out"):
        out.append(f"Check-out      : {format_when(booking['check_out'], full)}")

    if guests:
        out += field(
            "Guests",
            f"{guests.get('total_guests', '-')} "
            f"(adults {guests.get('adults', '-')}, seniors {guests.get('seniors', 0)}, "
            f"children {guests.get('children', 0)})"
        )
    for number, guest in enumerate(booking.get("guest_list", []), start=1):
        name = guest["name"][:18] + (" (primary)" if guest.get("primary") else "")
        out.append(line(f"  {number}. {name}", guest.get("contact") or "-"))

    if booking.get("special_requests"):
        out += field("Requests", " ".join(booking["special_requests"].split()))

    out.append("-" * WIDTH)

    # ----- cost breakdown -----
    rooms = booking.get("rooms")
    if rooms:
        for room in rooms:
            out.append(line(
                f"{room['quantity']} x {room['room_type']} ({booking['duration']} {unit})",
                money(room["amount"])
            ))
        if len(rooms) > 1 or rooms[0]["quantity"] > 1:
            out.append(line("Room subtotal", money(booking["room_charge"])))
    else:                              # bookings saved before multi-room
        out.append(line("Room charge", money(booking["room_charge"])))

    if discount.get("discount_used"):
        kind = discount.get("discount_type")
        label = f"Discount - {kind}" if kind else "Discount"
        out.append(line(
            f"{label} ({discount['discount_rate'] * 100:.0f}%)",
            "-" + money(discount["discount_amount"])
        ))
        if discount.get("discount_reference"):
            detail = f"ID/voucher: {discount['discount_reference']}"
            if discount.get("discount_holder"):
                detail += f" ({discount['discount_holder']})"
            out += note(detail)

    for service in booking["services"]:
        out.append(line(service["name"], money(service["price"])))
        if service.get("spec"):
            out += note(service["spec"])

    for item in booking["dining"]:
        out.append(line(f"{item['quantity']} x {item['name']}", money(item["amount"])))

    out += ["-" * WIDTH, line("TOTAL", money(booking["total_price"])), "-" * WIDTH]

    # ----- payment -----
    if payment:
        out.append(f"Payment Method : {payment['method']}")
        if payment.get("provider"):
            out.append(f"Provider       : {payment['provider']}")
        if payment.get("card_last4"):
            out.append(f"Card           : **** **** **** {payment['card_last4']}")
        if payment.get("receiver_name"):
            out += field(
                "Paid to",
                f"{payment['receiver_name']} {payment['receiver_number']}"
                + (f" ({payment['receiver_bank']})" if payment.get("receiver_bank") else "")
            )
            out += field("Transaction no.", payment["transaction_reference"])
        if payment.get("location"):
            out += field("Pay at", payment["location"])
        out.append(f"Reference      : {payment['reference']}")
        out.append(f"Status         : {payment['status']}")
        if "amount_tendered" in payment:
            out.append(line("Amount tendered", money(payment["amount_tendered"])))
            out.append(line("Change", money(payment["change"])))
    else:
        out.append("Payment Status : Unpaid")

    if cancelled:
        cancel = booking["cancellation"]
        out += [
            "-" * WIDTH,
            "CANCELLED".center(WIDTH),
            line(f"Cancellation fee ({cancel['fee_rate'] * 100:.0f}%)", money(cancel["fee"])),
            line("Refund", money(cancel["refund"])),
        ]

    out += ["=" * WIDTH, "Thank you for staying with us!".center(WIDTH), "=" * WIDTH]
    return "\n".join(out)


def generate_cancellation_slip(booking):
    """Short slip handed to the guest after cancelling."""
    cancel = booking["cancellation"]
    full = "%B %d, %Y %I:%M %p"
    out = [
        "=" * WIDTH,
        "HOTEL BOOKING SYSTEM".center(WIDTH),
        "CANCELLATION SLIP".center(WIDTH),
        "=" * WIDTH,
        f"Booking Number : {booking['booking_number']:05d}",
        f"Customer       : {booking['customer_name']}",
    ]
    out += field("Rooms", booking["room_type"])
    out += [
        f"Check-in       : {format_when(booking.get('check_in'), full)}",
        f"Cancelled on   : {format_when(cancel['cancelled_at'], full)}",
        "-" * WIDTH,
        line("Total paid", money(booking["total_price"])),
        line(f"Cancellation fee ({cancel['fee_rate'] * 100:.0f}%)",
             "-" + money(cancel["fee"])),
        "-" * WIDTH,
        line("REFUND", money(cancel["refund"])),
    ]
    if cancel.get("refund_method"):
        out += field("Refund via", cancel["refund_method"])
    out += ["=" * WIDTH]
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


def save_cancellation_slip(booking, folder=RECEIPT_FOLDER):
    """Writes Cancellation_00001.txt. Returns the path."""
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, f"Cancellation_{booking['booking_number']:05d}.txt")
    with open(path, "w", encoding="utf-8") as file:
        file.write(generate_cancellation_slip(booking) + "\n")
    return path


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
