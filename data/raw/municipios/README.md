# Ficha técnica: fuentes geográficas de municipios de Colombia

Esta carpeta reúne códigos territoriales y geometrías del DANE. **DIVIPOLA** es la División Político Administrativa de Colombia: una nomenclatura que asigna códigos a departamentos, municipios y otras unidades territoriales para identificarlos de forma consistente.

## Códigos DIVIPOLA (CSV)

El archivo `DIVIPOLA-_Códigos_municipios_20261007.csv` contiene códigos y nombres de departamentos y municipios, el tipo de unidad territorial y coordenadas de referencia. Los códigos deben leerse como **texto** para conservar los ceros iniciales.

La copia local incluye `94343` (Barrancominas) y no incluye el código histórico `94663` (Mapiripana). El GeoJSON local también contiene `94343` y no `94663`. El procesamiento semanal de Sivigila homologa las notificaciones con residencia `94663` a `94343` para usar la geografía actual; esta decisión se documenta en la [ficha del resultado](../../processed/sivigila/README.md).

Fuente: [DIVIPOLA - Códigos municipios, Datos Abiertos Colombia](https://www.datos.gov.co/Mapas-Nacionales/DIVIPOLA-C-digos-municipios/gdxc-w37w/about_data).

Para descargar una copia, abre la página de la fuente, entra a la vista de datos y usa **Exportar → CSV**. La fecha del nombre del archivo local identifica la copia guardada en este repositorio; consulta la página para obtener una versión actualizada.

## Geometrías GeoJSON del MGN 2025

El archivo local `MGN_ADM_MPIO_GRAFICO.geojson` contiene polígonos de municipios del Marco Geoestadístico Nacional (MGN) 2025, con códigos y nombres municipales, en **CRS84** (longitud y latitud en grados). El [Geoportal del DANE](https://geoportal.dane.gov.co/mparcgis/rest/services/MGN2025/Serv_CapasMGN_2025/FeatureServer/317) publica la capa **Municipio (ID 317)** como polígonos (`esriGeometryPolygon`) y admite consultas en GeoJSON. Los scripts climáticos seleccionan solo las entidades `MUNICIPIO`, comprueban sus códigos contra DIVIPOLA y calculan los recortes o las intersecciones a partir de este archivo.

Desde esta carpeta, descarga los polígonos municipales con:

```bash
curl -L \
  "https://geoportal.dane.gov.co/mparcgis/rest/services/MGN2025/Serv_CapasMGN_2025/FeatureServer/317/query?where=1%3D1&outFields=*&f=geojson" \
  -o MGN_ADM_MPIO_GRAFICO.geojson
```

También puedes [abrir la consulta directamente en el navegador](https://geoportal.dane.gov.co/mparcgis/rest/services/MGN2025/Serv_CapasMGN_2025/FeatureServer/317/query?where=1%3D1&outFields=*&f=geojson) y guardar el resultado como `MGN_ADM_MPIO_GRAFICO.geojson`.

## Esquemas y diccionarios de datos

### CSV DIVIPOLA

Una fila identifica una entidad territorial por `Código Municipio`. CSV no
almacena tipos: se indican tipos lógicos de lectura. Las coordenadas usan
coma decimal y deben convertirse explícitamente al leerlas como números.

| Columna | Tipo | Descripción |
| --- | --- | --- |
| `Código Departamento` | texto | Código departamental de dos dígitos, con ceros iniciales. |
| `Nombre Departamento` | texto | Nombre del departamento. |
| `Código Municipio` | texto | Código DIVIPOLA completo de cinco dígitos, con ceros iniciales. |
| `Nombre Municipio` | texto | Nombre de la entidad territorial. |
| `Tipo: Municipio / Isla / Área no municipalizada` | texto categórico | Tipo de entidad: Municipio, Isla o Área no municipalizada. |
| `longitud` | real (coma decimal en CSV) | Longitud de referencia, grados este; no es una geometría municipal. |
| `Latitud` | real (coma decimal en CSV) | Latitud de referencia, grados norte. |

### GeoJSON municipal

El objeto raíz es una `FeatureCollection`; `features` es un arreglo de
objetos `Feature`. Cada uno contiene `properties` y `geometry`. Las
geometrías del archivo local son `MultiPolygon`, con coordenadas CRS84 en orden
longitud, latitud. Las propiedades observadas son:

| Propiedad JSON | Tipo JSON | Descripción |
| --- | --- | --- |
| `dpto_ccdgo` | string | Código departamental de dos dígitos. |
| `mpio_ccdgo` | string | Componente municipal de tres dígitos dentro del departamento. |
| `mpio_cdpmp` | string | Código DIVIPOLA completo de cinco dígitos; clave de cruce. |
| `dpto_cnmbr` | string | Nombre del departamento. |
| `mpio_cnmbr` | string | Nombre de la entidad municipal. |
| `mpio_crslc` | string | Atributo original MGN; no se usa en el procesamiento y su codificación no se homologa aquí. |
| `mpio_tipo` | string | Tipo de entidad; los scripts climáticos seleccionan MUNICIPIO. |
| `mpio_narea` | number | Área publicada por MGN; no se usa como peso geodésico del procesamiento. |
| `mpio_nano` | integer | Año de referencia del atributo MGN; se observan 2024 y 2025 en el archivo local. |
| `shape_Leng` | number | Longitud geométrica almacenada por la fuente; no usar como distancia en metros sin verificar sus unidades. |
| `shape_Area` | number | Área geométrica almacenada por la fuente; no usar como área en m² sin verificar sus unidades. |
