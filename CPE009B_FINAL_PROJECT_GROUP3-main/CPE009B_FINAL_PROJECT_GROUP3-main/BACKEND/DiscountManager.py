#draft pa lang to
#10% promo discount
DISCOUNT_RATE = 0.10


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
        "room_charge_after_discount": round(room_charge - discount_amount, 2)
    }


def calculate_final_total(discount_result, dining_total=0.0, services_total=0.0):
    return round(
        discount_result["room_charge_after_discount"]
        + dining_total
        + services_total,
        2
    )