import re


def clean_text(text: str) -> str:
    text = str(text).lower()
    text = re.sub(r"https?://\S+", "", text)
    text = re.sub(r"@\w+|#\w+", "", text)
    text = re.sub(r"[^a-záéíóúüñà-ÿ0-9\s]", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text
