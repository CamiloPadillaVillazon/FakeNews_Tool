import json
import time

import pandas as pd
import requests

API_KEY = "AIzaSyBxw1KK60c_PSaDexEMoC9LfA0cdlqzGHI"
BASE_URL = "https://factchecktools.googleapis.com/v1alpha1/claims:search"
LANGUAGE_CODE = "es"

PUBLISHERS = [
    "boliviaverifica.bo",
    "chequeabolivia.bo",
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
    "prioridad",
]


def map_priority(textual_rating):
    if not textual_rating:
        return "Media"

    rating = textual_rating.strip().lower()

    alta_terms = [
        "falso",
        "falsa",
        "enga",
        "mentira",
        "insostenible",
    ]
    media_terms = [
        "discutible",
        "inexacto",
        "exagerado",
        "parcialmente falso",
        "verdad a medias",
    ]
    baja_terms = [
        "verdadero",
        "verdad",
        "verid",
        "consistente",
    ]

    for term in alta_terms:
        if term in rating:
            return "Alta"

    for term in media_terms:
        if term in rating:
            return "Media"

    for term in baja_terms:
        if term in rating:
            return "Baja"

    return "Media"


def fetch_data(site):
    all_claims = []
    page_token = None

    while True:
        params = {
            "key": API_KEY,
            "languageCode": LANGUAGE_CODE,
            "reviewPublisherSiteFilter": site,
        }
        if page_token:
            params["pageToken"] = page_token

        try:
            response = requests.get(BASE_URL, params=params, timeout=30)
        except requests.RequestException as exc:
            print(f"Error de conexion para '{site}': {exc}")
            break

        if response.status_code != 200:
            print(
                f"Respuesta HTTP {response.status_code} para '{site}'. "
                f"Contenido: {response.text[:200]}"
            )
            break

        try:
            payload = response.json()
        except json.JSONDecodeError as exc:
            print(f"JSON invalido para '{site}': {exc}")
            break

        claims = payload.get("claims", [])
        all_claims.extend(claims)

        page_token = payload.get("nextPageToken")
        time.sleep(1.5)
        if not page_token:
            break

    return all_claims


def process_claims(raw_claims):
    rows = []
    for claim in raw_claims:
        claim_reviews = claim.get("claimReview", [])
        if not claim_reviews:
            continue

        review = claim_reviews[0]
        review_url = review.get("url")
        if not review_url:
            continue

        rows.append(
            {
                "fecha_publicacion": review.get("reviewDate") or claim.get("claimDate"),
                "fuente_verificadora": review.get("publisher", {}).get("name"),
                "url_origen": review_url,
                "texto_crudo": claim.get("text"),
                "categoria_original": review.get("textualRating"),
                "prioridad": map_priority(review.get("textualRating")),
            }
        )

    return rows


def build_keyword_pattern(keywords):
    return "|".join(keywords)


def filter_electoral(df, keywords):
    pattern = build_keyword_pattern(keywords)
    mask = df["texto_crudo"].str.contains(pattern, case=False, na=False, regex=True)
    return df[mask]


def save_datasets(df):
    df = df[OUTPUT_COLUMNS]

    df.to_csv("dataset_electoral_maestro.csv", index=False, encoding="utf-8-sig")

    df[df["prioridad"] == "Alta"].to_csv(
        "solo_prioridad_alta.csv", index=False, encoding="utf-8-sig"
    )
    df[df["prioridad"] == "Media"].to_csv(
        "solo_prioridad_media.csv", index=False, encoding="utf-8-sig"
    )
    df[df["prioridad"] == "Baja"].to_csv(
        "solo_prioridad_baja.csv", index=False, encoding="utf-8-sig"
    )


def main():
    all_rows = []
    total_raw_claims = 0

    for site in PUBLISHERS:
        print(f"Procesando fuente: {site}...")
        raw_claims = fetch_data(site)
        total_raw_claims += len(raw_claims)
        rows = process_claims(raw_claims)
        all_rows.extend(rows)
        print(f"Encontrados: {len(rows)} registros nuevos")
        time.sleep(1.5)

    df = pd.DataFrame(all_rows)

    if df.empty:
        print("No se encontraron registros para exportar.")
        return

    df = df.drop_duplicates(subset=["url_origen"]).reset_index(drop=True)
    df = filter_electoral(df, KEYWORDS).reset_index(drop=True)
    df["id_registro"] = df.index + 1

    if df.empty:
        print("No se encontraron registros con el filtro electoral.")
        return

    save_datasets(df)

    counts = df["prioridad"].value_counts().to_dict()
    print(f"Total registros crudos descargados: {total_raw_claims}")
    print(f"Total registros filtrados: {len(df)}")
    print(
        "Distribucion por prioridad: "
        f"Alta={counts.get('Alta', 0)}, "
        f"Media={counts.get('Media', 0)}, "
        f"Baja={counts.get('Baja', 0)}"
    )


if __name__ == "__main__":
    main()
