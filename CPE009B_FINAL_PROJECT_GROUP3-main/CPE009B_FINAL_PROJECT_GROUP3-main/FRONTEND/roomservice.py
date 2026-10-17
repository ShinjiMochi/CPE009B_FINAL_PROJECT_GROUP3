from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QGridLayout,
    QLabel, QPushButton, QSpinBox, QMessageBox
)
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt
from pathlib import Path


class RoomService(QWidget):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Room Service")
        layout = QVBoxLayout(self)

        title = QLabel("Room Service")
        title.setStyleSheet("font-size: 28px; font-weight: bold;")
        layout.addWidget(title)

        menu = QGridLayout()
        self.order = {}

        foods = [
            ("Cheese Burger", 300, "burger.jpg"),
            ("Fruit Platter", 500, "fruits.jpg"),
            ("Carbonara", 450, "pasta.jpg"),
            ("All-Meat Pizza", 1100, "pizza.jpg"),
            ("Caesar Salad", 600, "salad.jpg"),
            ("Egg Drop Soup", 550, "soup.jpg")
        ]

        for i, (name, price, picture) in enumerate(foods):
            item = QVBoxLayout()

            # Food picture
            image = QLabel()
            path = Path(__file__).parent / "foods" / picture
            pixmap = QPixmap(str(path))

            if pixmap.isNull():
                image.setText("Image not found!")
            else:
                image.setPixmap(
                    pixmap.scaled(
                        200, 120,
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation
                    )
                )

            image.setAlignment(Qt.AlignmentFlag.AlignCenter)
            item.addWidget(image)

            # Food name and price
            item.addWidget(QLabel(name))
            item.addWidget(QLabel(f"Price: ₱{price}"))

            # Quantity
            quantity = QSpinBox()
            quantity.setMinimum(1)
            quantity.setMaximum(99)
            item.addWidget(quantity)

            # Add to Order button
            button = QPushButton("Add to Order")
            button.clicked.connect(
                lambda checked=False, n=name, p=price, q=quantity:
                self.AddOrder(n, p, q.value())
            )
            item.addWidget(button)

            menu.addLayout(item, i // 3, i % 3)

        layout.addLayout(menu)

        # View Order button
        view = QPushButton("View Order")
        view.clicked.connect(self.ViewOrder)
        layout.addWidget(view)

    def AddOrder(self, name, price, quantity):
        self.order[name] = self.order.get(name, 0) + (price * quantity)

        QMessageBox.information(
            self, "Order Added",
            f"{quantity} x {name} added to your order!"
        )

    def ViewOrder(self):
        if not self.order:
            QMessageBox.information(
                self, "Order", "There are no orders!"
            )
            return

        details = "<br>".join(
            f"{name}: ₱{amount}"
            for name, amount in self.order.items()
        )

        total = sum(self.order.values())

        msg = QMessageBox(self)
        msg.setWindowTitle("Your Orders")
        msg.setTextFormat(Qt.TextFormat.RichText)
        msg.setText(
            f"{details}<br><br><b>Total: ₱{total}</b>"
        )
        msg.exec()