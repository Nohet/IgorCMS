import re

import unicodedata


def sanitize_text(text: str) -> str:
    text = text.lower()

    text = unicodedata.normalize('NFD', text)
    text = ''.join(c for c in text if unicodedata.category(c) != 'Mn')

    text = re.sub(r'[/\s?.,!@#$%^&*()+=\[\]{};:\'"\|\<>]', '-', text)

    text = re.sub(r'[^a-zA-Z0-9\-]', '', text)

    text = re.sub(r'-+', '-', text)

    text = text.strip('-')

    return text
