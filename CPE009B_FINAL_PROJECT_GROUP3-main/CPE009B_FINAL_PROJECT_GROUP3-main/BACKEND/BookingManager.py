import os

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

    def save_booking(self, booking):
        with open(self.booking_file, "a", encoding="utf-8") as file:
            file.write(
                f"Booking Number: {booking['booking_number']}\n"
                f"Customer Name: {booking['customer_name']}\n"
                f"Room Type: {booking['room_type']}\n"
                f"Duration: {booking['duration']} "
                f"{booking['duration_type']}\n"
                f"Total Price: PHP {booking['total_price']:,.2f}\n"
                f"{'-' * 40}\n"
            )

    def create_booking(
        self,
        customer_name,
        room,
        duration_type,
        duration
    ):
        if not customer_name.strip():
            raise ValueError("Customer name cannot be empty.")

        total_price = self.calculate_price(
            room,
            duration_type,
            duration
        )

        booking = {
            "booking_number": self.generate_booking_number(),
            "customer_name": customer_name.strip(),
            "room_type": room.room_type,
            "duration_type": duration_type,
            "duration": duration,
            "total_price": total_price
        }

        self.save_booking(booking)
        self.bookings.append(booking)

        return booking


# Create one shared booking manager
booking_manager = BookingManager()