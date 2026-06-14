import asyncio
from concurrent.futures import ThreadPoolExecutor
import pytesseract
from PIL import Image
import io

_executor = ThreadPoolExecutor(max_workers=4)


def _run_tesseract(image_bytes: bytes) -> str:
    image = Image.open(io.BytesIO(image_bytes))
    return pytesseract.image_to_string(image, lang="spa", config="--psm 6")


async def apply_ocr(image_bytes: bytes) -> str:
    loop = asyncio.get_event_loop()
    text = await loop.run_in_executor(_executor, _run_tesseract, image_bytes)
    return text.strip()
