import random
import string
from app.config import settings


def generate_short_code(length: int = None) -> str:
    alphabet = string.ascii_letters + string.digits
    length = length or settings.SHORT_CODE_LENGTH
    return ''.join(random.choices(alphabet, k=length))
