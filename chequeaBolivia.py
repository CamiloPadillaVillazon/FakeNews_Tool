import re
import time
from typing import Dict, Iterable, List, Optional, Tuple
from urllib.parse import urljoin

import pandas as pd
import requests
from bs4 import BeautifulSoup


BASE_CATEGORIES: Dict[str, str] = {
	"Falso": "https://chequeabolivia.bo/falsa",
	"Verdadero": "https://chequeabolivia.bo/verdadera",
	"Engañoso": "https://chequeabolivia.bo/enganosa",
}

HEADERS = {
	"User-Agent": (
		"Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
		"AppleWebKit/537.36 (KHTML, like Gecko) "
		"Chrome/123.0.0.0 Safari/537.36"
	),
	"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
	"Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
	"Connection": "keep-alive",
}

TAG_ALLOWLIST = {"Elecciones", "Electoral", "Política", "TSE", "Votos"}

ELECTORAL_KEYWORDS = [
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
	"urnas",
	"sufragio",
	"votacion",
	"votaciones",
	"comicios",
	"tuto",
	"evo",
	"morales",
	"arce",
	"choquehuanca",
	"mesa",
	"camacho",
	"andronico",
	"mas-ipsp",
	"creemos",
	"comunidad ciudadana",
	"cc",
	"partido",
	"bancada",
	"tapiados",
	"vocal",
	"vocales",
	"democracia",
	"campaña",
	"proselitismo",
	"encuesta",
	"encuestas",
	"intencion de voto",
	"debates",
	"debate",
	"gubernamental",
	"referendum",
	"circunscripcion",
]

DATE_PATTERNS = [
	re.compile(r"\b\d{4}-\d{2}-\d{2}\b"),
	re.compile(r"\b\d{1,2}/\d{1,2}/\d{4}\b"),
	re.compile(r"\b\d{1,2}\s+\w+\s+\d{4}\b", re.IGNORECASE),
]


def clean_text(text: str) -> str:
	text = re.sub(r"\s+", " ", text or "").strip()
	return text


def extract_date(card: BeautifulSoup) -> str:
	time_tag = card.find("time")
	if time_tag:
		if time_tag.has_attr("datetime"):
			return clean_text(time_tag["datetime"])
		return clean_text(time_tag.get_text(" ", strip=True))

	date_candidates = []
	for selector in [".date", ".fecha", ".field--name-field-date", ".field--name-created"]:
		el = card.select_one(selector)
		if el:
			date_candidates.append(clean_text(el.get_text(" ", strip=True)))

	card_text = clean_text(card.get_text(" ", strip=True))
	date_candidates.append(card_text)

	for candidate in date_candidates:
		for pattern in DATE_PATTERNS:
			match = pattern.search(candidate)
			if match:
				return clean_text(match.group(0))

	return ""


def extract_title_and_url(card: BeautifulSoup, base_url: str) -> Tuple[str, str]:
	for heading in ["h1", "h2", "h3", "h4"]:
		h_tag = card.find(heading)
		if h_tag:
			link = h_tag.find("a", href=True)
			if link:
				title = clean_text(link.get_text(" ", strip=True))
				href = link.get("href", "")
				if href:
					return title, urljoin(base_url, href)

	link = card.find("a", href=True)
	if link:
		title = clean_text(link.get_text(" ", strip=True))
		href = link.get("href", "")
		if href:
			return title, urljoin(base_url, href)

	return "", ""


def collect_tag_texts(card: BeautifulSoup) -> List[str]:
	tag_texts: List[str] = []

	for el in card.find_all(True, class_=True):
		class_str = " ".join(el.get("class", []))
		if any(
			key in class_str
			for key in [
				"taxonomy",
				"field-name-field-tags",
				"field--name-field-tags",
				"posted-in",
			]
		):
			for link in el.find_all("a"):
				tag_texts.append(clean_text(link.get_text(" ", strip=True)))
			if not el.find("a"):
				tag_texts.append(clean_text(el.get_text(" ", strip=True)))

	for link in card.find_all("a", rel=True):
		if "tag" in link.get("rel", []):
			tag_texts.append(clean_text(link.get_text(" ", strip=True)))

	return [text for text in tag_texts if text]


def passes_electoral_filter(title: str, tags: Iterable[str]) -> bool:
	for tag in tags:
		if tag in TAG_ALLOWLIST:
			return True

	text_pool = " ".join([title] + list(tags))
	text_pool_lower = text_pool.lower()
	for keyword in ELECTORAL_KEYWORDS:
		if keyword in text_pool_lower:
			return True

	return False


def find_cards(soup: BeautifulSoup) -> List[BeautifulSoup]:
	selectors = [
		"article",
		".views-row",
		".node--type-fact-check",
		".node--type-factcheck",
		".node--type-noticia",
	]
	for selector in selectors:
		cards = soup.select(selector)
		if cards:
			return cards

	return []


def is_404_page(soup: BeautifulSoup, response_text: str) -> bool:
	if "404" in response_text[:500]:
		return True
	header = soup.find(["h1", "title"])
	if header and "404" in header.get_text(" ", strip=True):
		return True
	return False


def scrape_category(category_label: str, base_url: str, session: requests.Session) -> List[Dict[str, str]]:
	records: List[Dict[str, str]] = []
	page = 0
	seen_urls: set[str] = set()

	while True:
		url = f"{base_url}?_wrapper_format=html&page={page}"
		try:
			response = session.get(url, headers=HEADERS, timeout=15)
		except requests.RequestException:
			break

		if response.status_code != 200:
			break

		soup = BeautifulSoup(response.text, "html.parser")
		if is_404_page(soup, response.text):
			break

		cards = find_cards(soup)
		if not cards:
			break

		page_urls: List[str] = []

		for card in cards:
			title, article_url = extract_title_and_url(card, base_url)
			if not article_url:
				continue

			page_urls.append(article_url)

			tags = collect_tag_texts(card)
			if not passes_electoral_filter(title, tags):
				continue

			record = {
				"id_registro": None,
				"fecha_publicacion": extract_date(card),
				"fuente_verificadora": "chequeabolivia.bo",
				"url_origen": article_url,
				"texto_crudo": title,
				"categoria_original": category_label,
			}
			records.append(record)

		if not page_urls:
			break

		new_urls = [url for url in page_urls if url not in seen_urls]
		if page > 0 and not new_urls:
			break

		seen_urls.update(page_urls)

		page += 1
		time.sleep(1.5)

	return records


def main() -> None:
	session = requests.Session()
	all_records: List[Dict[str, str]] = []

	for category_label, base_url in BASE_CATEGORIES.items():
		all_records.extend(scrape_category(category_label, base_url, session))

	if not all_records:
		print("No se encontraron registros.")
		return

	df = pd.DataFrame(all_records)
	df["texto_crudo"] = df["texto_crudo"].apply(clean_text)
	df["fecha_publicacion"] = df["fecha_publicacion"].apply(clean_text)

	if "id_registro" in df.columns:
		df = df.drop(columns=["id_registro"])

	df = df.drop_duplicates(subset=["url_origen"]).reset_index(drop=True)
	df.insert(0, "id_registro", range(1, len(df) + 1))

	df = df[
		[
			"id_registro",
			"fecha_publicacion",
			"fuente_verificadora",
			"url_origen",
			"texto_crudo",
			"categoria_original",
		]
	]

	output_path = "dataset_chequeabolivia_electoral.csv"
	df.to_csv(output_path, index=False, encoding="utf-8-sig")
	print(f"Dataset generado: {output_path} ({len(df)} registros)")


if __name__ == "__main__":
	main()
