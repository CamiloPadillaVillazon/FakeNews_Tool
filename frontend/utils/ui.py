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
    # Acento tricolor Bolivia (adaptado a dark mode)
    "bo_rojo":     "#E5443B",
    "bo_amarillo": "#F2C744",
    "bo_verde":    "#1FA763",
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

.stApp { background: #0B1220; }

/* Aurora animada de fondo (capa fija detras del contenido) */
[data-testid="stAppViewContainer"]::before {
    content: ""; position: fixed; inset: -25%; z-index: 0; pointer-events: none;
    background:
        radial-gradient(620px 620px at 18% 28%, rgba(59,130,246,0.22), transparent 60%),
        radial-gradient(560px 560px at 82% 18%, rgba(34,211,238,0.16), transparent 60%),
        radial-gradient(560px 560px at 62% 82%, rgba(31,167,99,0.13), transparent 60%),
        radial-gradient(520px 520px at 30% 88%, rgba(244,63,94,0.10), transparent 60%);
    animation: aurora 22s ease-in-out infinite alternate;
    filter: blur(8px);
}
.block-container, header, [data-testid="stHeader"] { position: relative; z-index: 1; }

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
    background: linear-gradient(180deg, #E5443B 0 33%, #F2C744 33% 66%, #1FA763 66%);
}
/* Resplandor orbital dentro del hero */
.he-hero::before {
    content: ""; position: absolute; right: -80px; top: -120px;
    width: 320px; height: 320px; border-radius: 50%;
    background: radial-gradient(circle, rgba(59,130,246,0.35), transparent 65%);
    animation: floatGlow 9s ease-in-out infinite; pointer-events: none;
}
.he-hero h1 {
    font-size: 2.6rem; font-weight: 800; margin: 12px 0 8px 0; letter-spacing: -0.6px;
    background: linear-gradient(90deg, #FFFFFF, #9EC0FF, #22D3EE, #9EC0FF, #FFFFFF);
    background-size: 220% auto;
    -webkit-background-clip: text; background-clip: text;
    -webkit-text-fill-color: transparent; color: transparent;
    animation: textShine 6s linear infinite;
}
.he-hero p { color: #A7B6D4; font-size: 1.04rem; margin: 0; max-width: 720px; line-height: 1.55; position: relative; }
.he-chip {
    display: inline-block; padding: 6px 14px; border-radius: 999px;
    background: rgba(59,130,246,0.14); border: 1px solid rgba(59,130,246,0.45);
    color: #9EC0FF; font-size: 0.8rem; font-weight: 600; letter-spacing: .3px;
    position: relative;
    animation: floatY 4.5s ease-in-out infinite, glowChip 3s ease-in-out infinite;
}

/* ---------- CARDS ---------- */
.he-card {
    position: relative; overflow: hidden;
    background: linear-gradient(180deg, #141E33 0%, #111A2E 100%);
    border: 1px solid #26334F; border-radius: 16px;
    padding: 22px 24px; box-shadow: 0 10px 30px rgba(0,0,0,0.35);
    height: 100%;
    transition: transform .25s ease, box-shadow .25s ease, border-color .25s ease;
}
.he-card::before {
    content: ""; position: absolute; top: 0; left: 0; right: 0; height: 3px;
    background: linear-gradient(90deg, #3B82F6, #22D3EE, #1FA763);
    transform: scaleX(0); transform-origin: left; transition: transform .35s ease;
}
.he-card:hover {
    transform: translateY(-6px);
    border-color: rgba(59,130,246,0.55);
    box-shadow: 0 22px 48px rgba(0,0,0,0.5), 0 0 0 1px rgba(59,130,246,0.25);
}
.he-card:hover::before { transform: scaleX(1); }
.he-card:hover .ic { animation: iconPop .5s ease; }
.he-card h4 { color: #F3F7FF; margin: 8px 0 6px 0; font-size: 1.05rem; font-weight: 700; }
.he-card p  { color: #93A1BC; font-size: 0.9rem; margin: 0; line-height: 1.45; }
.he-card .ic { font-size: 1.9rem; display: inline-block; }

/* Banner de resultado */
.he-banner {
    border-radius: 16px; padding: 20px 24px; margin: 4px 0 8px 0;
    display: flex; align-items: center; gap: 16px;
    border: 1px solid var(--bc); border-left: 7px solid var(--bc);
    background: linear-gradient(135deg, var(--bg1), #111A2E 80%);
    box-shadow: 0 12px 32px rgba(0,0,0,0.4);
    animation: popIn .5s cubic-bezier(.18,.89,.32,1.28) both, bannerGlow 2.6s ease-in-out infinite .5s;
}
.he-banner .em { font-size: 2.3rem; line-height: 1; animation: floatY 3s ease-in-out infinite; }
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
    position: relative; overflow: hidden;
    background: linear-gradient(135deg, #3B82F6, #2563EB); color: #fff;
    border: 0; border-radius: 11px; padding: 0.58rem 1.35rem; font-weight: 700;
    box-shadow: 0 6px 18px rgba(37,99,235,0.35); transition: all .18s ease;
}
.stButton > button::after, .stDownloadButton > button::after {
    content: ""; position: absolute; top: 0; left: -130%; width: 60%; height: 100%;
    background: linear-gradient(120deg, transparent, rgba(255,255,255,0.45), transparent);
    transform: skewX(-20deg);
}
.stButton > button:hover, .stDownloadButton > button:hover {
    transform: translateY(-2px); box-shadow: 0 14px 30px rgba(37,99,235,0.6); color: #fff;
}
.stButton > button:hover::after, .stDownloadButton > button:hover::after {
    animation: shine .75s ease;
}
.stButton > button:active, .stDownloadButton > button:active { transform: scale(.97); }

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

/* ============ ANIMACIONES (keyframes) ============ */
@keyframes fadeSlideUp { from { opacity:0; transform:translateY(18px); } to { opacity:1; transform:translateY(0); } }
@keyframes fadeIn      { from { opacity:0; } to { opacity:1; } }
@keyframes expandBar   { from { width:0%; } to { width:var(--target-width); } }
@keyframes pulse       { 0%,100% { opacity:1; transform:scale(1); } 50% { opacity:.4; transform:scale(.7); } }
@keyframes shimmer     { 0% { background-position:-200% 0; } 100% { background-position:200% 0; } }
@keyframes bounceIn    { 0% { transform:scale(.85); opacity:0; } 60% { transform:scale(1.05); opacity:1; } 100% { transform:scale(1); opacity:1; } }
@keyframes spin        { to { transform:rotate(360deg); } }
@keyframes aurora      { 0% { transform:translate(0,0) rotate(0deg); } 50% { transform:translate(4%,3%) rotate(8deg); } 100% { transform:translate(-3%,-2%) rotate(-6deg); } }
@keyframes textShine   { to { background-position:220% center; } }
@keyframes floatY      { 0%,100% { transform:translateY(0); } 50% { transform:translateY(-6px); } }
@keyframes floatGlow   { 0%,100% { transform:translate(0,0) scale(1); opacity:.8; } 50% { transform:translate(-20px,18px) scale(1.12); opacity:1; } }
@keyframes glowChip    { 0%,100% { box-shadow:0 0 0 0 rgba(59,130,246,0); } 50% { box-shadow:0 0 18px 2px rgba(59,130,246,0.45); } }
@keyframes shine       { from { left:-130%; } to { left:130%; } }
@keyframes popIn       { 0% { opacity:0; transform:scale(.9) translateY(10px); } 100% { opacity:1; transform:scale(1) translateY(0); } }
@keyframes bannerGlow  { 0%,100% { box-shadow:0 12px 32px rgba(0,0,0,0.4), 0 0 0 0 var(--bc); } 50% { box-shadow:0 12px 32px rgba(0,0,0,0.4), 0 0 26px 1px var(--bc); } }
@keyframes iconPop     { 0% { transform:scale(1); } 40% { transform:scale(1.35) rotate(-8deg); } 100% { transform:scale(1); } }
@keyframes barFlow     { from { background-position:-180% 0; } to { background-position:180% 0; } }
@keyframes dotBounce   { 0%,80%,100% { transform:scale(.5); opacity:.4; } 40% { transform:scale(1); opacity:1; } }
@keyframes scanY       { 0% { top:-10%; } 100% { top:110%; } }

/* Aplicar entrada animada a banner, cards y metrics */
.he-card   { animation: fadeSlideUp .5s ease-out both; }
[data-testid="stMetric"] { animation: popIn .5s ease-out both; transition: transform .2s ease, box-shadow .2s ease; }
[data-testid="stMetric"]:hover { transform: translateY(-4px); box-shadow: 0 16px 34px rgba(0,0,0,0.45); }

/* ---------- Franja tricolor Bolivia (con brillo deslizante) ---------- */
.he-tricolor {
    position: relative; height: 6px; width: 100%; border-radius: 999px; margin-top: 18px;
    overflow: hidden;
    background: linear-gradient(to right,
        #E5443B 0 33.33%, #F2C744 33.33% 66.66%, #1FA763 66.66% 100%);
    box-shadow: 0 2px 18px rgba(0,0,0,0.4), 0 0 14px rgba(242,199,68,0.3);
}
.he-tricolor::after {
    content: ""; position: absolute; top: 0; left: 0; width: 40%; height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.7), transparent);
    animation: shine 3.2s ease-in-out infinite;
}

/* ---------- Barras de probabilidad animadas ---------- */
.he-bar-wrap { margin: 12px 0; animation: fadeSlideUp .5s ease-out both; }
.he-bar-row  { display:flex; justify-content:space-between; font-size:.86rem; color:#9FB0CC; margin-bottom:6px; font-weight:600; }
.he-bar-row .val { color:#E6EDF7; }
.he-bar-track {
    height: 15px; background:#0F1830; border:1px solid #26334F;
    border-radius: 999px; overflow: hidden;
}
.he-bar-fill {
    position: relative; height: 100%; border-radius: 999px; width: 0;
    animation: expandBar 1.15s cubic-bezier(.34,1.4,.6,1) forwards;
    box-shadow: 0 0 14px var(--gl);
}
.he-bar-fill::after {
    content: ""; position: absolute; inset: 0; border-radius: 999px;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.45), transparent);
    background-size: 180% 100%;
    animation: barFlow 2.2s linear infinite;
}

/* ---------- Loader de puntos tricolor (fallback Lottie carga) ---------- */
.he-dots { display:flex; justify-content:center; gap:11px; padding:1.2rem 0; }
.he-dots span { width:15px; height:15px; border-radius:50%; animation: dotBounce 1.2s ease-in-out infinite; }
.he-dots span:nth-child(1) { background:#E5443B; animation-delay:0s; }
.he-dots span:nth-child(2) { background:#F2C744; animation-delay:.18s; }
.he-dots span:nth-child(3) { background:#1FA763; animation-delay:.36s; }

/* ---------- Spinner tricolor (alternativa) ---------- */
.he-tricolor-spinner {
    width: 54px; height: 54px; border-radius: 50%;
    border: 5px solid #1B2742;
    border-top-color: #E5443B; border-right-color: #F2C744; border-bottom-color: #1FA763;
    animation: spin .8s linear infinite;
}

/* ---------- Checkmark de exito ---------- */
.he-check {
    width: 60px; height: 60px; margin: 0 auto; border-radius: 50%;
    background: rgba(31,167,99,.15); border: 2px solid #1FA763;
    display:flex; align-items:center; justify-content:center; color:#22C55E; font-size:1.9rem;
    box-shadow: 0 0 22px rgba(31,167,99,0.5);
    animation: bounceIn .55s ease-out both;
}

/* ---------- Skeleton loader ---------- */
.he-skeleton {
    background: linear-gradient(90deg, #141E33 25%, #1C2A45 50%, #141E33 75%);
    background-size: 200% 100%; animation: shimmer 1.4s infinite;
    border-radius: 8px; height: 16px; margin: 9px 0;
}

/* Punto de estado pulsante */
.he-status::before {
    content:""; display:inline-block; width:8px; height:8px; border-radius:50%;
    margin-right:7px; vertical-align:middle; animation: pulse 1.6s ease-in-out infinite;
}
.he-ok::before   { background:#22C55E; box-shadow:0 0 10px #22C55E; }
.he-down::before { background:#F43F5E; box-shadow:0 0 10px #F43F5E; }

/* ============ MAS ANIMACIONES ============ */
@keyframes growBar   { to { height:68%; } }
@keyframes ring      { 0% { transform:scale(.75); opacity:.6; } 100% { transform:scale(1.6); opacity:0; } }
@keyframes stepPulse { 0%,100% { box-shadow:0 0 0 0 rgba(59,130,246,.45); } 50% { box-shadow:0 0 0 12px rgba(59,130,246,0); } }
@keyframes floatUp   { 0% { transform:translateY(10px); opacity:0; } 20% { opacity:.85; } 100% { transform:translateY(-130px); opacity:0; } }
@keyframes navGlow   { 0%,100% { box-shadow:0 4px 14px rgba(37,99,235,.35); } 50% { box-shadow:0 6px 24px rgba(59,130,246,.7); } }
@keyframes dividerFlow { 0% { background-position:-200% 0; } 100% { background-position:200% 0; } }

/* Entrada suave del contenido al cambiar de vista */
section.main .block-container { animation: fadeIn .45s ease-out; }

/* Titulos de seccion (###) con acento animado que crece */
.block-container h3 { position: relative; padding-left: 15px; }
.block-container h3::before {
    content:""; position:absolute; left:0; top:50%; transform:translateY(-50%);
    width:5px; height:0; border-radius:3px;
    background:linear-gradient(180deg,#3B82F6,#22D3EE);
    box-shadow:0 0 10px rgba(59,130,246,.6);
    animation: growBar .5s ease .1s forwards;
}

/* Iconos de las cards flotan suavemente siempre */
.he-card .ic { animation: floatY 3.4s ease-in-out infinite; }

/* Numero de paso (Inicio) con pulso */
.he-step-num {
    font-size:1.6rem; font-weight:800; color:#9EC0FF;
    width:56px; height:56px; margin:0 auto 8px; border-radius:50%;
    display:flex; align-items:center; justify-content:center;
    background:rgba(59,130,246,0.12); border:1px solid rgba(59,130,246,0.45);
    animation: stepPulse 2.4s ease-in-out infinite;
}

/* Emoji del banner con anillo expansivo */
.he-banner .em { position: relative; }
.he-banner .em::after {
    content:""; position:absolute; inset:-7px; border-radius:50%;
    border:2px solid var(--bc); opacity:.5;
    animation: ring 1.8s ease-out infinite;
}

/* Particulas flotantes del hero */
.he-particles { position:absolute; inset:0; overflow:hidden; pointer-events:none; }
.he-particles i {
    position:absolute; bottom:-10px; width:7px; height:7px; border-radius:50%;
    background:rgba(158,192,255,0.55); box-shadow:0 0 8px rgba(120,170,255,0.6);
    animation: floatUp linear infinite;
}

/* Navbar: item activo con glow pulsante */
.nav-link.active { animation: navGlow 2.6s ease-in-out infinite; }

/* Uploader y expander con hover reactivo */
[data-testid="stFileUploader"] section {
    transition: border-color .2s, box-shadow .2s, transform .2s;
}
[data-testid="stFileUploader"] section:hover {
    border-color:#3B82F6 !important; box-shadow:0 0 0 3px rgba(59,130,246,0.15);
    transform: translateY(-2px);
}
[data-testid="stExpander"] { transition: border-color .2s; }
[data-testid="stExpander"]:hover { border-color: rgba(59,130,246,0.55) !important; }

/* Radio: leve elevacion al hover */
[role="radiogroup"] label { transition: transform .15s ease; }
[role="radiogroup"] label:hover { transform: translateY(-1px); }

/* Divider con flujo de luz */
hr {
    border: 0; height: 2px;
    background: linear-gradient(90deg, transparent, #3B82F6, #22D3EE, transparent);
    background-size: 200% 100%; animation: dividerFlow 3s linear infinite;
}

/* ============ CONTADOR ANIMADO DE PORCENTAJES ============ */
/* Cuenta de 0 hasta --target usando @property (Chrome/Edge). Sin JS. */
@property --pct { syntax: '<integer>'; initial-value: 0; inherits: false; }
@keyframes countUp { from { --pct: 0; } to { --pct: var(--target, 0); } }
.he-num {
    counter-reset: pct var(--pct);
    animation: countUp 1.25s cubic-bezier(.2,.7,.2,1) forwards;
    font-variant-numeric: tabular-nums;
}
.he-num::after { content: counter(pct) '%'; }

/* Numero grande (gauge) */
.he-num-lg { font-weight: 800; line-height: 1; text-align: center; margin: 6px 0 2px; }

/* Contador entero SIN % (conteos del historial) */
@property --cnt { syntax: '<integer>'; initial-value: 0; inherits: false; }
@keyframes countUpN { from { --cnt: 0; } to { --cnt: var(--target, 0); } }
.he-count {
    counter-reset: cnt var(--cnt);
    animation: countUpN 1.1s cubic-bezier(.2,.7,.2,1) forwards;
    font-variant-numeric: tabular-nums;
}
.he-count::after { content: counter(cnt); }

/* Tarjeta-metrica personalizada (con contador) */
.he-metric {
    background: linear-gradient(180deg, #141E33, #111A2E);
    border: 1px solid #26334F; border-radius: 14px;
    padding: 16px 18px; box-shadow: 0 6px 20px rgba(0,0,0,0.3);
    text-align: center; height: 100%;
    animation: popIn .5s ease-out both;
    transition: transform .2s ease, box-shadow .2s ease, border-color .2s ease;
}
.he-metric:hover {
    transform: translateY(-4px); border-color: rgba(59,130,246,0.5);
    box-shadow: 0 16px 34px rgba(0,0,0,0.45);
}
.he-metric-val { font-size: 1.9rem; font-weight: 800; line-height: 1; }
.he-metric-lbl { color: #93A1BC; font-size: .82rem; font-weight: 600; margin-top: 6px; }
</style>
"""


# Particulas flotantes del hero (left%, tamaño px, duracion s, retraso s)
_PARTICLE_SPECS = [
    (8, 6, 7, 0.0), (20, 4, 9, 1.4), (33, 8, 6, 0.6), (46, 5, 8, 2.1),
    (58, 7, 7.5, 0.9), (70, 4, 10, 1.8), (82, 6, 6.5, 0.3), (92, 5, 8.5, 2.6),
]
_PARTICLES = '<div class="he-particles">' + "".join(
    f'<i style="left:{l}%;width:{s}px;height:{s}px;animation-duration:{d}s;animation-delay:{dl}s"></i>'
    for (l, s, d, dl) in _PARTICLE_SPECS
) + "</div>"


def inject_css():
    st.markdown(_CSS, unsafe_allow_html=True)


def hero(subtitle: str = "Clasificación de contenido electoral potencialmente desinformativo en tres niveles de prioridad de verificación."):
    st.markdown(
        f"""
        <div class="he-hero">
            {_PARTICLES}
            <span class="he-chip">🗳️ Bolivia · Verificación electoral</span>
            <h1>Herramienta Electoral</h1>
            <p>{subtitle}</p>
            <div class="he-tricolor"></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def animated_bars(scores: dict):
    """Barras de probabilidad animadas (crecen desde 0) con color por clase."""
    orden = [
        ("Alta",  "Falso",    COLORS["alta"]),
        ("Media", "Engañoso", COLORS["media"]),
        ("Baja",  "Verdadero", COLORS["baja"]),
    ]
    filas = ""
    for clave, glosa, color in orden:
        pct = float(scores.get(clave, 0.0)) * 100
        filas += (
            f"<div class='he-bar-wrap'>"
            f"<div class='he-bar-row'><span>{clave} ({glosa})</span>"
            f"<span class='val he-num' style='--target:{int(round(pct))}'></span></div>"
            f"<div class='he-bar-track'>"
            f"<div class='he-bar-fill' style='--target-width:{pct:.1f}%;--gl:{color}66;"
            f"background:{color}'></div></div></div>"
        )
    st.markdown(filas, unsafe_allow_html=True)


def count_number(pct: float, color: str = "#F3F7FF", size: str = "2.7rem"):
    """Numero grande de porcentaje con conteo animado de 0 a pct."""
    st.markdown(
        f"<div class='he-num he-num-lg' style='--target:{int(round(pct))};color:{color};font-size:{size}'></div>",
        unsafe_allow_html=True,
    )


def metric_card(label: str, value: int, color: str = "#F3F7FF") -> str:
    """HTML de una tarjeta-metrica con contador entero animado (sin %)."""
    return (
        "<div class='he-metric'>"
        f"<div class='he-metric-val he-count' style='--target:{int(value)};color:{color}'></div>"
        f"<div class='he-metric-lbl'>{label}</div></div>"
    )


def skeleton_rows(n: int = 5):
    """Filas skeleton (shimmer) mientras carga contenido."""
    st.markdown("".join("<div class='he-skeleton'></div>" for _ in range(n)), unsafe_allow_html=True)


def success_check():
    """Checkmark de exito (fallback / refuerzo visual)."""
    st.markdown("<div class='he-check'>✓</div>", unsafe_allow_html=True)


def status_badge(ok: bool, detail: str = ""):
    if ok:
        st.markdown('<span class="he-status he-ok">Backend conectado</span>', unsafe_allow_html=True)
    else:
        st.markdown(
            f'<span class="he-status he-down">Backend no disponible{(" — " + detail) if detail else ""}</span>',
            unsafe_allow_html=True,
        )
