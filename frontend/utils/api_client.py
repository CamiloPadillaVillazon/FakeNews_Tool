import requests

BASE_URL = "http://localhost:8000"


def health_check() -> dict:
    r = requests.get(f"{BASE_URL}/health", timeout=5)
    r.raise_for_status()
    return r.json()


def analyze_image(image_bytes: bytes, filename: str, content_type: str = "image/jpeg") -> dict:
    """Envía imagen al endpoint /api/v1/analyze/image"""
    files = {"file": (filename, image_bytes, content_type)}
    r = requests.post(f"{BASE_URL}/api/v1/analyze/image", files=files, timeout=30)
    r.raise_for_status()
    return r.json()


def analyze_text(texto: str) -> dict:
    """Envía texto al endpoint /api/v1/analyze/text"""
    r = requests.post(
        f"{BASE_URL}/api/v1/analyze/text",
        json={"texto": texto},
        timeout=15,
    )
    r.raise_for_status()
    return r.json()


def get_history(skip: int = 0, limit: int = 100) -> list:
    """Obtiene el historial de análisis desde /api/v1/history"""
    r = requests.get(f"{BASE_URL}/api/v1/history", params={"skip": skip, "limit": limit}, timeout=10)
    r.raise_for_status()
    return r.json()
