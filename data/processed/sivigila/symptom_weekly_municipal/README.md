# Sivigila: casos por semana de inicio de síntomas y municipio de residencia

## Contenido y cobertura

Archivos `sivigila_symptom_weekly_municipal_AAAA.parquet`, uno por **año
epidemiológico calculado desde `INI_SIN`**. Fuente: [CSV individuales
de varicela, evento 831](../../../raw/sivigila/README.md). Cada fila
es una entidad DIVIPOLA de residencia × semana de la fecha individual;
solo aparecen combinaciones con casos. Se aplican las mismas reglas de
inclusión y homologación de residencia del [agregado de origen](../source_weekly_municipal/README.md).
Los 19 CSV de entrada tienen
`ANO` reportado entre 2007 y 2025.

El calendario es domingo–sábado y la semana 1 contiene el 4 de enero.
El año `AAAA` del archivo, `ano_epidemiologico`, `semana_epidemiologica`,
`inicio_semana` y `fin_semana` se calculan desde la fecha individual.
Por ello un archivo puede reunir casos de varios CSV de origen.
Los casos del año epidemiológico de borde 2006 se conservan.

Perfil de los archivos actuales: **20 Parquet, 218.963 filas, 1.195.823 casos, 1.121 entidades y 85 columnas**.

**55.701 casos incluidos en el agregado de origen no tienen
`INI_SIN` interpretable y se excluyen de este dataset**: 55.686
proceden del CSV de 2013 y 15 del de 2012. En 2013, `INI_SIN` se
lee como mes/día/año; en los demás CSV, como día/mes/año.
El total de este dataset representa casos con inicio conocido.

| Año epidemiológico | Filas entidad-semana | Casos (`casos_total`) |
| --- | ---: | ---: |
| 2006 | 29 | 117 |
| 2007 | 454 | 26.608 |
| 2008 | 8.090 | 63.211 |
| 2009 | 12.299 | 72.955 |
| 2010 | 12.536 | 73.714 |
| 2011 | 17.024 | 120.764 |
| 2012 | 16.675 | 99.834 |
| 2013 | 7.323 | 38.306 |
| 2014 | 16.964 | 107.883 |
| 2015 | 16.877 | 110.715 |
| 2016 | 17.477 | 111.981 |
| 2017 | 16.197 | 86.389 |
| 2018 | 15.230 | 74.982 |
| 2019 | 14.632 | 67.236 |
| 2020 | 6.319 | 18.075 |
| 2021 | 5.478 | 14.348 |
| 2022 | 7.817 | 22.647 |
| 2023 | 9.824 | 31.596 |
| 2024 | 8.372 | 24.911 |
| 2025 | 9.346 | 29.551 |
| **Total** | **218.963** | **1.195.823** |

## Columnas, tipos y nulos

**Las 85 columnas tienen 0 nulos físicos** en estos Parquet. Esto no
significa que todas las variables clínicas originales estén completas:
varios `casos_*` cuentan valores ausentes o desconocidos dentro de los
grupos. Los indicadores `casos_inicio_sintomas_fuera_semana_reportada`
y `casos_notificacion_fuera_semana_reportada` siguen comparando con
**`ANO`/`SEMANA` originales del CSV**, no con la semana de esta fila.
Los tipos listados son los tipos físicos Arrow observados en los
archivos actuales; `casos_*` son conteos, incluso si un tipo fuera `int8`.

| Columna | Tipo Arrow observado | Nulos | Descripción |
| --- | --- | ---: | --- |
| `codigo_municipio` | `large_string` | 0 | Código DIVIPOLA de cinco dígitos de la entidad de residencia; incluye municipios, islas y áreas no municipalizadas aceptadas. |
| `nombre_municipio` | `large_string` | 0 | Nombre de la entidad de residencia según el DIVIPOLA local. |
| `codigo_departamento` | `large_string` | 0 | Código DIVIPOLA de dos dígitos del departamento de residencia. |
| `ano_epidemiologico` | `int64` | 0 | Año epidemiológico calculado desde `INI_SIN`; puede diferir de `ANO` del CSV. |
| `semana_epidemiologica` | `int16` | 0 | Semana epidemiológica calculada desde `INI_SIN` con calendario domingo–sábado. |
| `inicio_semana` | `date32[day]` | 0 | Domingo inicial de la semana calculada desde `INI_SIN`. |
| `fin_semana` | `date32[day]` | 0 | Sábado final de la semana calculada desde `INI_SIN`. |
| `casos_total` | `int64` | 0 | Casos incluidos cuya fecha `INI_SIN` corresponde a esta entidad de residencia y semana. |
| `casos_masculinos` | `int64` | 0 | Registros con `SEXO=M`. |
| `casos_femeninos` | `int64` | 0 | Registros con `SEXO=F`. |
| `casos_hospitalizados` | `int64` | 0 | Registros con `PAC_HOS=1`. |
| `casos_menor_1` | `int64` | 0 | Edad convertible a años menor de 1 año. |
| `casos_1_4` | `int64` | 0 | Edad de 1 a menos de 5 años. |
| `casos_5_14` | `int64` | 0 | Edad de 5 a menos de 15 años. |
| `casos_15_49` | `int64` | 0 | Edad de 15 a menos de 50 años. |
| `casos_50_mas` | `int64` | 0 | Edad de 50 años o más. |
| `casos_edad_desconocida` | `int64` | 0 | Edad no convertible a años con `EDAD` y `UNI_MED`. |
| `casos_cabecera` | `int64` | 0 | Registros en cabecera municipal (`AREA=1`). |
| `casos_centro_poblado` | `int64` | 0 | Registros en centro poblado (`AREA=2`). |
| `casos_rural` | `int8` | 0 | Registros en área rural dispersa (`AREA=3`). |
| `casos_contributivo` | `int64` | 0 | Régimen contributivo (`TIP_SS=C`). |
| `casos_subsidiado` | `int64` | 0 | Régimen subsidiado (`TIP_SS=S`). |
| `casos_excepcion` | `int64` | 0 | Régimen de excepción (`TIP_SS=P`). |
| `casos_especial` | `int64` | 0 | Régimen especial (`TIP_SS=E`). |
| `casos_no_asegurado` | `int64` | 0 | No asegurados (`TIP_SS=N`). |
| `casos_indigena` | `int64` | 0 | Pertenencia étnica indígena (`PER_ETN=1`). |
| `casos_rom` | `int64` | 0 | Pertenencia étnica Rrom (`PER_ETN=2`). |
| `casos_raizal` | `int64` | 0 | Pertenencia étnica raizal (`PER_ETN=3`). |
| `casos_palenquero` | `int64` | 0 | Pertenencia étnica palenquera (`PER_ETN=4`). |
| `casos_afro` | `int64` | 0 | Pertenencia étnica afrocolombiana (`PER_ETN=5`). |
| `casos_otro_etnico` | `int64` | 0 | Otra categoría étnica (`PER_ETN=6`). |
| `casos_estrato_1` | `int64` | 0 | Estrato socioeconómico 1. |
| `casos_estrato_2` | `int64` | 0 | Estrato socioeconómico 2. |
| `casos_estrato_3` | `int64` | 0 | Estrato socioeconómico 3. |
| `casos_estrato_4` | `int64` | 0 | Estrato socioeconómico 4. |
| `casos_estrato_5` | `int64` | 0 | Estrato socioeconómico 5. |
| `casos_estrato_6` | `int64` | 0 | Estrato socioeconómico 6. |
| `casos_discapacidad` | `int64` | 0 | Grupo poblacional discapacidad (`GP_DISCAPA=1`). |
| `casos_desplazados` | `int64` | 0 | Grupo poblacional desplazados (`GP_DESPLAZ=1`). |
| `casos_migrantes` | `int64` | 0 | Grupo poblacional migrantes (`GP_MIGRANT=1`). |
| `casos_carcelarios` | `int64` | 0 | Grupo poblacional carcelario (`GP_CARCELA=1`). |
| `casos_gestantes` | `int64` | 0 | Grupo poblacional gestantes (`GP_GESTAN=1`). |
| `casos_indigentes` | `int64` | 0 | Grupo poblacional indigentes (`GP_INDIGEN=1`); distinto de pertenencia étnica indígena. |
| `casos_icbf` | `int64` | 0 | Grupo poblacional ICBF (`GP_POBICFB=1`). |
| `casos_madres_comunitarias` | `int64` | 0 | Madres comunitarias (`GP_MAD_COM=1`). |
| `casos_desmovilizados` | `int64` | 0 | Grupo poblacional desmovilizados (`GP_DESMOVI=1`). |
| `casos_centros_psiquiatricos` | `int64` | 0 | Grupo poblacional centros psiquiátricos (`GP_PSIQUIA=1`). |
| `casos_victimas_violencia` | `int64` | 0 | Grupo poblacional víctimas de violencia (`GP_VIC_VIO=1`). |
| `casos_otros_grupos` | `int64` | 0 | Otros grupos poblacionales (`GP_OTROS=1`). |
| `casos_notificacion_rutinaria` | `int64` | 0 | Fuente de notificación rutinaria (`fuente=1`). |
| `casos_busqueda_activa_institucional` | `int8` | 0 | Fuente de búsqueda activa institucional (`fuente=2`). |
| `casos_vigilancia_intensificada` | `int8` | 0 | Fuente de vigilancia intensificada (`fuente=3`). |
| `casos_busqueda_activa_comunitaria` | `int8` | 0 | Fuente de búsqueda activa comunitaria (`fuente=4`). |
| `casos_investigaciones` | `int8` | 0 | Fuente de investigaciones (`fuente=5`). |
| `casos_notificados_mismo_municipio` | `int64` | 0 | Notificados en la misma entidad de residencia. |
| `casos_notificados_otro_municipio` | `int8` | 0 | Notificados en otra entidad DIVIPOLA válida. |
| `casos_municipio_notificacion_desconocido` | `int8` | 0 | Código de entidad de notificación no reconocido en el DIVIPOLA local. |
| `casos_ocurridos_en_colombia` | `int64` | 0 | País de ocurrencia Colombia (`COD_PAIS_O=170`), aunque la entidad sea desconocida. |
| `casos_ocurrencia_mismo_municipio_residencia` | `int64` | 0 | Ocurridos en Colombia en la misma entidad de residencia. |
| `casos_ocurrencia_otro_municipio` | `int64` | 0 | Ocurridos en Colombia en otra entidad DIVIPOLA válida. |
| `casos_ocurrencia_municipio_desconocido` | `int64` | 0 | Ocurridos en Colombia con entidad de ocurrencia no reconocida. |
| `casos_inicio_sintomas_fuera_semana_reportada` | `int64` | 0 | Fecha interpretable de inicio de síntomas fuera de la semana reportada. |
| `casos_inicio_sintomas_sin_fecha` | `int64` | 0 | Sin fecha interpretable de inicio de síntomas. |
| `casos_notificacion_fuera_semana_reportada` | `int64` | 0 | Fecha interpretable de notificación fuera de la semana reportada. |
| `casos_notificados_mismo_dia` | `int64` | 0 | Notificación el mismo día del inicio de síntomas. |
| `casos_notificados_1_3_dias` | `int64` | 0 | Notificación entre 1 y 3 días después del inicio de síntomas. |
| `casos_notificados_4_7_dias` | `int64` | 0 | Notificación entre 4 y 7 días después del inicio de síntomas. |
| `casos_notificados_mas_7_dias` | `int64` | 0 | Notificación más de 7 días después del inicio de síntomas. |
| `casos_notificados_antes_inicio_sintomas` | `int64` | 0 | Fecha de notificación anterior a la de inicio de síntomas. |
| `casos_sin_fecha_para_demora` | `int64` | 0 | Falta una fecha interpretable para calcular la demora entre síntomas y notificación. |
| `casos_clasificacion_inicial_sospechosos` | `int64` | 0 | Clasificación inicial sospechosa (`TIP_CAS=1`). |
| `casos_clasificacion_inicial_probables` | `int64` | 0 | Clasificación inicial probable (`TIP_CAS=2`). |
| `casos_clasificacion_inicial_confirmados_laboratorio` | `int64` | 0 | Clasificación inicial confirmada por laboratorio (`TIP_CAS=3`). |
| `casos_clasificacion_inicial_confirmados_clinica` | `int64` | 0 | Clasificación inicial confirmada por clínica (`TIP_CAS=4`). |
| `casos_clasificacion_inicial_confirmados_nexo` | `int8` | 0 | Clasificación inicial confirmada por nexo (`TIP_CAS=5`). |
| `casos_vivos` | `int64` | 0 | Condición final vivo (`CON_FIN=1`). |
| `casos_fallecidos` | `int8` | 0 | Condición final fallecido (`CON_FIN=2`). |
| `casos_condicion_desconocida` | `int8` | 0 | Condición final distinta de vivo o fallecido, o sin dato. |
| `casos_ajuste_sin_ajuste` | `int64` | 0 | Código de ajuste `AJUSTE=0`. |
| `casos_ajuste_confirmados_laboratorio` | `int8` | 0 | Código de ajuste `AJUSTE=3` (confirmación por laboratorio). |
| `casos_ajuste_confirmados_clinica` | `int64` | 0 | Código de ajuste `AJUSTE=4` (confirmación clínica). |
| `casos_ajuste_confirmados_nexo` | `int8` | 0 | Código de ajuste `AJUSTE=5` (confirmación por nexo). |
| `casos_ajuste_otro_ajuste` | `int8` | 0 | Código de ajuste `AJUSTE=7` (otro ajuste). |
| `casos_fuerzas_armadas` | `int8` | 0 | Al menos uno de `FM_FUERZA`, `FM_UNIDAD` o `FM_GRADO` tiene contenido. |
| `prop_notificados_fuera_municipio` | `double` | 0 | `casos_notificados_otro_municipio / casos_total`; proporción entre 0 y 1. |

## Calidad y reproducción

El archivo [quality_report/summary.json](quality_report/summary.json)
registra los casos de los CSV de origen, las fechas ausentes para el
agrupamiento y las filas/casos de cada año epidemiológico de salida.
Las categorías `casos_*` de grupos distintos pueden superponerse.
Una semana sin fila no se completa como cero.

Las cifras y los tipos anteriores describen los archivos presentes el
**2026-10-23**. Si se regeneran, conviene volver a perfilar las salidas.

```bash
.venv/bin/python scripts/processing/calculate_date_weekly_sivigila.py --mode symptom
```
