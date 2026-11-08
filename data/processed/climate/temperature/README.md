# Ficha técnica: temperatura semanal municipal

| Campo | Descripción |
| --- | --- |
| Entrada | [`data/raw/era5_land/era5_land_daily_AAAA.nc`](../../../raw/era5_land/README.md), variable `t2m` en K; meses de borde 2006-12 y 2026-01 |
| Geografía | [MGN 2025 y DIVIPOLA](../../../raw/municipios/README.md); solo entidades `MUNICIPIO` |
| Salida | `temperature_weekly_municipal_AAAA.parquet`, un archivo por año epidemiológico 2007–2025 |
| Unidad y tiempo | °C; semanas de domingo a sábado sobre días 00:00–23:59 UTC |
| Generado por | [`scripts/processing/calculate_weekly_temperature.py`](../../../../scripts/processing/calculate_weekly_temperature.py) |

Se calcula `t2m − 273,15` por celda y día. La media municipio-semana usa el área geodésica de intersección celda-polígono y solo los valores válidos en numerador y denominador. `fraccion_area_con_datos` mide el área válida acumulada respecto de siete días de cobertura de la grilla. Las columnas son `codigo_municipio`, `nombre_municipio`, `ano_epidemiologico`, `semana_epidemiologica`, `inicio_semana`, `fin_semana`, `temperatura_media_c` y `fraccion_area_con_datos`. Véase la [metodología común](../README.md). Providencia (`88564`) permanece sin datos en esta fuente y tiene una [estimación aparte](../providencia/README.md).

Desde la raíz del repositorio:

```bash
.venv/bin/python scripts/processing/calculate_weekly_temperature.py --validate-only
.venv/bin/python scripts/processing/calculate_weekly_temperature.py
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
| `temperatura_media_c` | `double` | Temperatura media semanal ponderada por área y día, en °C. |
| `fraccion_area_con_datos` | `double` | Fracción de área y días con datos válidos respecto de siete días, entre 0 y 1. |
