from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QComboBox, QStackedWidget, QMessageBox,
    QTabWidget, QTableWidget, QTableWidgetItem, QHeaderView, QFrame,
    QSpacerItem, QSizePolicy
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.dates as mdates
from datetime import datetime

from database import DatabaseManager
from logic import BMILogic

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Advanced BMI Calculator")
        self.setGeometry(100, 100, 900, 700)
        
        # Dark Theme Stylesheet
        self.setStyleSheet("""
            QMainWindow { background-color: #1e1e1e; }
            QWidget { color: #ecf0f1; font-family: 'Segoe UI', sans-serif; font-size: 14px; }
            
            QFrame#Card { 
                background-color: #2d2d2d; 
                border-radius: 12px; 
                border: 1px solid #3d3d3d;
            }
            
            QLabel { color: #ecf0f1; }
            QLabel#Title { font-size: 26px; font-weight: bold; color: #ffffff; margin-bottom: 20px; }
            QLabel#Subtitle { font-size: 18px; color: #bdc3c7; }
            QLabel#Result { font-size: 28px; font-weight: bold; }
            
            QLineEdit { 
                background-color: #363636; 
                border: 1px solid #4d4d4d; 
                border-radius: 6px; 
                padding: 12px; 
                color: #ecf0f1;
            }
            QLineEdit:focus { border: 1px solid #3498db; }
            
            QComboBox {
                background-color: #363636;
                border: 1px solid #4d4d4d;
                border-radius: 6px;
                padding: 10px;
                color: #ecf0f1;
            }
            QComboBox::drop-down { border: none; }
            
            QPushButton { 
                background-color: #3498db; 
                color: white; 
                border-radius: 6px; 
                padding: 12px; 
                font-weight: bold;
                border: none;
            }
            QPushButton:hover { background-color: #2980b9; }
            QPushButton#Secondary { background-color: #95a5a6; }
            QPushButton#Secondary:hover { background-color: #7f8c8d; }
            QPushButton#Destructive { background-color: #e74c3c; }
            QPushButton#Destructive:hover { background-color: #c0392b; }
            QPushButton#Success { background-color: #2ecc71; }
            QPushButton#Success:hover { background-color: #27ae60; }
            
            QTabWidget::pane { border: 1px solid #3d3d3d; background-color: #2d2d2d; border-radius: 6px; }
            QTabBar::tab {
                background: #2d2d2d;
                color: #bdc3c7;
                padding: 10px 20px;
                margin-right: 2px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
            }
            QTabBar::tab:selected { background: #3d3d3d; color: white; font-weight: bold; }
            
            QTableWidget {
                background-color: #2d2d2d;
                gridline-color: #3d3d3d;
                border: none;
            }
            QTableWidget::item { padding: 5px; }
            QHeaderView::section {
                background-color: #363636;
                padding: 5px;
                border: none;
                font-weight: bold;
            }
        """)

        self.db = DatabaseManager()
        self.logic = BMILogic()

        self.central_widget = QStackedWidget()
        self.setCentralWidget(self.central_widget)

        self.login_widget = LoginWidget(self)
        self.dashboard_widget = DashboardWidget(self)

        self.central_widget.addWidget(self.login_widget)
        self.central_widget.addWidget(self.dashboard_widget)

    def switch_to_dashboard(self, user_name):
        self.dashboard_widget.set_user(user_name)
        self.dashboard_widget.load_history()
        self.central_widget.setCurrentWidget(self.dashboard_widget)

    def logout(self):
        self.central_widget.setCurrentWidget(self.login_widget)
        self.login_widget.load_users()

class LoginWidget(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        
        # Center the content using a card
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        card_frame = QFrame()
        card_frame.setObjectName("Card")
        card_frame.setFixedWidth(400)
        
        layout = QVBoxLayout(card_frame)
        layout.setSpacing(15)
        layout.setContentsMargins(40, 40, 40, 40)

        title = QLabel("BMI Tracker")
        title.setObjectName("Title")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        subtitle = QLabel("Sign in to track your health")
        subtitle.setObjectName("Subtitle")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addSpacing(20)

        self.user_combo = QComboBox()
        self.user_combo.setPlaceholderText("Select Profile")
        
        self.login_btn = QPushButton("Login")
        self.login_btn.clicked.connect(self.login)

        # Divider
        divider_layout = QHBoxLayout()
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("color: #4d4d4d;")
        divider_layout.addWidget(line)
        layout.addLayout(divider_layout)
        
        self.new_user_input = QLineEdit()
        self.new_user_input.setPlaceholderText("Enter new name...")
        
        self.create_btn = QPushButton("Create Profile")
        self.create_btn.setObjectName("Success")
        self.create_btn.clicked.connect(self.create_user)

        layout.addWidget(self.user_combo)
        layout.addWidget(self.login_btn)
        layout.addSpacing(10)
        layout.addWidget(self.new_user_input)
        layout.addWidget(self.create_btn)

        main_layout.addWidget(card_frame)
        self.setLayout(main_layout)
        self.load_users()

    def load_users(self):
        self.user_combo.clear()
        users = self.main_window.db.get_users()
        self.user_combo.addItems(users)

    def login(self):
        user = self.user_combo.currentText()
        if user:
            self.main_window.switch_to_dashboard(user)
        else:
            QMessageBox.warning(self, "Error", "Please select a user")

    def create_user(self):
        name = self.new_user_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Error", "Name cannot be empty")
            return
        
        if self.main_window.db.add_user(name):
            QMessageBox.information(self, "Success", f"User '{name}' created!")
            self.load_users()
            self.new_user_input.clear()
        else:
            QMessageBox.warning(self, "Error", "User already exists")

class DashboardWidget(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.setLayout(self.layout)

        # Header
        header = QHBoxLayout()
        self.welcome_label = QLabel("Welcome")
        self.welcome_label.setObjectName("Title")
        self.welcome_label.setStyleSheet("font-size: 20px; margin: 0;")
        
        logout_btn = QPushButton("Logout")
        logout_btn.setObjectName("Destructive")
        logout_btn.setFixedWidth(100)
        logout_btn.clicked.connect(self.main_window.logout)
        
        header.addWidget(self.welcome_label)
        header.addStretch()
        header.addWidget(logout_btn)
        self.layout.addLayout(header)

        # Tabs
        self.tabs = QTabWidget()
        self.calculator_tab = CalculatorTab(self)
        self.history_tab = HistoryTab(self)
        
        self.tabs.addTab(self.calculator_tab, "Calculator")
        self.tabs.addTab(self.history_tab, "History & Trends")
        
        self.layout.addWidget(self.tabs)

    def set_user(self, user_name):
        self.welcome_label.setText(f"Hello, {user_name}")
        self.user_name = user_name

    def load_history(self):
        self.history_tab.refresh_data(self.user_name)

class CalculatorTab(QWidget):
    def __init__(self, dashboard):
        super().__init__()
        self.dashboard = dashboard
        
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        card = QFrame()
        card.setObjectName("Card")
        card.setFixedWidth(500)
        
        layout = QVBoxLayout(card)
        layout.setSpacing(20)
        layout.setContentsMargins(40, 40, 40, 40)

        layout.addWidget(QLabel("Input Measurements", objectName="Subtitle"))

        self.weight_input = QLineEdit()
        self.weight_input.setPlaceholderText("Weight (kilograms)")
        
        self.height_input = QLineEdit()
        self.height_input.setPlaceholderText("Height (meters)")
        
        calc_btn = QPushButton("Calculate BMI")
        calc_btn.clicked.connect(self.calculate)

        layout.addWidget(self.weight_input)
        layout.addWidget(self.height_input)
        layout.addWidget(calc_btn)
        
        # Divider
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("color: #4d4d4d; margin: 10px 0;")
        layout.addWidget(line)

        # Result Display with better typography
        result_container = QVBoxLayout()
        result_container.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.result_label = QLabel("--")
        self.result_label.setObjectName("Result")
        self.result_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.category_label = QLabel("")
        self.category_label.setObjectName("Subtitle")
        self.category_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        result_container.addWidget(QLabel("Your BMI", alignment=Qt.AlignmentFlag.AlignCenter))
        result_container.addWidget(self.result_label)
        result_container.addWidget(self.category_label)
        
        layout.addLayout(result_container)

        main_layout.addWidget(card)
        self.setLayout(main_layout)

    def calculate(self):
        w_text = self.weight_input.text()
        h_text = self.height_input.text()

        try:
            w, h = BMILogic.validate_input(w_text, h_text)
            bmi = BMILogic.calculate_bmi(w, h)
            category = BMILogic.get_category(bmi)

            self.result_label.setText(f"{bmi}")
            self.category_label.setText(category)

            # Color coding
            color = "#2ecc71" if category == "Normal weight" else "#f1c40f" if category == "Overweight" else "#e74c3c"
            self.result_label.setStyleSheet(f"color: {color}; font-size: 48px;")
            self.category_label.setStyleSheet(f"color: {color};")

            # Save to DB
            self.dashboard.main_window.db.add_record(
                self.dashboard.user_name, w, h, bmi, category
            )
            self.dashboard.load_history()

        except ValueError as e:
            QMessageBox.warning(self, "Input Error", str(e))

class HistoryTab(QWidget):
    def __init__(self, dashboard):
        super().__init__()
        self.dashboard = dashboard
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.setLayout(self.layout)

        # Matplotlib Graph Configuration
        plt.style.use('dark_background')
        self.figure = plt.figure(figsize=(5, 4))
        self.figure.patch.set_facecolor('#2d2d2d') # Match card background
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setStyleSheet("background-color: #2d2d2d; border-radius: 12px;")
        
        # Container for graph to give it rounded corners look via parent if needed, 
        # but canvas is its own widget. We'll rely on global styling or matplotlib config.
        self.layout.addWidget(self.canvas, stretch=1)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Date", "Weight (kg)", "BMI", "Category"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setAlternatingRowColors(True)
        self.table.stylesheet = "alternate-background-color: #363636;"
        self.layout.addWidget(self.table, stretch=1)

    def refresh_data(self, user_name):
        history = self.dashboard.main_window.db.get_history(user_name)
        
        # Update Table
        self.table.setRowCount(len(history))
        dates = []
        bmis = []
        
        for i, row in enumerate(history):
            date_str = row[0]
            weight = row[1]
            bmi = row[3]
            category = row[4]

            # Shorten date for display
            display_date = date_str.split(" ")[0]

            self.table.setItem(i, 0, QTableWidgetItem(display_date))
            self.table.setItem(i, 1, QTableWidgetItem(str(weight)))
            self.table.setItem(i, 2, QTableWidgetItem(str(bmi)))
            
            # Color code category cell
            cat_item = QTableWidgetItem(category)
            color = QColor("#2ecc71") if category == "Normal weight" else QColor("#f1c40f") if category == "Overweight" else QColor("#e74c3c")
            cat_item.setForeground(color)
            self.table.setItem(i, 3, cat_item)

            dates.append(datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S"))
            bmis.append(bmi)

        # Update Graph
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.set_facecolor('#2d2d2d')
        
        if dates:
            ax.plot(dates, bmis, marker='o', linestyle='-', color='#3498db', linewidth=2, markersize=8)
            ax.set_title(f"BMI Progression", color='white', fontsize=12, pad=15)
            ax.set_ylabel("BMI Value", color='#bdc3c7')
            ax.tick_params(axis='x', colors='#bdc3c7', labelsize=9)
            ax.tick_params(axis='y', colors='#bdc3c7')
            ax.grid(True, linestyle='--', alpha=0.3)
            
            # Highlight zones
            ax.axhspan(18.5, 24.9, color='#2ecc71', alpha=0.1, label='Normal')
            
            self.figure.autofmt_xdate()
        else:
            ax.text(0.5, 0.5, "No Data to Display", ha='center', va='center', color='#bdc3c7')
            ax.axis('off')
        
        self.canvas.draw()
