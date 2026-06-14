import streamlit as st
import plotly.graph_objects as go

from utils.ui import COLORS, LABEL_META

_PLOTLY_CONF = {"displayModeBar": False, "staticPlot": False}


def _confidence_gauge(score: float, color: str) -> go.Figure:
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=round(score * 100, 1),
            number={"suffix": "%", "font": {"size": 42, "color": "#F3F7FF", "family": "Inter"}},
            gauge={
                "axis": {"range": [0, 100], "tickwidth": 1, "tickcolor": "#3A4B5A",
                         "tickfont": {"color": "#8B98AE", "size": 11}},
                "bar": {"color": color, "thickness": 0.30},
                "bgcolor": "rgba(255,255,255,0.04)",
                "borderwidth": 0,
                "steps": [
                    {"range": [0, 50],  "color": "rgba(255,255,255,0.03)"},
                    {"range": [50, 80], "color": "rgba(255,255,255,0.05)"},
                    {"range": [80, 100], "color": "rgba(255,255,255,0.08)"},
                ],
            },
            domain={"x": [0, 1], "y": [0, 1]},
        )
    )
    fig.update_layout(
        height=250, margin=dict(l=24, r=24, t=36, b=8),
        paper_bgcolor="rgba(0,0,0,0)", font={"color": "#E6EDF7", "family": "Inter"},
    )
    return fig


def _class_donut(scores: dict) -> go.Figure:
    labels = ["Alta", "Media", "Baja"]
    values = [scores.get("Alta", 0.0), scores.get("Media", 0.0), scores.get("Baja", 0.0)]
    colors = [COLORS["alta"], COLORS["media"], COLORS["baja"]]
    fig = go.Figure(
        go.Pie(
            labels=labels, values=values, hole=0.62, sort=False, direction="clockwise",
            marker={"colors": colors, "line": {"color": "#0B1220", "width": 3}},
            textinfo="percent", textfont={"color": "#0B1220", "size": 13, "family": "Inter"},
            hovertemplate="%{label}: %{percent}<extra></extra>",
        )
    )
    fig.update_layout(
        height=250, margin=dict(l=8, r=8, t=36, b=8), showlegend=True,
        legend={"font": {"color": "#C7D2E5", "family": "Inter"}, "orientation": "h", "y": -0.08, "x": 0.5, "xanchor": "center"},
        paper_bgcolor="rgba(0,0,0,0)",
        annotations=[{"text": "PROB.", "x": 0.5, "y": 0.5, "font": {"size": 13, "color": "#7E8CA8", "family": "Inter"}, "showarrow": False}],
    )
    return fig


def render_result_card(result: dict):
    """result: dict con label, score_alta, score_media, score_baja, texto_extraido, fuente"""
    label = result.get("label", "Desconocido")
    meta = LABEL_META.get(label, {"color": COLORS["muted"], "emoji": "⚪", "titulo": label, "sub": ""})
    scores = {
        "Alta":  float(result.get("score_alta", 0.0)),
        "Media": float(result.get("score_media", 0.0)),
        "Baja":  float(result.get("score_baja", 0.0)),
    }
    top = scores.get(label, max(scores.values()) if scores else 0.0)

    # Banner
    st.markdown(
        f"""
        <div class="he-banner" style="--bc:{meta['color']}; --bg1:{meta['color']}1f;">
            <span class="em">{meta['emoji']}</span>
            <div>
                <p class="ti">{meta['titulo']}</p>
                <p class="su">{meta['sub']}</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Gauge + Donut
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("<p style='color:#93A1BC;font-weight:600;margin:6px 0 0'>Confianza del modelo</p>", unsafe_allow_html=True)
        st.plotly_chart(_confidence_gauge(top, meta["color"]), use_container_width=True, config=_PLOTLY_CONF)
    with c2:
        st.markdown("<p style='color:#93A1BC;font-weight:600;margin:6px 0 0'>Distribución por clase</p>", unsafe_allow_html=True)
        st.plotly_chart(_class_donut(scores), use_container_width=True, config=_PLOTLY_CONF)

    # Texto extraido por OCR
    if result.get("fuente") == "imagen":
        with st.expander("📄 Texto extraído por OCR"):
            st.write(result.get("texto_extraido") or "(sin texto extraído)")
