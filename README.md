# Procesamiento de datos de clima y varicela en Colombia

Este repositorio prepara series semanales por municipio para estudiar la relación entre el clima y las notificaciones de varicela individual (evento 831) en Colombia durante 2007–2025. Descarga datos climáticos, transforma los microdatos de Sivigila y genera archivos Parquet por año epidemiológico. También procesa las proyecciones anuales de población municipal del DANE para usarlas como denominadores en el análisis de incidencia.

El [catálogo de datos](data/README.md) describe las variables, unidades, fuentes y limitaciones de cada conjunto.

## Estructura

| Ruta | Contenido |
| --- | --- |
| [`scripts/download/`](scripts/download/) | Descarga de ERA5-Land, ERA5 atmosférico para Providencia y CHIRPS. |
| [`scripts/processing/`](scripts/processing/) | Cálculo climático semanal, estimación de Providencia y procesamiento de Sivigila y población. |
| [`data/raw/`](data/raw/) | Fuentes originales y sus fichas técnicas. |
| [`data/processed/`](data/processed/) | Resultados semanales y descripción de sus métodos. |
| [`notebooks/`](notebooks/) | Cuadernos de exploración de población y Sivigila, e integración de ambos conjuntos. |
| [`tests/`](tests/) | Pruebas de los descargadores y procesadores. |

Algunos datos voluminosos y fuentes originales están excluidos de Git. Una copia nueva del repositorio requiere obtener esas entradas antes de ejecutar los procesadores. Consulte las fichas de [geografía municipal](data/raw/municipios/README.md), [Sivigila](data/raw/sivigila/README.md) y [población DANE](data/raw/population/README.md) para preparar los archivos locales.

## Preparación

Se requiere Python 3.10 o posterior. Desde la raíz del repositorio:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r scripts/requirements.txt
```

Las descargas de ERA5 desde Earth Data Hub requieren una clave de API en `EARTHDATAHUB_API_KEY` o en `~/.netrc` para `data.earthdatahub.destine.eu`. Los scripts de CHIRPS descargan datos públicos sin esa clave. Las fichas de [ERA5-Land](data/raw/era5_land/README.md), [ERA5 para Providencia](data/raw/era5_atmosphere_providencia/README.md) y [CHIRPS](data/raw/precipitation/chirps/README.md) detallan cada fuente.

## Flujo de trabajo

Los comandos siguientes se ejecutan desde la raíz y, salvo que se indiquen años, trabajan sobre 2007–2025.

1. Obtenga el CSV DIVIPOLA y el GeoJSON municipal MGN 2025 según la [ficha geográfica](data/raw/municipios/README.md). Son necesarios para los cálculos por municipio.
2. Descargue ERA5-Land, incluidos los meses de borde que completan las semanas inicial y final:

   ```bash
   .venv/bin/python scripts/download/download_era5_land.py --validate-only
   .venv/bin/python scripts/download/download_era5_land.py
   .venv/bin/python scripts/download/download_era5_land.py --month 2006-12
   .venv/bin/python scripts/download/download_era5_land.py --month 2026-01
   ```

3. Genere los tres productos climáticos semanales:

   ```bash
   .venv/bin/python scripts/processing/calculate_weekly_temperature.py
   .venv/bin/python scripts/processing/calculate_weekly_humidity.py
   .venv/bin/python scripts/processing/calculate_weekly_precipitation.py
   ```

4. Para Sivigila, descargue los Excel anuales del evento 831 como explica su [ficha](data/raw/sivigila/README.md), guárdelos en `data/raw/sivigila/excel/` y ejecute:

   ```bash
   .venv/bin/python scripts/processing/convert_sivigila_excel_to_csv.py
   .venv/bin/python scripts/processing/calculate_weekly_sivigila.py
   ```

5. Descargue los dos libros Excel municipales del DANE indicados en la [ficha de población](data/raw/population/README.md), guárdelos en `data/raw/population/` y genere el CSV municipal:

   ```bash
   .venv/bin/python scripts/processing/process_population.py
   ```

La salida climática queda en `data/processed/climate/{temperature,humidity,precipitation}/` y la de casos en `data/processed/sivigila/`. Cada producto tiene un Parquet por año; Sivigila también genera informes `quality_report_AAAA.json`. Los scripts de cálculo semanal aceptan `--start-year`, `--end-year`, `--validate-only` y `--overwrite`; los climáticos admiten además `--municipality CODIGO`. Consulte la [metodología climática](data/processed/climate/README.md) y la [ficha del agregado Sivigila](data/processed/sivigila/README.md) antes de unir las tablas.

El procesador de población crea un único archivo, [`population_municipal_2007_2025.csv`](data/processed/population/population_municipal_2007_2025.csv), con una fila por municipio y año, y columnas de población total, por sexo, área y grupo de edad. El notebook [`population_explore.ipynb`](notebooks/population_explore.ipynb) muestra la transformación; [`integration_sivigila.ipynb`](notebooks/integration_sivigila.ipynb) lee este CSV y lo cruza con el agregado semanal de Sivigila por código municipal y año. La [ficha de población procesada](data/processed/population/README.md) describe sus variables.

### Fuentes y productos adicionales

- **Providencia:** ERA5-Land no aporta celdas válidas para el municipio `88564`. La [estimación separada](data/processed/climate/providencia/README.md) usa ERA5 atmosférico horario. Se obtiene con `download_era5_providencia.py` y se procesa con `estimate_providencia.py`; sus Parquet se guardan aparte e identifican la fuente y el carácter estimado del dato.
- **CHIRPS:** `scripts/download/download_chirps_precipitation.py` descarga precipitación diaria CHIRPS v3 Final/rnl. Consulte su [ficha](data/raw/precipitation/chirps/README.md). El procesador semanal de precipitación indicado arriba usa `tp` de ERA5-Land; CHIRPS es una fuente adicional, no su entrada.
- **Vacunación:** las coberturas PAI están descritas en su [ficha de origen](data/raw/vaccine_coverage/README.md); este repositorio no incluye un procesador para esa fuente.

## Interpretación y pruebas

Las semanas epidemiológicas van de domingo a sábado y la semana 1 contiene el 4 de enero. Los días de ERA5 usados aquí están etiquetados en UTC. Los registros Sivigila se agrupan por el año y la semana **reportados** en sus microdatos; los conteos representan notificaciones. Las poblaciones DANE son estimaciones anuales que el notebook de integración usa como denominadores de incidencia por 100.000 habitantes. La [ficha del agregado](data/processed/sivigila/README.md) documenta discrepancias entre semanas reportadas y fechas individuales que deben revisarse al cruzar casos con clima.

Para ejecutar las pruebas locales:

```bash
.venv/bin/python -m unittest discover -s tests
```
