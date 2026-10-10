import sys
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QTabWidget
)


from customerdetails import CustomerDetails
from roomservice import RoomService

class HotelApp(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle(
            "Hotel Booking System"
        )
        self.resize(1100, 700)
        tabs = QTabWidget()


        tabs.addTab(
            CustomerDetails(),
            "Customer"
        )

        tabs.addTab(
            RoomService(),
            "Room Service"
        )
        self.setCentralWidget(tabs)


app = QApplication(sys.argv)
window = HotelApp()
window.show()
sys.exit(app.exec())