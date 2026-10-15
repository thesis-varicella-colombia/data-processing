"""Integrar SIVIGILA semanal con población, vacunación, CHIRPS y clima."""

from __future__ import annotations

import argparse
import os
import sys
from functools import reduce
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
YEARS = range(2007, 2026)
WEEK_KEYS = ["codigo_municipio", "ano_epidemiologico", "semana_epidemiologica"]
PROVIDENCIA_CODE = "88564"
HUMIDITY_COLUMNS = [
    "humedad_relativa_media_pct",
    "fraccion_area_con_datos_humedad_relativa_media_pct",
    "humedad_especifica_media_g_kg",
    "fraccion_area_con_datos_humedad_especifica_media_g_kg",
    "humedad_absoluta_media_g_m3",
    "fraccion_area_con_datos_humedad_absoluta_media_g_m3",
]


def configure_java() -> None:
    """Match the notebook's Java and Python worker configuration."""
    java_17 = Path("/usr/lib/jvm/java-17-openjdk-amd64")
    if java_17.is_dir():
        os.environ["JAVA_HOME"] = str(java_17)
        os.environ["PATH"] = str(java_17 / "bin") + os.pathsep + os.environ["PATH"]
    os.environ["PYSPARK_PYTHON"] = sys.executable
    os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable


def yearly_files(directory: Path, pattern: str) -> list[Path]:
    files = [directory / pattern.format(year=year) for year in YEARS]
    missing = [path for path in files if not path.is_file()]
    if missing:
        raise FileNotFoundError(f"Faltan archivos de entrada: {missing}")
    return files


def read_yearly(spark, directory: Path, pattern: str):
    return spark.read.parquet(
        *(str(path.resolve()) for path in yearly_files(directory, pattern))
    )


def add_incidence(df, F):
    """Calculate the ten rates per 100,000 used in the notebook."""
    rates = {
        "incidencia_total_100k": (F.col("casos_total"), F.col("poblacion_total")),
        "incidencia_cabecera_100k": (
            F.col("casos_cabecera"), F.col("poblacion_cabecera")
        ),
        "incidencia_rural_100k": (
            F.col("casos_centro_poblado") + F.col("casos_rural"),
            F.col("poblacion_rural"),
        ),
        "incidencia_menor_1_100k": (
            F.col("casos_menor_1"), F.col("poblacion_menor_1")
        ),
        "incidencia_1_4_100k": (F.col("casos_1_4"), F.col("poblacion_1_4")),
        "incidencia_5_14_100k": (F.col("casos_5_14"), F.col("poblacion_5_14")),
        "incidencia_15_49_100k": (
            F.col("casos_15_49"), F.col("poblacion_15_49")
        ),
        "incidencia_50_mas_100k": (
            F.col("casos_50_mas"), F.col("poblacion_50_mas")
        ),
        "incidencia_masculina_100k": (
            F.col("casos_masculinos"), F.col("poblacion_hombres")
        ),
        "incidencia_femenina_100k": (
            F.col("casos_femeninos"), F.col("poblacion_mujeres")
        ),
    }
    for name, (numerator, denominator) in rates.items():
        df = df.withColumn(name, F.try_divide(numerator, denominator) * 100000)
    return df


def join_population_and_vaccination(spark, F):
    sivigila_files = yearly_files(
        REPO_ROOT / "data/processed/sivigila",
        "sivigila_weekly_municipal_{year}.parquet",
    )
    # Los tipos de algunas columnas cambian entre años; se unen por nombre.
    sivigila = reduce(
        lambda left, right: left.unionByName(right),
        (spark.read.parquet(str(path.resolve())) for path in sivigila_files),
    )

    population_path = (
        REPO_ROOT / "data/processed/population/population_municipal_2007_2025.csv"
    )
    if not population_path.is_file():
        raise FileNotFoundError(population_path)
    population_csv = spark.read.option("header", True).csv(str(population_path))
    population = population_csv.select(
        F.col("codigo_municipio"),
        F.col("ano_epidemiologico").cast("int").alias("ano_epidemiologico"),
        *(
            F.col(name).cast("long").alias(name)
            for name in population_csv.columns
            if name not in {"codigo_municipio", "ano_epidemiologico"}
        ),
    )
    integrated = add_incidence(
        sivigila.join(population, ["codigo_municipio", "ano_epidemiologico"], "left"),
        F,
    )

    vaccination_path = (
        REPO_ROOT
        / "data/processed/vaccine_coverage/coberturas_municipales_2016_2025.csv"
    )
    if not vaccination_path.is_file():
        raise FileNotFoundError(vaccination_path)
    vaccination_csv = spark.read.option("header", True).csv(str(vaccination_path))
    vaccination_columns = [
        name
        for name in vaccination_csv.columns
        if name not in {"CODEP", "Nombre_ET", "DIVIPOLA", "Municipio", "anio"}
    ]
    vaccination = vaccination_csv.select(
        F.col("DIVIPOLA").alias("codigo_municipio"),
        F.col("anio").cast("long").alias("ano_epidemiologico"),
        *(F.col(name).cast("double").alias(name) for name in vaccination_columns),
    )
    return integrated.join(
        vaccination, ["codigo_municipio", "ano_epidemiologico"], "left"
    )


def join_chirps(df, spark, F):
    chirps = read_yearly(
        spark,
        REPO_ROOT / "data/processed/chirps_precipitation",
        "chirps_precipitation_weekly_municipal_sat_{year}.parquet",
    )
    selected = chirps.select(
        F.col("codigo_municipio"),
        F.col("ano_epidemiologico"),
        F.col("semana_epidemiologica").cast("short").alias("semana_epidemiologica"),
        F.col("precipitacion_total_mm").alias("precipitacion_total_mm_chirps_sat"),
        F.col("fraccion_area_con_datos").alias("fraccion_area_con_datos_chirps_sat"),
        F.col("dias_con_datos").alias("dias_con_datos_chirps_sat"),
        F.col("dias_imputados").alias("dias_imputados_chirps_sat"),
    )
    return df.join(selected, WEEK_KEYS, "left")


def join_humidity(df, spark, F):
    land = read_yearly(
        spark,
        REPO_ROOT / "data/processed/climate/humidity",
        "humidity_weekly_municipal_{year}.parquet",
    )
    selected = land.select(
        F.col("codigo_municipio"),
        F.col("ano_epidemiologico"),
        F.col("semana_epidemiologica").cast("short").alias("semana_epidemiologica"),
        *(F.col(name) for name in HUMIDITY_COLUMNS),
    )
    df = df.join(selected, WEEK_KEYS, "left")

    providencia = read_yearly(
        spark,
        REPO_ROOT / "data/processed/climate/providencia/humidity",
        "humidity_weekly_providencia_{year}.parquet",
    )
    providencia_selected = providencia.select(
        F.col("codigo_municipio"),
        F.col("ano_epidemiologico"),
        F.col("semana_epidemiologica").cast("short").alias("semana_epidemiologica"),
        *(F.col(name).alias(f"{name}_providencia") for name in HUMIDITY_COLUMNS),
        F.col("fuente_dato").alias("fuente_humedad_providencia"),
        F.col("es_estimacion").alias("es_estimacion_providencia"),
    )
    df = df.join(providencia_selected, WEEK_KEYS, "left").withColumn(
        "_usar_humedad_providencia",
        (F.col("codigo_municipio") == PROVIDENCIA_CODE)
        & F.col("humedad_relativa_media_pct").isNull()
        & F.col("humedad_relativa_media_pct_providencia").isNotNull(),
    )
    for name in HUMIDITY_COLUMNS:
        df = df.withColumn(
            name,
            F.when(
                F.col("_usar_humedad_providencia"), F.col(f"{name}_providencia")
            ).otherwise(F.col(name)),
        )
    return (
        df.withColumn(
            "fuente_humedad",
            F.when(
                F.col("_usar_humedad_providencia"),
                F.col("fuente_humedad_providencia"),
            ).otherwise(F.lit("ERA5-Land_daily_UTC")),
        )
        .withColumn(
            "es_estimacion_humedad",
            F.when(
                F.col("_usar_humedad_providencia"),
                F.col("es_estimacion_providencia"),
            ).otherwise(F.lit(False)),
        )
        .drop(
            "_usar_humedad_providencia",
            "fuente_humedad_providencia",
            "es_estimacion_providencia",
            *(f"{name}_providencia" for name in HUMIDITY_COLUMNS),
        )
    )


def join_climate_variable(df, spark, F, *, variable: str, value_column: str):
    """Use Providencia estimates only where ERA5-Land has a null value."""
    land = read_yearly(
        spark,
        REPO_ROOT / f"data/processed/climate/{variable}",
        f"{variable}_weekly_municipal_{{year}}.parquet",
    )
    providencia = read_yearly(
        spark,
        REPO_ROOT / f"data/processed/climate/providencia/{variable}",
        f"{variable}_weekly_providencia_{{year}}.parquet",
    )
    providencia_selected = providencia.select(
        F.col("codigo_municipio"),
        F.col("ano_epidemiologico"),
        F.col("semana_epidemiologica").cast("short").alias("semana_epidemiologica"),
        F.col(value_column).alias("_valor_providencia"),
        F.col("fraccion_area_con_datos").alias("_cobertura_providencia"),
        F.col("fuente_dato").alias("_fuente_providencia"),
        F.col("es_estimacion").alias("_estimacion_providencia"),
    )
    combined = (
        land.select(
            F.col("codigo_municipio"),
            F.col("ano_epidemiologico"),
            F.col("semana_epidemiologica")
            .cast("short")
            .alias("semana_epidemiologica"),
            F.col(value_column),
            F.col("fraccion_area_con_datos"),
        )
        .join(providencia_selected, WEEK_KEYS, "left")
        .withColumn(
            "_usar_providencia",
            (F.col("codigo_municipio") == PROVIDENCIA_CODE)
            & F.col(value_column).isNull()
            & F.col("_valor_providencia").isNotNull(),
        )
    )
    label = "precipitacion" if variable == "precipitation" else "temperatura"
    selected = combined.select(
        *WEEK_KEYS,
        F.when(F.col("_usar_providencia"), F.col("_valor_providencia"))
        .otherwise(F.col(value_column))
        .alias(f"{value_column}_era5"),
        F.when(F.col("_usar_providencia"), F.col("_cobertura_providencia"))
        .otherwise(F.col("fraccion_area_con_datos"))
        .alias(f"fraccion_area_con_datos_{label}_era5"),
        F.when(F.col("_usar_providencia"), F.col("_fuente_providencia"))
        .when(F.col(value_column).isNotNull(), F.lit("ERA5-Land_daily_UTC"))
        .alias(f"fuente_{label}"),
        F.when(F.col("_usar_providencia"), F.col("_estimacion_providencia"))
        .when(F.col(value_column).isNotNull(), F.lit(False))
        .alias(f"es_estimacion_{label}"),
    )
    return df.join(selected, WEEK_KEYS, "left")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--master", default="local[2]", help="Spark master")
    parser.add_argument("--driver-memory", default="2g", help="Spark driver memory")
    parser.add_argument(
        "--output",
        type=Path,
        default=REPO_ROOT
        / "data/processed/integration_data/sivigila_integrado_semanal_municipal.parquet",
        help="Output Spark Parquet directory; existing data is overwritten",
    )
    args = parser.parse_args()
    configure_java()
    from pyspark.sql import SparkSession, functions as F

    spark = (
        SparkSession.builder.master(args.master)
        .appName("integrate-sivigila")
        .config("spark.driver.memory", args.driver_memory)
        .config("spark.ui.enabled", "false")
        .config("spark.sql.shuffle.partitions", "8")
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("ERROR")
    try:
        integrated = join_population_and_vaccination(spark, F)
        integrated = join_chirps(integrated, spark, F)
        integrated = join_humidity(integrated, spark, F)
        integrated = join_climate_variable(
            integrated,
            spark,
            F,
            variable="precipitation",
            value_column="precipitacion_total_mm",
        )
        integrated = join_climate_variable(
            integrated,
            spark,
            F,
            variable="temperature",
            value_column="temperatura_media_c",
        )
        output = args.output.expanduser().resolve()
        output.parent.mkdir(parents=True, exist_ok=True)
        integrated.coalesce(4).write.mode("overwrite").parquet(str(output))
        print(f"Dataset integrado guardado en {output}")
    finally:
        spark.stop()


if __name__ == "__main__":
    main()
