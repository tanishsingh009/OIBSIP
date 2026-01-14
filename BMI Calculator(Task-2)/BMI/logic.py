from typing import Tuple

class BMILogic:
    @staticmethod
    def calculate_bmi(weight_kg: float, height_m: float) -> float:
        """Calculates BMI given weight in kg and height in meters."""
        if height_m <= 0:
            raise ValueError("Height must be positive")
        return round(weight_kg / (height_m ** 2), 2)

    @staticmethod
    def get_category(bmi: float) -> str:
        """Returns the BMI category."""
        if bmi < 18.5:
            return "Underweight"
        elif 18.5 <= bmi < 24.9:
            return "Normal weight"
        elif 24.9 <= bmi < 29.9:
            return "Overweight"
        else:
            return "Obese"

    @staticmethod
    def validate_input(weight: str, height: str) -> Tuple[float, float]:
        """Validates and converts input strings to float values."""
        try:
            w = float(weight)
            h = float(height)
            if w <= 0 or h <= 0:
                raise ValueError("Values must be positive")
            return w, h
        except ValueError as e:
            raise ValueError("Invalid numeric input")
