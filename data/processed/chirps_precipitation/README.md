# Precipitación semanal municipal CHIRPS v3

Este producto agrega los NetCDF diarios [CHIRPS v3.0 Final](../../raw/precipitation/chirps/README.md) a municipios de Colombia y semanas epidemiológicas. La variante **`sat` es la alternativa principal para la sensibilidad frente a ERA5**; la serie `rnl` previa se conserva por separado. Lo genera [`calculate_weekly_chirps_precipitation.py`](../../../scripts/processing/calculate_weekly_chirps_precipitation.py), siguiendo la exploración de [`precipitation_raw_explore.ipynb`](../../../notebooks/precipitation_raw_explore.ipynb).

## Método

Las semanas van de **domingo a sábado** y la semana 1 contiene el 4 de enero, igual que en el [pipeline climático ERA5-Land](../climate/README.md). El intervalo de salida es 2007–2025 por año epidemiológico. Se lee también el día observado 2006-12-31 y, para completar la última semana de 2025, los días **imputados** 2026-01-01 a 2026-01-03. `dias_imputados` identifica las semanas que incluyen esos días.

El GeoJSON MGN 2025 en CRS84 se comprueba contra DIVIPOLA y se seleccionan solo entidades `MUNICIPIO`. Para cada celda CHIRPS de 0,05° que intersecta un municipio, se calcula el área geodésica de la intersección. Esos pesos se calculan una vez y se reutilizan mientras la grilla de los NetCDF sea idéntica. No se usan los centroides municipales; la geometría MGN 2025 se aplica a toda la serie sin armonizar cambios administrativos históricos.

Para cada municipio y día, `precip` se promedia espacialmente como `Σ(precip_celda × área_intersección válida) / Σ(área_intersección válida)`. Los valores no finitos o negativos se excluyen. Los **siete acumulados diarios municipales se suman** para producir el total semanal. CHIRPS ya proporciona acumulados diarios en mm: no se aplica la conversión `× 1000` de ERA5-Land. Si un municipio carece por completo de celdas válidas en algún día, `precipitacion_total_mm` queda nulo para esa semana.

`fraccion_area_con_datos` es `Σ(área válida diaria) / (7 × área municipal intersectada por la grilla)`, entre 0 y 1. Indica la cobertura espacial y temporal del cálculo; en costas e islas puede reflejar celdas sin datos CHIRPS sobre el mar. La fecha CHIRPS es una etiqueta diaria coherente para la desagregación, pero no garantiza que todas las estaciones usadas en el total pentadal observaran idénticas 24 horas UTC. `sat` usa IMERG para distribuir el total pentadal entre días y aporta mayor independencia respecto a la asignación diaria de ERA5 que `rnl`. **No es una medición totalmente independiente**: ambas variantes comparten los totales pentadales de CHIRPS y algunas pentadas hasta 2022 se rellenaron con ERA5 cuando faltaban datos infrarrojos. Consulte la [ficha de origen](../../raw/precipitation/chirps/README.md) para esa interpretación.

Para la sensibilidad, sustituya la precipitación ERA5-Land por CHIRPS `sat` en modelos separados y compare sobre las mismas filas municipio-semana. Si incluye ambas variables en un mismo modelo, evalúe su correlación y el aporte adicional de cada una; usar `sat` no garantiza ausencia de redundancia. Las semanas con `dias_imputados > 0` merecen un análisis separado o exclusión al comparar estimaciones observadas.

Como diagnóstico descriptivo de esta serie 2007–2025, se emparejaron las semanas por código municipal, año y número de semana con ERA5-Land y CHIRPS `rnl`. Se excluyó la semana con días imputados y las filas sin dato ERA5-Land; quedaron 1.092.082 observaciones de 1.102 municipios y 991 semanas. La correlación de Pearson **mediana por municipio** con ERA5-Land fue 0,611 para `sat` y 0,657 para `rnl`; en los 1.102 municipios la de `sat` fue menor. Esto describe menor similitud de las series semanales, pero no mide el aporte predictivo de cada variable ni demuestra ausencia de colinealidad en un modelo particular.

## Archivos y columnas

El script escribe un Parquet por año epidemiológico y variante en esta carpeta. `chirps_precipitation_weekly_municipal_sat_AAAA.parquet` identifica `sat`; los archivos anteriores `chirps_precipitation_weekly_municipal_AAAA.parquet` son `rnl`. Los archivos `sat` también incluyen `variante_chirps = "sat"`.

| Columna | Tipo | Descripción |
| --- | --- | --- |
| `codigo_municipio` | `large_string` | Código DIVIPOLA de cinco dígitos, conservando ceros iniciales. |
| `nombre_municipio` | `large_string` | Nombre de la entidad municipal. |
| `ano_epidemiologico` | `int64` | Año epidemiológico de la semana; puede diferir del año calendario. |
| `semana_epidemiologica` | `int64` | Número de semana epidemiológica, de domingo a sábado; semana 1 contiene el 4 de enero. |
| `inicio_semana` | `large_string` | Domingo inicial, inclusive; texto ISO AAAA-MM-DD en estos Parquet climáticos. |
| `fin_semana` | `large_string` | Sábado final, inclusive; texto ISO AAAA-MM-DD en estos Parquet climáticos. |
| `precipitacion_total_mm` | `double` | Suma semanal de las medias municipales diarias ponderadas por área, en mm. |
| `fraccion_area_con_datos` | `double` | Fracción de área y días con datos válidos respecto de siete días, entre 0 y 1. |
| `dias_con_datos` | `uint8` | Días con alguna celda válida en el municipio, de 0 a 7. |
| `dias_imputados` | `uint8` | Días procedentes del borde imputado de 2026, de 0 a 3. |
| `variante_chirps` | `large_string` | Variante CHIRPS; sat en las salidas que incluyen esta columna. |

## Reproducción

Con los NetCDF y el GeoJSON/DIVIPOLA descritos en las fichas de [CHIRPS](../../raw/precipitation/chirps/README.md) y [municipios](../../raw/municipios/README.md), desde la raíz del repositorio:

```bash
.venv/bin/python scripts/processing/calculate_weekly_chirps_precipitation.py --validate-only
.venv/bin/python scripts/processing/calculate_weekly_chirps_precipitation.py
.venv/bin/python scripts/processing/calculate_weekly_chirps_precipitation.py --variant rnl --validate-only
```

`sat` es la variante por defecto; `--variant rnl` reproduce la serie anterior. `--start-year` y `--end-year` delimitan los años epidemiológicos; `--municipality CODIGO` limita el cálculo a municipios concretos; `--overwrite` reemplaza salidas de la variante seleccionada. El script también acepta `--input-dir` y `--output-dir`. Lee solo el recorte espacial necesario en bloques de hasta 31 días y escribe cada Parquet mediante un archivo temporal `.part`.

## Esquema de almacenamiento

Los tipos son los tipos físicos Arrow observados en los Parquet locales. `large_string` es texto, `int64` es entero de 64 bits y `double` es real de 64 bits. Las medidas sin datos válidos pueden ser nulas; una cobertura 0 indica ausencia de datos. La clave de cada archivo es (`codigo_municipio`, `ano_epidemiologico`, `semana_epidemiologica`).

`uint8` es un entero sin signo de 8 bits. Los archivos `sat` tienen 11 columnas; los `rnl` anteriores tienen las mismas diez primeras columnas y omiten `variante_chirps`. Las fechas de estos archivos son texto, aunque el integrador las combine con fechas Arrow de SIVIGILA.
