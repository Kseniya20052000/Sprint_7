import random
import string

def generate_random_string(length=10):
    """Генерирует случайную строку из букв нижнего регистра."""
    letters = string.ascii_lowercase
    return "".join(random.choice(letters) for _ in range(length))
