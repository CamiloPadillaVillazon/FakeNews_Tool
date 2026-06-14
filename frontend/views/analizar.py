import requests
import streamlit as st

from utils.api_client import analyze_image, analyze_text
from components.result_card import render_result_card


def _manejar_error(e: Exception):
    if isinstance(e, requests.ConnectionError):
        st.error("No se pudo conectar al backend. ¿Está corriendo en localhost:8000?")
    elif isinstance(e, requests.HTTPError):
        detalle = ""
        try:
            detalle = e.response.json().get("detail", "")
        except Exception:
            detalle = str(e)
        st.error(f"Error: {detalle or e}")
    else:
        st.error(f"Error: {e}")


def render():
    st.markdown("### 🔍 Analizar contenido")
    st.caption("Sube una imagen o pega un texto para clasificar su nivel de prioridad de verificación.")

    tipo = st.radio("Tipo de entrada", ["📝 Texto", "🖼️ Imagen"], horizontal=True, label_visibility="collapsed")

    if tipo == "🖼️ Imagen":
        archivo = st.file_uploader("Sube una imagen (JPG o PNG)", type=["jpg", "jpeg", "png"])
        if archivo is not None:
            c1, c2 = st.columns([1, 1])
            with c1:
                st.image(archivo, caption=archivo.name, use_container_width=True)
            with c2:
                st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
                if st.button("⚡ Analizar imagen", type="primary", use_container_width=True):
                    with st.spinner("Analizando contenido..."):
                        try:
                            resultado = analyze_image(archivo.getvalue(), archivo.name, archivo.type or "image/jpeg")
                            st.session_state["ultimo_resultado"] = resultado
                        except Exception as e:  # noqa: BLE001
                            _manejar_error(e)
    else:
        texto = st.text_area(
            "Texto a analizar", height=170,
            placeholder="Pega aquí el contenido a analizar...",
            label_visibility="collapsed",
        )
        if st.button("⚡ Analizar texto", type="primary"):
            if not texto.strip():
                st.warning("Ingresa un texto antes de analizar.")
            else:
                with st.spinner("Analizando contenido..."):
                    try:
                        resultado = analyze_text(texto)
                        st.session_state["ultimo_resultado"] = resultado
                    except Exception as e:  # noqa: BLE001
                        _manejar_error(e)

    if "ultimo_resultado" in st.session_state:
        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
        st.divider()
        st.markdown("#### Resultado del análisis")
        render_result_card(st.session_state["ultimo_resultado"])
