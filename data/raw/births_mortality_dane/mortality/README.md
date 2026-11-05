# Ficha técnica: defunciones no fetales por residencia — DANE, archivos originales

| Campo | Descripción |
| --- | --- |
| Fuente | [Defunciones, Estadísticas Vitales del DANE](https://www.dane.gov.co/index.php/estadisticas-por-tema/salud/nacimientos-y-defunciones/defunciones) |
| Cobertura local | Colombia, con categorías de residencia en el extranjero y sin información; 18 libros anuales de 2008–2025 |
| Producto utilizado | Cuadro 5: defunciones por grupos de edad y sexo, según departamento, municipio de residencia y grupos de causas |
| Unidad de observación | Entidad de residencia × año × causa o total de causas; incluye totales nacionales, departamentales y desgloses municipales/países |
| Unidad de medida | Defunciones no fetales, expresadas como conteos enteros; no población, tasas ni microdatos individuales |
| Formato | Excel: 16 archivos XLS (2008–2023) y dos XLSX (2024–2025) |
| Producto derivado | [Parquet consolidado de defunciones 2008–2025](../../../processed/births_mortality_dane/mortality/README.md) |

## Cómo se generan los datos

El DANE consolida y valida certificados de defunción físicos o digitales,
diligenciados por personal autorizado, y procesa la información de edad,
sexo, causas y residencia habitual del fallecido. La certificación web se
implementó desde 2008 mediante RUAF-ND. Las defunciones no fetales corresponden
a fallecimientos posteriores al nacimiento con vida y excluyen las fetales.
Fuente: [descripción oficial de defunciones](https://www.dane.gov.co/index.php/estadisticas-por-tema/salud/nacimientos-y-defunciones/defunciones).

El Cuadro 5 agrupa por **residencia del fallecido**, que puede diferir del
lugar de ocurrencia. Los grupos de causas se identifican en los títulos como
lista agrupada 6/67 de la CIE-10 de OPS. Los libros raw conservan las filas de
causas específicas, además de los totales que utiliza el procesador.

## Archivos y descarga

Abrir la página de la fuente, seleccionar el año en **Defunciones no
fetales** y descargar el **Cuadro 5** para 2008–2019 o los **cuadros
unificados** para 2020–2025. Guardar los originales en esta carpeta con los
nombres indicados abajo. No hay un script de descarga para esta fuente en
el repositorio. La fecha exacta de descarga no está registrada.

| Periodo | Archivo local | Contenido utilizado |
| --- | --- | --- |
| 2008–2019 | `cuadro5_AAAA.xls` (12 libros, uno por año) | Hojas de código departamental de dos dígitos, `Extranjeros` y `Sin_información`; `00` contiene el total nacional y desde 2009 también hay índice |
| 2020 | `defunciones-no-fetales2020-cuadros-unificados-definitivo-2020.xls` | Hoja `Cuadro5` |
| 2021 | `defunciones-no-fetales2021-cuadro-definitivo-2021.xls` | Hoja `Cuadro5` |
| 2022 | `defunciones-no-fetales2022-cuadro-definitivo-2022.xls` | Hoja `Cuadro5` |
| 2023 | `anex-EEVV-DefuncionesNoFetales2023pCuadroDefinitivo-2023.xls` | Hoja `Cuadro5` |
| 2024 | `anex-EEVV-DefuncionesNoFetalesCuadroUnificado-2024.xlsx` | Hoja `Cuadro5` |
| 2025 | `anex-EEVV-DefuncionesNoFetalesCuadroUnificado-2025.xlsx` | Hoja `Cuadro5` |

Los libros unificados contienen otros cuadros que no se incorporan al
Parquet. Los archivos de esta carpeta se conservan sin transformaciones.
Los XLS de 2020–2023 vienen cifrados con la clave estándar de Excel; el
procesador los abre en memoria con `msoffcrypto-tool` y `xlrd`, sin modificar
los originales. Los XLSX se leen con `openpyxl`.

## Variables y estructura

| Variable original | Contenido y unidad |
| --- | --- |
| Departamento | Código de dos dígitos y nombre; en 2008–2019 el código es el nombre de la hoja |
| Municipio o país | Código y nombre de residencia; los códigos municipales tienen cinco dígitos y los países pueden tener tres o cinco |
| Causa | Código y descripción del grupo de causas, o una etiqueta de total |
| Total | Defunciones de todas las edades y sexos para la entidad y causa de la fila |
| Sexo | Hombres, mujeres e indeterminado |
| Grupos de edad | Menor de 1 año, 1–4, 5–14, 15–44, 45–64 y grupos mayores, desagregados por sexo |
| Edad desconocida | Conteos por sexo sin edad conocida; es distinta de la residencia sin información |
| Año | Año de referencia declarado en el título del cuadro |

| Archivos | Encabezados y datos observados |
| --- | --- |
| 2008–2014 | Encabezados en 11–12, datos desde 13, A:AA; departamento/categoría en A10 |
| 2015–2016 | Encabezados en 11–12, datos desde 13, A:AG; departamento/categoría en A10 |
| 2017 | Encabezados en 13–14, datos desde 15, A:AG; departamento/categoría en A12 |
| 2018–2019 | Encabezados en 12–13, datos desde 14, A:AG; departamento/categoría en A11 |
| 2020–2025 | Hoja `Cuadro5`, encabezados en 8–9, datos desde 10, C:AJ; C identifica el departamento y D el municipio |

En 2008–2019, A contiene el código y nombre municipal/país, B la causa y C
el total numérico. La primera fila de datos de cada hoja territorial tiene
A y B iguales a `TOTAL`; las siguientes filas detallan causas. Cada municipio
o país tiene también su fila B=`TOTAL` y el detalle de causas debajo. En
2020–2025, E contiene la causa, F el total numérico y G:AJ los desgloses por
edad y sexo. La fila 10 es el total nacional; siguen sus causas y los bloques
departamentales y municipales. C y D pueden estar vacías en las filas de
detalle: el territorio se interpreta dentro de su bloque.

En 2020–2024 las filas con departamento en C tienen D=`Total Dpto`; en 2025
D está vacía en esas filas. Las causas de totales se etiquetan `TOTAL` o
`Total`; en 2025 los totales municipales usan **`TOTAL MUN`**, mientras los
países conservan `Total`. Las filas municipales sin información deben
conservarse al comparar sumas con los totales departamentales.

En 2008–2014 el grupo mayor es **65 y más**. Desde 2015 se divide en
**65–84**, **85–99** y **100 y más**, cada uno por sexo. El raw conserva esta
desagregación; la suma para armonizarla con los años anteriores se realiza
en el [procesamiento](../../../processed/births_mortality_dane/mortality/README.md).
La edad desconocida permanece separada.

Algunos encabezados antiguos mencionan residencia de la madre, pero el
título del Cuadro 5 corresponde a defunciones por residencia. Los nombres
territoriales pueden cambiar en mayúsculas o tildes entre libros. Desde
2017 algunos títulos territoriales llevan prefijo de código. Conservar los
códigos como texto para mantener ceros iniciales; los códigos de países no
son códigos municipales.

## Temporalidad y precauciones

El año es calendario y corresponde al periodo de referencia, no a la fecha
de descarga o publicación. La carpeta conserva las versiones locales; no
se deben sustituir por otra revisión sin documentarlo y regenerar el derivado.

| Archivo local | Estado o corte documentado |
| --- | --- |
| `cuadro5_2019.xls` | El título indica cifras preliminares de defunciones no fetales de 2019 reportadas hasta el 31 de julio de 2020 |
| Libro de 2023 | La [publicación anual 2023](https://www.dane.gov.co/index.php/estadisticas-por-tema/salud/nacimientos-y-defunciones/defunciones-no-fetales/defunciones-no-fetales-2023) identifica cifras definitivas publicadas el 19 de diciembre de 2024, fecha que coincide con la actualización local; el nombre incluye `2023p` |
| Libro de 2024 | La [publicación anual 2024](https://www.dane.gov.co/index.php/estadisticas-por-tema/salud/nacimientos-y-defunciones/defunciones-no-fetales/defunciones-no-fetales-2024) identifica cifras definitivas actualizadas el 6 de febrero de 2026, coincidente con la fecha del libro local |
| Libro de 2025 | La [publicación anual 2025](https://www.dane.gov.co/index.php/estadisticas-por-tema/salud/nacimientos-y-defunciones/defunciones-no-fetales/defunciones-no-fetales-2025) identifica cifras definitivas publicadas el 24 de septiembre de 2026, coincidente con la fecha del libro local |

La página del DANE también publica [registros tardíos](https://www.dane.gov.co/index.php/estadisticas-por-tema/salud/nacimientos-y-defunciones/defunciones)
reportados después del cierre de las cifras definitivas. No hay un libro de
registros tardíos en el inventario local de esta carpeta y el consolidado
actual no los añade.

**No sumar totales y sus desgloses juntos**, ni filas de total de causas con
las causas específicas: se duplicarían defunciones. Bogotá tiene desglose
municipal en 2008 y desde 2019; en 2009–2018 solo tiene total departamental.
La categoría de residencia sin información solo tiene total, sin desglose
territorial. La ausencia de una entidad no demuestra un cero observado.

Los conteos son anuales, no semanales ni tasas. Para calcular tasas se requiere
un denominador y armonización territorial explícitos; no se deben interpretar
como población residente. Los códigos y nombres corresponden a cada libro y
no se homologan automáticamente a un DIVIPOLA actual.

Ficha elaborada mediante inspección de los archivos locales y de la fuente
oficial el **2026-11-05**. Las cifras pueden cambiar con nuevas descargas.
