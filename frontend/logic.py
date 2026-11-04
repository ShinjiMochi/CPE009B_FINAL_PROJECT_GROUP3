"""Rules, data and price math for the hotel booking system.
Merged from: CustomerRules, GuestRules, DiscountManager, Services, RoomTypes.
No PyQt in here, so it can be tested on its own."""

import re
from dataclasses import dataclass
from datetime import date, datetime


# =====================================================================
# Rooms
# =====================================================================
@dataclass
class Room:
    room_type: str
    hourly_rate: float
    daily_rate: float
    description: str
    amenities: list
    image: str
    max_guests: int = 2     # most guests one of this room can hold

ROOM_DATA = {
    "Economy": Room(
        room_type="Economy",
        hourly_rate=1100 / 12,
        daily_rate=1500,
        description="A simple and affordable room for short stays.",
        amenities=["Double bed", "Air conditioning", "Private bathroom",
                   "Hot shower", "Wi-Fi", "Smart TV"],
        image="images/Econo",
        max_guests=3,
    ),
    "Deluxe": Room(
        room_type="Deluxe",
        hourly_rate=1650 / 12,
        daily_rate=1950,
        description="A comfortable room with upgraded facilities.",
        amenities=["Queen bed", "Air conditioning", "Private bathroom",
                   "Hot shower", "Wi-Fi", "Smart TV"],
        image="images/Deluxe",
        max_guests=4,
    ),
    "Premium": Room(
        room_type="Premium",
        hourly_rate=1750 / 12,
        daily_rate=2000,
        description="A relaxing room with extra comfort and space.",
        amenities=["Queen bed", "Air conditioning", "Private bathroom",
                   "Hot shower", "Wi-Fi", "Smart TV", "Mini refrigerator"],
        image="images/Premium",
        max_guests=5,
    ),
    "Family Suite": Room(
        room_type="Family Suite",
        hourly_rate=2400 / 12,
        daily_rate=3200,
        description="A spacious suite with a sofa bed, made for families.",
        amenities=["Queen bed", "Sofa bed", "Air conditioning", "Private bathroom",
                   "Hot shower", "Wi-Fi", "Smart TV", "Mini refrigerator"],
        image="images/FamilySuite",
        max_guests=6,
    ),
    "Executive Suite": Room(
        room_type="Executive Suite",
        hourly_rate=2800 / 12,
        daily_rate=3800,
        description="A suite with a king bed, work desk and bathtub.",
        amenities=["King bed", "Air conditioning", "Private bathroom", "Bathtub",
                   "Hot shower", "Wi-Fi", "Smart TV", "Mini refrigerator", "Work desk"],
        image="images/Executive",
        max_guests=5,
    ),
    "Presidential Suite": Room(
        room_type="Presidential Suite",
        hourly_rate=4800 / 12,
        daily_rate=6500,
        description="Our top suite with a living area and private balcony.",
        amenities=["King bed", "Sofa bed", "Air conditioning", "Private bathroom",
                   "Bathtub", "Hot shower", "Wi-Fi", "Smart TV", "Mini refrigerator",
                   "Work desk", "Balcony"],
        image="images/Presidential",
        max_guests=10,
    ),
}

MAX_ROOMS_PER_BOOKING = 5

def get_room(room_type):
    return ROOM_DATA.get(room_type)


def get_all_rooms():
    return ROOM_DATA

# =====================================================================
#               Services and dining menu (prices in PHP)
# =====================================================================

ADDITIONAL_SERVICES = {
    "Extra Bed": 500.00,
    "Extra Pillow & Blanket Set": 150.00,
    "Laundry Service": 350.00,
    "Late Check-out": 600.00,
    "Airport Transfer": 1200.00,
    "Spa Massage": 1500.00,
}

# What each service includes. Shown on the payment breakdown and receipt.
SERVICE_SPECS = {
    "Extra Bed": "1 rollaway bed set up in the room, per stay.",
    "Extra Pillow & Blanket Set": "1 set: 2 pillows and 1 blanket, per stay.",
    "Laundry Service": "Up to 5 kg of laundry, returned within 24 hours.",
    "Late Check-out": "Check-out extended by up to 3 hours.",
    "Airport Transfer": "One-way trip, 1 vehicle for up to 4 passengers.",
    "Spa Massage": "60-minute full-body massage for 1 guest.",
}


def get_service_spec(name):
    return SERVICE_SPECS.get(name, "")


# The image is looked up in the "foods" folder.
DINING_MENU = {
    "Cheese Burger": {"price": 300.00, "image": "burger.jpg"},
    "Fruit Platter": {"price": 500.00, "image": "fruits.jpg"},
    "Carbonara": {"price": 450.00, "image": "pasta.jpg"},
    "All-Meat Pizza": {"price": 1100.00, "image": "pizza.jpg"},
    "Caesar Salad": {"price": 600.00, "image": "salad.jpg"},
    "Egg Drop Soup": {"price": 550.00, "image": "soup.jpg"},
}


def get_additional_services():
    """Returns {service name: price}."""
    return dict(ADDITIONAL_SERVICES)


def get_dining_menu():
    """Returns {item name: {"price": ..., "image": ...}}."""
    return {name: dict(item) for name, item in DINING_MENU.items()}


# =====================================================================
#           Pricing (the only place prices are calculated)
# =====================================================================
def calculate_price(room, duration_type, duration):
    """Room charge for ONE room for the stay. Hourly is capped at the daily
    rate so a long hourly stay never costs more than a full day."""
    if duration <= 0:
        raise ValueError("Duration must be greater than zero.")

    if duration_type == "Hourly":
        total = min(room.hourly_rate * duration, room.daily_rate)
    elif duration_type == "Daily":
        total = room.daily_rate * duration
    else:
        raise ValueError("Invalid duration type.")

    return round(total, 2)


def price_rooms(rooms, duration_type, duration):
    """rooms: [{"room": Room, "quantity": n}].
    Returns (lines, total) where each line is
    {"room_type", "quantity", "unit_charge", "amount"}."""
    lines = []
    for entry in rooms:
        unit = calculate_price(entry["room"], duration_type, duration)
        lines.append({
            "room_type": entry["room"].room_type,
            "quantity": entry["quantity"],
            "unit_charge": unit,
            "amount": round(unit * entry["quantity"], 2),
        })
    return lines, round(sum(l["amount"] for l in lines), 2)


def total_capacity(rooms):
    """Most guests the selected rooms can hold together."""
    return sum(e["room"].max_guests * e["quantity"] for e in rooms)


def total_room_count(rooms):
    return sum(e["quantity"] for e in rooms)


def rooms_summary(rooms):
    """'2 x Deluxe, 1 x Economy'"""
    return ", ".join(f"{e['quantity']} x {e['room'].room_type}" for e in rooms)


# =====================================================================
#                 Discounts (details + ID / voucher checks)
# =====================================================================
# Only ONE discount per booking. It applies to the room charge only.
DISCOUNT_TYPES = {
    "Senior Citizen": {
        "rate": 0.20, "kind": "id",
        "id_label": "Senior Citizen ID number",
        "description": "20% off the room charge. Needs a valid Senior Citizen "
                       "(OSCA) ID. Present the ID at check-in.",
    },
    "PWD": {
        "rate": 0.20, "kind": "id",
        "id_label": "PWD ID number",
        "description": "20% off the room charge. Needs a valid PWD ID. "
                       "Present the ID at check-in.",
    },
    "Student": {
        "rate": 0.10, "kind": "id",
        "id_label": "School ID number",
        "description": "10% off the room charge. Needs a valid school ID for "
                       "the current school year. Present it at check-in.",
    },
    "Promo Voucher": {
        "rate": None, "kind": "voucher",
        "id_label": "Voucher code",
        "description": "Enter a valid voucher code. The rate, expiry date and "
                       "any minimum spend depend on the voucher.",
    },
}

# demo voucher list: code -> rate, last valid day, minimum room charge
VOUCHERS = {
    "AUREVELLE10": {"rate": 0.10, "expires": "2026-12-31", "min_room_charge": 0},
    "WELCOME15": {"rate": 0.15, "expires": "2027-06-30", "min_room_charge": 2000},
    "HOLIDAY20": {"rate": 0.20, "expires": "2026-12-25", "min_room_charge": 3000},
}

ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9\-]{4,19}$")


def mask_code(code):
    return "*" * max(0, len(code) - 4) + code[-4:]


def verify_discount(discount_type, code, holder_name="", room_charge=0.0, today=None):
    """Checks the ID or voucher. Returns the discount info dict used by
    apply_discount(), or raises ValueError with a message for the screen.
    (Demo check: format and voucher rules only, there is no ID database.)"""
    info = DISCOUNT_TYPES.get(discount_type)
    if info is None:
        raise ValueError("Choose a discount type.")

    code = (code or "").strip().upper()
    today = today or date.today()

    if info["kind"] == "id":
        holder = (holder_name or "").strip()
        if not is_valid_name(holder):
            raise ValueError("Enter the ID holder's full name as printed on the ID.")
        if not ID_PATTERN.match(code):
            raise ValueError(
                f"{info['id_label']} must be 5 to 20 letters, numbers or dashes."
            )
        return {
            "type": discount_type,
            "rate": info["rate"],
            "holder": holder,
            "reference": mask_code(code),      # only the last 4 characters are kept
            "verified": True,
        }

    voucher = VOUCHERS.get(code)
    if voucher is None:
        raise ValueError("Voucher code not recognised.")
    expiry = date.fromisoformat(voucher["expires"])
    if today > expiry:
        raise ValueError(f"This voucher expired on {expiry:%b %d, %Y}.")
    if room_charge < voucher["min_room_charge"]:
        raise ValueError(
            f"This voucher needs a room charge of at least "
            f"₱{voucher['min_room_charge']:,.2f}."
        )
    return {
        "type": discount_type,
        "rate": voucher["rate"],
        "holder": "",
        "reference": code,
        "verified": True,
    }


def apply_discount(room_charge, discount=None):
    """room_charge is before discount. discount is the dict from
    verify_discount() or None. Returns a dictionary."""
    if room_charge < 0:
        raise ValueError("Room charge cannot be negative.")

    rate = discount["rate"] if discount else 0.0
    discount_amount = round(room_charge * rate, 2)

    return {
        "room_charge": round(room_charge, 2),
        "discount_used": bool(discount),
        "discount_type": discount["type"] if discount else None,
        "discount_reference": discount.get("reference") if discount else None,
        "discount_holder": discount.get("holder") if discount else None,
        "discount_rate": rate,
        "discount_amount": discount_amount,
        "room_charge_after_discount": round(room_charge - discount_amount, 2),
    }


def calculate_totals(room_charge, discount=None, services=(), dining=()):
    """One call gives every number the screens, booking and receipt need.
    services: [{"name", "price"}]   dining: [{"name", "price", "quantity"}]"""
    discount_result = apply_discount(room_charge, discount)
    services_total = round(sum(s["price"] for s in services), 2)
    dining_total = round(sum(d["price"] * d["quantity"] for d in dining), 2)
    total = round(
        discount_result["room_charge_after_discount"] + services_total + dining_total, 2
    )
    return {
        "discount": discount_result,
        "services_total": services_total,
        "dining_total": dining_total,
        "total": total,
    }


# =====================================================================
#                   Cancellation fee (percent of the total)
# =====================================================================
# (hours before check-in, fee rate, text for the screen). First match wins.
CANCELLATION_POLICY = [
    (168, 0.10, "7 days or more before check-in"),
    (72, 0.25, "3 to 7 days before check-in"),
    (24, 0.50, "1 to 3 days before check-in"),
    (0, 1.00, "Less than 24 hours before check-in"),
]


def cancellation_policy_lines():
    return [f"{text}: {rate * 100:.0f}% of the total"
            for _, rate, text in CANCELLATION_POLICY]


def cancellation_fee(check_in, amount, now=None):
    """Fee and refund if the booking is cancelled now. Raises ValueError if
    the stay has already started."""
    try:
        start = datetime.fromisoformat(str(check_in))
    except ValueError:
        raise ValueError("This booking has no valid check-in date.")

    now = now or datetime.now()
    hours = (start - now).total_seconds() / 3600
    if hours <= 0:
        raise ValueError(
            "The stay has already started, so this booking can no longer be cancelled."
        )

    for threshold, rate, _ in CANCELLATION_POLICY:
        if hours >= threshold:
            fee = round(amount * rate, 2)
            return {
                "fee_rate": rate,
                "fee": fee,
                "refund": round(amount - fee, 2),
                "hours_before": round(hours, 1),
            }


# =====================================================================
#                              Guest Logic
# =====================================================================
MINIMUM_GUESTS = 2

@dataclass
class GuestInfo:
    total_guests: int
    is_family: bool = False
    seniors: int = 0
    children: int = 0

    def adults(self):
        return self.total_guests - self.seniors - self.children

    def to_dict(self):
        return {
            "total_guests": self.total_guests,
            "is_family": self.is_family,
            "seniors": self.seniors,
            "children": self.children,
            "adults": self.adults(),
        }

def validate_guests(total_guests, is_family=False, seniors=0, children=0,
                    max_guests=None):
    """Returns a list of error messages. Empty list means valid.
    max_guests is the capacity of the selected rooms."""
    errors = []

    if total_guests < MINIMUM_GUESTS:
        errors.append(f"A booking needs at least {MINIMUM_GUESTS} guests.")

    if max_guests is not None and total_guests > max_guests:
        errors.append(f"The selected rooms fit up to {max_guests} guests.")

    if seniors < 0 or children < 0:
        errors.append("Senior and child counts cannot be negative.")
    elif is_family and seniors + children > total_guests:
        errors.append("Seniors and children cannot be more than the total guests.")

    return errors

def create_guest_info(total_guests, is_family=False, seniors=0, children=0,
                      max_guests=None):
    """Returns a GuestInfo, or raises ValueError if the input is invalid."""
    errors = validate_guests(total_guests, is_family, seniors, children, max_guests)
    if errors:
        raise ValueError("\n".join(errors))

    if not is_family:
        seniors = children = 0

    return GuestInfo(int(total_guests), is_family, int(seniors), int(children))


# =====================================================================
#                      Customer Information Rules
# =====================================================================
MAX_SPECIAL_REQUESTS = 500

EMAIL_PATTERN = re.compile(
    r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}$"
)
# Philippine mobile: 09XXXXXXXXX or +639XXXXXXXXX
CONTACT_PATTERN = re.compile(r"^(09\d{9}|\+639\d{9})$")


def clean_contact(contact):
    return re.sub(r"[\s\-()]", "", str(contact or ""))


def normalize_contact(contact):
    """Returns the number as 09XXXXXXXXX."""
    cleaned = clean_contact(contact)
    if cleaned.startswith("+63"):
        cleaned = "0" + cleaned[3:]
    return cleaned


def is_valid_name(name):
    letters = [c for c in name if c.isalpha()]
    return len(letters) >= 2 and all(c.isalpha() or c in " .'-" for c in name)


def validate_customer(full_name, contact_number, email, address, special_requests=""):
    """Returns {field: error message}. An empty dict means valid."""
    errors = {}

    full_name = (full_name or "").strip()
    if not full_name:
        errors["full_name"] = "Full name is required."
    elif not is_valid_name(full_name):
        errors["full_name"] = "Use letters, spaces, . ' and - only."

    contact = clean_contact(contact_number)
    if not contact:
        errors["contact_number"] = "Contact number is required."
    elif not CONTACT_PATTERN.match(contact):
        errors["contact_number"] = "Enter an 11-digit mobile number (09XXXXXXXXX)."

    email = (email or "").strip()
    if not email:
        errors["email"] = "Email is required."
    elif not EMAIL_PATTERN.match(email):
        errors["email"] = "Enter a valid email (example: name@mail.com)."

    if not (address or "").strip():
        errors["address"] = "Address is required."

    if len(special_requests or "") > MAX_SPECIAL_REQUESTS:
        errors["special_requests"] = f"Keep it under {MAX_SPECIAL_REQUESTS} characters."

    return errors


def create_customer_info(full_name, contact_number, email, address, special_requests=""):
    """Returns a cleaned customer dict, or raises ValueError if invalid."""
    errors = validate_customer(full_name, contact_number, email, address, special_requests)
    if errors:
        raise ValueError("\n".join(errors.values()))

    return {
        "full_name": full_name.strip(),
        "contact_number": normalize_contact(contact_number),
        "email": email.strip(),
        "address": address.strip(),
        "special_requests": (special_requests or "").strip(),
    }

# =====================================================================
#              Additional guests (names and contact numbers)
# =====================================================================
def validate_guest_list(guests):
    """guests: [{"name", "contact"}] for every guest AFTER the primary one.
    Name is required. Contact is optional but must be a valid mobile number
    if it is filled in. Returns {row index: {field: message}}."""
    errors = {}
    for index, guest in enumerate(guests):
        row = {}
        name = (guest.get("name") or "").strip()
        contact = clean_contact(guest.get("contact"))

        if not name:
            row["name"] = "Name is required."
        elif not is_valid_name(name):
            row["name"] = "Use letters, spaces, . ' and - only."

        if contact and not CONTACT_PATTERN.match(contact):
            row["contact"] = "Enter an 11-digit mobile number (09XXXXXXXXX)."

        if row:
            errors[index] = row
    return errors


def create_guest_list(guests):
    """Cleaned [{"name", "contact"}], or raises ValueError if invalid."""
    if validate_guest_list(guests):
        raise ValueError("Some guest names or contact numbers are not valid.")
    return [
        {"name": g["name"].strip(),
         "contact": normalize_contact(g.get("contact")) or ""}
        for g in guests
    ]


# =====================================================================
#                           Random Helper
# =====================================================================
def format_when(text, fmt="%b %d, %Y %I:%M %p"):
    """ISO string -> readable date, or "-" if it can't be read."""
    try:
        return datetime.fromisoformat(text).strftime(fmt)
    except (TypeError, ValueError):
        return "-"
