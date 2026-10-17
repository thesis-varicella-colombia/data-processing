"""Comprueba los conteos semanales y su equivalencia con las reglas del notebook."""

import csv
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts/processing"))

from calculate_weekly_sivigila import (  # noqa: E402
    SOURCE_COLUMNS, add_metrics, entity_names, process_year,
)
from epidemiological_weeks import weeks_in_range  # noqa: E402
import pandas as pd


def test_hospitalization_matches_notebook_boolean_conversion():
    rows = pd.DataFrame({"PAC_HOS": ["1", "2", "", "1.0"]})
    for column in SOURCE_COLUMNS:
        if column not in rows:
            rows[column] = ""
    rows["codigo_municipio"] = "11001"
    rows["inicio_semana_reportada"] = pd.Timestamp("2024-12-29")
    assert add_metrics(rows, set())["casos_hospitalizados"].tolist() == [1, 0, 0, 0]


def test_age_groups_follow_requested_boundaries():
    ages = ["11", "12", "59", "60", "4", "5", "14", "15", "49", "50", "130", "0"]
    units = ["2", "2", "2", "2"] + ["1"] * 7 + ["0"]
    rows = pd.DataFrame({"EDAD": ages, "UNI_MED": units})
    for column in SOURCE_COLUMNS:
        if column not in rows:
            rows[column] = ""
    rows["codigo_municipio"] = "11001"
    rows["inicio_semana_reportada"] = pd.Timestamp("2024-12-29")
    metrics = add_metrics(rows, set())
    expected = {
        "casos_menor_1": [0],
        "casos_1_4": [1, 2, 4],
        "casos_5_14": [3, 5, 6],
        "casos_15_49": [7, 8],
        "casos_50_mas": [9, 10],
        "casos_edad_desconocida": [11],
    }
    for column, indexes in expected.items():
        assert metrics.index[metrics[column].eq(1)].tolist() == indexes


def test_weekly_counts_preserve_reported_fields_and_unknowns():
    with tempfile.TemporaryDirectory() as directory:
        check_weekly_counts(Path(directory))


def test_divipola_includes_all_entity_types():
    with tempfile.TemporaryDirectory() as directory:
        divipola = Path(directory) / "divipola.csv"
        with divipola.open("w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=[
                "Código Municipio", "Nombre Municipio",
                "Tipo: Municipio / Isla / Área no municipalizada",
            ])
            writer.writeheader()
            writer.writerows([
                {"Código Municipio": "11001", "Nombre Municipio": "BOGOTÁ",
                 "Tipo: Municipio / Isla / Área no municipalizada": "Municipio"},
                {"Código Municipio": "88001", "Nombre Municipio": "SAN ANDRÉS",
                 "Tipo: Municipio / Isla / Área no municipalizada": "Isla"},
                {"Código Municipio": "27493", "Nombre Municipio": "NUEVO BELÉN DE BAJIRÁ",
                 "Tipo: Municipio / Isla / Área no municipalizada": "Municipio"},
                {"Código Municipio": "91405", "Nombre Municipio": "LA CHORRERA",
                 "Tipo: Municipio / Isla / Área no municipalizada": "Área no municipalizada"},
                {"Código Municipio": "91540", "Nombre Municipio": "OTRA ÁREA",
                 "Tipo: Municipio / Isla / Área no municipalizada": "Área no municipalizada"},
                {"Código Municipio": "94343", "Nombre Municipio": "BARRANCOMINAS",
                 "Tipo: Municipio / Isla / Área no municipalizada": "Municipio"},
            ])
        names, all_codes = entity_names(divipola)
        assert set(names) == {"11001", "27493", "88001", "91405", "91540", "94343"}
        assert "94663" not in all_codes
        assert all_codes == set(names)


def check_weekly_counts(tmp_path):
    source = tmp_path / "Datos_2025_831.csv"
    rows = []
    for overrides in [
        {"COD_DPTO_R": "11", "COD_MUN_R": "001", "COD_MUN_N": "05001",
         "SEXO": "F", "PAC_HOS": "2", "UNI_MED": "", "EDAD": "",
         "CON_FIN": "1", "FEC_DEF": "2/01/2025", "GP_GESTAN": "2"},
        {"COD_DPTO_R": "11", "COD_MUN_R": "001", "COD_MUN_N": "11001",
         "SEXO": "M", "PAC_HOS": "1", "UNI_MED": "2", "EDAD": "2",
         "CON_FIN": "2", "FM_UNIDAD": "123", "GP_GESTAN": "1"},
        {"COD_DPTO_R": "00", "COD_MUN_R": "000", "COD_MUN_N": "11001",
         "SEXO": "F", "PAC_HOS": "1", "UNI_MED": "1", "EDAD": "30"},
        {"COD_DPTO_R": "27", "COD_MUN_R": "086", "COD_MUN_N": "27086",
         "COD_PAIS_O": "170", "COD_DPTO_O": "27", "COD_MUN_O": "086",
         "SEXO": "F", "UNI_MED": "1", "EDAD": "30"},
        {"COD_DPTO_R": "94", "COD_MUN_R": "663", "COD_MUN_N": "94663",
         "COD_PAIS_O": "170", "COD_DPTO_O": "94", "COD_MUN_O": "663",
         "SEXO": "F", "UNI_MED": "1", "EDAD": "30"},
        {"COD_DPTO_R": "94", "COD_MUN_R": "343", "COD_MUN_N": "94343",
         "COD_PAIS_O": "170", "COD_DPTO_O": "94", "COD_MUN_O": "343",
         "SEXO": "F", "UNI_MED": "1", "EDAD": "30"},
        {"COD_DPTO_R": "88", "COD_MUN_R": "000", "COD_MUN_N": "88000",
         "COD_PAIS_O": "170", "COD_DPTO_O": "88", "COD_MUN_O": "000",
         "SEXO": "F", "UNI_MED": "1", "EDAD": "30"},
        {"COD_DPTO_R": "88", "COD_MUN_R": "001", "COD_MUN_N": "88001",
         "COD_PAIS_O": "170", "COD_DPTO_O": "88", "COD_MUN_O": "001",
         "SEXO": "F", "UNI_MED": "1", "EDAD": "30"},
    ]:
        row = {column: "" for column in SOURCE_COLUMNS}
        row.update({"ANO": "2025", "SEMANA": "1", "COD_EVE": "831",
                    "AJUSTE": "0", "FEC_NOT": "3/01/2025 12:00:00 a. m.",
                    "INI_SIN": "1/01/2025 12:00:00 a. m."})
        row.update(overrides)
        rows.append(row)
    with source.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=SOURCE_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)

    weeks = {(year, number): start for year, number, start in weeks_in_range(2025, 2025)}
    result, report = process_year(source, 2025,
                                  {"11001": "BOGOTÁ", "05001": "MEDELLÍN",
                                   "27493": "NUEVO BELÉN DE BAJIRÁ",
                                   "94343": "BARRANCOMINAS", "88001": "SAN ANDRÉS"},
                                  {"11001", "05001", "27493", "94343", "88001"}, weeks)
    row = result.loc[result.codigo_municipio.eq("11001")].iloc[0]
    assert row.codigo_municipio == "11001"
    assert row.casos_total == 2
    assert row.casos_hospitalizados == 1
    assert row.casos_edad_desconocida == 1
    assert row.casos_menor_1 == 1
    assert row.casos_notificados_mismo_municipio == 1
    assert row.casos_notificados_otro_municipio == 1
    assert row.casos_fallecidos == 1
    assert row.casos_fuerzas_armadas == 1
    assert row.casos_gestantes == 1
    assert report["conteos"]["excluidos_codigo_residencia_desconocido"] == 1
    assert report["conteos"]["evidencia_defuncion_sin_CON_FIN_2"] == 1
    assert report["conteos"]["CON_FIN_2_sin_fecha_ni_causa"] == 1
    belen = result.loc[result.codigo_municipio.eq("27493")].iloc[0]
    assert belen.casos_total == 1
    assert belen.casos_notificados_mismo_municipio == 1
    assert belen.casos_ocurrencia_mismo_municipio_residencia == 1
    assert report["conteos"]["homologados_27086_a_27493"] == 1
    barrancominas = result.loc[result.codigo_municipio.eq("94343")].iloc[0]
    assert barrancominas.casos_total == 2
    assert barrancominas.casos_notificados_mismo_municipio == 2
    assert barrancominas.casos_ocurrencia_mismo_municipio_residencia == 2
    assert report["conteos"]["homologados_94663_a_94343"] == 1
    san_andres = result.loc[result.codigo_municipio.eq("88001")].iloc[0]
    assert san_andres.casos_total == 2
    assert san_andres.casos_notificados_mismo_municipio == 2
    assert san_andres.casos_ocurrencia_mismo_municipio_residencia == 2
    assert report["conteos"]["homologados_88000_a_88001"] == 1


if __name__ == "__main__":
    test_weekly_counts_preserve_reported_fields_and_unknowns()
    test_divipola_includes_all_entity_types()
