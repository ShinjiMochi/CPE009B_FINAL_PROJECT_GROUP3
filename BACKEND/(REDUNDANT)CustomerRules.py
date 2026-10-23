import re

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
        "special_requests": (special_requests or "").strip()
    }