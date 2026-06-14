import streamlit as st
from streamlit_option_menu import option_menu

from utils.ui import inject_css, COLORS
from views import inicio, analizar, historial

st.set_page_config(
    page_title="Herramienta Electoral",
    page_icon="🗳️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

inject_css()

selected = option_menu(
    menu_title=None,
    options=["Inicio", "Analizar", "Historial"],
    icons=["house-door", "search", "clock-history"],
    orientation="horizontal",
    default_index=0,
    styles={
        "container": {
            "padding": "6px", "background-color": "#0F1830",
            "border-radius": "14px", "border": "1px solid #26334F",
            "margin-bottom": "18px",
        },
        "icon": {"color": "#9EC0FF", "font-size": "16px"},
        "nav-link": {
            "color": "#9FB0CC", "font-size": "15px", "font-weight": "600",
            "padding": "11px 20px", "border-radius": "10px",
            "--hover-color": "#1B2742",
        },
        "nav-link-selected": {
            "background": "linear-gradient(135deg, #3B82F6, #2563EB)",
            "color": "#ffffff", "font-weight": "700",
        },
    },
)

if selected == "Inicio":
    inicio.render()
elif selected == "Analizar":
    analizar.render()
elif selected == "Historial":
    historial.render()
