# Datos semanales de varicela y clima en Colombia

Este repositorio construye una tabla municipio × semana epidemiológica para analizar notificaciones de varicela individual (Sivigila, evento 831) entre 2007 y 2025 junto con población, vacunación y clima. El resultado final se genera con [`scripts/processing/integrate_sivigila.py`](scripts/processing/integrate_sivigila.py) en [`data/processed/integration_data/`](data/processed/integration_data/README.md). El [catálogo de datos](data/README.md) describe las variables y unidades de las fuentes y productos.

## Requisitos y archivos que se obtienen manualmente

Se requiere **Python 3.12** y **Java 17** para PySpark. Desde la raíz del repositorio:

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

Los descargadores de ERA5 necesitan `EARTHDATAHUB_API_KEY` (o `EDH_API_KEY`) o credenciales para `data.earthdatahub.destine.eu` en `~/.netrc`. CHIRPS se descarga sin esa clave. Para ejecutar desde cero, prepare además estas entradas que no tienen descargador automático en el repositorio:

| Entrada | Ubicación esperada | Instrucciones |
| --- | --- | --- |
| Códigos DIVIPOLA y polígonos MGN 2025 | `data/raw/municipios/DIVIPOLA-_Códigos_municipios_20261007.csv` y `data/raw/municipios/MGN_ADM_MPIO_GRAFICO.geojson` | [Geografía municipal](data/raw/municipios/README.md) |
| Excel anuales de varicela, 2007–2025 | `data/raw/sivigila/excel/Datos_AAAA_831.xlsx` | [Microdatos Sivigila](data/raw/sivigila/README.md) y [diccionario](data/raw/sivigila/dic_datos.md) |
| Dos libros de proyecciones municipales DANE | `data/raw/population/` con los nombres exactos de la ficha | [Población DANE](data/raw/population/README.md) |
| Libro de coberturas PAI | `data/raw/vaccine_coverage/` con el nombre exacto de la ficha | [Vacunación PAI](data/raw/vaccine_coverage/README.md) |

Los archivos originales y varios resultados grandes están excluidos de Git; una clonación nueva no contiene necesariamente los datos necesarios. La descarga CHIRPS `sat` completa requiere aproximadamente **70–80 GiB** de espacio para sus NetCDF anuales. Compruebe espacio y credenciales antes de empezar.

## Datos y documentación

El [catálogo general](data/README.md) reúne variables, unidades y periodos. Estas son **todas las fichas README de datos** del repositorio:

| Etapa | Datos y README | Producto principal |
| --- | --- | --- |
| Entrada | [MGN 2025 y DIVIPOLA](data/raw/municipios/README.md) | Geometría y códigos municipales |
| Entrada | [Sivigila evento 831](data/raw/sivigila/README.md) | Excel anuales de notificaciones |
| Entrada | [Población DANE](data/raw/population/README.md) | Dos libros Excel municipales |
| Entrada | [Vacunación PAI](data/raw/vaccine_coverage/README.md) | Libro Excel de coberturas |
| Entrada | [ERA5-Land](data/raw/era5_land/README.md) | NetCDF diarios de 2007–2025 y meses de borde |
| Entrada | [ERA5 atmosférico para Providencia](data/raw/era5_atmosphere_providencia/README.md) | NetCDF horarios mensuales de 2006-12 a 2026-01 |
| Entrada | [CHIRPS v3](data/raw/precipitation/chirps/README.md) | NetCDF diarios `sat` y, opcionalmente, `rnl` |
| Método común | [Clima municipal](data/processed/climate/README.md) | Semanas epidemiológicas, fórmulas y ponderación espacial |
| Derivado | [Temperatura ERA5-Land](data/processed/climate/temperature/README.md) | `temperature_weekly_municipal_AAAA.parquet` |
| Derivado | [Humedad ERA5-Land](data/processed/climate/humidity/README.md) | `humidity_weekly_municipal_AAAA.parquet` |
| Derivado | [Precipitación ERA5-Land](data/processed/climate/precipitation/README.md) | `precipitation_weekly_municipal_AAAA.parquet` |
| Derivado | [Clima estimado para Providencia](data/processed/climate/providencia/README.md) | Temperatura, humedad y precipitación semanales separadas |
| Derivado | [Precipitación CHIRPS municipal](data/processed/chirps_precipitation/README.md) | `chirps_precipitation_weekly_municipal_sat_AAAA.parquet` |
| Derivado | [Casos Sivigila municipales](data/processed/sivigila/README.md) | `sivigila_weekly_municipal_AAAA.parquet` |
| Derivado | [Población municipal](data/processed/population/README.md) | `population_municipal_2007_2025.csv` |
| Derivado | [Coberturas de varicela](data/processed/vaccine_coverage/README.md) | `coberturas_municipales_2016_2025.csv` |
| Final | [Integración semanal municipal](data/processed/integration_data/README.md) | `sivigila_integrado_semanal_municipal.parquet/` |

Los [scripts de descarga](scripts/download/) obtienen ERA5 y CHIRPS; los [scripts de procesamiento](scripts/processing/) generan las tablas. Los [notebooks](notebooks/) sirven para exploración y contienen la [integración interactiva](notebooks/integration_sivigila.ipynb). La ruta reproducible para la salida final es el script de integración.

## Orden de ejecución desde cero

Ejecute los comandos **desde la raíz del repositorio**. Los valores predeterminados cubren 2007–2025. Complete primero los archivos manuales de la sección anterior: DIVIPOLA y MGN son necesarios para las descargas y agregaciones espaciales, y los Excel para sus respectivos procesadores.

### 1. Descargar ERA5-Land y calcular el clima municipal

La descarga anual no incluye los dos meses que completan las semanas epidemiológicas extremas; descárguelos explícitamente antes de procesar. La [ficha de entrada](data/raw/era5_land/README.md) y la [metodología climática](data/processed/climate/README.md) describen el recorte y las variables.

```bash
.venv/bin/python scripts/download/download_era5_land.py --validate-only
.venv/bin/python scripts/download/download_era5_land.py
.venv/bin/python scripts/download/download_era5_land.py --month 2006-12
.venv/bin/python scripts/download/download_era5_land.py --month 2026-01
.venv/bin/python scripts/processing/calculate_weekly_temperature.py
.venv/bin/python scripts/processing/calculate_weekly_humidity.py
.venv/bin/python scripts/processing/calculate_weekly_precipitation.py
```

Esto genera 19 Parquet por variable en `data/processed/climate/{temperature,humidity,precipitation}/`.

### 2. Descargar y procesar ERA5 atmosférico para Providencia

El descargador obtiene los meses horarios necesarios, incluidos los bordes; el procesador deriva días UTC y después las tres series semanales. Véanse las fichas de [entrada](data/raw/era5_atmosphere_providencia/README.md) y [estimación](data/processed/climate/providencia/README.md).

```bash
.venv/bin/python scripts/download/download_era5_providencia.py --validate-only
.venv/bin/python scripts/download/download_era5_providencia.py
.venv/bin/python scripts/processing/estimate_providencia.py
```

### 3. Descargar y agregar CHIRPS `sat`

El descargador incluye el día observado 2006-12-31 y genera los días **imputados** 2026-01-01 a 2026-01-03 necesarios para la última semana. La integración final usa `sat`. Consulte las fichas de [descarga](data/raw/precipitation/chirps/README.md) y [agregación](data/processed/chirps_precipitation/README.md).

```bash
.venv/bin/python scripts/download/download_chirps_precipitation.py --dry-run
.venv/bin/python scripts/download/download_chirps_precipitation.py --variant sat --workers 2
.venv/bin/python scripts/processing/calculate_weekly_chirps_precipitation.py --variant sat
```

Para reconstruir también la serie histórica adicional `rnl`, repita los dos últimos comandos con `--variant rnl`. **`rnl` no es una entrada del dataset integrado**.

### 4. Procesar los Excel de Sivigila

Los 19 archivos `Datos_AAAA_831.xlsx` deben estar en `data/raw/sivigila/excel/`. Primero se convierten a CSV y después se agregan por municipio, año y semana **reportados** en los microdatos. Consulte las fichas de [origen](data/raw/sivigila/README.md) y [agregado](data/processed/sivigila/README.md).

```bash
.venv/bin/python scripts/processing/convert_sivigila_excel_to_csv.py
.venv/bin/python scripts/processing/calculate_weekly_sivigila.py
```

### 5. Procesar población y vacunación

Con los libros DANE y PAI en las carpetas indicadas arriba, genere los dos CSV que utiliza la integración. Consulte las fichas de [población](data/processed/population/README.md) y [vacunación](data/processed/vaccine_coverage/README.md).

```bash
.venv/bin/python scripts/processing/process_population.py
.venv/bin/python scripts/processing/process_vaccine_coverage.py
```

La cobertura de vacunación integrada se etiqueta con el año siguiente al de la hoja PAI; por eso el CSV final cubre 2016–2025.

### 6. Generar el dataset integrado

Ejecute este paso **después** de completar todas las salidas anteriores:

```bash
.venv/bin/python scripts/processing/integrate_sivigila.py
```

El script verifica la presencia de los archivos anuales requeridos, calcula diez tasas de incidencia por 100.000 habitantes y une población y vacunación por municipio y año; CHIRPS y clima se unen por municipio, año y semana epidemiológica. Completa solo los valores climáticos nulos de Providencia (`88564`) con sus estimaciones separadas y conserva columnas de fuente, cobertura y carácter estimado. Escribe un **directorio Parquet de Spark** en `data/processed/integration_data/sivigila_integrado_semanal_municipal.parquet/`, sobrescribiendo la salida anterior. La [ficha del producto final](data/processed/integration_data/README.md) explica cómo leerlo.

## Interpretación y comprobación

Las semanas epidemiológicas van de domingo a sábado; la semana 1 contiene el 4 de enero. ERA5-Land y los días derivados para Providencia usan UTC. CHIRPS usa etiquetas diarias cuyo periodo observacional no siempre equivale a un día UTC. Los conteos Sivigila son **notificaciones**, y la población DANE son estimaciones anuales usadas como denominadores. La estimación atmosférica para Providencia tiene otra fuente y resolución que ERA5-Land. Consulte las fichas enlazadas para interpretar esas diferencias y los faltantes.

Para ejecutar las pruebas locales:

```bash
.venv/bin/python -m unittest discover -s tests
```
