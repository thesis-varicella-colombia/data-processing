"""Comprueba la unión territorial y el saldo del año calendario anterior."""

import json
from pathlib import Path
import sys
import tempfile
import unittest

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts/processing"))

from integrate_surviving_infants import (  # noqa: E402
    OUTPUT_COLUMNS, integrate_frames, process,
)


def births(rows):
    return pd.DataFrame(rows, columns=[
        "ano", "codigo_departamento", "nombre_departamento",
        "codigo_municipio", "nombre_municipio", "total",
    ])


def mortality(rows):
    frame = pd.DataFrame(rows, columns=[
        "ano", "codigo_departamento", "nombre_departamento",
        "codigo_municipio", "nombre_municipio",
        "edad_menor_1_hombres", "edad_menor_1_mujeres",
    ])
    frame["edad_menor_1_indeterminado"] = 999
    return frame


class SurvivingInfantsTest(unittest.TestCase):
    def test_previous_year_exactly_and_join_ignores_name_differences(self):
        b = births([
            (2009, "05", "Antioquia", "05001", "Medellín", 100),
            (2010, "05", "Antioquia", "05001", "Medellín", 200),
            (2009, "05", "Antioquia", "05", " Total ", 10000),
        ])
        m = mortality([
            (2009, "05", "ANTIOQUIA", "05001", "MEDELLIN", 2, 3),
            (2010, "05", "ANTIOQUIA", "05001", "MEDELLIN", 20, 30),
            (2009, "05", "Antioquia", "05", "TOTAL", 200, 300),
        ])
        result, audit, report = integrate_frames(b, m)
        self.assertEqual(result.columns.tolist(), OUTPUT_COLUMNS)
        self.assertEqual(len(result), 2)
        self.assertTrue(audit.empty)
        self.assertEqual(report["totales_excluidos"], {"births": 1, "mortality": 1})
        self.assertTrue(pd.isna(result.iloc[0]["sobrevivientes_edad_1"]))
        self.assertEqual(result.iloc[1]["sobrevivientes_edad_1"], 95)
        self.assertEqual(result.iloc[1]["total_defunciones_menor_1"], 50)
        self.assertEqual(result.iloc[1]["nombre_municipio"], "Medellín")
        self.assertEqual(result["codigo_municipio"].tolist(), ["05001", "05001"])
        self.assertEqual(result["ano"].max(), 2010)  # No inventa un año adicional.

    def test_missing_calendar_year_is_not_replaced_by_previous_available_row(self):
        b = births([(year, "05", "Antioquia", "05001", "Medellín", 100)
                    for year in (2008, 2010)])
        m = mortality([(year, "05", "Antioquia", "05001", "Medellín", 1, 2)
                       for year in (2008, 2010)])
        result, _, _ = integrate_frames(b, m)
        self.assertTrue(result["sobrevivientes_edad_1"].isna().all())

    def test_unmatched_rows_remain_and_complete_previous_year_can_supply_survivors(self):
        b = births([
            (2009, "05", "Antioquia", "05001", "Medellín", 100),
            (2010, "05", "Antioquia", "05001", "Medellín", 110),
            (2010, "08", "Atlántico", "08001", "Barranquilla", 500),
        ])
        m = mortality([
            (2009, "05", "Antioquia", "05001", "Medellín", 1, 2),
            (2010, "11", "Bogotá", "11001", "Bogotá", 3, 4),
        ])
        result, audit, report = integrate_frames(b, m)
        self.assertEqual(len(result), 4)
        self.assertEqual(report["filas_con_join"], 1)
        self.assertEqual(report["filas_sin_join"]["births"]["sin_correspondencia"], 0)
        self.assertEqual(report["filas_sin_join"]["mortality"]["sin_correspondencia"], 1)
        self.assertEqual(len(audit), 1)
        self.assertEqual(report["filas_mortality_asumidas_cero"], 2)
        city = result.loc[result.ano.eq(2010) & result.codigo_municipio.eq("05001")].iloc[0]
        self.assertEqual(city["total_defunciones_menor_1"], 0)
        self.assertEqual(city["sobrevivientes_edad_1"], 97)

    def test_missing_mortality_is_zero_in_previous_year_subtraction(self):
        b = births([(year, "05", "Antioquia", "05001", "Medellín", 100)
                    for year in (2009, 2010)])
        m = mortality([(2010, "05", "Antioquia", "05001", "Medellín", 2, 3)])
        result, audit, report = integrate_frames(b, m)
        self.assertEqual(result.iloc[0]["total_defunciones_menor_1"], 0)
        self.assertEqual(result.iloc[1]["sobrevivientes_edad_1"], 100)
        self.assertTrue(audit.empty)
        self.assertEqual(report["filas_mortality_asumidas_cero"], 1)

    def test_null_department_countries_do_not_match_or_multiply(self):
        b = births([(2009, None, "Extranjeros", "-1", country, 10)
                    for country in ("Brasil", "Perú")])
        m = mortality([(2009, None, "Extranjeros", "-1", country, 1, 1)
                       for country in ("Brasil", "Perú")])
        result, audit, report = integrate_frames(b, m)
        self.assertEqual(len(result), 4)
        self.assertEqual(len(audit), 4)
        self.assertTrue(audit.motivo.eq("clave_incompleta").all())
        self.assertEqual(report["filas_con_join"], 0)
        self.assertTrue(result["sobrevivientes_edad_1"].isna().all())

    def test_incomplete_infant_count_stays_null_and_negative_balance_is_preserved(self):
        b = births([(year, "05", "Antioquia", "05001", "Medellín", 1)
                    for year in (2009, 2010, 2011)])
        m = mortality([
            (2009, "05", "Antioquia", "05001", "Medellín", 2, 3),
            (2010, "05", "Antioquia", "05001", "Medellín", 2, None),
            (2011, "05", "Antioquia", "05001", "Medellín", 0, 0),
        ])
        result, _, report = integrate_frames(b, m)
        self.assertEqual(result.loc[result.ano.eq(2010), "sobrevivientes_edad_1"].iloc[0], -4)
        self.assertTrue(pd.isna(result.loc[result.ano.eq(2010), "total_defunciones_menor_1"].iloc[0]))
        self.assertTrue(pd.isna(result.loc[result.ano.eq(2011), "sobrevivientes_edad_1"].iloc[0]))
        self.assertEqual(report["sobrevivientes_negativos"], 1)

    def test_duplicate_complete_keys_are_rejected(self):
        b = births([(2009, "05", "Antioquia", "05001", "Medellín", 10)] * 2)
        m = mortality([(2009, "05", "Antioquia", "05001", "Medellín", 1, 1)])
        with self.assertRaisesRegex(ValueError, "births: claves de unión duplicadas"):
            integrate_frames(b, m)

    def test_writes_parquet_and_auditable_reports(self):
        b = births([(2009, "05", "Antioquia", "05001", "Medellín", 10)])
        m = mortality([(2009, "08", "Atlántico", "08001", "Barranquilla", 1, 1)])
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            b.to_parquet(root / "births.parquet", index=False)
            m.to_parquet(root / "mortality.parquet", index=False)
            output = root / "integration/surviving_infants.parquet"
            report = process(root / "births.parquet", root / "mortality.parquet", output)
            self.assertEqual(pd.read_parquet(output).shape, (2, 8))
            self.assertEqual(len(pd.read_csv(output.parent / "unmatched_rows.csv")), 1)
            self.assertEqual(json.loads((output.parent / "quality_report.json").read_text()), report)


if __name__ == "__main__":
    unittest.main()
