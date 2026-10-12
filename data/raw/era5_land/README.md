# Ficha técnica: ERA5-Land Daily UTC para Colombia

| Campo | Descripción |
| --- | --- |
| Fuente | [Earth Data Hub, ERA5-Land Daily](https://earthdatahub.destine.eu/collections/era5/datasets/era5-land-daily), Zarr `https://data.earthdatahub.destine.eu/era5/era5-land-daily-utc-v1.zarr` |
| Producto local | `era5_land_daily_AAAA.nc`, NetCDF anual; `era5_land_daily_AAAA_MM.nc` para meses de prueba y bordes |
| Periodo | 2007–2025; 2006-12 y 2026-01 completan las semanas epidemiológicas extremas |
| Resolución | 0,1°; un valor por día, **00:00–23:59 UTC** |
| Cobertura | Rectángulo derivado del [GeoJSON municipal](../municipios/README.md), con margen de 0,1°; no es el Zarr global |
| Variables y unidades originales | `t2m` y `d2m`: K; `sp`: Pa; `tp`: m de agua acumulada por día |
| Generado por | [`scripts/download/download_era5_land.py`](../../../scripts/download/download_era5_land.py) |
| Destino de procesamiento | [Clima semanal municipal](../../processed/climate/README.md) |

## Procedencia y significado de los valores

**ERA5** es un reanálisis producido por ECMWF para el servicio climático Copernicus. Combina observaciones históricas de estaciones, globos meteorológicos, aeronaves, barcos, boyas y satélites con un modelo físico de la atmósfera. Mediante *asimilación de datos*, el sistema ajusta periódicamente una estimación del estado atmosférico con las observaciones disponibles y genera campos continuos en espacio y tiempo. Así, el valor de una celda es una **estimación del sistema**, no la lectura de un instrumento ubicado en esa celda. La disponibilidad y calidad de observaciones varían por lugar y época. Véanse la [explicación de ERA5 de Copernicus](https://cds.climate.copernicus.eu/datasets/reanalysis-era5-single-levels?tab=overview) y la [documentación técnica de ECMWF](https://confluence.ecmwf.int/pages/viewpage.action?pageId=179741903).

**ERA5-Land** toma los campos meteorológicos de ERA5 como condiciones de entrada y ejecuta de nuevo el componente de superficie terrestre a mayor resolución. Esa ejecución terrestre **no asimila observaciones directamente**: las observaciones influyen a través de los campos de ERA5 que la alimentan. Su resolución de cálculo es aproximadamente 9 km; Earth Data Hub distribuye aquí los valores en una grilla regular de 0,1°. Una grilla más fina no equivale a tener más estaciones de medición. Véase la [documentación de ERA5-Land de ECMWF](https://confluence.ecmwf.int/pages/viewpage.action?pageId=505384848).

En estos archivos, `t2m` representa la temperatura estimada del aire a 2 m y `d2m` la temperatura estimada del punto de rocío a 2 m; ambas se obtienen del cálculo terrestre de ERA5-Land. `sp` (presión superficial) y `tp` (precipitación **acumulada**) son campos meteorológicos de entrada procedentes de ERA5, interpolados a la grilla de ERA5-Land: **no los genera el modelo de superficie terrestre**. Ninguna de estas celdas equivale a la lectura directa de una estación o pluviómetro. La [tabla de parámetros de ECMWF](https://confluence.ecmwf.int/pages/viewpage.action?pageId=505384848) identifica qué campos se usan como entrada y distingue variables instantáneas de acumuladas. Para evaluar exactitud local, especialmente en costas, islas y relieve complejo, conviene comparar las estimaciones con estaciones disponibles.

El [producto diario de Earth Data Hub](https://earthdatahub.destine.eu/collections/era5/datasets/era5-land-daily) se deriva del ERA5-Land **horario**: promedia por día UTC variables instantáneas como `t2m` y entrega el total diario para `tp`. Earth Data Hub prepara y distribuye el producto; no realiza las observaciones meteorológicas originales.

El descargador usa `xarray`/Zarr y Dask para seleccionar solo estas cuatro variables, el periodo y las celdas del recorte. Conserva las unidades y atributos de Earth Data Hub; no convierte temperaturas ni precipitación y no calcula agregados municipales. Acepta longitudes de origen 0–360° y latitud en cualquiera de los dos órdenes. La grilla se comprueba entre archivos. Las fechas diarias **no se trasladan a UTC−05:00**.

## Reproducción

Desde la raíz del repositorio, con `scripts/requirements.txt` instalado y la API key en `~/.netrc` para `data.earthdatahub.destine.eu` (o `EARTHDATAHUB_API_KEY`):

```bash
.venv/bin/python scripts/download/download_era5_land.py --month 2024-03
.venv/bin/python scripts/download/download_era5_land.py --start-year 2024 --end-year 2024
.venv/bin/python scripts/download/download_era5_land.py
.venv/bin/python scripts/download/download_era5_land.py --month 2006-12
.venv/bin/python scripts/download/download_era5_land.py --month 2026-01
```

`--month` crea un archivo mensual separado; un mes interior no sustituye su archivo anual. El modo normal abarca 2007–2025. `--validate-only` valida el GeoJSON y muestra el plan sin consultar el Zarr; `--overwrite` reemplaza un archivo existente. Cada descarga se escribe como `.part`, se valida por fechas UTC, variables, unidades, coordenadas, grilla y datos legibles, y después se renombra. Un archivo anual completo y válido se omite al reanudar.

El producto anterior obtenido de CDS utilizaba días UTC−05:00. Este producto usa días UTC, así que los valores semanales pueden cambiar cerca de los límites de día y semana. La unión por fecha con [CHIRPS](../precipitation/chirps/README.md) alinea etiquetas diarias; no garantiza que cada observación incorporada en CHIRPS represente exactamente la misma ventana horaria.
