from pathlib import Path

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QWidget, QLabel, QPushButton


BASE_DIR = Path(__file__).resolve().parent
BACKGROUND_PATH = BASE_DIR / "hotel_background.png"


class AurevelleMainMenu(QWidget):
    book_requested = pyqtSignal()

    def __init__(self):
        super().__init__()

        self.setMinimumSize(850, 550)

        self.background_label = QLabel(self)
        self.background_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )
        self.background_label.setScaledContents(False)

        self.original_pixmap = QPixmap(str(BACKGROUND_PATH))

        if self.original_pixmap.isNull():
            self.background_label.setText(
                "Background image not found:\n"
                "hotel_background.png"
            )
            self.background_label.setStyleSheet(
                "color: white; background-color: #24180F;"
            )

        self.content = QWidget(self.background_label)
        self.content.setStyleSheet("background: transparent;")

        self.book_button = QPushButton(self.content)
        self.book_button.setText("")
        self.book_button.setCursor(
            Qt.CursorShape.PointingHandCursor
        )
        self.book_button.setFocusPolicy(
            Qt.FocusPolicy.NoFocus
        )

        self.book_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                border-radius: 30px;
            }

            QPushButton:hover {
                background-color: rgba(245, 217, 155, 15);
                border: none;
            }

            QPushButton:pressed {
                background-color: rgba(245, 217, 155, 30);
                border: none;
            }
        """)

        self.book_button.clicked.connect(
            self.book_requested.emit
        )

        self.update_background()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_background()

    def update_background(self):
        self.background_label.setGeometry(self.rect())
        self.content.setGeometry(
            self.background_label.rect()
        )

        if self.original_pixmap.isNull():
            return

        size = self.background_label.size()

        if size.width() <= 0 or size.height() <= 0:
            return
        
        scaled = self.original_pixmap.scaled(
            size,
            Qt.AspectRatioMode.KeepAspectRatioByExpanding,
            Qt.TransformationMode.SmoothTransformation,
        )

        x = (scaled.width() - size.width()) // 2
        y = (scaled.height() - size.height()) // 2

        self.background_label.setPixmap(
            scaled.copy(
                x,
                y,
                size.width(),
                size.height()
            )
        )

        self.book_button.setGeometry(
            int(size.width() * 0.605),
            int(size.height() * 0.455),
            int(size.width() * 0.265),
            int(size.height() * 0.09),
        )

        self.content.raise_()
        self.book_button.raise_()