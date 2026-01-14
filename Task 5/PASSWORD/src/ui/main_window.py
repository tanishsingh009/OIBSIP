from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QCheckBox, QSlider, QLineEdit, QPushButton, 
    QProgressBar, QMessageBox, QFrame, QApplication
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QClipboard, QIcon
import pyperclip

from src.generator_logic import PasswordGenerator
from src.ui.styles import DARK_THEME

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.generator = PasswordGenerator()
        self.init_ui()
        self.generate_password() # Initial generation

    def init_ui(self):
        self.setWindowTitle("Advanced Password Generator")
        self.setGeometry(100, 100, 500, 600)
        
        # Central Widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)
        central_widget.setLayout(main_layout)

        # Title
        title_label = QLabel("Password Generator")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #3b8ed0;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)

        # Password Display Section
        display_layout = QHBoxLayout()
        self.password_display = QLineEdit()
        self.password_display.setReadOnly(True)
        self.password_display.setPlaceholderText("Generated Password")
        self.password_display.setStyleSheet("font-size: 18px; padding: 10px;")
        
        self.copy_btn = QPushButton("Copy")
        self.copy_btn.setObjectName("copyButton")
        self.copy_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.copy_btn.clicked.connect(self.copy_to_clipboard)
        
        self.regenerate_btn = QPushButton("Generate")
        self.regenerate_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.regenerate_btn.clicked.connect(self.generate_password)

        display_layout.addWidget(self.password_display)
        display_layout.addWidget(self.copy_btn)
        display_layout.addWidget(self.regenerate_btn)
        main_layout.addLayout(display_layout)

        # Strength Meter
        strength_layout = QVBoxLayout()
        strength_label_title = QLabel("Password Strength:")
        self.strength_bar = QProgressBar()
        self.strength_bar.setTextVisible(True)
        self.strength_bar.setRange(0, 128) # Entropy range approx
        self.strength_text = QLabel("Strength: Unknown")
        self.strength_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        strength_layout.addWidget(strength_label_title)
        strength_layout.addWidget(self.strength_bar)
        strength_layout.addWidget(self.strength_text)
        main_layout.addLayout(strength_layout)

        # Separator
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        main_layout.addWidget(line)

        # Options Section
        options_layout = QVBoxLayout()
        
        # Length
        length_layout = QHBoxLayout()
        length_label = QLabel("Length:")
        self.length_val_label = QLabel("16")
        self.length_slider = QSlider(Qt.Orientation.Horizontal)
        self.length_slider.setRange(4, 64)
        self.length_slider.setValue(16)
        self.length_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.length_slider.setTickInterval(4)
        self.length_slider.valueChanged.connect(self.update_length_label)
        self.length_slider.valueChanged.connect(self.generate_password) # Real-time generation

        length_layout.addWidget(length_label)
        length_layout.addWidget(self.length_slider)
        length_layout.addWidget(self.length_val_label)
        options_layout.addLayout(length_layout)

        # Checkboxes
        checkboxes_layout = QHBoxLayout()
        self.check_upper = QCheckBox("Uppercase (A-Z)")
        self.check_upper.setChecked(True)
        self.check_upper.stateChanged.connect(self.generate_password)
        
        self.check_lower = QCheckBox("Lowercase (a-z)")
        self.check_lower.setChecked(True)
        self.check_lower.stateChanged.connect(self.generate_password)
        
        checkboxes_layout.addWidget(self.check_upper)
        checkboxes_layout.addWidget(self.check_lower)
        options_layout.addLayout(checkboxes_layout)

        checkboxes_layout_2 = QHBoxLayout()
        self.check_digits = QCheckBox("Digits (0-9)")
        self.check_digits.setChecked(True)
        self.check_digits.stateChanged.connect(self.generate_password)
        
        self.check_symbols = QCheckBox("Symbols (!@#)")
        self.check_symbols.setChecked(True)
        self.check_symbols.stateChanged.connect(self.generate_password)
        
        checkboxes_layout_2.addWidget(self.check_digits)
        checkboxes_layout_2.addWidget(self.check_symbols)
        options_layout.addLayout(checkboxes_layout_2)

        # Exclude Characters
        exclude_layout = QVBoxLayout()
        exclude_label = QLabel("Exclude Characters:")
        self.exclude_input = QLineEdit()
        self.exclude_input.setPlaceholderText("e.g. iIlL1oO0")
        self.exclude_input.textChanged.connect(self.generate_password)
        
        exclude_layout.addWidget(exclude_label)
        exclude_layout.addWidget(self.exclude_input)
        options_layout.addLayout(exclude_layout)

        main_layout.addLayout(options_layout)
        main_layout.addStretch()

        # Set Style
        self.setStyleSheet(DARK_THEME)

    def update_length_label(self, value):
        self.length_val_label.setText(str(value))

    def generate_password(self):
        length = self.length_slider.value()
        use_upper = self.check_upper.isChecked()
        use_lower = self.check_lower.isChecked()
        use_digits = self.check_digits.isChecked()
        use_symbols = self.check_symbols.isChecked()
        exclude_chars = self.exclude_input.text()

        # Prevent unchecking all valid options
        if not (use_upper or use_lower or use_digits or use_symbols):
             self.password_display.setText("Select at least one option")
             self.strength_bar.setValue(0)
             self.strength_text.setText("Strength: INVALID")
             return

        password = self.generator.generate_password(
            length, use_upper, use_lower, use_digits, use_symbols, exclude_chars
        )
        self.password_display.setText(password)
        
        self.update_strength(password)

    def update_strength(self, password):
        if password.startswith("Error"):
            self.strength_bar.setValue(0)
            self.strength_text.setText("Strength: N/A")
            return

        strength_desc, entropy = self.generator.check_strength(password)
        
        # Color code based on strength
        color = "#ff4d4d" # Weak (Red)
        if strength_desc == "Medium":
            color = "#ffca28" # Medium (Yellow)
        elif strength_desc in ["Strong", "Very Strong"]:
            color = "#4caf50" # Green

        self.strength_bar.setStyleSheet(f"""
            QProgressBar::chunk {{ background-color: {color}; border-radius: 3px; }}
            QProgressBar {{ border: 1px solid #555555; background-color: #3b3b3b; text-align: center; }}
        """)
        
        self.strength_bar.setValue(min(int(entropy), 128))
        self.strength_text.setText(f"Strength: {strength_desc} ({int(entropy)} bits)")

    def copy_to_clipboard(self):
        password = self.password_display.text()
        if password and not password.startswith("Error") and not password.startswith("Select"):
            pyperclip.copy(password)
            # Optional: Show a small tooltip or status message?
            self.copy_btn.setText("Copied!")
            # Retain "Copied!" for a second then revert (requires QTimer, maybe overkill, just leave plain for now or use QTimer)
            # Simpler: just leave it, or maybe use QTimer.singleShot
            from PyQt6.QtCore import QTimer
            QTimer.singleShot(2000, lambda: self.copy_btn.setText("Copy"))

