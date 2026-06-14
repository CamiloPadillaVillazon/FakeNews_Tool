"""
Script: collect_factcheck_api.py
OE2 — Recolección de datos vía Google Fact Check Tools API

Uso:
    python backend/data/scripts/collect_factcheck_api.py

Salida:
    backend/data/dataset_api_nuevos.csv   <- registros nuevos listos para merge
"""

import requests
import pandas as pd
import time
import os
import re

# ── Configuración ─────────────────────────────────────────────────────────────

API_KEY  = "AIzaSyBxw1KK60c_PSaDexEMoC9LfA0cdlqzGHI"
BASE_URL = "https://factchecktools.googleapis.com/v1alpha1/claims:search"

OUTPUT_PATH  = "backend/data/dataset_api_nuevos.csv"
MAESTRO_PATH = "backend/data/dataset_maestro.csv"

# Términos de búsqueda — combina "Bolivia" con contexto electoral
QUERIES = [
    "Bolivia elecciones",
    "Bolivia electoral",
    "Bolivia voto",
    "Bolivia TSE",
    "Bolivia candidato presidente",
    "Bolivia fraude electoral",
    "Bolivia padrón electoral",
    "Bolivia referéndum",
    "Bolivia Tribunal Supremo Electoral",
    "Bolivia campaña política",
    "Bolivia diputados senado",
    "Bolivia urnas",
]

# Mapeo de rating → label (igual que en el proyecto)
LABEL_MAP = {
    "falso":     "Alta",
    "falsa":     "Alta",
    "false":     "Alta",
    "engañoso":  "Media",
    "engañosa":  "Media",
    "misleading":"Media",
    "verdadero": "Baja",
    "verdadera": "Baja",
    "true":      "Baja",
    "correcto":  "Baja",
}

MAX_PAGES_PER_QUERY = 5   # máximo de páginas por término (10 results/página = 50 por query)
PAGE_SIZE           = 10
DELAY_BETWEEN_CALLS = 0.5 # segundos entre llamadas para no saturar la API


# ── Funciones ──────────────────────────────────────────────────────────────────

def normalize_rating(rating: str) -> str | None:
    """Normaliza el textualRating a su forma canónica."""
    clean = re.sub(r"[^a-záéíóúüñ]", "", rating.lower().strip())
    return LABEL_MAP.get(clean)


def fetch_page(query: str, page_token: str = None) -> dict:
    """Llama a la API y devuelve el JSON de respuesta."""
    params = {
        "key":          API_KEY,
        "query":        query,
        "languageCode": "es",
        "pageSize":     PAGE_SIZE,
        "maxAgeDays":   3650,   # últimos 10 años
    }
    if page_token:
        params["pageToken"] = page_token

    resp = requests.get(BASE_URL, params=params, timeout=15)
    resp.raise_for_status()
    return resp.json()


def is_electoral(text: str) -> bool:
    """Filtra registros con contenido claramente electoral."""
    keywords = [
        "elecciones", "electoral", "voto", "votar", "candidato", "tse",
        "tribunal supremo", "padrón", "urna", "campaña", "presidente",
        "diputado", "senador", "referéndum", "referendo", "sufragio",
        "partido", "reelección", "fraude", "bolivia verifica",
    ]
    text_lower = text.lower()
    return any(kw in text_lower for kw in keywords)


def collect_all() -> list[dict]:
    """Recorre todas las queries y páginas, devuelve lista de registros crudos."""
    records = []
    seen_urls = set()

    for query in QUERIES:
        print(f"\n🔍 Query: '{query}'")
        page_token = None

        for page_num in range(1, MAX_PAGES_PER_QUERY + 1):
            try:
                data = fetch_page(query, page_token)
            except requests.HTTPError as e:
                print(f"   ⚠️  HTTP error en página {page_num}: {e}")
                break

            claims = data.get("claims", [])
            if not claims:
                print(f"   Sin más resultados en página {page_num}")
                break

            print(f"   Página {page_num}: {len(claims)} claims")

            for claim in claims:
                reviews = claim.get("claimReview", [])
                if not reviews:
                    continue

                review = reviews[0]
                url    = review.get("url", "")

                # Deduplicar por URL
                if url in seen_urls:
                    continue
                seen_urls.add(url)

                texto        = claim.get("text", "").strip()
                rating_raw   = review.get("textualRating", "").strip()
                label        = normalize_rating(rating_raw)

                # Solo procesar si tiene label reconocible
                if not label:
                    continue

                # Filtro electoral (segunda línea de defensa)
                if not is_electoral(texto + " " + query):
                    continue

                records.append({
                    "fuente_verificadora": review.get("publisher", {}).get("site", ""),
                    "url_origen":          url,
                    "texto_crudo":         texto,
                    "categoria_original":  rating_raw,
                    "label":               label,
                })

            page_token = data.get("nextPageToken")
            if not page_token:
                break

            time.sleep(DELAY_BETWEEN_CALLS)

    return records


def build_dataframe(records: list[dict]) -> pd.DataFrame:
    """Convierte los registros a DataFrame y deduplica."""
    df = pd.DataFrame(records)

    antes = len(df)
    df.drop_duplicates(subset=["url_origen"],  keep="first", inplace=True)
    df.drop_duplicates(subset=["texto_crudo"], keep="first", inplace=True)
    despues = len(df)

    df.reset_index(drop=True, inplace=True)
    df.index += 1
    df.index.name = "id_registro"
    df.reset_index(inplace=True)

    print(f"\n{'='*55}")
    print(f"  Registros recolectados      : {antes}")
    print(f"  Después de deduplicar       : {despues}")
    print(f"  Duplicados eliminados       : {antes - despues}")
    return df


def remove_already_in_maestro(df_new: pd.DataFrame) -> pd.DataFrame:
    """Elimina registros cuya URL ya está en el dataset maestro actual."""
    if not os.path.exists(MAESTRO_PATH):
        return df_new

    df_maestro = pd.read_csv(MAESTRO_PATH, encoding="utf-8")
    existing_urls = set(df_maestro["url_origen"].dropna())

    antes = len(df_new)
    df_filtered = df_new[~df_new["url_origen"].isin(existing_urls)].copy()
    df_filtered.reset_index(drop=True, inplace=True)
    df_filtered.index += 1
    df_filtered.index.name = "id_registro"
    df_filtered.reset_index(inplace=True)

    print(f"  Ya existían en maestro      : {antes - len(df_filtered)}")
    print(f"  Registros verdaderamente nuevos: {len(df_filtered)}")
    return df_filtered


def print_summary(df: pd.DataFrame):
    print(f"\n  Distribución de label:")
    for label, count in df["label"].value_counts().items():
        print(f"    {label:<6}: {count}")

    print(f"\n  Distribución por fuente (top 5):")
    for fuente, count in df["fuente_verificadora"].value_counts().head(5).items():
        print(f"    {fuente}: {count}")
    print(f"{'='*55}")


# ── Main ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 55)
    print("  RECOLECCIÓN — Google Fact Check Tools API")
    print("  Proyecto: Herramienta Electoral Bolivia")
    print("=" * 55)

    records = collect_all()

    if not records:
        print("\n⚠️  No se recolectaron registros. Revisa la API key o los filtros.")
        exit(1)

    df = build_dataframe(records)
    df = remove_already_in_maestro(df)

    if df.empty:
        print("\n✅ Todos los registros ya estaban en el dataset maestro. Nada nuevo.")
        exit(0)

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    df.to_csv(OUTPUT_PATH, index=False, encoding="utf-8")

    print_summary(df)
    print(f"\n✅ Archivo guardado en: {OUTPUT_PATH}")
    print(f"\nPróximo paso: revisar el archivo y ejecutar merge_dataset.py")
    print(f"para incorporar los nuevos registros al dataset_maestro.csv")
