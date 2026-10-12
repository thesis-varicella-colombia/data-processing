# Catálogo de datos

Este catálogo indica **qué variables contiene cada conjunto**. Las fichas enlazadas, guardadas junto a los datos, explican su fuente, periodo, generación y limitaciones. Los comandos de sus fichas se ejecutan desde la raíz del repositorio.

## Datos de entrada (`raw/`)

| Conjunto y ficha técnica | Variables disponibles | Resolución temporal y espacial |
| --- | --- | --- |
| [ERA5-Land Daily UTC, Colombia](raw/era5_land/README.md) | `t2m`: temperatura del aire a 2 m (K); `d2m`: temperatura del punto de rocío a 2 m (K); `sp`: presión superficial (Pa); `tp`: precipitación total diaria (m de agua) | Día UTC, grilla de 0,1°; archivos anuales 2007–2025 y meses de borde |
| [ERA5 atmosférico, Providencia](raw/era5_atmosphere_providencia/README.md) | `t2m`: temperatura del aire a 2 m (K); `d2m`: punto de rocío a 2 m (K); `sp`: presión superficial (Pa); `tp`: precipitación horaria (m de agua) | Hora UTC, grilla de 0,25°; archivos mensuales 2006-12 a 2026-01 |
| [CHIRPS v3 Final/rnl](raw/precipitation/chirps/README.md) | `precip`: precipitación diaria (mm/día, acumulado del día) | Día, grilla global de 0,05°; archivos anuales 2007–2025, borde observado 2006-12-31 y borde imputado 2026-01-01 a 2026-01-03 |
| [MGN 2025 y DIVIPOLA](raw/municipios/README.md) | Polígonos municipales, código y nombre de municipio y departamento, tipo de entidad; DIVIPOLA incluye longitud y latitud de referencia | Geometrías y tabla de códigos, sin serie temporal |
| [Sivigila, varicela individual (evento 831)](raw/sivigila/README.md) | Registros de notificación; entre sus campos: `FEC_NOT` (fecha de notificación), `ANO`, `SEMANA`, `EDAD`, `SEXO`, `COD_DPTO_O`, `TIP_CAS` y `AJUSTE`. Consulte el [diccionario completo](raw/sivigila/dic_datos.md) | Registro individual; archivos por año 2007–2025 |

## Datos derivados (`processed/`)

| Conjunto y ficha técnica | Variables de resultado | Unidad de análisis y origen |
| --- | --- | --- |
| [Temperatura municipal](processed/climate/temperature/README.md) | `temperatura_media_c` (°C), `fraccion_area_con_datos` (0–1) | Municipio × semana epidemiológica; calculada de `t2m` de ERA5-Land |
| [Humedad municipal](processed/climate/humidity/README.md) | `humedad_relativa_media_pct` (%), `humedad_especifica_media_g_kg` (g/kg), `humedad_absoluta_media_g_m3` (g/m³) y fracción de cobertura independiente por variable (0–1) | Municipio × semana epidemiológica; calculada de `t2m`, `d2m` y `sp` de ERA5-Land |
| [Precipitación municipal ERA5-Land](processed/climate/precipitation/README.md) | `precipitacion_total_mm` (mm/semana), `fraccion_area_con_datos` (0–1) | Municipio × semana epidemiológica; suma de siete medias municipales diarias derivadas de `tp` |
| [Estimación separada de Providencia](processed/climate/providencia/README.md) | Días derivados con `t2m` y `d2m` (K), `sp` (Pa) y `tp` (m); Parquet semanales con `temperatura_media_c` (°C), `humedad_relativa_media_pct` (%), `humedad_especifica_media_g_kg` (g/kg), `humedad_absoluta_media_g_m3` (g/m³), `precipitacion_total_mm` (mm), cobertura, `fuente_dato` y `es_estimacion` | Municipio 88564 × día UTC y × semana epidemiológica; parte de ERA5 atmosférico horario, no de ERA5-Land |

Las salidas semanales incluyen `codigo_municipio`, `nombre_municipio`, `ano_epidemiologico`, `semana_epidemiologica`, `inicio_semana` y `fin_semana`. Las semanas van de domingo a sábado; la semana 1 contiene el 4 de enero. La [metodología común](processed/climate/README.md) detalla fórmulas, ponderación por área y manejo de faltantes.

**Interpretación temporal:** ERA5-Land y los días derivados de ERA5 atmosférico usan días UTC. CHIRPS aporta etiquetas diarias; su ficha explica por qué la coincidencia de fecha no implica una ventana horaria exactamente igual. La estimación de Providencia emplea otra fuente y resolución y se mantiene separada de los resultados ERA5-Land.
