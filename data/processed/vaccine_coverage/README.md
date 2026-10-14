# Coberturas municipales de vacunación contra varicela

`coberturas_municipales_2016_2025.csv` reúne las columnas de varicela del [libro PAI](../../raw/vaccine_coverage/README.md). El [script de procesamiento](../../../scripts/processing/process_vaccine_coverage.py) reproduce la selección y transformación del [notebook exploratorio](../../../notebooks/vacc_coverage_raw_explore.ipynb).

## Alcance y temporalidad

El archivo tiene **11.220 filas y 11 columnas**: 1.122 filas por año de salida, de 2016 a 2025. Cada fila conserva los identificadores territoriales y las metas, dosis y coberturas de la hoja Excel correspondiente. `DIVIPOLA` y `CODEP` se leen como texto para conservar ceros iniciales.

El año de salida `anio` es el **año de la hoja original más uno**: los datos de 2015 se etiquetan como 2016, y así sucesivamente hasta los datos de 2024, etiquetados como 2025. Este desplazamiento reproduce la decisión analítica del notebook de usar la cobertura publicada al cierre del año anterior. **`anio` no es el año en que se aplicaron las dosis**. La hoja 2025 se lee durante el procesamiento, pero se excluye del CSV final.

## Columnas

| Columna | Contenido |
| --- | --- |
| `CODEP` | Código de departamento del libro de origen. |
| `Nombre_ET` | Nombre de la entidad territorial en el libro. |
| `DIVIPOLA` | Código municipal, conservado como texto. |
| `Municipio` | Nombre municipal en la hoja original. |
| `meta_pob_1_anio` | Meta de población usada para la dosis de varicela de un año; se conserva el valor original, incluida la meta de media cohorte de la hoja 2015. |
| `varicela_un_anio_dosis_unica` | Dosis única de varicela de un año reportadas. |
| `%_varicela_un_anio_dosis_unica` | Cobertura publicada para esa dosis, en porcentaje. |
| `meta_pob_5_anios` | Meta de población de cinco años; nula para las hojas 2015–2018. |
| `varicela_cinco_anios_refuerzo` | Dosis de refuerzo de cinco años; nula para las hojas 2015–2018. |
| `%_varicela_cinco_anios_refuerzo` | Cobertura publicada del refuerzo, en porcentaje; nula para las hojas 2015–2018. |
| `anio` | Año de análisis asignado tras desplazar un año la hoja de origen. |

Las columnas de cobertura se copian del Excel, **no se recalculan** a partir de dosis y metas. Pueden superar 100 %. En la hoja 2019 el conteo de cinco años aparece sin la palabra `Ref.` en el encabezado; se armoniza con el mismo nombre de salida. La columna adicional `% Varicela\n5 Años ` de la hoja 2025 se descarta antes de unir los años, aunque esa hoja no llega al CSV final.

El script selecciona rangos fijos de filas de las hojas, igual que el notebook. No valida cada código municipal ni elimina filas vacías: el CSV actual contiene **dos filas sin `DIVIPOLA`**, una en el año de salida 2023 y otra en 2024. Revise esas filas antes de usar el archivo como tabla de municipios únicos. Los valores faltantes en las tres columnas de cinco años para los años de salida 2016–2019 son intencionales.

## Reproducción

Coloque el libro con el nombre indicado en la [ficha de origen](../../raw/vaccine_coverage/README.md) dentro de `data/raw/vaccine_coverage/`. Desde la raíz del repositorio, con las dependencias de `requirements.txt` instaladas:

```bash
.venv/bin/python scripts/processing/process_vaccine_coverage.py
```

El script escribe `data/processed/vaccine_coverage/coberturas_municipales_2016_2025.csv`. Acepta `--input-file` y `--output-file` para cambiar las rutas. El CSV se guarda con codificación UTF-8 con BOM (`utf-8-sig`).
