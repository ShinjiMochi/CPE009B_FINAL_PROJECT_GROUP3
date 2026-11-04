import os

from PyQt6.QtCore import Qt, pyqtSignal, QRegularExpression
from PyQt6.QtGui import QColor, QPainter, QPixmap, QRegularExpressionValidator
from PyQt6.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QFormLayout,
    QLabel, QComboBox, QLineEdit, QDoubleSpinBox, QPushButton
)

from managers import get_cash_locations, get_payment_accounts, get_payment_methods
from ui_common import BASE_FOLDER, make_secondary_button, make_title

QR_FOLDER = os.path.join(BASE_FOLDER, "images")
QR_SIZE = 190


def make_wrapped_label(text="", muted=False):
    label = QLabel(text)
    label.setWordWrap(True)
    if muted:
        label.setObjectName("muted")
    return label


def make_qr_label(payload, image_name, size=QR_SIZE):
    """The hotel's own QR image (qr/<image_name>.png|jpg) if it exists,
    otherwise a QR code drawn from `payload` (needs: pip install qrcode),
    otherwise a gray placeholder box."""
    label = QLabel()
    label.setFixedSize(size, size)
    label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    label.setStyleSheet("background: white; border: 1px solid #dccfb7;")

    for extension in (".png", ".jpg", ".jpeg"):
        path = os.path.join(QR_FOLDER, image_name + extension)
        if os.path.exists(path):
            pixmap = QPixmap(path)
            if not pixmap.isNull():
                label.setPixmap(pixmap.scaled(
                    size - 8, size - 8,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                ))
                return label

    try:
        import qrcode
        qr = qrcode.QRCode(border=1)
        qr.add_data(payload)
        qr.make(fit=True)
        matrix = qr.get_matrix()
    except Exception:
        label.setWordWrap(True)
        label.setText(
            f"[ QR code ]\nAdd qr/{image_name}.png\nor run: pip install qrcode"
        )
        return label

    count = len(matrix)
    cell = max(1, (size - 8) // count)
    pixmap = QPixmap(cell * count, cell * count)
    pixmap.fill(QColor("white"))
    painter = QPainter(pixmap)
    for y, row in enumerate(matrix):
        for x, dark in enumerate(row):
            if dark:
                painter.fillRect(x * cell, y * cell, cell, cell, QColor("black"))
    painter.end()
    label.setPixmap(pixmap)
    return label


class PaymentDialog(QDialog):
    """Separate payment window, opened after the guest confirms the booking.
    main.py connects pay_requested, tries to book, and calls accept() on success
    (or shows an error and leaves the window open)."""
    pay_requested = pyqtSignal(dict)    # {"method", "provider", "details"}

    def __init__(self, total, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Payment")
        self.setModal(True)
        self.setMinimumWidth(560)

        self.total = total
        self.methods = get_payment_methods()
        self.accounts = get_payment_accounts()
        self.locations = get_cash_locations()

        layout = QVBoxLayout(self)
        layout.addWidget(make_title("Payment"))

        amount = QLabel(f"Amount due: ₱{total:,.2f}")
        amount.setObjectName("price")
        layout.addWidget(amount)
        layout.addWidget(make_wrapped_label(
            "Demo: every payment is approved once the required details are filled in.",
            muted=True
        ))

        # ----- method + provider -----
        top = QFormLayout()
        self.method_combo = QComboBox()
        self.method_combo.addItems(self.methods.keys())
        top.addRow("Method:", self.method_combo)

        self.provider_combo = QComboBox()
        self.provider_label = QLabel("Option:")
        top.addRow(self.provider_label, self.provider_combo)
        layout.addLayout(top)

        # ----- e-wallet / bank: receiver account + QR -----
        self.epay_box = QGroupBox("Send your payment to this account")
        epay_layout = QVBoxLayout(self.epay_box)

        epay_top = QHBoxLayout()
        self.qr_holder = QVBoxLayout()
        epay_top.addLayout(self.qr_holder)

        info = QVBoxLayout()
        self.receiver_label = QLabel()
        self.receiver_label.setTextFormat(Qt.TextFormat.RichText)
        self.receiver_label.setWordWrap(True)
        info.addWidget(self.receiver_label)
        info.addWidget(make_wrapped_label(
            "Scan the QR code with your app, or send the exact amount to the "
            "account shown. Then type the transaction / reference number you "
            "received.",
            muted=True
        ))
        info.addStretch()
        epay_top.addLayout(info, 1)
        epay_layout.addLayout(epay_top)

        ref_form = QFormLayout()
        self.reference_input = QLineEdit()
        self.reference_input.setPlaceholderText("Transaction / reference number")
        self.reference_input.setMaxLength(30)
        ref_form.addRow("Reference no.:", self.reference_input)
        epay_layout.addLayout(ref_form)
        layout.addWidget(self.epay_box)

        # ----- cash: where to pay -----
        self.cash_box = QGroupBox("Pay in cash at")
        cash_layout = QVBoxLayout(self.cash_box)
        cash_form = QFormLayout()
        self.location_combo = QComboBox()
        self.location_combo.addItems(self.locations.keys())
        cash_form.addRow("Location:", self.location_combo)
        self.tendered_spin = QDoubleSpinBox()
        self.tendered_spin.setDecimals(2)
        self.tendered_spin.setRange(0, 100000000)
        self.tendered_spin.setPrefix("₱ ")
        self.tendered_spin.setValue(total)
        cash_form.addRow("Amount tendered:", self.tendered_spin)
        cash_layout.addLayout(cash_form)
        self.location_address = make_wrapped_label(muted=True)
        cash_layout.addWidget(self.location_address)
        layout.addWidget(self.cash_box)

        # ----- card -----
        self.card_box = QGroupBox("Card details")
        card_form = QFormLayout(self.card_box)
        self.card_number_input = QLineEdit()
        self.card_number_input.setPlaceholderText("Digits only (up to 16)")
        self.card_number_input.setMaxLength(16)
        self.card_number_input.setValidator(
            QRegularExpressionValidator(QRegularExpression("[0-9]*"))
        )
        self.card_holder_input = QLineEdit()
        self.card_holder_input.setPlaceholderText("Letters and spaces only")
        self.card_holder_input.setMaxLength(40)
        self.card_holder_input.setValidator(
            QRegularExpressionValidator(QRegularExpression(r"[\p{L} ]*"))
        )
        card_form.addRow("Card number:", self.card_number_input)
        card_form.addRow("Card holder:", self.card_holder_input)
        layout.addWidget(self.card_box)

        # ----- buttons -----
        buttons = QHBoxLayout()
        cancel = make_secondary_button("Cancel")
        self.pay_button = QPushButton(f"Pay ₱{total:,.2f}")
        buttons.addWidget(cancel)
        buttons.addStretch()
        buttons.addWidget(self.pay_button)
        layout.addLayout(buttons)

        cancel.clicked.connect(self.reject)
        self.pay_button.clicked.connect(self.on_pay)
        self.method_combo.currentTextChanged.connect(self.update_method_fields)
        self.provider_combo.currentTextChanged.connect(self.update_epay)
        self.location_combo.currentTextChanged.connect(self.update_location)
        self.update_method_fields()

    # ---------- showing the right fields ----------
    def update_method_fields(self, *args):
        method = self.method_combo.currentText()
        providers = self.methods.get(method, [])

        self.provider_combo.blockSignals(True)
        self.provider_combo.clear()
        self.provider_combo.addItems(providers)
        self.provider_combo.blockSignals(False)

        self.provider_combo.setVisible(bool(providers))
        self.provider_label.setVisible(bool(providers))
        self.epay_box.setVisible(method == "E-Wallet / E-Banking")
        self.cash_box.setVisible(method == "Cash")
        self.card_box.setVisible(method == "Card")

        self.update_epay()
        self.update_location()
        self.adjustSize()

    def update_epay(self, *args):
        provider = self.provider_combo.currentText()
        account = self.accounts.get(provider)
        if self.method_combo.currentText() != "E-Wallet / E-Banking" or account is None:
            return

        # swap in the QR for this provider
        while self.qr_holder.count():
            item = self.qr_holder.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        payload = (
            f"{provider}|{account['account_name']}|{account['account_number']}"
            f"|PHP {self.total:.2f}"
        )
        self.qr_holder.addWidget(make_qr_label(payload, account["qr_image"]))
        self.qr_holder.addStretch()

        bank_line = f"<b>Bank:</b> {account['bank']}<br>" if account["bank"] else ""
        self.receiver_label.setText(
            f"<b>{provider}</b><br>"
            f"{bank_line}"
            f"<b>Account name:</b> {account['account_name']}<br>"
            f"<b>Account number:</b> {account['account_number']}<br>"
            f"<b>Amount:</b> ₱{self.total:,.2f}"
        )
        self.reference_input.clear()

    def update_location(self, *args):
        self.location_address.setText(
            self.locations.get(self.location_combo.currentText(), "")
        )

    # ---------- paying ----------
    def on_pay(self):
        method = self.method_combo.currentText()
        provider = self.provider_combo.currentText() or None
        details = {}

        if method == "Cash":
            details["amount_tendered"] = self.tendered_spin.value()
            details["location"] = self.location_combo.currentText()
        elif method == "Card":
            details["card_number"] = self.card_number_input.text()
            details["card_holder"] = self.card_holder_input.text()
        elif method == "E-Wallet / E-Banking":
            details["reference_number"] = self.reference_input.text()

        self.pay_requested.emit({
            "method": method,
            "provider": provider,
            "details": details
        })
