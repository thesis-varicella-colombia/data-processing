"""Procesa coberturas municipales de varicela y guarda el CSV 2016–2025."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INPUT = ROOT / (
    "data/raw/vaccine_coverage/"
    "Coberturas de Vacunacion Municipal desde 1998-2025(30-01-2025).xlsx"
)
DEFAULT_OUTPUT = (
    ROOT / "data/processed/vaccine_coverage/coberturas_municipales_2016_2025.csv"
)

POPULATION_COLUMNS = {
    2015: ("Poblaciòn de 1 año (Meta varicela media cohorte)",),
    2016: ("Poblaciòn de 1 año Meta Programática)",),
    2017: ("Poblaciòn de 1 año Meta Programática)",),
    2018: ("Poblaciòn de 1 año Meta Programática)",),
    2019: (
        "Poblaciòn de 1 año Meta Programática)",
        "Pob. 5 años  (Meta Programatica)",
    ),
    2020: (
        "Poblaciòn de 1 año (Meta Programática 2020)",
        "Pob. 5 años  (Meta Programática 2020)",
    ),
    2021: (
        "Poblaciòn de 1 año (Meta Programática 2021)",
        "Pob. 5 años  (Meta Programática 2021)",
    ),
    2022: (
        "Poblaciòn de 1 año (Meta Programática 2022)",
        "Pob. 5 años  (Meta Programática 2022)",
    ),
    2023: (
        "POB. 1 año\nMETA PROGRAM 2023",
        "POB. 5 Años\nMETA PROGRAM 2023",
    ),
    2024: (
        "POB. 1 año\nMETA PROGRAMATICA\n2024 (Aj2_20241028)",
        "POB. 5 Años\nMETA PROGRAMATICA 2024 (Aj2_20241028)",
    ),
    2025: (
        "POB. < 1 AÑO\nMETA PROGRAMATICA\n2025 (20251130)VerF",
        "POB. 5 Años\nMETA PROGRAMATICA 2025 (20251130)VerF",
    ),
}


def process_coverage(source: Path) -> pd.DataFrame:
    """Reproduce la selección, normalización y asignación anual del notebook."""
    coberturas = {}
    with pd.ExcelFile(source) as excel:
        for anio in range(2015, 2026):
            header_row = 6 if anio == 2016 else 5
            last_row = 1128 if anio == 2016 else 1127
            df = pd.read_excel(
                excel,
                sheet_name=str(anio),
                header=header_row - 1,
                nrows=last_row - header_row,
                dtype={"CODEP": "string", "DIVIPOLA": "string"},
            )

            base_columns = df.columns[1:5] if anio in (2016, 2017) else df.columns[:4]
            varicella_columns = [
                column for column in df.columns if "VARICELA" in str(column).upper()
            ]
            population_columns = POPULATION_COLUMNS[anio]
            selected = list(dict.fromkeys(
                [*base_columns, *population_columns, *varicella_columns]
            ))
            missing = [column for column in selected if column not in df.columns]
            if missing:
                raise ValueError(f"Hoja {anio}: faltan columnas {missing}")

            rename = dict(zip(
                population_columns, ("meta_pob_1_anio", "meta_pob_5_anios")
            ))
            rename.update({
                "VARICELA DE 1 AÑO\nD. Unica": "varicela_un_anio_dosis_unica",
                "% VARICELA DE 1 AÑO": "%_varicela_un_anio_dosis_unica",
            })
            if anio == 2015:
                rename.update({
                    "VARICELA DE 1 AÑO\n1a": "varicela_un_anio_dosis_unica",
                    "% VARICELA DE 1 AÑO - Cump AGOSTO": "%_varicela_un_anio_dosis_unica",
                })
            if anio >= 2019:
                rename.update({
                    "VARICELA DE 5 AÑOS Ref.": "varicela_cinco_anios_refuerzo",
                    "% VARICELA": "%_varicela_cinco_anios_refuerzo",
                })
            if anio == 2019:
                rename["VARICELA DE 5 AÑOS"] = "varicela_cinco_anios_refuerzo"

            coverage = df.loc[:, selected].rename(columns=rename).copy()
            if anio == 2025:
                coverage = coverage.drop(columns=["% Varicela\n5 Años "])
            if anio < 2019:
                for column in (
                    "meta_pob_5_anios",
                    "varicela_cinco_anios_refuerzo",
                    "%_varicela_cinco_anios_refuerzo",
                ):
                    coverage[column] = pd.NA
            coberturas[anio] = coverage

    combined = pd.concat(
        [df.assign(anio=anio) for anio, df in sorted(coberturas.items())],
        ignore_index=True,
        sort=False,
    )
    # La cobertura publicada en diciembre se asigna al año siguiente.
    combined = combined.loc[combined["anio"] != 2025].copy()
    combined["anio"] += 1
    return combined


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-file", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output-file", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    if not args.input_file.is_file():
        parser.error(f"No existe el Excel: {args.input_file}")

    coverage = process_coverage(args.input_file)
    args.output_file.parent.mkdir(parents=True, exist_ok=True)
    coverage.to_csv(args.output_file, index=False, encoding="utf-8-sig")
    print(f"Guardado: {args.output_file} ({len(coverage):,} filas)")


if __name__ == "__main__":
    main()
