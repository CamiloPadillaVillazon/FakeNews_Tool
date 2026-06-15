"""Animaciones Lottie con fallback CSS (adaptado a dark mode + acento tricolor Bolivia).

Si una URL de Lottie falla o no existe, se muestra un fallback CSS para que la UI
nunca quede "rota". El resultado de la descarga se cachea para no reintentar URLs
muertas en cada rerun de Streamlit.
"""
import requests
import streamlit as st

try:
    from streamlit_lottie import st_lottie
    _LOTTIE_OK = True
except Exception:  # pragma: no cover - si la lib no esta instalada
    _LOTTIE_OK = False


@st.cache_data(show_spinner=False, ttl=3600)
def load_lottie_url(url: str) -> dict | None:
    """Carga una animacion Lottie desde URL. Retorna None si falla (cacheado)."""
    if not url:
        return None
    try:
        r = requests.get(url, timeout=4)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return None


# URLs de animaciones Lottie. Vacias por defecto -> se usan los fallbacks CSS
# (animados, sin latencia de red ni dependencia externa). Para activar Lottie real:
# ir a lottiefiles.com/free-animations, "Get URL" del .json y pegar la URL aqui.
LOTTIE_URLS = {
    "loading": "",
    "success": "",
    "upload":  "",
    "empty":   "",
    "search":  "",
}


def render_lottie(key: str, height: int = 180, fallback_html: str = ""):
    """Renderiza una animacion Lottie. Si falla, muestra fallback_html o un spinner CSS."""
    animation = load_lottie_url(LOTTIE_URLS.get(key, "")) if _LOTTIE_OK else None
    if animation and _LOTTIE_OK:
        st_lottie(animation, height=height, key=f"lottie_{key}")
        return
    if fallback_html:
        st.markdown(fallback_html, unsafe_allow_html=True)
    else:
        css_spinner()


def css_spinner(label: str = ""):
    """Loader CSS de puntos tricolor (Bolivia) sobre dark mode, como fallback de Lottie."""
    extra = (
        f"<p style='text-align:center;color:#93A1BC;font-size:.9rem;margin-top:.2rem'>{label}</p>"
        if label else ""
    )
    st.markdown(
        f"""
        <div class="he-dots"><span></span><span></span><span></span></div>
        {extra}
        """,
        unsafe_allow_html=True,
    )
