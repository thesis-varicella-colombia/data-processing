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

## Diccionario de columnas

Los tipos siguientes corresponden al esquema del **Parquet generado actualmente**: `string` es texto, `date32` es fecha sin hora, `bool` es booleano, `double` es número de punto flotante y `int8`/`int16`/`int64` son enteros de 8/16/64 bits. En particular, algunos conteos `casos_*` se almacenan como `int8` por su rango observado; siguen siendo **conteos**, no indicadores booleanos. Los conteos de SIVIGILA se refieren a las notificaciones de la fila (entidad de residencia y semana reportada). Las categorías de distintos grupos pueden superponerse; los datos agregados por año o semana se repiten en las filas correspondientes. Los valores de fuentes unidas pueden ser nulos cuando no existe una coincidencia.

### Municipio y semana

| Columna | Tipo | Descripción |
| --- | --- | --- |
| `codigo_municipio` | `string` | Código DIVIPOLA de cinco dígitos de la entidad de residencia; incluye municipios, islas y áreas no municipalizadas aceptadas. |
| `ano_epidemiologico` | `int64` | Año epidemiológico `ANO` reportado por SIVIGILA; clave de unión con población y vacunación. |
| `semana_epidemiologica` | `int16` | Número de semana `SEMANA` reportado por SIVIGILA. |
| `nombre_municipio` | `string` | Nombre de la entidad de residencia según el DIVIPOLA local. |
| `codigo_departamento` | `string` | Código DIVIPOLA de dos dígitos del departamento de residencia. |
| `inicio_semana` | `date32` | Domingo inicial de la semana reportada, según el calendario epidemiológico del proyecto. |
| `fin_semana` | `date32` | Sábado final de esa semana, inclusive; puede caer en otro año calendario. |

### Casos

Todos los campos `casos_*` de esta sección son conteos de registros de varicela (evento 831), no tasas. El desglose usa los valores originales del CSV; la [ficha de SIVIGILA](../sivigila/README.md) documenta las homologaciones geográficas, exclusiones y limitaciones temporales. En las comparaciones geográficas, «mismo» y «otro» se refieren a la entidad DIVIPOLA de residencia tras homologar los códigos.

| Columna | Tipo | Descripción |
| --- | --- | --- |
| `casos_total` | `int64` | Total de notificaciones incluidas en la entidad y semana. |
| `casos_masculinos` | `int64` | Registros con `SEXO=M`. |
| `casos_femeninos` | `int64` | Registros con `SEXO=F`. |
| `casos_hospitalizados` | `int64` | Registros con `PAC_HOS=1`. |
| `casos_menor_1` | `int64` | Edad convertible a años menor de 1 año. |
| `casos_1_4` | `int64` | Edad de 1 a menos de 5 años. |
| `casos_5_14` | `int64` | Edad de 5 a menos de 15 años. |
| `casos_15_49` | `int64` | Edad de 15 a menos de 50 años. |
| `casos_50_mas` | `int64` | Edad de 50 años o más. |
| `casos_edad_desconocida` | `int64` | Edad no convertible a años con `EDAD` y `UNI_MED`. |
| `casos_cabecera` | `int64` | Registros en cabecera municipal (`AREA=1`). |
| `casos_centro_poblado` | `int64` | Registros en centro poblado (`AREA=2`). |
| `casos_rural` | `int8` | Registros en área rural dispersa (`AREA=3`). |
| `casos_contributivo` | `int64` | Régimen contributivo (`TIP_SS=C`). |
| `casos_subsidiado` | `int64` | Régimen subsidiado (`TIP_SS=S`). |
| `casos_excepcion` | `int64` | Régimen de excepción (`TIP_SS=P`). |
| `casos_especial` | `int64` | Régimen especial (`TIP_SS=E`). |
| `casos_no_asegurado` | `int64` | No asegurados (`TIP_SS=N`). |
| `casos_indigena` | `int64` | Pertenencia étnica indígena (`PER_ETN=1`). |
| `casos_rom` | `int64` | Pertenencia étnica Rrom (`PER_ETN=2`). |
| `casos_raizal` | `int64` | Pertenencia étnica raizal (`PER_ETN=3`). |
| `casos_palenquero` | `int64` | Pertenencia étnica palenquera (`PER_ETN=4`). |
| `casos_afro` | `int64` | Pertenencia étnica afrocolombiana (`PER_ETN=5`). |
| `casos_otro_etnico` | `int64` | Otra categoría étnica (`PER_ETN=6`). |
| `casos_estrato_1` | `int64` | Estrato socioeconómico 1. |
| `casos_estrato_2` | `int64` | Estrato socioeconómico 2. |
| `casos_estrato_3` | `int64` | Estrato socioeconómico 3. |
| `casos_estrato_4` | `int64` | Estrato socioeconómico 4. |
| `casos_estrato_5` | `int64` | Estrato socioeconómico 5. |
| `casos_estrato_6` | `int64` | Estrato socioeconómico 6. |
| `casos_discapacidad` | `int64` | Grupo poblacional discapacidad (`GP_DISCAPA=1`). |
| `casos_desplazados` | `int64` | Grupo poblacional desplazados (`GP_DESPLAZ=1`). |
| `casos_migrantes` | `int64` | Grupo poblacional migrantes (`GP_MIGRANT=1`). |
| `casos_carcelarios` | `int64` | Grupo poblacional carcelario (`GP_CARCELA=1`). |
| `casos_gestantes` | `int64` | Grupo poblacional gestantes (`GP_GESTAN=1`). |
| `casos_indigentes` | `int64` | Grupo poblacional indigentes (`GP_INDIGEN=1`); distinto de pertenencia étnica indígena. |
| `casos_icbf` | `int64` | Grupo poblacional ICBF (`GP_POBICFB=1`). |
| `casos_madres_comunitarias` | `int64` | Madres comunitarias (`GP_MAD_COM=1`). |
| `casos_desmovilizados` | `int64` | Grupo poblacional desmovilizados (`GP_DESMOVI=1`). |
| `casos_centros_psiquiatricos` | `int64` | Grupo poblacional centros psiquiátricos (`GP_PSIQUIA=1`). |
| `casos_victimas_violencia` | `int64` | Grupo poblacional víctimas de violencia (`GP_VIC_VIO=1`). |
| `casos_otros_grupos` | `int64` | Otros grupos poblacionales (`GP_OTROS=1`). |
| `casos_notificacion_rutinaria` | `int64` | Fuente de notificación rutinaria (`fuente=1`). |
| `casos_busqueda_activa_institucional` | `int8` | Fuente de búsqueda activa institucional (`fuente=2`). |
| `casos_vigilancia_intensificada` | `int8` | Fuente de vigilancia intensificada (`fuente=3`). |
| `casos_busqueda_activa_comunitaria` | `int8` | Fuente de búsqueda activa comunitaria (`fuente=4`). |
| `casos_investigaciones` | `int8` | Fuente de investigaciones (`fuente=5`). |
| `casos_notificados_mismo_municipio` | `int64` | Notificados en la misma entidad de residencia. |
| `casos_notificados_otro_municipio` | `int8` | Notificados en otra entidad DIVIPOLA válida. |
| `casos_municipio_notificacion_desconocido` | `int8` | Código de entidad de notificación no reconocido en el DIVIPOLA local. |
| `casos_ocurridos_en_colombia` | `int64` | País de ocurrencia Colombia (`COD_PAIS_O=170`), aunque la entidad sea desconocida. |
| `casos_ocurrencia_mismo_municipio_residencia` | `int64` | Ocurridos en Colombia en la misma entidad de residencia. |
| `casos_ocurrencia_otro_municipio` | `int64` | Ocurridos en Colombia en otra entidad DIVIPOLA válida. |
| `casos_ocurrencia_municipio_desconocido` | `int64` | Ocurridos en Colombia con entidad de ocurrencia no reconocida. |
| `casos_inicio_sintomas_fuera_semana_reportada` | `int64` | Fecha interpretable de inicio de síntomas fuera de la semana reportada. |
| `casos_inicio_sintomas_sin_fecha` | `int64` | Sin fecha interpretable de inicio de síntomas. |
| `casos_notificacion_fuera_semana_reportada` | `int64` | Fecha interpretable de notificación fuera de la semana reportada. |
| `casos_notificados_mismo_dia` | `int64` | Notificación el mismo día del inicio de síntomas. |
| `casos_notificados_1_3_dias` | `int64` | Notificación entre 1 y 3 días después del inicio de síntomas. |
| `casos_notificados_4_7_dias` | `int64` | Notificación entre 4 y 7 días después del inicio de síntomas. |
| `casos_notificados_mas_7_dias` | `int64` | Notificación más de 7 días después del inicio de síntomas. |
| `casos_notificados_antes_inicio_sintomas` | `int64` | Fecha de notificación anterior a la de inicio de síntomas. |
| `casos_sin_fecha_para_demora` | `int64` | Falta una fecha interpretable para calcular la demora entre síntomas y notificación. |
| `casos_clasificacion_inicial_sospechosos` | `int64` | Clasificación inicial sospechosa (`TIP_CAS=1`). |
| `casos_clasificacion_inicial_probables` | `int64` | Clasificación inicial probable (`TIP_CAS=2`). |
| `casos_clasificacion_inicial_confirmados_laboratorio` | `int64` | Clasificación inicial confirmada por laboratorio (`TIP_CAS=3`). |
| `casos_clasificacion_inicial_confirmados_clinica` | `int64` | Clasificación inicial confirmada por clínica (`TIP_CAS=4`). |
| `casos_clasificacion_inicial_confirmados_nexo` | `int8` | Clasificación inicial confirmada por nexo (`TIP_CAS=5`). |
| `casos_vivos` | `int64` | Condición final vivo (`CON_FIN=1`). |
| `casos_fallecidos` | `int8` | Condición final fallecido (`CON_FIN=2`). |
| `casos_condicion_desconocida` | `int8` | Condición final distinta de vivo o fallecido, o sin dato. |
| `casos_ajuste_sin_ajuste` | `int64` | Código de ajuste `AJUSTE=0`. |
| `casos_ajuste_confirmados_laboratorio` | `int8` | Código de ajuste `AJUSTE=3` (confirmación por laboratorio). |
| `casos_ajuste_confirmados_clinica` | `int64` | Código de ajuste `AJUSTE=4` (confirmación clínica). |
| `casos_ajuste_confirmados_nexo` | `int8` | Código de ajuste `AJUSTE=5` (confirmación por nexo). |
| `casos_ajuste_otro_ajuste` | `int8` | Código de ajuste `AJUSTE=7` (otro ajuste). |
| `casos_fuerzas_armadas` | `int8` | Al menos uno de `FM_FUERZA`, `FM_UNIDAD` o `FM_GRADO` tiene contenido. |
| `prop_notificados_fuera_municipio` | `double` | `casos_notificados_otro_municipio / casos_total`; proporción entre 0 y 1. |

### Población e incidencia

Las poblaciones son **personas estimadas o proyectadas** por entidad y año, repetidas en cada semana con casos. Las incidencias son casos reportados por cada 100.000 personas del denominador indicado; quedan nulas si falta el denominador o este es cero. Para `incidencia_rural_100k`, el numerador suma casos de centro poblado y rural disperso, de acuerdo con la definición de la población rural de origen.

| Columna | Tipo | Descripción |
| --- | --- | --- |
| `poblacion_total` | `int64` | Población total de la entidad y año. |
| `poblacion_hombres` | `int64` | Población de hombres de todas las edades. |
| `poblacion_mujeres` | `int64` | Población de mujeres de todas las edades. |
| `poblacion_cabecera` | `int64` | Población en cabecera municipal. |
| `poblacion_rural` | `int64` | Población en centros poblados y rural disperso. |
| `poblacion_menor_1` | `int64` | Población total menor de 1 año. |
| `poblacion_1_4` | `int64` | Población total de 1 a 4 años. |
| `poblacion_5_14` | `int64` | Población total de 5 a 14 años. |
| `poblacion_15_49` | `int64` | Población total de 15 a 49 años. |
| `poblacion_50_mas` | `int64` | Población total de 50 años o más. |
| `poblacion_hombres_menor_1` | `int64` | Hombres menores de 1 año. |
| `poblacion_hombres_1_4` | `int64` | Hombres de 1 a 4 años. |
| `poblacion_hombres_5_14` | `int64` | Hombres de 5 a 14 años. |
| `poblacion_hombres_15_49` | `int64` | Hombres de 15 a 49 años. |
| `poblacion_hombres_50_mas` | `int64` | Hombres de 50 años o más. |
| `poblacion_mujeres_menor_1` | `int64` | Mujeres menores de 1 año. |
| `poblacion_mujeres_1_4` | `int64` | Mujeres de 1 a 4 años. |
| `poblacion_mujeres_5_14` | `int64` | Mujeres de 5 a 14 años. |
| `poblacion_mujeres_15_49` | `int64` | Mujeres de 15 a 49 años. |
| `poblacion_mujeres_50_mas` | `int64` | Mujeres de 50 años o más. |
| `incidencia_total_100k` | `double` | `casos_total / poblacion_total × 100.000`. |
| `incidencia_cabecera_100k` | `double` | `casos_cabecera / poblacion_cabecera × 100.000`. |
| `incidencia_rural_100k` | `double` | `(casos_centro_poblado + casos_rural) / poblacion_rural × 100.000`. |
| `incidencia_menor_1_100k` | `double` | `casos_menor_1 / poblacion_menor_1 × 100.000`. |
| `incidencia_1_4_100k` | `double` | `casos_1_4 / poblacion_1_4 × 100.000`. |
| `incidencia_5_14_100k` | `double` | `casos_5_14 / poblacion_5_14 × 100.000`. |
| `incidencia_15_49_100k` | `double` | `casos_15_49 / poblacion_15_49 × 100.000`. |
| `incidencia_50_mas_100k` | `double` | `casos_50_mas / poblacion_50_mas × 100.000`. |
| `incidencia_masculina_100k` | `double` | `casos_masculinos / poblacion_hombres × 100.000`. |
| `incidencia_femenina_100k` | `double` | `casos_femeninos / poblacion_mujeres × 100.000`. |

### Vacunación

Estas variables son anuales y se repiten por semana. El año de unión corresponde al **año de análisis asignado**, uno posterior al año de la hoja PAI original; por ejemplo, 2016 usa la hoja de 2015. La cobertura publicada se conserva como porcentaje, sin recalcularla ni limitarla a 100 %. Consulte la [ficha de vacunación](../vaccine_coverage/README.md).

| Columna | Tipo | Descripción |
| --- | --- | --- |
| `meta_pob_1_anio` | `double` | Meta de población para la dosis única de varicela al año de edad. |
| `varicela_un_anio_dosis_unica` | `double` | Dosis únicas de varicela al año de edad reportadas por PAI. |
| `%_varicela_un_anio_dosis_unica` | `double` | Cobertura publicada de la dosis única al año de edad, en %. |
| `meta_pob_5_anios` | `double` | Meta de población para el refuerzo de varicela a los cinco años. |
| `varicela_cinco_anios_refuerzo` | `double` | Dosis de refuerzo de varicela a los cinco años reportadas por PAI. |
| `%_varicela_cinco_anios_refuerzo` | `double` | Cobertura publicada del refuerzo a los cinco años, en %. |

### Clima

Estas variables corresponden a la misma entidad y semana epidemiológica. Las fracciones de área con datos van de 0 a 1 y expresan cobertura espacial y temporal de la grilla utilizada. La precipitación CHIRPS `sat` y la precipitación ERA5 son series distintas. Para Providencia (`88564`), los nulos de ERA5-Land pueden completarse con una **estimación de ERA5 atmosférico**; las columnas `fuente_*` y `es_estimacion_*` identifican esa procedencia. Las marcas de fuente pueden ser nulas si no hubo dato para precipitación o temperatura; en humedad el integrador marca ERA5-Land por defecto cuando no se aplicó la estimación. Consulte las fichas de [CHIRPS](../chirps_precipitation/README.md), [ERA5-Land](../climate/README.md) y [Providencia](../climate/providencia/README.md).

| Columna | Tipo | Descripción |
| --- | --- | --- |
| `precipitacion_total_mm_chirps_sat` | `double` | Suma semanal de precipitación diaria CHIRPS `sat`, media espacial ponderada por área; mm. |
| `fraccion_area_con_datos_chirps_sat` | `double` | Fracción de área y días con datos válidos CHIRPS `sat`. |
| `dias_con_datos_chirps_sat` | `int16` | Días de la semana con alguna celda CHIRPS válida dentro de la entidad; de 0 a 7. |
| `dias_imputados_chirps_sat` | `int16` | Días tomados del archivo CHIRPS imputado de borde de 2026; de 0 a 3. |
| `humedad_relativa_media_pct` | `double` | Media semanal de humedad relativa ponderada por área y día; %. |
| `fraccion_area_con_datos_humedad_relativa_media_pct` | `double` | Fracción de área y días válidos para humedad relativa. |
| `humedad_especifica_media_g_kg` | `double` | Media semanal de humedad específica ponderada por área y día; g/kg. |
| `fraccion_area_con_datos_humedad_especifica_media_g_kg` | `double` | Fracción de área y días válidos para humedad específica. |
| `humedad_absoluta_media_g_m3` | `double` | Media semanal de densidad de vapor de agua ponderada por área y día; g/m³. |
| `fraccion_area_con_datos_humedad_absoluta_media_g_m3` | `double` | Fracción de área y días válidos para humedad absoluta. |
| `fuente_humedad` | `string` | Fuente utilizada para la humedad: `ERA5-Land_daily_UTC` o `ERA5_atmosphere_hourly_EDH`. |
| `es_estimacion_humedad` | `bool` | `true` si la humedad proviene de la estimación atmosférica para Providencia. |
| `precipitacion_total_mm_era5` | `double` | Suma semanal de precipitación diaria ERA5 ponderada por área; mm. |
| `fraccion_area_con_datos_precipitacion_era5` | `double` | Fracción de área y días válidos para precipitación ERA5. |
| `fuente_precipitacion` | `string` | Fuente de precipitación ERA5: `ERA5-Land_daily_UTC` o `ERA5_atmosphere_hourly_EDH`. |
| `es_estimacion_precipitacion` | `bool` | `true` si la precipitación ERA5 proviene de la estimación para Providencia. |
| `temperatura_media_c_era5` | `double` | Media semanal de temperatura del aire ponderada por área y día; °C. |
| `fraccion_area_con_datos_temperatura_era5` | `double` | Fracción de área y días válidos para temperatura ERA5. |
| `fuente_temperatura` | `string` | Fuente de temperatura: `ERA5-Land_daily_UTC` o `ERA5_atmosphere_hourly_EDH`. |
| `es_estimacion_temperatura` | `bool` | `true` si la temperatura proviene de la estimación para Providencia. |
