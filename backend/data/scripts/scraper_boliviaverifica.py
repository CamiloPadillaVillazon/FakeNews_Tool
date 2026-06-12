"""
Scraper de boliviaverifica.bo via WordPress JSON API.
Filtra artículos electorales por categoría ID=458 (Elecciones) o keywords en título.
Salida: backend/data/dataset_boliviaverifica_nuevos.csv
Ejecutar desde cualquier directorio: python backend/data/scripts/scraper_boliviaverifica.py
"""
import os
import time
import pandas as pd
import requests
from bs4 import BeautifulSoup

ROOT        = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
OUTPUT_FILE = os.path.join(ROOT, "backend", "data", "dataset_boliviaverifica_nuevos.csv")
MAESTRO_CSV = os.path.join(ROOT, "backend", "data", "dataset_maestro.csv")

SITE = "boliviaverifica.bo"

CATEGORIES = ["falso", "verdadero", "enganosa"]

KEYWORDS = [
    "eleccion", "elecciones", "tse", "fraude",
    "votos", "voto", "papeleta", "candidatos",
    "candidato", "padron", "computo", "acta",
]

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
}

# IDs de categoría en la API WP de boliviaverifica.bo
BV_CATEGORIAS_MAP = {
    "falso":    2,
    "verdadero": 4,
    "enganoso": 6,
    "enganosa": 6,
}
BV_ELECCIONES_ID = 458

LABEL_MAP = {"Falso": "Alta", "Engañoso": "Media", "Verdadero": "Baja"}


def clean_text(value):
    if not value:
        return ""
    return " ".join(value.split())


def normalize_category(slug):
    return {"falso": "Falso", "verdadero": "Verdadero",
            "enganoso": "Engañoso", "enganosa": "Engañoso"}.get(slug.lower(), slug.title())


def matches_keywords(text):
    if not text:
        return False
    t = text.lower()
    return any(kw in t for kw in KEYWORDS)


def cargar_urls_existentes() -> set:
    urls = set()
    if not os.path.exists(MAESTRO_CSV):
        return urls
    df = pd.read_csv(MAESTRO_CSV, encoding="utf-8", usecols=["url_origen"])
    urls = set(df["url_origen"].dropna().str.strip())
    return urls


def request_page(url):
    try:
        return requests.get(url, headers=HEADERS, timeout=30)
    except requests.RequestException as exc:
        print(f"  Error de conexión: {exc}")
        return None


def scrape_category(category_slug, urls_existentes):
    rows = []
    cat_id = BV_CATEGORIAS_MAP.get(category_slug.lower())
    if not cat_id:
        return rows

    categoria_label = normalize_category(category_slug)
    label           = LABEL_MAP.get(categoria_label, "")
    page            = 1
    vistos          = 0
    nuevos          = 0

    print(f"\n--- Categoría: {category_slug} ({categoria_label}) ---")

    while True:
        url      = f"https://{SITE}/wp-json/wp/v2/posts?categories={cat_id}&per_page=100&page={page}"
        response = request_page(url)

        if not response or response.status_code != 200:
            break

        data = response.json()
        if not data:
            break

        for post in data:
            vistos += 1
            title_html = post.get("title", {}).get("rendered", "")
            title      = clean_text(BeautifulSoup(title_html, "html.parser").get_text())
            if not title:
                continue

            post_categories = post.get("categories", [])
            badge_match     = BV_ELECCIONES_ID in post_categories
            keyword_match   = matches_keywords(title)

            if not badge_match and not keyword_match:
                continue

            link = post.get("link", "")
            if link in urls_existentes:
                continue

            rows.append({
                "fuente_verificadora": SITE,
                "url_origen":          link,
                "texto_crudo":         title,
                "categoria_original":  categoria_label,
                "label":               label,
                "fecha_publicacion":   post.get("date", ""),
            })
            urls_existentes.add(link)
            nuevos += 1

        print(f"  Página {page}: {len(data)} posts, {nuevos} electorales nuevos acumulados.")
        page += 1
        time.sleep(1.0)

    print(f"  Total: {nuevos} artículos electorales nuevos de {vistos} revisados.")
    return rows


def main():
    print("=" * 60)
    print("  Scraper boliviaverifica.bo — Filtro Electoral")
    print("=" * 60)

    urls_existentes = cargar_urls_existentes()
    print(f"URLs ya en dataset maestro: {len(urls_existentes)}")

    all_rows = []
    for slug in CATEGORIES:
        all_rows.extend(scrape_category(slug, urls_existentes))

    if not all_rows:
        print("\nNo se encontraron artículos electorales nuevos.")
        return

    df = pd.DataFrame(all_rows)
    df = df.drop_duplicates(subset=["url_origen"]).reset_index(drop=True)
    df["id_registro"] = df.index + 1
    df = df[["id_registro", "fuente_verificadora", "url_origen",
             "texto_crudo", "categoria_original", "label"]]

    df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8")

    dist  = df["label"].value_counts()
    total = len(df)
    print("\n" + "=" * 60)
    print(f"  Nuevos artículos electorales encontrados: {total}")
    for label in ["Alta", "Media", "Baja"]:
        n = dist.get(label, 0)
        print(f"    {label:<5} : {n} ({n/total*100:.1f}%)")
    print(f"  Archivo guardado en: backend/data/dataset_boliviaverifica_nuevos.csv")
    print("=" * 60)


if __name__ == "__main__":
    main()
