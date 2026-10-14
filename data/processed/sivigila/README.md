# Ficha técnica: notificaciones semanales de varicela por municipio

| Campo | Descripción |
| --- | --- |
| Fuente | [Microdatos Sivigila de varicela individual (evento 831)](../../raw/sivigila/README.md), CSV anuales `data/raw/sivigila/csv/Datos_AAAA_831.csv` |
| Geografía | [DIVIPOLA](../../raw/municipios/README.md), entidades con tipo `Municipio` (1.103 códigos); se conserva el código de cinco dígitos como texto |
| Periodo | Años epidemiológicos reportados 2007–2025 |
| Unidad de análisis | Municipio de **residencia** × `ANO`/`SEMANA` reportados por Sivigila |
| Formato | `sivigila_weekly_municipal_AAAA.parquet`, uno por año, e informe `quality_report_AAAA.json` |
| Generado por | [`scripts/processing/calculate_weekly_sivigila.py`](../../../scripts/processing/calculate_weekly_sivigila.py) |

Los Parquet contienen **solo combinaciones municipio-semana con al menos una notificación**. `casos_total` es un conteo de registros del evento 831, no una tasa de incidencia ni una población completa de enfermos. No se deduplican registros porque el notebook [`sivigila_raw_explore.ipynb`](../../../notebooks/sivigila_raw_explore.ipynb) no definía una clave ni una regla de deduplicación verificable. No se imputan semanas sin registros como cero.

## Variables de salida

Las columnas de identificación son `codigo_municipio`, `nombre_municipio`, `codigo_departamento`, `ano_epidemiologico`, `semana_epidemiologica`, `inicio_semana` y `fin_semana`. Las fechas de inicio y fin se calculan con la convención del proyecto: domingo a sábado; la semana 1 contiene el 4 de enero. **El agrupamiento usa siempre `ANO` y `SEMANA` de Sivigila**, no recalcula la semana desde `FEC_NOT` ni desde `INI_SIN`.

Además de `casos_total`, hay conteos por sexo, hospitalización, edad, área, régimen de salud, pertenencia étnica, estrato, grupos poblacionales, fuente de notificación, municipio de notificación y de ocurrencia, demora entre síntomas y notificación, clasificación inicial, condición final, ajuste y fuerzas armadas. Todos los indicadores `casos_*` cuentan registros que cumplen su criterio; categorías de distintos grupos pueden superponerse. `prop_notificados_fuera_municipio` divide `casos_notificados_otro_municipio` entre `casos_total`. Los indicadores `casos_inicio_sintomas_fuera_semana_reportada`, `casos_inicio_sintomas_sin_fecha` y `casos_notificacion_fuera_semana_reportada` permiten revisar la coherencia temporal **por municipio y semana**.

Las categorías de edad usan `EDAD` y `UNI_MED`: años, meses, días, horas o minutos se convierten a años antes de clasificar, igual que en el notebook. Los grupos son `<1`, `1-4`, `5-14`, `15-49` y `50+` años, representados por `casos_menor_1`, `casos_1_4`, `casos_5_14`, `casos_15_49` y `casos_50_mas`. No se aplica un límite superior de edad: los 8 registros con `UNI_MED=1` y `EDAD` entre 121 y 130 años quedan en `casos_50_mas`. `casos_edad_desconocida` significa **edad no convertible a años**. En los 1.248.625 registros municipales incluidos, suma 1.288 casos, todos con `EDAD=0` y `UNI_MED=0` («no aplica» según el diccionario del notebook). No hay `EDAD` ausentes ni no numéricas en estos registros. Los campos `GP_*` se cuentan como afirmativos solo si valen `1`. En el notebook, `PAC_HOS` se transforma primero en booleano (`True` solo para el texto `"1"`) y luego se suma; este script aplica esa misma condición directamente al CSV para `casos_hospitalizados`. `casos_fallecidos` usa exclusivamente `CON_FIN=2`; una fecha o causa de muerte discordante se informa para revisión, sin cambiar la clasificación. Los indicadores de `TIP_CAS` llevan prefijo `casos_clasificacion_inicial_` y los de `AJUSTE` llevan `casos_ajuste_`, para mantener las dos fuentes de clasificación separadas.

El municipio de notificación se compara con `COD_MUN_N`, que **ya contiene cinco dígitos**; el de residencia se forma con `COD_DPTO_R` (dos dígitos) y `COD_MUN_R` (tres dígitos). Los municipios de notificación u ocurrencia inválidos se cuentan por separado y no se consideran automáticamente «otro municipio». Se incluyen notificaciones de cualquier clasificación inicial; los códigos de descarte `AJUSTE=6` o `D` se excluyen. En los CSV actuales no aparece ninguno de esos descartes.

## Calidad y límites para el cruce con clima

Los 19 CSV contienen **1.257.304 registros**. Se incluyeron **1.248.625** en **226.195 filas municipio-semana**. Se excluyeron 2.543 registros asignados a entidades DIVIPOLA que no son `Municipio` (incluida San Andrés, clasificada `Isla`) y 6.136 con código de residencia que no identifica una entidad DIVIPOLA. Cada informe anual registra los códigos excluidos. Esta regla coincide con el universo municipal del pipeline climático, pero excluye esas notificaciones de los conteos municipales.

Hay una discrepancia temporal que requiere atención antes de unir esta tabla con variables climáticas: **72.426** registros incluidos tienen `INI_SIN` fuera de la semana que resulta de interpretar su `ANO`/`SEMANA` con la convención domingo–sábado del proyecto; otros **55.630** no tienen fecha de inicio de síntomas interpretable. La discrepancia se concentra en 2007 (**11.642**) y 2008 (**24.948**). En cambio, **448.140** fechas de notificación caen fuera de la semana reportada. Esto sugiere que la relación entre semana reportada y fechas individuales no fue uniforme a lo largo de la serie; no permite asumir que `ANO`/`SEMANA` siempre represente la semana de notificación o la de síntomas. `inicio_semana` y `fin_semana` son la **interpretación del calendario del proyecto** para esos números, no una corrección de los registros del INS. Revise esta diferencia antes de atribuir exposiciones climáticas a casos de 2007–2008.

El informe también cuenta 13 registros incluidos con fecha o causa de defunción y `CON_FIN` distinto de 2. Se preserva el valor original de `CON_FIN`; la discrepancia no basta para reclasificar el desenlace. Los conteos son notificaciones de vigilancia, sujetos a cobertura y cambios administrativos; para calcular tasas se requiere población y una definición de caso explícita.

## Reproducción

Desde la raíz del repositorio, con los CSV generados por [`convert_sivigila_excel_to_csv.py`](../../../scripts/processing/convert_sivigila_excel_to_csv.py) y dependencias de `scripts/requirements.txt`:

```bash
.venv/bin/python scripts/processing/calculate_weekly_sivigila.py --validate-only
.venv/bin/python scripts/processing/calculate_weekly_sivigila.py
.venv/bin/python scripts/processing/calculate_weekly_sivigila.py --start-year 2025 --end-year 2025 --overwrite
```

`--input-dir`, `--output-dir` y `--divipola` permiten cambiar rutas. `--start-year` y `--end-year` limitan los años. El script lee cada CSV por bloques, valida evento, año y semana, escribe primero `.part` y renombra el Parquet e informe al terminar. Al reanudar, omite pares Parquet/informe válidos; `--overwrite` los regenera. Los archivos `quality_report_AAAA.json` contienen recuentos de entrada, exclusiones, discrepancias temporales y códigos de residencia excluidos.
