from pydantic import BaseModel


class AnalyzeResponse(BaseModel):
    id: int
    label: str                        # Alta / Media / Baja
    score_alta: float
    score_media: float
    score_baja: float
    texto_extraido: str               # texto que procesó el pipeline
    fuente: str                       # imagen / texto


class AnalyzeTextRequest(BaseModel):
    texto: str
