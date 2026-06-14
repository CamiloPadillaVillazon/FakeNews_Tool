import requests
import pandas as pd
import streamlit as st

from utils.api_client import get_history

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

    try:
        datos = get_history(limit=200)
    except requests.ConnectionError:
        st.error("No se pudo conectar al backend. ¿Está corriendo en localhost:8000?")
        return
    except Exception as e:  # noqa: BLE001
        st.error(f"Error al cargar el historial: {e}")
        return

    if not datos:
        st.info("Aún no hay análisis registrados. Ve a **Analizar** para crear el primero.")
        return

    df = pd.DataFrame(datos)

    # Metricas (sobre el total)
    total = len(df)
    n_alta = int((df["label"] == "Alta").sum())
    n_media = int((df["label"] == "Media").sum())
    n_baja = int((df["label"] == "Baja").sum())
    m = st.columns(4)
    m[0].metric("Total de análisis", total)
    m[1].metric("🔴 Alta", n_alta)
    m[2].metric("🟡 Media", n_media)
    m[3].metric("🟢 Baja", n_baja)

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
        "Fecha": df.get("timestamp"),
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
            "Fecha": st.column_config.TextColumn("Fecha", width="medium"),
            "Fuente": st.column_config.TextColumn("Fuente", width="small"),
            "Prioridad": st.column_config.TextColumn("Prioridad", width="small"),
            "Alta":  st.column_config.ProgressColumn("🔴 Alta",  format="%.0f%%", min_value=0, max_value=100),
            "Media": st.column_config.ProgressColumn("🟡 Media", format="%.0f%%", min_value=0, max_value=100),
            "Baja":  st.column_config.ProgressColumn("🟢 Baja",  format="%.0f%%", min_value=0, max_value=100),
            "Texto": st.column_config.TextColumn("Texto", width="large"),
        },
    )
