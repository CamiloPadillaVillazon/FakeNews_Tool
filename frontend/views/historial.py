import requests
import pandas as pd
import streamlit as st

from utils.api_client import get_history
from utils.animations import render_lottie
from utils.ui import skeleton_rows, metric_card, COLORS

_EMOJI = {"Alta": "🔴 Alta", "Media": "🟡 Media", "Baja": "🟢 Baja"}


def render():
    top = st.columns([3, 1, 1])
    with top[0]:
        st.markdown("### 📋 Historial de análisis")
    with top[1]:
        filtro = st.selectbox("Prioridad", ["Todas", "Alta", "Media", "Baja"], label_visibility="collapsed")
    with top[2]:
        if st.button("🔄 Actualizar", use_container_width=True):
            st.rerun()

    cargando = st.empty()
    with cargando.container():
        skeleton_rows(6)
    try:
        datos = get_history(limit=200)
    except requests.ConnectionError:
        cargando.empty()
        st.error("No se pudo conectar al backend. ¿Está corriendo en localhost:8000?")
        return
    except Exception as e:  # noqa: BLE001
        cargando.empty()
        st.error(f"Error al cargar el historial: {e}")
        return
    finally:
        cargando.empty()

    if not datos:
        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
            render_lottie(
                "empty", height=170,
                fallback_html="<p style='text-align:center;font-size:2.6rem;margin:0'>🗂️</p>",
            )
        st.info("Aún no hay análisis registrados. Ve a **Analizar** para crear el primero.")
        return

    df = pd.DataFrame(datos)

    # Metricas (sobre el total)
    total = len(df)
    n_alta = int((df["label"] == "Alta").sum())
    n_media = int((df["label"] == "Media").sum())
    n_baja = int((df["label"] == "Baja").sum())
    m = st.columns(4)
    m[0].markdown(metric_card("Total de análisis", total, COLORS["primary"]), unsafe_allow_html=True)
    m[1].markdown(metric_card("🔴 Alta", n_alta, COLORS["alta"]), unsafe_allow_html=True)
    m[2].markdown(metric_card("🟡 Media", n_media, COLORS["media"]), unsafe_allow_html=True)
    m[3].markdown(metric_card("🟢 Baja", n_baja, COLORS["baja"]), unsafe_allow_html=True)

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    # Filtro
    if filtro != "Todas":
        df = df[df["label"] == filtro]
    if df.empty:
        st.info(f"No hay análisis con prioridad {filtro}.")
        return

    # Preparar tabla de presentacion
    vista = pd.DataFrame({
        "id": df.get("id"),
        "Fuente": df.get("fuente"),
        "Prioridad": df["label"].map(lambda x: _EMOJI.get(x, x)),
        "Alta": (df.get("score_alta", 0) * 100),
        "Media": (df.get("score_media", 0) * 100),
        "Baja": (df.get("score_baja", 0) * 100),
        "Texto": df.get("texto"),
    })

    st.dataframe(
        vista,
        use_container_width=True,
        hide_index=True,
        column_config={
            "id": st.column_config.NumberColumn("ID", width="small"),
            "Fuente": st.column_config.TextColumn("Fuente", width="small"),
            "Prioridad": st.column_config.TextColumn("Prioridad", width="small"),
            "Alta":  st.column_config.ProgressColumn("🔴 Alta",  format="%.0f%%", min_value=0, max_value=100),
            "Media": st.column_config.ProgressColumn("🟡 Media", format="%.0f%%", min_value=0, max_value=100),
            "Baja":  st.column_config.ProgressColumn("🟢 Baja",  format="%.0f%%", min_value=0, max_value=100),
            "Texto": st.column_config.TextColumn("Texto", width="large"),
        },
    )
