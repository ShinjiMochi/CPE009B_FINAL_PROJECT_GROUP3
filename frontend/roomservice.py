from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QGridLayout, QScrollArea,
    QLabel, QPushButton, QSpinBox, QMessageBox
)

from logic import get_dining_menu
from ui_common import ImageBox, FOODS_FOLDER, make_title, make_nav_buttons


class RoomService(QWidget):
    continued = pyqtSignal(list)    
    back_requested = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Room Service")

        self.menu = get_dining_menu()
        self.order = {}      
        self.spins = {}

        layout = QVBoxLayout(self)
        layout.addWidget(make_title("Room Service"))
        layout.addWidget(QLabel("Dining is optional. Press Continue to skip."))

        content = QWidget()
        grid = QGridLayout(content)

        for index, (name, info) in enumerate(self.menu.items()):
            item = QVBoxLayout()
            item.addWidget(
                ImageBox(info["image"], 200, 120, FOODS_FOLDER),
                alignment=Qt.AlignmentFlag.AlignCenter
            )
            item.addWidget(QLabel(name), alignment=Qt.AlignmentFlag.AlignCenter)
            item.addWidget(QLabel(f"Price: ₱{info['price']:,.2f}"),
                           alignment=Qt.AlignmentFlag.AlignCenter)

            spin = QSpinBox()
            spin.setRange(1, 99)
            self.spins[name] = spin
            item.addWidget(spin)

            button = QPushButton("Add to Order")
            button.clicked.connect(
                lambda checked=False, n=name: self.add_order(n, self.spins[n].value())
            )
            item.addWidget(button)

            grid.addLayout(item, index // 3, index % 3)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(content)
        layout.addWidget(scroll)

        self.order_label = QLabel()
        self.order_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(self.order_label)

        view = QPushButton("View Order")
        clear = QPushButton("Clear Order")
        buttons, back, continue_button = make_nav_buttons(extra=(view, clear))
        layout.addLayout(buttons)

        back.clicked.connect(self.back_requested.emit)
        view.clicked.connect(self.view_order)
        clear.clicked.connect(self.clear_order)
        continue_button.clicked.connect(self.on_continue)

        self.refresh()

    def add_order(self, name, quantity):
        self.order[name] = self.order.get(name, 0) + quantity
        self.spins[name].setValue(1)
        self.refresh()

    def clear_order(self):
        self.order.clear()
        self.refresh()

    def get_order_items(self):
        return [
            {"name": name, "price": self.menu[name]["price"], "quantity": quantity}
            for name, quantity in self.order.items()
        ]

    def order_total(self):
        return sum(i["price"] * i["quantity"] for i in self.get_order_items())

    def refresh(self):
        if not self.order:
            self.order_label.setText("No items ordered yet.")
        else:
            count = sum(self.order.values())
            self.order_label.setText(
                f"{count} item(s) ordered - ₱{self.order_total():,.2f}"
            )

    def view_order(self):
        if not self.order:
            QMessageBox.information(self, "Order", "There are no orders!")
            return

        details = "<br>".join(
            f"{i['quantity']} x {i['name']}: ₱{i['price'] * i['quantity']:,.2f}"
            for i in self.get_order_items()
        )

        msg = QMessageBox(self)
        msg.setWindowTitle("Your Orders")
        msg.setTextFormat(Qt.TextFormat.RichText)
        msg.setText(f"{details}<br><br><b>Total: ₱{self.order_total():,.2f}</b>")
        msg.exec()

    def on_continue(self):
        self.continued.emit(self.get_order_items())

    def reset(self):
        self.clear_order()
        for spin in self.spins.values():
            spin.setValue(1)