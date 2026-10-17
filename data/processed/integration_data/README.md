# Dataset integrado semanal municipal

`sivigila_integrado_semanal_municipal.parquet/` es un **dataset Parquet de Spark** (un directorio con archivos `part-*.parquet`), producido por [`scripts/processing/integrate_sivigila.py`](../../../scripts/processing/integrate_sivigila.py). El script reproduce las transformaciones de [`notebooks/integration_sivigila.ipynb`](../../../notebooks/integration_sivigila.ipynb) y sobrescribe la salida al ejecutarse. La tabla conserva las filas de SIVIGILA; las demás fuentes se incorporan mediante uniones izquierdas.

## Entradas y uniones

| Fuente | Ruta | Unión |
| --- | --- | --- |
| Casos semanales de SIVIGILA | `data/processed/sivigila/sivigila_weekly_municipal_AAAA.parquet` | Tabla base |
| Población municipal | `data/processed/population/population_municipal_2007_2025.csv` | Municipio y año epidemiológico |
| Cobertura de vacunación | `data/processed/vaccine_coverage/coberturas_municipales_2016_2025.csv` | Municipio y año epidemiológico |
| Precipitación CHIRPS satelital | `data/processed/chirps_precipitation/chirps_precipitation_weekly_municipal_sat_AAAA.parquet` | Municipio, año y semana epidemiológica |
| Humedad, precipitación y temperatura ERA5-Land | `data/processed/climate/{humidity,precipitation,temperature}/` | Municipio, año y semana epidemiológica |
| Estimaciones de Providencia | `data/processed/climate/providencia/{humidity,precipitation,temperature}/` | Municipio, año y semana epidemiológica |

Se esperan archivos anuales de 2007 a 2025. Las tasas `incidencia_*_100k` dividen los casos por la población correspondiente y multiplican por 100.000. La cobertura de vacunación empieza en 2016; las filas sin coincidencia permanecen en la tabla con valores nulos en las columnas añadidas.

Providencia (`88564`) carece de valores climáticos en ERA5-Land. Sus valores nulos se completan con los archivos separados de ERA5 atmosférico horario. Para cada variable se conserva la fracción de área con datos de la fuente utilizada y se incluyen columnas `fuente_*` y `es_estimacion_*`. Estas series son **estimaciones de otra fuente y resolución**, no observaciones locales ni valores directamente equivalentes a ERA5-Land. CHIRPS permanece como una precipitación separada (`precipitacion_total_mm_chirps_sat`).

## Generación y lectura

Desde la raíz del repositorio, con el entorno del proyecto y Java 17:

```bash
.venv/bin/python scripts/processing/integrate_sivigila.py
```

El script toma las entradas relativas a la raíz del repositorio, independientemente del directorio de ejecución. Admite `--master`, `--driver-memory` y `--output` para ajustar Spark o la ruta de salida. Escribe el dataset con compresión Parquet predeterminada de Spark en `data/processed/integration_data/sivigila_integrado_semanal_municipal.parquet/`.

```python
from pyspark.sql import SparkSession

spark = SparkSession.builder.getOrCreate()
df = spark.read.parquet(
    "data/processed/integration_data/sivigila_integrado_semanal_municipal.parquet"
)
```

La generación local con las entradas actuales produjo **227.113 filas y 141 columnas**, que suman **1.251.524 casos**. La unidad de cada fila es una combinación presente en SIVIGILA de entidad DIVIPOLA de residencia y semana epidemiológica; la salida no representa todas las semanas posibles de todas las entidades. Incluye las islas y áreas no municipalizadas aceptadas por el procesamiento semanal de SIVIGILA.
