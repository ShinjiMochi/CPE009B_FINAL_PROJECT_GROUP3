import sys

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QStackedWidget, QMessageBox,
    QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel
)
from pathlib import Path
from PyQt6.QtGui import QIcon

from customerdetails import CustomerDetails
from GuestOptions import GuestOptions
from logic import get_additional_services
from managers import booking_manager
from PaymentScreen import PaymentScreen
from ReceiptScreen import ReceiptScreen
from RoomSelection import RoomSelectionScreen
from roomservice import RoomService
from Staydur import StayDuration
from ui_common import apply_theme
from RoomMainMenu import AurevelleMainMenu

# names of the steps shown in the navbar, same order as the screens
STEP_NAMES = ["Room", "Stay", "Guests", "Details", "Dining", "Payment", "Receipt"]

# main window of the app. it holds all the screens and the booking data and connects them together
class HotelApp(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Aurevelle Booking System")
        self.setWindowIcon(
            QIcon(str(Path(__file__).resolve().parent/"aurevelle_logo.ico"))
        )
        self.resize(1100, 700)

        # dictionary where we keep everything the user entered, until they pay
        self.data = {}   # everything collected so far

        # make each screen one time only, then we just reuse them
        self.menu = AurevelleMainMenu()
        self.room_selection = RoomSelectionScreen()
        self.stay = StayDuration()
        self.guest = GuestOptions(get_additional_services())
        self.customer = CustomerDetails()
        self.dining = RoomService()
        self.payment = PaymentScreen()
        self.receipt = ReceiptScreen()

        # same order as STEP_NAMES (the menu sits in front of these, at index 0)
        # the booking steps in order (the main menu is not here, it's at index 0 of the stack)
        self.screens = (
            self.room_selection, self.stay, self.guest, self.customer,
            self.dining, self.payment, self.receipt
        )
        # the stack only shows one screen at a time
        self.stack = QStackedWidget()
        self.stack.addWidget(self.menu)
        for screen in self.screens:
            self.stack.addWidget(screen)

        self.navbar = self.make_navbar()

        # navbar on top, then the current screen under it
        central = QWidget()
        central_layout = QVBoxLayout(central)
        central_layout.setContentsMargins(0, 0, 0, 0)
        central_layout.setSpacing(0)
        central_layout.addWidget(self.navbar)
        central_layout.addWidget(self.stack, 1)
        self.setCentralWidget(central)
        self.stack.currentChanged.connect(self.update_steps)
        self.update_steps()

        # forward
        # when a screen is done it sends a signal, and these functions save the data and go to the next screen
        self.menu.book_requested.connect(lambda: self.show_screen(self.room_selection))
        self.room_selection.room_selected.connect(self.on_room_selected)
        self.stay.continued.connect(self.on_stay_continued)
        self.guest.continued.connect(self.on_guest_continued)
        self.customer.continued.connect(self.on_customer_continued)
        self.dining.continued.connect(self.on_dining_continued)
        self.payment.pay_requested.connect(self.on_pay)

        # back
        # back buttons just go to the screen before
        self.stay.back_requested.connect(lambda: self.show_screen(self.room_selection))
        self.guest.back_requested.connect(lambda: self.show_screen(self.stay))
        self.customer.back_requested.connect(lambda: self.show_screen(self.guest))
        self.dining.back_requested.connect(lambda: self.show_screen(self.customer))
        self.payment.back_requested.connect(lambda: self.show_screen(self.dining))

        self.receipt.new_booking_requested.connect(self.new_booking)

    # makes the top bar with the logo and the step names
    def make_navbar(self):
        bar = QFrame()
        bar.setObjectName("navbar")
        row = QHBoxLayout(bar)
        row.setContentsMargins(24, 10, 24, 6)

        logo = QLabel("Hotel Booking")
        logo.setObjectName("logo")
        row.addWidget(logo)
        row.addSpacing(24)

        self.step_labels = []
        for name in STEP_NAMES:
            label = QLabel(name)
            self.step_labels.append(label)
            row.addWidget(label)
        row.addStretch()
        return bar

    # hides the navbar on the main menu and highlights the step we are on
    def update_steps(self, *args):
        # index 0 is the main menu (no navbar); the steps start at index 1
        self.navbar.setVisible(self.stack.currentWidget() is not self.menu)
        current = self.stack.currentIndex() - 1
        for index, label in enumerate(self.step_labels):
            label.setObjectName("stepActive" if index == current else "step")
            # refresh the style so the new look (active or not) shows up
            label.style().unpolish(label)
            label.style().polish(label)

    # changes which screen is showing
    def show_screen(self, screen):
        self.stack.setCurrentWidget(screen)

    # room -> stay: save the room the user picked and send it to the stay screen
    def on_room_selected(self, room):
        self.data["room"] = room
        self.stay.set_room(room)
        self.show_screen(self.stay)

    # stay -> guests: save the stay info and give the room charge to the guest screen
    def on_stay_continued(self, stay):
        self.data.update(stay)   # duration_type, duration, room_charge, check_in, check_out
        self.guest.set_room_charge(stay["room_charge"], self.data["room"].room_type)
        self.show_screen(self.guest)

    # guests -> details: save the guests, discount and services
    def on_guest_continued(self, guest_data):
        self.data.update(guest_data)   # guests, discount, services
        self.show_screen(self.customer)

    # details -> dining: save the customer info
    def on_customer_continued(self, customer):
        self.data["customer"] = customer
        self.show_screen(self.dining)

    def on_dining_continued(self, items):
        self.data["dining"] = items
        self.payment.set_summary(self.data)
        self.show_screen(self.payment)

    # payment -> receipt: make the booking using everything we collected, then show the receipt
    def on_pay(self, payment):
        d = self.data

        try:
            booking = booking_manager.create_booking(
                customer=d["customer"],
                room=d["room"],
                duration_type=d["duration_type"],
                duration=d["duration"],
                guests=d["guests"],
                use_discount=d["discount"]["discount_used"],
                services=d["services"],
                dining=d["dining"],
                payment_method=payment["method"],
                payment_provider=payment["provider"],
                payment_details=payment["details"],
                check_in=d.get("check_in"),
                check_out=d.get("check_out")
            )
        # if the payment or saving fails, show a warning and stop here
        except (ValueError, OSError) as error:
            QMessageBox.warning(self, "Payment / Booking Error", str(error))
            return

        self.receipt.show_receipt(booking)   # no re-reading of Bookings files
        self.show_screen(self.receipt)

    # clear all the data and screens then go back to the main menu
    def new_booking(self):
        self.data.clear()
        for screen in self.screens:
            screen.reset()
        self.show_screen(self.menu)


# this is where the program starts
if __name__ == "__main__":
    app = QApplication(sys.argv)
    apply_theme(app)
    window = HotelApp()
    window.show()
    sys.exit(app.exec())
