import os
import sys
import joblib
from contextlib import asynccontextmanager
from fastapi import FastAPI

# La consola de Windows usa cp1252 por defecto; forzar UTF-8 para que los
# mensajes con emojis no rompan el arranque del servidor.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass
from .config.settings import settings
from .config.database import engine
from .models.claim import Base
from .api.v1.analyze import router as analyze_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Crear tablas si no existen
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as exc:
        print(f"⚠️  No se pudo conectar a PostgreSQL al crear tablas: {exc}")
    # Cargar modelos una sola vez
    app.state.vectorizer = joblib.load(
        os.path.join(settings.models_dir, "tfidf_vectorizer.pkl")
    )
    app.state.classifier = joblib.load(
        os.path.join(settings.models_dir, "mlp_classifier.pkl")
    )
    print("✅ Modelos cargados correctamente")
    yield
    print("🛑 Servidor detenido")


app = FastAPI(title="Herramienta Electoral", lifespan=lifespan)
app.include_router(analyze_router)


@app.get("/health")
def health_check():
    return {"status": "ok"}
