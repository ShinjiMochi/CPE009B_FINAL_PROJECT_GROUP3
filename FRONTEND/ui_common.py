import os
 
from PyQt6.QtCore import Qt, QPoint, QRect, QSize
from PyQt6.QtGui import QColor, QPalette, QPixmap
from PyQt6.QtWidgets import (
    QHBoxLayout, QLabel, QLayout, QPushButton, QSizePolicy
)
 
# =====================================================================
# Theme
# =====================================================================
BLUE = "#1a56db"
BLUE_DARK = "#1446b5"
BORDER = "#e3e6ea"
BACKGROUND = "#f5f6f8"
MUTED = "#6b7280"
TEXT = "#1f2937"
 
STYLESHEET = f"""
* {{
    font-family: "Segoe UI", "Helvetica Neue", Arial, sans-serif;
    font-size: 13px;
    color: {TEXT};
}}
QLabel {{ background: transparent; }}
QLabel#muted {{ color: {MUTED}; font-size: 12px; }}
QLabel#heading {{ font-size: 18px; font-weight: 700; }}
QLabel#sectionTitle {{ font-size: 15px; font-weight: 700; }}
QLabel#price {{ font-size: 22px; font-weight: 700; }}
QLabel#chip {{
    color: {BLUE}; border: 1px solid {BLUE}; border-radius: 10px;
    padding: 2px 8px; font-size: 11px; background: white;
}}
 
QFrame#navbar {{ background: white; border-bottom: 1px solid {BORDER}; }}
QLabel#logo {{ font-size: 20px; font-weight: 800; }}
QLabel#step {{ color: {MUTED}; padding: 4px 10px; }}
QLabel#stepActive {{ color: {BLUE}; font-weight: 700; padding: 4px 10px;
                     border-bottom: 2px solid {BLUE}; }}
 
QFrame#card, QFrame#sidebar {{
    background: white; border: 1px solid {BORDER}; border-radius: 12px;
}}
QFrame#card QLabel, QFrame#sidebar QLabel {{ border: none; }}
 
QGroupBox {{
    background: white; border: 1px solid {BORDER}; border-radius: 12px;
    margin-top: 14px; padding: 12px;
}}
QGroupBox::title {{
    subcontrol-origin: margin; left: 14px; padding: 0 6px;
    font-weight: 700; background: {BACKGROUND};
}}
 
QPushButton {{
    background: {BLUE}; color: white; border: none; border-radius: 16px;
    padding: 8px 20px; font-weight: 600;
}}
QPushButton:hover {{ background: {BLUE_DARK}; }}
QPushButton:disabled {{ background: #c3cad6; color: #f3f4f6; }}
QPushButton[secondary="true"] {{
    background: white; color: {BLUE}; border: 1px solid {BLUE};
}}
QPushButton[secondary="true"]:hover {{ background: #eef3ff; }}
 
QLineEdit, QTextEdit, QPlainTextEdit, QSpinBox, QDoubleSpinBox,
QComboBox, QTimeEdit {{
    background: white; border: 1px solid #cfd5dd; border-radius: 8px;
    padding: 6px 8px;
}}
QLineEdit:focus, QTextEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus,
QComboBox:focus, QTimeEdit:focus {{ border: 1px solid {BLUE}; }}
 
QCheckBox, QRadioButton {{ spacing: 8px; background: transparent; }}
QScrollArea {{ border: none; background: transparent; }}
QScrollArea > QWidget > QWidget {{ background: transparent; }}
 
QCalendarWidget QWidget#qt_calendar_navigationbar {{ background: white; }}
QCalendarWidget QToolButton {{
    color: {TEXT}; background: transparent; border: none;
    padding: 4px 8px; font-weight: 600;
}}
QCalendarWidget QToolButton:hover {{ background: #eef3ff; border-radius: 6px; }}
QCalendarWidget QAbstractItemView:enabled {{
    color: {TEXT}; background: white;
    alternate-background-color: #eef1f5;
    selection-background-color: {BLUE}; selection-color: white;
}}
QCalendarWidget QAbstractItemView:disabled {{ color: #b0b6c0; }}
 
QSlider::groove:horizontal {{ height: 4px; background: {BORDER}; border-radius: 2px; }}
QSlider::sub-page:horizontal {{ background: {BLUE}; border-radius: 2px; }}
QSlider::handle:horizontal {{
    background: white; border: 2px solid {BLUE};
    width: 14px; height: 14px; margin: -6px 0; border-radius: 8px;
}}
"""
EXTRA_STYLES = f"""
QCheckBox::indicator {{
    width: 16px; height: 16px; border-radius: 4px;
    border: 1px solid #9aa3b2; background: white;
}}
QCheckBox::indicator:hover {{ border-color: {BLUE}; }}
QCheckBox::indicator:checked {{
    background: {BLUE}; border-color: {BLUE};
    image: url(CHECK_PATH);
}}
QCheckBox::indicator:disabled {{ background: #eef0f3; border-color: #d5d9e0; }}
 
QRadioButton::indicator {{
    width: 14px; height: 14px; border-radius: 8px;
    border: 1px solid #9aa3b2; background: white;
}}
QRadioButton::indicator:checked {{
    width: 6px; height: 6px; border: 5px solid {BLUE}; background: white;
}}
 
QScrollBar:vertical {{ background: transparent; width: 10px; margin: 2px; }}
QScrollBar::handle:vertical {{
    background: #c3cad6; border-radius: 4px; min-height: 30px;
}}
QScrollBar::handle:vertical:hover {{ background: #9aa3b2; }}
QScrollBar:horizontal {{ background: transparent; height: 10px; margin: 2px; }}
QScrollBar::handle:horizontal {{
    background: #c3cad6; border-radius: 4px; min-width: 30px;
}}
QScrollBar::handle:horizontal:hover {{ background: #9aa3b2; }}
QScrollBar::add-line, QScrollBar::sub-line {{ width: 0; height: 0; }}
QScrollBar::add-page, QScrollBar::sub-page {{ background: transparent; }}
QAbstractSpinBox {{ padding-right: 26px; }}
QAbstractSpinBox::up-button {{
    subcontrol-origin: border; subcontrol-position: top right;
    width: 22px; border: none; background: transparent;
    border-top-right-radius: 8px;
}}
QAbstractSpinBox::down-button {{
    subcontrol-origin: border; subcontrol-position: bottom right;
    width: 22px; border: none; background: transparent;
    border-bottom-right-radius: 8px;
}}
QAbstractSpinBox::up-button:hover, QAbstractSpinBox::down-button:hover {{
    background: #eef3ff;
}}
QAbstractSpinBox::up-arrow {{ image: url(UP_PATH); width: 10px; height: 10px; }}
QAbstractSpinBox::down-arrow {{ image: url(DOWN_PATH); width: 10px; height: 10px; }}
 
QComboBox::drop-down {{
    subcontrol-origin: padding; subcontrol-position: center right;
    width: 24px; border: none;
}}
QComboBox::down-arrow {{ image: url(DOWN_PATH); width: 10px; height: 10px; }}
"""
 
def make_check_icon():
    """Draws a white checkmark PNG once and returns its path."""
    from PyQt6.QtCore import QPointF
    from PyQt6.QtGui import QPainter, QPen
 
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "check.png")
    if not os.path.exists(path):
        pixmap = QPixmap(16, 16)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        pen = QPen(QColor("white"), 2.2)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)
        painter.drawPolyline([QPointF(3.5, 8.5), QPointF(6.8, 11.8), QPointF(12.5, 4.8)])
        painter.end()
        pixmap.save(path)
    return path.replace("\\", "/")
 
def make_arrow_icon(name, up):
    """Draws a small gray triangle PNG once and returns its path."""
    from PyQt6.QtCore import QPointF
    from PyQt6.QtGui import QPainter, QPolygonF
 
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), name)
    if not os.path.exists(path):
        pixmap = QPixmap(10, 10)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(MUTED))
        if up:
            points = [QPointF(1.5, 7), QPointF(8.5, 7), QPointF(5, 2.5)]
        else:
            points = [QPointF(1.5, 3), QPointF(8.5, 3), QPointF(5, 7.5)]
        painter.drawPolygon(QPolygonF(points))
        painter.end()
        pixmap.save(path)
    return path.replace("\\", "/")
 
def apply_theme(app):
    app.setStyle("Fusion")
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(BACKGROUND))
    palette.setColor(QPalette.ColorRole.Base, QColor("white"))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(TEXT))
    palette.setColor(QPalette.ColorRole.Text, QColor(TEXT))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor("#eef1f5"))
    app.setPalette(palette)
    styles = (
            EXTRA_STYLES
            .replace("CHECK_PATH", make_check_icon())
            .replace("UP_PATH", make_arrow_icon("arrow_up.png", True))
            .replace("DOWN_PATH", make_arrow_icon("arrow_down.png", False))
        )
    app.setStyleSheet(STYLESHEET + styles)
 
 
# =====================================================================
# Images
# =====================================================================
BASE_FOLDER = os.path.dirname(os.path.abspath(__file__))
IMAGE_FOLDER = BASE_FOLDER                              # banners, icons, "images/Econo" etc.
FOODS_FOLDER = os.path.join(BASE_FOLDER, "foods")       # dining pictures
 
 
class ImageBox(QLabel):
    """Shows folder/name.jpg|jpeg|png, or a gray placeholder if it's missing."""
 
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
 
 
class BannerBox(QLabel):
    """Full-width banner. Scales with the window: the width follows its
    layout and the height keeps the image's aspect ratio (capped at
    max_height, in which case the image is cropped evenly top and bottom)."""
 
    def __init__(self, name, max_height=250, folder=IMAGE_FOLDER):
        super().__init__()
        self.max_height = max_height
        self.name = os.path.splitext(name)[0]
        self.source = QPixmap()
 
        for extension in (".jpg", ".jpeg", ".png"):
            path = os.path.join(folder, self.name + extension)
            if os.path.exists(path):
                self.source = QPixmap(path)
                break
 
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setMinimumSize(1, 1)
        self.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Fixed)
 
        if self.source.isNull():
            self.setText(f"[ Image here ]\n{self.name}")
            self.setStyleSheet("background: #eeeeee; border: 1px dashed gray;")
            self.setFixedHeight(min(self.max_height, 120))
        else:
            self.setFixedHeight(self.max_height)
 
    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.source.isNull() or self.width() <= 0:
            return
 
        ratio = self.source.height() / self.source.width()
        height = max(1, min(self.max_height, round(self.width() * ratio)))
        if height != self.height():
            self.setFixedHeight(height)
 
        self.setPixmap(self.source.scaled(
            self.width(), height,
            Qt.AspectRatioMode.KeepAspectRatioByExpanding,
            Qt.TransformationMode.SmoothTransformation
        ))
 
 
# =====================================================================
# Layout and screen helpers
# =====================================================================
class FlowLayout(QLayout):
    """Lays widgets out left to right and wraps to a new row when the
    space runs out, so the amenity chips never push the card too wide."""
 
    def __init__(self, spacing=6):
        super().__init__()
        self._items = []
        self._gap = spacing
        self.setContentsMargins(0, 0, 0, 0)
 
    def addItem(self, item):
        self._items.append(item)
 
    def count(self):
        return len(self._items)
 
    def itemAt(self, index):
        return self._items[index] if 0 <= index < len(self._items) else None
 
    def takeAt(self, index):
        return self._items.pop(index) if 0 <= index < len(self._items) else None
 
    def expandingDirections(self):
        return Qt.Orientation(0)
 
    def hasHeightForWidth(self):
        return True
 
    def heightForWidth(self, width):
        return self._arrange(QRect(0, 0, width, 0), apply=False)
 
    def setGeometry(self, rect):
        super().setGeometry(rect)
        self._arrange(rect, apply=True)
 
    def sizeHint(self):
        return self.minimumSize()
 
    def minimumSize(self):
        size = QSize()
        for item in self._items:
            size = size.expandedTo(item.minimumSize())
        return size
 
    def _arrange(self, rect, apply):
        x, y, row_height = rect.x(), rect.y(), 0
        for item in self._items:
            hint = item.sizeHint()
            if x + hint.width() > rect.right() + 1 and row_height > 0:
                x = rect.x()
                y += row_height + self._gap
                row_height = 0
            if apply:
                item.setGeometry(QRect(QPoint(x, y), hint))
            x += hint.width() + self._gap
            row_height = max(row_height, hint.height())
        return y + row_height - rect.y()
 
 
def make_title(text):
    """The big 28px bold heading every screen uses."""
    title = QLabel(text)
    title.setStyleSheet("font-size: 28px; font-weight: bold;")
    return title
 
 
def make_secondary_button(text="Back"):
    button = QPushButton(text)
    button.setProperty("secondary", True)    # outlined look from the theme
    return button
 
 
def make_nav_buttons(next_text="Continue", back=True, extra=()):
    """Bottom button row:  [Back] [extra...] ......... [Next]
    Returns (layout, back_button or None, next_button)."""
    row = QHBoxLayout()
 
    back_button = None
    if back:
        back_button = make_secondary_button("Back")
        row.addWidget(back_button)
 
    for button in extra:
        row.addWidget(button)
 
    row.addStretch()
    next_button = QPushButton(next_text)
    row.addWidget(next_button)
    return row, back_button, next_button
 
