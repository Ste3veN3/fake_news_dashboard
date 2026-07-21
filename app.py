"""
Panel Exploratorio — Estilometría de Noticias Falsas vs. Verdaderas
Proyecto Final · Visualización de Datos · USFQ
Autor: Steeven Quezada

Componente A: Distribución por clase (boxplot + jitter, con brushing real)
Los Componentes B, C y D se agregan en iteraciones siguientes.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# ============================================================
# CONFIGURACIÓN DE PÁGINA Y PALETA (misma identidad del pitch)
# ============================================================
st.set_page_config(
    page_title="Estilometría de Noticias",
    page_icon="📰",
    layout="wide",
)

INK = "#1B1917"
RED = "#B23A2E"    # falsa
TEAL = "#1F6E68"   # verdadera
MUTED = "#6B6864"
CARD = "#EFF1F0"
TEXT_DARK = "#211F1C"

st.markdown(
    f"""
    <style>
    html {{ font-size: 118%; }}
    .stApp {{ background-color: #FFFFFF; }}
    h1, h2, h3 {{ color: {INK}; }}
    </style>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# CARGA DE DATOS (cacheada — no se recalcula en cada interacción)
# ============================================================
@st.cache_data
def load_data():
    df = pd.read_csv("data/processed/dataset_muestra.csv")
    df["date_parsed"] = pd.to_datetime(df["date_parsed"], errors="coerce")
    df["label_name"] = df["label"].map({0: "Falsa", 1: "Verdadera"})
    return df

df = load_data()

# ============================================================
# ENCABEZADO — apertura narrativa
# ============================================================
st.title("📰 Estilometría de Noticias: Falsas vs. Verdaderas")
st.caption(
    "Imagina que eres verificador de hechos y tienes 200 artículos en tu bandeja esta mañana. "
    "¿Por cuál empiezas? Este panel explora si el **estilo de escritura** —sin leer el contenido, "
    "sin ningún modelo— ya da pistas."
)
st.divider()

# ============================================================
# FILTROS GLOBALES (sidebar)
# ============================================================
st.sidebar.header("Filtros")

subjects = sorted(df["subject"].dropna().unique().tolist())
selected_subjects = st.sidebar.multiselect(
    "Subject", options=subjects, default=subjects
)

min_date, max_date = df["date_parsed"].min(), df["date_parsed"].max()
date_range = st.sidebar.date_input(
    "Rango de fecha",
    value=(min_date.date(), max_date.date()),
    min_value=min_date.date(),
    max_value=max_date.date(),
)

# Aplicar filtros globales
mask = df["subject"].isin(selected_subjects)
if len(date_range) == 2:
    start, end = date_range
    mask &= (df["date_parsed"].dt.date >= start) & (df["date_parsed"].dt.date <= end)

df_filtered = df[mask].copy()

st.sidebar.metric("Artículos tras filtro", f"{len(df_filtered):,}")

# ============================================================
# COMPONENTE A — Distribución por clase (boxplot + jitter + brushing)
# ============================================================
st.subheader("A · Distribución por clase")
st.caption(
    "Cada punto es un artículo real. Selecciona un grupo de puntos (arrastra un rectángulo o "
    "usa lasso) para ver esos artículos específicos más abajo."
)

variable_labels = {
    "exclamations": "Exclamaciones",
    "questions": "Preguntas",
    "title_length": "Longitud del título",
    "avg_word_len": "Longitud promedio de palabra",
    "text_length": "Longitud del texto",
}
if "variable_select" not in st.session_state:
    st.session_state["variable_select"] = "exclamations"
if "pending_variable_select" not in st.session_state:
    st.session_state["pending_variable_select"] = None

# Si el Componente B pidió cambiar la variable (ver más abajo), se aplica
# ACÁ, antes de crear el selectbox — después de instanciado, Streamlit ya
# no permite reescribir st.session_state["variable_select"] directamente.
if st.session_state["pending_variable_select"] is not None:
    st.session_state["variable_select"] = st.session_state["pending_variable_select"]
    st.session_state["pending_variable_select"] = None

variable = st.selectbox(
    "Variable a explorar",
    options=list(variable_labels.keys()),
    format_func=lambda k: variable_labels[k],
    key="variable_select",
)

def make_jitter_boxplot(data: pd.DataFrame, col: str) -> go.Figure:
    fig = go.Figure()

    for label_val, name, color, xpos in [(0, "Falsa", RED, 0), (1, "Verdadera", TEAL, 1)]:
        sub = data[data["label"] == label_val]
        # Boxplot resumen (sin puntos propios — los puntos van en un trace aparte para poder seleccionarlos)
        fig.add_trace(go.Box(
            y=sub[col], x=[xpos] * len(sub), name=name,
            marker_color=color, boxpoints=False, width=0.4,
            line=dict(color=color), fillcolor=color, opacity=0.25,
            showlegend=False, hoverinfo="skip",
        ))
        # Nube de puntos individuales, con jitter manual — este SÍ es seleccionable (brushing)
        rng = np.random.default_rng(42)
        jitter = rng.uniform(-0.15, 0.15, size=len(sub))
        fig.add_trace(go.Scatter(
            x=xpos + jitter, y=sub[col], mode="markers", name=name,
            marker=dict(color=color, size=4.5, opacity=0.4),
            customdata=sub.index, showlegend=True,
            hovertemplate=(
                "<b>%{customdata}</b><br>" + variable_labels[col] + ": %{y}<extra>" + name + "</extra>"
            ),
        ))

    fig.update_layout(
        xaxis=dict(
            tickmode="array", tickvals=[0, 1], ticktext=["Falsa", "Verdadera"], title="",
            range=[-0.5, 1.5],
        ),
        yaxis=dict(
            title=dict(text=variable_labels[col], standoff=15),
            rangemode="tozero",  # nunca recortar el eje Y — Semana 1, Correll et al. CHI 2020
            automargin=True,
        ),
        height=460,
        dragmode="select",
        margin=dict(l=50, r=10, t=10, b=40),
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        font=dict(color="#211F1C", size=15),
    )
    fig.update_xaxes(gridcolor="#E5E5E5", zerolinecolor="#E5E5E5")
    fig.update_yaxes(gridcolor="#E5E5E5", zerolinecolor="#E5E5E5")
    return fig

fig_a = make_jitter_boxplot(df_filtered, variable)

zero_pct_fake = (df_filtered[df_filtered["label"] == 0][variable] == 0).mean() * 100
zero_pct_real = (df_filtered[df_filtered["label"] == 1][variable] == 0).mean() * 100
if max(zero_pct_fake, zero_pct_real) >= 40:
    st.caption(
        f"ℹ️ **{variable_labels[variable]}** tiene muchos artículos en cero: "
        f"{zero_pct_fake:.0f}% de las falsas y {zero_pct_real:.0f}% de las verdaderas. "
        "Por eso la caja se ve como una línea plana en 0 — no es un error, es que ahí "
        "está literalmente el 25°, 50° y/o 75° percentil. La diferencia entre clases está "
        "en la cola de valores altos, no en el cuerpo de la distribución."
    )

selection = st.plotly_chart(
    fig_a,
    on_select="rerun",
    selection_mode=("points", "box", "lasso"),
    key="component_a",
    width="stretch",
    theme=None,
)

# ============================================================
# Resultado del brushing (placeholder de lo que alimentará C y D)
# ============================================================
selected_indices = []
if selection and selection.get("selection", {}).get("point_indices"):
    # point_indices de streamlit son posiciones dentro del trace, no índices del df directamente;
    # usamos customdata (que sí es el índice real del df) para mapear de vuelta.
    for point in selection["selection"]["points"]:
        if "customdata" in point:
            selected_indices.append(point["customdata"][0] if isinstance(point["customdata"], list) else point["customdata"])

if selected_indices:
    st.success(f"🖱️ {len(selected_indices)} artículo(s) seleccionado(s) por brushing.")
    tabla = df.loc[df.index.isin(selected_indices), ["title", "subject", variable, "label_name"]].copy()
    st.caption(
        f"Nota: **{variable_labels[variable]}** se cuenta sobre el cuerpo del artículo, "
        "no sobre el título. Haz clic en una fila para abrir su ficha completa en el Componente C."
    )
    row_selection = st.dataframe(
        tabla,
        width="stretch",
        hide_index=True,
        on_select="rerun",
        selection_mode="single-row",
        key="tabla_articulos",
    )
    picked_rows = row_selection["selection"]["rows"] if row_selection else []
    if picked_rows:
        st.session_state["articulo_seleccionado"] = tabla.iloc[picked_rows[0]].name
else:
    st.info("Selecciona puntos en el gráfico de arriba para ver los artículos correspondientes aquí (esto alimentará el Componente C).")

st.divider()

# ============================================================
# COMPONENTE B — Variables más discriminantes (Cohen's d)
# ============================================================
st.subheader("B · Variables más discriminantes")
st.caption(
    "Ordenadas por tamaño del efecto (Cohen's d), no solo por significancia estadística — "
    "haz clic en una barra para explorarla en el Componente A."
)

@st.cache_data
def compute_cohens_d(data: pd.DataFrame, cols: list) -> pd.DataFrame:
    from scipy import stats as scipy_stats

    def cohens_d(x, y):
        nx, ny = len(x), len(y)
        pooled_std = np.sqrt(((nx - 1) * x.std(ddof=1) ** 2 + (ny - 1) * y.std(ddof=1) ** 2) / (nx + ny - 2))
        return (x.mean() - y.mean()) / pooled_std

    rows = []
    for col in cols:
        fake_vals = data[data["label"] == 0][col]
        real_vals = data[data["label"] == 1][col]
        d = cohens_d(fake_vals, real_vals)
        _, p = scipy_stats.mannwhitneyu(fake_vals, real_vals)
        rows.append({"variable": col, "d": d, "p": p})
    out = pd.DataFrame(rows)
    out["abs_d"] = out["d"].abs()
    return out.sort_values("abs_d", ascending=True).reset_index(drop=True)

def interpret_d(abs_d: float) -> str:
    if abs_d >= 0.8:
        return "efecto grande"
    if abs_d >= 0.5:
        return "efecto mediano"
    if abs_d >= 0.2:
        return "efecto pequeño"
    return "efecto marginal (significativo, pero poco relevante en la práctica)"

d_table = compute_cohens_d(df_filtered, list(variable_labels.keys()))

fig_b = go.Figure()
bar_colors = [RED if d > 0 else TEAL for d in d_table["d"]]
fig_b.add_trace(go.Bar(
    x=d_table["abs_d"], y=[variable_labels[v] for v in d_table["variable"]],
    orientation="h", marker_color=bar_colors,
    customdata=np.stack([d_table["variable"], d_table["d"], d_table["p"]], axis=1),
    hovertemplate=(
        "<b>%{y}</b><br>Cohen's d = %{customdata[1]:.2f}<br>"
        "Mann-Whitney p = %{customdata[2]:.2g}<extra></extra>"
    ),
))
fig_b.update_layout(
    height=360,
    margin=dict(l=10, r=10, t=10, b=50),
    xaxis_title="|Cohen's d|  (rojo = más en falsas · verde = más en verdaderas)",
    xaxis_rangemode="tozero",  # consistente con el mismo principio aplicado en A
    yaxis=dict(automargin=True),
    paper_bgcolor="#FFFFFF", plot_bgcolor="#FFFFFF", font=dict(color="#211F1C", size=15),
)
fig_b.update_xaxes(gridcolor="#E5E5E5")
fig_b.update_yaxes(gridcolor="#E5E5E5")

selection_b = st.plotly_chart(
    fig_b, on_select="rerun", selection_mode="points", key="component_b",
    width="stretch", theme=None,
)

# Mostrar la interpretación de la barra seleccionada (o la de mayor efecto, por defecto)
if selection_b and selection_b.get("selection", {}).get("points"):
    clicked_var = selection_b["selection"]["points"][0]["customdata"][0]
    if clicked_var != st.session_state["variable_select"]:
        st.session_state["pending_variable_select"] = clicked_var
        st.rerun()
    row = d_table[d_table["variable"] == clicked_var].iloc[0]
else:
    row = d_table.iloc[-1]  # la de mayor |d| por defecto

st.caption(
    f"**{variable_labels[row['variable']]}**: d = {row['d']:.2f} — {interpret_d(row['abs_d'])} "
    f"(p = {row['p']:.2g})."
)

st.divider()

# ============================================================
# COMPONENTE C — Ficha del artículo seleccionado
# ============================================================
st.subheader("C · Explorador de casos individuales")
st.caption(
    "Ancla los patrones agregados de A y B a un artículo concreto y verificable — "
    "selecciona una fila en la tabla de arriba."
)

articulo_idx = st.session_state.get("articulo_seleccionado")

if articulo_idx is None or articulo_idx not in df.index:
    st.info("Todavía no hay ningún artículo seleccionado. Haz brushing en A y haz clic en una fila de la tabla.")
else:
    art = df.loc[articulo_idx]

    st.markdown(f"#### {art['title']}")
    meta_col1, meta_col2, meta_col3 = st.columns(3)
    meta_col1.markdown(f"**Subject:** {art['subject']}")
    meta_col2.markdown(f"**Fecha:** {art['date_parsed'].date() if pd.notna(art['date_parsed']) else art['date']}")
    meta_col3.markdown(f"**Clase:** {'🔴 Falsa' if art['label'] == 0 else '🟢 Verdadera'}")

    with st.expander("Ver texto completo del artículo"):
        st.write(art["text"])

    st.markdown("**¿Qué tan atípico es este artículo respecto al promedio de su propia clase?**")

    # mismo orden que el Componente B (por |Cohen's d| descendente)
    ordered_vars = d_table.sort_values("abs_d", ascending=False)["variable"].tolist()

    z_cols = st.columns(len(ordered_vars))
    class_data = df_filtered[df_filtered["label"] == art["label"]]
    for i, v in enumerate(ordered_vars):
        mean_ = class_data[v].mean()
        std_ = class_data[v].std(ddof=1)
        z = (art[v] - mean_) / std_ if std_ > 0 else 0.0
        highlight = abs(z) >= 2
        with z_cols[i]:
            st.markdown(
                f"""<div style="background:{CARD if not highlight else '#FBF0EA'};
                border-radius:8px; padding:10px; text-align:center;">
                <div style="font-size:11px; color:{MUTED};">{variable_labels[v]}</div>
                <div style="font-size:18px; font-weight:700; color:{RED if highlight else TEXT_DARK};">
                {z:+.1f}σ</div></div>""",
                unsafe_allow_html=True,
            )
    if any(abs((art[v] - df_filtered[df_filtered['label']==art['label']][v].mean()) /
               (df_filtered[df_filtered['label']==art['label']][v].std(ddof=1) or 1)) >= 2 for v in ordered_vars):
        st.caption("🟠 Resaltado en naranja: variables donde este artículo se aleja 2+ desviaciones estándar del promedio de su clase.")

st.divider()

# ============================================================
# COMPONENTE D — Composición del dataset por subject
# Idiom: barra apilada al 100% (2 attrib categ + 1 quant, tarea parte-todo — Semana 1)
# Principio de normalización aplicado (Semana 3: nunca mostrar conteos crudos
# si el tamaño base varía entre categorías — mismo error que un mapa de población sin normalizar)
# ============================================================
st.subheader("D · Composición del dataset por subject")

@st.cache_data
def compute_composition(data: pd.DataFrame) -> pd.DataFrame:
    comp = data.groupby(["subject", "label"]).size().unstack(fill_value=0)
    comp.columns = [c for c in comp.columns]
    for lbl in [0, 1]:
        if lbl not in comp.columns:
            comp[lbl] = 0
    comp = comp.rename(columns={0: "falsa", 1: "verdadera"})
    comp["total"] = comp["falsa"] + comp["verdadera"]
    comp = comp[comp["total"] > 0]
    comp["pct_falsa"] = (comp["falsa"] / comp["total"] * 100).round(1)
    comp["pct_verdadera"] = 100 - comp["pct_falsa"]
    return comp.sort_values("pct_falsa", ascending=True)

comp = compute_composition(df_filtered)

if len(comp) == 0:
    st.info("No hay artículos para los filtros seleccionados.")
else:
    pure_subjects = (comp["pct_falsa"].isin([0, 100])).sum()

    fig_d = go.Figure()
    fig_d.add_trace(go.Bar(
        y=comp.index, x=comp["pct_falsa"], orientation="h", name="Falsa",
        marker_color=RED, legendrank=1,
        text=[f"{p:.0f}%" if p > 0 else "" for p in comp["pct_falsa"]],
        textposition="inside", insidetextanchor="middle",
        textfont=dict(color="white", size=13),
        customdata=np.stack([comp["falsa"], comp["total"]], axis=1),
        hovertemplate="<b>%{y}</b><br>Falsa: %{customdata[0]:.0f} de %{customdata[1]:.0f} (%{x:.1f}%)<extra></extra>",
    ))
    fig_d.add_trace(go.Bar(
        y=comp.index, x=comp["pct_verdadera"], orientation="h", name="Verdadera",
        marker_color=TEAL, legendrank=2,
        text=[f"{p:.0f}%" if p > 0 else "" for p in comp["pct_verdadera"]],
        textposition="inside", insidetextanchor="middle",
        textfont=dict(color="white", size=13),
        customdata=np.stack([comp["verdadera"], comp["total"]], axis=1),
        hovertemplate="<b>%{y}</b><br>Verdadera: %{customdata[0]:.0f} de %{customdata[1]:.0f} (%{x:.1f}%)<extra></extra>",
    ))
    fig_d.update_layout(
        barmode="stack",
        height=80 + 45 * len(comp),
        margin=dict(l=10, r=10, t=10, b=40),
        xaxis=dict(title="% del subject", range=[0, 100], rangemode="tozero"),
        yaxis=dict(automargin=True),
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        paper_bgcolor="#FFFFFF", plot_bgcolor="#FFFFFF", font=dict(color="#211F1C", size=15),
    )
    fig_d.add_vline(
        x=50, line_dash="dash", line_color=MUTED, opacity=0.5,
    )
    fig_d.update_xaxes(gridcolor="#E5E5E5")

    st.plotly_chart(fig_d, width="stretch", theme=None)

    if pure_subjects == len(comp):
        st.warning(
            f"⚠️ **Los {len(comp)} subjects son 100% de una sola clase, sin excepción.** "
            "Por un momento esto podría parecer la señal perfecta — 100% de precisión con solo "
            "mirar la categoría. Pero una separación así de limpia es sospechosa, no celebrable: "
            "`subject` no mide estilo editorial, mide de qué fuente venía cada artículo en la "
            "recolección original del dataset. Se muestra aquí como **contexto**, no como variable "
            "predictiva — normalizado por porcentaje (no conteo crudo), porque los subjects no "
            "tienen el mismo tamaño base."
        )
    else:
        st.caption(
            f"{pure_subjects} de {len(comp)} subjects son 100% de una sola clase — revisa si "
            "`subject` debería tratarse como señal de origen más que editorial."
        )