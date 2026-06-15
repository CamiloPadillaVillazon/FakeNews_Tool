import requests
import streamlit as st

from utils.api_client import analyze_image, analyze_text
from utils.animations import render_lottie
from utils.ui import success_check
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


def _analizar(func, *args):
    """Ejecuta la llamada al backend mostrando una animacion Lottie de carga."""
    holder = st.empty()
    with holder.container():
        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
            render_lottie(
                "loading", height=150,
                fallback_html=None,  # usa el spinner tricolor CSS
            )
            st.markdown(
                "<p style='text-align:center;color:#93A1BC;font-size:.9rem'>Ejecutando pipeline de IA…</p>",
                unsafe_allow_html=True,
            )
    try:
        resultado = func(*args)
        st.session_state["ultimo_resultado"] = resultado
        st.session_state["analisis_ok"] = True
    except Exception as e:  # noqa: BLE001
        st.session_state.pop("analisis_ok", None)
        _manejar_error(e)
    finally:
        holder.empty()


def render():
    st.markdown("### 🔍 Analizar contenido")
    st.caption("Sube una imagen o pega un texto para clasificar su nivel de prioridad de verificación.")

    tipo = st.radio("Tipo de entrada", ["📝 Texto", "🖼️ Imagen"], horizontal=True, label_visibility="collapsed")

    if tipo == "🖼️ Imagen":
        st.markdown("#### Sube una imagen")
        col1, col2 = st.columns([1, 1])
        with col1:
            archivo = st.file_uploader("JPG o PNG", type=["jpg", "jpeg", "png"], label_visibility="collapsed")
        with col2:
            if archivo is None:
                render_lottie(
                    "upload", height=120,
                    fallback_html="<p style='text-align:center;font-size:2.4rem;margin:0'>📤</p>"
                    "<p style='text-align:center;color:#93A1BC;font-size:.85rem'>Arrastra tu imagen aquí</p>",
                )
        if archivo is not None:
            st.image(archivo, caption=archivo.name, use_container_width=True)
            if st.button("⚡ Analizar imagen", type="primary"):
                _analizar(analyze_image, archivo.getvalue(), archivo.name, archivo.type or "image/jpeg")
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
                _analizar(analyze_text, texto)

    if "ultimo_resultado" in st.session_state:
        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
        st.divider()
        st.markdown("#### Resultado del análisis")
        if st.session_state.pop("analisis_ok", None):
            c1, c2, c3 = st.columns([2, 1, 2])
            with c2:
                render_lottie(
                    "success", height=90,
                    fallback_html="<div class='he-check'>✓</div>",
                )
        render_result_card(st.session_state["ultimo_resultado"])
