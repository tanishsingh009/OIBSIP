import random
import string
import math

class PasswordGenerator:
    def __init__(self):
        self.uppercase = string.ascii_uppercase
        self.lowercase = string.ascii_lowercase
        self.digits = string.digits
        self.symbols = "!@#$%^&*()_+-=[]{}|;:,.<>?"

    def generate_password(self, length=12, use_upper=True, use_lower=True, use_digits=True, use_symbols=True, exclude_chars=""):
        """
        Generates a random password based on criteria.
        """
        char_pool = ""
        if use_upper:
            char_pool += self.uppercase
        if use_lower:
            char_pool += self.lowercase
        if use_digits:
            char_pool += self.digits
        if use_symbols:
            char_pool += self.symbols

        if exclude_chars:
            char_pool = "".join(c for c in char_pool if c not in exclude_chars)

        if not char_pool:
            return "Error: No characters available"

        password = "".join(random.choice(char_pool) for _ in range(length))
        return password

    def calculate_entropy(self, password):
        """
        Calculates the entropy of the password in bits.
        """
        pool_size = 0
        if any(c in string.ascii_uppercase for c in password):
            pool_size += 26
        if any(c in string.ascii_lowercase for c in password):
            pool_size += 26
        if any(c in string.digits for c in password):
            pool_size += 10
        if any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            pool_size += 32 # Approximate special chars
        
        if pool_size == 0:
            return 0
            
        entropy = len(password) * math.log2(pool_size)
        return entropy

    def check_strength(self, password):
        """
        Returns a strength description based on entropy.
        """
        entropy = self.calculate_entropy(password)
        if entropy < 28:
            return "Very Weak", entropy
        elif entropy < 36:
            return "Weak", entropy
        elif entropy < 60:
            return "Medium", entropy
        elif entropy < 128:
            return "Strong", entropy
        else:
            return "Very Strong", entropy
