# Integración de nacimientos y mortalidad infantil

Entradas: [births](../births/README.md) y [mortality](../mortality/README.md).
Salida: `surviving_infants.parquet`, **21.868 filas y 8 columnas**, 2008–2025.
Procesador: [`integrate_surviving_infants.py`](../../../../scripts/processing/integrate_surviving_infants.py).

## Unión y tratamiento de faltantes

Se excluyen las filas con nombre de municipio `Total`. Se unen los datos por
`ano`, `codigo_departamento` y `codigo_municipio`, conservando las filas de
ambas entradas. Se prefieren los nombres de births; los nombres no son claves.

**Si existe births con clave completa y no existe la fila de mortality, se
asume `total_defunciones_menor_1 = 0`.** Se aplica directamente en la integración;
no se agregan filas ni se modifican los Parquet de entrada. Esas filas no
se cuentan como sin correspondencia. La imputación se registra por separado
en `quality_report.json`, como `filas_mortality_asumidas_cero`.

La suma de hombres y mujeres menores de un año requiere ambos componentes;
si una fila de mortality existe pero contiene un componente nulo, su resultado
sigue nulo. La regla de cero solo se aplica a la ausencia de la fila.

Las claves completas deben ser únicas por entrada. Los países con departamento
nulo y código municipal `-1` se conservan separados por origen: no se pueden
emparejar de forma única ni se les imputa cero. Las filas `-2` con departamento
conocido sí participan en la unión y en la regla de cero.

## Columnas y cálculo

| Columna | Contenido |
| --- | --- |
| `ano` | Año de la fila |
| `codigo_departamento` | Código departamental como texto, con ceros iniciales |
| `nombre_departamento` | Nombre departamental o categoría especial |
| `codigo_municipio` | Código municipal o convención especial, como texto |
| `nombre_municipio` | Nombre municipal o del país |
| `total_nacimientos` | Columna `total` de births, renombrada; nacimientos del año actual |
| `total_defunciones_menor_1` | Hombres + mujeres menores de un año de mortality del año actual; cero si no existe su fila y la clave de births es completa |
| `sobrevivientes_edad_1` | Nacimientos menos defunciones infantiles del año inmediatamente anterior |

```text
sobrevivientes_edad_1(t) = total_nacimientos(t-1) - total_defunciones_menor_1(t-1)
```

Se exige el año calendario anterior exacto, sin saltar huecos. Si no hay fila
de mortality de ese año pero sí births con clave completa, se resta cero.
Los nacimientos ausentes no se convierten a cero. Los saldos de 2008 quedan
nulos por falta de 2007; no se crean filas nuevas de 2026. Se conservan los
negativos y los conteos nulos existentes. Este saldo anual no es seguimiento
individual de una cohorte.

## Validación y reportes

Hay **20.322 claves con correspondencia real** y **454 filas de births cuya
mortalidad se asume cero**. Estas últimas ya no se incluyen en el reporte de
filas sin correspondencia.

`unmatched_rows.csv` conserva los identificadores, medidas disponibles,
`origen` y `motivo` de **1.092 filas pendientes**:

| Resultado | Births | Mortality |
| --- | ---: | ---: |
| Claves completas sin correspondencia | 0 | 0 |
| Claves incompletas | 408 | 684 |
| Total pendiente | 408 | 684 |

Bogotá se armoniza como municipio `11001` en las entradas: en births
se copia el total departamental de 2008–2019 y en mortality el de 2009–2018.
Sus claves ahora tienen correspondencia en todos los años.

La identidad de filas es `21.868 = 20.322 + 454 + 1.092`.
El saldo tiene **2.248 nulos y 16 negativos**, estos últimos en municipios
sin información. `quality_report.json` contiene también el perfil anual y
los conteos de totales excluidos. Volver a calcular este perfil si cambian
las entradas o la lógica.

## Generación y exploración

```bash
.venv/bin/python scripts/processing/integrate_surviving_infants.py
.venv/bin/python -m unittest discover -s tests -p test_surviving_infants.py -v
```

El script acepta `--births`, `--mortality` y `--output`; sobrescribe el Parquet
y los dos reportes de su carpeta mediante archivos temporales. Sus rutas
predeterminadas se resuelven desde el repositorio.

El notebook [`surviving_infants_explore.ipynb`](../../../../notebooks/surviving_infants_explore.ipynb)
muestra el schema, primeras diez filas, métricas, resúmenes por año,
consultas departamentales y municipales, filas sin correspondencia y saldos
negativos. Está guardado con resultados; volver a ejecutarlo tras regenerar.

Los tests cubren el año anterior exacto, huecos temporales, mortalidad ausente
asumida cero, nulos existentes, negativos, claves duplicadas o incompletas y
la escritura de los reportes.
