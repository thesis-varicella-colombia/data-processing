"""Comprueba los totales de nacimientos por año y departamento/categoría."""

import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

import pandas as pd
from openpyxl import Workbook

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts/processing"))

from process_births_dane import (  # noqa: E402
    DEFAULT_INPUT, OUTPUT_COLUMNS, SOURCE_NAMES, YEARS, read_all_births,
    read_births, read_modern_sheet, validate_totals,
)


class BirthsTotalsTest(unittest.TestCase):
    def setUp(self):
        self.frame = pd.DataFrame({
            "ano": [2008, 2008, 2008, 2009, 2009, 2009, 2008, 2008, 2008],
            "codigo_departamento": ["05"] * 6 + [None] * 3,
            "nombre_departamento": ["Antioquia"] * 6 + ["Extranjeros"] * 3,
            "nombre_municipio": ["Total", "Medellín", "Sin Información"] * 3,
            "total": pd.Series([10, 8, 2, 7, 6, 1, 3, 1, 2], dtype="Int64"),
            # La comparación debe ignorar el resto de conteos.
            "total_hombres": [999] * 9,
        })

    def test_totals_are_compared_per_year_including_special_categories(self):
        result = validate_totals(self.frame)
        self.assertEqual(len(result), 3)
        self.assertTrue(result["estado"].eq("coincide").all())
        self.assertTrue(result["diferencia"].eq(0).all())

    def test_detects_a_wrong_sum(self):
        self.frame.loc[1, "total"] = 9
        with self.assertRaisesRegex(ValueError, "no coinciden"):
            validate_totals(self.frame)

    def test_rejects_missing_values_duplicate_totals_and_orphan_details(self):
        missing = self.frame.copy()
        missing.loc[1, "total"] = pd.NA
        with self.assertRaisesRegex(ValueError, "incompletos"):
            validate_totals(missing)
        with self.assertRaisesRegex(ValueError, "más de una"):
            validate_totals(pd.concat([self.frame, self.frame.iloc[[0]]]))
        with self.assertRaisesRegex(ValueError, "sin fila Total"):
            validate_totals(self.frame.drop(index=0))

    def test_total_without_details_is_not_compared_to_zero(self):
        result = validate_totals(self.frame.iloc[[0]])
        self.assertEqual(result.iloc[0]["estado"], "sin desglose")
        self.assertTrue(pd.isna(result.iloc[0]["diferencia"]))

    @unittest.skipUnless(
        all((DEFAULT_INPUT / name).is_file() for name in SOURCE_NAMES.values()),
        "Requiere los dieciocho archivos originales DANE de 2008–2025",
    )
    def test_all_source_years_match_published_totals(self):
        frame = read_all_births(DEFAULT_INPUT)
        self.assertEqual(frame.columns.tolist(), OUTPUT_COLUMNS)
        self.assertEqual(set(frame["ano"]), set(YEARS))
        self.assertFalse(frame["codigo_municipio"].isna().any())
        self.assertFalse(frame["nombre_municipio"].eq("Total Nacional").any())
        result = validate_totals(frame)
        self.assertEqual(len(result), 35 * len(YEARS))
        for year in YEARS:
            annual = result.loc[result["ano"].eq(year)]
            self.assertEqual(annual["estado"].eq("coincide").sum(), 33 if year < 2020 else 34)
            self.assertEqual(annual["estado"].eq("sin desglose").sum(), 2 if year < 2020 else 1)
        modern_municipalities = frame.loc[
            frame["ano"].ge(2020) & frame["codigo_municipio"].str.fullmatch(r"\d{5}")
        ]
        self.assertTrue(modern_municipalities["codigo_municipio"].str[:2].eq(
            modern_municipalities["codigo_departamento"]
        ).all())


class ModernBirthsSheetTest(unittest.TestCase):
    def setUp(self):
        self.rows = [[""] * 20 for _ in range(10)]
        self.rows[4][2] = "Año 2020"
        self.rows[7][2] = "Departamento y municipio de residencia de la madre"
        self.rows[7][4:20] = [
            "Total", "Total", "", "", "Cabecera municipal", "", "",
            "Centro poblado", "", "", "Rural disperso", "", "",
            "Sin información", "", "",
        ]
        self.rows[8][5:20] = ["Hombres", "Mujeres", "Indeterminado"] * 5
        self.rows[9][2:20] = ["Total Nacional", "", 999, *range(1, 16)]
        for department, municipality, total in [
            ("05 Antioquia", "Total", 10),
            ("", "05001 Medellín", 8),
            ("", "Sin Información", 2),
            ("08 Atlántico", "Total", 7),
            ("", "08001 Barranquilla", 7),
            ("Extranjero", "Total", 3),
            ("", "862 Venezuela", 3),
            ("Sin Información", "Total", 1),
        ]:
            self.rows.append(["", "", department, municipality, total, *range(1, 16)])
        self.rows.append(["", "", "Fuente: DANE", *([""] * 17)])
        self.sheet = SimpleNamespace(
            name="Cuadro3", nrows=len(self.rows), ncols=20,
            cell_value=lambda row, column: self.rows[row][column],
            row_values=lambda row, start, end: self.rows[row][start:end],
        )

    def test_maps_departments_municipalities_special_codes_and_counts(self):
        frame = read_modern_sheet(self.sheet, 2020)
        self.assertEqual(frame.columns.tolist(), OUTPUT_COLUMNS)
        self.assertEqual(len(frame), 8)  # Excluye el total nacional y la nota.
        self.assertEqual(frame["codigo_municipio"].tolist(),
                         ["05", "05001", "-2", "08", "08001", "-1", "-1", "-2"])
        self.assertEqual(frame["nombre_municipio"].tolist(),
                         ["Total", "Medellín", "Sin Información", "Total",
                          "Barranquilla", "Total", "Venezuela", "Total"])
        self.assertEqual(frame["codigo_departamento"].iloc[:5].tolist(),
                         ["05", "05", "05", "08", "08"])
        self.assertTrue(frame["codigo_departamento"].iloc[5:].isna().all())
        self.assertEqual(frame["nombre_departamento"].iloc[:3].tolist(), ["Antioquia"] * 3)
        expected_counts = {
            "total": 10, "total_hombres": 1, "total_mujeres": 2,
            "total_indeterminado": 3,
            "cabecera_municipal_hombres": 4, "cabecera_municipal_mujeres": 5,
            "cabecera_municipal_indeterminado": 6,
            "centro_poblado_hombres": 7, "centro_poblado_mujeres": 8,
            "centro_poblado_indeterminado": 9,
            "rural_disperso_hombres": 10, "rural_disperso_mujeres": 11,
            "rural_disperso_indeterminado": 12,
            "sin_informacion_hombres": 13, "sin_informacion_mujeres": 14,
            "sin_informacion_indeterminado": 15,
        }
        self.assertEqual(frame.iloc[0][list(expected_counts)].to_dict(), expected_counts)
        result = validate_totals(frame)
        self.assertEqual(result["estado"].eq("coincide").sum(), 3)
        self.assertEqual(result["estado"].eq("sin desglose").sum(), 1)

    def test_rejects_municipality_from_another_department(self):
        self.rows[11][3] = "08001 Barranquilla"
        with self.assertRaisesRegex(ValueError, "no pertenece al departamento 05"):
            read_modern_sheet(self.sheet, 2020)

    def test_rejects_year_that_disagrees_with_the_heading(self):
        with self.assertRaisesRegex(ValueError, "año del encabezado"):
            read_modern_sheet(self.sheet, 2021)

    def test_normalizes_total_dpto_for_departments_and_special_categories(self):
        for index in (10, 13, 15, 17):
            self.rows[index][3] = "Total Dpto"
        for year in (2023, 2024, 2025):
            with self.subTest(year=year):
                self.rows[4][2] = f"Año {year}"
                frame = read_modern_sheet(self.sheet, year)
                totals = frame.loc[frame["nombre_municipio"].eq("Total")]
                self.assertEqual(len(totals), 4)
                self.assertEqual(totals["codigo_municipio"].tolist(), ["05", "08", "-1", "-2"])
                self.assertEqual(validate_totals(frame)["estado"].eq("coincide").sum(), 3)

    def test_reads_xlsx_with_empty_cells_and_total_dpto(self):
        self.rows[4][2] = "Año 2025"
        for index in (10, 13, 15, 17):
            self.rows[index][3] = "Total Dpto"
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / SOURCE_NAMES[2025]
            workbook = Workbook()
            sheet = workbook.active
            sheet.title = "Cuadro3"
            for row in self.rows:
                sheet.append([None if value == "" else value for value in row])
            # Simula las filas vacías con formato de los archivos DANE.
            sheet.cell(100, 20).number_format = "0"
            workbook.save(path)
            workbook.close()
            frame = read_births(path)
        self.assertEqual(frame.shape, (8, len(OUTPUT_COLUMNS)))
        self.assertTrue(frame["ano"].eq(2025).all())
        self.assertEqual(frame["codigo_municipio"].tolist(),
                         ["05", "05001", "-2", "08", "08001", "-1", "-1", "-2"])
        self.assertEqual(validate_totals(frame)["estado"].eq("coincide").sum(), 3)


if __name__ == "__main__":
    unittest.main()
