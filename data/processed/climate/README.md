# Ficha técnica: clima semanal municipal, días UTC

Los procesadores usan `data/raw/era5_land/era5_land_daily_AAAA.nc`, obtenido de [Earth Data Hub ERA5-Land Daily UTC](https://earthdatahub.destine.eu/collections/era5/datasets/era5-land-daily). El periodo de análisis es **2007–2025** por año epidemiológico. Los archivos se escriben por separado en `temperature/`, `humidity/` y `precipitation/`, uno por año epidemiológico. Las unidades originales son K (`t2m`, `d2m`), Pa (`sp`) y m (`tp`). La resolución de origen es 0,1° y un día **00:00–23:59 UTC**, sin conversión horaria.

## Semanas y geometría

Las semanas son de **domingo a sábado**; la semana 1 contiene el **4 de enero**. `ano_epidemiologico`, `semana_epidemiologica`, `inicio_semana` y `fin_semana` describen cada semana completa, incluso si atraviesa dos años calendario. Por eso pueden requerirse datos de 2006 y 2026. Las fechas son etiquetas de días UTC. La definición de semana se conserva del pipeline anterior; cambia la base horaria de los datos diarios, que antes era UTC−05:00.

Los polígonos se leen del MGN municipal en CRS84 y se comprueban contra DIVIPOLA. Se usan solo entidades `MUNICIPIO`. Para cada celda que intersecta un polígono se calcula el **área geodésica real de la intersección** con `pyproj.Geod(ellps="WGS84")`; `STRtree` reduce las parejas que requieren intersección. No se usan centroides. La geometría MGN 2025 se aplica a toda la serie, como en el pipeline anterior; los cambios administrativos históricos no se armonizan automáticamente.

En la serie 2007–2025, **Providencia (`88564`)** no tiene valores válidos en las celdas ERA5-Land que intersectan su polígono: las 992 salidas semanales de ese municipio son `NaN` con cobertura 0. El pipeline conserva ese faltante para no asignar datos de celdas externas al municipio.

La [estimación separada para Providencia](providencia/README.md) usa ERA5 atmosférico horario de Earth Data Hub a 0,25°. Sus archivos llevan marcas de procedencia y no alteran estos resultados ERA5-Land.

Para temperatura y humedad, cada celda y día válido aporta `valor × área` al numerador y `área` al denominador de su municipio y semana. Un `NaN` no aporta a ninguno. Esto conserva el esquema de ponderación **área × día** del pipeline previo; con cobertura completa equivale al promedio de las siete medias diarias municipales. La cobertura se calcula como `área válida acumulada / (7 × área municipal cubierta por la grilla)`, entre 0 y 1. En humedad se publica una cobertura por variable.

## Variables

- **Temperatura:** `t2m − 273,15`, de K a °C. Salida `temperature/temperature_weekly_municipal_AAAA.parquet`; columna `temperatura_media_c` y `fraccion_area_con_datos`.
- **Humedad:** primero se calculan tres humedades **por celda y día** usando `t2m`, `d2m` y `sp`, y después se promedian por área y semana. Salida `humidity/humidity_weekly_municipal_AAAA.parquet`; columnas `humedad_relativa_media_pct`, `humedad_especifica_media_g_kg`, `humedad_absoluta_media_g_m3` y `fraccion_area_con_datos_<nombre_de_columna>` para cada una.
- **Precipitación:** `tp × 1000`, de m a mm. Cada día se calcula la media municipal ponderada por área y después **se suman los siete días**. No se promedian los días. Una semana con un día sin ninguna celda válida queda `NaN`, con cobertura menor que 1. Salida `precipitation/precipitation_weekly_municipal_AAAA.parquet`; columnas `precipitacion_total_mm` y `fraccion_area_con_datos`.

## Fórmulas de humedad

Se usa presión de vapor de saturación sobre agua (Magnus): `e_s(T) = 611,2 × exp[17,67 × T_C/(T_C + 243,5)]` Pa, con `T_C = T_K − 273,15` y `e = e_s(Td)`.

- Humedad relativa: `RH = 100 × e/e_s(T)` (%).
- Humedad específica: `q = 1000 × 0,622 × e/[sp − 0,378 × e]` (g/kg). `sp` es la presión superficial de cada celda, no una presión fija.
- Humedad absoluta, densidad del vapor: `ρ_v = 1000 × e/(461,5 × T_K)` (g/m³).

Se descartan combinaciones no finitas, presión no positiva, presión menor o igual que `e`, temperaturas fuera de 180–330 K y `Td > T + 0,5 K`. RH mayor que 100,5 % se descarta; valores hasta 100,5 % se truncan a 100 %. También se exige `q ≥ 0` y `ρ_v ≥ 0`. La fórmula de Magnus sobre agua se conserva del pipeline previo, incluso bajo 0 °C. Estas humedades se derivan de **medias diarias** de temperatura y punto de rocío: no equivalen exactamente a promediar humedades calculadas hora por hora.

[ECMWF explica el cálculo de RH y humedad específica a partir de T, Td y presión superficial](https://confluence.ecmwf.int/pages/viewpage.action?pageId=171416412). [Su material de termodinámica define humedad absoluta y específica](https://confluence.ecmwf.int/download/attachments/50042306/MOIST_INTRO_T1.pdf?api=v2). [WMO tabula `R_v = 461,5 J kg⁻¹ K⁻¹`](https://cyclone.wmo.int/pdf/Global-Guide-to-Tropical-Cyclone-Forecasting.pdf).

## Formato y ejecución

Todos los Parquet incluyen `codigo_municipio` como texto, `nombre_municipio`, `ano_epidemiologico`, `semana_epidemiologica`, `inicio_semana` y `fin_semana`. La [ficha de los NetCDF de entrada](../../raw/era5_land/README.md) explica su descarga y autenticación. Las tres salidas tienen fichas propias: [temperatura](temperature/README.md), [humedad](humidity/README.md) y [precipitación](precipitation/README.md).

Desde la raíz del repositorio, con `scripts/requirements.txt` instalado:

```bash
.venv/bin/python scripts/processing/calculate_weekly_temperature.py --validate-only
.venv/bin/python scripts/processing/calculate_weekly_humidity.py --validate-only
.venv/bin/python scripts/processing/calculate_weekly_precipitation.py --validate-only
.venv/bin/python scripts/processing/calculate_weekly_temperature.py
.venv/bin/python scripts/processing/calculate_weekly_humidity.py
.venv/bin/python scripts/processing/calculate_weekly_precipitation.py
```

Los procesadores aceptan `--start-year`, `--end-year`, `--municipality CODIGO`, `--validate-only` y `--overwrite`. `--validate-only` cuenta archivos de entrada faltantes; `--overwrite` regenera salidas existentes. Se lee un año calendario por vez en bloques de diez días y se reutilizan los pesos espaciales mientras la grilla sea idéntica. Para cubrir semanas completas se usan los meses de borde 2006-12 y 2026-01 descritos en la ficha de entrada.
