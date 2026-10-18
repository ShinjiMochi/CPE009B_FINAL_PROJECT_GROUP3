import os
import subprocess
import sys
from datetime import datetime

from BookingManager import booking_manager

WIDTH = 52
RECEIPT_FOLDER = "Receipts"


def money(amount):
    return f"PHP {amount:,.2f}"


def when(text):
    try:
        return datetime.fromisoformat(text).strftime("%B %d, %Y %I:%M %p")
    except (TypeError, ValueError):
        return str(text)


def line(label, amount):
    return f"{label:<{WIDTH - 18}}{amount:>18}"


def generate_receipt(booking_number, manager=booking_manager):
    """Returns the receipt as text. Raises ValueError if the booking doesn't exist."""
    booking = manager.get_booking(booking_number)
    if booking is None:
        raise ValueError(f"Booking {booking_number} was not found.")

    guests = booking.get("guests")
    discount = booking.get("discount") or {}
    payment = booking.get("payment")

    try:
        date_text = datetime.fromisoformat(booking["created_at"]).strftime(
            "%B %d, %Y %I:%M %p"
        )
    except (KeyError, ValueError):
        date_text = booking.get("created_at", "-")

    unit = "hour(s)" if booking["duration_type"] == "Hourly" else "day(s)"

    out = [
        "=" * WIDTH,
        "HOTEL BOOKING SYSTEM".center(WIDTH),
        "OFFICIAL RECEIPT".center(WIDTH),
        "=" * WIDTH,
        f"Booking Number : {booking['booking_number']:05d}",
        f"Date           : {date_text}",
        f"Customer       : {booking['customer_name']}",
    ]

    if booking.get("contact_number"):
        out.append(f"Contact        : {booking['contact_number']}")
    if booking.get("email"):
        out.append(f"Email          : {booking['email']}")

    out += [
        f"Room           : {booking['room_type']}",
        f"Stay           : {booking['duration']} {unit}",
    ]

    if booking.get("check_in"):
        out.append(f"Check-in       : {when(booking['check_in'])}")
    if booking.get("check_out"):
        out.append(f"Check-out      : {when(booking['check_out'])}")

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
        out.append(line(
            f"{item['quantity']} x {item['name']}", money(item["amount"])
        ))

    out += [
        "-" * WIDTH,
        line("TOTAL", money(booking["total_price"])),
        "-" * WIDTH,
    ]

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


def save_receipt(booking_number, folder=RECEIPT_FOLDER, manager=booking_manager):
    """Writes Receipts/Receipt_00001.txt and returns the file path."""
    text = generate_receipt(booking_number, manager)

    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, f"Receipt_{booking_number:05d}.txt")

    with open(path, "w", encoding="utf-8") as file:
        file.write(text + "\n")

    return path


def print_receipt(booking_number, folder=RECEIPT_FOLDER, manager=booking_manager):
    """Saves the receipt, then sends it to the default printer. Raises OSError on failure."""
    path = save_receipt(booking_number, folder, manager)

    try:
        if sys.platform.startswith("win"):
            os.startfile(path, "print")
        else:
            subprocess.run(["lp", path], check=True)
    except (FileNotFoundError, subprocess.CalledProcessError) as error:
        raise OSError(f"Could not print the receipt: {error}")

    return path
