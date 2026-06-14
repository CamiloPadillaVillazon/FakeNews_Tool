from fastapi import APIRouter, UploadFile, File, Depends, Request, HTTPException
from sqlalchemy.orm import Session
from ...config.database import get_db
from ...schemas.analyze_schema import AnalyzeResponse, AnalyzeTextRequest
from ...services.analysis_service import analyze_image, analyze_text

router = APIRouter(prefix="/api/v1", tags=["analyze"])


@router.post("/analyze/image", response_model=AnalyzeResponse)
async def analyze_image_endpoint(
    request: Request,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    if file.content_type not in ("image/jpeg", "image/png"):
        raise HTTPException(status_code=400, detail="Solo se aceptan imágenes JPG o PNG")
    image_bytes = await file.read()
    return await analyze_image(image_bytes, request, db)


@router.post("/analyze/text", response_model=AnalyzeResponse)
async def analyze_text_endpoint(
    request: Request,
    body: AnalyzeTextRequest,
    db: Session = Depends(get_db),
):
    if not body.texto.strip():
        raise HTTPException(status_code=400, detail="El texto no puede estar vacío")
    return await analyze_text(body.texto, request, db)


@router.get("/history")
def get_history(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
):
    from ...repositories.claim_repository import get_all_claims
    claims = get_all_claims(db, skip=skip, limit=limit)
    return [
        {
            "id":         c.id,
            "label":      c.label,
            "score_alta": c.score_alta,
            "score_media": c.score_media,
            "score_baja": c.score_baja,
            "fuente":     c.fuente,
            "texto":      c.texto_original[:120] + "..." if len(c.texto_original or "") > 120 else c.texto_original,
            "timestamp":  str(c.timestamp),
        }
        for c in claims
    ]
