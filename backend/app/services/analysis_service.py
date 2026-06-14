from fastapi import Request
from sqlalchemy.orm import Session
from ..pipeline.context import PipelineContext
from ..pipeline.manager import run_pipeline
from ..repositories.claim_repository import save_claim


async def analyze_image(image_bytes: bytes, request: Request, db: Session) -> dict:
    ctx = PipelineContext(raw_bytes=image_bytes, fuente="imagen")
    ctx = await run_pipeline(ctx, request.app.state.vectorizer, request.app.state.classifier)
    return _persist_and_return(ctx, db)


async def analyze_text(texto: str, request: Request, db: Session) -> dict:
    ctx = PipelineContext(raw_text=texto, fuente="texto")
    ctx = await run_pipeline(ctx, request.app.state.vectorizer, request.app.state.classifier)
    return _persist_and_return(ctx, db)


def _persist_and_return(ctx: PipelineContext, db: Session) -> dict:
    claim = save_claim(db, {
        "texto_original": ctx.extracted_text,
        "texto_limpio":   ctx.clean_text,
        "label":          ctx.label,
        "score_alta":     ctx.score_alta,
        "score_media":    ctx.score_media,
        "score_baja":     ctx.score_baja,
        "fuente":         ctx.fuente,
    })
    return {
        "id":             claim.id,
        "label":          claim.label,
        "score_alta":     claim.score_alta,
        "score_media":    claim.score_media,
        "score_baja":     claim.score_baja,
        "texto_extraido": claim.texto_original,
        "fuente":         claim.fuente,
    }
