# Ficha técnica: coberturas municipales de vacunación — PAI

| Campo | Descripción |
| --- | --- |
| Fuente | [Coberturas de vacunación, Programa Ampliado de Inmunizaciones (PAI), Ministerio de Salud y Protección Social](https://vacunacion.minsalud.gov.co/RT/Paginas/Coberturas-de-vacunacion.aspx) |
| Repositorio de origen | [Repositorio 1998 a 2025 enlazado por el Ministerio](https://www.minsalud.gov.co/sites/rid/Lists/BibliotecaDigital/RIDE/VS/PP/PAI/coberturas-vacunacion-municipal-desde-1998.zip) |
| Archivo local | `Coberturas de Vacunacion Municipal desde 1998-2025(30-01-2025).xlsx` (aprox. 16 MiB) |
| Formato y periodo | Libro Excel con 28 hojas anuales, `1998`–`2025`, y cuatro hojas adicionales: `CONSOLIDADO_AÑOS`, `Departamento`, `Municipio` y `Cob_Trazad2019-2024` |
| Unidad de observación principal | Municipio × año; cada hoja contiene varias columnas de biológico, dosis y grupo objetivo |
| Identificación territorial | `DIVIPOLA`, `Municipio`, código y nombre de departamento; los encabezados varían entre hojas |

## Cómo se generan los datos

El PAI consolida información sobre la **aplicación de vacunas**. Según el Ministerio, los puntos de vacunación, equipos extramurales, municipios y departamentos reportan las aplicaciones a su nivel superior; el programa consolida la información diaria y mensualmente. Este libro presenta resultados agregados de ese sistema de reporte. No contiene registros individuales de vacunación ni permite verificar el esquema de una persona.

Para reproducir la obtención del archivo, abrir la [página de coberturas](https://vacunacion.minsalud.gov.co/RT/Paginas/Coberturas-de-vacunacion.aspx), seguir el enlace **Repositorio 1998 a 2025**, descargar el ZIP y extraer el libro Excel en esta carpeta. El archivo local se conserva sin transformaciones; **no hay un script de descarga ni de procesamiento para este conjunto** en el repositorio. Una descarga posterior puede contener revisiones de los datos.

## Variables disponibles

Las hojas anuales incluyen códigos y nombres territoriales, **población objetivo o meta programática**, números de dosis aplicadas y columnas de **cobertura** (`%`) para biológicos, dosis y edades específicas. Entre los encabezados observados figuran BCG, hepatitis B, polio/VIP, pentavalente, rotavirus, triple viral/SRP, DPT y VPH. La oferta de variables cambia con el calendario de vacunación y con el diseño de cada hoja; por ejemplo, la hoja de 1998 tiene 27 columnas y la de 2025 tiene 158.

Las columnas de población se usan como referencia o denominador de cobertura; las de dosis son conteos de aplicaciones. **No se debe asumir una escala numérica uniforme para las columnas `%`:** en 1998 se observan proporciones como `0,929`, mientras que en 2025 se observan valores como `105,2`. Antes de comparar años, revisar el encabezado y la escala efectiva de cada hoja. Las coberturas pueden superar 100 y no deben truncarse automáticamente. Conservar `DIVIPOLA` como texto para mantener ceros iniciales.

## Temporalidad y precauciones

Cada hoja anual indica su propio corte. Por ejemplo, la hoja `2023` dice **noviembre de 2023** y las hojas `2024` y `2025` dicen **diciembre** de sus respectivos años. El nombre del archivo local incluye `(30-01-2025)`, pero la hoja `2025` dice «diciembre 2025»; por ello, **el nombre del archivo no debe usarse como fecha de corte de todo el libro**. La fecha exacta de extracción del portal no está registrada en esta carpeta.

El libro tiene filas de títulos, encabezados, posibles totales y estructuras distintas entre años; no es una tabla rectangular única lista para concatenar. Algunas hojas incluyen más filas que municipios. Para un análisis municipal, seleccionar explícitamente las filas con códigos territoriales válidos, revisar los cambios de DIVIPOLA y documentar cómo se armonizan biológicos, dosis, denominadores y escalas de cobertura. Estas coberturas son indicadores administrativos agregados, no datos semanales ni mediciones individuales; no se pueden alinear directamente con las semanas epidemiológicas de Sivigila o del clima.

Ficha elaborada mediante inspección del libro local y de la [descripción oficial del PAI](https://vacunacion.minsalud.gov.co/RT/Paginas/Coberturas-de-vacunacion.aspx).
