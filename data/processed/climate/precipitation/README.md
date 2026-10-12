# Ficha técnica: precipitación semanal municipal ERA5-Land

| Campo | Descripción |
| --- | --- |
| Entrada | [`data/raw/era5_land/era5_land_daily_AAAA.nc`](../../../raw/era5_land/README.md), variable `tp` en m; meses de borde 2006-12 y 2026-01 |
| Geografía | [MGN 2025 y DIVIPOLA](../../../raw/municipios/README.md); solo entidades `MUNICIPIO` |
| Salida | `precipitation_weekly_municipal_AAAA.parquet`, un archivo por año epidemiológico 2007–2025 |
| Unidad y tiempo | mm acumulados por semana de domingo a sábado, basada en días 00:00–23:59 UTC |
| Generado por | [`scripts/processing/calculate_weekly_precipitation.py`](../../../../scripts/processing/calculate_weekly_precipitation.py) |

Se convierte `tp × 1000` de m a mm por celda y día. Se calcula la media municipal de cada día ponderada por área geodésica de intersección y **se suman los siete días**. Si falta un día municipal completo, el total semanal queda `NaN`. Las columnas son `codigo_municipio`, `nombre_municipio`, `ano_epidemiologico`, `semana_epidemiologica`, `inicio_semana`, `fin_semana`, `precipitacion_total_mm` y `fraccion_area_con_datos`. La cobertura y las semanas se definen en la [metodología común](../README.md). Providencia (`88564`) permanece sin datos en esta fuente y tiene una [estimación aparte](../providencia/README.md).

Desde la raíz del repositorio:

```bash
.venv/bin/python scripts/processing/calculate_weekly_precipitation.py --validate-only
.venv/bin/python scripts/processing/calculate_weekly_precipitation.py
```

`--start-year`, `--end-year` y `--municipality` delimitan la ejecución; `--overwrite` regenera salidas existentes.
