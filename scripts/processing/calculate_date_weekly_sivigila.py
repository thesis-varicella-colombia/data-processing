"""Agrega los casos de varicela por semana de notificación o de síntomas.

Conserva las mismas entidades, indicadores y reglas de inclusión del agregado
por ANO/SEMANA del CSV. Las semanas de salida se calculan desde FEC_NOT o
INI_SIN con el calendario epidemiológico del proyecto.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import timedelta
from pathlib import Path

import pandas as pd

from calculate_weekly_sivigila import (
    CHUNK_SIZE, DIVIPOLA, GEOGRAPHIC_CODE_ALIASES, GROUP_COLUMNS, INPUT,
    OUTPUT, SOURCE_COLUMNS, add_metrics, entity_names, number, read_date,
)
from epidemiological_weeks import week_one_start, weeks_in_range


MODES = {"notification": "FEC_NOT", "symptom": "INI_SIN"}


def symptom_date(series: pd.Series, source_year: int) -> pd.Series:
    """El CSV de 2013 guarda INI_SIN como mes/día/año."""
    if source_year != 2013:
        return read_date(series)
    first = series.str.extract(r"^(\d{1,2}/\d{1,2}/\d{4})", expand=False)
    return pd.to_datetime(first, format="%m/%d/%Y", errors="coerce")


def week_keys(dates: pd.Series) -> pd.DataFrame:
    """Devuelve año, semana e inicio según domingo-sábado, incluso en bordes."""
    if dates.isna().any():
        raise ValueError("No se pueden asignar semanas a fechas nulas")
    calendar_year = dates.dt.year
    starts = {year: pd.Timestamp(week_one_start(year)) for year in
              range(int(calendar_year.min()) - 1, int(calendar_year.max()) + 2)}
    first = calendar_year.map(starts)
    next_first = (calendar_year + 1).map(starts)
    epi_year = calendar_year.where(dates.ge(first), calendar_year - 1)
    epi_year = epi_year.where(dates.lt(next_first), calendar_year + 1)
    epi_start = epi_year.map(starts)
    epi_week = ((dates - epi_start).dt.days // 7 + 1).astype("int16")
    return pd.DataFrame({
        "ano_epidemiologico": epi_year.astype("int64"),
        "semana_epidemiologica": epi_week,
    }, index=dates.index)


def process_source_year(source: Path, source_year: int, mode: str,
                        names: dict[str, str]) -> tuple[pd.DataFrame, dict]:
    """Agrega un CSV anual por la semana de la fecha elegida."""
    if mode not in MODES:
        raise ValueError(f"Modo desconocido: {mode}")
    valid = set(names)
    reported_starts = {week: pd.Timestamp(start) for _, week, start in
                       weeks_in_range(source_year, source_year)}
    quality: Counter[str] = Counter()
    pieces = []
    for chunk in pd.read_csv(source, dtype=str, keep_default_na=False,
                             usecols=SOURCE_COLUMNS, chunksize=CHUNK_SIZE,
                             encoding="utf-8-sig"):
        quality["registros_entrada"] += len(chunk)
        if not number(chunk.ANO).eq(source_year).all():
            raise ValueError(f"{source.name}: ANO no coincide con {source_year}")
        if not number(chunk.COD_EVE).eq(831).all():
            raise ValueError(f"{source.name}: contiene eventos distintos de 831")
        reported_week = number(chunk.SEMANA)
        if not reported_week.isin(reported_starts).all():
            raise ValueError(f"{source.name}: SEMANA fuera de calendario")

        raw_code = (chunk.COD_DPTO_R.str.strip().str.zfill(2)
                    + chunk.COD_MUN_R.str.strip().str.zfill(3))
        code = raw_code.replace(GEOGRAPHIC_CODE_ALIASES)
        adjustment = chunk.AJUSTE.str.strip().str.upper()
        included = code.isin(valid) & ~adjustment.isin(["6", "D"])
        quality["registros_incluidos_fuente"] += int(included.sum())
        chunk = chunk.loc[included].copy()
        if chunk.empty:
            continue
        chunk["codigo_municipio"] = code.loc[included]
        chunk["inicio_semana_reportada"] = reported_week.loc[included].map(reported_starts)
        notified = read_date(chunk.FEC_NOT)
        onset = symptom_date(chunk.INI_SIN, source_year)
        selected_date = notified if mode == "notification" else onset
        quality["sin_fecha_para_agrupacion"] += int(selected_date.isna().sum())
        available = selected_date.notna()
        if not available.any():
            continue
        chunk = chunk.loc[available]
        notified = notified.loc[available]
        onset = onset.loc[available]
        selected_date = selected_date.loc[available]
        keys = week_keys(selected_date)
        keys["codigo_municipio"] = chunk.codigo_municipio
        metrics = add_metrics(chunk, valid, notification_date=notified,
                              symptom_date=onset)
        pieces.append(pd.concat([keys, metrics], axis=1)
                      .groupby(GROUP_COLUMNS, as_index=False, sort=False).sum())
        quality["registros_agrupados"] += len(chunk)
    if not pieces:
        raise ValueError(f"{source.name}: no hay fechas para agrupar por {mode}")
    frame = (pd.concat(pieces, ignore_index=True)
             .groupby(GROUP_COLUMNS, as_index=False).sum())
    if int(frame.casos_total.sum()) != quality["registros_agrupados"]:
        raise ValueError(f"{source.name}: la agregación no conserva los casos")
    quality.setdefault("sin_fecha_para_agrupacion", 0)
    return frame, dict(sorted(quality.items()))


def finish_year(frame: pd.DataFrame, names: dict[str, str]) -> pd.DataFrame:
    """Reconstruye las columnas y el orden del agregado semanal de origen."""
    frame = frame.copy()
    frame["nombre_municipio"] = frame.codigo_municipio.map(names)
    frame["codigo_departamento"] = frame.codigo_municipio.str[:2]
    starts = {(year, week): start for year in frame.ano_epidemiologico.unique()
              for _, week, start in weeks_in_range(int(year), int(year))}
    frame["inicio_semana"] = [starts[int(year), int(week)] for year, week in
                              zip(frame.ano_epidemiologico, frame.semana_epidemiologica)]
    frame["fin_semana"] = [start + timedelta(days=6) for start in frame.inicio_semana]
    frame["prop_notificados_fuera_municipio"] = (
        frame.casos_notificados_otro_municipio / frame.casos_total)
    leading = ["codigo_municipio", "nombre_municipio", "codigo_departamento",
               "ano_epidemiologico", "semana_epidemiologica", "inicio_semana",
               "fin_semana"]
    frame = frame[leading + [col for col in frame if col not in leading]]
    return frame.sort_values(["ano_epidemiologico", "semana_epidemiologica",
                              "codigo_municipio"]).reset_index(drop=True)


def process_mode(mode: str, input_dir: Path, output_dir: Path,
                 names: dict[str, str], start_year: int, end_year: int) -> dict:
    """Une años de origen y escribe un archivo por año epidemiológico calculado."""
    pieces = []
    source_quality = {}
    for source_year in range(start_year, end_year + 1):
        source = input_dir / f"Datos_{source_year}_831.csv"
        if not source.is_file():
            raise FileNotFoundError(source)
        frame, quality = process_source_year(source, source_year, mode, names)
        pieces.append(frame)
        source_quality[str(source_year)] = quality
    combined = (pd.concat(pieces, ignore_index=True)
                .groupby(GROUP_COLUMNS, as_index=False).sum())
    expected = sum(q["registros_agrupados"] for q in source_quality.values())
    if int(combined.casos_total.sum()) != expected:
        raise ValueError(f"{mode}: pérdida de casos entre años de origen")

    destination = output_dir / f"{mode}_weekly_municipal"
    destination.mkdir(parents=True, exist_ok=True)
    output_quality = {}
    for epi_year, part in combined.groupby("ano_epidemiologico", sort=True):
        year = int(epi_year)
        frame = finish_year(part, names)
        output = destination / f"sivigila_{mode}_weekly_municipal_{year}.parquet"
        temporary = output.with_name(output.name + ".part")
        try:
            frame.to_parquet(temporary, index=False)
            check = pd.read_parquet(temporary, columns=GROUP_COLUMNS + ["casos_total"])
            if (len(check) != len(frame) or check.duplicated(GROUP_COLUMNS).any()
                    or int(check.casos_total.sum()) != int(frame.casos_total.sum())):
                raise ValueError(f"{output.name}: validación del Parquet falló")
            temporary.replace(output)
        finally:
            temporary.unlink(missing_ok=True)
        output_quality[str(year)] = {"filas_municipio_semana": len(frame),
                                     "casos_total": int(frame.casos_total.sum())}
        print(f"{mode} {year}: {len(frame):,} filas, {int(frame.casos_total.sum()):,} casos")
    report = {"semana_basada_en": MODES[mode],
              "anio_archivo": "año epidemiológico calculado desde la fecha",
              "fuentes_por_ano_reportado": source_quality,
              "salidas_por_ano_epidemiologico": output_quality,
              "registros_agrupados": expected,
              "sin_fecha_para_agrupacion": sum(
                  q.get("sin_fecha_para_agrupacion", 0) for q in source_quality.values())}
    report_dir = destination / "quality_report"
    report_dir.mkdir(exist_ok=True)
    report_path = report_dir / "summary.json"
    temporary = report_path.with_name(report_path.name + ".part")
    try:
        temporary.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n",
                             encoding="utf-8")
        temporary.replace(report_path)
    finally:
        temporary.unlink(missing_ok=True)
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=["notification", "symptom", "both"],
                        default="both")
    parser.add_argument("--start-year", type=int, default=2007)
    parser.add_argument("--end-year", type=int, default=2025)
    parser.add_argument("--input-dir", type=Path, default=INPUT)
    parser.add_argument("--output-dir", type=Path, default=OUTPUT)
    parser.add_argument("--divipola", type=Path, default=DIVIPOLA)
    args = parser.parse_args()
    if args.start_year < 2007 or args.end_year > 2025 or args.start_year > args.end_year:
        parser.error("El intervalo debe estar entre 2007 y 2025 y en orden ascendente")
    names, _ = entity_names(args.divipola)
    modes = MODES if args.mode == "both" else [args.mode]
    for mode in modes:
        process_mode(mode, args.input_dir, args.output_dir, names,
                     args.start_year, args.end_year)


if __name__ == "__main__":
    main()
