from datetime import datetime, timedelta

from PyQt6.QtCore import pyqtSignal, QDate, QTime, Qt
from PyQt6.QtGui import QColor, QFont, QPainter, QTextCharFormat
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel,
    QRadioButton, QSpinBox, QCalendarWidget, QTimeEdit
)

from logic import calculate_price
from ui_common import make_title, make_nav_buttons, TEXT

# how the dates and times are shown, like Oct 24, 2026 02:00 PM
DISPLAY_FORMAT = "%b %d, %Y %I:%M %p"


class StayCalendar(QCalendarWidget):
    """Calendar that highlights the check-in day, the check-out day and
    every day in between. Painted by hand so the app stylesheet can't hide it."""

    STAY_BLUE = QColor("#1a56db")
    STAY_TINT = QColor(26, 86, 219, 45)

    def __init__(self):
        super().__init__()
        self.stay_start = None
        self.stay_end = None

    # saves the check-in and check-out dates and redraws the calendar
    def set_stay(self, start, end):
        """start and end are QDate values (check-in day, check-out day)."""
        self.stay_start, self.stay_end = start, end
        self.updateCells()

    # draw the normal cell first, then the highlight on top
    def paintCell(self, painter, rect, date):
        super().paintCell(painter, rect, date)

        start, end = self.stay_start, self.stay_end
        if start is None or end is None or not (start <= date <= end):
            return

        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # check-in and check-out are solid blue, the days between are light blue
        if date == start and date == end:
            self._draw_solid(painter, rect, date, "Check-in / out")
        elif date == start:
            self._draw_solid(painter, rect, date, "Check-in")
        elif date == end:
            self._draw_solid(painter, rect, date, "Check-out")
        else:
            painter.fillRect(rect, self.STAY_TINT)

        painter.restore()

    def _draw_solid(self, painter, rect, date, label):
        """Solid blue cell with the day number and a small label under it."""
        painter.fillRect(rect, self.STAY_BLUE)
        painter.setPen(QColor("white"))

        number_font = QFont(painter.font())
        number_font.setBold(True)
        painter.setFont(number_font)
        painter.drawText(
            rect.adjusted(0, 0, 0, -6),
            Qt.AlignmentFlag.AlignCenter,
            str(date.day())
        )

        label_font = QFont(painter.font())
        label_font.setPointSize(7)
        label_font.setBold(False)
        painter.setFont(label_font)
        painter.drawText(
            rect.adjusted(0, 0, 0, -4),
            Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignBottom,
            label
        )


# second step: choose check-in date and time and how long to stay. shows the room charge
class StayDuration(QWidget):
    continued = pyqtSignal(dict)
    back_requested = pyqtSignal()

    def __init__(self):
        super().__init__()
        # set later when main.py gives us the chosen room
        self.room = None

        layout = QVBoxLayout(self)
        layout.addWidget(make_title("Stay Duration"))

        self.room_label = QLabel()
        self.room_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(self.room_label)

        self.description_label = QLabel()
        self.description_label.setWordWrap(True)
        layout.addWidget(self.description_label)

        self.rates_label = QLabel()
        layout.addWidget(self.rates_label)

        # two columns: calendar on the left, time and duration on the right
        columns = QHBoxLayout()

        # ----- left: calendar -----
        calendar_box = QGroupBox("Check-in date")
        calendar_layout = QVBoxLayout(calendar_box)
        self.calendar = StayCalendar()
        self.calendar.setGridVisible(True)
        # can't pick a date that already passed
        self.calendar.setMinimumDate(QDate.currentDate())

        # sets the header and weekend text color so the app stylesheet doesn't make it hard to read
        day_format = QTextCharFormat()
        day_format.setForeground(QColor(TEXT))
        self.calendar.setHeaderTextFormat(day_format)
        self.calendar.setWeekdayTextFormat(Qt.DayOfWeek.Saturday, day_format)
        self.calendar.setWeekdayTextFormat(Qt.DayOfWeek.Sunday, day_format)

        # shade the past dates again when the month changes
        self.calendar.currentPageChanged.connect(self.mark_past_dates)

        self.calendar.setVerticalHeaderFormat(
            QCalendarWidget.VerticalHeaderFormat.NoVerticalHeader
        )

        calendar_layout.addWidget(self.calendar)
        columns.addWidget(calendar_box, 3)

        # ----- right: time and duration -----
        details_box = QGroupBox("Check-in time and length of stay")
        details = QVBoxLayout(details_box)

        time_row = QHBoxLayout()
        time_row.addWidget(QLabel("Check-in time:"))
        self.time_edit = QTimeEdit()
        self.time_edit.setDisplayFormat("hh:mm AP")
        time_row.addWidget(self.time_edit)
        time_row.addStretch()
        details.addLayout(time_row)

        details.addWidget(QLabel("Stay type:"))
        self.hourly_radio = QRadioButton("Per Hour")
        self.daily_radio = QRadioButton("Per Day")
        self.daily_radio.setChecked(True)
        details.addWidget(self.hourly_radio)
        details.addWidget(self.daily_radio)

        duration_row = QHBoxLayout()
        self.duration_label = QLabel("Number of days:")
        self.duration_spin = QSpinBox()
        self.duration_spin.setRange(1, 365)
        duration_row.addWidget(self.duration_label)
        duration_row.addWidget(self.duration_spin)
        duration_row.addStretch()
        details.addLayout(duration_row)

        self.checkin_label = QLabel()
        self.checkout_label = QLabel()
        details.addWidget(self.checkin_label)
        details.addWidget(self.checkout_label)

        self.warning_label = QLabel()
        self.warning_label.setStyleSheet("color: red; font-weight: bold;")
        self.warning_label.setWordWrap(True)
        details.addWidget(self.warning_label)

        self.total_label = QLabel()
        self.total_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        details.addWidget(self.total_label)
        details.addStretch()

        columns.addWidget(details_box, 2)
        layout.addLayout(columns)

        buttons, back, self.continue_button = make_nav_buttons()
        layout.addLayout(buttons)

        back.clicked.connect(self.back_requested.emit)
        self.continue_button.clicked.connect(self.on_continue)
        # anything that changes recalculates the check-out, price and warning
        self.hourly_radio.toggled.connect(self.update_total)
        self.duration_spin.valueChanged.connect(self.update_total)
        self.calendar.selectionChanged.connect(self.update_total)
        self.time_edit.timeChanged.connect(self.update_total)

        self.set_default_checkin()
        self.mark_past_dates()
        self.update_total()

    # returns 'Hourly' or 'Daily' based on the radio button
    def duration_type(self):
        return "Hourly" if self.hourly_radio.isChecked() else "Daily"

    def set_default_checkin(self):
        """Defaults to the start of the next full hour."""
        start = (datetime.now() + timedelta(hours=1)).replace(
            minute=0, second=0, microsecond=0
        )
        self.calendar.setSelectedDate(QDate(start.year, start.month, start.day))
        self.time_edit.setTime(QTime(start.hour, 0))

    # combines the picked date and time into one datetime
    def get_check_in(self):
        date = self.calendar.selectedDate()
        time = self.time_edit.time()
        return datetime(
            date.year(), date.month(), date.day(), time.hour(), time.minute()
        )

    # check-in plus the number of hours or days
    def get_check_out(self, check_in):
        if self.duration_type() == "Hourly":
            return check_in + timedelta(hours=self.duration_spin.value())
        return check_in + timedelta(days=self.duration_spin.value())

    # main.py calls this when a room is picked
    def set_room(self, room):
        self.room = room
        self.room_label.setText(f"Selected Room: {room.room_type}")
        self.description_label.setText(room.description)
        self.rates_label.setText(
            f"Hourly rate: ₱{room.hourly_rate:,.2f}    "
            f"Daily rate: ₱{room.daily_rate:,.2f}"
        )
        self.update_total()

    # check-in can't be earlier than right now
    def check_in_is_valid(self, check_in):
        return check_in >= datetime.now().replace(second=0, microsecond=0)

    # updates the labels, calendar, warning and price. Continue only works if the check-in is valid
    def update_total(self, *args):
        hourly = self.duration_type() == "Hourly"
        self.duration_label.setText(
            "Number of hours:" if hourly else "Number of days:"
        )
        # hourly is up to 23 hours only, for longer use per day
        self.duration_spin.setRange(1, 23 if hourly else 365)

        check_in = self.get_check_in()
        check_out = self.get_check_out(check_in)
        self.checkin_label.setText(f"Check-in:  {check_in.strftime(DISPLAY_FORMAT)}")
        self.checkout_label.setText(f"Check-out: {check_out.strftime(DISPLAY_FORMAT)}")

        # highlight check-in, check-out and the days between on the calendar
        self.calendar.set_stay(
            QDate(check_in.year, check_in.month, check_in.day),
            QDate(check_out.year, check_out.month, check_out.day)
        )

        valid = self.check_in_is_valid(check_in)
        self.warning_label.setText("" if valid else "Check-in can't be in the past.")

        if self.room is None:
            self.total_label.setText("Room charge: ₱0.00")
            self.continue_button.setEnabled(False)
            return

        total = calculate_price(
            self.room, self.duration_type(), self.duration_spin.value()
        )
        self.total_label.setText(f"Room charge: ₱{total:,.2f}")
        self.continue_button.setEnabled(valid)

    # checks again, then sends the stay info to main.py (dates are saved as text)
    def on_continue(self):
        if self.room is None:
            return

        check_in = self.get_check_in()
        if not self.check_in_is_valid(check_in):
            self.update_total()
            return

        room_charge = calculate_price(
            self.room, self.duration_type(), self.duration_spin.value()
        )
        self.continued.emit({
            "duration_type": self.duration_type(),
            "duration": self.duration_spin.value(),
            "room_charge": room_charge,
            "check_in": check_in.isoformat(timespec="minutes"),
            "check_out": self.get_check_out(check_in).isoformat(timespec="minutes")
        })

    def mark_past_dates(self, *args):
        """Shades every date before today so it looks unselectable."""
        past = QTextCharFormat()
        past.setForeground(QColor("#9aa3b2"))
        past.setBackground(QColor("#eceef2"))

        first = QDate(
            self.calendar.yearShown(), self.calendar.monthShown(), 1
        ).addDays(-7)             
        today = QDate.currentDate()
        # a calendar page can show about 6 weeks so we check 50 days
        for offset in range(50):
            day = first.addDays(offset)
            if day < today:
                self.calendar.setDateTextFormat(day, past)

    # puts the stay settings back to default
    def reset(self):
        self.daily_radio.setChecked(True)
        self.duration_spin.setValue(1)
        self.set_default_checkin()
        self.update_total()
