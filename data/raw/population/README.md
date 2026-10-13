# Ficha técnica: proyecciones y retroproyecciones municipales de población — DANE

| Campo | Descripción |
| --- | --- |
| Fuente | [Proyecciones de población del DANE](https://www.dane.gov.co/index.php/estadisticas-por-tema/demografia-y-poblacion/proyecciones-de-poblacion), sección municipal por área, sexo y edad |
| Base estadística | Censo Nacional de Población y Vivienda (CNPV) 2018; el DANE indica que las series fueron actualizadas con información posterior a la pandemia de COVID-19 |
| Cobertura local | Municipios de Colombia; años 2005–2042 mediante dos libros Excel |
| Unidad principal | Municipio × año × área geográfica; población desagregada por sexo y edad simple en columnas |
| Unidad de medida | Personas estimadas o proyectadas, no registros individuales |

## Archivos y descarga

| Archivo local | Enlace de descarga del DANE | Contenido inspeccionado |
| --- | --- | --- |
| `DCD-area-sexo-edad-proypoblacion-Mun-2005-2017_VP.xlsx` (aprox. 53 MiB) | [Serie municipal 2005–2017 por área, sexo y edad](https://www.dane.gov.co/files/censo2018/proyecciones-de-poblacion/Municipal/DCD-area-sexo-edad-proypoblacion-Mun-2005-2017_VP.xlsx) | Hoja `NuevaMpal`, 43.770 filas y 267 columnas; datos desde la fila 13 |
| `PPED-AreaSexoEdadMun-2018-2042_VP.xlsx` (aprox. 126 MiB) | [Serie municipal 2018–2042 por área, sexo y edad](https://www.dane.gov.co/files/censo2018/proyecciones-de-poblacion/Municipal/PPED-AreaSexoEdadMun-2018-2042_VP.xlsx) | Hojas `Índice`, `PPED` y `PobMunicipalxÁreaSexoEdad`; esta última tiene 84.245 filas y 312 columnas, con datos desde la fila 10 |

Para reproducir la obtención, abrir la [página de proyecciones](https://www.dane.gov.co/index.php/estadisticas-por-tema/demografia-y-poblacion/proyecciones-de-poblacion), ir a **Proyecciones y retroproyecciones de población municipal** y descargar las dos series **por área, sexo y edad** para 2005–2017 y 2018–2042. Guardar los Excel originales en esta carpeta. No hay un script de descarga o transformación de población en este repositorio. El libro 2018–2042 indica en su hoja `PPED` «Actualizado el 30 de Julio de 2025»; una descarga futura puede incorporar revisiones.

## Variables y estructura

Ambos libros incluyen año (`AÑO`), departamento (`DP`, `DPNOM`), identificador y nombre municipal, y `ÁREA GEOGRÁFICA`: **Cabecera Municipal**, **Centros Poblados y Rural Disperso** y **Total**. Para obtener una población municipal total, usar únicamente la fila `Total` de cada municipio y año; sumar las tres áreas duplicaría la población.

Los nombres `MPIO` y `DPMP` **cambian de significado entre libros**:

| Libro | Código municipal de cinco dígitos | Nombre municipal |
| --- | --- | --- |
| 2005–2017 | `MPIO` | `DPMP` |
| 2018–2042 | `DPMP` | `MPIO` |

Tratar el código como texto para conservar los ceros iniciales. La serie 2005–2017 tiene columnas `Hombres_<edad>`, `Mujeres_<edad>` y `Total_<edad>` hasta **85 y más**, además de `Total Hombres`, `Total Mujeres` y `Total General`. La serie 2018–2042 tiene `Total`, `Hombres`, `Mujeres` y columnas por sexo y total hasta **100 años y más**. Antes de unir ambas series o calcular grupos etarios, armonizar las edades finales y los nombres de columnas; la distinta categoría abierta impide comparar directamente el grupo de 85 años y más con el de 100 años y más.

## Interpretación y uso

El DANE elabora estas series a partir del CNPV 2018 y de modelos demográficos; el libro 2018–2042 menciona un modelo de componentes de cohortes con enfoque multirregional adaptado. Los valores de cada año son **estimaciones o proyecciones anuales**, no conteos observados ese año ni población semanal. Para tasas municipales de Sivigila, documentar el año de población elegido como denominador y la forma de aplicarlo a las semanas epidemiológicas. Revisar también cambios de códigos o límites municipales antes de cruzarlos con DIVIPOLA.

Referencias: [página de proyecciones del DANE](https://www.dane.gov.co/index.php/estadisticas-por-tema/demografia-y-poblacion/proyecciones-de-poblacion) · [documento metodológico de las proyecciones de población](https://www.dane.gov.co/files/censo2018/proyecciones-de-poblacion/Documento-metodologico-proyecciones.pdf).
