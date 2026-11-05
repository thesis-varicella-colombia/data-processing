# Ficha técnica: nacimientos por residencia de la madre — DANE, consolidado 2008–2025

| Campo | Descripción |
| --- | --- |
| Datos de entrada | [Archivos raw de nacimientos](../../../raw/births_mortality_dane/births/), 18 libros anuales |
| Documentación de entrada | [Ficha técnica de raw](../../../raw/births_mortality_dane/births/README.md): inventario, origen, versiones y estructura de los archivos |
| Archivo local | `births_2008.parquet`, un único archivo; el nombre se conserva, pero contiene **2008–2025** |
| Cobertura | Colombia y categorías de residencia en el extranjero y sin información |
| Unidad de observación | Año × entidad de residencia de la madre; incluye municipios, países, filas sin información y totales departamentales/categorías |
| Unidad de medida | Nacidos vivos; conteos enteros, no población ni tasas |
| Tamaño observado | **21.802 filas y 21 columnas** |
| Generación | [`process_births_dane.py`](../../../../scripts/processing/process_births_dane.py) |

## Cómo se generan los datos

El script parte de los 18 archivos anuales presentes en la
[carpeta raw de nacimientos](../../../raw/births_mortality_dane/births/),
descritos en su [README](../../../raw/births_mortality_dane/births/README.md),
y concatena los datos por nombre de columna. No incorpora el libro adicional
de registros tardíos. Las reglas de extracción son:

1. En 2008–2019, excluir `Indice` y `00`, localizar los encabezados de las
   hojas departamentales y de categorías especiales, y conservar sus totales
   y desgloses. Los encabezados determinan las columnas, incluidas las de
   sexo indeterminado que aparecen en algunas hojas desde 2014.
2. En 2020–2025, leer únicamente `Cuadro3`, C:T, con encabezados en 8–9.
   Excluir el total nacional de la fila 10. Extraer código y nombre del
   departamento de C y mantenerlos en las filas municipales con C vacía.
   Comprobar que cada código municipal empiece por el código departamental.
3. Separar códigos y nombres municipales; normalizar `Total Dpto` a `Total`.
   Conservar los códigos territoriales como texto y aplicar las convenciones
   especiales descritas abajo. No homologar nombres ni códigos a otro DIVIPOLA.
4. Conservar los conteos sin recalcularlos. Las columnas no presentes en una
   hoja y las celdas de conteo vacías se guardan nulas; no se imputan ceros.
5. Comparar únicamente `total` por año y departamento/categoría antes de
   escribir el archivo. Si la validación falla, no reemplazar el Parquet.

Los XLS protegidos se descifran en memoria sin modificar los originales.
Los XLSX de 2024–2025 se leen con sus valores almacenados; se omiten filas
vacías y notas al pie.

## Contenido y cobertura

Las filas `Total` son totales publicados de departamento/categoría. Los demás
registros son desgloses municipales, países de residencia en el extranjero
o filas de residencia sin información. La tabla no es una cuadrícula completa
de todos los municipios posibles por año. Los nombres conservan la escritura
de cada libro de entrada y pueden variar en mayúsculas o tildes entre años.

| Año | Filas consolidadas | Nacimientos publicados, suma de filas `Total` |
| --- | ---: | ---: |
| 2008 | 1.206 | 715.453 |
| 2009 | 1.208 | 699.775 |
| 2010 | 1.212 | 654.627 |
| 2011 | 1.206 | 665.499 |
| 2012 | 1.211 | 676.835 |
| 2013 | 1.207 | 658.835 |
| 2014 | 1.208 | 669.137 |
| 2015 | 1.206 | 660.999 |
| 2016 | 1.216 | 647.521 |
| 2017 | 1.215 | 656.704 |
| 2018 | 1.212 | 649.115 |
| 2019 | 1.211 | 639.820 |
| 2020 | 1.210 | 629.402 |
| 2021 | 1.219 | 616.914 |
| 2022 | 1.212 | 573.625 |
| 2023 | 1.212 | 515.549 |
| 2024 | 1.214 | 453.901 |
| 2025 | 1.217 | 441.537 |

Los nacimientos de esta tabla incluyen extranjeros y sin información,
según los grupos publicados. No se obtienen sumando todas las filas del
Parquet, porque eso sumaría totales y sus desgloses.

## Variables, tipos y nulos

Los tipos son los del esquema Arrow del Parquet inspeccionado. `int64` es
entero de 64 bits; `large_string` es texto. En pandas, los enteros se leen como
`Int64` nullable. Todos los conteos se expresan en nacimientos.

| Columna | Tipo Arrow | Nulos | Descripción |
| --- | --- | ---: | --- |
| `ano` | `int64` | 0 | Año de referencia, 2008–2025, verificado contra el título del cuadro. |
| `codigo_departamento` | `large_string` | 444 | Código original de dos dígitos; nulo para las categorías de extranjeros y sin información. |
| `nombre_departamento` | `large_string` | 0 | Nombre del departamento o categoría especial, sin prefijo de código. |
| `codigo_municipio` | `large_string` | 0 | Código municipal de cinco dígitos o convención de total/categoría especial. |
| `nombre_municipio` | `large_string` | 0 | Nombre del municipio/país sin código inicial, `Total` o nombre de fila sin información. |
| `total` | `int64` | 0 | Nacimientos totales de la fila, todos los sexos y áreas. |
| `total_hombres` | `int64` | 0 | Nacimientos de hombres, todas las áreas. |
| `total_mujeres` | `int64` | 0 | Nacimientos de mujeres, todas las áreas. |
| `cabecera_municipal_hombres` | `int64` | 0 | Hombres en cabecera municipal. |
| `cabecera_municipal_mujeres` | `int64` | 0 | Mujeres en cabecera municipal. |
| `centro_poblado_hombres` | `int64` | 0 | Hombres en centro poblado. |
| `centro_poblado_mujeres` | `int64` | 0 | Mujeres en centro poblado. |
| `rural_disperso_hombres` | `int64` | 0 | Hombres en rural disperso. |
| `rural_disperso_mujeres` | `int64` | 0 | Mujeres en rural disperso. |
| `sin_informacion_hombres` | `int64` | 0 | Hombres sin información de área. |
| `sin_informacion_mujeres` | `int64` | 0 | Mujeres sin información de área. |
| `total_indeterminado` | `int64` | 8.289 | Sexo indeterminado, todas las áreas; nulo si no se publica la columna. |
| `cabecera_municipal_indeterminado` | `int64` | 8.416 | Sexo indeterminado en cabecera municipal. |
| `centro_poblado_indeterminado` | `int64` | 8.458 | Sexo indeterminado en centro poblado. |
| `rural_disperso_indeterminado` | `int64` | 8.331 | Sexo indeterminado en rural disperso. |
| `sin_informacion_indeterminado` | `int64` | 8.458 | Sexo indeterminado sin información de área. |

Las convenciones de `codigo_municipio` son:

| Tipo de fila | Código guardado |
| --- | --- |
| Municipio identificado | Código original de cinco dígitos, con ceros iniciales |
| `Total` de un departamento | Código del departamento, de dos dígitos |
| País o `Total` de extranjeros | `-1` |
| Fila municipal sin información o cualquier fila de la categoría departamental sin información | `-2` |

`-1` y `-2` son convenciones del proyecto, no códigos DIVIPOLA. Se repiten y
no identifican una fila única. El perfil actual no tiene duplicados de la
combinación año, código y nombre de departamento, código y nombre de
municipio. Para identificar totales usar `nombre_municipio == "Total"`, no
solo la longitud del código, porque también hay totales de categorías especiales.

## Validación de totales

Por `ano`, `codigo_departamento` y `nombre_departamento`, la validación suma
**únicamente `total`** de las filas distintas de `Total` y compara con la fila
de total publicado. Incluye países y filas municipales sin información.
No valida el resto de las columnas por sexo o área.

Resultado actual: **600 grupos coinciden, ninguna diferencia y 30 grupos
sin desglose**. En 2008–2019 hay 33 comparaciones y dos grupos sin desglose
por año (Bogotá y sin información); en 2020–2025 hay 34 comparaciones y un
grupo sin desglose por año (sin información). Bogotá incluye detalle desde
2020. No se compara una fila sin desglose contra cero.

El script rechaza diferencias, valores de `total` incompletos, totales
duplicados y desgloses sin total. Que las sumas coincidan verifica la
consistencia de extracción, no la exhaustividad del registro de nacimientos.

## Generación y lectura

Desde la raíz del repositorio, con las dependencias de `requirements.txt`:

```bash
.venv/bin/python scripts/processing/process_births_dane.py
.venv/bin/python -m unittest discover -s tests -p test_births_dane.py -v
```

El script admite `--input-dir` y `--output`; sus rutas predeterminadas se
resuelven desde la raíz del repositorio, independientemente del directorio
de ejecución. Escribe primero un archivo temporal y después reemplaza
`data/processed/births_mortality_dane/births/births_2008.parquet`.

```python
import pandas as pd

births = pd.read_parquet(
    "data/processed/births_mortality_dane/births/births_2008.parquet"
)
totales_publicados = births.loc[births["nombre_municipio"].eq("Total")]
nacimientos_por_ano = totales_publicados.groupby("ano")["total"].sum()
```

El notebook [`births_dane_explore.ipynb`](../../../../notebooks/births_dane_explore.ipynb)
muestra schema, tipos, nulos, primeras diez filas y las comparaciones de
totales por año y departamento/categoría.

## Interpretación y limitaciones

**No sumar los totales junto con sus desgloses.** Para una serie nacional
usar las filas `Total`; para análisis municipal, seleccionar los códigos
municipales de cinco dígitos y tratar explícitamente los registros sin
información y las categorías especiales. Bogotá en 2008–2019 requiere una
decisión de armonización: su fila se conserva como total departamental con
código `11`, no se transforma automáticamente a `11001`.

El año es calendario, no epidemiológico. Los conteos son nacimientos por
residencia de la madre, no población residente ni nacimientos por lugar de
ocurrencia. No se distribuyen entre semanas ni se ajustan por cambios
territoriales. Un nulo de sexo indeterminado significa columna no publicada
o celda vacía; no equivale a cero.

El consolidado conserva las versiones de los archivos presentes en raw;
no añade registros tardíos ni corrige versiones anteriores. El origen, los
cortes y el estado de revisión de los datos de entrada se documentan en el
[README de raw](../../../raw/births_mortality_dane/births/README.md).

Perfil elaborado el **2026-11-05** sobre el Parquet local. Volver a calcular
filas, tipos, nulos y comparaciones si cambian los archivos o el procesador.
