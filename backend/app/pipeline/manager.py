from .filter_ocr import apply_ocr
from .filter_cleaner import clean_text
from .filter_vectorizer import vectorize_text
from .filter_classifier import classify_vector


def run_pipeline(image_bytes: bytes) -> dict:
    text = apply_ocr(image_bytes)
    cleaned = clean_text(text)
    vector = vectorize_text(cleaned)
    prediction = classify_vector(vector)
    return prediction
