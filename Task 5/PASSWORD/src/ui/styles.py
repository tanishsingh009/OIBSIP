DARK_THEME = """
QWidget {
    background-color: #2b2b2b;
    color: #ffffff;
    font-family: 'Segoe UI', sans-serif;
    font-size: 14px;
}

QLineEdit {
    background-color: #3b3b3b;
    border: 1px solid #555555;
    border-radius: 4px;
    padding: 8px;
    color: #ffffff;
    font-size: 16px;
}

QLineEdit:focus {
    border: 1px solid #3b8ed0;
}

QPushButton {
    background-color: #3b8ed0;
    color: white;
    border: none;
    border-radius: 4px;
    padding: 8px 16px;
    font-weight: bold;
}

QPushButton:hover {
    background-color: #3682be;
}

QPushButton#copyButton {
    background-color: #4caf50;
}

QPushButton#copyButton:hover {
    background-color: #45a049;
}

QLabel {
    color: #dddddd;
}

QCheckBox {
    spacing: 5px;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
}

QSlider::groove:horizontal {
    border: 1px solid #999999;
    height: 8px;
    background: #4a4a4a;
    margin: 2px 0;
    border-radius: 4px;
}

QSlider::handle:horizontal {
    background: #3b8ed0;
    border: 1px solid #3b8ed0;
    width: 18px;
    height: 18px;
    margin: -7px 0;
    border-radius: 9px;
}

QProgressBar {
    border: 1px solid #555555;
    border-radius: 4px;
    text-align: center;
    background-color: #3b3b3b;
}

QProgressBar::chunk {
    background-color: #3b8ed0;
    border-radius: 3px;
}
"""
