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
