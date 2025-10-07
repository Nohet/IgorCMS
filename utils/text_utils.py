import os
import re
import secrets

import unicodedata


def sanitize_text(text: str) -> str:
    text = text.lower()

    text = unicodedata.normalize("NFD", text)
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")

    text = re.sub(r"[/\s?.,!@#$%^&*()+=\[\]{};:'\"\\|<>]", "-", text)
    text = re.sub(r"[^a-zA-Z0-9\-]", "", text)
    text = re.sub(r"-+", "-", text)

    text = text.strip("-")

    return text


def sanitize_filename(filename: str, *, fallback: str | None = None) -> str:
    if not filename:
        filename = fallback or secrets.token_hex(8)

    candidate = os.path.basename(filename)
    name, _, ext = candidate.partition(".")

    name = unicodedata.normalize("NFD", name)
    name = "".join(c for c in name if unicodedata.category(c) != "Mn")
    name = re.sub(r"[^a-zA-Z0-9_-]", "_", name)

    if not name:
        name = fallback or secrets.token_hex(8)

    ext = re.sub(r"[^a-zA-Z0-9]", "", ext.lower())

    if ext:
        return f"{name}.{ext}"

    return name
