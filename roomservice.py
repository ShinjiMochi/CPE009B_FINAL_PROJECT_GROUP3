from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QGridLayout,
    QLabel, QPushButton, QSpinBox
)

class RoomService(QWidget):

    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)

        title = QLabel("Room Service")
        title.setStyleSheet(
            "font-size: 28px; font-weight: bold;"
        )

        layout.addWidget(title)

        menu = QGridLayout()

        foods = [
            ("Food Here", "Price"),
            ("Food Here", "Price"),
            ("Food Here", "Price"),
            ("Food Here", "Price"),
            ("Food Here", "Price"),
            ("Food Here", "Price")
        ]

        for i, (food, price) in enumerate(foods):

            item = QVBoxLayout()
            item.addWidget(
                QLabel("[ FOOD IMAGE ]")
            )
            item.addWidget(
                QLabel(food)
            )
            item.addWidget(
                QLabel(price)
            )
            item.addWidget(
                QSpinBox()
            )
            item.addWidget(
                QPushButton("Add to Order")
            )
            menu.addLayout(
                item,
                i // 3,
                i % 3
            )
        layout.addLayout(menu)
        layout.addWidget(
            QPushButton("View Order")
        )