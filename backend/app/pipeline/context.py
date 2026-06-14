from dataclasses import dataclass


@dataclass
class PipelineContext:
    raw_bytes: bytes | None = None       # imagen cruda (si input es imagen)
    raw_text: str | None = None          # texto directo (si input es texto)
    fuente: str = "texto"                # "imagen" | "texto"
    processed_bytes: bytes | None = None  # imagen tras preprocessor
    extracted_text: str = ""             # texto tras OCR
    clean_text: str = ""                 # texto tras cleaner
    vector: object = None                # csr_matrix tras vectorizer
    label: str = ""
    score_alta: float = 0.0
    score_media: float = 0.0
    score_baja: float = 0.0
