MINIMUM_GUESTS = 2

class GuestInfo:
    def __init__(self, total_guests, is_family=False, seniors=0, children=0):
        self.total_guests = total_guests
        self.is_family = is_family
        self.seniors = seniors
        self.children = children

    def adults(self):
        return self.total_guests - self.seniors - self.children

    def to_dict(self):
        return {
            "total_guests": self.total_guests,
            "is_family": self.is_family,
            "seniors": self.seniors,
            "children": self.children,
            "adults": self.adults()
        }


def is_whole_number(value):
    
    try:
        return int(value) == float(value)
    except (ValueError, TypeError):
        return False


def validate_guests(total_guests, is_family=False, seniors=0, children=0):
    """Returns a list of error messages. Empty list means valid."""
    for value in (total_guests, seniors, children):
        if not is_whole_number(value):
            return ["Guest numbers must be whole numbers."]

    total_guests = int(total_guests)
    seniors = int(seniors)
    children = int(children)
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
        seniors = 0
        children = 0

    return GuestInfo(int(total_guests), is_family, int(seniors), int(children))
