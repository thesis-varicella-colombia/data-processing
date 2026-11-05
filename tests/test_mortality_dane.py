"""Valida la extracción de totales territoriales, excluyendo las causas."""

import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

import xlrd
import pandas as pd
from openpyxl import Workbook, load_workbook

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts/processing"))

from process_mortality_dane import (  # noqa: E402
    DEFAULT_INPUT, DEFAULT_INPUT_DIR, OUTPUT_COLUMNS, SOURCE_NAMES, VALUE_COLUMNS, YEARS,
    XlsxSheet, open_mortality_workbook, read_all_mortality, read_modern_sheet,
    read_mortality, read_sheet, validate_totals,
)


class MortalityExtractionTest(unittest.TestCase):
    def setUp(self):
        self.rows = [[""] * 27 for _ in range(12)]
        self.rows[7][0] = "AÑO 2008"
        self.rows[9][0] = "ANTIOQUIA"
        self.rows[10][2:27] = [
            "TOTAL", "Total", "", "", "Menor 1 año", "", "",
            "De 1-4 años", "", "", "De 5-14 años", "", "",
            "De 15-44 años", "", "", "De 45-64 años", "", "",
            "De 65 y más", "", "", "Edad desconocida", "", "",
        ]
        self.rows[11][3:27] = ["Hombres", "Mujeres", "Indeterminado"] * 8
        for label, cause, total in [
            ("TOTAL", "TOTAL", 10),
            ("", "101 ENFERMEDADES INFECCIOSAS INTESTINALES", 999),
            ("05001 MEDELLÍN", "TOTAL", 8),
            ("", "201 TUMOR MALIGNO DEL ESTOMAGO", 999),
            ("05999 SIN INFORMACIÓN", "TOTAL", 2),
        ]:
            self.rows.append([label, cause, total, *range(1, 25)])
        self.sheet = SimpleNamespace(
            name="05", nrows=len(self.rows), ncols=27,
            cell_value=lambda row, column: self.rows[row][column],
            row_values=lambda row, start, end: self.rows[row][start:end],
        )

    def test_keeps_territorial_totals_without_adding_cause_rows(self):
        frame = read_sheet(self.sheet)
        self.assertEqual(frame.columns.tolist(), OUTPUT_COLUMNS)
        self.assertEqual(frame["total"].tolist(), [10, 8, 2])
        self.assertEqual(frame["codigo_municipio"].tolist(), ["05", "05001", "-2"])
        self.assertEqual(frame["nombre_municipio"].tolist(), ["Total", "MEDELLÍN", "SIN INFORMACIÓN"])
        self.assertEqual(frame.loc[1, "total_hombres"], 1)
        self.assertEqual(frame.loc[1, "edad_menor_1_hombres"], 4)
        self.assertEqual(frame.loc[1, "edad_15_44_hombres"], 13)
        self.assertEqual(frame.loc[1, "edad_desconocida_indeterminado"], 24)

    def test_foreign_countries_use_special_code(self):
        self.sheet.name = "Extranjeros"
        self.rows[9][0] = "EXTRANJEROS"
        self.rows[14][0] = "75076 BRASIL"
        self.rows[16][0] = "75862 VENEZUELA"
        frame = read_sheet(self.sheet)
        self.assertTrue(frame["codigo_departamento"].isna().all())
        self.assertEqual(frame["codigo_municipio"].tolist(), ["-1"] * 3)
        self.assertEqual(frame["nombre_municipio"].tolist(), ["Total", "BRASIL", "VENEZUELA"])

    def test_rejects_wrong_municipal_prefix_and_shifted_headers(self):
        self.rows[14][0] = "08001 BARRANQUILLA"
        with self.assertRaisesRegex(ValueError, "no pertenece"):
            read_sheet(self.sheet)
        self.rows[10][6] = "Otra edad"
        with self.assertRaisesRegex(ValueError, "encabezados no reconocidos"):
            read_sheet(self.sheet)

    def test_total_comparison_ignores_other_counts_and_detects_wrong_sum(self):
        frame = read_sheet(self.sheet)
        result = validate_totals(frame)
        self.assertEqual(result.iloc[0]["estado"], "coincide")
        self.assertEqual(result.iloc[0]["diferencia"], 0)
        frame.loc[1, "total"] = 9
        with self.assertRaisesRegex(ValueError, "no coinciden"):
            validate_totals(frame)

    def test_rejects_incomplete_totals_duplicates_and_orphan_details(self):
        frame = read_sheet(self.sheet)
        missing = frame.copy()
        missing.loc[1, "total"] = None
        with self.assertRaisesRegex(ValueError, "incompletos"):
            validate_totals(missing)
        with self.assertRaisesRegex(ValueError, "más de una fila Total"):
            validate_totals(pd.concat([frame, frame.iloc[[0]]]))
        with self.assertRaisesRegex(ValueError, "sin fila Total"):
            validate_totals(frame.iloc[1:])

    def test_total_without_details_is_not_compared_to_zero(self):
        frame = read_sheet(self.sheet).iloc[[0]]
        result = validate_totals(frame)
        self.assertEqual(result.iloc[0]["estado"], "sin desglose")
        self.assertTrue(pd.isna(result.iloc[0]["diferencia"]))

    def test_year_is_checked_against_the_heading(self):
        with self.assertRaisesRegex(ValueError, "se esperaba el año 2009"):
            read_sheet(self.sheet, 2009)

    def set_expanded_age_groups(self, year):
        self.rows[7][0] = f"AÑO {year}"
        self.rows[10][21:24] = [
            "De 65-84 años", "", "", "De 85-99 años", "", "", "De 100 y más", "", "",
        ]
        self.rows[11][21:24] = ["Hombres", "Mujeres", "Indeterminado"] * 3
        for row in self.rows[12:]:
            row[21:24] = [10, 20, 30, 40, 50, 60, 70, 80, 90]
        self.sheet.ncols = 33

    def test_merges_older_ages_by_sex_without_shifting_unknown_age(self):
        for year in (2015, 2016):
            with self.subTest(year=year):
                self.setUp()
                self.set_expanded_age_groups(year)
                frame = read_sheet(self.sheet, year)
                self.assertEqual(frame.columns.tolist(), OUTPUT_COLUMNS)
                self.assertEqual(frame["total"].tolist(), [10, 8, 2])
                for sex, expected in zip(("hombres", "mujeres", "indeterminado"), (120, 150, 180)):
                    self.assertTrue(frame[f"edad_65_mas_{sex}"].eq(expected).all())
                self.assertEqual(frame.loc[1, "edad_45_64_hombres"], 16)
                self.assertEqual(frame.loc[1, "edad_desconocida_hombres"], 22)
                self.assertEqual(frame.loc[1, "edad_desconocida_indeterminado"], 24)

    def test_missing_older_age_component_produces_null_instead_of_partial_sum(self):
        self.set_expanded_age_groups(2015)
        self.rows[14][24] = ""  # Hombres de 85–99 del municipio.
        frame = read_sheet(self.sheet, 2015)
        self.assertTrue(pd.isna(frame.loc[1, "edad_65_mas_hombres"]))
        self.assertEqual(frame.loc[1, "edad_65_mas_mujeres"], 150)

    def test_shifted_headers_department_prefixes_and_preliminary_title(self):
        for year, offset in ((2017, 2), (2018, 1), (2019, 1)):
            with self.subTest(year=year):
                self.setUp()
                self.set_expanded_age_groups(year)
                self.rows[9][0] = "05 Antioquia"
                if year == 2019:
                    self.rows[7][0] = "Acumulado año 2019 preliminar – reportadas hasta el 31 de julio de 2020"
                self.rows[8:8] = [[""] * 33 for _ in range(offset)]
                self.sheet.nrows = len(self.rows)
                frame = read_sheet(self.sheet, year)
                self.assertEqual(frame.shape, (3, 30))
                self.assertTrue(frame["nombre_departamento"].eq("Antioquia").all())
                self.assertEqual(frame["codigo_municipio"].tolist(), ["05", "05001", "-2"])
                self.assertTrue(frame["edad_65_mas_hombres"].eq(120).all())
                self.assertTrue(frame["ano"].eq(year).all())

    def test_three_digit_country_codes_do_not_become_municipal_codes(self):
        self.set_expanded_age_groups(2018)
        self.sheet.name = "Extranjeros"
        self.rows[9][0] = "Extranjeros"
        self.rows[14][0] = "032 Argentina"
        self.rows[16][0] = "076 Brasil"
        frame = read_sheet(self.sheet, 2018)
        self.assertEqual(frame["nombre_municipio"].tolist(), ["Total", "Argentina", "Brasil"])
        self.assertTrue(frame["codigo_municipio"].eq("-1").all())
        self.assertTrue(frame["codigo_departamento"].isna().all())

    @unittest.skipUnless(DEFAULT_INPUT.is_file(), "Requiere cuadro5_2008.xls")
    def test_actual_workbook_totals_match_every_extracted_cell(self):
        frame = read_mortality(DEFAULT_INPUT)
        self.assertEqual(frame.shape, (1200, 30))
        self.assertTrue(frame["ano"].eq(2008).all())
        self.assertFalse(frame["codigo_municipio"].isna().any())
        workbook = xlrd.open_workbook(str(DEFAULT_INPUT), on_demand=True)
        expected = []
        try:
            for sheet in workbook.sheets():
                if sheet.name == "00":
                    continue
                for index in range(12, sheet.nrows):
                    if str(sheet.cell_value(index, 1)).strip().upper() == "TOTAL":
                        expected.append(sheet.row_values(index, 2, 27))
        finally:
            workbook.release_resources()
        self.assertEqual(frame[VALUE_COLUMNS].to_numpy().tolist(), expected)

    @unittest.skipUnless(
        all((DEFAULT_INPUT_DIR / name).is_file() for name in SOURCE_NAMES.values()),
        "Requiere los dieciocho archivos originales de 2008–2025",
    )
    def test_all_years_match_departmental_totals(self):
        frame = read_all_mortality(DEFAULT_INPUT_DIR)
        self.assertEqual(frame.columns.tolist(), OUTPUT_COLUMNS)
        self.assertEqual(set(frame["ano"]), set(YEARS))
        self.assertEqual(frame.shape, (21626, 30))
        validation = validate_totals(frame)
        self.assertEqual(len(validation), 35 * len(YEARS))
        for year in YEARS:
            with self.subTest(year=year):
                annual = validation.loc[validation["ano"].eq(year)]
                self.assertEqual(annual["estado"].eq("coincide").sum(), 34 if year == 2008 or year >= 2019 else 33)
                self.assertEqual(annual["estado"].eq("sin desglose").sum(), 1 if year == 2008 or year >= 2019 else 2)
                departments = annual.loc[
                    annual["codigo_departamento"].notna()
                    & annual["filas_desglose"].gt(0)
                ]
                self.assertTrue(departments["diferencia"].eq(0).all())

    @unittest.skipUnless(
        all((DEFAULT_INPUT_DIR / f"cuadro5_{year}.xls").is_file() for year in range(2015, 2020)),
        "Requiere cuadro5_2015.xls a cuadro5_2019.xls",
    )
    def test_expanded_workbooks_match_raw_age_sums_for_every_row(self):
        for year in range(2015, 2020):
            with self.subTest(year=year):
                source = DEFAULT_INPUT_DIR / f"cuadro5_{year}.xls"
                frame = read_mortality(source)
                workbook = xlrd.open_workbook(str(source), on_demand=True)
                expected = []
                try:
                    for sheet in workbook.sheets():
                        if sheet.name in {"00", "Indice"}:
                            continue
                        for index in range(12, sheet.nrows):
                            if str(sheet.cell_value(index, 1)).strip().upper() != "TOTAL":
                                continue
                            row = sheet.row_values(index, 0, 33)
                            older = [sum(row[column] for column in (21 + sex, 24 + sex, 27 + sex))
                                     for sex in range(3)]
                            expected.append([*row[2:21], *older, *row[30:33]])
                finally:
                    workbook.release_resources()
                self.assertEqual(frame[VALUE_COLUMNS].to_numpy().tolist(), expected)


class ModernMortalityTest(unittest.TestCase):
    def setUp(self):
        self.rows = [[""] * 36 for _ in range(10)]
        self.rows[4][2] = "Año 2020"
        self.rows[7][5:36] = [
            "TOTAL", "Total", "", "", "Menor 1 año", "", "",
            "De 1-4 años", "", "", "De 5-14 años", "", "",
            "De 15-44 años", "", "", "De 45-64 años", "", "",
            "De 65-84 años", "", "", "De 85-99 años", "", "",
            "De 100 y más", "", "", "Edad desconocida", "", "",
        ]
        self.rows[8][6:36] = ["Hombres", "Mujeres", "Indeterminado"] * 10
        self.rows[9][2:36] = ["Total Nacional", "", "TOTAL", 999, *range(1, 31)]
        for department, municipality, cause, total in [
            ("05 Antioquia", "Total Dpto", "TOTAL", 10),
            ("", "", "101 Causa específica", 999),
            ("", "05001 Medellín", "TOTAL", 8),
            ("", "Sin Información", "TOTAL", 2),
            ("08 Atlántico", "Total Dpto", "TOTAL", 7),
            ("", "08001 Barranquilla", "TOTAL", 7),
            ("Extranjero", "Total Dpto", "TOTAL", 3),
            ("", "862 Venezuela", "TOTAL", 3),
            ("Sin Información", "Total Dpto", "TOTAL", 1),
        ]:
            self.rows.append(["", "", department, municipality, cause, total, *range(1, 31)])
        self.rows.append(["", "", "Fuente: DANE", *([""] * 33)])
        self.sheet = SimpleNamespace(
            name="Cuadro5", nrows=len(self.rows), ncols=36,
            cell_value=lambda row, column: self.rows[row][column],
            row_values=lambda row, start, end: self.rows[row][start:end],
        )

    def test_selects_totals_and_propagates_departments_without_national_or_causes(self):
        frame = read_modern_sheet(self.sheet, 2020)
        self.assertEqual(frame.columns.tolist(), OUTPUT_COLUMNS)
        self.assertEqual(frame.shape, (8, 30))
        self.assertEqual(frame["total"].tolist(), [10, 8, 2, 7, 7, 3, 3, 1])
        self.assertEqual(frame["codigo_municipio"].tolist(),
                         ["05", "05001", "-2", "08", "08001", "-1", "-1", "-2"])
        self.assertEqual(frame["nombre_municipio"].tolist(),
                         ["Total", "Medellín", "Sin Información", "Total",
                          "Barranquilla", "Total", "Venezuela", "Total"])
        self.assertTrue(frame["codigo_departamento"].iloc[5:].isna().all())
        self.assertEqual(frame.loc[1, "total_hombres"], 1)
        self.assertEqual(frame.loc[1, "edad_65_mas_hombres"], 66)
        self.assertEqual(frame.loc[1, "edad_65_mas_mujeres"], 69)
        self.assertEqual(frame.loc[1, "edad_65_mas_indeterminado"], 72)
        self.assertEqual(frame.loc[1, "edad_desconocida_indeterminado"], 30)
        self.assertEqual(validate_totals(frame)["estado"].eq("coincide").sum(), 3)

    def test_total_mun_and_empty_department_total_labels_are_kept_in_2025(self):
        self.rows[4][2] = "Año 2025"
        for index in (10, 14, 16, 18):
            self.rows[index][3] = ""
        for index in (12, 13, 15):
            self.rows[index][4] = "TOTAL MUN"
        frame = read_modern_sheet(self.sheet, 2025)
        self.assertEqual(frame["total"].tolist(), [10, 8, 2, 7, 7, 3, 3, 1])
        self.assertEqual(validate_totals(frame)["estado"].eq("coincide").sum(), 3)

    def test_rejects_wrong_municipal_prefix_and_preserves_missing_age_component(self):
        self.rows[12][3] = "08001 Barranquilla"
        with self.assertRaisesRegex(ValueError, "no pertenece a 05"):
            read_modern_sheet(self.sheet, 2020)
        self.rows[12][3] = "05001 Medellín"
        self.rows[12][27] = ""
        frame = read_modern_sheet(self.sheet, 2020)
        self.assertTrue(pd.isna(frame.loc[1, "edad_65_mas_hombres"]))
        self.assertEqual(frame.loc[1, "edad_desconocida_hombres"], 28)

    def test_reads_xlsx_empty_cells_and_preserves_schema(self):
        self.rows[4][2] = "Año 2024"
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / SOURCE_NAMES[2024]
            workbook = Workbook()
            sheet = workbook.active
            sheet.title = "Cuadro5"
            for row in self.rows:
                sheet.append([None if value == "" else value for value in row])
            workbook.save(path)
            workbook.close()
            frame = read_mortality(path)
        self.assertEqual(frame.shape, (8, 30))
        self.assertTrue(frame["ano"].eq(2024).all())
        self.assertEqual(validate_totals(frame)["estado"].eq("coincide").sum(), 3)

    @unittest.skipUnless(
        all((DEFAULT_INPUT_DIR / SOURCE_NAMES[year]).is_file() for year in range(2020, 2026)),
        "Requiere los seis libros de 2020–2025",
    )
    def test_actual_modern_workbooks_match_raw_totals_and_age_sums(self):
        for year in range(2020, 2026):
            with self.subTest(year=year):
                source = DEFAULT_INPUT_DIR / SOURCE_NAMES[year]
                frame = read_mortality(source)
                if source.suffix == ".xlsx":
                    workbook = load_workbook(source, read_only=True, data_only=True)
                    sheet = XlsxSheet(workbook["Cuadro5"])
                else:
                    workbook = open_mortality_workbook(source)
                    sheet = workbook.sheet_by_name("Cuadro5")
                expected = []
                try:
                    for index in range(10, sheet.nrows):
                        row = sheet.row_values(index, 0, 36)
                        if str(row[4]).strip().casefold() not in {"total", "total mun"}:
                            continue
                        older = [sum(row[column] for column in (24 + sex, 27 + sex, 30 + sex))
                                 for sex in range(3)]
                        expected.append([*row[5:24], *older, *row[33:36]])
                finally:
                    if source.suffix == ".xlsx":
                        workbook.close()
                    else:
                        workbook.release_resources()
                self.assertEqual(frame[VALUE_COLUMNS].to_numpy().tolist(), expected)


if __name__ == "__main__":
    unittest.main()
