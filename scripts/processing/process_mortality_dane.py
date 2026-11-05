"""Consolida y valida los totales del Cuadro 5 de defunciones DANE de 2008–2025."""

from __future__ import annotations

import argparse
import io
import logging
from pathlib import Path
import re
import unicodedata

import pandas as pd
import xlrd
from openpyxl import load_workbook


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INPUT = ROOT / "data/raw/births_mortality_dane/mortality/cuadro5_2008.xls"
DEFAULT_INPUT_DIR = DEFAULT_INPUT.parent
DEFAULT_OUTPUT = ROOT / "data/processed/births_mortality_dane/mortality/mortality.parquet"
YEARS = range(2008, 2026)
SOURCE_NAMES = {year: f"cuadro5_{year}.xls" for year in range(2008, 2020)} | {
    2020: "defunciones-no-fetales2020-cuadros-unificados-definitivo-2020.xls",
    2021: "defunciones-no-fetales2021-cuadro-definitivo-2021.xls",
    2022: "defunciones-no-fetales2022-cuadro-definitivo-2022.xls",
    2023: "anex-EEVV-DefuncionesNoFetales2023pCuadroDefinitivo-2023.xls",
    2024: "anex-EEVV-DefuncionesNoFetalesCuadroUnificado-2024.xlsx",
    2025: "anex-EEVV-DefuncionesNoFetalesCuadroUnificado-2025.xlsx",
}
LOGGER = logging.getLogger(__name__)
AGE_GROUPS = {
    "total": "Total",
    "edad_menor_1": "Menor 1 año",
    "edad_1_4": "De 1-4 años",
    "edad_5_14": "De 5-14 años",
    "edad_15_44": "De 15-44 años",
    "edad_45_64": "De 45-64 años",
    "edad_65_mas": "De 65 y más",
    "edad_desconocida": "Edad desconocida",
}
SEXES = ("hombres", "mujeres", "indeterminado")
VALUE_COLUMNS = ["total", *(f"{age}_{sex}" for age in AGE_GROUPS for sex in SEXES)]
IDENTIFIERS = ["ano", "codigo_departamento", "nombre_departamento",
               "codigo_municipio", "nombre_municipio"]
OUTPUT_COLUMNS = [*IDENTIFIERS, *VALUE_COLUMNS]


def normalize(value: str) -> str:
    text = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")


def validate_header(sheet, year: int, value_start: int = 2,
                    label_column: int = 0) -> tuple[int, list[list[int]]]:
    """Valida el encabezado y resuelve las columnas para cada conteo de salida."""
    labels = []
    for age, label in AGE_GROUPS.items():
        if age == "edad_65_mas" and year >= 2015:
            labels.extend(["De 65-84 años", "De 85-99 años", "De 100 y más"])
        else:
            labels.append(label)
    expected = ["total", *(
        normalize(f"{label} {sex}") for label in labels for sex in SEXES
    )]
    if sheet.ncols < len(expected) + value_start:
        raise ValueError(f"Hoja {sheet.name!r}: faltan columnas en la tabla")
    candidates = [
        index for index in range(min(30, sheet.nrows - 2))
        if normalize(str(sheet.cell_value(index, value_start))) == "total"
        and normalize(str(sheet.cell_value(index, value_start + 1))) == "total"
        and normalize(str(sheet.cell_value(index + 1, value_start + 1))) == "hombres"
    ]
    if len(candidates) != 1:
        raise ValueError(f"Hoja {sheet.name!r}: no se encontró un encabezado único")
    header = candidates[0]
    title_years = {
        int(match.group(1)) for index in range(header)
        if (match := re.search(r"(?:^|_)ano_(\d{4})(?:_|$)",
                               normalize(str(sheet.cell_value(index, label_column)))))
    }
    if title_years != {year}:
        raise ValueError(f"Hoja {sheet.name!r}: se esperaba el año {year}")
    actual = []
    age = ""
    for column in range(value_start, len(expected) + value_start):
        top = str(sheet.cell_value(header, column)).strip()
        sex = str(sheet.cell_value(header + 1, column)).strip()
        if top:
            age = top
        actual.append(normalize(f"{age} {sex}"))
    if actual != expected:
        raise ValueError(f"Hoja {sheet.name!r}: encabezados no reconocidos: {actual}")
    positions = {name: index for index, name in enumerate(actual)}
    groups = [[positions["total"]]]
    for age, label in AGE_GROUPS.items():
        source_labels = (["De 65-84 años", "De 85-99 años", "De 100 y más"]
                         if age == "edad_65_mas" and year >= 2015 else [label])
        for sex in SEXES:
            groups.append([positions[normalize(f"{source_label} {sex}")]
                           for source_label in source_labels])
    return header, groups


def harmonize_counts(values, column_groups: list[list[int]], context: str) -> list[int | None]:
    """Convierte los conteos y suma los grupos mayores por sexo sin imputar."""
    counts = []
    for value in values:
        if value == "":
            counts.append(None)
        elif isinstance(value, (int, float)) and value >= 0 and float(value).is_integer():
            counts.append(int(value))
        else:
            raise ValueError(f"{context}: conteo inválido {value!r}")
    harmonized = []
    for group in column_groups:
        parts = [counts[position] for position in group]
        harmonized.append(sum(parts) if all(value is not None for value in parts) else None)
    return harmonized


def cast_mortality(frame: pd.DataFrame) -> pd.DataFrame:
    result = frame.reindex(columns=OUTPUT_COLUMNS).copy()
    result[["ano", *VALUE_COLUMNS]] = result[["ano", *VALUE_COLUMNS]].astype("Int64")
    for column in IDENTIFIERS[1:]:
        result[column] = result[column].astype("string")
    return result


def open_mortality_workbook(source: Path):
    """Abre XLS, incluidos los cifrados con la clave estándar de Excel."""
    try:
        return xlrd.open_workbook(str(source), on_demand=True)
    except xlrd.XLRDError as error:
        if "encrypted" not in str(error).lower():
            raise
    import msoffcrypto

    with source.open("rb") as stream:
        office = msoffcrypto.OfficeFile(stream)
        office.load_key(password="VelvetSweatshop")
        decrypted = io.BytesIO()
        office.decrypt(decrypted)
    return xlrd.open_workbook(file_contents=decrypted.getvalue(), on_demand=True)


class XlsxSheet:
    """Adapta A:AJ de openpyxl a la interfaz de hoja usada por el lector XLS."""

    def __init__(self, sheet):
        self.name = sheet.title
        self.rows = [
            tuple("" if value is None else value for value in row)
            for row in sheet.iter_rows(min_col=1, max_col=36, values_only=True)
        ]
        while self.rows and not any(self.rows[-1]):
            self.rows.pop()
        self.nrows = len(self.rows)
        self.ncols = 36

    def cell_value(self, row: int, column: int):
        return self.rows[row][column]

    def row_values(self, row: int, start: int, end: int):
        return self.rows[row][start:end]


def read_modern_sheet(sheet, year: int) -> pd.DataFrame:
    """Lee Cuadro5 de 2020–2025: C/D territorio, E causa y F:AJ conteos."""
    header, groups = validate_header(sheet, year, value_start=5, label_column=2)
    if header != 7 or normalize(str(sheet.cell_value(header + 2, 2))) != "total_nacional":
        raise ValueError(f"{year}: se esperaba el encabezado en 8–9 y el total nacional en 10")
    department_code = department = category = None
    rows = []
    for index in range(header + 2, sheet.nrows):
        department_label, label, cause, *values = sheet.row_values(index, 2, 36)
        if normalize(str(cause)) not in {"total", "total_mun"}:
            continue
        department_label = str(department_label).strip()
        label = str(label).strip()
        context = f"{year}, hoja {sheet.name!r}, fila {index + 1}"
        if normalize(department_label) == "total_nacional":
            continue
        if department_label:
            match = re.fullmatch(r"(\d{2})\s+(.+)", department_label)
            if match:
                department_code, department = match.groups()
                category = "department"
            elif normalize(department_label) in {"extranjero", "extranjeros"}:
                department_code, department, category = None, "Extranjeros", "foreign"
            elif normalize(department_label) == "sin_informacion":
                department_code, department, category = None, "Sin Información", "unknown"
            else:
                raise ValueError(f"{context}: departamento inesperado {department_label!r}")
            if normalize(label) not in {"", "total", "total_dpto"}:
                raise ValueError(f"{context}: se esperaba el total del departamento/categoría")
            municipality_code, municipality = department_code, "Total"
        else:
            if department is None:
                raise ValueError(f"{context}: municipio/país sin departamento/categoría")
            if normalize(label) == "sin_informacion":
                municipality_code, municipality = "-2", label
            else:
                pattern = r"(\d{3,5})\s+(.+)" if category == "foreign" else r"(\d{5})\s+(.+)"
                match = re.fullmatch(pattern, label)
                if match is None:
                    raise ValueError(f"{context}: municipio/país inesperado {label!r}")
                municipality_code, municipality = match.groups()
                if category == "department" and municipality_code[:2] != department_code:
                    raise ValueError(f"{context}: el municipio {municipality_code} no pertenece a {department_code}")
                if normalize(municipality) == "sin_informacion":
                    municipality_code = "-2"
        if category == "foreign":
            municipality_code = "-1"
        elif category == "unknown":
            municipality_code = "-2"
        counts = harmonize_counts(values, groups, context)
        rows.append([year, department_code, department, municipality_code, municipality, *counts])
    if not rows:
        raise ValueError(f"{year}: no se encontraron totales territoriales en Cuadro5")
    return cast_mortality(pd.DataFrame(rows, columns=OUTPUT_COLUMNS))


def read_sheet(sheet, year: int = 2008) -> pd.DataFrame:
    """Selecciona solo B=TOTAL y descarta las filas de causas específicas."""
    header, column_groups = validate_header(sheet, year)
    first_data = header + 2
    value_end = max(index for group in column_groups for index in group) + 3
    department = re.sub(r"^\d{2}\s+", "", str(sheet.cell_value(header - 1, 0)).strip())
    if not department:
        raise ValueError(f"Hoja {sheet.name!r}: falta el nombre del departamento/categoría")
    category = normalize(sheet.name)
    department_code = sheet.name if re.fullmatch(r"\d{2}", sheet.name) else None
    if department_code is None and category not in {"extranjeros", "sin_informacion"}:
        raise ValueError(f"Hoja inesperada: {sheet.name!r}")
    if (normalize(str(sheet.cell_value(first_data, 0))) != "total"
            or normalize(str(sheet.cell_value(first_data, 1))) != "total"):
        raise ValueError(f"Hoja {sheet.name!r}: falta el Total de la fila {first_data + 1}")

    rows = []
    for index in range(first_data, sheet.nrows):
        label, cause, *values = sheet.row_values(index, 0, value_end)
        if normalize(str(cause)) != "total":
            continue
        context = f"Hoja {sheet.name!r}, fila {index + 1}"
        label = str(label).strip()
        if normalize(label) == "total":
            municipality_code, municipality = department_code, "Total"
        else:
            pattern = r"(\d{3,5})\s+(.+)" if category == "extranjeros" else r"(\d{5})\s+(.+)"
            match = re.fullmatch(pattern, label)
            if match is None:
                raise ValueError(f"{context}: etiqueta territorial inesperada {label!r}")
            municipality_code, municipality = match.groups()
            if department_code and municipality_code[:2] != department_code:
                raise ValueError(f"{context}: el municipio {municipality_code} no pertenece a {department_code}")
            if normalize(municipality) == "sin_informacion":
                municipality_code = "-2"
        if category == "extranjeros":
            municipality_code = "-1"
        elif category == "sin_informacion":
            municipality_code = "-2"
        harmonized = harmonize_counts(values, column_groups, context)
        rows.append([year, department_code, department,
                     municipality_code, municipality, *harmonized])
    frame = pd.DataFrame(rows, columns=OUTPUT_COLUMNS)
    # Bogotá es una sola entidad: en estos años la hoja solo publica su total.
    if department_code == "11" and 2009 <= year <= 2018:
        if not frame["codigo_municipio"].eq("11001").any():
            totals = frame.loc[frame["nombre_municipio"].eq("Total")]
            if len(totals) != 1:
                raise ValueError(f"{year}: se esperaba un único total de Bogotá")
            municipality = totals.copy()
            municipality["codigo_municipio"] = "11001"
            municipality["nombre_municipio"] = department
            frame = pd.concat([frame, municipality], ignore_index=True)
    return frame


def read_mortality(source: Path) -> pd.DataFrame:
    """Consolida un archivo anual de cualquiera de las dos estructuras."""
    year = next((year for year, name in SOURCE_NAMES.items() if name == source.name), None)
    if year is None:
        raise ValueError(f"Archivo no admitido (2008–2025): {source.name}")
    if source.suffix.lower() == ".xlsx":
        workbook = load_workbook(source, read_only=True, data_only=True)
        try:
            return read_modern_sheet(XlsxSheet(workbook["Cuadro5"]), year)
        finally:
            workbook.close()
    workbook = open_mortality_workbook(source)
    frames = []
    try:
        if year >= 2020:
            return read_modern_sheet(workbook.sheet_by_name("Cuadro5"), year)
        for sheet in workbook.sheets():
            if normalize(sheet.name) in {"00", "indice"}:
                continue
            frame = read_sheet(sheet, year)
            frames.append(frame)
            LOGGER.debug("%s, %s (%s): %d filas", year, sheet.name,
                         frame.iloc[0]["nombre_departamento"], len(frame))
    finally:
        workbook.release_resources()
    if not frames:
        raise ValueError("No se encontraron hojas para consolidar")
    return cast_mortality(pd.concat(frames, ignore_index=True))


def read_all_mortality(input_dir: Path) -> pd.DataFrame:
    """Exige los dieciocho archivos y concatena sus tablas anuales."""
    sources = [input_dir / name for name in SOURCE_NAMES.values()]
    missing = [str(source) for source in sources if not source.is_file()]
    if missing:
        raise FileNotFoundError("Faltan archivos anuales: " + ", ".join(missing))
    frames = []
    for source in sources:
        frame = read_mortality(source)
        frames.append(frame)
        LOGGER.info("%s: %d filas", source.name, len(frame))
    return pd.concat(frames, ignore_index=True)


def validate_totals(frame: pd.DataFrame) -> pd.DataFrame:
    """Compara solo total de los desgloses con el total departamental/categoría."""
    keys = ["ano", "codigo_departamento", "nombre_departamento"]
    is_total = frame["nombre_municipio"].str.casefold().eq("total")
    reported = frame.loc[is_total, keys + ["total"]].rename(columns={"total": "total_publicado"})
    if reported.duplicated(keys).any():
        raise ValueError("Hay más de una fila Total por año y departamento/categoría")
    sums = frame.loc[~is_total].groupby(keys, dropna=False).agg(
        suma_desglose=("total", lambda values: values.sum(min_count=1)),
        filas_desglose=("total", "size"),
        valores_presentes=("total", "count"),
    ).reset_index()
    result = reported.merge(sums, on=keys, how="outer", indicator=True)
    if result["_merge"].eq("right_only").any():
        raise ValueError("Hay desgloses sin fila Total")
    result["filas_desglose"] = result["filas_desglose"].fillna(0).astype(int)
    has_detail = result["filas_desglose"].gt(0)
    incomplete = result["total_publicado"].isna() | (
        has_detail & result["valores_presentes"].ne(result["filas_desglose"])
    )
    result["diferencia"] = result["suma_desglose"] - result["total_publicado"]
    issues = result.loc[incomplete | (has_detail & result["diferencia"].ne(0).fillna(False))]
    if not issues.empty:
        raise ValueError("Los totales no coinciden o están incompletos:\n" + issues.to_string(index=False))
    result["estado"] = "sin desglose"
    result.loc[has_detail, "estado"] = "coincide"
    return result.drop(columns=["_merge", "valores_presentes"])


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    inputs = parser.add_mutually_exclusive_group()
    inputs.add_argument("--input", type=Path, help="Procesar solo un archivo anual")
    inputs.add_argument("--input-dir", type=Path, default=DEFAULT_INPUT_DIR,
                        help="Directorio con los 18 archivos anuales de 2008–2025")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    frame = (read_mortality(args.input.expanduser().resolve()) if args.input
             else read_all_mortality(args.input_dir.expanduser().resolve()))
    validation = validate_totals(frame)
    LOGGER.info("Validación de total: %d grupos coinciden; %d sin desglose",
                validation["estado"].eq("coincide").sum(),
                validation["estado"].eq("sin desglose").sum())
    output = args.output.expanduser().resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_name(output.name + ".part")
    try:
        frame.to_parquet(temporary, engine="pyarrow", index=False)
        temporary.replace(output)
    finally:
        temporary.unlink(missing_ok=True)
    LOGGER.info("Guardado %s: %d filas, %d columnas", output, *frame.shape)


if __name__ == "__main__":
    main()
