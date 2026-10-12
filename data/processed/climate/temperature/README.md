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
