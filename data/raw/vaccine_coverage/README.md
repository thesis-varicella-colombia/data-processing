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

Para reproducir la obtención del archivo, abrir la [página de coberturas](https://vacunacion.minsalud.gov.co/RT/Paginas/Coberturas-de-vacunacion.aspx), seguir el enlace **Repositorio 1998 a 2025**, descargar el ZIP y extraer el libro Excel en esta carpeta. El archivo local se conserva sin transformaciones; no hay un script de descarga. El [procesador de varicela](../../processed/vaccine_coverage/README.md) genera el CSV municipal utilizado en el análisis. Una descarga posterior puede contener revisiones de los datos.

## Variables disponibles

Las hojas anuales incluyen códigos y nombres territoriales, **población objetivo o meta programática**, números de dosis aplicadas y columnas de **cobertura** (`%`) para biológicos, dosis y edades específicas. Entre los encabezados observados figuran BCG, hepatitis B, polio/VIP, pentavalente, rotavirus, triple viral/SRP, DPT y VPH. La oferta de variables cambia con el calendario de vacunación y con el diseño de cada hoja; por ejemplo, la hoja de 1998 tiene 27 columnas y la de 2025 tiene 158.

Las columnas de población se usan como referencia o denominador de cobertura; las de dosis son conteos de aplicaciones. **No se debe asumir una escala numérica uniforme para las columnas `%`:** en 1998 se observan proporciones como `0,929`, mientras que en 2025 se observan valores como `105,2`. Antes de comparar años, revisar el encabezado y la escala efectiva de cada hoja. Las coberturas pueden superar 100 y no deben truncarse automáticamente. Conservar `DIVIPOLA` como texto para mantener ceros iniciales.

## Temporalidad y precauciones

Cada hoja anual indica su propio corte. Por ejemplo, la hoja `2023` dice **noviembre de 2023** y las hojas `2024` y `2025` dicen **diciembre** de sus respectivos años. El nombre del archivo local incluye `(30-01-2025)`, pero la hoja `2025` dice «diciembre 2025»; por ello, **el nombre del archivo no debe usarse como fecha de corte de todo el libro**. La fecha exacta de extracción del portal no está registrada en esta carpeta.

El libro tiene filas de títulos, encabezados, posibles totales y estructuras distintas entre años; no es una tabla rectangular única lista para concatenar. Algunas hojas incluyen más filas que municipios. Para un análisis municipal, seleccionar explícitamente las filas con códigos territoriales válidos, revisar los cambios de DIVIPOLA y documentar cómo se armonizan biológicos, dosis, denominadores y escalas de cobertura. Estas coberturas son indicadores administrativos agregados, no datos semanales ni mediciones individuales; no se pueden alinear directamente con las semanas epidemiológicas de Sivigila o del clima.

Ficha elaborada mediante inspección del libro local y de la [descripción oficial del PAI](https://vacunacion.minsalud.gov.co/RT/Paginas/Coberturas-de-vacunacion.aspx).

## Esquema y diccionario de los datos anuales

Cada hoja anual es una tabla municipio × año con títulos antes del encabezado.
No tiene un esquema físico uniforme: Excel permite mezclar números, textos,
fórmulas y vacíos. Los siguientes son tipos lógicos de lectura. Las medidas
se documentan como reales porque los originales pueden contener fracciones;
no se fuerza un entero ni se convierte un vacío en cero. Los códigos son texto.
Las columnas `%` requieren revisar la escala de cada hoja, como se explicó arriba.

El inventario siguiente se verificó en los encabezados locales. Se cuentan
solo columnas con encabezado, excluyendo celdas vacías y columnas de formato.
Las hojas de índice, catálogos y consolidaciones tienen estructuras distintas
y no se tratan como tablas anuales de coberturas.

| Hoja/año | Fila de encabezado (Excel, desde 1) | Columnas con nombre |
| --- | --- | --- |
| 1998 | 5 | 20 |
| 1999 | 5 | 20 |
| 2000 | 5 | 20 |
| 2001 | 5 | 20 |
| 2002 | 5 | 20 |
| 2003 | 5 | 20 |
| 2004 | 5 | 18 |
| 2005 | 5 | 18 |
| 2006 | 5 | 18 |
| 2007 | 5 | 18 |
| 2008 | 6 | 18 |
| 2009 | 5 | 26 |
| 2010 | 5 | 33 |
| 2011 | 5 | 56 |
| 2012 | 5 | 64 |
| 2013 | 5 | 65 |
| 2014 | 5 | 65 |
| 2015 | 5 | 68 |
| 2016 | 6 | 73 |
| 2017 | 5 | 78 |
| 2018 | 5 | 76 |
| 2019 | 5 | 84 |
| 2020 | 5 | 85 |
| 2021 | 5 | 86 |
| 2022 | 5 | 86 |
| 2023 | 5 | 89 |
| 2024 | 5 | 117 |
| 2025 | 5 | 153 |

### Diccionario de los 355 encabezados anuales distintos

Cada nombre se conserva tal como aparece en el libro (los saltos de línea se
conservan visualmente); las variantes ortográficas no se fusionan. «Hojas»
indica dónde aparece el campo. Un nombre puede repetirse dentro de una hoja:
para seleccionarlo se debe conservar también su posición original. La
descripción de dosis o población se completa con el biológico, grupo, dosis y
periodo escritos en el propio encabezado. Los indicadores territoriales sin
catálogo local se dejan como categorías sin homologar.

<details>
<summary>Ver todos los encabezados, tipos lógicos y significados</summary>

| Encabezado original | Tipo lógico | Descripción | Hojas |
| --- | --- | --- | --- |
| `CORPES` | texto | Nombre o agrupación territorial publicada. | 1998–2003 |
| `PROVINCIA` | texto | Nombre o agrupación territorial publicada. | 1998–2003 |
| `CODEP` | texto | Código territorial; conservar ceros iniciales. | 1998–2025 |
| `Nombre_ET` | texto | Nombre o agrupación territorial publicada. | 1998–2025 |
| `DIVIPOLA` | texto | Código territorial; conservar ceros iniciales. | 1998–2025 |
| `Municipio` | texto | Nombre o agrupación territorial publicada. | 1998–2025 |
| `MENORES DE UN AÑO` | real | Población, meta o proyección publicada para el grupo y periodo del encabezado; personas. | 1998–2002 |
| `Polio < DE 1 AÑO 3ras Dosis` | real | Dosis/aplicaciones publicadas para el biológico, edad y esquema del encabezado; conservar el valor original. | 1998–2014, 2020 |
| `% 3ras. Dosis de Polio` | real | Cobertura/indicador publicado para el biológico y grupo del encabezado; verificar escala en cada hoja. | 1998–2020 |
| `PENTA MENOR DE UN AÑO 3ras` | real | Dosis/aplicaciones publicadas para el biológico, edad y esquema del encabezado; conservar el valor original. | 1998–2025 |
| `% Pentavalente 3ras. Dosis` | real | Cobertura/indicador publicado para el biológico y grupo del encabezado; verificar escala en cada hoja. | 1998–2014 |
| `B.C.G (Tuberculosis) en Recién Nacidos` | real | Dosis/aplicaciones publicadas para el biológico, edad y esquema del encabezado; conservar el valor original. | 1998–2014 |
| `% B.C.G (Tuberculosis) en Recién Nacidos` | real | Cobertura/indicador publicado para el biológico y grupo del encabezado; verificar escala en cada hoja. | 1998–2009, 2015–2025 |
| `HB MENOR DE UN AÑO 3ras` | real | Dosis/aplicaciones publicadas para el biológico, edad y esquema del encabezado; conservar el valor original. | 1998–2012 |
| `% Hepatitis B` | real | Cobertura/indicador publicado para el biológico y grupo del encabezado; verificar escala en cada hoja. | 1998–2012 |
| `HiB MENOR DE UN AÑO 3ras` | real | Dosis/aplicaciones publicadas para el biológico, edad y esquema del encabezado; conservar el valor original. | 1998–2012 |
| `%Hib < 1 Año 3ras` | real | Cobertura/indicador publicado para el biológico y grupo del encabezado; verificar escala en cada hoja. | 1998–2012 |
| `Población de 1 Año` | real | Población, meta o proyección publicada para el grupo y periodo del encabezado; personas. | 1998–2004 |
| `SRP (T.V.) DE UN AÑO`<br>`D. Unica` | real | Dosis/aplicaciones publicadas para el biológico, edad y esquema del encabezado; conservar el valor original. | 1998–2025 |
| `% de TV al Año de edad` | real | Cobertura/indicador publicado para el biológico y grupo del encabezado; verificar escala en cada hoja. | 1998–2014 |
| `Población Menor de un año` | real | Población, meta o proyección publicada para el grupo y periodo del encabezado; personas. | 2003 |
| `Población Menor de 1 Año` | real | Población, meta o proyección publicada para el grupo y periodo del encabezado; personas. | 2004 |
| `Población menor de 1 año (1)` | real | Población, meta o proyección publicada para el grupo y periodo del encabezado; personas. | 2005–2007 |
| `Población de 1 año (1)` | real | Población, meta o proyección publicada para el grupo y periodo del encabezado; personas. | 2005–2007 |
| `Poblaciòn Menor de 1 año` | real | Población, meta o proyección publicada para el grupo y periodo del encabezado; personas. | 2008–2011 |
| `Poblaciòn de 1 año` | real | Población, meta o proyección publicada para el grupo y periodo del encabezado; personas. | 2008–2011 |
| `Cons` | entero | Consecutivo de la fila publicado en la hoja. | 2009–2011, 2016–2017 |
| `F.A. 1 Año Dosis Unica` | real | Dosis/aplicaciones publicadas para el biológico, edad y esquema del encabezado; conservar el valor original. | 2009–2014 |
| `%F.A.` | real | Cobertura/indicador publicado para el biológico y grupo del encabezado; verificar escala en cada hoja. | 2009–2011, 2015–2020 |
| `Rotavirus 2da Dosis` | real | Dosis/aplicaciones publicadas para el biológico, edad y esquema del encabezado; conservar el valor original. | 2009–2010 |
| `%ROTA` | real | Cobertura/indicador publicado para el biológico y grupo del encabezado; verificar escala en cada hoja. | 2009–2010 |
| `Neumococo 3ra Dosis   1er. Año` | real | Dosis/aplicaciones publicadas para el biológico, edad y esquema del encabezado; conservar el valor original. | 2009 |
| `Neumococo 2da Dosis     (12-23 meses)` | real | Dosis/aplicaciones publicadas para el biológico, edad y esquema del encabezado; conservar el valor original. | 2009 |
| `Neumococo Dosis Unica (24-35 meses)` | real | Dosis/aplicaciones publicadas para el biológico, edad y esquema del encabezado; conservar el valor original. | 2009 |
| `% B.C.G en R.N.` | real | Cobertura/indicador publicado para el biológico y grupo del encabezado; verificar escala en cada hoja. | 2010–2011 |
| `Neumo 2da (11 Meses 29 Dias)` | real | Dosis/aplicaciones publicadas para el biológico, edad y esquema del encabezado; conservar el valor original. | 2010 |
| `Neumo 3ra (12 Meses)` | real | Dosis/aplicaciones publicadas para el biológico, edad y esquema del encabezado; conservar el valor original. | 2010 |
| `Neumo 2da (12-23 meses)` | real | Dosis/aplicaciones publicadas para el biológico, edad y esquema del encabezado; conservar el valor original. | 2010 |
| `Neumo U. (24- 35 Meses)` | real | Dosis/aplicaciones publicadas para el biológico, edad y esquema del encabezado; conservar el valor original. | 2010 |
| `VOP Al año de la 3ra Dosis 1er. Ref.` | real | Dosis/aplicaciones publicadas para el biológico, edad y esquema del encabezado; conservar el valor original. | 2010 |
| `DPT Al año de la 3ra Dosis 1er. Ref.` | real | Dosis/aplicaciones publicadas para el biológico, edad y esquema del encabezado; conservar el valor original. | 2010 |
| `Poblaciòn de 5 años` | real | Población, meta o proyección publicada para el grupo y periodo del encabezado; personas. | 2010 |
| `VOP 5 AÑOS 2do. Ref.` | real | Dosis/aplicaciones publicadas para el biológico, edad y esquema del encabezado; conservar el valor original. | 2010–2022 |
| `DPT 2do. Ref. 5 AÑOS` | real | Dosis/aplicaciones publicadas para el biológico, edad y esquema del encabezado; conservar el valor original. | 2010, 2017–2025 |
| `TV`<br>`2do Ref. 5 Años` | real | Dosis/aplicaciones publicadas para el biológico, edad y esquema del encabezado; conservar el valor original. | 2010, 2017–2023 |
| `Polio < DE 1 AÑO 1a Dosis` | real | Dosis/aplicaciones publicadas para el biológico, edad y esquema del encabezado; conservar el valor original. | 2011–2014 |
| `% 1as Dosis de Polio` | real | Cobertura/indicador publicado para el biológico y grupo del encabezado; verificar escala en cada hoja. | 2011–2014 |
| `Polio < DE 1 AÑO 2a Dosis` | real | Dosis/aplicaciones publicadas para el biológico, edad y esquema del encabezado; conservar el valor original. | 2011–2014 |
| `% 2as Dosis de Polio` | real | Cobertura/indicador publicado para el biológico y grupo del encabezado; verificar escala en cada hoja. | 2011–2014 |
| `PENTA MENOR DE UN AÑO 1ras` | real | Dosis/aplicaciones publicadas para el biológico, edad y esquema del encabezado; conservar el valor original. | 2011–2025 |
| `% Pentavalente 1as. Dosis` | real | Cobertura/indicador publicado para el biológico y grupo del encabezado; verificar escala en cada hoja. | 2011–2014 |
| `PENTA MENOR DE UN AÑO 2das` | real | Dosis/aplicaciones publicadas para el biológico, edad y esquema del encabezado; conservar el valor original. | 2011–2025 |
| `% Pentavalente 2das. Dosis` | real | Cobertura/indicador publicado para el biológico y grupo del encabezado; verificar escala en cada hoja. | 2011–2014 |
| `ROTAVIRUS DE 2 A 7 MESES 29 DIAS 1ras` | real | Dosis/aplicaciones publicadas para el biológico, edad y esquema del encabezado; conservar el valor original. | 2011–2014 |
| `% Rota 1ras` | real | Cobertura/indicador publicado para el biológico y grupo del encabezado; verificar escala en cada hoja. | 2011–2025 |
| `ROTAVIRUS DE 2 A 7 MESES 29 DIAS 2das` | real | Dosis/aplicaciones publicadas para el biológico, edad y esquema del encabezado; conservar el valor original. | 2011–2014 |
| `% Rota  2das` | real | Cobertura/indicador publicado para el biológico y grupo del encabezado; verificar escala en cada hoja. | 2011–2025 |
| `FLU DE 6 A 11 MESES 2a Dosis` | real | Dosis/aplicaciones publicadas para el biológico, edad y esquema del encabezado; conservar el valor original. | 2011 |
| `% FLU de 6 a 11 Meses 2da` | real | Cobertura/indicador publicado para el biológico y grupo del encabezado; verificar escala en cada hoja. | 2011–2019 |
| `Neumo (11 Meses 29 Dias) 1ras` | real | Dosis/aplicaciones publicadas para el biológico, edad y esquema del encabezado; conservar el valor original. | 2011–2013 |
| `% Neumo`<br>`1ra dosis` | real | Cobertura/indicador publicado para el biológico y grupo del encabezado; verificar escala en cada hoja. | 2011–2025 |
| `Neumo (11 Meses 29 Dias) `<br>`2das` | real | Dosis/aplicaciones publicadas para el biológico, edad y esquema del encabezado; conservar el valor original. | 2011 |
| `% Neumo (11 Meses 29 Dias) `<br>`2da D` | real | Cobertura/indicador publicado para el biológico y grupo del encabezado; verificar escala en cada hoja. | 2011 |
| `Neumo de 12 Meses`<br>`3ra` | real | Dosis/aplicaciones publicadas para el biológico, edad y esquema del encabezado; conservar el valor original. | 2011–2013 |
| `% Neumo`<br>`3ra dosis` | real | Cobertura/indicador publicado para el biológico y grupo del encabezado; verificar escala en cada hoja. | 2011–2015 |
| `Neumo de 12-23 meses`<br>`1ras` | real | Dosis/aplicaciones publicadas para el biológico, edad y esquema del encabezado; conservar el valor original. | 2011–2013, 2015 |
| `Neumo de 12-23 meses`<br>`2das` | real | Dosis/aplicaciones publicadas para el biológico, edad y esquema del encabezado; conservar el valor original. | 2011–2013, 2015 |
| `Neumo de 24- 35 Meses`<br>`Unica` | real | Dosis/aplicaciones publicadas para el biológico, edad y esquema del encabezado; conservar el valor original. | 2011 |
| `VOP Al año de la 3ra Dosis `<br>`1er. Ref.` | real | Dosis/aplicaciones publicadas para el biológico, edad y esquema del encabezado; conservar el valor original. | 2011–2015 |
| `% VOP`<br>`1er Ref.` | real | Cobertura/indicador publicado para el biológico y grupo del encabezado; verificar escala en cada hoja. | 2011–2025 |
| `DPT Al año de la 3ra Dosis`<br>`1er. Ref.` | real | Dosis/aplicaciones publicadas para el biológico, edad y esquema del encabezado; conservar el valor original. | 2011–2015 |
| `% DPT`<br>`1er Ref.` | real | Cobertura/indicador publicado para el biológico y grupo del encabezado; verificar escala en cada hoja. | 2011–2020 |
| `Pob. 5 años 2011` | real | Población, meta o proyección publicada para el grupo y periodo del encabezado; personas. | 2011 |
| `% VOP`<br>`2do Ref. 5 Años` | real | Cobertura/indicador publicado para el biológico y grupo del encabezado; verificar escala en cada hoja. | 2011, 2015–2025 |
| `DPT 5 AÑOS`<br>`2do. Ref.` | real | Dosis/aplicaciones publicadas para el biológico, edad y esquema del encabezado; conservar el valor original. | 2011–2016 |
| `% DPT`<br>`2do Ref. 5 Años` | real | Cobertura/indicador publicado para el biológico y grupo del encabezado; verificar escala en cada hoja. | 2011–2016 |
| `SRP (T.V.) 5 AÑOS`<br>`Ref.` | real | Dosis/aplicaciones publicadas para el biológico, edad y esquema del encabezado; conservar el valor original. | 2011–2016 |
| `% TV`<br>`2do Ref. 5 Años` | real | Cobertura/indicador publicado para el biológico y grupo del encabezado; verificar escala en cada hoja. | 2011–2019 |
| `FLU de 50 Años y más`<br>`UNICA` | real | Dosis/aplicaciones publicadas para el biológico, edad y esquema del encabezado; conservar el valor original. | 2011–2012 |
| `Poblaciòn Menor de 1 año (Meta Programatica)` | real | Población, meta o proyección publicada para el grupo y periodo del encabezado; personas. | 2012–2018 |
| `% B.C.G (Tuberculosis) en Recién Nacidos`<br>`(NV Ajustada)` | real | Cobertura/indicador publicado para el biológico y grupo del encabezado; verificar escala en cada hoja. | 2012–2014 |
| `HB RECIEN NACIDO (HASTA 28 DÍAS)` | real | Dosis/aplicaciones publicadas para el biológico, edad y esquema del encabezado; conservar el valor original. | 2012–2015 |
| `% HB` | real | Cobertura/indicador publicado para el biológico y grupo del encabezado; verificar escala en cada hoja. | 2012–2020 |
| `FLU DE 6 A 11 MESES 2a` | real | Dosis/aplicaciones publicadas para el biológico, edad y esquema del encabezado; conservar el valor original. | 2012–2025 |
| `Poblaciòn de 1 año (Meta Programatica)` | real | Población, meta o proyección publicada para el grupo y periodo del encabezado; personas. | 2012, 2014–2015 |
| `% F.A.`<br>`(Meta Programat)` | real | Cobertura/indicador publicado para el biológico y grupo del encabezado; verificar escala en cada hoja. | 2012–2014 |
| `Neumo (11 Meses 29 Dias) 2das` | real | Dosis/aplicaciones publicadas para el biológico, edad y esquema del encabezado; conservar el valor original. | 2012–2013 |
| `% Neumo`<br>`2ra dosis` | real | Cobertura/indicador publicado para el biológico y grupo del encabezado; verificar escala en cada hoja. | 2012–2025 |
| `Neumo de 24- 47 Meses`<br>`Unica` | real | Dosis/aplicaciones publicadas para el biológico, edad y esquema del encabezado; conservar el valor original. | 2012–2013, 2015 |
| `Pob. 5 años Meta Programatica 2012` | real | Población, meta o proyección publicada para el grupo y periodo del encabezado; personas. | 2012 |
| `% VOP`<br>`2do Ref.`<br>`5 Años`<br>`(Meta Prog)` | real | Cobertura/indicador publicado para el biológico y grupo del encabezado; verificar escala en cada hoja. | 2012–2014 |
| `CENSO ET` | real | Población, meta o proyección publicada para el grupo y periodo del encabezado; personas. | 2012–2015 |
| `VPH 1a Dosis` | real | Dosis/aplicaciones publicadas para el biológico, edad y esquema del encabezado; conservar el valor original. | 2012–2015, 2017 |
| `% VPH 1as Dosis` | real | Cobertura/indicador publicado para el biológico y grupo del encabezado; verificar escala en cada hoja. | 2012–2015 |
| `VPH 2a Dosis` | real | Dosis/aplicaciones publicadas para el biológico, edad y esquema del encabezado; conservar el valor original. | 2012–2015, 2017–2018, 2020–2022 |
| `% VPH 2das Dosis` | real | Cobertura/indicador publicado para el biológico y grupo del encabezado; verificar escala en cada hoja. | 2012–2015 |
| `VPH 3a Dosis` | real | Dosis/aplicaciones publicadas para el biológico, edad y esquema del encabezado; conservar el valor original. | 2012–2015, 2017 |
| `% VPH 3as Dosis` | real | Cobertura/indicador publicado para el biológico y grupo del encabezado; verificar escala en cada hoja. | 2012 |
| `FLU DE 12 A 23 MESES 2a + UNICA` | real | Dosis/aplicaciones publicadas para el biológico, edad y esquema del encabezado; conservar el valor original. | 2013–2014, 2017–2025 |
| `% FLU de 12 a 23 Meses 2da` | real | Cobertura/indicador publicado para el biológico y grupo del encabezado; verificar escala en cada hoja. | 2013–2014, 2017–2025 |
| `Poblaciòn de `<br>`1 año (Meta Programatica)` | real | Población, meta o proyección publicada para el grupo y periodo del encabezado; personas. | 2013 |
| `HA`<br>`1 AÑO UNICA` | real | Dosis/aplicaciones publicadas para el biológico, edad y esquema del encabezado; conservar el valor original. | 2013–2025 |
| `% HA`<br>`1 AÑO UNICA` | real | Cobertura/indicador publicado para el biológico y grupo del encabezado; verificar escala en cada hoja. | 2013–2025 |
| `Pob. 5 años 2013 (Meta Programatica)` | real | Población, meta o proyección publicada para el grupo y periodo del encabezado; personas. | 2013–2014 |
| `FLU de 50 a 59 Años UNICA` | real | Dosis/aplicaciones publicadas para el biológico, edad y esquema del encabezado; conservar el valor original. | 2013–2014 |
| `FLU de 60 Años y más`<br>`UNICA` | real | Dosis/aplicaciones publicadas para el biológico, edad y esquema del encabezado; conservar el valor original. | 2013–2014 |
| `Gestantes a partir de la semana 14 ÚNICA` | real | Dosis/aplicaciones publicadas para el biológico, edad y esquema del encabezado; conservar el valor original. | 2013–2025 |
| `Neumo (De 2 Meses a 11 Meses 29 Dias) 1ras` | real | Dosis/aplicaciones publicadas para el biológico, edad y esquema del encabezado; conservar el valor original. | 2014 |
| `Neumo (De 2 Meses a 11 Meses 29 Dias) 2das` | real | Dosis/aplicaciones publicadas para el biológico, edad y esquema del encabezado; conservar el valor original. | 2014 |
| `Neumo de 12 Meses a 23 Meses`<br>`Ref.` | real | Dosis/aplicaciones publicadas para el biológico, edad y esquema del encabezado; conservar el valor original. | 2014 |
| `Neumo de 12 meses a 23 meses`<br>`1ras` | real | Dosis/aplicaciones publicadas para el biológico, edad y esquema del encabezado; conservar el valor original. | 2014, 2016–2025 |
| `Neumo de 12 meses a 23 meses`<br>`2das` | real | Dosis/aplicaciones publicadas para el biológico, edad y esquema del encabezado; conservar el valor original. | 2014, 2016–2025 |
| `Neumo de 24 meses a 47 Meses`<br>`Unica` | real | Dosis/aplicaciones publicadas para el biológico, edad y esquema del encabezado; conservar el valor original. | 2014, 2016–2024 |
| `ANTIPOLIO INACTIVADA (VIP) PARENTERAL`<br>`<  DE 1 AÑO`<br>`1a` | real | Dosis/aplicaciones publicadas para el biológico, edad y esquema del encabezado; conservar el valor original. | 2015–2025 |
| `% (VIP) PARENTERAL`<br>`<  DE 1 AÑO`<br>`1a` | real | Cobertura/indicador publicado para el biológico y grupo del encabezado; verificar escala en cada hoja. | 2015–2025 |
| `VOP <  DE 1 AÑO 2a` | real | Dosis/aplicaciones publicadas para el biológico, edad y esquema del encabezado; conservar el valor original. | 2015–2016 |
| `% VOP 2as` | real | Cobertura/indicador publicado para el biológico y grupo del encabezado; verificar escala en cada hoja. | 2015–2016 |
| `VOP <DE1 AÑO 3ras + VIP <1AÑO 3as` | real | Dosis/aplicaciones publicadas para el biológico, edad y esquema del encabezado; conservar el valor original. | 2015 |
| `% DPT 1ras` | real | Cobertura/indicador publicado para el biológico y grupo del encabezado; verificar escala en cada hoja. | 2015–2025 |
| `% DPT 2das` | real | Cobertura/indicador publicado para el biológico y grupo del encabezado; verificar escala en cada hoja. | 2015–2025 |
| `% 3ras. Dosis de Pentavalente` | real | Cobertura/indicador publicado para el biológico y grupo del encabezado; verificar escala en cada hoja. | 2015–2019 |
| `BCG RECIEN NACIDO (HASTA 28 DÍAS) + MENOR UN AÑO (29 DÍAS A 11 MESES 29 DIAS) Unica` | real | Dosis/aplicaciones publicadas para el biológico, edad y esquema del encabezado; conservar el valor original. | 2015 |
| `ROTAVIRUS DE 2 A 3 MESES 29 DIAS 1ras` | real | Dosis/aplicaciones publicadas para el biológico, edad y esquema del encabezado; conservar el valor original. | 2015 |
| `ROTAVIRUS DE 4 A 11 MESES 29 DIAS 2a` | real | Dosis/aplicaciones publicadas para el biológico, edad y esquema del encabezado; conservar el valor original. | 2015–2025 |
| `FLU DE 6 A 11 MESES 1a` | real | Dosis/aplicaciones publicadas para el biológico, edad y esquema del encabezado; conservar el valor original. | 2015–2025 |
| `% FLU de 6 a 11 Meses 1a` | real | Cobertura/indicador publicado para el biológico y grupo del encabezado; verificar escala en cada hoja. | 2015–2019 |
| `% de Triple Viral al Año de edad` | real | Cobertura/indicador publicado para el biológico y grupo del encabezado; verificar escala en cada hoja. | 2015–2019 |
| `Poblaciòn de 1 año (Meta varicela media cohorte)` | real | Población, meta o proyección publicada para el grupo y periodo del encabezado; personas. | 2015 |
| `VARICELA DE 1 AÑO`<br>`1a` | real | Dosis/aplicaciones publicadas para el biológico, edad y esquema del encabezado; conservar el valor original. | 2015 |
| `% VARICELA DE 1 AÑO - Cump AGOSTO` | real | Cobertura/indicador publicado para el biológico y grupo del encabezado; verificar escala en cada hoja. | 2015 |
| `F.A. 1 AÑO`<br>`Dosis Unica` | real | Dosis/aplicaciones publicadas para el biológico, edad y esquema del encabezado; conservar el valor original. | 2015 |
| `Neumo (2 a 11 Meses 29 Dias) 1ras` | real | Dosis/aplicaciones publicadas para el biológico, edad y esquema del encabezado; conservar el valor original. | 2015 |
| `Neumo (2 a 11 Meses 29 Dias) 2das` | real | Dosis/aplicaciones publicadas para el biológico, edad y esquema del encabezado; conservar el valor original. | 2015 |
| `Neumo de (12 a 23 meses)`<br>`REF.` | real | Dosis/aplicaciones publicadas para el biológico, edad y esquema del encabezado; conservar el valor original. | 2015 |
| `Pob. 5 años 2013 (Meta Programatica) - Preliminar` | real | Población, meta o proyección publicada para el grupo y periodo del encabezado; personas. | 2015 |
| `FLU DE 18 A 49 AÑOS UNICA` | real | Dosis/aplicaciones publicadas para el biológico, edad y esquema del encabezado; conservar el valor original. | 2015 |
| `FLU DE 50 AÑOS Y MAS `<br>`U.` | real | Dosis/aplicaciones publicadas para el biológico, edad y esquema del encabezado; conservar el valor original. | 2015 |
| `ANTIPOLIO INACTIVADA (VIP) PARENTERAL`<br>`<  DE 1 AÑO`<br>`2a` | real | Dosis/aplicaciones publicadas para el biológico, edad y esquema del encabezado; conservar el valor original. | 2016 |
| `% (VIP) PARENTERAL`<br>`<  DE 1 AÑO`<br>`2a` | real | Cobertura/indicador publicado para el biológico y grupo del encabezado; verificar escala en cada hoja. | 2016 |
| `ANTIPOLIO INACTIVADA (VIP) PARENTERAL`<br>`<  DE 1 AÑO`<br>`3a` | real | Dosis/aplicaciones publicadas para el biológico, edad y esquema del encabezado; conservar el valor original. | 2016 |
| `% (VIP) PARENTERAL`<br>`<  DE 1 AÑO`<br>`3a` | real | Cobertura/indicador publicado para el biológico y grupo del encabezado; verificar escala en cada hoja. | 2016 |
| `VOP < DE1 AÑO 3ras + VIP <1AÑO 3as` | real | Dosis/aplicaciones publicadas para el biológico, edad y esquema del encabezado; conservar el valor original. | 2016 |
| `BCG RECIEN NACIDO (DE 0 HASTA 29 DÍAS) + MENOR UN AÑO (A PARTIR DE 1 MES HASTA 11 MESES 29 DIAS) Unica` | real | Dosis/aplicaciones publicadas para el biológico, edad y esquema del encabezado; conservar el valor original. | 2016–2025 |
| `HB RECIEN NACIDO (HASTA 29 DÍAS)` | real | Dosis/aplicaciones publicadas para el biológico, edad y esquema del encabezado; conservar el valor original. | 2016 |
| `ROTAVIRUS DE 2 A 3 MESES 21 DIAS 1ras` | real | Dosis/aplicaciones publicadas para el biológico, edad y esquema del encabezado; conservar el valor original. | 2016–2023 |
| `Neumo (2 a 11 Meses 29 Dias)  1as Dosis` | real | Dosis/aplicaciones publicadas para el biológico, edad y esquema del encabezado; conservar el valor original. | 2016–2025 |
| `Neumo (2 a 11 Meses 29 Dias)  2as Dosis` | real | Dosis/aplicaciones publicadas para el biológico, edad y esquema del encabezado; conservar el valor original. | 2016–2025 |
| `Poblaciòn de 1 año Meta Programática)` | real | Población, meta o proyección publicada para el grupo y periodo del encabezado; personas. | 2016–2019 |
| `VARICELA DE 1 AÑO`<br>`D. Unica` | real | Dosis/aplicaciones publicadas para el biológico, edad y esquema del encabezado; conservar el valor original. | 2016–2025 |
| `% VARICELA DE 1 AÑO` | real | Cobertura/indicador publicado para el biológico y grupo del encabezado; verificar escala en cada hoja. | 2016–2025 |
| `Neumo de 12 Meses a 23 Meses`<br>`REF.` | real | Dosis/aplicaciones publicadas para el biológico, edad y esquema del encabezado; conservar el valor original. | 2016–2025 |
| `% Neumo 12 a 23 Meses`<br>`REF.`<br>`3ra dosis` | real | Cobertura/indicador publicado para el biológico y grupo del encabezado; verificar escala en cada hoja. | 2016–2025 |
| `F.A. 1 AÑO (18 Meses de Edad)`<br>`Dosis Unica` | real | Dosis/aplicaciones publicadas para el biológico, edad y esquema del encabezado; conservar el valor original. | 2016–2024 |
| `VOP Al año de la 3ra Dosis (De 18 a 23 meses)`<br>`1er. Ref.` | real | Dosis/aplicaciones publicadas para el biológico, edad y esquema del encabezado; conservar el valor original. | 2016–2022 |
| `DPT Al año de la 3ra Dosis (De 18 a 23 meses)`<br>`1er. Ref.` | real | Dosis/aplicaciones publicadas para el biológico, edad y esquema del encabezado; conservar el valor original. | 2016–2018, 2020–2022 |
| `Pob. 5 años  (Meta Programatica)` | real | Población, meta o proyección publicada para el grupo y periodo del encabezado; personas. | 2016–2019 |
| `FLU de 19 a 49 años ÚNICA` | real | Dosis/aplicaciones publicadas para el biológico, edad y esquema del encabezado; conservar el valor original. | 2016–2018 |
| `FLU de 50 años y más ÚNICA` | real | Dosis/aplicaciones publicadas para el biológico, edad y esquema del encabezado; conservar el valor original. | 2016–2018 |
| `TdaP ACELULAR GESTANTES DE 10 AÑOS Y MAS * UNICA DOSIS EN CADA EMBARAZO` | real | Dosis/aplicaciones publicadas para el biológico, edad y esquema del encabezado; conservar el valor original. | 2016 |
| `%` | real | Cobertura/indicador publicado para el biológico y grupo del encabezado; verificar escala en cada hoja. | 2016–2022, 2025 |
| `POB. META TOTAL` | real | Población, meta o proyección publicada para el grupo y periodo del encabezado; personas. | 2016 |
| `VPH Niñas de 9 años 1a Dosis` | real | Dosis/aplicaciones publicadas para el biológico, edad y esquema del encabezado; conservar el valor original. | 2016, 2018–2022 |
| `% VPH niñas de 9 años`<br>`1as Dosis` | real | Cobertura/indicador publicado para el biológico y grupo del encabezado; verificar escala en cada hoja. | 2016 |
| `VPH Niñas de 9 años 2a Dosis` | real | Dosis/aplicaciones publicadas para el biológico, edad y esquema del encabezado; conservar el valor original. | 2016 |
| `% VPH niñas de 9 años`<br>`2as Dosis` | real | Cobertura/indicador publicado para el biológico y grupo del encabezado; verificar escala en cada hoja. | 2016 |
| `HEPATITIS B RECIEN NACIDO (HASTA 29 DÍAS) (Primeras 12 Horas)` | real | Dosis/aplicaciones publicadas para el biológico, edad y esquema del encabezado; conservar el valor original. | 2017–2024 |
| `% HB RN (HASTA 29 DÍAS) (Primeras 12 Horas)` | real | Cobertura/indicador publicado para el biológico y grupo del encabezado; verificar escala en cada hoja. | 2017–2025 |
| `HEPATITIS B RECIEN NACIDO (HASTA 29 DÍAS) Despues de las primeras 12 horas ` | real | Dosis/aplicaciones publicadas para el biológico, edad y esquema del encabezado; conservar el valor original. | 2017–2025 |
| `% HB RN (HASTA 29 DÍAS) (Despues de las primeras 12 Horas)` | real | Cobertura/indicador publicado para el biológico y grupo del encabezado; verificar escala en cada hoja. | 2017–2025 |
| `HB RECIEN NACIDO (HASTA 29 DÍAS) (Primeras 12 Horas)+ Despues de las primeras 12 horas` | real | Dosis/aplicaciones publicadas para el biológico, edad y esquema del encabezado; conservar el valor original. | 2017–2025 |
| `Polio <  DE 1 AÑO 2a` | real | Dosis/aplicaciones publicadas para el biológico, edad y esquema del encabezado; conservar el valor original. | 2017–2018 |
| `% Dosis de Polio 2as` | real | Cobertura/indicador publicado para el biológico y grupo del encabezado; verificar escala en cada hoja. | 2017–2018 |
| `Polio < DE1 AÑO 3ras + VIP <1AÑO 3as` | real | Dosis/aplicaciones publicadas para el biológico, edad y esquema del encabezado; conservar el valor original. | 2017–2019 |
| `% DPT 5 AÑOS` | real | Cobertura/indicador publicado para el biológico y grupo del encabezado; verificar escala en cada hoja. | 2017–2020 |
| `TdaP ACELULAR DE 10 AÑOS Y MAS * GESTANTES UNICA DOSIS EN CADA EMBARAZO` | real | Dosis/aplicaciones publicadas para el biológico, edad y esquema del encabezado; conservar el valor original. | 2017–2025 |
| `Pob. Niñas de 9 años  (Dane)` | real | Población, meta o proyección publicada para el grupo y periodo del encabezado; personas. | 2017 |
| `% V.  P.  H. DE 9 AÑOS 1a` | real | Cobertura/indicador publicado para el biológico y grupo del encabezado; verificar escala en cada hoja. | 2017 |
| `% V.  P.  H. DE 9 AÑOS 2a` | real | Cobertura/indicador publicado para el biológico y grupo del encabezado; verificar escala en cada hoja. | 2017 |
| `Fronterizos` | texto/categoría | Clasificación territorial auxiliar original; no se homologa su catálogo en el procesamiento. | 2017–2022, 2024–2025 |
| `Mpios Front Venez` | texto/categoría | Clasificación territorial auxiliar original; no se homologa su catálogo en el procesamiento. | 2017–2022 |
| `Pob. VPH Niñas de 9 años` | real | Población, meta o proyección publicada para el grupo y periodo del encabezado; personas. | 2018–2019 |
| `% VPH Niñas de 9 años 1as Dosis` | real | Cobertura/indicador publicado para el biológico y grupo del encabezado; verificar escala en cada hoja. | 2018–2024 |
| `% VPH Niñas de 9 años 2as Dosis` | real | Cobertura/indicador publicado para el biológico y grupo del encabezado; verificar escala en cada hoja. | 2018–2022 |
| `Población Menor de 1 año (Meta Programatica)` | real | Población, meta o proyección publicada para el grupo y periodo del encabezado; personas. | 2019 |
| `(VIP) PARENTERAL`<br>`< 1 AÑO`<br>`2a` | real | Dosis/aplicaciones publicadas para el biológico, edad y esquema del encabezado; conservar el valor original. | 2019–2025 |
| `% (VIP) `<br>`< 1 AÑO`<br>`2a` | real | Cobertura/indicador publicado para el biológico y grupo del encabezado; verificar escala en cada hoja. | 2019–2025 |
| `DPT 1er REF. al año de la 3ra Dosis` | real | Dosis/aplicaciones publicadas para el biológico, edad y esquema del encabezado; conservar el valor original. | 2019 |
| `VARICELA DE 5 AÑOS` | real | Dosis/aplicaciones publicadas para el biológico, edad y esquema del encabezado; conservar el valor original. | 2019 |
| `% VARICELA` | real | Cobertura/indicador publicado para el biológico y grupo del encabezado; verificar escala en cada hoja. | 2019–2025 |
| `FLU DE 18 A 40 AÑOS UNICA` | real | Dosis/aplicaciones publicadas para el biológico, edad y esquema del encabezado; conservar el valor original. | 2019–2022 |
| `FLU DE 41 A 59 AÑOS UNICA` | real | Dosis/aplicaciones publicadas para el biológico, edad y esquema del encabezado; conservar el valor original. | 2019–2022 |
| `Poblacion de 60 y mas años (30% Dane)` | real | Población, meta o proyección publicada para el grupo y periodo del encabezado; personas. | 2019 |
| `FLU DE 60 AÑOS Y MAS `<br>`U.` | real | Dosis/aplicaciones publicadas para el biológico, edad y esquema del encabezado; conservar el valor original. | 2019–2025 |
| `VPH Niñas 9 años 2a Dosis` | real | Dosis/aplicaciones publicadas para el biológico, edad y esquema del encabezado; conservar el valor original. | 2019, 2023 |
| `Zonas Futuro` | texto/categoría | Clasificación territorial auxiliar original; no se homologa su catálogo en el procesamiento. | 2019 |
| `DEPTOS` | texto | Nombre o agrupación territorial publicada. | 2019 |
| `Poblaciòn Menor de 1 año (Meta Programática 2020)` | real | Población, meta o proyección publicada para el grupo y periodo del encabezado; personas. | 2020 |
| `% 3ras. Dosis de Pentavalente Menores de 1 año` | real | Cobertura/indicador publicado para el biológico y grupo del encabezado; verificar escala en cada hoja. | 2020 |
| `Aport poblacional` | real | Población, meta o proyección publicada para el grupo y periodo del encabezado; personas. | 2020–2025 |
| `% FLU de 6 a 11 Meses 1a *` | real | Cobertura/indicador publicado para el biológico y grupo del encabezado; verificar escala en cada hoja. | 2020–2025 |
| `% FLU de 6 a 11 Meses 2da *` | real | Cobertura/indicador publicado para el biológico y grupo del encabezado; verificar escala en cada hoja. | 2020–2025 |
| `Poblaciòn de 1 año (Meta Programática 2020)` | real | Población, meta o proyección publicada para el grupo y periodo del encabezado; personas. | 2020 |
| `% de SRP (Triple Viral) al Año de edad` | real | Cobertura/indicador publicado para el biológico y grupo del encabezado; verificar escala en cada hoja. | 2020 |
| `Pob. 5 años  (Meta Programática 2020)` | real | Población, meta o proyección publicada para el grupo y periodo del encabezado; personas. | 2020 |
| `% SRP (Triple Viral) `<br>`Ref. 5 años` | real | Cobertura/indicador publicado para el biológico y grupo del encabezado; verificar escala en cada hoja. | 2020–2023 |
| `VARICELA DE 5 AÑOS Ref.` | real | Dosis/aplicaciones publicadas para el biológico, edad y esquema del encabezado; conservar el valor original. | 2020–2025 |
| `Poblacion de 60 y mas años (30% Censo Dane2018)` | real | Población, meta o proyección publicada para el grupo y periodo del encabezado; personas. | 2020–2022 |
| `% FLU DE 60 AÑOS Y MAS` | real | Cobertura/indicador publicado para el biológico y grupo del encabezado; verificar escala en cada hoja. | 2020–2025 |
| `% Gestantes ` | real | Cobertura/indicador publicado para el biológico y grupo del encabezado; verificar escala en cada hoja. | 2020–2023 |
| `Pob. VPH Niñas de 9 años (Censo DANE 2018)` | real | Población, meta o proyección publicada para el grupo y periodo del encabezado; personas. | 2020–2023 |
| `Mpios PEDT` | texto/categoría | Clasificación territorial auxiliar original; no se homologa su catálogo en el procesamiento. | 2020–2022, 2024–2025 |
| `Poblaciòn Menor de 1 año (Meta Programática 2021)` | real | Población, meta o proyección publicada para el grupo y periodo del encabezado; personas. | 2021 |
| `% HB RECIEN NACIDO (HASTA 29 DÍAS)` | real | Cobertura/indicador publicado para el biológico y grupo del encabezado; verificar escala en cada hoja. | 2021–2025 |
| `(VIP) PARENTERAL`<br>`< 1 AÑO`<br>`3a` | real | Dosis/aplicaciones publicadas para el biológico, edad y esquema del encabezado; conservar el valor original. | 2021–2025 |
| `% (VIP) `<br>`< 1 AÑO`<br>`3a` | real | Cobertura/indicador publicado para el biológico y grupo del encabezado; verificar escala en cada hoja. | 2021–2025 |
| `% Pentavalente Menor de 1 año`<br>`3ras. Dosis de ` | real | Cobertura/indicador publicado para el biológico y grupo del encabezado; verificar escala en cada hoja. | 2021, 2023–2024 |
| `Poblaciòn de 1 año (Meta Programática 2021)` | real | Población, meta o proyección publicada para el grupo y periodo del encabezado; personas. | 2021 |
| `% SRP (Triple Viral) `<br>`al Año de edad` | real | Cobertura/indicador publicado para el biológico y grupo del encabezado; verificar escala en cada hoja. | 2021–2025 |
| `% F.A. 1 AÑO`<br>`Dosis Unica` | real | Cobertura/indicador publicado para el biológico y grupo del encabezado; verificar escala en cada hoja. | 2021–2024 |
| `% Al año de la 3ra Dosis `<br>`1er Ref.` | real | Cobertura/indicador publicado para el biológico y grupo del encabezado; verificar escala en cada hoja. | 2021–2022 |
| `Pob. 5 años  (Meta Programática 2021)` | real | Población, meta o proyección publicada para el grupo y periodo del encabezado; personas. | 2021 |
| `% DPT`<br>`5 Años `<br>`2do Ref.` | real | Cobertura/indicador publicado para el biológico y grupo del encabezado; verificar escala en cada hoja. | 2021–2025 |
| `capital` | texto/categoría | Clasificación territorial auxiliar original; no se homologa su catálogo en el procesamiento. | 2021–2022, 2024–2025 |
| `Poblaciòn Menor de 1 año (Meta Programática 2022)` | real | Población, meta o proyección publicada para el grupo y periodo del encabezado; personas. | 2022 |
| `% Pentavalente Menor de 1 año`<br>`3ras. Dosis` | real | Cobertura/indicador publicado para el biológico y grupo del encabezado; verificar escala en cada hoja. | 2022, 2025 |
| `Poblaciòn de 1 año (Meta Programática 2022)` | real | Población, meta o proyección publicada para el grupo y periodo del encabezado; personas. | 2022 |
| `Pob. 5 años  (Meta Programática 2022)` | real | Población, meta o proyección publicada para el grupo y periodo del encabezado; personas. | 2022 |
| `POB. < 1 AÑO`<br>`META PROGRAM 2023` | real | Población, meta o proyección publicada para el grupo y periodo del encabezado; personas. | 2023 |
| `BCG RECIEN NACIDO (DE 0 HASTA 29 DÍAS) ` | real | Dosis/aplicaciones publicadas para el biológico, edad y esquema del encabezado; conservar el valor original. | 2023–2025 |
| `POB. 1 año`<br>`META PROGRAM 2023` | real | Población, meta o proyección publicada para el grupo y periodo del encabezado; personas. | 2023 |
| `SRP (TRIPLE VIRAL) REFUERZO DE 18 MESES` | real | Dosis/aplicaciones publicadas para el biológico, edad y esquema del encabezado; conservar el valor original. | 2023–2025 |
| `% SRP (TRIPLE VIRAL) REFUERZO DE 18 MESES` | real | Cobertura/indicador publicado para el biológico y grupo del encabezado; verificar escala en cada hoja. | 2023–2025 |
| `ANTIPOLIO INACTIVADA (VIP)   AL AÑO DE LA 3ra DOSIS (De 18 a 23 meses) 1er REF.` | real | Dosis/aplicaciones publicadas para el biológico, edad y esquema del encabezado; conservar el valor original. | 2023–2025 |
| `Pentavalente Al año de la 3ra Dosis (De 18 a 23 meses)`<br>`1er. Ref.` | real | Dosis/aplicaciones publicadas para el biológico, edad y esquema del encabezado; conservar el valor original. | 2023–2025 |
| `% Pentavalente Al año de la 3ra Dosis `<br>`1er Ref.` | real | Cobertura/indicador publicado para el biológico y grupo del encabezado; verificar escala en cada hoja. | 2023–2025 |
| `POB. 5 Años`<br>`META PROGRAM 2023` | real | Población, meta o proyección publicada para el grupo y periodo del encabezado; personas. | 2023 |
| `ANTIPOLIO INACTIVADA (VIP) `<br>`5 AÑOS `<br>`2° REF.` | real | Dosis/aplicaciones publicadas para el biológico, edad y esquema del encabezado; conservar el valor original. | 2023–2025 |
| `FLU de 9 a 17 años ` | real | Dosis/aplicaciones publicadas para el biológico, edad y esquema del encabezado; conservar el valor original. | 2023–2025 |
| `FLU de 18 a 59 años ` | real | Dosis/aplicaciones publicadas para el biológico, edad y esquema del encabezado; conservar el valor original. | 2023–2025 |
| `Poblacion de 60 y mas años 2023 `<br>`(30% Censo Dane2018)` | real | Población, meta o proyección publicada para el grupo y periodo del encabezado; personas. | 2023–2025 |
| `% TdaP Acelular Gestantes` | real | Cobertura/indicador publicado para el biológico y grupo del encabezado; verificar escala en cada hoja. | 2023 |
| `VPH Niñas 9 años 1a Dosis` | real | Dosis/aplicaciones publicadas para el biológico, edad y esquema del encabezado; conservar el valor original. | 2023, 2025 |
| `Pob. VPH Niños de 9 años (Censo DANE 2018) Meta meses Octubre a Diciembre` | real | Población, meta o proyección publicada para el grupo y periodo del encabezado; personas. | 2023 |
| `VPH Niños 9 años 1a Dosis` | real | Dosis/aplicaciones publicadas para el biológico, edad y esquema del encabezado; conservar el valor original. | 2023, 2025 |
| `% VPH Niños de 9 años 1as Dosis` | real | Cobertura/indicador publicado para el biológico y grupo del encabezado; verificar escala en cada hoja. | 2023–2024 |
| `POB. < 1 AÑO`<br>`META PROGRAMATICA`<br>`2024 (Aj2_20241028)` | real | Población, meta o proyección publicada para el grupo y periodo del encabezado; personas. | 2024 |
| `%B.C.G (Tuberculosis) en Recién Nacidos` | real | Cobertura/indicador publicado para el biológico y grupo del encabezado; verificar escala en cada hoja. | 2024–2025 |
| `ROTAVIRUS DE 2 A 3 MESES 29 DIAS 1a` | real | Dosis/aplicaciones publicadas para el biológico, edad y esquema del encabezado; conservar el valor original. | 2024–2025 |
| `POB. 1 año`<br>`META PROGRAMATICA`<br>`2024 (Aj2_20241028)` | real | Población, meta o proyección publicada para el grupo y periodo del encabezado; personas. | 2024 |
| `Aporte poblacional` | real | Población, meta o proyección publicada para el grupo y periodo del encabezado; personas. | 2024–2025 |
| `POB. 5 Años`<br>`META PROGRAMATICA 2024 (Aj2_20241028)` | real | Población, meta o proyección publicada para el grupo y periodo del encabezado; personas. | 2024 |
| `Aporte poblacional por ET a los 5 años de edad` | real | Población, meta o proyección publicada para el grupo y periodo del encabezado; personas. | 2024–2025 |
| `% Influenza Gestantes ` | real | Cobertura/indicador publicado para el biológico y grupo del encabezado; verificar escala en cada hoja. | 2024–2025 |
| `% TdaP ACELULAR DE 10 AÑOS Y MAS * GESTANTES` | real | Cobertura/indicador publicado para el biológico y grupo del encabezado; verificar escala en cada hoja. | 2024–2025 |
| `VPH 9 AÑOS PROYECCIONES DANE 2024` | real | Población, meta o proyección publicada para el grupo y periodo del encabezado; personas. | 2024 |
| `VPH Niñas `<br>`9 años `<br>`1a Dosis` | real | Dosis/aplicaciones publicadas para el biológico, edad y esquema del encabezado; conservar el valor original. | 2024 |
| `Pob. VPH Niños de 9 años (Censo DANE 2018)` | real | Población, meta o proyección publicada para el grupo y periodo del encabezado; personas. | 2024 |
| `VPH Niños `<br>`9 años `<br>`1a Dosis` | real | Dosis/aplicaciones publicadas para el biológico, edad y esquema del encabezado; conservar el valor original. | 2024 |
| `Pob. VPH Niños de 10 años (Censo DANE 2018)` | real | Población, meta o proyección publicada para el grupo y periodo del encabezado; personas. | 2024 |
| `VPH Niños `<br>`10 años `<br>`Dosis 1` | real | Dosis/aplicaciones publicadas para el biológico, edad y esquema del encabezado; conservar el valor original. | 2024 |
| `% VPH Niños de 10 años Dosis 1` | real | Cobertura/indicador publicado para el biológico y grupo del encabezado; verificar escala en cada hoja. | 2024 |
| `Pob. VPH Niños de 11 años (Censo DANE 2018)` | real | Población, meta o proyección publicada para el grupo y periodo del encabezado; personas. | 2024 |
| `VPH Niños `<br>`11 años `<br>`Dosis 1` | real | Dosis/aplicaciones publicadas para el biológico, edad y esquema del encabezado; conservar el valor original. | 2024 |
| `% VPH Niños de 11 años Dosis 1` | real | Cobertura/indicador publicado para el biológico y grupo del encabezado; verificar escala en cada hoja. | 2024 |
| `Pob. VPH Niños de 12 años (Censo DANE 2018)` | real | Población, meta o proyección publicada para el grupo y periodo del encabezado; personas. | 2024 |
| `VPH Niños `<br>`12 años `<br>`Dosis 1` | real | Dosis/aplicaciones publicadas para el biológico, edad y esquema del encabezado; conservar el valor original. | 2024 |
| `% VPH Niños de 12 años Dosis 1` | real | Cobertura/indicador publicado para el biológico y grupo del encabezado; verificar escala en cada hoja. | 2024 |
| `Pob. VPH Niños de 13 años (Censo DANE 2018)` | real | Población, meta o proyección publicada para el grupo y periodo del encabezado; personas. | 2024 |
| `VPH Niños `<br>`13 años `<br>`Dosis 1` | real | Dosis/aplicaciones publicadas para el biológico, edad y esquema del encabezado; conservar el valor original. | 2024 |
| `% VPH Niños de 13 años Dosis 1` | real | Cobertura/indicador publicado para el biológico y grupo del encabezado; verificar escala en cada hoja. | 2024 |
| `Pob. VPH Niños de 14 años (Censo DANE 2018)` | real | Población, meta o proyección publicada para el grupo y periodo del encabezado; personas. | 2024 |
| `VPH Niños `<br>`14 años `<br>`Dosis 1` | real | Dosis/aplicaciones publicadas para el biológico, edad y esquema del encabezado; conservar el valor original. | 2024 |
| `% VPH Niños de 14 años Dosis 1` | real | Cobertura/indicador publicado para el biológico y grupo del encabezado; verificar escala en cada hoja. | 2024 |
| `Pob. VPH Niños de 15 años (Censo DANE 2018)` | real | Población, meta o proyección publicada para el grupo y periodo del encabezado; personas. | 2024 |
| `VPH Niños 15 años Dosis 1` | real | Dosis/aplicaciones publicadas para el biológico, edad y esquema del encabezado; conservar el valor original. | 2024–2025 |
| `% VPH Niños de 15 años Dosis 1` | real | Cobertura/indicador publicado para el biológico y grupo del encabezado; verificar escala en cada hoja. | 2024 |
| `Pob. VPH Niños de 16 años (Censo DANE 2018)` | real | Población, meta o proyección publicada para el grupo y periodo del encabezado; personas. | 2024 |
| `VPH Niños 16 años Dosis 1` | real | Dosis/aplicaciones publicadas para el biológico, edad y esquema del encabezado; conservar el valor original. | 2024–2025 |
| `% VPH Niños de 16 años Dosis 1` | real | Cobertura/indicador publicado para el biológico y grupo del encabezado; verificar escala en cada hoja. | 2024 |
| `Pob. VPH Niños de 17 años (Censo DANE 2018)` | real | Población, meta o proyección publicada para el grupo y periodo del encabezado; personas. | 2024 |
| `VPH Niños 17 años Dosis 1` | real | Dosis/aplicaciones publicadas para el biológico, edad y esquema del encabezado; conservar el valor original. | 2024–2025 |
| `% VPH Niños de 17 años Dosis 1` | real | Cobertura/indicador publicado para el biológico y grupo del encabezado; verificar escala en cada hoja. | 2024 |
| `Anexo 1 Mpios de Alto Riesto FA` | texto/categoría | Clasificación territorial auxiliar original; no se homologa su catálogo en el procesamiento. | 2024 |
| `Mpios Front` | texto/categoría | Clasificación territorial auxiliar original; no se homologa su catálogo en el procesamiento. | 2024–2025 |
| `Municipios Priorizados (400)` | texto/categoría | Clasificación territorial auxiliar original; no se homologa su catálogo en el procesamiento. | 2024 |
| `Mpios riesgo Volcan NR` | texto/categoría | Clasificación territorial auxiliar original; no se homologa su catálogo en el procesamiento. | 2024–2025 |
| `POB. Recien Nacidos`<br>`META PROGRAMATICA`<br>`2025 (20251130)VerF` | real | Población, meta o proyección publicada para el grupo y periodo del encabezado; personas. | 2025 |
| `HEPATITIS B RECIEN NACIDO (Primeras 12 Horas)` | real | Dosis/aplicaciones publicadas para el biológico, edad y esquema del encabezado; conservar el valor original. | 2025 |
| `POB. < 1 AÑO`<br>`META PROGRAMATICA`<br>`2025 (20251130)VerF` | real | Población, meta o proyección publicada para el grupo y periodo del encabezado; personas. | 2025 |
| `IDEAL VACUNADOS A DICIIEMBRE` | real | Meta publicada de vacunados a diciembre. | 2025 |
| `DIFERENCIA No DOSIS` | real | Diferencia publicada de dosis; conservar signo y faltantes. | 2025 |
| `POB. 1 año`<br>`META PROGRAMATICA`<br>`2025 (20251130)VerF` | real | Población, meta o proyección publicada para el grupo y periodo del encabezado; personas. | 2025 |
| `IDEAL VACUNADOS DICIEMBRE` | real | Meta publicada de vacunados a diciembre. | 2025 |
| `DIFERENCIA No  DOSIS` | real | Diferencia publicada de dosis; conservar signo y faltantes. | 2025 |
| `Neumo de 24 meses a 71 Meses`<br>`Unica` | real | Dosis/aplicaciones publicadas para el biológico, edad y esquema del encabezado; conservar el valor original. | 2025 |
| `POB. Susceptibles`<br>`01/01/2025`<br>` 9m_23m` | real | Población, meta o proyección publicada para el grupo y periodo del encabezado; personas. | 2025 |
| `F.A. 9 Meses a 1 AÑO (18 Meses de Edad)`<br>`Dosis Unica` | real | Dosis/aplicaciones publicadas para el biológico, edad y esquema del encabezado; conservar el valor original. | 2025 |
| `% F.A. 9 meses a 1 AÑO`<br>`Dosis Unica` | real | Cobertura/indicador publicado para el biológico y grupo del encabezado; verificar escala en cada hoja. | 2025 |
| `POB. 5 Años`<br>`META PROGRAMATICA 2025 (20251130)VerF` | real | Población, meta o proyección publicada para el grupo y periodo del encabezado; personas. | 2025 |
| `Meta_Niñas 9 Años Ajustef_20251130` | real | Población, meta o proyección publicada para el grupo y periodo del encabezado; personas. | 2025 |
| `% Niñas VPH 9 años` | real | Cobertura/indicador publicado para el biológico y grupo del encabezado; verificar escala en cada hoja. | 2025 |
| `Meta Niños _9_años Ajustef_20251130` | real | Población, meta o proyección publicada para el grupo y periodo del encabezado; personas. | 2025 |
| `% Niños de 9 años` | real | Cobertura/indicador publicado para el biológico y grupo del encabezado; verificar escala en cada hoja. | 2025 |
| `Meta Niños _10_años Ajustef_20251130` | real | Población, meta o proyección publicada para el grupo y periodo del encabezado; personas. | 2025 |
| `VPH Niños 10 años Dosis 1` | real | Dosis/aplicaciones publicadas para el biológico, edad y esquema del encabezado; conservar el valor original. | 2025 |
| `% Niños de 10 años` | real | Cobertura/indicador publicado para el biológico y grupo del encabezado; verificar escala en cada hoja. | 2025 |
| `Meta Niños _11_años Ajustef_20251130` | real | Población, meta o proyección publicada para el grupo y periodo del encabezado; personas. | 2025 |
| `VPH Niños 11 años Dosis 1` | real | Dosis/aplicaciones publicadas para el biológico, edad y esquema del encabezado; conservar el valor original. | 2025 |
| `% Niños de 11 años` | real | Cobertura/indicador publicado para el biológico y grupo del encabezado; verificar escala en cada hoja. | 2025 |
| `Meta Niños _12_años Ajustef_20251130` | real | Población, meta o proyección publicada para el grupo y periodo del encabezado; personas. | 2025 |
| `VPH Niños 12 años Dosis 1` | real | Dosis/aplicaciones publicadas para el biológico, edad y esquema del encabezado; conservar el valor original. | 2025 |
| `% Niños de 12 años` | real | Cobertura/indicador publicado para el biológico y grupo del encabezado; verificar escala en cada hoja. | 2025 |
| `Meta Niños _13_años Ajustef_20251130` | real | Población, meta o proyección publicada para el grupo y periodo del encabezado; personas. | 2025 |
| `VPH Niños 13 años Dosis 1` | real | Dosis/aplicaciones publicadas para el biológico, edad y esquema del encabezado; conservar el valor original. | 2025 |
| `% Niños de 13 años` | real | Cobertura/indicador publicado para el biológico y grupo del encabezado; verificar escala en cada hoja. | 2025 |
| `Meta Niños _14_años Ajustef_20251130` | real | Población, meta o proyección publicada para el grupo y periodo del encabezado; personas. | 2025 |
| `VPH Niños 14 años Dosis 1` | real | Dosis/aplicaciones publicadas para el biológico, edad y esquema del encabezado; conservar el valor original. | 2025 |
| `% Niños de 14 años` | real | Cobertura/indicador publicado para el biológico y grupo del encabezado; verificar escala en cada hoja. | 2025 |
| `Meta Niños _15_años Ajustef_20251130` | real | Población, meta o proyección publicada para el grupo y periodo del encabezado; personas. | 2025 |
| `% Niños de 15 años` | real | Cobertura/indicador publicado para el biológico y grupo del encabezado; verificar escala en cada hoja. | 2025 |
| `Meta Niños _16_años Ajustef_20251130` | real | Población, meta o proyección publicada para el grupo y periodo del encabezado; personas. | 2025 |
| `% Niños de 16 años` | real | Cobertura/indicador publicado para el biológico y grupo del encabezado; verificar escala en cada hoja. | 2025 |
| `Meta Niños _17_años Ajustef_20251130` | real | Población, meta o proyección publicada para el grupo y periodo del encabezado; personas. | 2025 |
| `% Niños de 17 años` | real | Cobertura/indicador publicado para el biológico y grupo del encabezado; verificar escala en cada hoja. | 2025 |
| `Anexo 1 Mpios de Alto Riesgo - FA` | texto/categoría | Clasificación territorial auxiliar original; no se homologa su catálogo en el procesamiento. | 2025 |
| `Municipios Priorizados (426)` | texto/categoría | Clasificación territorial auxiliar original; no se homologa su catálogo en el procesamiento. | 2025 |
| `Catatumbo` | texto/categoría | Clasificación territorial auxiliar original; no se homologa su catálogo en el procesamiento. | 2025 |
| `Municipios PNSR  397` | texto/categoría | Clasificación territorial auxiliar original; no se homologa su catálogo en el procesamiento. | 2025 |
| `Mpios con Brote Tosferina` | texto/categoría | Clasificación territorial auxiliar original; no se homologa su catálogo en el procesamiento. | 2025 |
| `% B.C.G (Tuberculosis) en Recién Nacidos3` | real | Cobertura/indicador publicado para el biológico y grupo del encabezado; verificar escala en cada hoja. | 2025 |
| `% Hb  Recien Nacido ` | real | Cobertura/indicador publicado para el biológico y grupo del encabezado; verificar escala en cada hoja. | 2025 |
| `% (VIP) PARENTERAL`<br>`<  1 Año `<br>`1a Dosis` | real | Cobertura/indicador publicado para el biológico y grupo del encabezado; verificar escala en cada hoja. | 2025 |
| `% Pentavalente `<br>`< 1 Año `<br>`1a Dosis` | real | Cobertura/indicador publicado para el biológico y grupo del encabezado; verificar escala en cada hoja. | 2025 |
| `% Pentavalente `<br>`< 1 Año `<br>`3a Dosis` | real | Cobertura/indicador publicado para el biológico y grupo del encabezado; verificar escala en cada hoja. | 2025 |
| `%Neumo `<br>`<1 año`<br>`2da  Dosis` | real | Cobertura/indicador publicado para el biológico y grupo del encabezado; verificar escala en cada hoja. | 2025 |
| `% ROTAVIRUS`<br>`DE 4 a 11 Meses 29 Dias 2das Dosis` | real | Cobertura/indicador publicado para el biológico y grupo del encabezado; verificar escala en cada hoja. | 2025 |
| `% SRP (Triple Viral)`<br>`de 1 Año`<br>`U. Dosis` | real | Cobertura/indicador publicado para el biológico y grupo del encabezado; verificar escala en cada hoja. | 2025 |
| `% Ha 1 año` | real | Cobertura/indicador publicado para el biológico y grupo del encabezado; verificar escala en cada hoja. | 2025 |
| `% SRP (TRIPLE VIRAL) REFUERZO DE 18 MESES7` | real | Cobertura/indicador publicado para el biológico y grupo del encabezado; verificar escala en cada hoja. | 2025 |
| `% F.A. 1 AÑO  18 Meses de Edad)`<br>`Dosis Unica`<br>`Proyec diciembre24` | real | Cobertura/indicador publicado para el biológico y grupo del encabezado; verificar escala en cada hoja. | 2025 |
| `% DPT `<br>`Al año de 3ra dosis`<br>`1er Ref.` | real | Cobertura/indicador publicado para el biológico y grupo del encabezado; verificar escala en cada hoja. | 2025 |
| `% Varicela`<br>`5 Años ` | real | Cobertura/indicador publicado para el biológico y grupo del encabezado; verificar escala en cada hoja. | 2025 |
| `% DPT `<br>`5 AÑOS`<br>`2do Ref.` | real | Cobertura/indicador publicado para el biológico y grupo del encabezado; verificar escala en cada hoja. | 2025 |
| `Proyeccion VPH Niñas 9 años` | real | Población, meta o proyección publicada para el grupo y periodo del encabezado; personas. | 2025 |
| `Proyección VPH Niños 9 años` | real | Población, meta o proyección publicada para el grupo y periodo del encabezado; personas. | 2025 |
| `POBLACION MENSUAL MENORES DE 1 AÑO` | real | Población, meta o proyección publicada para el grupo y periodo del encabezado; personas. | 2025 |
| `INFLUENZA POB MENOR 1 AÑO - PARA 9 MESES` | real | Población, meta o proyección publicada para el grupo y periodo del encabezado; personas. | 2025 |
| `No DOSIS APLICADAS DE FLU  `<br>`DE 6 A 11 MESES 1as D` | real | Dosis/aplicaciones publicadas para el biológico, edad y esquema del encabezado; conservar el valor original. | 2025 |
| `% FLU `<br>`6 a 11 Meses 1as Dosis` | real | Cobertura/indicador publicado para el biológico y grupo del encabezado; verificar escala en cada hoja. | 2025 |
| `No DOSIS APLICADAS DE FLU  `<br>`DE 6 A 11 MESES 2as D` | real | Dosis/aplicaciones publicadas para el biológico, edad y esquema del encabezado; conservar el valor original. | 2025 |
| `% FLU `<br>`DE 6 a 11 Meses `<br>`2as Dosis` | real | Cobertura/indicador publicado para el biológico y grupo del encabezado; verificar escala en cada hoja. | 2025 |
| `Poblacion de 9 a 11 MESES` | real | Población, meta o proyección publicada para el grupo y periodo del encabezado; personas. | 2025 |
| `Poblacion de 9 meses a 23 meses` | real | Población, meta o proyección publicada para el grupo y periodo del encabezado; personas. | 2025 |
| `Poblacion Niños de 10 a 14 años VPH` | real | Población, meta o proyección publicada para el grupo y periodo del encabezado; personas. | 2025 |
| `No dosis aplicadas niños de 10 a 14 años VPH` | real | Dosis/aplicaciones publicadas para el biológico, edad y esquema del encabezado; conservar el valor original. | 2025 |

</details>

El [CSV procesado de varicela](../../processed/vaccine_coverage/README.md)
tiene un esquema estable y un diccionario independiente de 11 columnas.
