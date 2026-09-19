"""
Dashboard interactivo - Ventas SRI 2026
------------------------------------------
FASE 5 del proyecto: dashboard interactivo con diseño personalizado.

Para ejecutarlo:
    streamlit run dashboard.py
"""

import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Dashboard Ventas SRI 2026", page_icon="📊", layout="wide")

# --------------------------------------------------------------
# Paleta de colores del dashboard (defínela una vez, úsala en todo)
# --------------------------------------------------------------
BG = "#0F1620"
CARD_BG = "#182130"
BORDER = "#2A3441"
ACCENT_GOLD = "#E8A33D"
ACCENT_TEAL = "#2DD4BF"
TEXT_MAIN = "#EDEDED"
TEXT_MUTED = "#9CA3AF"

# --------------------------------------------------------------
# CSS personalizado: tipografía + tarjetas + detalles visuales
# --------------------------------------------------------------
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;700&family=Inter:wght@400;500;600&display=swap');

html, body, [class*="css"] {{
    font-family: 'Inter', sans-serif;
}}

h1, h2, h3 {{
    font-family: 'Space Grotesk', sans-serif !important;
}}

/* Franja de acento superior */
.top-accent {{
    height: 4px;
    background: linear-gradient(90deg, {ACCENT_GOLD}, {ACCENT_TEAL});
    border-radius: 4px;
    margin-bottom: 24px;
}}

/* Tarjetas de KPIs personalizadas */
.metric-card {{
    background: {CARD_BG};
    border: 1px solid {BORDER};
    border-left: 3px solid {ACCENT_GOLD};
    border-radius: 10px;
    padding: 18px 22px;
}}
.metric-card.teal {{ border-left-color: {ACCENT_TEAL}; }}
.metric-label {{
    color: {TEXT_MUTED};
    font-size: 13px;
    text-transform: uppercase;
    letter-spacing: 0.04em;
}}
.metric-value {{
    color: {TEXT_MAIN};
    font-family: 'Space Grotesk', sans-serif;
    font-size: 30px;
    font-weight: 700;
    margin-top: 4px;
}}

section[data-testid="stSidebar"] {{
    border-right: 1px solid {BORDER};
}}
</style>
""", unsafe_allow_html=True)


# --------------------------------------------------------------
# Carga de datos
# --------------------------------------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv('sri_ventas_2026.csv', sep='|', encoding='latin-1', decimal=',')

    sectores = {
        'A': 'Agricultura, ganadería, silvicultura y pesca',
        'B': 'Explotación de minas y canteras',
        'C': 'Industrias manufactureras',
        'D': 'Suministro de electricidad y gas',
        'E': 'Distribución de agua y saneamiento',
        'F': 'Construcción',
        'G': 'Comercio al por mayor y menor',
        'H': 'Transporte y almacenamiento',
        'I': 'Alojamiento y servicios de comida',
        'J': 'Información y comunicación',
        'K': 'Actividades financieras y de seguros',
        'L': 'Actividades inmobiliarias',
        'M': 'Actividades profesionales, científicas y técnicas',
        'N': 'Actividades de servicios administrativos',
        'O': 'Administración pública y defensa',
        'P': 'Enseñanza',
        'Q': 'Actividades de salud humana',
        'R': 'Artes, entretenimiento y recreación',
        'S': 'Otras actividades de servicios',
        'T': 'Actividades de hogares como empleadores',
        'U': 'Organizaciones extraterritoriales',
        '9': 'No clasificado',
    }
    df['SECTOR'] = df['CODIGO_SECTOR_N1'].map(sectores).fillna('Otro / sin clasificar')
    df['VENTAS_LOCALES'] = df['TOTAL_VENTAS'] - df['EXPORTACIONES']
    return df

df = load_data()

# --------------------------------------------------------------
# Encabezado
# --------------------------------------------------------------
st.markdown('<div class="top-accent"></div>', unsafe_allow_html=True)
st.title("📊 Dashboard de Ventas SRI · Ecuador 2026")
st.caption("Datos del Servicio de Rentas Internas — enero a junio 2026")

# --------------------------------------------------------------
# Filtros
# --------------------------------------------------------------
st.sidebar.header("Filtros")
meses_disponibles = sorted(df['MES'].unique())
meses_sel = st.sidebar.multiselect("Mes", meses_disponibles, default=meses_disponibles)
provincias_sel = st.sidebar.multiselect("Provincia (vacío = todas)", sorted(df['PROVINCIA'].unique()))
sectores_sel = st.sidebar.multiselect("Sector (vacío = todos)", sorted(df['SECTOR'].unique()))

df_filtrado = df[df['MES'].isin(meses_sel)]
if provincias_sel:
    df_filtrado = df_filtrado[df_filtrado['PROVINCIA'].isin(provincias_sel)]
if sectores_sel:
    df_filtrado = df_filtrado[df_filtrado['SECTOR'].isin(sectores_sel)]

# --------------------------------------------------------------
# KPIs con tarjetas personalizadas
# --------------------------------------------------------------
col1, col2, col3 = st.columns(3)
kpis = [
    (col1, "Ventas totales", df_filtrado['TOTAL_VENTAS'].sum(), ""),
    (col2, "Exportaciones", df_filtrado['EXPORTACIONES'].sum(), "teal"),
    (col3, "Compras totales", df_filtrado['TOTAL_COMPRAS'].sum(), ""),
]
for col, label, valor, clase in kpis:
    col.markdown(f"""
        <div class="metric-card {clase}">
            <div class="metric-label">{label}</div>
            <div class="metric-value">${valor:,.0f}</div>
        </div>
    """, unsafe_allow_html=True)

st.write("")  # espacio

# --------------------------------------------------------------
# Plantilla común para los gráficos de Plotly
# --------------------------------------------------------------
def estilizar(fig):
    fig.update_layout(
        paper_bgcolor=BG,
        plot_bgcolor=BG,
        font_color=TEXT_MAIN,
        title_font_family="Space Grotesk, sans-serif",
        margin=dict(t=50, l=10, r=10, b=10),
    )
    fig.update_xaxes(gridcolor=BORDER, zerolinecolor=BORDER)
    fig.update_yaxes(gridcolor=BORDER, zerolinecolor=BORDER)
    return fig

# --------------------------------------------------------------
# Gráfico 1: evolución mensual
# --------------------------------------------------------------
ventas_mes = df_filtrado.groupby('MES')['TOTAL_VENTAS'].sum().reset_index()
fig1 = px.line(
    ventas_mes, x='MES', y='TOTAL_VENTAS', markers=True,
    title='Evolución de ventas totales por mes',
    color_discrete_sequence=[ACCENT_GOLD],
)
fig1.update_traces(line_width=3, marker_size=9)
st.plotly_chart(estilizar(fig1), use_container_width=True)

# --------------------------------------------------------------
# Gráficos 2 y 3
# --------------------------------------------------------------
col4, col5 = st.columns(2)

with col4:
    top_sectores = (
        df_filtrado.groupby('SECTOR')['TOTAL_VENTAS'].sum()
        .sort_values(ascending=False).head(8).reset_index()
    )
    fig2 = px.bar(
        top_sectores, x='TOTAL_VENTAS', y='SECTOR', orientation='h',
        title='Top 8 sectores por ventas',
        color_discrete_sequence=[ACCENT_TEAL],
    )
    fig2.update_layout(yaxis={'categoryorder': 'total ascending'})
    st.plotly_chart(estilizar(fig2), use_container_width=True)

with col5:
    top_provincias = (
        df_filtrado.groupby('PROVINCIA')['TOTAL_VENTAS'].sum()
        .sort_values(ascending=False).head(10).reset_index()
    )
    fig3 = px.bar(
        top_provincias, x='TOTAL_VENTAS', y='PROVINCIA', orientation='h',
        title='Top 10 provincias por ventas',
        color_discrete_sequence=[ACCENT_GOLD],
    )
    fig3.update_layout(yaxis={'categoryorder': 'total ascending'})
    st.plotly_chart(estilizar(fig3), use_container_width=True)

# --------------------------------------------------------------
# Tabla de detalle
# --------------------------------------------------------------
st.subheader("Detalle de datos filtrados")
st.dataframe(df_filtrado.head(200), use_container_width=True)
