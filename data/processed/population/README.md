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
