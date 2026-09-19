"""
Dashboard interactivo - Ventas SRI 2026
------------------------------------------
FASE 5 del proyecto: convertir el análisis en una app interactiva.

Para ejecutarlo (no se corre con el botón ▶ normal):
    streamlit run dashboard.py

Esto abre automáticamente una pestaña en tu navegador.
"""

import pandas as pd
import streamlit as st
import plotly.express as px

# Configuración de la página (debe ir primero)
st.set_page_config(page_title="Dashboard Ventas SRI 2026", layout="wide")

# --------------------------------------------------------------
# Carga de datos (con caché: así no se vuelve a leer el CSV
# cada vez que mueves un filtro, solo la primera vez)
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
st.title("📊 Dashboard de Ventas SRI - Ecuador 2026")
st.caption("Datos del Servicio de Rentas Internas, enero–junio 2026")

# --------------------------------------------------------------
# Filtros en la barra lateral
# --------------------------------------------------------------
st.sidebar.header("Filtros")

meses_disponibles = sorted(df['MES'].unique())
meses_sel = st.sidebar.multiselect("Mes", meses_disponibles, default=meses_disponibles)

provincias_sel = st.sidebar.multiselect(
    "Provincia (vacío = todas)", sorted(df['PROVINCIA'].unique())
)

sectores_sel = st.sidebar.multiselect(
    "Sector (vacío = todos)", sorted(df['SECTOR'].unique())
)

# Aplicar filtros
df_filtrado = df[df['MES'].isin(meses_sel)]
if provincias_sel:
    df_filtrado = df_filtrado[df_filtrado['PROVINCIA'].isin(provincias_sel)]
if sectores_sel:
    df_filtrado = df_filtrado[df_filtrado['SECTOR'].isin(sectores_sel)]

# --------------------------------------------------------------
# Tarjetas de KPIs (números grandes arriba)
# --------------------------------------------------------------
col1, col2, col3 = st.columns(3)
col1.metric("Ventas totales", f"${df_filtrado['TOTAL_VENTAS'].sum():,.0f}")
col2.metric("Exportaciones", f"${df_filtrado['EXPORTACIONES'].sum():,.0f}")
col3.metric("Compras totales", f"${df_filtrado['TOTAL_COMPRAS'].sum():,.0f}")

# --------------------------------------------------------------
# Gráfico 1: evolución mensual (ancho completo)
# --------------------------------------------------------------
ventas_mes = df_filtrado.groupby('MES')['TOTAL_VENTAS'].sum().reset_index()
fig1 = px.line(
    ventas_mes, x='MES', y='TOTAL_VENTAS', markers=True,
    title='Evolución de ventas totales por mes'
)
st.plotly_chart(fig1, use_container_width=True)

# --------------------------------------------------------------
# Gráficos 2 y 3: sectores y provincias, lado a lado
# --------------------------------------------------------------
col4, col5 = st.columns(2)

with col4:
    top_sectores = (
        df_filtrado.groupby('SECTOR')['TOTAL_VENTAS'].sum()
        .sort_values(ascending=False).head(8).reset_index()
    )
    fig2 = px.bar(
        top_sectores, x='TOTAL_VENTAS', y='SECTOR', orientation='h',
        title='Top 8 sectores por ventas'
    )
    fig2.update_layout(yaxis={'categoryorder': 'total ascending'})
    st.plotly_chart(fig2, use_container_width=True)

with col5:
    top_provincias = (
        df_filtrado.groupby('PROVINCIA')['TOTAL_VENTAS'].sum()
        .sort_values(ascending=False).head(10).reset_index()
    )
    fig3 = px.bar(
        top_provincias, x='TOTAL_VENTAS', y='PROVINCIA', orientation='h',
        title='Top 10 provincias por ventas'
    )
    fig3.update_layout(yaxis={'categoryorder': 'total ascending'})
    st.plotly_chart(fig3, use_container_width=True)

# --------------------------------------------------------------
# Tabla de datos filtrados (para explorar el detalle)
# --------------------------------------------------------------
st.subheader("Detalle de datos filtrados")
st.dataframe(df_filtrado.head(200))
