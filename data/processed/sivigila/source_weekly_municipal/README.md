# Sivigila: casos por semana reportada y entidad de residencia

## Contenido y cobertura

Un Parquet anual `sivigila_weekly_municipal_AAAA.parquet` y un informe
`quality_report/quality_report_AAAA.json` por año reportado, de 2007 a 2025. Fuente:
[CSV individuales de varicela, evento 831](../../../raw/sivigila/README.md).
Cada fila representa una entidad DIVIPOLA de residencia y una combinación
`ANO`/`SEMANA` **reportada** con al menos un caso. El calendario interpretado
por el proyecto va de domingo a sábado; la semana 1 contiene el 4 de enero.
El método de inclusión, homologación y agregación se explica en la
[ficha general](../README.md).

Perfil de los archivos actuales: **19 Parquet, 227.113 filas, 1.251.524 notificaciones sumadas y 1.121 entidades**.
Hay 85 columnas. No se crean filas para combinaciones entidad-semana sin
notificaciones; la ausencia de una fila no debe interpretarse automáticamente
como un cero comprobado.

| Año | Filas entidad-semana | Casos (`casos_total`) |
| --- | ---: | ---: |
| 2007 | 379 | 26.441 |
| 2008 | 7.863 | 63.491 |
| 2009 | 12.299 | 72.950 |
| 2010 | 12.535 | 73.715 |
| 2011 | 17.025 | 120.772 |
| 2012 | 16.711 | 100.195 |
| 2013 | 15.775 | 93.606 |
| 2014 | 16.959 | 107.924 |
| 2015 | 16.877 | 110.714 |
| 2016 | 17.477 | 111.984 |
| 2017 | 16.196 | 86.386 |
| 2018 | 15.227 | 74.982 |
| 2019 | 14.634 | 67.236 |
| 2020 | 6.319 | 18.075 |
| 2021 | 5.478 | 14.348 |
| 2022 | 7.817 | 22.647 |
| 2023 | 9.824 | 31.596 |
| 2024 | 8.372 | 24.911 |
| 2025 | 9.346 | 29.551 |
| **Total** | **227.113** | **1.251.524** |

## Nulos y tipos

**Todas las columnas tienen 0 nulos físicos** en estos 19 Parquet.
Esto no equivale a datos clínicos completos: por ejemplo,
`casos_inicio_sintomas_sin_fecha` cuenta fechas ausentes dentro de filas
agregadas. Los campos `casos_*` son conteos enteros; algunos se guardan como
`int8` en un año y `int64` en otro según el rango observado. La columna de
tipo indica todos los tipos Arrow presentes en los archivos actuales.

| Columna | Tipo Arrow observado | Nulos | Descripción |
| --- | --- | ---: | --- |
| `codigo_municipio` | `large_string` | 0 | Código DIVIPOLA de cinco dígitos de la entidad de residencia; incluye municipios, islas y áreas no municipalizadas aceptadas. |
| `nombre_municipio` | `large_string` | 0 | Nombre de la entidad de residencia según el DIVIPOLA local. |
| `codigo_departamento` | `large_string` | 0 | Código DIVIPOLA de dos dígitos del departamento de residencia. |
| `ano_epidemiologico` | `int64` | 0 | Año epidemiológico `ANO` reportado por SIVIGILA; clave de unión con población y vacunación. |
| `semana_epidemiologica` | `int16` | 0 | Número de semana `SEMANA` reportado por SIVIGILA. |
| `inicio_semana` | `date32[day]` | 0 | Domingo inicial de la semana reportada, según el calendario epidemiológico del proyecto. |
| `fin_semana` | `date32[day]` | 0 | Sábado final de esa semana, inclusive; puede caer en otro año calendario. |
| `casos_total` | `int64` | 0 | Total de notificaciones incluidas en la entidad y semana. |
| `casos_masculinos` | `int64` / `int8` | 0 | Registros con `SEXO=M`. |
| `casos_femeninos` | `int64` / `int8` | 0 | Registros con `SEXO=F`. |
| `casos_hospitalizados` | `int64` / `int8` | 0 | Registros con `PAC_HOS=1`. |
| `casos_menor_1` | `int64` / `int8` | 0 | Edad convertible a años menor de 1 año. |
| `casos_1_4` | `int64` / `int8` | 0 | Edad de 1 a menos de 5 años. |
| `casos_5_14` | `int64` / `int8` | 0 | Edad de 5 a menos de 15 años. |
| `casos_15_49` | `int64` / `int8` | 0 | Edad de 15 a menos de 50 años. |
| `casos_50_mas` | `int64` / `int8` | 0 | Edad de 50 años o más. |
| `casos_edad_desconocida` | `int64` / `int8` | 0 | Edad no convertible a años con `EDAD` y `UNI_MED`. |
| `casos_cabecera` | `int64` / `int8` | 0 | Registros en cabecera municipal (`AREA=1`). |
| `casos_centro_poblado` | `int64` / `int8` | 0 | Registros en centro poblado (`AREA=2`). |
| `casos_rural` | `int8` | 0 | Registros en área rural dispersa (`AREA=3`). |
| `casos_contributivo` | `int64` / `int8` | 0 | Régimen contributivo (`TIP_SS=C`). |
| `casos_subsidiado` | `int64` / `int8` | 0 | Régimen subsidiado (`TIP_SS=S`). |
| `casos_excepcion` | `int64` / `int8` | 0 | Régimen de excepción (`TIP_SS=P`). |
| `casos_especial` | `int64` / `int8` | 0 | Régimen especial (`TIP_SS=E`). |
| `casos_no_asegurado` | `int64` / `int8` | 0 | No asegurados (`TIP_SS=N`). |
| `casos_indigena` | `int64` / `int8` | 0 | Pertenencia étnica indígena (`PER_ETN=1`). |
| `casos_rom` | `int64` / `int8` | 0 | Pertenencia étnica Rrom (`PER_ETN=2`). |
| `casos_raizal` | `int64` / `int8` | 0 | Pertenencia étnica raizal (`PER_ETN=3`). |
| `casos_palenquero` | `int64` / `int8` | 0 | Pertenencia étnica palenquera (`PER_ETN=4`). |
| `casos_afro` | `int64` / `int8` | 0 | Pertenencia étnica afrocolombiana (`PER_ETN=5`). |
| `casos_otro_etnico` | `int64` / `int8` | 0 | Otra categoría étnica (`PER_ETN=6`). |
| `casos_estrato_1` | `int64` / `int8` | 0 | Estrato socioeconómico 1. |
| `casos_estrato_2` | `int64` / `int8` | 0 | Estrato socioeconómico 2. |
| `casos_estrato_3` | `int64` / `int8` | 0 | Estrato socioeconómico 3. |
| `casos_estrato_4` | `int64` / `int8` | 0 | Estrato socioeconómico 4. |
| `casos_estrato_5` | `int64` / `int8` | 0 | Estrato socioeconómico 5. |
| `casos_estrato_6` | `int64` / `int8` | 0 | Estrato socioeconómico 6. |
| `casos_discapacidad` | `int64` / `int8` | 0 | Grupo poblacional discapacidad (`GP_DISCAPA=1`). |
| `casos_desplazados` | `int64` / `int8` | 0 | Grupo poblacional desplazados (`GP_DESPLAZ=1`). |
| `casos_migrantes` | `int64` / `int8` | 0 | Grupo poblacional migrantes (`GP_MIGRANT=1`). |
| `casos_carcelarios` | `int64` / `int8` | 0 | Grupo poblacional carcelario (`GP_CARCELA=1`). |
| `casos_gestantes` | `int64` / `int8` | 0 | Grupo poblacional gestantes (`GP_GESTAN=1`). |
| `casos_indigentes` | `int64` / `int8` | 0 | Grupo poblacional indigentes (`GP_INDIGEN=1`); distinto de pertenencia étnica indígena. |
| `casos_icbf` | `int64` / `int8` | 0 | Grupo poblacional ICBF (`GP_POBICFB=1`). |
| `casos_madres_comunitarias` | `int64` / `int8` | 0 | Madres comunitarias (`GP_MAD_COM=1`). |
| `casos_desmovilizados` | `int64` / `int8` | 0 | Grupo poblacional desmovilizados (`GP_DESMOVI=1`). |
| `casos_centros_psiquiatricos` | `int64` / `int8` | 0 | Grupo poblacional centros psiquiátricos (`GP_PSIQUIA=1`). |
| `casos_victimas_violencia` | `int64` / `int8` | 0 | Grupo poblacional víctimas de violencia (`GP_VIC_VIO=1`). |
| `casos_otros_grupos` | `int64` / `int8` | 0 | Otros grupos poblacionales (`GP_OTROS=1`). |
| `casos_notificacion_rutinaria` | `int64` / `int8` | 0 | Fuente de notificación rutinaria (`fuente=1`). |
| `casos_busqueda_activa_institucional` | `int8` | 0 | Fuente de búsqueda activa institucional (`fuente=2`). |
| `casos_vigilancia_intensificada` | `int8` | 0 | Fuente de vigilancia intensificada (`fuente=3`). |
| `casos_busqueda_activa_comunitaria` | `int8` | 0 | Fuente de búsqueda activa comunitaria (`fuente=4`). |
| `casos_investigaciones` | `int8` | 0 | Fuente de investigaciones (`fuente=5`). |
| `casos_notificados_mismo_municipio` | `int64` / `int8` | 0 | Notificados en la misma entidad de residencia. |
| `casos_notificados_otro_municipio` | `int8` | 0 | Notificados en otra entidad DIVIPOLA válida. |
| `casos_municipio_notificacion_desconocido` | `int8` | 0 | Código de entidad de notificación no reconocido en el DIVIPOLA local. |
| `casos_ocurridos_en_colombia` | `int64` / `int8` | 0 | País de ocurrencia Colombia (`COD_PAIS_O=170`), aunque la entidad sea desconocida. |
| `casos_ocurrencia_mismo_municipio_residencia` | `int64` / `int8` | 0 | Ocurridos en Colombia en la misma entidad de residencia. |
| `casos_ocurrencia_otro_municipio` | `int64` / `int8` | 0 | Ocurridos en Colombia en otra entidad DIVIPOLA válida. |
| `casos_ocurrencia_municipio_desconocido` | `int64` / `int8` | 0 | Ocurridos en Colombia con entidad de ocurrencia no reconocida. |
| `casos_inicio_sintomas_fuera_semana_reportada` | `int64` / `int8` | 0 | Fecha interpretable de inicio de síntomas fuera de la semana reportada. |
| `casos_inicio_sintomas_sin_fecha` | `int64` / `int8` | 0 | Sin fecha interpretable de inicio de síntomas. |
| `casos_notificacion_fuera_semana_reportada` | `int64` / `int8` | 0 | Fecha interpretable de notificación fuera de la semana reportada. |
| `casos_notificados_mismo_dia` | `int64` / `int8` | 0 | Notificación el mismo día del inicio de síntomas. |
| `casos_notificados_1_3_dias` | `int64` / `int8` | 0 | Notificación entre 1 y 3 días después del inicio de síntomas. |
| `casos_notificados_4_7_dias` | `int64` / `int8` | 0 | Notificación entre 4 y 7 días después del inicio de síntomas. |
| `casos_notificados_mas_7_dias` | `int64` / `int8` | 0 | Notificación más de 7 días después del inicio de síntomas. |
| `casos_notificados_antes_inicio_sintomas` | `int64` / `int8` | 0 | Fecha de notificación anterior a la de inicio de síntomas. |
| `casos_sin_fecha_para_demora` | `int64` / `int8` | 0 | Falta una fecha interpretable para calcular la demora entre síntomas y notificación. |
| `casos_clasificacion_inicial_sospechosos` | `int64` / `int8` | 0 | Clasificación inicial sospechosa (`TIP_CAS=1`). |
| `casos_clasificacion_inicial_probables` | `int64` / `int8` | 0 | Clasificación inicial probable (`TIP_CAS=2`). |
| `casos_clasificacion_inicial_confirmados_laboratorio` | `int64` / `int8` | 0 | Clasificación inicial confirmada por laboratorio (`TIP_CAS=3`). |
| `casos_clasificacion_inicial_confirmados_clinica` | `int64` / `int8` | 0 | Clasificación inicial confirmada por clínica (`TIP_CAS=4`). |
| `casos_clasificacion_inicial_confirmados_nexo` | `int8` | 0 | Clasificación inicial confirmada por nexo (`TIP_CAS=5`). |
| `casos_vivos` | `int64` / `int8` | 0 | Condición final vivo (`CON_FIN=1`). |
| `casos_fallecidos` | `int8` | 0 | Condición final fallecido (`CON_FIN=2`). |
| `casos_condicion_desconocida` | `int8` | 0 | Condición final distinta de vivo o fallecido, o sin dato. |
| `casos_ajuste_sin_ajuste` | `int64` / `int8` | 0 | Código de ajuste `AJUSTE=0`. |
| `casos_ajuste_confirmados_laboratorio` | `int8` | 0 | Código de ajuste `AJUSTE=3` (confirmación por laboratorio). |
| `casos_ajuste_confirmados_clinica` | `int64` / `int8` | 0 | Código de ajuste `AJUSTE=4` (confirmación clínica). |
| `casos_ajuste_confirmados_nexo` | `int8` | 0 | Código de ajuste `AJUSTE=5` (confirmación por nexo). |
| `casos_ajuste_otro_ajuste` | `int8` | 0 | Código de ajuste `AJUSTE=7` (otro ajuste). |
| `casos_fuerzas_armadas` | `int8` | 0 | Al menos uno de `FM_FUERZA`, `FM_UNIDAD` o `FM_GRADO` tiene contenido. |
| `prop_notificados_fuera_municipio` | `double` | 0 | `casos_notificados_otro_municipio / casos_total`; proporción entre 0 y 1. |

## Interpretación

Los `casos_*` cuentan registros que cumplen cada criterio; las categorías
de grupos distintos pueden solaparse. `ANO`/`SEMANA` se preservan del CSV:
no se recalculan desde `FEC_NOT` ni `INI_SIN`. Los indicadores temporales
agregados de 2013 se calcularon con una lectura día/mes/año de `INI_SIN`;
el [agregado por semana de síntomas](../symptom_weekly_municipal/README.md)
aplica la lectura mes/día/año identificada para ese campo en 2013. Consulte el informe de calidad anual
antes de usar los indicadores de demora o concordancia temporal.

Las cifras y tipos de este README describen los archivos presentes el
**2026-10-23**. Si se regeneran los Parquet, deben volver a perfilarse.

```bash
.venv/bin/python scripts/processing/calculate_weekly_sivigila.py
```
