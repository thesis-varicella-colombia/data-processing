# Ficha técnica: humedad semanal municipal

| Campo | Descripción |
| --- | --- |
| Entrada | [`data/raw/era5_land/era5_land_daily_AAAA.nc`](../../../raw/era5_land/README.md): `t2m`, `d2m` en K y `sp` en Pa; meses de borde 2006-12 y 2026-01 |
| Geografía | [MGN 2025 y DIVIPOLA](../../../raw/municipios/README.md); solo entidades `MUNICIPIO` |
| Salida | `humidity_weekly_municipal_AAAA.parquet`, un archivo por año epidemiológico 2007–2025 |
| Tiempo | Semanas de domingo a sábado sobre días 00:00–23:59 UTC |
| Generado por | [`scripts/processing/calculate_weekly_humidity.py`](../../../../scripts/processing/calculate_weekly_humidity.py) |

Primero se calculan por **celda y día** la humedad relativa (%), específica (g/kg) y absoluta (g/m³) a partir de las medias diarias de temperatura y punto de rocío y la presión superficial local. Luego se promedian por área geodésica de intersección y semana. El [README común](../README.md) contiene las fórmulas, validaciones físicas y definición de cobertura. Cada indicador tiene su propia columna `fraccion_area_con_datos_<nombre_del_indicador>`; los indicadores son `humedad_relativa_media_pct`, `humedad_especifica_media_g_kg` y `humedad_absoluta_media_g_m3`. También se incluyen códigos y nombres municipales, año y semana epidemiológicos, e inicio y fin de semana. Providencia (`88564`) permanece sin datos en esta fuente y tiene una [estimación aparte](../providencia/README.md).

Desde la raíz del repositorio:

```bash
.venv/bin/python scripts/processing/calculate_weekly_humidity.py --validate-only
.venv/bin/python scripts/processing/calculate_weekly_humidity.py
```

`--start-year`, `--end-year` y `--municipality` delimitan la ejecución; `--overwrite` regenera salidas existentes.

## Esquema y diccionario de datos

Los tipos son los tipos físicos Arrow observados en los Parquet locales. `large_string` es texto, `int64` es entero de 64 bits y `double` es real de 64 bits. Las medidas sin datos válidos pueden ser nulas; una cobertura 0 indica ausencia de datos. La clave de cada archivo es (`codigo_municipio`, `ano_epidemiologico`, `semana_epidemiologica`).

| Columna | Tipo | Descripción |
| --- | --- | --- |
| `codigo_municipio` | `large_string` | Código DIVIPOLA de cinco dígitos, conservando ceros iniciales. |
| `nombre_municipio` | `large_string` | Nombre de la entidad municipal. |
| `ano_epidemiologico` | `int64` | Año epidemiológico de la semana; puede diferir del año calendario. |
| `semana_epidemiologica` | `int64` | Número de semana epidemiológica, de domingo a sábado; semana 1 contiene el 4 de enero. |
| `inicio_semana` | `large_string` | Domingo inicial, inclusive; texto ISO AAAA-MM-DD en estos Parquet climáticos. |
| `fin_semana` | `large_string` | Sábado final, inclusive; texto ISO AAAA-MM-DD en estos Parquet climáticos. |
| `humedad_relativa_media_pct` | `double` | Humedad relativa media semanal ponderada por área y día, en %. |
| `fraccion_area_con_datos_humedad_relativa_media_pct` | `double` | Fracción de área y días válidos para humedad_relativa_media_pct, entre 0 y 1. |
| `humedad_especifica_media_g_kg` | `double` | Humedad específica media semanal ponderada por área y día, en g/kg. |
| `fraccion_area_con_datos_humedad_especifica_media_g_kg` | `double` | Fracción de área y días válidos para humedad_especifica_media_g_kg, entre 0 y 1. |
| `humedad_absoluta_media_g_m3` | `double` | Densidad media semanal de vapor de agua ponderada por área y día, en g/m³. |
| `fraccion_area_con_datos_humedad_absoluta_media_g_m3` | `double` | Fracción de área y días válidos para humedad_absoluta_media_g_m3, entre 0 y 1. |
