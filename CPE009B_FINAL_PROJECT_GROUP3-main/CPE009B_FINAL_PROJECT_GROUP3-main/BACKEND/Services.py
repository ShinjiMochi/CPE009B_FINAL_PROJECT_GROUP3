ADDITIONAL_SERVICES = {
    "Extra Bed": 500.00,
    "Extra Pillow & Blanket Set": 150.00,
    "Laundry Service": 350.00,
    "Late Check-out": 600.00,
    "Airport Transfer": 1200.00,
    "Spa Massage": 1500.00,
}

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
