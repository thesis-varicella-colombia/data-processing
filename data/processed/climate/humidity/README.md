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
