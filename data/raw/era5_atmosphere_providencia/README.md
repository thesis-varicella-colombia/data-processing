# Ficha técnica: ERA5 atmosférico horario para Providencia

| Campo | Descripción |
| --- | --- |
| Fuente | [Earth Data Hub, ERA5 single levels atmosphere](https://earthdatahub.destine.eu/collections/era5/datasets/era5-single-levels-atmosphere), Zarr `https://data.earthdatahub.destine.eu/era5/era5-single-levels-atmosphere-v0.zarr` |
| Producto local vigente | `era5_atmosphere_hourly_AAAA_MM.nc`, un NetCDF por mes |
| Periodo | 2006-12 a 2026-01 para las semanas epidemiológicas 2007–2025 |
| Resolución | 0,25°; una muestra por hora UTC |
| Cobertura | Recorte de 2 × 2 celdas alrededor del polígono municipal de Providencia (`88564`) en [GeoJSON/DIVIPOLA](../municipios/README.md), con margen de 0,25° |
| Variables y unidades originales | `t2m`, `d2m`: K; `sp`: Pa; `tp`: m de agua |
| Generado por | [`scripts/download/download_era5_providencia.py`](../../../scripts/download/download_era5_providencia.py) |
| Destino de procesamiento | [Días derivados y semanas estimadas de Providencia](../../processed/climate/providencia/README.md) |

## Procedencia y significado de los valores

Estos archivos proceden de **ERA5 atmosférico** de ECMWF, publicado para este proyecto por Earth Data Hub como un [subconjunto horario en Zarr](https://earthdatahub.destine.eu/collections/era5/datasets/era5-single-levels-atmosphere). ERA5 reconstruye el tiempo pasado combinando observaciones de estaciones, globos meteorológicos, aeronaves, barcos, boyas y satélites con un modelo físico de la atmósfera. La *asimilación de datos* ajusta el estado estimado del modelo con las observaciones disponibles; el resultado es un campo horario continuo, incluso donde no había un instrumento. Por eso cada valor descargado es una **estimación de reanálisis**, no una medición puntual realizada en Providencia. Véanse la [descripción de Copernicus](https://cds.climate.copernicus.eu/datasets/reanalysis-era5-single-levels?tab=overview) y la [documentación técnica de ECMWF](https://confluence.ecmwf.int/pages/viewpage.action?pageId=179741903).

`t2m` estima la temperatura del aire a 2 m, `d2m` el punto de rocío a 2 m y `sp` la presión superficial. Son variables instantáneas en su hora UTC. `tp` es precipitación acumulada producida por el modelo, no una lectura de pluviómetro en la isla; [ECMWF distingue la precipitación acumulada de las variables instantáneas](https://confluence.ecmwf.int/pages/viewpage.action?pageId=111151155). Earth Data Hub distribuye los campos de ERA5, pero no realiza las observaciones originales.

La grilla de 0,25° puede incluir una proporción importante de mar cerca de Providencia. Su valor representa la celda de ERA5 y puede diferir de una estación sobre la isla; la estimación municipal posterior se obtiene ponderando las celdas por su área de intersección con el polígono, como explica la [ficha del procesamiento](../../processed/climate/providencia/README.md). Es conveniente contrastarla con observaciones locales antes de interpretarla como clima observado.

El descargador selecciona solo las cuatro variables y las horas necesarias. Cada archivo mensual incluye **00:00 UTC del día siguiente al último día del mes** para poder cerrar la precipitación del último día: cada `tp` horario representa la hora que termina en su marca temporal, según [ECMWF](https://confluence.ecmwf.int/pages/viewpage.action?pageId=197702797). `t2m`, `d2m` y `sp` son variables instantáneas. Se conservan los atributos, unidades, coordenadas y horas UTC del producto; la conversión diaria ocurre en el [procesador](../../../scripts/processing/estimate_providencia.py). Las longitudes de origen 0–360° solo se adaptan durante la selección e intersección espacial.

## Reproducción

Con dependencias de `scripts/requirements.txt` y la API key ya configurada en `~/.netrc` para `data.earthdatahub.destine.eu` (o en `EARTHDATAHUB_API_KEY`), ejecutar desde la raíz:

```bash
.venv/bin/python scripts/download/download_era5_providencia.py --month 2024-03
.venv/bin/python scripts/download/download_era5_providencia.py
```

`--start-year` y `--end-year` delimitan años epidemiológicos; `--month` descarga solo un mes de prueba. `--validate-only` muestra el plan sin consultar el Zarr. Cada archivo se escribe como `.part`, se valida por horas, variables, unidades, grilla y presencia de datos, y se renombra al completar. Los archivos válidos se omiten al reanudar; `--overwrite` los regenera.

Se conservaron aquí archivos antiguos `era5_atmosphere_daily_AAAA_MM.nc` de una versión anterior. **No son la entrada vigente:** el procesador actual lee los `hourly` y escribe los días derivados bajo `data/processed/climate/providencia/daily/`. En la ejecución local hubo 230 NetCDF horarios (aproximadamente 19,66 MiB) para 2006-12 a 2026-01.
