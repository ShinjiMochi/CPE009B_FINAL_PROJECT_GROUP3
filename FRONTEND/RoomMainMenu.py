
import sys
from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QFont
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QSizePolicy,
)


BASE_DIR = Path(__file__).resolve().parent
BACKGROUND_PATH = BASE_DIR / "hotel_background.png"


class AurevelleMainMenu(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Aurevelle Hotel")
        self.resize(1200, 700)
        self.setMinimumSize(850, 550)

        # Main background
        self.background_label = QLabel()
        self.background_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )
        self.background_label.setScaledContents(False)

        pixmap = QPixmap(str(BACKGROUND_PATH))
        if pixmap.isNull():
            self.background_label.setText(
                "Background image not found.\n"
                "Please check assets/hotel_background.png"
            )
            self.background_label.setStyleSheet(
                "color: white; background-color: #24180F;"
            )
            self.original_pixmap = QPixmap()
        else:
            self.original_pixmap = pixmap

        # Welcome title
        self.welcome_label = QLabel(
            "W E L C O M E   T O"
        )
        self.welcome_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )
        self.welcome_label.setStyleSheet(
            "color: #FFFFFF; background: transparent;"
        )
        self.welcome_label.setFont(QFont("Georgia", 13))

        self.hotel_label = QLabel("Aurevelle Hotel")
        self.hotel_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )
        self.hotel_label.setStyleSheet(
            "color: #F5D99B; background: transparent;"
        )
        self.hotel_label.setFont(QFont("Georgia", 34))

        self.tagline_label = QLabel(
            "Your comfort, our priority."
        )
        self.tagline_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )
        self.tagline_label.setStyleSheet(
            "color: white; background: transparent;"
        )
        self.tagline_label.setFont(
            QFont("Georgia", 15, QFont.Weight.Normal)
        )

        # Only one button
        self.book_button = QPushButton(
            "   ♧   Book a Room     →   "
        )
        self.book_button.setCursor(
            Qt.CursorShape.PointingHandCursor
        )
        self.book_button.setMinimumHeight(64)
        self.book_button.setMaximumWidth(390)
        self.book_button.setFont(QFont("Arial", 16))

        self.book_button.setStyleSheet("""
            QPushButton {
                color: #F5D99B;
                background-color: rgba(30, 23, 17, 225);
                border: 2px solid #D9B568;
                border-radius: 30px;
                padding: 12px 24px;
            }

            QPushButton:hover {
                background-color: #594020;
                border: 2px solid #FFE3A1;
            }

            QPushButton:pressed {
                background-color: #19120C;
            }
        """)

        self.book_button.clicked.connect(
            self.open_booking
        )

        # Content layout
        content = QWidget()
        content.setStyleSheet("background: transparent;")

        layout = QVBoxLayout(content)
        layout.setContentsMargins(20, 30, 35, 30)
        layout.setSpacing(22)

        layout.addStretch(2)
        layout.addWidget(self.welcome_label)
        layout.addWidget(self.hotel_label)
        layout.addWidget(self.tagline_label)
        layout.addSpacing(10)

        button_row = QHBoxLayout()
        button_row.addStretch()
        button_row.addWidget(self.book_button)
        button_row.addStretch()

        layout.addLayout(button_row)
        layout.addStretch(3)

        # Background with content layered over it
        self.container = QWidget()
        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setContentsMargins(0, 0, 0, 0)
        self.container_layout.addWidget(self.background_label)
        self.setCentralWidget(self.container)

        # Overlay content on the background
        self.content = content
        self.content.setParent(self.background_label)
        self.content.raise_()

        self.update_background()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_background()

    def update_background(self):
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
            scaled.copy(x, y, size.width(), size.height())
        )

        self.content.setGeometry(
            self.background_label.rect()
        )

    def open_booking(self):
        # TODO: Connect this to your existing
        # RoomSelectionScreen or booking workflow.
        print("Opening Aurevelle Hotel booking...")


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = AurevelleMainMenu()
    window.show()

    sys.exit(app.exec())