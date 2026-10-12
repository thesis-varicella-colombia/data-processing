# Ficha técnica: fuentes geográficas de municipios de Colombia

Esta carpeta reúne códigos territoriales y geometrías del DANE. **DIVIPOLA** es la División Político Administrativa de Colombia: una nomenclatura que asigna códigos a departamentos, municipios y otras unidades territoriales para identificarlos de forma consistente.

## Códigos DIVIPOLA (CSV)

El archivo `DIVIPOLA-_Códigos_municipios_20261007.csv` contiene códigos y nombres de departamentos y municipios, el tipo de unidad territorial y coordenadas de referencia. Los códigos deben leerse como **texto** para conservar los ceros iniciales.

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
