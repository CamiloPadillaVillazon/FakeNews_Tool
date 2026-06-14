from .context import PipelineContext
from .filter_preprocessor import preprocess_image
from .filter_ocr import apply_ocr
from .filter_cleaner import clean_text
from .filter_vectorizer import vectorize_text
from .filter_classifier import classify_vector


async def run_pipeline(
    ctx: PipelineContext,
    vectorizer,
    classifier,
) -> PipelineContext:

    # Filtro 0: preprocessor (solo si es imagen)
    if ctx.fuente == "imagen" and ctx.raw_bytes:
        ctx.processed_bytes = preprocess_image(ctx.raw_bytes)

    # Filtro 1: OCR (solo si es imagen)
    if ctx.fuente == "imagen":
        ctx.extracted_text = await apply_ocr(ctx.processed_bytes or ctx.raw_bytes)
    else:
        ctx.extracted_text = ctx.raw_text or ""

    # Filtro 2: cleaner
    ctx.clean_text = clean_text(ctx.extracted_text)

    # Filtro 3: vectorizer
    ctx.vector = vectorize_text(ctx.clean_text, vectorizer)

    # Filtro 4: classifier
    result = classify_vector(ctx.vector, classifier)
    ctx.label       = result["label"]
    ctx.score_alta  = result["score_alta"]
    ctx.score_media = result["score_media"]
    ctx.score_baja  = result["score_baja"]

    return ctx
