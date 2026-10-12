# Ficha técnica: estimación climática separada para Providencia (88564)

El producto [Earth Data Hub ERA5 single levels atmosphere](https://earthdatahub.destine.eu/collections/era5/datasets/era5-single-levels-atmosphere) se consulta desde `https://data.earthdatahub.destine.eu/era5/era5-single-levels-atmosphere-v0.zarr`. Es ERA5 atmosférico horario global a **0,25°**. Se extraen solo `t2m` y `d2m` (K), `sp` (Pa) y `tp` (m), en la grilla que rodea el polígono municipal CRS84 de Providencia. Las celdas se ponderan por el área geodésica real de intersección con ese polígono; no se usan centroides. Las coordenadas de la fuente son 0–360° y se normalizan a −180–180° solo para la intersección espacial. No se cambia la hora de los datos.

Esta **estimación** usa una fuente y resolución distintas de ERA5-Land (0,1°). Puede reflejar una celda atmosférica con alta fracción de mar y no es una observación local de la isla. Por eso se guarda aparte, con `fuente_dato=ERA5_atmosphere_hourly_EDH` y `es_estimacion=True`; los `NaN` y cobertura 0 de Providencia en los Parquet de ERA5-Land se conservan. Los resultados deben validarse con estaciones antes de interpretarlos como clima observado o de integrarlos al modelo. La grilla y el método de interpolación de ERA5 atmosférico cambian el significado físico de la serie respecto de ERA5-Land.

## Días UTC y precipitación

El día D contiene observaciones instantáneas de `t2m`, `d2m` y `sp` a D **00:00, 01:00, …, 23:00 UTC**. Cada media diaria requiere las 24 horas válidas. Para `tp`, [ECMWF especifica que el valor horario de ERA5 reanalysis acumula la precipitación de la hora que termina en su marca temporal](https://confluence.ecmwf.int/pages/viewpage.action?pageId=197702797). Por ello el total del día D suma **D 01:00 … D 23:00 y D+1 00:00 UTC**, con las 24 horas válidas. El archivo horario de cada mes incluye la hora 00:00 del día siguiente al último día del mes; esa hora solo se usa en el `tp` del último día. No se convierte a UTC−05:00 ni se reinterpreta la marca temporal.

La [ficha de los datos horarios de entrada](../../../raw/era5_atmosphere_providencia/README.md) documenta fuente, recorte, descarga y archivos. El [procesador](../../../../scripts/processing/estimate_providencia.py) lee exclusivamente `data/raw/era5_atmosphere_providencia/era5_atmosphere_hourly_AAAA_MM.nc` y escribe los días derivados en `daily/era5_atmosphere_daily_AAAA_MM.nc`, antes de calcular las semanas. Escribe primero `.part`, valida y renombra al finalizar. No requiere credenciales ni red. Los archivos diarios antiguos en `data/raw/era5_atmosphere_providencia/` no son entrada de este pipeline. Se necesitan meses de borde (2006-12 y 2026-01) para cubrir las semanas epidemiológicas de 2007–2025.

## Semanas y variables

Se reutiliza la definición del proyecto: domingo a sábado, semana 1 contiene el 4 de enero; `ano_epidemiologico`, `semana_epidemiologica`, `inicio_semana` y `fin_semana` admiten semanas que cruzan años. La temperatura es `t2m − 273,15` °C. La precipitación diaria es `tp × 1000` mm, se promedia entre celdas por área cada día y se **suman siete días**; falta un día completo ⇒ total semanal `NaN`. La temperatura y las humedades se calculan primero por celda y día y después se promedian entre celdas y días, ponderando por área. `NaN` no entra en numerador ni denominador. La cobertura es `área válida acumulada/(7 × área municipal cubierta por la grilla)`; en humedad se calcula por variable. La cobertura de estos archivos se refiere a **ERA5 atmosférico**, no a ERA5-Land.

La humedad usa las mismas ecuaciones y validaciones que [el pipeline principal](../README.md): `e_s(T)=611,2 exp(17,67 T_C/(T_C+243,5))` Pa, `e=e_s(Td)`, humedad relativa `100 e/e_s(T)` %, específica `1000 × 0,622 e/[sp−0,378 e]` g/kg y absoluta `1000 e/(461,5 T_K)` g/m³. Se usa `sp` de la celda; no se fija una presión estándar. [ECMWF describe la derivación de humedad desde temperatura, punto de rocío y presión](https://confluence.ecmwf.int/pages/viewpage.action?pageId=171416412). El método diario, aplicado sobre medias diarias, es el mismo del procesamiento ERA5-Land; no equivale al promedio de humedades horarias.

Se produce un Parquet por año epidemiológico en `temperature/temperature_weekly_providencia_AAAA.parquet`, `humidity/humidity_weekly_providencia_AAAA.parquet` y `precipitation/precipitation_weekly_providencia_AAAA.parquet`. Tienen las columnas de los productos principales más `fuente_dato` y `es_estimacion`. La secuencia 2007–2025 contiene 992 semanas. El script omite salidas existentes válidas salvo que se indique `--overwrite`.

## Ejecución

Desde la raíz del repositorio:

```bash
# Prueba de adquisición horaria y derivación diaria; no genera semanas parciales.
.venv/bin/python scripts/download/download_era5_providencia.py --month 2024-03
.venv/bin/python scripts/processing/estimate_providencia.py --month 2024-03

# Adquirir todo el periodo, incluidos meses de borde.
.venv/bin/python scripts/download/download_era5_providencia.py

# Derivar días UTC y procesar semanas desde los archivos horarios locales.
.venv/bin/python scripts/processing/estimate_providencia.py

# Reanudar sin volver a descargar meses completos.
.venv/bin/python scripts/download/download_era5_providencia.py --start-year 2024 --end-year 2024
.venv/bin/python scripts/processing/estimate_providencia.py --start-year 2024 --end-year 2024

# Regenerar derivados y salidas semanales del periodo.
.venv/bin/python scripts/processing/estimate_providencia.py --overwrite
```

`--start-year` y `--end-year` delimitan **años epidemiológicos** en ambos scripts. `--month` permite probar un único mes; en el procesador solo deriva el archivo diario. `--validate-only` muestra el plan de descarga o los horarios faltantes, según el script. `--overwrite` reemplaza los archivos del periodo indicado. El periodo completo implica descargar muchos meses horarios y puede requerir tiempo y transferencia de datos considerables; la prueba mensual permite medirlos antes.

## Verificación de la serie generada

En la ejecución local se guardaron **230 archivos horarios** (19,66 MiB) desde 2006-12 hasta 2026-01, en una grilla de 2 × 2 celdas. La derivación diaria ocupa aproximadamente 8,70 MiB para los 230 meses. Se generaron **19 Parquet por variable**, cada serie con **992 filas** para Providencia, sin faltantes y con cobertura 1 en este producto. Los rangos semanales observados fueron 25,170–29,076 °C; 70,564–87,784 % de humedad relativa; 14,542–20,403 g/kg de humedad específica; 17,044–23,545 g/m³ de humedad absoluta; y 0,021–249,594 mm de precipitación. Estos rangos son controles de plausibilidad, no una validación frente a observaciones locales. Los Parquet ERA5-Land de Providencia permanecen en `NaN` con cobertura 0.

Tras separar los scripts, se comprobaron los **230 diarios nuevos** contra los derivados previos: las cuatro variables coincidieron exactamente. Los tres Parquet semanales de 2024 recalculados desde la nueva ruta también coincidieron exactamente con las salidas existentes.
