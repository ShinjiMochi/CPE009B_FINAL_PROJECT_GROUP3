from PyQt6.QtGui import QColor, QPalette

BLUE = "#1a56db"
BLUE_DARK = "#1446b5"
BORDER = "#e3e6ea"
BACKGROUND = "#f5f6f8"
MUTED = "#6b7280"
TEXT = "#1f2937"

STYLESHEET = f"""
* {{
    font-family: "Segoe UI", "Helvetica Neue", Arial, sans-serif;
    font-size: 13px;
    color: {TEXT};
}}
QLabel {{ background: transparent; }}
QLabel#muted {{ color: {MUTED}; font-size: 12px; }}
QLabel#heading {{ font-size: 18px; font-weight: 700; }}
QLabel#sectionTitle {{ font-size: 15px; font-weight: 700; }}
QLabel#price {{ font-size: 22px; font-weight: 700; }}
QLabel#chip {{
    color: {BLUE}; border: 1px solid {BLUE}; border-radius: 10px;
    padding: 2px 8px; font-size: 11px; background: white;
}}

QFrame#navbar {{ background: white; border-bottom: 1px solid {BORDER}; }}
QLabel#logo {{ font-size: 20px; font-weight: 800; }}
QLabel#step {{ color: {MUTED}; padding: 4px 10px; }}
QLabel#stepActive {{ color: {BLUE}; font-weight: 700; padding: 4px 10px;
                     border-bottom: 2px solid {BLUE}; }}

QFrame#card, QFrame#sidebar {{
    background: white; border: 1px solid {BORDER}; border-radius: 12px;
}}
QFrame#card QLabel, QFrame#sidebar QLabel {{ border: none; }}

QGroupBox {{
    background: white; border: 1px solid {BORDER}; border-radius: 12px;
    margin-top: 14px; padding: 12px;
}}
QGroupBox::title {{
    subcontrol-origin: margin; left: 14px; padding: 0 6px;
    font-weight: 700; background: {BACKGROUND};
}}

QPushButton {{
    background: {BLUE}; color: white; border: none; border-radius: 16px;
    padding: 8px 20px; font-weight: 600;
}}
QPushButton:hover {{ background: {BLUE_DARK}; }}
QPushButton:disabled {{ background: #c3cad6; color: #f3f4f6; }}
QPushButton[secondary="true"] {{
    background: white; color: {BLUE}; border: 1px solid {BLUE};
}}
QPushButton[secondary="true"]:hover {{ background: #eef3ff; }}

QLineEdit, QTextEdit, QPlainTextEdit, QSpinBox, QDoubleSpinBox,
QComboBox, QTimeEdit {{
    background: white; border: 1px solid #cfd5dd; border-radius: 8px;
    padding: 6px 8px;
}}
QLineEdit:focus, QTextEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus,
QComboBox:focus, QTimeEdit:focus {{ border: 1px solid {BLUE}; }}

QCheckBox, QRadioButton {{ spacing: 8px; background: transparent; }}
QScrollArea {{ border: none; background: transparent; }}
QScrollArea > QWidget > QWidget {{ background: transparent; }}

QSlider::groove:horizontal {{ height: 4px; background: {BORDER}; border-radius: 2px; }}
QSlider::sub-page:horizontal {{ background: {BLUE}; border-radius: 2px; }}
QSlider::handle:horizontal {{
    background: white; border: 2px solid {BLUE};
    width: 14px; height: 14px; margin: -6px 0; border-radius: 8px;
}}
"""


def apply_theme(app):
    app.setStyle("Fusion")
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(BACKGROUND))
    palette.setColor(QPalette.ColorRole.Base, QColor("white"))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(TEXT))
    palette.setColor(QPalette.ColorRole.Text, QColor(TEXT))
    app.setPalette(palette)
    app.setStyleSheet(STYLESHEET)