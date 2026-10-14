# Población municipal por sexo y grupo de edad

`population_municipal_2007_2025.csv` reproduce `poblacion_to_join` del notebook a partir de los dos libros en [`data/raw/population`](../../raw/population/README.md). Cada fila corresponde a municipio (`codigo_municipio`) y año (`ano_epidemiologico`) entre 2007 y 2025. El código municipal se conserva como texto de cinco dígitos.

Las columnas de población incluyen el total municipal, hombres, mujeres, cabecera, rural y cinco grupos de edad (`<1`, `1-4`, `5-14`, `15-49`, `50+`) para el total y cada sexo. En el libro 2005–2017, `50+` suma las edades 50–84 y `85 y más`; en el libro 2018–2042 suma 50–99 y `100 años y más`. Los valores son personas estimadas o proyectadas, no casos de vigilancia.

Los totales por sexo y edad proceden de la fila de área `Total`. `poblacion_cabecera` procede de `Cabecera Municipal` y `poblacion_rural` de `Centros Poblados y Rural Disperso`.

Para regenerarlo desde la raíz del repositorio:

```bash
.venv/bin/python scripts/processing/process_population.py
```

El notebook [`population_raw_explore.ipynb`](../../../notebooks/population_raw_explore.ipynb) muestra las mismas transformaciones y tiene una celda final para guardar este CSV.
