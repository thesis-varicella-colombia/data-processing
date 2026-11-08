# Defunciones DANE: totales territoriales de 2008–2025

| Campo | Descripción |
| --- | --- |
| Entrada | Dieciocho libros anuales de la [carpeta raw de mortalidad](../../../raw/births_mortality_dane/mortality/) |
| Documentación de entrada | [Ficha técnica de raw](../../../raw/births_mortality_dane/mortality/README.md): inventario, origen, versiones y estructura de los archivos |
| Salida | `mortality.parquet`, un único archivo con **21.636 filas y 30 columnas** |
| Periodo | 2008–2025 |
| Unidad | Total de defunciones de todas las causas por municipio/país o departamento/categoría y año |
| Procesador | [`process_mortality_dane.py`](../../../../scripts/processing/process_mortality_dane.py) |

## Extracción

El procesamiento parte de los libros locales de la
[carpeta raw](../../../raw/births_mortality_dane/mortality/), descritos en su
[README](../../../raw/births_mortality_dane/mortality/README.md).

En 2008–2019 se excluyen la hoja nacional `00` y el índice (`Indice`/`Índice`, presente
desde 2009). En las 35 hojas restantes de cada año se localizan y combinan
las dos filas de encabezado. El nombre del departamento/categoría se toma de
la fila anterior y se elimina el prefijo de dos dígitos cuando aparece.
Se leen A:AA en 2008–2014 y A:AG en 2015–2019.
Se conservan **solo las filas con B
igual a `TOTAL`**: el total de la hoja y los totales municipales o de países.
Las filas de causas específicas, vacías y notas al pie se descartan.

| Años | Encabezados | Primer total | Nombre de departamento/categoría |
| --- | --- | --- | --- |
| 2008–2016 | 11–12 | Fila 13 | A10 |
| 2017 | 13–14 | Fila 15 | A12 |
| 2018–2019 | 12–13 | Fila 14 | A11 |

En 2020–2025 se lee únicamente `Cuadro5`, C:AJ, con encabezados en 8–9 y
datos desde 10. Se excluye la fila nacional y sus causas. C identifica el
departamento con código de dos dígitos y nombre; D identifica el municipio;
E contiene la causa y F:AJ los conteos. Se conservan solo las filas con E
igual a `TOTAL` o `TOTAL MUN` (esta última etiqueta aparece en los municipios
de 2025), ignorando las causas específicas. Las filas con departamento en C
son sus totales: D puede decir `Total Dpto` o estar vacía. Se normalizan a
`nombre_municipio = "Total"`. El departamento se mantiene en las filas
municipales con C vacía.

Los XLS cifrados se abren con `msoffcrypto-tool` usando la clave estándar de
Excel y se descifran en memoria. Los XLSX se leen con `openpyxl`, usando los
valores almacenados. No se modifican los originales ni se escriben copias
descifradas.

En 2015–2025 se suman los grupos **65–84 + 85–99 + 100 y más**, de forma
independiente para hombres, mujeres y sexo indeterminado, para obtener las
tres columnas `edad_65_mas_*` existentes. La edad desconocida se conserva
aparte. Si falta algún componente de la suma, el resultado queda nulo en
lugar de guardar una suma parcial. Las columnas del Parquet no cambian.

La etiqueta municipal (A en 2008–2019, D en 2020–2025) se divide en código y
nombre. Los códigos municipales
se guardan como texto para mantener sus ceros iniciales y se verifica su
prefijo departamental. El total de cada departamento usa el código de dos
dígitos de la hoja o de C. Todas las filas de extranjeros usan `-1`; las de la
categoría sin información y los municipios sin información usan `-2`.
Las dos categorías especiales tienen código de departamento nulo. Estos
códigos especiales pueden repetirse y no identifican una fila única.
Los códigos de países extranjeros pueden tener tres o cinco dígitos; se
separan del nombre antes de asignar `-1` y no se tratan como municipios.

## Columnas

El orden es `ano`, `codigo_departamento`, `nombre_departamento`,
`codigo_municipio`, `nombre_municipio`, seguido de 25 conteos armonizados
al esquema de C:AA de 2008–2014.
Los identificadores y nombres son texto; el año y los conteos son enteros
de 64 bits. Una celda de conteo vacía se conserva nula. Los rangos de la tabla
siguiente corresponden a los libros de 2008–2019; en 2020–2025 los conteos
comienzan en F y los rangos numéricos se desplazan tres columnas a la derecha.

| Columna o grupo | Contenido |
| --- | --- |
| `ano` | Año 2008–2025, verificado contra el título de cada hoja |
| `codigo_departamento`, `nombre_departamento` | Código de hoja y nombre anterior al encabezado (2008–2019), o extraídos de C (2020–2025); incluye extranjeros y sin información |
| `codigo_municipio`, `nombre_municipio` | Código separado del nombre; las filas de total de hoja usan el nombre `Total` |
| `total` | Defunciones de todas las edades y sexos: C en 2008–2019, F en 2020–2025 |
| `total_{hombres,mujeres,indeterminado}` | Columnas D:F: total por sexo |
| `edad_menor_1_{hombres,mujeres,indeterminado}` | Columnas G:I: menores de un año por sexo |
| `edad_1_4_{hombres,mujeres,indeterminado}` | Columnas J:L: edades de 1 a 4 años por sexo |
| `edad_5_14_{hombres,mujeres,indeterminado}` | Columnas M:O: edades de 5 a 14 años por sexo |
| `edad_15_44_{hombres,mujeres,indeterminado}` | Columnas P:R: edades de 15 a 44 años por sexo |
| `edad_45_64_{hombres,mujeres,indeterminado}` | Columnas S:U: edades de 45 a 64 años por sexo |
| `edad_65_mas_{hombres,mujeres,indeterminado}` | En 2008–2014, V:X; en 2015–2019, suma por sexo de los tres grupos de V:AD |
| `edad_desconocida_{hombres,mujeres,indeterminado}` | En 2008–2014, Y:AA; en 2015–2019, AE:AG; edad desconocida por sexo |

Cada expresión entre llaves representa tres columnas independientes.
No se conserva la columna de causa (B o E) porque todas las filas
seleccionadas corresponden al total de causas. El Parquet no contiene los
conteos de causas específicas. En 2020–2025 los grupos mayores proceden de
Y:AG y la edad desconocida de AH:AJ.

## Generación y consulta

Desde la raíz del repositorio, con las dependencias de `requirements.txt`:

```bash
.venv/bin/python scripts/processing/process_mortality_dane.py
.venv/bin/python -m unittest discover -s tests -p test_mortality_dane.py -v
```

El script exige los dieciocho archivos anuales por defecto. Acepta `--input-dir`
para cambiar la carpeta y `--input` para procesar solo un archivo; ambas
opciones son excluyentes. `--output` cambia el destino. Las rutas
predeterminadas funcionan desde cualquier directorio; el archivo de salida
se sobrescribe después de validar los totales.
Los tests verifican la exclusión de causas, los códigos, la correspondencia
con el Excel, los totales por año y departamento/categoría, y el rechazo de
diferencias, datos incompletos, duplicados y desgloses sin total. También
comparan las sumas de los tres grupos mayores contra todas las filas de los
Excel de 2015–2025 y verifican la propagación de componentes nulos, los
encabezados desplazados, los prefijos de nombres y los códigos de países.
Los casos de 2020–2025 cubren la propagación de departamentos, `TOTAL MUN`,
la exclusión de causas/nacional y la lectura de celdas vacías en XLSX.

El notebook [`mortality_dane_explore.ipynb`](../../../../notebooks/mortality_dane_explore.ipynb)
abre el Parquet, muestra el schema, tipos y nulos, y las primeras diez filas
con todos sus encabezados. Tanto el script como el notebook comparan las
sumas: agrupan por año y departamento/categoría y suman `total` de las filas distintas de `Total`
para comparar con el primer total de cada hoja: C13 en 2008–2016, C15 en 2017
y C14 en 2018–2019. En 2020–2025 compara la suma municipal con F de la fila
que identifica cada departamento/categoría. Incluye países y filas municipales
sin información; no compara los otros conteos por sexo y edad.

Resultado actual: **612 comparaciones coincidentes, ninguna diferencia y 18
grupos sin desglose**. La categoría sin información no tiene desglose en
ningún año. Bogotá incluye `11001` en todos los años procesados; en 2009–2018
la fila municipal se deriva del total departamental. La hoja `00` queda fuera
del Parquet para evitar duplicar el total nacional.

| Año | Filas | Defunciones, suma de filas `Total` |
| --- | ---: | ---: |
| 2008 | 1.200 | 196.943 |
| 2009 | 1.208 | 196.933 |
| 2010 | 1.216 | 200.524 |
| 2011 | 1.212 | 195.823 |
| 2012 | 1.206 | 199.756 |
| 2013 | 1.212 | 203.071 |
| 2014 | 1.203 | 210.051 |
| 2015 | 1.208 | 219.472 |
| 2016 | 1.209 | 223.078 |
| 2017 | 1.198 | 227.624 |
| 2018 | 1.190 | 236.932 |
| 2019 | 1.192 | 243.396 |
| 2020 | 1.188 | 300.853 |
| 2021 | 1.195 | 363.089 |
| 2022 | 1.195 | 287.251 |
| 2023 | 1.200 | 268.411 |
| 2024 | 1.199 | 275.778 |
| 2025 | 1.205 | 284.254 |

**No sumar totales departamentales junto con sus desgloses**: se duplicarían
las defunciones. Para identificar el total de una hoja usar
`nombre_municipio == "Total"`. La selección de filas por causa y las
posiciones del encabezado y la armonización de edades corresponden a los
formatos de 2008–2025. El consolidado conserva las versiones presentes en
raw; no añade registros tardíos ni corrige versiones anteriores. El origen,
los cortes y el estado de revisión de las entradas se documentan en el
[README de raw](../../../raw/births_mortality_dane/mortality/README.md).

## Armonización de Bogotá

Para 2009–2018, la hoja `11` solo contiene el total departamental. El
procesador conserva ese total y crea una fila municipal `11001` con el nombre
de Bogotá y exactamente los mismos 25 conteos. No se duplica si ya existe
el municipio. La validación compara esta fila derivada con el total; no
representa un desglose independiente publicado. Los raw no se modifican.

## Esquema físico y diccionario completo

Las 30 columnas siguientes están en el orden del Parquet local. `large_string` es texto y `int64` es entero de 64 bits. Los conteos ausentes se conservan como nulos; no se sustituyen por cero. La unidad es año × entidad territorial o categoría, incluyendo las filas Total descritas arriba.

| Columna | Tipo | Descripción |
| --- | --- | --- |
| `ano` | `int64` | Año de referencia de las defunciones, 2008–2025. |
| `codigo_departamento` | `large_string` | Código departamental como texto, conservando ceros iniciales. |
| `nombre_departamento` | `large_string` | Nombre del departamento o categoría especial. |
| `codigo_municipio` | `large_string` | Código municipal de cinco dígitos o convención de total/categoría especial. |
| `nombre_municipio` | `large_string` | Nombre del municipio, país o Total. |
| `total` | `int64` | Defunciones de todas las edades y sexos de la entidad. |
| `total_hombres` | `int64` | Defunciones de todas las edades; hombres. |
| `total_mujeres` | `int64` | Defunciones de todas las edades; mujeres. |
| `total_indeterminado` | `int64` | Defunciones de todas las edades; sexo indeterminado. |
| `edad_menor_1_hombres` | `int64` | Defunciones menores de 1 año; hombres. |
| `edad_menor_1_mujeres` | `int64` | Defunciones menores de 1 año; mujeres. |
| `edad_menor_1_indeterminado` | `int64` | Defunciones menores de 1 año; sexo indeterminado. |
| `edad_1_4_hombres` | `int64` | Defunciones de 1 a 4 años; hombres. |
| `edad_1_4_mujeres` | `int64` | Defunciones de 1 a 4 años; mujeres. |
| `edad_1_4_indeterminado` | `int64` | Defunciones de 1 a 4 años; sexo indeterminado. |
| `edad_5_14_hombres` | `int64` | Defunciones de 5 a 14 años; hombres. |
| `edad_5_14_mujeres` | `int64` | Defunciones de 5 a 14 años; mujeres. |
| `edad_5_14_indeterminado` | `int64` | Defunciones de 5 a 14 años; sexo indeterminado. |
| `edad_15_44_hombres` | `int64` | Defunciones de 15 a 44 años; hombres. |
| `edad_15_44_mujeres` | `int64` | Defunciones de 15 a 44 años; mujeres. |
| `edad_15_44_indeterminado` | `int64` | Defunciones de 15 a 44 años; sexo indeterminado. |
| `edad_45_64_hombres` | `int64` | Defunciones de 45 a 64 años; hombres. |
| `edad_45_64_mujeres` | `int64` | Defunciones de 45 a 64 años; mujeres. |
| `edad_45_64_indeterminado` | `int64` | Defunciones de 45 a 64 años; sexo indeterminado. |
| `edad_65_mas_hombres` | `int64` | Defunciones de 65 años o más; hombres. |
| `edad_65_mas_mujeres` | `int64` | Defunciones de 65 años o más; mujeres. |
| `edad_65_mas_indeterminado` | `int64` | Defunciones de 65 años o más; sexo indeterminado. |
| `edad_desconocida_hombres` | `int64` | Defunciones con edad desconocida; hombres. |
| `edad_desconocida_mujeres` | `int64` | Defunciones con edad desconocida; mujeres. |
| `edad_desconocida_indeterminado` | `int64` | Defunciones con edad desconocida; sexo indeterminado. |
