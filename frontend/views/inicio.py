import requests
import streamlit as st

from utils.ui import hero, status_badge
from utils.api_client import health_check

_FEATURES = [
    ("📝", "Análisis de texto", "Pega cualquier afirmación o publicación y obtén su nivel de prioridad de verificación al instante."),
    ("🖼️", "Lectura de imágenes (OCR)", "Sube un meme o captura: el sistema extrae el texto automáticamente y lo clasifica."),
    ("📊", "Historial y métricas", "Consulta todos los análisis previos con filtros y visualizaciones por nivel de prioridad."),
]

_STEPS = [
    ("1", "Ingresa contenido", "Texto o imagen"),
    ("2", "Procesamiento ML", "TF-IDF + red neuronal MLP"),
    ("3", "Prioridad asignada", "Alta · Media · Baja"),
]


def render():
    hero()

    # Estado del backend
    try:
        health_check()
        status_badge(True)
    except requests.ConnectionError:
        status_badge(False, "ejecuta uvicorn en localhost:8000")
    except Exception as e:  # noqa: BLE001
        status_badge(False, str(e))

    st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)

    # Tarjetas de funcionalidades
    cols = st.columns(3)
    for col, (ic, titulo, desc) in zip(cols, _FEATURES):
        with col:
            st.markdown(
                f"""<div class="he-card">
                    <div class="ic">{ic}</div>
                    <h4>{titulo}</h4>
                    <p>{desc}</p>
                </div>""",
                unsafe_allow_html=True,
            )

    st.markdown("<div style='height:26px'></div>", unsafe_allow_html=True)
    st.markdown("#### ¿Cómo funciona?")
    scols = st.columns(3)
    for col, (n, titulo, desc) in zip(scols, _STEPS):
        with col:
            st.markdown(
                f"""<div class="he-card" style="text-align:center">
                    <div class="he-step-num">{n}</div>
                    <h4 style="margin-top:4px">{titulo}</h4>
                    <p>{desc}</p>
                </div>""",
                unsafe_allow_html=True,
            )

    st.markdown("<div style='height:22px'></div>", unsafe_allow_html=True)
    st.caption(
        "Esta herramienta **no** determina de forma autónoma si un contenido es falso o verdadero: "
        "prioriza el material para revisión humana."
    )
