# Ficha técnica: nacimientos por residencia de la madre — DANE, archivos originales

| Campo | Descripción |
| --- | --- |
| Fuente | [Nacimientos, Estadísticas Vitales del DANE](https://www.dane.gov.co/index.php/estadisticas-por-tema/salud/nacimientos-y-defunciones/nacimientos) |
| Cobertura local | Colombia, con categorías de residencia en el extranjero y sin información; 18 archivos anuales de 2008–2025 y un libro adicional de registros tardíos |
| Producto utilizado | Cuadro 3: nacimientos por área y sexo, según departamento y municipio de residencia de la madre |
| Unidad de observación | Entidad de residencia de la madre × año; incluye totales departamentales, municipios, países y categorías sin información |
| Unidad de medida | Nacidos vivos, expresados como conteos enteros; no población, tasas ni microdatos individuales |
| Formato | Excel: 16 archivos anuales XLS y dos XLSX; un XLSX adicional de registros tardíos |
| Producto derivado | [Parquet consolidado de nacimientos 2008–2025](../../../processed/births_mortality_dane/births/README.md) |

## Cómo se generan los datos

El DANE consolida y valida certificados de nacido vivo diligenciados por
personal autorizado, en papel o digitalmente. La certificación web mediante
RUAF-ND se implementó gradualmente desde 2008. Estos libros contienen cuadros
agregados publicados por el DANE. El Cuadro 3 organiza los nacimientos por
**residencia de la madre**, que puede diferir del lugar donde ocurrió el
nacimiento. Fuente: [descripción oficial de nacimientos](https://www.dane.gov.co/index.php/estadisticas-por-tema/salud/nacimientos-y-defunciones/nacimientos).

## Archivos y descarga

Abrir la página de la fuente, seleccionar el año y descargar el **Cuadro 3**
para 2008–2019 o los **cuadros unificados** para 2020–2025. Guardar los libros
originales en esta carpeta con los nombres indicados abajo. El repositorio
no tiene un script de descarga para esta fuente. No sustituir un archivo por
otra revisión sin documentar el cambio de versión y regenerar el derivado.

| Periodo | Archivo local | Contenido utilizado |
| --- | --- | --- |
| 2008–2019 | `Cuadro3_AAAA.xls` (12 libros, uno por año) | Hojas departamentales de dos dígitos, `Extranjeros` y `Sin_información`; se excluyen `Indice` y `00` |
| 2020 | `nacimientos2020-cuadro-definitivo-2020.xls` | Hoja `Cuadro3` |
| 2021 | `nacimientos2021-cuadro-definitivo-2021.xls` | Hoja `Cuadro3` |
| 2022 | `nacimientos2022-cuadro-definitivo-2022.xls` | Hoja `Cuadro3` |
| 2023 | `anex-EEVV-Nacimientos2023pCuadroDefinivo-2023.xls` | Hoja `Cuadro3` |
| 2024 | `anex-EEVV-NacimientosCuadroAcumulado-2024.xlsx` | Hoja `Cuadro3` |
| 2025 | `anex-EEVV-NacimientosCuadroAcumulado-2025.xlsx` | Hoja `Cuadro3` |
| 2003–2024, registros tardíos | `anex-EEVV-RegistrosTardiosNacimientos-2003a2024-sep2026.xlsx` | Archivo adicional conservado en raw; **no procesado ni sumado al Parquet** |

El libro de registros tardíos contiene `Indice` y hojas
`Nacimientos_Ocu_AAAA` y `Nacimientos_Res_AAAA` de 2003 a 2024: conteos por
sexo, departamento de ocurrencia o residencia y grupos de edad de la madre.
No tiene la misma estructura municipal del Cuadro 3. El índice local conserva
un texto de actualización de una versión anterior; no usarlo como fecha de
corte de todas sus hojas. La [página oficial](https://www.dane.gov.co/index.php/estadisticas-por-tema/salud/nacimientos-y-defunciones/nacimientos)
publica estos registros por separado, posteriores al cierre de las cifras
definitivas; no deben añadirse automáticamente a esta serie.

## Variables y estructura

Los encabezados están distribuidos en dos filas con celdas combinadas. Las
columnas numéricas contienen el total general y su desglose por sexo y área.

| Variable original | Contenido y unidad |
| --- | --- |
| Departamento | Código de dos dígitos y nombre; en libros antiguos el código es el nombre de la hoja |
| Municipio o país | Código y nombre de residencia de la madre; incluye filas `Total` y sin información |
| Total | Nacimientos, todos los sexos y áreas |
| Sexo | Hombres, mujeres y, donde aparece, indeterminado |
| Cabecera municipal | Conteos por sexo para esta área de residencia |
| Centro poblado | Conteos por sexo para esta área de residencia |
| Rural disperso | Conteos por sexo para esta área de residencia |
| Sin información | Conteos por sexo sin información de área; no equivale a desconocer el municipio o el departamento |
| Año | Año de referencia declarado en el título del cuadro |

| Archivos | Encabezados y datos observados |
| --- | --- |
| 2008–2013 | Encabezados en 11–12 y datos desde 13, columnas A:L; A contiene código y nombre municipal |
| 2014 | Encabezados en 11–12; algunas hojas agregan columnas de sexo indeterminado y llegan hasta N; otras conservan A:L |
| 2015–2016 | Encabezados en 11–12, datos desde 13, columnas A:Q; incluyen sexo indeterminado para total y áreas |
| 2017 | Encabezados en 13–14, datos desde 15, columnas A:Q |
| 2018–2019 | Encabezados en 12–13, datos desde 14, columnas A:Q |
| 2020–2025 | Hoja `Cuadro3`, encabezados en 8–9 y datos desde 10, columnas C:T; C identifica el departamento, D el municipio y E:T los conteos |

En 2008–2019, cada hoja tiene un total y sus desgloses; Bogotá solo tiene la
fila `Total`. En 2020–2025, la fila 10 es el total nacional; las filas con C
no vacía identifican los totales de departamento/categoría y las siguientes
filas con C vacía pertenecen a ese grupo. D dice `Total` en 2020–2024 y
`Total Dpto` en el archivo local de 2025. Los códigos municipales tienen cinco
dígitos y sus dos primeros coinciden con el departamento; los códigos de
país no son códigos municipales. Conservar los códigos como texto.

Los XLS de 2020–2023 están cifrados con la clave estándar de Excel; el
procesador los abre en memoria mediante `msoffcrypto-tool` y `xlrd`. Los XLSX
se leen con `openpyxl`. Los originales permanecen sin transformaciones.

## Temporalidad y precauciones

Los años identifican el periodo del nacimiento y los libros pueden tener
distintas fechas de cierre, publicación o revisión. El nombre del archivo no
determina por sí solo si sus cifras son preliminares o definitivas:

| Archivo local | Estado o corte documentado |
| --- | --- |
| `Cuadro3_2019.xls` | El título local indica acumulado preliminar de nacimientos ocurridos en 2019 y reportados hasta el 31 de julio de 2020; se conserva esa versión |
| Libro de 2023 | La [publicación anual 2023](https://www.dane.gov.co/index.php/estadisticas-por-tema/salud/nacimientos-y-defunciones/nacimientos/nacimientos-2023) identifica cifras definitivas publicadas el 19 de diciembre de 2024; coincide con la actualización del libro local, aunque el nombre incluye `2023p` |
| Libro de 2024 | La [publicación anual 2024](https://www.dane.gov.co/index.php/estadisticas-por-tema/salud/nacimientos-y-defunciones/nacimientos/nacimientos-2024) identifica cifras definitivas actualizadas el 6 de febrero de 2026; coincide con la actualización local, aunque el archivo se llama `CuadroAcumulado` |
| Libro de 2025 | La [publicación anual 2025](https://www.dane.gov.co/index.php/estadisticas-por-tema/salud/nacimientos-y-defunciones/nacimientos/nacimientos-2025) identifica cifras definitivas publicadas el 24 de septiembre de 2026; coincide con la actualización local, aunque el archivo se llama `CuadroAcumulado` |

**No sumar totales y desgloses juntos**: se duplicarían nacimientos. La
ausencia de una columna de sexo indeterminado no equivale a un cero
observado. La categoría de área sin información es distinta de los grupos
territoriales sin información. Los códigos y nombres corresponden a cada
libro: no se homologan automáticamente a una versión actual de DIVIPOLA.
Esta fuente es anual, no semanal ni una medida de población residente.

Ficha elaborada mediante inspección de los archivos locales y de la fuente
oficial el **2026-11-05**. Las cifras pueden cambiar con nuevas descargas.
