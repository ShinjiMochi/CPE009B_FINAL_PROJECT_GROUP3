import tkinter as tk
from tkinter import ttk, messagebox

from RoomTypes import get_all_rooms
from Staydur import StayDurationWindow


class RoomSelectionWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Hotel Room Selection")
        self.root.geometry("850x650")
        self.root.resizable(False, False)

        self.rooms = get_all_rooms()
        self.selected_room_type = tk.StringVar(value="Econo")
        self.image_references = []

        self.create_widgets()

    def create_widgets(self):
        ttk.Label(
            self.root,
            text="HOTEL ROOM BOOKING SYSTEM",
            font=("Arial", 20, "bold")
        ).pack(pady=(20, 5))

        ttk.Label(
            self.root,
            text="Choose a room that suits your needs",
            font=("Arial", 11)
        ).pack(pady=(0, 15))

        room_container = ttk.Frame(self.root)
        room_container.pack(padx=15, fill="both", expand=True)

        for room_type, room in self.rooms.items():
            card = ttk.LabelFrame(
                room_container,
                text=f"{room_type} Room",
                padding=10
            )
            card.pack(
                side="left",
                fill="both",
                expand=True,
                padx=7,
                pady=5
            )

            # Optional room image: PNG or GIF supported by Tkinter
            image_loaded = False

            try:
                room_image = tk.PhotoImage(file=room.image)
                self.image_references.append(room_image)

                ttk.Label(
                    card,
                    image=room_image
                ).pack(pady=5)

                image_loaded = True

            except tk.TclError:
                pass

            if not image_loaded:
                ttk.Label(
                    card,
                    text="[Room Image]",
                    font=("Arial", 12, "italic"),
                    width=20,
                    anchor="center"
                ).pack(pady=20)

            ttk.Label(
                card,
                text=room.description,
                wraplength=210,
                justify="center"
            ).pack(pady=8)

            ttk.Label(
                card,
                text=f"₱{room.hourly_rate:.2f} / hour",
                font=("Arial", 10, "bold")
            ).pack()

            ttk.Label(
                card,
                text=f"₱{room.daily_rate:,.2f} / day",
                font=("Arial", 10, "bold")
            ).pack(pady=3)

            ttk.Label(
                card,
                text="Amenities:\n" + "\n".join(
                    f"• {amenity}" for amenity in room.amenities
                ),
                justify="left"
            ).pack(pady=10, anchor="w")

            ttk.Radiobutton(
                card,
                text=f"Select {room_type}",
                variable=self.selected_room_type,
                value=room_type
            ).pack(side="bottom", pady=10)

        ttk.Button(
            self.root,
            text="Continue to Stay Duration",
            command=self.open_stay_duration
        ).pack(pady=20)

    def open_stay_duration(self):
        room_type = self.selected_room_type.get()
        selected_room = self.rooms.get(room_type)

        if selected_room is None:
            messagebox.showerror(
                "Error",
                "Please select a valid room."
            )
            return

        StayDurationWindow(self.root, selected_room)


if __name__ == "__main__":
    root = tk.Tk()
    app = RoomSelectionWindow(root)
    root.mainloop()