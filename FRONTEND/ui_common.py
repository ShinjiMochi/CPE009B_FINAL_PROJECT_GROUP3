import os
 
from PyQt6.QtCore import Qt, QPoint, QRect, QSize
from PyQt6.QtGui import QColor, QPalette, QPixmap
from PyQt6.QtWidgets import (
    QHBoxLayout, QLabel, QLayout, QPushButton, QSizePolicy
)
 

# Theme
ACCENT = "#9c6a1d"         # bronze gold (buttons, active states)
ACCENT_DARK = "#7d5415"    # button hover
ACCENT_SOFT = "#f6ead2"    # light gold wash for hovers
GOLD_LIGHT = "#f0c674"     # gold used on the dark navbar
WALNUT = "#2b1a0d"         # navbar background
CREAM = "#f7ecd6"          # text on the navbar
BORDER = "#e6d9c0"
BACKGROUND = "#faf5ea"
MUTED = "#7a6650"
TEXT = "#2e1c0e"
 
# the stylesheet (like CSS) that gives the whole app its look
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
    color: {ACCENT}; border: 1px solid {ACCENT}; border-radius: 10px;
    padding: 2px 8px; font-size: 11px; background: white;
}}
 
QFrame#navbar {{ background: {WALNUT}; border-bottom: 2px solid {ACCENT}; }}
QLabel#logo {{ color: {CREAM}; font-size: 20px; font-weight: 800; }}
QLabel#step {{ color: #c9b697; padding: 4px 10px; }}
QLabel#stepActive {{ color: {GOLD_LIGHT}; font-weight: 700; padding: 4px 10px;
                     border-bottom: 2px solid {GOLD_LIGHT}; }}
 
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
    background: {ACCENT}; color: white; border: none; border-radius: 16px;
    padding: 8px 20px; font-weight: 600;
}}
QPushButton:hover {{ background: {ACCENT_DARK}; }}
QPushButton:disabled {{ background: #d9cfbd; color: #f8f3e8; }}
QPushButton[secondary="true"] {{
    background: white; color: {ACCENT}; border: 1px solid {ACCENT};
}}
QPushButton[secondary="true"]:hover {{ background: {ACCENT_SOFT}; }}
 
QLineEdit, QTextEdit, QPlainTextEdit, QSpinBox, QDoubleSpinBox,
QComboBox, QTimeEdit {{
    background: white; border: 1px solid #dccfb7; border-radius: 8px;
    padding: 6px 8px;
}}
QLineEdit:focus, QTextEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus,
QComboBox:focus, QTimeEdit:focus {{ border: 1px solid {ACCENT}; }}
 
QCheckBox, QRadioButton {{ spacing: 8px; background: transparent; }}
QScrollArea {{ border: none; background: transparent; }}
QScrollArea > QWidget > QWidget {{ background: transparent; }}
 
QCalendarWidget QWidget#qt_calendar_navigationbar {{ background: white; }}
QCalendarWidget QToolButton {{
    color: {TEXT}; background: transparent; border: none;
    padding: 4px 8px; font-weight: 600;
}}
QCalendarWidget QToolButton:hover {{ background: {ACCENT_SOFT}; border-radius: 6px; }}
QCalendarWidget QAbstractItemView:enabled {{
    color: {TEXT}; background: white;
    alternate-background-color: #f3ecdd;
    selection-background-color: {ACCENT}; selection-color: white;
}}
QCalendarWidget QAbstractItemView:disabled {{ color: #bcae98; }}
 
QSlider::groove:horizontal {{ height: 4px; background: {BORDER}; border-radius: 2px; }}
QSlider::sub-page:horizontal {{ background: {ACCENT}; border-radius: 2px; }}
QSlider::handle:horizontal {{
    background: white; border: 2px solid {ACCENT};
    width: 14px; height: 14px; margin: -6px 0; border-radius: 8px;
}}
"""
# more styles for checkboxes, radio buttons, scrollbars, spinboxes and comboboxes. the icon paths get filled in by apply_theme
EXTRA_STYLES = f"""
QCheckBox::indicator {{
    width: 16px; height: 16px; border-radius: 4px;
    border: 1px solid #a8997f; background: white;
}}
QCheckBox::indicator:hover {{ border-color: {ACCENT}; }}
QCheckBox::indicator:checked {{
    background: {ACCENT}; border-color: {ACCENT};
    image: url(CHECK_PATH);
}}
QCheckBox::indicator:disabled {{ background: #f2ebdd; border-color: #e4d9c4; }}
 
QRadioButton::indicator {{
    width: 14px; height: 14px; border-radius: 8px;
    border: 1px solid #a8997f; background: white;
}}
QRadioButton::indicator:checked {{
    width: 6px; height: 6px; border: 5px solid {ACCENT}; background: white;
}}
 
QScrollBar:vertical {{ background: transparent; width: 10px; margin: 2px; }}
QScrollBar::handle:vertical {{
    background: #d6c7ab; border-radius: 4px; min-height: 30px;
}}
QScrollBar::handle:vertical:hover {{ background: #a8997f; }}
QScrollBar:horizontal {{ background: transparent; height: 10px; margin: 2px; }}
QScrollBar::handle:horizontal {{
    background: #d6c7ab; border-radius: 4px; min-width: 30px;
}}
QScrollBar::handle:horizontal:hover {{ background: #a8997f; }}
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
    background: {ACCENT_SOFT};
}}
QAbstractSpinBox::up-arrow {{ image: url(UP_PATH); width: 10px; height: 10px; }}
QAbstractSpinBox::down-arrow {{ image: url(DOWN_PATH); width: 10px; height: 10px; }}
 
QComboBox::drop-down {{
    subcontrol-origin: padding; subcontrol-position: center right;
    width: 24px; border: none;
}}
QComboBox::down-arrow {{ image: url(DOWN_PATH); width: 10px; height: 10px; }}
"""
 
# draws the checkmark picture one time, saves it, and returns the path
def make_check_icon():
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
 
# same idea but for the up and down arrows
def make_arrow_icon(name, up):
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
 
# call this once when the app starts. sets the style, colors and stylesheet
def apply_theme(app):
    app.setStyle("Fusion")
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(BACKGROUND))
    palette.setColor(QPalette.ColorRole.Base, QColor("white"))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(TEXT))
    palette.setColor(QPalette.ColorRole.Text, QColor(TEXT))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor("#f3ecdd"))
    app.setPalette(palette)
    # replace the placeholder names with the real icon paths
    styles = (
            EXTRA_STYLES
            .replace("CHECK_PATH", make_check_icon())
            .replace("UP_PATH", make_arrow_icon("arrow_up_warm.png", True))
            .replace("DOWN_PATH", make_arrow_icon("arrow_down_warm.png", False))
        )
    app.setStyleSheet(STYLESHEET + styles)
 
 

# Images
BASE_FOLDER = os.path.dirname(os.path.abspath(__file__))
IMAGE_FOLDER = BASE_FOLDER                              # banners, icons, "images/Econo" etc.
FOODS_FOLDER = os.path.join(BASE_FOLDER, "foods")       # dining pictures
 
 
# a picture with a fixed size. if the file isn't found it shows a dashed placeholder (tries .jpg, .jpeg, .png)
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
            self.setStyleSheet("background: #efe6d4; border: 1px dashed #a8997f;")
        else:
            self.setPixmap(pixmap.scaled(
                width, height,
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation
            ))
 
 
# a wide banner that resizes with the window, up to max_height
class BannerBox(QLabel):
 
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
            self.setStyleSheet("background: #efe6d4; border: 1px dashed #a8997f;")
            self.setFixedHeight(min(self.max_height, 120))
        else:
            self.setFixedHeight(self.max_height)
 
    # resize the banner picture to the new width
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
 
 
# Layout and screen helpers
# puts widgets in a row and moves to the next row when there's no more space
class FlowLayout(QLayout):
 
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
 
    # places the items row by row. if apply is False it only measures the height
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
 
 
# makes the big title label
def make_title(text):
    title = QLabel(text)
    title.setStyleSheet("font-size: 28px; font-weight: bold;")
    return title
 
 
# makes an outlined button (the 'secondary' look in the stylesheet)
def make_secondary_button(text="Back"):
    button = QPushButton(text)
    button.setProperty("secondary", True)    # outlined look from the theme
    return button
 
 
# returns the layout, back button and next button. Back is on the left, Continue on the right
def make_nav_buttons(next_text="Continue", back=True, extra=()):
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
