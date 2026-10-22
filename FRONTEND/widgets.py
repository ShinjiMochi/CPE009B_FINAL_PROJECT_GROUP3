import os

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QLabel

BASE_FOLDER = os.path.dirname(os.path.abspath(__file__))
IMAGE_FOLDER = os.path.join(BASE_FOLDER, "images")   # rooms, banners, icons
FOODS_FOLDER = os.path.join(BASE_FOLDER, "foods")    # dining pictures


class ImageBox(QLabel):

    def __init__(self, name, width, height, folder=IMAGE_FOLDER):
        super().__init__()
        self.setFixedSize(width, height)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)

        name = os.path.splitext(name)[0]
        pixmap = QPixmap()
        for extension in (".jpg", ".jpeg", ".png"):
            path = os.path.join(folder, name + extension)
            if os.path.exists(path):
                pixmap = QPixmap(path)
                break

        if pixmap.isNull():
            self.setText(f"[ Image here ]\n{name}")
            self.setStyleSheet("background: #eeeeee; border: 1px dashed gray;")
        else:
            self.setPixmap(pixmap.scaled(
                width, height,
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation
            ))