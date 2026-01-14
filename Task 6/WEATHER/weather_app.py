import sys
import requests
import geocoder
from typing import Optional, Dict, Any
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QRadioButton, QButtonGroup,
    QMessageBox, QFrame, QGridLayout
)
from PyQt6.QtCore import QThread, pyqtSignal, Qt
from PyQt6.QtGui import QPixmap, QFont, QColor, QPalette

class WeatherModel:
    def __init__(self):
        self.weather_data: Optional[Dict[str, Any]] = None
    
    def parse_weather_data(self, json_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            parsed = {
                'city': json_data.get('name', 'Unknown'),
                'country': json_data.get('sys', {}).get('country', ''),
                'temp_kelvin': json_data.get('main', {}).get('temp', 0),
                'temp_celsius': json_data.get('main', {}).get('temp', 0) - 273.15,
                'temp_fahrenheit': (json_data.get('main', {}).get('temp', 0) - 273.15) * 9/5 + 32,
                'condition': json_data.get('weather', [{}])[0].get('main', 'Unknown'),
                'description': json_data.get('weather', [{}])[0].get('description', '').title(),
                'humidity': json_data.get('main', {}).get('humidity', 0),
                'pressure': json_data.get('main', {}).get('pressure', 0),
                'wind_speed': json_data.get('wind', {}).get('speed', 0),
                'icon_code': json_data.get('weather', [{}])[0].get('icon', '01d')
            }
            self.weather_data = parsed
            return parsed
        except (KeyError, IndexError, TypeError) as e:
            raise ValueError(f"Failed to parse weather data: {str(e)}")
    
    def get_icon_url(self, icon_code: str) -> str:
        return f"http://openweathermap.org/img/wn/{icon_code}@2x.png"


class WeatherWorker(QThread):
    """
    QThread worker for handling API requests in background.
    """
    weather_fetched = pyqtSignal(dict) 
    error_occurred = pyqtSignal(str)    
    
    def __init__(self, api_key: str):
        super().__init__()
        self.api_key = api_key
        self.city: Optional[str] = None
        self.use_coords = False
        self.lat: Optional[float] = None
        self.lon: Optional[float] = None
        self.model = WeatherModel()
    
    def set_city(self, city: str):
        self.city = city
        self.use_coords = False
    
    def set_coordinates(self, lat: float, lon: float):
        self.lat = lat
        self.lon = lon
        self.use_coords = True
    
    def run(self):
        try:
            base_url = "https://api.openweathermap.org/data/2.5/weather"
            
            if self.use_coords and self.lat is not None and self.lon is not None:
                url = f"{base_url}?lat={self.lat}&lon={self.lon}&appid={self.api_key}"
            elif self.city:
                url = f"{base_url}?q={self.city}&appid={self.api_key}"
            else:
                self.error_occurred.emit("No city or coordinates provided.")
                return
            
            response = requests.get(url, timeout=10)
            
            if response.status_code == 401:
                self.error_occurred.emit("Invalid API Key. Please check your OpenWeatherMap API key.")
                return
            elif response.status_code == 404:
                self.error_occurred.emit(f"City '{self.city}' not found. Please check spelling.")
                return
            elif response.status_code != 200:
                self.error_occurred.emit(f"API Error: {response.status_code}")
                return
            
            json_data = response.json()
            parsed_data = self.model.parse_weather_data(json_data)
            self.weather_fetched.emit(parsed_data)
            
        except requests.exceptions.Timeout:
            self.error_occurred.emit("Request timed out.")
        except requests.exceptions.ConnectionError:
            self.error_occurred.emit("Connection error.")
        except ValueError as e:
            self.error_occurred.emit(str(e))
        except Exception as e:
            self.error_occurred.emit(f"Unexpected error: {str(e)}")


class LocationWorker(QThread):
    location_detected = pyqtSignal(float, float, str)  
    error_occurred = pyqtSignal(str)
    
    def run(self):
        try:
            g = geocoder.ip('me')
            if g.ok and g.latlng:
                lat, lon = g.latlng
                city = g.city or "Unknown Location"
                self.location_detected.emit(lat, lon, city)
            else:
                self.error_occurred.emit("Could not detect location.")
        except Exception as e:
            self.error_occurred.emit(f"Location detection failed: {str(e)}")


class InfoCard(QFrame):
    def __init__(self, title, value, icon_char=""):
        super().__init__()
        self.setFrameShape(QFrame.Shape.StyledPanel)
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.title_lbl = QLabel(f"{icon_char} {title}")
        self.title_lbl.setFont(QFont("Segoe UI", 10))
        self.title_lbl.setStyleSheet("color: #a6adc8;")
        
        self.value_lbl = QLabel(value)
        self.value_lbl.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        self.value_lbl.setStyleSheet("color: #cdd6f4;")
        
        layout.addWidget(self.title_lbl)
        layout.addWidget(self.value_lbl)
        
        self.setStyleSheet("""
            QFrame {
                background-color: #313244;
                border-radius: 12px;
                padding: 5px;
            }
        """)

    def update_value(self, value):
        self.value_lbl.setText(value)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.api_key = "ab04093855c57e38932461d82eb94461" # Replace with your actual key
        self.current_unit = "celsius"
        self.weather_data: Optional[Dict[str, Any]] = None
        
        self.init_ui()
        self.apply_stylesheet()
    
    def init_ui(self):
        self.setWindowTitle("Atmosphere")
        self.setMinimumSize(450, 750)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main Layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(25, 25, 25, 25)
        
        # --- Header Section ---
        header_layout = QHBoxLayout()
        
        self.city_input = QLineEdit()
        self.city_input.setPlaceholderText("Search city...")
        self.city_input.returnPressed.connect(self.fetch_weather)
        
        self.search_btn = QPushButton("🔍")
        self.search_btn.setFixedSize(45, 45)
        self.search_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.search_btn.clicked.connect(self.fetch_weather)
        
        self.location_btn = QPushButton("📍") 
        self.location_btn.setFixedSize(45, 45)
        self.location_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.location_btn.setToolTip("Use My Location")
        self.location_btn.clicked.connect(self.detect_location)
        
        header_layout.addWidget(self.city_input)
        header_layout.addWidget(self.search_btn)
        header_layout.addWidget(self.location_btn)
        
        main_layout.addLayout(header_layout)
        
        # --- Unit Toggle ---
        unit_layout = QHBoxLayout()
        unit_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.unit_group = QButtonGroup()
        
        self.celsius_radio = QRadioButton("°C")
        self.fahrenheit_radio = QRadioButton("°F")
        self.celsius_radio.setChecked(True)
        self.celsius_radio.setCursor(Qt.CursorShape.PointingHandCursor)
        self.fahrenheit_radio.setCursor(Qt.CursorShape.PointingHandCursor)
        
        self.unit_group.addButton(self.celsius_radio)
        self.unit_group.addButton(self.fahrenheit_radio)
        self.celsius_radio.toggled.connect(self.update_temperature_display)
        
        unit_layout.addWidget(self.celsius_radio)
        unit_layout.addSpacing(15)
        unit_layout.addWidget(self.fahrenheit_radio)
        main_layout.addLayout(unit_layout)

        # --- Weather Display Container (Initially Hidden) ---
        self.weather_container = QWidget()
        weather_layout = QVBoxLayout(self.weather_container)
        weather_layout.setSpacing(10)
        weather_layout.setContentsMargins(0, 10, 0, 0)
        
        # City & Country
        self.city_label = QLabel("City Name")
        self.city_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.city_label.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        weather_layout.addWidget(self.city_label)
        
        # Date/Desc
        self.condition_label = QLabel("Condition")
        self.condition_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.condition_label.setFont(QFont("Segoe UI", 14))
        self.condition_label.setStyleSheet("color: #bac2de;")
        weather_layout.addWidget(self.condition_label)
        
        # Icon
        self.icon_label = QLabel()
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.icon_label.setMinimumHeight(120)
        weather_layout.addWidget(self.icon_label)
        
        # Temperature
        self.temp_label = QLabel("--°")
        self.temp_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.temp_label.setFont(QFont("Segoe UI", 56, QFont.Weight.Bold))
        weather_layout.addWidget(self.temp_label)
        
        weather_layout.addSpacing(20)
        
        # Detail Cards Grid
        grid_layout = QGridLayout()
        grid_layout.setSpacing(15)
        
        self.humidity_card = InfoCard("Humidity", "--%", "💧")
        self.wind_card = InfoCard("Wind", "-- m/s", "💨")
        self.pressure_card = InfoCard("Pressure", "-- hPa", "🌡️")
        
        # Arrange in a grid
        grid_layout.addWidget(self.humidity_card, 0, 0)
        grid_layout.addWidget(self.wind_card, 0, 1)
        grid_layout.addWidget(self.pressure_card, 1, 0, 1, 2) # Span 2 columns
        
        weather_layout.addLayout(grid_layout)
        weather_layout.addStretch()
        
        main_layout.addWidget(self.weather_container)
        self.weather_container.hide()
        
        # Initial status or placeholder
        self.status_label = QLabel("Enter a city to start")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("color: #585b70; font-size: 14px;")
        main_layout.addWidget(self.status_label)
        
    def apply_stylesheet(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e2e;
            }
            QWidget {
                color: #cdd6f4;
            }
            QLineEdit {
                background-color: #313244;
                border: 2px solid #45475a;
                border-radius: 22px;
                padding: 0 15px;
                font-size: 14px;
                height: 40px;
                color: #cdd6f4;
            }
            QLineEdit:focus {
                border: 2px solid #89b4fa;
            }
            QPushButton {
                background-color: #313244;
                border: 2px solid #45475a;
                border-radius: 22px;
                color: #89b4fa;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #45475a;
                border-color: #89b4fa;
            }
            QPushButton:pressed {
                background-color: #89b4fa;
                color: #1e1e2e;
            }
            QRadioButton {
                font-size: 14px;
                font-weight: bold;
                color: #bac2de;
            }
            QRadioButton::indicator {
                width: 16px;
                height: 16px;
                border-radius: 8px;
                border: 2px solid #45475a;
                background-color: #313244;
            }
            QRadioButton::indicator:checked {
                background-color: #89b4fa;
                border-color: #89b4fa;
            }
            QRadioButton::checked {
                color: #89b4fa;
            }
        """)

    def fetch_weather(self):
        city = self.city_input.text().strip()
        if not city:
            QMessageBox.warning(self, "Input Error", "Please enter a city name.")
            return
        
        self.set_ui_loading(True)
        
        self.worker = WeatherWorker(self.api_key)
        self.worker.set_city(city)
        self.worker.weather_fetched.connect(self.display_weather)
        self.worker.error_occurred.connect(self.handle_error)
        self.worker.finished.connect(lambda: self.set_ui_loading(False))
        self.worker.start()

    def detect_location(self):
        self.set_ui_loading(True)
        self.location_worker = LocationWorker()
        self.location_worker.location_detected.connect(self.on_location_detected)
        self.location_worker.error_occurred.connect(self.handle_error)
        self.location_worker.finished.connect(lambda: self.set_ui_loading(False))
        self.location_worker.start()

    def on_location_detected(self, lat: float, lon: float, city: str):
        self.city_input.setText(city)
        self.worker = WeatherWorker(self.api_key)
        self.worker.set_coordinates(lat, lon)
        self.worker.weather_fetched.connect(self.display_weather)
        self.worker.error_occurred.connect(self.handle_error)
        self.worker.start()

    def display_weather(self, data: Dict[str, Any]):
        self.weather_data = data
        self.status_label.hide()
        self.weather_container.show()
        
        self.city_label.setText(f"{data['city']}, {data['country']}")
        self.condition_label.setText(data['description'])
        self.update_temperature_display()
        
        self.humidity_card.update_value(f"{data['humidity']}%")
        self.wind_card.update_value(f"{data['wind_speed']:.1f} m/s")
        self.pressure_card.update_value(f"{data['pressure']} hPa")
        
        # Load Icon
        try:
            icon_url = f"http://openweathermap.org/img/wn/{data['icon_code']}@2x.png"
            # In a real app, you might want to cache these or download asynchronously 
            # without blocking UI, but requests in main thread for small image is acceptable for this demo
            # Ideally, use another worker or NetworkAccessManager. 
            # For simplicity matching the prompt's style, we keep it simple but safe via try/except.
            response = requests.get(icon_url, timeout=3)
            if response.status_code == 200:
                pixmap = QPixmap()
                pixmap.loadFromData(response.content)
                self.icon_label.setPixmap(pixmap.scaled(
                    150, 150,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                ))
        except Exception:
            self.icon_label.setText("🌤️")

    def update_temperature_display(self):
        if not self.weather_data:
            return
        
        if self.celsius_radio.isChecked():
            temp = self.weather_data['temp_celsius']
            self.temp_label.setText(f"{temp:.1f}°")
        else:
            temp = self.weather_data['temp_fahrenheit']
            self.temp_label.setText(f"{temp:.1f}°")

    def handle_error(self, message):
        QMessageBox.critical(self, "Error", message)

    def set_ui_loading(self, loading):
        self.search_btn.setEnabled(not loading)
        self.location_btn.setEnabled(not loading)
        if loading:
            self.search_btn.setText("...")
        else:
            self.search_btn.setText("🔍")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Optional: nicer font smoothing
    font = app.font()
    font.setHintingPreference(QFont.HintingPreference.PreferNoHinting)
    app.setFont(font)
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
