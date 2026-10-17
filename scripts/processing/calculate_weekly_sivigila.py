"""Agrega notificaciones de varicela de Sivigila por municipio y semana reportada.

Lee los CSV originales por bloques. Conserva ANO/SEMANA del INS y documenta
las discrepancias con fechas y códigos geográficos en un informe por año.
"""

from __future__ import annotations

import argparse
import json
import logging
from collections import Counter
from datetime import timedelta
from pathlib import Path

import pandas as pd

from epidemiological_weeks import weeks_in_range


ROOT = Path(__file__).resolve().parents[2]
INPUT = ROOT / "data/raw/sivigila/csv"
DIVIPOLA = ROOT / "data/raw/municipios/DIVIPOLA-_Códigos_municipios_20261007.csv"
OUTPUT = ROOT / "data/processed/sivigila"
LOGGER = logging.getLogger(__name__)
CHUNK_SIZE = 50_000
GEOGRAPHIC_CODE_ALIASES = {
    "27086": "27493",  # Belén de Bajirá -> Nuevo Belén de Bajirá
    "94663": "94343",  # Mapiripana -> Barrancominas
    "88000": "88001",  # Municipio desconocido del archipiélago -> San Andrés
}
RESIDENCE_CRITERION = (
    "todas las entidades del DIVIPOLA local; "
    "homologaciones 27086 a 27493, 94663 a 94343 y 88000 a 88001"
)

GROUP_COLUMNS = ["ano_epidemiologico", "semana_epidemiologica", "codigo_municipio"]
SOURCE_COLUMNS = [
    "ANO", "SEMANA", "COD_EVE", "COD_DPTO_R", "COD_MUN_R", "COD_MUN_N",
    "COD_DPTO_O", "COD_MUN_O", "COD_PAIS_O", "FEC_NOT", "INI_SIN",
    "AJUSTE", "SEXO", "PAC_HOS", "EDAD", "UNI_MED", "AREA", "TIP_SS",
    "PER_ETN", "estrato", "fuente", "TIP_CAS", "CON_FIN", "FEC_DEF",
    "CBMTE", "FM_FUERZA", "FM_UNIDAD", "FM_GRADO", "GP_DISCAPA",
    "GP_DESPLAZ", "GP_MIGRANT", "GP_CARCELA", "GP_GESTAN", "GP_INDIGEN",
    "GP_POBICFB", "GP_MAD_COM", "GP_DESMOVI", "GP_PSIQUIA", "GP_VIC_VIO",
    "GP_OTROS",
]

POPULATION_GROUPS = {
    "GP_DISCAPA": "casos_discapacidad",
    "GP_DESPLAZ": "casos_desplazados",
    "GP_MIGRANT": "casos_migrantes",
    "GP_CARCELA": "casos_carcelarios",
    "GP_GESTAN": "casos_gestantes",
    "GP_INDIGEN": "casos_indigentes",
    "GP_POBICFB": "casos_icbf",
    "GP_MAD_COM": "casos_madres_comunitarias",
    "GP_DESMOVI": "casos_desmovilizados",
    "GP_PSIQUIA": "casos_centros_psiquiatricos",
    "GP_VIC_VIO": "casos_victimas_violencia",
    "GP_OTROS": "casos_otros_grupos",
}


def entity_names(path: Path) -> tuple[dict[str, str], set[str]]:
    """Acepta todos los códigos de entidades del DIVIPOLA local."""
    df = pd.read_csv(path, dtype=str, encoding="utf-8-sig", keep_default_na=False)
    expected = {"Código Municipio", "Nombre Municipio"}
    if not expected.issubset(df.columns):
        raise ValueError(f"DIVIPOLA carece de columnas requeridas: {expected - set(df.columns)}")
    codes = df["Código Municipio"].str.strip().str.zfill(5)
    names = df["Nombre Municipio"].str.strip()
    if codes.duplicated().any():
        raise ValueError("DIVIPOLA tiene códigos de entidad duplicados")
    valid = dict(zip(codes, names))
    if not valid:
        raise ValueError("DIVIPOLA no contiene entidades")
    missing_targets = set(GEOGRAPHIC_CODE_ALIASES.values()) - set(valid)
    if missing_targets:
        raise ValueError(f"DIVIPOLA carece de códigos destino para homologar: {sorted(missing_targets)}")
    return valid, set(codes)


def read_date(series: pd.Series) -> pd.Series:
    """Los CSV guardan fechas d/M/AAAA seguidas de una hora en texto español."""
    first = series.str.extract(r"^(\d{1,2}/\d{1,2}/\d{4})", expand=False)
    return pd.to_datetime(first, format="%d/%m/%Y", errors="coerce")


def number(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series.str.strip(), errors="coerce")


def add_metrics(df: pd.DataFrame, valid_codes: set[str]) -> pd.DataFrame:
    """Construye indicadores mutuamente interpretables sin imputar datos clínicos."""
    result = pd.DataFrame(index=df.index)
    result["casos_total"] = 1

    def add(name: str, condition: pd.Series) -> None:
        if name in result:
            raise ValueError(f"Indicador duplicado: {name}")
        result[name] = condition.fillna(False).astype("int8")

    sex = df.SEXO.str.strip().str.upper()
    add("casos_masculinos", sex.eq("M"))
    add("casos_femeninos", sex.eq("F"))
    # Equivale al booleano del notebook: True solo para el texto exacto "1".
    add("casos_hospitalizados", df.PAC_HOS.eq("1"))

    age = number(df.EDAD)
    age_unit = number(df.UNI_MED)
    age_years = pd.Series(float("nan"), index=df.index)
    for unit, divisor in [(1, 1), (2, 12), (3, 365.25), (4, 365.25 * 24), (5, 365.25 * 24 * 60)]:
        mask = age_unit.eq(unit)
        age_years.loc[mask] = age.loc[mask] / divisor
    age_groups = [
        ("casos_menor_1", 0, 1), ("casos_1_4", 1, 5),
        ("casos_5_14", 5, 15), ("casos_15_49", 15, 50),
        ("casos_50_mas", 50, float("inf")),
    ]
    for name, minimum, maximum in age_groups:
        add(name, age_years.ge(minimum) & age_years.lt(maximum))
    add("casos_edad_desconocida", age_years.isna())

    area = number(df.AREA)
    for code, name in [(1, "cabecera"), (2, "centro_poblado"), (3, "rural")]:
        add(f"casos_{name}", area.eq(code))
    insurance = df.TIP_SS.str.strip().str.upper()
    for code, name in [("C", "contributivo"), ("S", "subsidiado"),
                       ("P", "excepcion"), ("E", "especial"), ("N", "no_asegurado")]:
        add(f"casos_{name}", insurance.eq(code))
    ethnicity = number(df.PER_ETN)
    for code, name in [(1, "indigena"), (2, "rom"), (3, "raizal"),
                       (4, "palenquero"), (5, "afro"), (6, "otro_etnico")]:
        add(f"casos_{name}", ethnicity.eq(code))
    for code in range(1, 7):
        add(f"casos_estrato_{code}", number(df.estrato).eq(code))
    for column, name in POPULATION_GROUPS.items():
        add(name, number(df[column]).eq(1))

    source = number(df.fuente)
    for code, name in [(1, "notificacion_rutinaria"), (2, "busqueda_activa_institucional"),
                       (3, "vigilancia_intensificada"), (4, "busqueda_activa_comunitaria"),
                       (5, "investigaciones")]:
        add(f"casos_{name}", source.eq(code))

    notification = df.COD_MUN_N.str.strip().str.zfill(5).replace(GEOGRAPHIC_CODE_ALIASES)
    known_notification = notification.isin(valid_codes)
    same_notification = known_notification & notification.eq(df.codigo_municipio)
    add("casos_notificados_mismo_municipio", same_notification)
    add("casos_notificados_otro_municipio", known_notification & ~same_notification)
    add("casos_municipio_notificacion_desconocido", ~known_notification)

    occurrence = (df.COD_DPTO_O.str.strip().str.zfill(2)
                  + df.COD_MUN_O.str.strip().str.zfill(3)).replace(GEOGRAPHIC_CODE_ALIASES)
    colombia = number(df.COD_PAIS_O).eq(170)
    known_occurrence = colombia & occurrence.isin(valid_codes)
    add("casos_ocurridos_en_colombia", colombia)
    add("casos_ocurrencia_mismo_municipio_residencia",
        known_occurrence & occurrence.eq(df.codigo_municipio))
    add("casos_ocurrencia_otro_municipio",
        known_occurrence & occurrence.ne(df.codigo_municipio))
    add("casos_ocurrencia_municipio_desconocido", colombia & ~known_occurrence)

    notification_date = read_date(df.FEC_NOT)
    symptom_date = read_date(df.INI_SIN)
    week_start = df.inicio_semana_reportada
    in_reported_week = ((symptom_date >= week_start)
                        & (symptom_date < week_start + pd.Timedelta(days=7)))
    add("casos_inicio_sintomas_fuera_semana_reportada",
        symptom_date.notna() & ~in_reported_week)
    add("casos_inicio_sintomas_sin_fecha", symptom_date.isna())
    add("casos_notificacion_fuera_semana_reportada",
        notification_date.notna() & ~((notification_date >= week_start)
                                      & (notification_date < week_start + pd.Timedelta(days=7))))
    lag = (notification_date - symptom_date).dt.days
    add("casos_notificados_mismo_dia", lag.eq(0))
    add("casos_notificados_1_3_dias", lag.between(1, 3))
    add("casos_notificados_4_7_dias", lag.between(4, 7))
    add("casos_notificados_mas_7_dias", lag.gt(7))
    add("casos_notificados_antes_inicio_sintomas", lag.lt(0))
    add("casos_sin_fecha_para_demora", lag.isna())

    initial = number(df.TIP_CAS)
    for code, name in [(1, "sospechosos"), (2, "probables"),
                       (3, "confirmados_laboratorio"), (4, "confirmados_clinica"),
                       (5, "confirmados_nexo")]:
        add(f"casos_clasificacion_inicial_{name}", initial.eq(code))
    final = number(df.CON_FIN)
    add("casos_vivos", final.eq(1))
    add("casos_fallecidos", final.eq(2))
    add("casos_condicion_desconocida", ~final.isin([1, 2]))
    adjustment = df.AJUSTE.str.strip().str.upper()
    for code, name in [("0", "sin_ajuste"), ("3", "confirmados_laboratorio"),
                       ("4", "confirmados_clinica"), ("5", "confirmados_nexo"),
                       ("7", "otro_ajuste")]:
        add(f"casos_ajuste_{name}", adjustment.eq(code))
    add("casos_fuerzas_armadas", df[["FM_FUERZA", "FM_UNIDAD", "FM_GRADO"]]
        .apply(lambda s: s.str.strip().ne(""), axis=0).any(axis=1))
    return result


def process_year(source: Path, year: int, names: dict[str, str], all_codes: set[str],
                 weeks: dict[tuple[int, int], object]) -> tuple[pd.DataFrame, dict]:
    valid = set(names)
    quality: Counter[str] = Counter()
    excluded_codes: Counter[str] = Counter()
    pieces = []
    for chunk in pd.read_csv(source, dtype=str, keep_default_na=False,
                             usecols=SOURCE_COLUMNS, chunksize=CHUNK_SIZE,
                             encoding="utf-8-sig"):
        quality["registros_entrada"] += len(chunk)
        if not number(chunk.ANO).eq(year).all():
            raise ValueError(f"{source.name}: ANO no coincide con {year}")
        if not number(chunk.COD_EVE).eq(831).all():
            raise ValueError(f"{source.name}: contiene eventos distintos de 831")
        reported_week = number(chunk.SEMANA)
        if not reported_week.isin([week for y, week in weeks if y == year]).all():
            raise ValueError(f"{source.name}: SEMANA fuera del calendario epidemiológico {year}")

        raw_code = chunk.COD_DPTO_R.str.strip().str.zfill(2) + chunk.COD_MUN_R.str.strip().str.zfill(3)
        code = raw_code.replace(GEOGRAPHIC_CODE_ALIASES)
        quality["homologados_27086_a_27493"] += int(raw_code.eq("27086").sum())
        quality["homologados_94663_a_94343"] += int(raw_code.eq("94663").sum())
        quality["homologados_88000_a_88001"] += int(raw_code.eq("88000").sum())
        known_entity = code.isin(valid)
        quality["excluidos_entidad_no_municipio"] += int((~known_entity & code.isin(all_codes)).sum())
        quality["excluidos_codigo_residencia_desconocido"] += int((~known_entity & ~code.isin(all_codes)).sum())
        excluded_codes.update(code[~known_entity].value_counts().to_dict())
        adjustment = chunk.AJUSTE.str.strip().str.upper()
        kept = known_entity & ~adjustment.isin(["6", "D"])
        quality["excluidos_ajuste_6_o_D"] += int((known_entity & ~kept).sum())
        chunk = chunk.loc[kept].copy()
        if chunk.empty:
            continue
        chunk["codigo_municipio"] = code.loc[kept]
        chunk["ano_epidemiologico"] = year
        chunk["semana_epidemiologica"] = reported_week.loc[kept].astype("int16")
        quality["registros_incluidos"] += len(chunk)

        start = chunk.semana_epidemiologica.map(lambda week: pd.Timestamp(weeks[year, int(week)]))
        chunk["inicio_semana_reportada"] = start
        onset = read_date(chunk.INI_SIN)
        notified = read_date(chunk.FEC_NOT)
        quality["inicio_sintomas_sin_fecha"] += int(onset.isna().sum())
        quality["inicio_sintomas_fuera_semana_reportada"] += int(
            (onset.notna() & ~((onset >= start) & (onset < start + pd.Timedelta(days=7)))).sum())
        quality["notificacion_fuera_semana_reportada"] += int(
            (notified.notna() & ~((notified >= start) & (notified < start + pd.Timedelta(days=7)))).sum())
        evidence = chunk.FEC_DEF.str.strip().ne("") | chunk.CBMTE.str.strip().ne("")
        death = number(chunk.CON_FIN).eq(2)
        quality["evidencia_defuncion_sin_CON_FIN_2"] += int((evidence & ~death).sum())
        quality["CON_FIN_2_sin_fecha_ni_causa"] += int((death & ~evidence).sum())

        metrics = add_metrics(chunk, valid)
        keys = chunk[GROUP_COLUMNS]
        pieces.append(pd.concat([keys, metrics], axis=1).groupby(GROUP_COLUMNS,
                      sort=False, as_index=False).sum())
    if not pieces:
        raise ValueError(f"{source.name}: no contiene notificaciones de municipios válidos")
    result = pd.concat(pieces, ignore_index=True).groupby(GROUP_COLUMNS, as_index=False).sum()
    result["nombre_municipio"] = result.codigo_municipio.map(names)
    result["codigo_departamento"] = result.codigo_municipio.str[:2]
    result["inicio_semana"] = [weeks[year, int(week)] for week in result.semana_epidemiologica]
    result["fin_semana"] = [start + timedelta(days=6) for start in result.inicio_semana]
    result["prop_notificados_fuera_municipio"] = (
        result.casos_notificados_otro_municipio / result.casos_total)
    leading = ["codigo_municipio", "nombre_municipio", "codigo_departamento",
               "ano_epidemiologico", "semana_epidemiologica", "inicio_semana", "fin_semana"]
    result = result[leading + [col for col in result if col not in leading]]
    result = result.sort_values(["ano_epidemiologico", "semana_epidemiologica",
                                 "codigo_municipio"]).reset_index(drop=True)
    if int(result.casos_total.sum()) != quality["registros_incluidos"]:
        raise ValueError("La agregación no conserva el total de notificaciones incluidas")
    quality["filas_municipio_semana"] = len(result)
    try:
        source_name = str(source.relative_to(ROOT))
    except ValueError:
        source_name = str(source)
    report = {"anio": year, "fuente": source_name,
              "criterio": f"ANO/SEMANA reportados; {RESIDENCE_CRITERION}",
              "conteos": dict(sorted(quality.items())),
              "codigos_residencia_excluidos": dict(excluded_codes.most_common())}
    return result, report


def saved_output_is_valid(output: Path, report_path: Path, year: int,
                          valid_codes: set[str]) -> bool:
    if not output.is_file() or not report_path.is_file():
        return False
    try:
        report = json.loads(report_path.read_text(encoding="utf-8"))
        frame = pd.read_parquet(output, columns=GROUP_COLUMNS + ["casos_total"])
        return (report["anio"] == year
                and report["criterio"] == f"ANO/SEMANA reportados; {RESIDENCE_CRITERION}"
                and not frame.empty
                and frame.ano_epidemiologico.eq(year).all()
                and frame.codigo_municipio.isin(valid_codes).all()
                and not frame.duplicated(GROUP_COLUMNS).any()
                and len(frame) == report["conteos"]["filas_municipio_semana"]
                and int(frame.casos_total.sum()) == report["conteos"]["registros_incluidos"])
    except (OSError, ValueError, KeyError, TypeError):
        return False


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start-year", type=int, default=2007)
    parser.add_argument("--end-year", type=int, default=2025)
    parser.add_argument("--input-dir", type=Path, default=INPUT)
    parser.add_argument("--output-dir", type=Path, default=OUTPUT)
    parser.add_argument("--divipola", type=Path, default=DIVIPOLA)
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args()
    if args.start_year < 2007 or args.end_year > 2025 or args.start_year > args.end_year:
        parser.error("El intervalo debe estar entre 2007 y 2025 y en orden ascendente")
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    names, all_codes = entity_names(args.divipola)
    weeks = {(year, number): start for year, number, start in
             weeks_in_range(args.start_year, args.end_year)}
    for year in range(args.start_year, args.end_year + 1):
        source = args.input_dir / f"Datos_{year}_831.csv"
        if not source.is_file():
            raise FileNotFoundError(source)
        output = args.output_dir / f"sivigila_weekly_municipal_{year}.parquet"
        report_path = args.output_dir / f"quality_report_{year}.json"
        LOGGER.info("%s: %s -> %s", year, source, output)
        if args.validate_only:
            with source.open(encoding="utf-8-sig") as file:
                columns = set(file.readline().strip().split(","))
            missing = set(SOURCE_COLUMNS) - columns
            if missing:
                raise ValueError(f"{source.name}: faltan columnas {sorted(missing)}")
            continue
        if not args.overwrite and saved_output_is_valid(output, report_path, year, set(names)):
            LOGGER.info("Ya existen Parquet e informe válidos; se omite %s", year)
            continue
        frame, report = process_year(source, year, names, all_codes, weeks)
        args.output_dir.mkdir(parents=True, exist_ok=True)
        part = output.with_name(output.name + ".part")
        report_part = report_path.with_name(report_path.name + ".part")
        try:
            frame.to_parquet(part, index=False)
            with report_part.open("w", encoding="utf-8") as file:
                json.dump(report, file, ensure_ascii=False, indent=2)
                file.write("\n")
            check = pd.read_parquet(part, columns=GROUP_COLUMNS + ["casos_total"])
            if len(check) != len(frame) or int(check.casos_total.sum()) != report["conteos"]["registros_incluidos"]:
                raise ValueError(f"{year}: Parquet temporal no supera la validación")
            part.replace(output)
            report_part.replace(report_path)
        finally:
            part.unlink(missing_ok=True)
            report_part.unlink(missing_ok=True)
        LOGGER.info("Guardado %s: %d filas, %d casos, %.1f MiB", output.name,
                    len(frame), int(frame.casos_total.sum()), output.stat().st_size / 2**20)


if __name__ == "__main__":
    main()
