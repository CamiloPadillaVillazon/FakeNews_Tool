"""
Scraper de ChequeaBolivia — categorías Verdadero y Engañoso.
Filtra solo artículos de ámbito electoral por keywords en título y cuerpo.
Salida: backend/data/dataset_chequeabolivia_nuevos.csv
Ejecutar desde cualquier directorio: python backend/data/scripts/scraper_chequeabolivia.py
"""
import os
import re
import time
import csv
import requests
from bs4 import BeautifulSoup

ROOT        = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
OUTPUT_FILE = os.path.join(ROOT, "backend", "data", "dataset_chequeabolivia_nuevos.csv")
MAESTRO_CSV = os.path.join(ROOT, "backend", "data", "dataset_maestro.csv")

BASE_URL = "https://chequeabolivia.bo"

CATEGORIAS = {
    "verdadera": "Verdadero",
    "enganosa":  "Engañoso",
}

KEYWORDS_ELECTORALES = [
    "elecci", "electoral", "elecciones",
    "candidat", "candidatura",
    "tse", "oep", "tribunal supremo electoral",
    "voto", "votos", "votación", "sufragio",
    "campaña", "campaña electoral",
    "partido", "partidos",
    "diputad", "senador", "asambleísta",
    "presidente", "vicepresidente",
    "mas ", " mas,", "movimiento al socialismo",
    "comunidad ciudadana", "creemos",
    "papeleta", "urna", "cómputo", "computo",
    "segunda vuelta", "primera vuelta",
    "padrón", "padron electoral",
    "habilitad", "inhabilitad",
    "reelección", "reeleccion",
    "referéndum", "referendum",
    "plebiscito",
    "alcalde", "gobernador",
    "municipio", "municipales",
    "arce", "morales", "tuto quiroga", "camacho",
    "asamblea legislativa", "congreso",
    "fraude electoral", "observadores electorales",
    "acta", "actas electorales",
]

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}


def es_electoral(texto: str) -> bool:
    t = texto.lower()
    return any(kw in t for kw in KEYWORDS_ELECTORALES)


def cargar_urls_existentes() -> set:
    """Carga todas las URLs ya presentes en el dataset maestro para evitar duplicados."""
    urls = set()
    if not os.path.exists(MAESTRO_CSV):
        return urls
    with open(MAESTRO_CSV, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if "url_origen" in row:
                urls.add(row["url_origen"].strip())
    return urls


def get_soup(url: str, retries: int = 3) -> BeautifulSoup | None:
    for intento in range(retries):
        try:
            r = requests.get(url, headers=HEADERS, timeout=20)
            if r.status_code == 200:
                return BeautifulSoup(r.text, "html.parser")
            print(f"  HTTP {r.status_code} en {url}")
        except Exception as e:
            print(f"  Error ({intento+1}/{retries}): {e}")
        time.sleep(2)
    return None


def extraer_urls_listado(categoria: str, pagina: int) -> tuple[list[tuple[str, str]], bool]:
    """Devuelve (lista de (url, titulo), hay_siguiente_pagina)."""
    url = f"{BASE_URL}/{categoria}?page={pagina}"
    soup = get_soup(url)
    if soup is None:
        return [], False

    vistos = set()
    resultados = []
    for a in soup.select("h2.node__title a, h2.title a"):
        href  = a.get("href", "").strip()
        titulo = a.get_text(strip=True)
        if not href or not titulo or len(titulo) < 10:
            continue
        if href.startswith("/"):
            href = BASE_URL + href
        if any(x in href for x in ["page=", "taxonomy", "sobrenostros", "metodologia", "podcast"]):
            continue
        if href in vistos:
            continue
        vistos.add(href)
        resultados.append((href, titulo))

    hay_siguiente = "Next page" in soup.get_text() or "Siguiente" in soup.get_text()
    return resultados, hay_siguiente


def extraer_articulo(url: str) -> dict | None:
    """Extrae título, texto completo y tags de un artículo."""
    soup = get_soup(url)
    if soup is None:
        return None

    titulo_tag = soup.find("h1")
    titulo = titulo_tag.get_text(strip=True) if titulo_tag else ""

    body = ""
    for selector in ["article .field--body", ".field--name-body", "article .node__content",
                     ".article-body", "article", "main"]:
        contenedor = soup.select_one(selector)
        if contenedor:
            for tag in contenedor.select("nav, header, footer, aside, .pager, script, style"):
                tag.decompose()
            body = contenedor.get_text(separator=" ", strip=True)
            if len(body) > 100:
                break

    NAV_TAGS = {"ChequeoDiscurso", "Investigaciones", "Podcasts", "Metodología",
                "Sobre Nosotros", "Chequeos", "Falso", "Verdadero", "Engañoso",
                "Fotomontaje", "Indeterminada"}
    tags = [a.get_text(strip=True) for a in soup.select("a[href*='taxonomy/term']")
            if a.get_text(strip=True) and a.get_text(strip=True) not in NAV_TAGS]

    return {
        "titulo": titulo,
        "texto": f"{titulo}. {body}".strip(),
        "tags":  ", ".join(tags),
    }


def main():
    print("=" * 60)
    print("  Scraper ChequeaBolivia — Filtro Electoral")
    print("=" * 60)

    urls_existentes = cargar_urls_existentes()
    print(f"URLs ya en dataset maestro: {len(urls_existentes)}")

    resultados = []
    contador = {"Verdadero": 0, "Engañoso": 0}

    for slug, categoria_label in CATEGORIAS.items():
        print(f"\n--- Scrapeando /{slug} ({categoria_label}) ---")
        pagina = 0
        articulos_vistos = 0
        articulos_pasaron = 0

        while True:
            print(f"  Página {pagina}...", end=" ", flush=True)
            items, hay_siguiente = extraer_urls_listado(slug, pagina)

            if not items:
                print("sin artículos, fin.")
                break

            nuevos_en_pagina = 0
            for url_art, titulo in items:
                articulos_vistos += 1
                if not es_electoral(titulo):
                    continue
                if url_art in urls_existentes:
                    continue

                datos = extraer_articulo(url_art)
                if datos is None:
                    continue

                texto_completo = datos["texto"]
                if not es_electoral(texto_completo):
                    continue

                resultados.append({
                    "id_registro":       None,
                    "fuente_verificadora": "chequeabolivia.bo",
                    "url_origen":        url_art,
                    "texto_crudo":       texto_completo,
                    "categoria_original": categoria_label,
                    "label":             {"Verdadero": "Baja", "Engañoso": "Media"}[categoria_label],
                })
                urls_existentes.add(url_art)
                nuevos_en_pagina += 1
                articulos_pasaron += 1
                contador[categoria_label] += 1
                time.sleep(0.5)

            print(f"{len(items)} artículos vistos, {nuevos_en_pagina} electorales nuevos.")

            if not hay_siguiente:
                print(f"  Última página alcanzada ({pagina}).")
                break

            pagina += 1
            time.sleep(1)

        print(f"  Total /{slug}: {articulos_pasaron} artículos electorales de {articulos_vistos} vistos.")

    if not resultados:
        print("\nNo se encontraron artículos electorales nuevos.")
        return

    for i, row in enumerate(resultados, start=1):
        row["id_registro"] = i

    fieldnames = ["id_registro", "fuente_verificadora", "url_origen", "texto_crudo", "categoria_original", "label"]
    with open(OUTPUT_FILE, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(resultados)

    print("\n" + "=" * 60)
    print(f"  Nuevos artículos electorales encontrados: {len(resultados)}")
    print(f"    Verdadero (Baja) : {contador['Verdadero']}")
    print(f"    Engañoso  (Media): {contador['Engañoso']}")
    print(f"  Archivo guardado en: backend/data/dataset_chequeabolivia_nuevos.csv")
    print("=" * 60)


if __name__ == "__main__":
    main()
