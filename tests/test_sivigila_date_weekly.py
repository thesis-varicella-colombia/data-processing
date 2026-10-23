"""Valida agrupación por fechas, cruces de año y fechas faltantes."""

import csv
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts/processing"))

from calculate_date_weekly_sivigila import (  # noqa: E402
    finish_year, process_source_year, symptom_date, week_keys,
)
from calculate_weekly_sivigila import SOURCE_COLUMNS  # noqa: E402


def test_week_keys_crosses_epidemiological_year():
    dates = pd.to_datetime(pd.Series(["2024-12-28", "2024-12-29",
                                      "2025-01-04", "2025-01-05"]))
    keys = week_keys(dates)
    assert list(zip(keys.ano_epidemiologico, keys.semana_epidemiologica)) == [
        (2024, 52), (2025, 1), (2025, 1), (2025, 2),
    ]


def test_notification_keeps_case_without_onset_and_symptom_excludes_it(tmp_path):
    source = tmp_path / "Datos_2025_831.csv"
    rows = []
    for notification, onset in [
        ("3/01/2025", "1/01/2025"),
        ("5/01/2025", "1/01/2025"),
        ("5/01/2025", ""),
    ]:
        row = {column: "" for column in SOURCE_COLUMNS}
        row.update({"ANO": "2025", "SEMANA": "1", "COD_EVE": "831",
                    "COD_DPTO_R": "11", "COD_MUN_R": "001", "AJUSTE": "0",
                    "FEC_NOT": notification, "INI_SIN": onset})
        rows.append(row)
    with source.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=SOURCE_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    names = {"11001": "BOGOTÁ"}
    notification, n_quality = process_source_year(source, 2025, "notification", names)
    symptom, s_quality = process_source_year(source, 2025, "symptom", names)
    assert n_quality["registros_agrupados"] == 3
    assert n_quality["sin_fecha_para_agrupacion"] == 0
    assert s_quality["registros_agrupados"] == 2
    assert s_quality["sin_fecha_para_agrupacion"] == 1
    assert notification.casos_total.sum() == 3
    assert notification.semana_epidemiologica.tolist() == [1, 2]
    assert symptom.casos_total.sum() == 2
    assert symptom.semana_epidemiologica.tolist() == [1]
    finished = finish_year(notification, names)
    assert finished.columns.tolist()[0:7] == [
        "codigo_municipio", "nombre_municipio", "codigo_departamento",
        "ano_epidemiologico", "semana_epidemiologica", "inicio_semana",
        "fin_semana",
    ]


def test_2013_symptom_date_uses_month_first():
    dates = symptom_date(pd.Series(["12/05/2013", ""]), 2013)
    assert dates.iloc[0] == pd.Timestamp("2013-12-05")
    assert pd.isna(dates.iloc[1])
