import math

from PyQt6.QtCore import Qt, QPoint, QRect, QSize, pyqtSignal
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFrame, QScrollArea, QLayout,
    QLabel, QCheckBox, QComboBox, QSlider, QPushButton
)

from BACKEND.RoomTypes import get_all_rooms
from FRONTEND.widgets import ImageBox

SORT_OPTIONS = ["Recommended", "Price: low to high", "Price: high to low"]
PRICE_STEP = 50
MAX_CHIPS = 4


def make_label(text, name=None, word_wrap=False):
    label = QLabel(text)
    if name:
        label.setObjectName(name)
    label.setWordWrap(word_wrap)
    return label


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


class RoomSelectionScreen(QWidget):
    room_selected = pyqtSignal(object)   # emits the chosen Room

    def __init__(self):
        super().__init__()
        self.rooms = get_all_rooms()

        daily = [r.daily_rate for r in self.rooms.values()]
        self.price_min = int(math.floor(min(daily) / PRICE_STEP) * PRICE_STEP)
        self.price_max = int(math.ceil(max(daily) / PRICE_STEP) * PRICE_STEP)

        outer = QHBoxLayout(self)
        outer.setContentsMargins(20, 16, 20, 16)
        outer.setSpacing(18)
        outer.addWidget(self.make_sidebar())
        outer.addLayout(self.make_results(), 1)

        self.reset()

    # ---------- left: filters ----------
    def make_sidebar(self):
        side = QFrame()
        side.setObjectName("sidebar")
        side.setFixedWidth(260)
        layout = QVBoxLayout(side)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(8)

        layout.addWidget(make_label("Your search", "heading"))
        layout.addWidget(make_label("Choose a room that suits your needs.", "muted", True))

        layout.addSpacing(10)
        layout.addWidget(make_label("Popular filters", "sectionTitle"))

        self.amenity_checks = {}
        amenities = []
        for room in self.rooms.values():
            for amenity in room.amenities:
                if amenity not in amenities:
                    amenities.append(amenity)
        # skip amenities every room has - they would not filter anything
        for amenity in amenities:
            if all(amenity in r.amenities for r in self.rooms.values()):
                continue
            check = QCheckBox(amenity)
            check.toggled.connect(self.rebuild)
            self.amenity_checks[amenity] = check
            layout.addWidget(check)

        layout.addSpacing(10)
        layout.addWidget(make_label("Price per day", "sectionTitle"))
        self.price_label = make_label("", "muted")
        layout.addWidget(self.price_label)

        self.price_slider = QSlider(Qt.Orientation.Horizontal)
        self.price_slider.setRange(self.price_min, self.price_max)
        self.price_slider.setSingleStep(PRICE_STEP)
        self.price_slider.setPageStep(PRICE_STEP)
        self.price_slider.valueChanged.connect(self.rebuild)
        layout.addWidget(self.price_slider)

        layout.addStretch()
        return side

    # ---------- right: results ----------
    def make_results(self):
        column = QVBoxLayout()

        top = QHBoxLayout()
        title_box = QVBoxLayout()
        self.count_label = make_label("", "muted")
        title_box.addWidget(self.count_label)
        title_box.addWidget(make_label("Hotel Room Booking", "heading"))
        top.addLayout(title_box)
        top.addStretch()

        top.addWidget(QLabel("Sort by"))
        self.sort_combo = QComboBox()
        self.sort_combo.addItems(SORT_OPTIONS)
        self.sort_combo.currentIndexChanged.connect(self.rebuild)
        top.addWidget(self.sort_combo)
        column.addLayout(top)

        self.cards_layout = QVBoxLayout()
        self.cards_layout.setSpacing(14)
        self.cards_layout.setContentsMargins(0, 8, 6, 8)
        holder = QWidget()
        holder_layout = QVBoxLayout(holder)
        holder_layout.setContentsMargins(0, 0, 0, 0)
        holder_layout.addLayout(self.cards_layout)
        holder_layout.addStretch()

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setWidget(holder)
        column.addWidget(scroll, 1)
        return column

    def make_card(self, room):
        card = QFrame()
        card.setObjectName("card")
        row = QHBoxLayout(card)
        row.setContentsMargins(12, 12, 16, 12)
        row.setSpacing(16)

        row.addWidget(ImageBox(room.image, 230, 150),
                      alignment=Qt.AlignmentFlag.AlignTop)

        # middle: name, description, amenity chips
        middle = QVBoxLayout()
        middle.addWidget(make_label(f"{room.room_type} Room", "heading"))
        middle.addWidget(make_label(room.description, "muted", True))
        middle.addSpacing(6)

        chips = FlowLayout(6)
        for amenity in room.amenities[:MAX_CHIPS]:
            chips.addWidget(make_label(amenity, "chip"))
        extra = len(room.amenities) - MAX_CHIPS
        if extra > 0:
            chips.addWidget(make_label(f"+{extra} more", "chip"))
        middle.addLayout(chips)
        middle.addStretch()
        row.addLayout(middle, 1)

        # right: price and button
        right = QVBoxLayout()
        right.addStretch()
        right.addWidget(make_label(f"₱{room.daily_rate:,.2f}", "price"),
                        alignment=Qt.AlignmentFlag.AlignRight)
        right.addWidget(make_label("per day", "muted"),
                        alignment=Qt.AlignmentFlag.AlignRight)
        right.addWidget(make_label(f"₱{room.hourly_rate:,.2f} per hour", "muted"),
                        alignment=Qt.AlignmentFlag.AlignRight)
        right.addSpacing(6)

        button = QPushButton("Select room")
        button.clicked.connect(
            lambda checked=False, r=room: self.room_selected.emit(r)
        )
        right.addWidget(button, alignment=Qt.AlignmentFlag.AlignRight)
        row.addLayout(right)
        return card

    # ---------- filtering ----------
    def visible_rooms(self):
        wanted = [a for a, check in self.amenity_checks.items() if check.isChecked()]
        limit = self.price_slider.value()

        rooms = [
            r for r in self.rooms.values()
            if r.daily_rate <= limit and all(a in r.amenities for a in wanted)
        ]

        sort = self.sort_combo.currentText()
        if sort == "Price: low to high":
            rooms.sort(key=lambda r: r.daily_rate)
        elif sort == "Price: high to low":
            rooms.sort(key=lambda r: r.daily_rate, reverse=True)
        return rooms

    def rebuild(self, *args):
        self.price_label.setText(f"Up to ₱{self.price_slider.value():,}")

        while self.cards_layout.count():
            item = self.cards_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        rooms = self.visible_rooms()
        self.count_label.setText(f"{len(rooms)} room(s) available")

        if not rooms:
            self.cards_layout.addWidget(
                make_label("No rooms match your filters.", "muted")
            )
        for room in rooms:
            self.cards_layout.addWidget(self.make_card(room))

    def reset(self):
        for widget in (self.sort_combo, self.price_slider,
                       *self.amenity_checks.values()):
            widget.blockSignals(True)

        self.sort_combo.setCurrentIndex(0)
        self.price_slider.setValue(self.price_max)
        for check in self.amenity_checks.values():
            check.setChecked(False)

        for widget in (self.sort_combo, self.price_slider,
                       *self.amenity_checks.values()):
            widget.blockSignals(False)

        self.rebuild()