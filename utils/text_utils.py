import unicodedata


def title_to_slug(title: str) -> str:
    return title.replace("/", "").replace(" ", "-").lower()


def normalize_text(text: str) -> str:
    normalized_text = unicodedata.normalize('NFD', text)
    result = ''.join(c for c in normalized_text if unicodedata.category(c) != 'Mn')
    return result
