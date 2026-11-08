# Catálogo de datos

Este catálogo indica **qué variables contiene cada conjunto**. Las fichas enlazadas, guardadas junto a los datos, explican su fuente, periodo, generación y limitaciones. Los comandos de sus fichas se ejecutan desde la raíz del repositorio.

## Cómo consultar los esquemas y diccionarios

Este README es un catálogo de conjuntos distintos y no tiene un esquema
tabular único. Cada ficha de datos enlazada documenta las columnas o
variables, tipos, unidad de observación y diccionario aplicables. En las
carpetas que agrupan varios productos, se enlaza el esquema específico de
cada salida.

Los tipos Arrow/NetCDF describen el almacenamiento inspeccionado. Para CSV
y Excel, que no fijan tipos por columna, las fichas indican tipos lógicos o
de lectura recomendados. En NetCDF el esquema incluye dimensiones y
coordenadas; en GeoJSON, propiedades y geometría. Las familias repetitivas
de edad se expresan por rangos y las variantes de encabezado se documentan
por libro o año. Los esquemas y significados sin evidencia local suficiente
se dejan sin especificar.

## Datos de entrada (`raw/`)

| Conjunto y ficha técnica | Variables disponibles | Resolución temporal y espacial |
| --- | --- | --- |
| [ERA5-Land Daily UTC, Colombia](raw/era5_land/README.md) | `t2m`: temperatura del aire a 2 m (K); `d2m`: temperatura del punto de rocío a 2 m (K); `sp`: presión superficial (Pa); `tp`: precipitación total diaria (m de agua) | Día UTC, grilla de 0,1°; archivos anuales 2007–2025 y meses de borde |
| [ERA5 atmosférico, Providencia](raw/era5_atmosphere_providencia/README.md) | `t2m`: temperatura del aire a 2 m (K); `d2m`: punto de rocío a 2 m (K); `sp`: presión superficial (Pa); `tp`: precipitación horaria (m de agua) | Hora UTC, grilla de 0,25°; archivos mensuales 2006-12 a 2026-01 |
| [CHIRPS v3 Final/sat y Final/rnl](raw/precipitation/chirps/README.md) | `precip`: precipitación diaria (mm/día, acumulado del día) | Día, grilla global de 0,05°; archivos anuales 2007–2025 por variante, borde observado 2006-12-31 y borde imputado 2026-01-01 a 2026-01-03 |
| [MGN 2025 y DIVIPOLA](raw/municipios/README.md) | Polígonos municipales, código y nombre de municipio y departamento, tipo de entidad; DIVIPOLA incluye longitud y latitud de referencia | Geometrías y tabla de códigos, sin serie temporal |
| [Sivigila, varicela individual (evento 831)](raw/sivigila/README.md) | Registros de notificación; entre sus campos: `FEC_NOT` (fecha de notificación), `ANO`, `SEMANA`, `EDAD`, `SEXO`, `COD_DPTO_O`, `TIP_CAS` y `AJUSTE`. Consulte el [diccionario completo](raw/sivigila/dic_datos.md) | Registro individual; archivos por año 2007–2025 |
| [Coberturas de vacunación PAI](raw/vaccine_coverage/README.md) | `DIVIPOLA`, municipio, población objetivo, dosis aplicadas y coberturas por biológico, dosis y grupo de edad (por ejemplo, BCG, hepatitis B, polio, pentavalente, rotavirus, SRP, DPT y VPH) | Hojas anuales municipales 1998–2025, con cortes indicados en cada hoja; también incluye consolidaciones |
| [Población municipal DANE](raw/population/README.md) | Población total y por sexo, edad simple y área geográfica (`Cabecera Municipal`, `Centros Poblados y Rural Disperso`, `Total`); código y nombre municipal | Series anuales municipales 2005–2017 y 2018–2042, basadas en el CNPV 2018 |
| [Nacimientos DANE, originales](raw/births_mortality_dane/births/README.md) | Cuadro 3: nacimientos por residencia de la madre, sexo y área; códigos, nombres y totales territoriales; libro adicional de registros tardíos sin incorporar al consolidado | 18 libros anuales 2008–2025; municipios, departamentos, extranjeros y sin información |
| [Defunciones DANE, originales](raw/births_mortality_dane/mortality/README.md) | Cuadro 5: defunciones por residencia, causa, grupo de edad y sexo; estructura Excel por versión | 18 libros anuales 2008–2025; totales y desgloses territoriales |

## Datos derivados (`processed/`)

| Conjunto y ficha técnica | Variables de resultado | Unidad de análisis y origen |
| --- | --- | --- |
| [Temperatura municipal](processed/climate/temperature/README.md) | `temperatura_media_c` (°C), `fraccion_area_con_datos` (0–1) | Municipio × semana epidemiológica; calculada de `t2m` de ERA5-Land |
| [Humedad municipal](processed/climate/humidity/README.md) | `humedad_relativa_media_pct` (%), `humedad_especifica_media_g_kg` (g/kg), `humedad_absoluta_media_g_m3` (g/m³) y fracción de cobertura independiente por variable (0–1) | Municipio × semana epidemiológica; calculada de `t2m`, `d2m` y `sp` de ERA5-Land |
| [Precipitación municipal ERA5-Land](processed/climate/precipitation/README.md) | `precipitacion_total_mm` (mm acumulados en la semana), `fraccion_area_con_datos` (0–1) | Municipio × semana epidemiológica; suma de siete medias municipales diarias derivadas de `tp` |
| [Precipitación municipal CHIRPS](processed/chirps_precipitation/README.md) | `precipitacion_total_mm` (mm acumulados en la semana), `fraccion_area_con_datos` (0–1), días con datos e imputados | Municipio × semana epidemiológica; `sat` es la variante principal para sensibilidad frente a ERA5; `rnl` se conserva como serie anterior |
| [Estimación separada de Providencia](processed/climate/providencia/README.md) | Días derivados con `t2m` y `d2m` (K), `sp` (Pa) y `tp` (m); Parquet semanales con `temperatura_media_c` (°C), `humedad_relativa_media_pct` (%), `humedad_especifica_media_g_kg` (g/kg), `humedad_absoluta_media_g_m3` (g/m³), `precipitacion_total_mm` (mm), cobertura, `fuente_dato` y `es_estimacion` | Municipio 88564 × día UTC y × semana epidemiológica; parte de ERA5 atmosférico horario, no de ERA5-Land |
| [Varicela Sivigila municipal](processed/sivigila/README.md) | 85 columnas de identificación, conteos `casos_*` y `prop_notificados_fuera_municipio`; diccionarios de [origen](processed/sivigila/source_weekly_municipal/README.md), [notificación](processed/sivigila/notification_weekly_municipal/README.md) y [síntomas](processed/sivigila/symptom_weekly_municipal/README.md) | Entidad de residencia × semana reportada o calculada desde la fecha; cobertura según variante |
| [Nacimientos DANE, consolidado](processed/births_mortality_dane/births/README.md) | `total` y nacimientos por sexo y área, año, códigos y nombres de departamento y municipio; 21 columnas | Año × entidad de residencia de la madre, 2008–2025; conserva totales y desgloses, países y filas sin información |
| [Defunciones DANE, consolidado](processed/births_mortality_dane/mortality/README.md) | 30 columnas: identificación, total y defunciones por edad y sexo | Año × entidad de residencia o categoría/total, 2008–2025 |
| [Integración de nacimientos y mortalidad infantil](processed/births_mortality_dane/integration/README.md) | 8 columnas del saldo de sobrevivientes, más esquemas del CSV y JSON de validación | Año × entidad o categoría; nacimientos menos defunciones infantiles del año anterior |
| [Población municipal](processed/population/README.md) | 22 columnas: código, año y población por sexo, área y grupo de edad | Municipio × año, 2007–2025; proyecciones y retroproyecciones DANE |
| [Vacunación municipal contra varicela](processed/vaccine_coverage/README.md) | 11 columnas: códigos, nombres, metas, dosis, coberturas y año de análisis | Municipio × año de análisis, 2016–2025; libro PAI |
| [Integración semanal municipal](processed/integration_data/README.md) | 141 columnas: casos, población, incidencia, vacunación y clima | Entidad de residencia × semana; tres variantes según la semana base de SIVIGILA |

Las salidas semanales incluyen `codigo_municipio`, `nombre_municipio`, `ano_epidemiologico`, `semana_epidemiologica`, `inicio_semana` y `fin_semana`. Las semanas van de domingo a sábado; la semana 1 contiene el 4 de enero. La [metodología común](processed/climate/README.md) detalla fórmulas, ponderación por área y manejo de faltantes.

**Interpretación temporal:** ERA5-Land y los días derivados de ERA5 atmosférico usan días UTC. CHIRPS aporta etiquetas diarias; su ficha explica por qué la coincidencia de fecha no implica una ventana horaria exactamente igual. La estimación de Providencia emplea otra fuente y resolución y se mantiene separada de los resultados ERA5-Land.
