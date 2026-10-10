import tkinter as tk
from tkinter import ttk, messagebox

from BookingManager import booking_manager


class StayDurationWindow:
    def __init__(self, parent, room):
        self.room = room

        self.window = tk.Toplevel(parent)
        self.window.title("Stay Duration")
        self.window.geometry("460x570")
        self.window.resizable(False, False)

        self.duration_type = tk.StringVar(value="Daily")
        self.duration_value = tk.StringVar(value="1")
        self.customer_name = tk.StringVar()

        self.create_widgets()

    def create_widgets(self):
        ttk.Label(
            self.window,
            text="Stay Duration and Booking",
            font=("Arial", 16, "bold")
        ).pack(pady=15)

        ttk.Label(
            self.window,
            text=f"Selected Room: {self.room.room_type}",
            font=("Arial", 12, "bold")
        ).pack(pady=5)

        ttk.Label(
            self.window,
            text=self.room.description,
            wraplength=380
        ).pack(pady=5)

        ttk.Label(
            self.window,
            text=f"Hourly Rate: PHP {self.room.hourly_rate:.2f}"
        ).pack()

        ttk.Label(
            self.window,
            text=f"Daily Rate: PHP {self.room.daily_rate:,.2f}"
        ).pack(pady=3)

        ttk.Label(
            self.window,
            text="Customer Name:"
        ).pack(pady=(15, 3))

        ttk.Entry(
            self.window,
            textvariable=self.customer_name,
            width=35
        ).pack()

        ttk.Label(
            self.window,
            text="Choose Stay Duration:"
        ).pack(pady=(15, 5))

        ttk.Radiobutton(
            self.window,
            text="Per Hour",
            variable=self.duration_type,
            value="Hourly",
            command=self.update_duration_label
        ).pack()

        ttk.Radiobutton(
            self.window,
            text="Per Day",
            variable=self.duration_type,
            value="Daily",
            command=self.update_duration_label
        ).pack()

        self.duration_label = ttk.Label(
            self.window,
            text="Number of days:"
        )
        self.duration_label.pack(pady=(10, 3))

        ttk.Entry(
            self.window,
            textvariable=self.duration_value,
            width=15
        ).pack()

        ttk.Button(
            self.window,
            text="Compute Total",
            command=self.show_total
        ).pack(pady=12)

        self.total_label = ttk.Label(
            self.window,
            text="Total Price: PHP 0.00",
            font=("Arial", 13, "bold")
        )
        self.total_label.pack(pady=10)

        ttk.Button(
            self.window,
            text="Confirm Booking",
            command=self.confirm_booking
        ).pack(pady=5)

    def update_duration_label(self):
        if self.duration_type.get() == "Hourly":
            self.duration_label.config(
                text="Number of hours:"
            )
        else:
            self.duration_label.config(
                text="Number of days:"
            )

    def get_duration(self):
        try:
            duration = int(self.duration_value.get())

            if duration <= 0:
                raise ValueError

            return duration

        except ValueError:
            messagebox.showerror(
                "Invalid Duration",
                "Please enter a whole number greater than zero.",
                parent=self.window
            )
            return None

    def show_total(self):
        duration = self.get_duration()

        if duration is None:
            return

        try:
            total_price = booking_manager.calculate_price(
                self.room,
                self.duration_type.get(),
                duration
            )

            self.total_label.config(
                text=f"Total Price: PHP {total_price:,.2f}"
            )

        except ValueError as error:
            messagebox.showerror(
                "Calculation Error",
                str(error),
                parent=self.window
            )

    def confirm_booking(self):
        name = self.customer_name.get().strip()

        if not name:
            messagebox.showerror(
                "Missing Information",
                "Please enter the customer's name.",
                parent=self.window
            )
            return

        duration = self.get_duration()

        if duration is None:
            return

        try:
            booking = booking_manager.create_booking(
                customer_name=name,
                room=self.room,
                duration_type=self.duration_type.get(),
                duration=duration
            )

        except (ValueError, OSError) as error:
            messagebox.showerror(
                "Booking Error",
                f"Could not save booking:\n{error}",
                parent=self.window
            )
            return

        messagebox.showinfo(
            "Booking Confirmed",
            f"Booking Number: {booking['booking_number']}\n"
            f"Customer: {booking['customer_name']}\n"
            f"Room: {booking['room_type']}\n"
            f"Duration: {booking['duration']} "
            f"{booking['duration_type']}\n"
            f"Total Price: PHP {booking['total_price']:,.2f}\n\n"
            "Transaction saved to Bookings.txt.",
            parent=self.window
        )

        self.window.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()

    from RoomTypes import get_room

    selected_room = get_room("Econo")
    StayDurationWindow(root, selected_room)

    root.mainloop()