import os
from datetime import datetime

from BACKEND.DiscountManager import apply_discount, calculate_final_total
from BACKEND.PaymentManager import process_payment

SEPARATOR = "-" * 40


class BookingManager:
    def __init__(self):
        self.booking_file = "Bookings.txt"
        self.bookings = []
        self.next_booking_number = self.get_next_booking_number()

    def get_next_booking_number(self):
        if not os.path.exists(self.booking_file):
            return 1

        highest_booking_number = 0

        with open(self.booking_file, "r", encoding="utf-8") as file:
            for line in file:
                if line.startswith("Booking Number: "):
                    try:
                        booking_number = int(
                            line.split(": ", 1)[1].strip()
                        )

                        if booking_number > highest_booking_number:
                            highest_booking_number = booking_number

                    except ValueError:
                        continue

        return highest_booking_number + 1

    def generate_booking_number(self):
        booking_number = self.next_booking_number
        self.next_booking_number += 1
        return booking_number

    def calculate_price(self, room, duration_type, duration):
        if duration <= 0:
            raise ValueError("Duration must be greater than zero.")

        if duration_type == "Hourly":
            total_price = room.hourly_rate * duration

        elif duration_type == "Daily":
            total_price = room.daily_rate * duration

        else:
            raise ValueError("Invalid duration type.")

        return round(total_price, 2)

    # ---------- saving ----------
    def save_booking(self, booking):
        """Same format as before. Extra lines are only written when present."""
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

        if "room_charge" in booking:
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

        with open(self.booking_file, "a", encoding="utf-8") as file:
            file.write("\n".join(lines) + "\n")

    # ---------- reading (used by the receipt) ----------
    @staticmethod
    def _money(text):
        return float(text.replace("PHP", "").replace(",", "").strip())

    def parse_block(self, block):
        data, services, dining = {}, [], []

        for raw in block.splitlines():
            if ": " not in raw:
                continue
            key, value = raw.split(": ", 1)
            key, value = key.strip(), value.strip()

            if key == "Service":
                name, price = value.rsplit(" | ", 1)
                services.append({"name": name, "price": float(price)})
            elif key == "Dining":
                name, quantity, price = value.rsplit(" | ", 2)
                quantity, price = int(quantity), float(price)
                dining.append({
                    "name": name, "price": price, "quantity": quantity,
                    "amount": round(price * quantity, 2)
                })
            else:
                data[key] = value

        if "Booking Number" not in data:
            return None

        try:
            duration, duration_type = data["Duration"].split(" ", 1)
            total_price = self._money(data["Total Price"])

            guests = None
            if "Guests" in data:
                total = int(data["Guests"])
                seniors = int(data.get("Seniors", 0))
                children = int(data.get("Children", 0))
                guests = {
                    "total_guests": total, "seniors": seniors,
                    "children": children, "adults": total - seniors - children
                }

            discount_amount = self._money(data["Discount"]) if "Discount" in data else 0.0
            discount = {
                "discount_used": discount_amount > 0,
                "discount_rate": float(data.get("Discount Rate", 0)),
                "discount_amount": discount_amount
            }

            payment = None
            if "Payment Method" in data:
                payment = {
                    "method": data["Payment Method"],
                    "provider": data.get("Payment Provider"),
                    "reference": data.get("Payment Reference"),
                    "status": data.get("Payment Status", "Approved"),
                }
                if "Amount Tendered" in data:
                    payment["amount_tendered"] = float(data["Amount Tendered"])
                    payment["change"] = float(data.get("Change", 0))
                if "Card Last4" in data:
                    payment["card_last4"] = data["Card Last4"]

            return {
                "booking_number": int(data["Booking Number"]),
                "created_at": data.get("Date"),
                "customer_name": data["Customer Name"],
                "contact_number": data.get("Contact Number"),
                "email": data.get("Email"),
                "room_type": data["Room Type"],
                "duration_type": duration_type,
                "duration": int(duration),
                "check_in": data.get("Check-in"),
                "check_out": data.get("Check-out"),
                "guests": guests,
                "room_charge": self._money(data["Room Charge"]) if "Room Charge" in data else total_price,
                "discount": discount,
                "services": services,
                "dining": dining,
                "total_price": total_price,
                "payment": payment,
                "payment_status": "Paid" if payment else "Unpaid"
            }
        except (KeyError, ValueError):
            return None

    def get_booking(self, booking_number):
        """Reads Bookings.txt and returns the booking dict, or None."""
        if not os.path.exists(self.booking_file):
            return None

        with open(self.booking_file, "r", encoding="utf-8") as file:
            text = file.read()

        for block in text.split(SEPARATOR):
            booking = self.parse_block(block)
            if booking and booking["booking_number"] == booking_number:
                return booking

        return None

    # ---------- creating ----------
    def create_booking(
        self,
        customer_name,
        room,
        duration_type,
        duration,
        guests=None,
        use_discount=False,
        services=None,
        dining=None,
        contact_number=None,
        email=None,
        payment_method=None,
        payment_provider=None,
        payment_details=None,
        check_in=None,
        check_out=None
    ):
        """
        The first four arguments work exactly like before; the rest are optional.

        guests:   GuestInfo.to_dict() result
        services: [{"name": ..., "price": ...}]
        dining:   [{"name": ..., "price": ..., "quantity": ...}]
        payment_method: "Cash", "E-Wallet / E-Banking" or "Card" (see PaymentManager)
        check_in, check_out: ISO strings like "2026-10-20T14:00" (or datetimes)
        """
        if not customer_name.strip():
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

        room_charge = self.calculate_price(room, duration_type, duration)
        discount = apply_discount(room_charge, use_discount)

        services = services or []
        dining_items = [
            {**d, "amount": round(d["price"] * d["quantity"], 2)}
            for d in (dining or [])
        ]

        total_price = calculate_final_total(
            discount,
            sum(d["amount"] for d in dining_items),
            sum(s["price"] for s in services)
        )

        # Pay before taking a booking number so a failed payment doesn't skip one
        payment = None
        if payment_method is not None:
            payment = process_payment(
                payment_method, total_price, payment_provider, payment_details
            )

        booking = {
            "booking_number": self.generate_booking_number(),
            "created_at": datetime.now().isoformat(timespec="seconds"),
            "customer_name": customer_name.strip(),
            "contact_number": contact_number,
            "email": email,
            "room_type": room.room_type,
            "duration_type": duration_type,
            "duration": duration,
            "check_in": check_in,
            "check_out": check_out,
            "guests": guests,
            "room_charge": room_charge,
            "discount": discount,
            "services": services,
            "dining": dining_items,
            "total_price": total_price,
            "payment": payment,
            "payment_status": "Paid" if payment else "Unpaid"
        }

        self.save_booking(booking)
        self.bookings.append(booking)

        return booking


# Create one shared booking manager
booking_manager = BookingManager()