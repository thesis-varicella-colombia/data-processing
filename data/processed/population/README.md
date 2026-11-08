# Población municipal por sexo y grupo de edad

`population_municipal_2007_2025.csv` reproduce `poblacion_to_join` del notebook a partir de los dos libros en [`data/raw/population`](../../raw/population/README.md). Cada fila corresponde a municipio (`codigo_municipio`) y año (`ano_epidemiologico`) entre 2007 y 2025. El código municipal se conserva como texto de cinco dígitos.

Las columnas de población incluyen el total municipal, hombres, mujeres, cabecera, rural y cinco grupos de edad (`<1`, `1-4`, `5-14`, `15-49`, `50+`) para el total y cada sexo. En el libro 2005–2017, `50+` suma las edades 50–84 y `85 y más`; en el libro 2018–2042 suma 50–99 y `100 años y más`. Los valores son personas estimadas o proyectadas, no casos de vigilancia.

Los totales por sexo y edad proceden de la fila de área `Total`. `poblacion_cabecera` procede de `Cabecera Municipal` y `poblacion_rural` de `Centros Poblados y Rural Disperso`.

Para regenerarlo desde la raíz del repositorio:

```bash
.venv/bin/python scripts/processing/process_population.py
```

El notebook [`population_raw_explore.ipynb`](../../../notebooks/population_raw_explore.ipynb) muestra las mismas transformaciones y tiene una celda final para guardar este CSV.

## Comparación con sobrevivientes de un año

El notebook [`surviving_infants_explore.ipynb`](../../../notebooks/surviving_infants_explore.ipynb)
consulta este CSV y lo une al [consolidado de sobrevivientes](../births_mortality_dane/integration/README.md)
por `codigo_municipio` y `ano_epidemiologico = ano`. Lee únicamente esas dos
claves y `poblacion_menor_1`, conservando los códigos como texto y validando
que población tenga una sola fila por municipio y año. La unión izquierda
conserva todas las filas de sobrevivientes y agrega solo `poblacion_menor_1`.

`poblacion_menor_1` representa personas menores de un año, de ambos sexos,
tomadas de la fila de área `Total`. La comparación usa la población del año
de la fila y calcula
`porcentaje_diferencia = abs(sobrevivientes_edad_1 - poblacion_menor_1) / poblacion_menor_1 * 100`.
El resultado se ordena de mayor a menor; los porcentajes no calculables quedan
al final. Si falta un valor o el denominador es cero o negativo, el porcentaje
queda nulo. El notebook muestra también la cobertura de la unión.

Es una comparación exploratoria entre población estimada/proyectada menor de
un año y un saldo de nacimientos menos defunciones infantiles del año previo;
las dos variables no representan exactamente la misma medida demográfica.
Esta consulta no modifica el CSV ni el Parquet de sobrevivientes.

## Esquema y diccionario de datos

CSV de 22 columnas, con una fila por (`codigo_municipio`, `ano_epidemiologico`). El CSV no almacena tipos físicos: se indican tipos de lectura recomendados de pandas (`string` e `Int64`, entero que admite nulos). Leer el código como texto para conservar los cinco dígitos. Todas las medidas son personas estimadas o proyectadas; un valor ausente no equivale a cero.

| Columna | Tipo | Descripción |
| --- | --- | --- |
| `codigo_municipio` | `string` | Código DIVIPOLA de cinco dígitos, conservando ceros iniciales. |
| `ano_epidemiologico` | `Int64` | Año epidemiológico de la semana; puede diferir del año calendario. |
| `poblacion_total` | `Int64` | Personas de todas las edades y ambos sexos, área Total. |
| `poblacion_hombres` | `Int64` | Hombres de todas las edades, área Total. |
| `poblacion_mujeres` | `Int64` | Mujeres de todas las edades, área Total. |
| `poblacion_cabecera` | `Int64` | Personas de todas las edades y ambos sexos en Cabecera Municipal. |
| `poblacion_rural` | `Int64` | Personas de todas las edades y ambos sexos en Centros Poblados y Rural Disperso. |
| `poblacion_menor_1` | `Int64` | Personas menores de 1 año, ambos sexos, área Total. |
| `poblacion_1_4` | `Int64` | Personas de 1 a 4 años, ambos sexos, área Total. |
| `poblacion_5_14` | `Int64` | Personas de 5 a 14 años, ambos sexos, área Total. |
| `poblacion_15_49` | `Int64` | Personas de 15 a 49 años, ambos sexos, área Total. |
| `poblacion_50_mas` | `Int64` | Personas de 50 años o más, ambos sexos, área Total. |
| `poblacion_hombres_menor_1` | `Int64` | Personas menores de 1 año, hombres, área Total. |
| `poblacion_hombres_1_4` | `Int64` | Personas de 1 a 4 años, hombres, área Total. |
| `poblacion_hombres_5_14` | `Int64` | Personas de 5 a 14 años, hombres, área Total. |
| `poblacion_hombres_15_49` | `Int64` | Personas de 15 a 49 años, hombres, área Total. |
| `poblacion_hombres_50_mas` | `Int64` | Personas de 50 años o más, hombres, área Total. |
| `poblacion_mujeres_menor_1` | `Int64` | Personas menores de 1 año, mujeres, área Total. |
| `poblacion_mujeres_1_4` | `Int64` | Personas de 1 a 4 años, mujeres, área Total. |
| `poblacion_mujeres_5_14` | `Int64` | Personas de 5 a 14 años, mujeres, área Total. |
| `poblacion_mujeres_15_49` | `Int64` | Personas de 15 a 49 años, mujeres, área Total. |
| `poblacion_mujeres_50_mas` | `Int64` | Personas de 50 años o más, mujeres, área Total. |
