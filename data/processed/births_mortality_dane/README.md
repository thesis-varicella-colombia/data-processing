# Nacimientos y mortalidad — DANE

Las fichas técnicas se guardan junto a cada conjunto de datos:

| Conjunto | Ficha técnica |
| --- | --- |
| Nacimientos originales | [Excel del DANE y sus versiones](../../raw/births_mortality_dane/births/README.md) |
| Nacimientos procesados | [Parquet consolidado 2008–2025](births/README.md) |
| Defunciones originales | [Excel y versiones de entrada](../../raw/births_mortality_dane/mortality/README.md) |
| Defunciones procesadas | [Totales territoriales de 2008–2025](mortality/README.md) |
| Integración de nacimientos y mortalidad infantil | [Saldo de sobrevivientes de un año y validación de unión](integration/README.md) |

Los archivos procesados se encuentran en `births/births.parquet`,
`mortality/mortality.parquet` e `integration/surviving_infants.parquet`. Sus fichas describen las variables,
la generación y las validaciones.

## Esquemas y diccionarios

Esta carpeta agrupa productos distintos. Cada ficha documenta su propio
esquema, tipos físicos Arrow y significado de todas las columnas:

| Producto | Unidad | Columnas | Esquema y diccionario |
| --- | --- | --- | --- |
| `births/births.parquet` | Año × entidad de residencia de la madre o categoría/total | 21 | [Nacimientos](births/README.md#variables-tipos-y-nulos) |
| `mortality/mortality.parquet` | Año × entidad de residencia o categoría/total | 30 | [Defunciones](mortality/README.md#esquema-físico-y-diccionario-completo) |
| `integration/surviving_infants.parquet` | Año × entidad o categoría, sin totales departamentales | 8 | [Saldo de sobrevivientes](integration/README.md#columnas-y-cálculo) |
| Archivos de validación de la integración | Fila pendiente u objeto de resumen | Depende del archivo | [CSV y JSON de validación](integration/README.md#esquema-de-los-archivos-de-validación) |
