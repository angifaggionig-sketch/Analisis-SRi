import pandas as pd
 
# 1. Cargar los datos
# El archivo del SRI usa "|" como separador, codificación latin-1
# (por las tildes y Ñ) y coma como separador decimal.
df = pd.read_csv(
    'sri_ventas_2026.csv',
    sep='|',
    encoding='latin-1',
    decimal=','
)
 
# 2. Primer vistazo
print("Filas y columnas:", df.shape)
print(df.head())
 
# 3. Tipos de datos y nulos
print(df.dtypes)
print("Valores nulos totales:", df.isnull().sum().sum())
 
# 4. Revisión de calidad de datos
print("Meses presentes:", sorted(df['MES'].unique()))
print("Filas con provincia 'ND':", (df['PROVINCIA'] == 'ND').sum())
print("Filas duplicadas:", df.duplicated().sum())
print("Códigos de sector (CIIU):", sorted(df['CODIGO_SECTOR_N1'].unique()))
 
# Hallazgos Fase 1:
# - 25,339 filas, 16 columnas, sin valores nulos
# - Datos de enero a junio 2026
# - 95 filas (0.37%) con provincia "ND" (No Determinado) -> se mantienen,
#   son insignificantes en volumen
# - 0 duplicados
# - 25 códigos de sector = letras de la clasificación CIIU
#   (se traducirán a nombres legibles a continuación)
 
 
"""
FASE 2: Traducir códigos y ver un resumen legible
----------------------------------------------------
Objetivo: convertir las letras de sector (CIIU) en nombres reales,
y mostrar un primer resumen ordenado y fácil de leer.
"""
 
# 5. Diccionario: letra CIIU -> nombre del sector económico
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
 
# Creamos una columna nueva "SECTOR" con el nombre legible.
# Si aparece una letra que no está en el diccionario, se marca como
# "Otro / sin clasificar" en vez de fallar.
df['SECTOR'] = df['CODIGO_SECTOR_N1'].map(sectores).fillna('Otro / sin clasificar')
 
# 6. Resumen legible: ventas totales por sector, ordenado de mayor a menor
resumen_sectores = (
    df.groupby('SECTOR')['TOTAL_VENTAS']
    .sum()
    .sort_values(ascending=False)
)
 
print()
print("=== VENTAS TOTALES POR SECTOR (enero-junio 2026) ===")
for sector, monto in resumen_sectores.items():
    print(f"{sector:<55} ${monto:,.2f}")
 
# 7. Resumen legible: ventas totales por provincia, top 10
resumen_provincias = (
    df.groupby('PROVINCIA')['TOTAL_VENTAS']
    .sum()
    .sort_values(ascending=False)
    .head(10)
)
 
print()
print("=== TOP 10 PROVINCIAS POR VENTAS TOTALES ===")
for provincia, monto in resumen_provincias.items():
    print(f"{provincia:<25} ${monto:,.2f}")
    

import matplotlib.pyplot as plt
 
# 8. Gráfico 1: evolución de ventas totales mes a mes
ventas_por_mes = df.groupby('MES')['TOTAL_VENTAS'].sum()
 
plt.figure(figsize=(8, 5))
plt.plot(ventas_por_mes.index, ventas_por_mes.values, marker='o', color='#2E86AB', linewidth=2)
plt.title('Evolución de ventas totales por mes (2026)')
plt.xlabel('Mes')
plt.ylabel('Ventas totales (USD)')
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('grafico_1_evolucion_mensual.png')
plt.show()
 
# 9. Gráfico 2: exportaciones vs ventas locales, top 8 sectores
df['VENTAS_LOCALES'] = df['TOTAL_VENTAS'] - df['EXPORTACIONES']
 
top8_sectores = resumen_sectores.head(8).index
comparacion = (
    df[df['SECTOR'].isin(top8_sectores)]
    .groupby('SECTOR')[['VENTAS_LOCALES', 'EXPORTACIONES']]
    .sum()
    .loc[top8_sectores]  # mantener el mismo orden que el ranking
)
 
plt.figure(figsize=(10, 6))
posiciones = range(len(comparacion))
plt.bar(posiciones, comparacion['VENTAS_LOCALES'], label='Ventas locales', color='#2E86AB')
plt.bar(posiciones, comparacion['EXPORTACIONES'], bottom=comparacion['VENTAS_LOCALES'],
        label='Exportaciones', color='#F18F01')
plt.xticks(posiciones, comparacion.index, rotation=45, ha='right')
plt.ylabel('USD')
plt.title('Ventas locales vs Exportaciones (Top 8 sectores)')
plt.legend()
plt.tight_layout()
plt.savefig('grafico_2_exportaciones_sector.png')
plt.show()
 
# 10. Gráfico 3: ranking de provincias (barras horizontales)
plt.figure(figsize=(8, 6))
plt.barh(resumen_provincias.index[::-1], resumen_provincias.values[::-1], color='#A23B72')
plt.xlabel('Ventas totales (USD)')
plt.title('Top 10 provincias por ventas totales')
plt.tight_layout()
plt.savefig('grafico_3_top_provincias.png')
plt.show()
 
print()
print("Gráficos guardados como PNG en tu carpeta: grafico_1_evolucion_mensual.png,")
print("grafico_2_exportaciones_sector.png, grafico_3_top_provincias.png")