from fastapi import FastAPI

app = FastAPI(title="Herramienta Electoral")


@app.get("/health")
def health_check():
    return {"status": "ok"}
