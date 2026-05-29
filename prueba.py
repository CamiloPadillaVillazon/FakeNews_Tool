import time

import pandas as pd
import requests
from bs4 import BeautifulSoup

PUBLISHERS = [
    "boliviaverifica.bo",
]

CATEGORIES = [
    "falso",
    "verdadero",
    "enganosa",
]

KEYWORDS = [
    "eleccion",
    "elecciones",
    "tse",
    "fraude",
    "votos",
    "voto",
    "papeleta",
    "candidatos",
    "candidato",
    "padron",
    "computo",
    "acta",
]

OUTPUT_COLUMNS = [
    "id_registro",
    "fecha_publicacion",
    "fuente_verificadora",
    "url_origen",
    "texto_crudo",
    "categoria_original",
]

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
}


def clean_text(value):
    if not value:
        return ""
    return " ".join(value.split())


def build_keyword_pattern(keywords):
    return "|".join(keywords)


def has_electoral_badge(article):
    badge = article.select_one("a.covernews-categories")
    if not badge:
        return False
    badge_text = clean_text(badge.get_text(" ")).lower()
    badge_href = badge.get("href", "").lower()
    if "elecciones" in badge_text:
        return True
    return "/category/elecciones" in badge_href


def matches_electoral_keywords(text, keywords):
    if not text:
        return False
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in keywords)


def request_page(url):
    try:
        response = requests.get(url, headers=HEADERS, timeout=30)
        return response
    except requests.RequestException as exc:
        print(f"Error de conexion para {url}: {exc}")
        return None


def extract_article_link(article):
    link = article.find("a", href=True)
    return link["href"] if link else ""


def extract_article_title(article):
    title_node = article.find(["h1", "h2", "h3"]) or article.find("a")
    return clean_text(title_node.get_text(" ")) if title_node else ""


def extract_article_date(article):
    time_node = article.find("time")
    if time_node:
        return time_node.get("datetime") or clean_text(time_node.get_text(" "))
    date_node = article.select_one(".entry-date, .post-date, .covernews-post-date")
    return clean_text(date_node.get_text(" ")) if date_node else ""


# IDs de clasificacion en Bolivia Verifica
BV_CATEGORIAS_MAP = {
    "falso": 2,
    "verdadero": 4,
    "enganoso": 6,
    "enganosa": 6
}
BV_ELECCIONES_ID = 458

def scrape_bolivia_verifica(site, category_slug, category_label):
    rows = []
    page = 1
    cat_id = BV_CATEGORIAS_MAP.get(category_slug.lower())
    if not cat_id:
        return rows

    while True:
        url = f"https://{site}/wp-json/wp/v2/posts?categories={cat_id}&per_page=100&page={page}"
        response = request_page(url)

        if not response or response.status_code != 200:
            break

        data = response.json()
        if not data:
            break

        for post in data:
            title_html = post.get("title", {}).get("rendered", "")
            title = clean_text(BeautifulSoup(title_html, "html.parser").get_text())
            if not title:
                continue

            categories = post.get("categories", [])
            badge_match = (BV_ELECCIONES_ID in categories)
            keyword_match = matches_electoral_keywords(title, KEYWORDS)

            if not badge_match and not keyword_match:
                continue

            link = post.get("link", "")
            date_str = post.get("date", "")

            rows.append(
                {
                    "fecha_publicacion": date_str,
                    "fuente_verificadora": site,
                    "url_origen": link,
                    "texto_crudo": title,
                    "categoria_original": category_label,
                }
            )

        page += 1
        time.sleep(1.0)

    return rows


def normalize_category_label(slug):
    if slug == "enganoso":
        return "Enganoso"
    if slug == "enganosa":
        return "Enganosa"
    if slug == "falso":
        return "Falso"
    if slug == "verdadero":
        return "Verdadero"
    return slug.title()


def scrape_site(site):
    rows = []

    for slug in CATEGORIES:
        category_slug = slug
        category_label = normalize_category_label(category_slug)
        print(f"Procesando {site} categoria {category_slug}...")

        rows.extend(scrape_bolivia_verifica(site, category_slug, category_label))

    return rows


def save_dataset(df):
    df = df[OUTPUT_COLUMNS]
    df.to_csv("dataset_electoral_maestro.csv", index=False, encoding="utf-8-sig")


def main():
    all_rows = []

    for site in PUBLISHERS:
        all_rows.extend(scrape_site(site))

    df = pd.DataFrame(all_rows)

    if df.empty:
        print("No se encontraron registros para exportar.")
        return

    df = df.drop_duplicates(subset=["url_origen"]).reset_index(drop=True)
    df["id_registro"] = df.index + 1

    save_dataset(df)
    print(f"Total de registros exportados: {len(df)}")


if __name__ == "__main__":
    main()