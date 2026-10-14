# Ficha técnica: precipitación diaria CHIRPS v3

## Fuente y producto

- **Productor:** Climate Hazards Center (CHC), University of California, Santa Barbara.
- **Producto:** CHIRPS v3.0 **Final**, precipitación diaria `sat` (principal para sensibilidad frente a ERA5) y `rnl` (serie anterior), en NetCDF.
- **Repositorios oficiales:** [`sat`](https://data.chc.ucsb.edu/products/CHIRPS/v3.0/daily/final/sat/netcdf/byYear/) y [`rnl`](https://data.chc.ucsb.edu/products/CHIRPS/v3.0/daily/final/rnl/netcdf/byYear/).
- **Resolución espacial:** grilla de 0,05°; cobertura terrestre casi global entre 60°N y 60°S.
- **Resolución temporal y unidad:** un valor por día; precipitación acumulada durante el día, en **mm** (no una tasa instantánea).
- **Periodo solicitado:** 2007-01-01 a 2025-12-31, inclusive (19 archivos anuales), más el día observado 2006-12-31 y tres días imputados de 2026-01-01 a 2026-01-03 para completar las semanas epidemiológicas de borde.
- **Fecha de descarga:** cada año y variante descargados se registran con fecha y hora UTC, URL y tamaño en [`download_manifest.csv`](download_manifest.csv). Los registros antiguos sin columna `variant` corresponden a `rnl`.

Para la sensibilidad frente a ERA5 se eligió `sat`: usa IMERG Late V07 para distribuir los totales pentadales de CHIRPS entre los días. `rnl` usa ERA5 para esa distribución. **Ambas conservan el mismo total por pentada, pero pueden asignar lluvia a días distintos**. Por ello `sat` aporta mayor independencia en la asignación diaria frente a ERA5, aunque no es una medición totalmente independiente: comparte los totales pentadales de CHIRPS con `rnl` y, en algunas zonas y periodos hasta 2022, CHIRPS rellenó pentadas con ERA5 cuando faltaban datos infrarrojos. Se usa la versión *Final* por su mayor control de calidad frente a *Prelim*. Véanse la [descripción oficial de CHIRPS v3](https://chc.ucsb.edu/data/chirps3), los [diagnósticos de relleno](https://www.chc.ucsb.edu/data/chirps3/diagnostics) y el [README oficial del producto diario](https://data.chc.ucsb.edu/products/CHIRPS/v3.0/daily/readme.txt).

## De dónde provienen los valores y cómo se estiman

CHIRPS significa *Climate Hazards Center Infrared Precipitation with Stations*. Cada valor de `precip` es una **estimación de precipitación para una celda de 0,05°**, no la lectura de un pluviómetro situado en esa celda. El Climate Hazards Center combina tres tipos de información:

1. **Climatología de precipitación (`CHPclim2`):** aporta una referencia espacial de cuánta lluvia suele recibir cada lugar. En CHIRPS v3 se construye con normales de estaciones e información satelital de largo plazo.
2. **Satélites geoestacionarios:** registran radiación infrarroja térmica. La duración de nubes con topes fríos ayuda a estimar dónde y cuánto pudo llover; el satélite **no mide directamente** los milímetros caídos en superficie. Con la climatología se forma la estimación satelital `CHIRP`.
3. **Pluviómetros de estaciones terrestres:** miden lluvia en ubicaciones concretas. Sus observaciones, después de controles de calidad y ajustes de medición, se combinan con `CHIRP` para formar `CHIRPS`. La versión **Final** incorpora más observaciones disponibles y una revisión más completa que la preliminar.

El método y las fuentes se describen en la [presentación oficial de CHIRPS v3](https://chc.ucsb.edu/data/chirps3); el [control de calidad y la densidad de estaciones](https://www.chc.ucsb.edu/data/chirps3/diagnostics) se documentan aparte. La cantidad de estaciones varía por lugar y fecha, por lo que también varía la información observacional disponible para corregir la estimación de cada región. La grilla fina no implica que exista una estación por celda.

**Cómo se obtiene el dato diario:** CHIRPS se construye principalmente para pentadas y meses. Para repartir el **total de cada pentada** entre sus días, `sat` usa la distribución diaria de IMERG Late V07 y `rnl` la de ERA5; no se añade una nueva corrección diaria con pluviómetros. Por ello, las dos variantes pueden coincidir en el total de una pentada y diferir en los acumulados de una semana que la atraviesa. Véanse la [explicación del productor](https://chc.ucsb.edu/data/chirps3) y el [README oficial del producto diario](https://data.chc.ucsb.edu/products/CHIRPS/v3.0/daily/readme.txt).

La fecha de un valor diario es una **etiqueta consistente de la desagregación**, no la prueba de que todos los pluviómetros aportaron mediciones de idénticas 24 horas UTC. El productor indica que no conoce la ventana local de observación de muchas estaciones. Al combinar esta serie con ERA5-Land por fecha se alinean días etiquetados, pero no se garantiza una ventana horaria observacional idéntica. La calidad local, en particular para lluvias extremas o regiones con pocas estaciones, debe evaluarse frente a observaciones independientes antes de interpretar una celda como medición puntual. [Fuente: Climate Hazards Center](https://chc.ucsb.edu/data/chirps3).

## Archivos y descarga

El archivo se genera con [`scripts/download/download_chirps_precipitation.py`](../../../../scripts/download/download_chirps_precipitation.py). Los archivos de esta carpeta siguen siendo datos diarios brutos; el [procesador municipal semanal](../../../processed/chirps_precipitation/README.md) genera un producto separado en `data/processed/chirps_precipitation/`.

El repositorio publica un NetCDF **anual y global** con el nombre `chirps-v3.0.VARIANTE.AAAA.days_p05.nc`. Las variantes se guardan en las mismas carpetas anuales con nombres distintos; no se reemplazan archivos `rnl`. No se descargan datos por municipio. Los archivos anuales rondan los 3,6–4,3 GiB, por lo que cada serie completa requiere aproximadamente 70–80 GiB de espacio.

Los 19 NetCDF anuales `rnl` de 2007–2025 y sus bordes se procesaron previamente. La descarga `sat` deja sus archivos en paralelo. El manifiesto registra las adquisiciones anuales.

```text
data/raw/precipitation/chirps/
├── README.md
├── download_manifest.csv             # aparece después de descargar
├── 2007/chirps-v3.0.rnl.2007.days_p05.nc
├── 2007/chirps-v3.0.sat.2007.days_p05.nc
├── ...
├── 2025/chirps-v3.0.rnl.2025.days_p05.nc
├── 2006/chirps-v3.0.rnl.2006.12.31.tif
├── 2006/chirps-v3.0.rnl.2006.epidemiological-border.observed.nc
├── 2006/chirps-v3.0.sat.2006.epidemiological-border.observed.nc
├── 2026/chirps-v3.0.rnl.2026.epidemiological-border.imputed.nc
└── 2026/chirps-v3.0.sat.2026.epidemiological-border.imputed.nc
```

Desde la raíz del repositorio:

```bash
uv pip install --python .venv/bin/python -r requirements.txt
.venv/bin/python scripts/download/download_chirps_precipitation.py --dry-run
.venv/bin/python scripts/download/download_chirps_precipitation.py --variant sat --workers 2
.venv/bin/python scripts/download/download_chirps_precipitation.py --variant rnl --dry-run
.venv/bin/python scripts/download/download_chirps_precipitation.py --start-year 2017 --end-year 2025 --workers 2 --include-2006-border
.venv/bin/python scripts/download/download_chirps_precipitation.py --border-only
```

El script usa `sat` por defecto y acepta `--variant sat|rnl`, `--start-year`, `--end-year`, `--output-dir`, `--workers` (1–4, por defecto 1; se recomienda probar 2), `--include-2006-border` y `--border-only`. `--include-2006-border` incluye el día observado 2006-12-31 aunque la descarga anual se reanude desde 2017; con varios workers se descarga en paralelo con los años pendientes cuando 2007 ya está disponible. `--border-only` obtiene únicamente ese día. El borde también se incluye automáticamente cuando `--start-year 2007`. Revisa los NetCDF ya presentes y omite los años válidos; descarga cada archivo primero como `.part`, lo valida con `xarray` y solo entonces le da el nombre definitivo. Si la transferencia se interrumpe, usa HTTP `Range` para continuar el `.part` existente: contrasta los últimos 64 KiB locales con la respuesta del servidor antes de anexar bytes. Si el servidor no admite reanudación o esos bytes no coinciden, el script se detiene y conserva el `.part` para revisión. Un `.part` completo se valida sin descargarlo otra vez. Los reintentos por errores transitorios también conservan el avance. El manifiesto registra la fecha real de cada **archivo anual** descargado; con varios hilos, su escritura se protege para no perder filas. Cada hilo usa una sesión HTTP propia.

`--workers 2` descarga **años diferentes** en paralelo; no parte un mismo archivo anual en dos conexiones. Puede mejorar el tiempo total si el servidor limita cada conexión, pero no necesariamente acelera el archivo de 2017 y puede ser peor si el cuello de botella es el ancho de banda compartido. Compare el progreso durante unos minutos antes de subir a 3 o 4. No ejecute dos instancias simultáneas sobre los mismos años o el mismo `.part`. Para aplicar la versión nueva a una descarga anterior, interrumpa el proceso con Ctrl+C (el `.part` se conserva) y vuelva a lanzar el comando indicado arriba; el archivo de 2017 retomará desde su tamaño actual. Los años completos anteriores se omiten.

Para el borde de 2006 se descarga **solo** el GeoTIFF diario oficial de 2006-12-31 de la variante seleccionada (por ejemplo, [sat](https://data.chc.ucsb.edu/products/CHIRPS/v3.0/daily/final/sat/2006/chirps-v3.0.sat.2006.12.31.tif)), de unos 15 MiB. Se conserva ese archivo fuente y se convierte a un NetCDF de un día con la grilla y los atributos de precipitación del anual CHIRPS 2007, cuya grilla debe coincidir con la georreferenciación del GeoTIFF. Los valores −9999 del TIFF pasan a `NaN`; la orientación norte→sur se invierte para la latitud ascendente del NetCDF. El archivo de borde de 2006 conserva la **estimación oficial de CHIRPS** para esa fecha; no es una imputación hecha por este proyecto ni una lectura directa de pluviómetro. Esta ruta evita transferir el anual 2006 de aproximadamente 4 GiB para extraer un único día. Si se ejecuta desde cero, primero debe estar listo 2007 para validar la grilla; el script ordena esos pasos automáticamente.

La ejecución previa de `rnl` generó el GeoTIFF de 15 MiB y el NetCDF de borde de 9,3 MiB (`time=1`, `latitude=2400`, `longitude=7200`, `precip` en mm/day, 2006-12-31). Como control de equivalencia de formatos, el GeoTIFF CHIRPS del 2007-01-01 y ese mismo día en el NetCDF anual 2007 coincidieron celda por celda, incluido `NaN`, tras invertir la latitud.

Para **2026-01-01, 2026-01-02 y 2026-01-03**, el script crea un NetCDF separado con valores **imputados**. Para cada celda de la grilla y cada día del mes, calcula la media aritmética de esa misma fecha en los 19 archivos CHIRPS Final de la variante seleccionada de **2007–2025**:

`P̂(2026-01-dd, celda) = media de P(año-01-dd, celda), año = 2007,…,2025`.

Se incluyen únicamente valores finitos y no negativos; si una celda no tiene ningún año válido, queda como `NaN`. Se exige la misma grilla en los 19 años y la presencia de todos los archivos anuales válidos. El archivo de 2026 registra en sus atributos el método, los años de referencia y `border_data_status=imputed_not_observed`. La media por fecha conserva una referencia estacional, pero **no estima el episodio meteorológico concreto de 2026**; cualquier total semanal que use estos tres días debe identificarse como parcialmente imputado. Si se requieren totales semanales observados, se deben reemplazar por datos diarios CHIRPS de 2026 cuando estén disponibles y recalcularlos.

Los días de borde se generan cuando el intervalo solicitado comienza en 2007 o termina en 2025, respectivamente. `--dry-run` muestra ambos pasos. `--end-year 2026` sigue sin admitirse mientras el año calendario esté en curso; estos tres días se producen por la ruta de imputación, no como un archivo anual 2026.

## Interpretación para el análisis posterior

Para sumar precipitación por semana epidemiológica, use los acumulados diarios de `precip` y documente la variante usada: `sat` distribuye el total pentadal con IMERG, mientras `rnl` usa ERA5. La fecha diaria se interpreta según la convención de desagregación descrita arriba. Toda semana que incluya 2026-01-01 a 2026-01-03 contiene valores **imputados por este proyecto** y debe identificarse como parcialmente imputada. El cálculo municipio-semana y la definición de semanas epidemiológicas quedan fuera de este descargador. [Fuente: CHC, documentación diaria](https://data.chc.ucsb.edu/products/CHIRPS/v3.0/daily/readme.txt).
