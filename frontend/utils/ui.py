"""Sistema de estilos: paleta, inyeccion de CSS y bloques de UI reutilizables.
Dark mode (dashboard) con acento institucional azul.
"""
import streamlit as st

# ---- Paleta central (importable desde otros modulos) ----
COLORS = {
    "bg":        "#0B1220",
    "surface":   "#141E33",
    "surface2":  "#111A2E",
    "border":    "#26334F",
    "primary":   "#3B82F6",
    "primary_d": "#2563EB",
    "text":      "#E6EDF7",
    "muted":     "#93A1BC",
    "alta":      "#F43F5E",
    "media":     "#F59E0B",
    "baja":      "#22C55E",
}

LABEL_META = {
    "Alta":  {"color": COLORS["alta"],  "emoji": "🔴", "titulo": "ALTA PRIORIDAD",  "sub": "Contenido probablemente Falso"},
    "Media": {"color": COLORS["media"], "emoji": "🟡", "titulo": "MEDIA PRIORIDAD", "sub": "Contenido probablemente Engañoso"},
    "Baja":  {"color": COLORS["baja"],  "emoji": "🟢", "titulo": "BAJA PRIORIDAD",  "sub": "Contenido probablemente Verdadero"},
}

_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, .stApp, [data-testid="stAppViewContainer"], [class*="css"] {
    font-family: 'Inter', -apple-system, sans-serif;
}

.stApp {
    background:
        radial-gradient(1100px 520px at 82% -8%, rgba(59,130,246,0.12), transparent 60%),
        radial-gradient(900px 480px at 0% 0%, rgba(37,99,235,0.07), transparent 55%),
        #0B1220;
}

/* Ocultar chrome por defecto de Streamlit */
#MainMenu, footer,
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"] { display: none !important; }
[data-testid="stHeader"] { background: transparent; height: 0; }

.block-container { padding-top: 1.4rem; padding-bottom: 3rem; max-width: 1140px; }

/* ---------- HERO ---------- */
.he-hero {
    position: relative;
    border: 1px solid #26334F;
    border-radius: 20px;
    padding: 34px 36px;
    margin-bottom: 22px;
    overflow: hidden;
    background:
        radial-gradient(600px 200px at 90% -40%, rgba(59,130,246,0.28), transparent 70%),
        linear-gradient(135deg, #16223D 0%, #0E1730 60%, #0B1220 100%);
    box-shadow: 0 16px 40px rgba(0,0,0,0.45);
}
.he-hero::after {
    content: ""; position: absolute; left: 0; top: 0; height: 100%; width: 5px;
    background: linear-gradient(180deg, #3B82F6, #22D3EE);
}
.he-hero h1 {
    font-size: 2.35rem; font-weight: 800; margin: 10px 0 6px 0; color: #F3F7FF;
    letter-spacing: -0.5px;
}
.he-hero p { color: #A7B6D4; font-size: 1.02rem; margin: 0; max-width: 720px; line-height: 1.5; }
.he-chip {
    display: inline-block; padding: 5px 13px; border-radius: 999px;
    background: rgba(59,130,246,0.14); border: 1px solid rgba(59,130,246,0.45);
    color: #9EC0FF; font-size: 0.8rem; font-weight: 600; letter-spacing: .3px;
}

/* ---------- CARDS ---------- */
.he-card {
    background: linear-gradient(180deg, #141E33 0%, #111A2E 100%);
    border: 1px solid #26334F; border-radius: 16px;
    padding: 22px 24px; box-shadow: 0 10px 30px rgba(0,0,0,0.35);
    height: 100%;
}
.he-card h4 { color: #F3F7FF; margin: 8px 0 6px 0; font-size: 1.05rem; font-weight: 700; }
.he-card p  { color: #93A1BC; font-size: 0.9rem; margin: 0; line-height: 1.45; }
.he-card .ic { font-size: 1.7rem; }

/* Banner de resultado */
.he-banner {
    border-radius: 16px; padding: 20px 24px; margin: 4px 0 8px 0;
    display: flex; align-items: center; gap: 16px;
    border: 1px solid var(--bc); border-left: 7px solid var(--bc);
    background: linear-gradient(135deg, var(--bg1), #111A2E 80%);
    box-shadow: 0 12px 32px rgba(0,0,0,0.4);
}
.he-banner .em { font-size: 2.1rem; line-height: 1; }
.he-banner .ti { color: var(--bc); font-weight: 800; font-size: 1.25rem; letter-spacing: .4px; margin: 0; }
.he-banner .su { color: #B7C4DE; font-size: 0.92rem; margin: 2px 0 0 0; }

/* ---------- METRIC como tarjeta ---------- */
[data-testid="stMetric"] {
    background: linear-gradient(180deg, #141E33, #111A2E);
    border: 1px solid #26334F; border-radius: 14px;
    padding: 14px 18px; box-shadow: 0 6px 20px rgba(0,0,0,0.3);
}
[data-testid="stMetricValue"] { color: #F3F7FF; font-weight: 700; }
[data-testid="stMetricLabel"] p { color: #93A1BC !important; font-weight: 600; }

/* ---------- Botones ---------- */
.stButton > button, .stDownloadButton > button {
    background: linear-gradient(135deg, #3B82F6, #2563EB); color: #fff;
    border: 0; border-radius: 11px; padding: 0.55rem 1.25rem; font-weight: 600;
    box-shadow: 0 6px 18px rgba(37,99,235,0.35); transition: all .15s ease;
}
.stButton > button:hover, .stDownloadButton > button:hover {
    transform: translateY(-1px); box-shadow: 0 12px 26px rgba(37,99,235,0.55);
    color: #fff;
}

/* ---------- Inputs ---------- */
.stTextArea textarea {
    background: #0F1830 !important; color: #E6EDF7 !important;
    border-radius: 12px !important; border: 1px solid #26334F !important;
}
[data-testid="stFileUploader"] section {
    background: #0F1830; border: 1px dashed #33446B; border-radius: 14px;
}
[data-testid="stExpander"] {
    border: 1px solid #26334F !important; border-radius: 12px !important;
    background: #111A2E !important;
}

/* Radio horizontal mas tipo "segmented" */
[role="radiogroup"] { gap: 8px; }

.he-status { font-size: 0.85rem; font-weight: 600; padding: 5px 12px; border-radius: 999px; display:inline-block; }
.he-ok   { color: #86EFAC; background: rgba(34,197,94,0.12); border: 1px solid rgba(34,197,94,0.4); }
.he-down { color: #FCA5A5; background: rgba(244,63,94,0.12); border: 1px solid rgba(244,63,94,0.4); }

hr { border-color: #26334F; }
</style>
"""


def inject_css():
    st.markdown(_CSS, unsafe_allow_html=True)


def hero(subtitle: str = "Clasificación de contenido electoral potencialmente desinformativo en tres niveles de prioridad de verificación."):
    st.markdown(
        f"""
        <div class="he-hero">
            <span class="he-chip">🗳️ Bolivia · Verificación electoral</span>
            <h1>Herramienta Electoral</h1>
            <p>{subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def status_badge(ok: bool, detail: str = ""):
    if ok:
        st.markdown('<span class="he-status he-ok">● Backend conectado</span>', unsafe_allow_html=True)
    else:
        st.markdown(
            f'<span class="he-status he-down">● Backend no disponible{(" — " + detail) if detail else ""}</span>',
            unsafe_allow_html=True,
        )
