"""Rules, data and price math for the hotel booking system.
Merged from: CustomerRules, GuestRules, DiscountManager, Services, RoomTypes.
No PyQt in here, so it can be tested on its own."""

import re
from dataclasses import dataclass
from datetime import datetime


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
    image: str          # no extension needed, ImageBox tries .jpg/.jpeg/.png

ROOM_DATA = {
    "Economy": Room(
        room_type="Economy",
        hourly_rate=1100 / 12,
        daily_rate=1500,
        description="A simple and affordable room for short stays.",
        amenities=["Double bed", "Air conditioning", "Private bathroom",
                   "Hot shower", "Wi-Fi", "Smart TV"],
        image="images/Econo",
    ),
    "Deluxe": Room(
        room_type="Deluxe",
        hourly_rate=1650 / 12,
        daily_rate=1950,
        description="A comfortable room with upgraded facilities.",
        amenities=["Queen bed", "Air conditioning", "Private bathroom",
                   "Hot shower", "Wi-Fi", "Smart TV"],
        image="images/Deluxe",
    ),
    "Premium": Room(
        room_type="Premium",
        hourly_rate=1750 / 12,
        daily_rate=2000,
        description="A relaxing room with extra comfort and space.",
        amenities=["Queen bed", "Air conditioning", "Private bathroom",
                   "Hot shower", "Wi-Fi", "Smart TV", "Mini refrigerator"],
        image="images/Premium",
    ),
}

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
DISCOUNT_RATE = 0.10   # 10% promo, room charge only

def calculate_price(room, duration_type, duration):
    """Room charge for the stay. Hourly is capped at the daily rate so a
    long hourly stay never costs more than a full day."""
    if duration <= 0:
        raise ValueError("Duration must be greater than zero.")

    if duration_type == "Hourly":
        total = min(room.hourly_rate * duration, room.daily_rate)
    elif duration_type == "Daily":
        total = room.daily_rate * duration
    else:
        raise ValueError("Invalid duration type.")

    return round(total, 2)


def apply_discount(room_charge, use_discount):
    """Takes the room charge before discount and returns a dictionary."""
    if room_charge < 0:
        raise ValueError("Room charge cannot be negative.")

    rate = DISCOUNT_RATE if use_discount else 0.0
    discount_amount = round(room_charge * rate, 2)

    return {
        "room_charge": round(room_charge, 2),
        "discount_used": bool(use_discount),
        "discount_rate": rate,
        "discount_amount": discount_amount,
        "room_charge_after_discount": round(room_charge - discount_amount, 2),
    }


def calculate_totals(room_charge, use_discount, services=(), dining=()):
    """One call gives every number the screens, booking and receipt need.
    services: [{"name", "price"}]   dining: [{"name", "price", "quantity"}]"""
    discount = apply_discount(room_charge, use_discount)
    services_total = round(sum(s["price"] for s in services), 2)
    dining_total = round(sum(d["price"] * d["quantity"] for d in dining), 2)
    total = round(
        discount["room_charge_after_discount"] + services_total + dining_total, 2
    )
    return {
        "discount": discount,
        "services_total": services_total,
        "dining_total": dining_total,
        "total": total,
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

def validate_guests(total_guests, is_family=False, seniors=0, children=0):
    """Returns a list of error messages. Empty list means valid."""
    errors = []

    if total_guests < MINIMUM_GUESTS:
        errors.append(f"A booking needs at least {MINIMUM_GUESTS} guests.")

    if seniors < 0 or children < 0:
        errors.append("Senior and child counts cannot be negative.")
    elif is_family and seniors + children > total_guests:
        errors.append("Seniors and children cannot be more than the total guests.")

    return errors

def create_guest_info(total_guests, is_family=False, seniors=0, children=0):
    """Returns a GuestInfo, or raises ValueError if the input is invalid."""
    errors = validate_guests(total_guests, is_family, seniors, children)
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
#                           Random Helper
# =====================================================================
def format_when(text, fmt="%b %d, %Y %I:%M %p"):
    """ISO string -> readable date, or "-" if it can't be read."""
    try:
        return datetime.fromisoformat(text).strftime(fmt)
    except (TypeError, ValueError):
        return "-"
