import random
import re
from datetime import datetime

CURRENCY = "PHP"

# method -> providers (empty list = no provider needed)
PAYMENT_METHODS = {
    "Cash": [],
    "E-Wallet / E-Banking": ["GCash", "Maya", "GrabPay", "Online Bank Transfer"],
    "Card": ["Credit Card", "Debit Card"]
}


def get_payment_methods():
    return {method: list(providers) for method, providers in PAYMENT_METHODS.items()}


def generate_reference():
    stamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"PAY-{stamp}-{random.randint(100, 999)}"


def process_payment(method, amount, provider=None, details=None):
    """
    method:   "Cash", "E-Wallet / E-Banking" or "Card"
    amount:   amount due in PHP
    provider: required for e-wallet and card (see PAYMENT_METHODS)
    details:  optional dict
              Cash:  {"amount_tendered": 2000}
              Card:  {"card_number": "4111 1111 1111 1111", "card_holder": "Juan Dela Cruz"}
    Always returns an "Approved" payment record, or raises ValueError for bad input.
    Only the last 4 digits of a card number are kept.
    """
    details = details or {}

    if method not in PAYMENT_METHODS:
        raise ValueError("Please choose a valid payment method.")

    if amount is None or amount <= 0:
        raise ValueError("Amount to pay must be greater than zero.")

    providers = PAYMENT_METHODS[method]
    if providers and provider not in providers:
        raise ValueError(f"Please choose a valid option for {method}.")

    payment = {
        "method": method,
        "provider": provider if providers else None,
        "amount": round(amount, 2),
        "currency": CURRENCY,
        "status": "Approved",
        "reference": generate_reference(),
        "paid_at": datetime.now().isoformat(timespec="seconds")
    }

    if method == "Cash":
        tendered = details.get("amount_tendered")
        if tendered is None:
            tendered = amount
        try:
            tendered = float(tendered)
        except (TypeError, ValueError):
            raise ValueError("Amount tendered must be a number.")
        if tendered < amount:
            raise ValueError("Amount tendered is less than the amount due.")

        payment["amount_tendered"] = round(tendered, 2)
        payment["change"] = round(tendered - amount, 2)

    elif method == "Card":
        number = re.sub(r"[\s\-]", "", str(details.get("card_number", "")))
        if not number.isdigit() or not 13 <= len(number) <= 19:
            raise ValueError("Card number must be 13 to 19 digits.")
        holder = str(details.get("card_holder", "")).strip()
        if not holder:
            raise ValueError("Card holder name is required.")

        payment["card_last4"] = number[-4:]
        payment["card_holder"] = holder

    return payment