"""Consolida y valida los Cuadros 3 de nacimientos DANE de 2008–2025."""

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
DEFAULT_INPUT = ROOT / "data/raw/births_mortality_dane/births"
DEFAULT_OUTPUT = ROOT / "data/processed/births_mortality_dane/births/births.parquet"
LOGGER = logging.getLogger(__name__)
YEARS = range(2008, 2026)
SOURCE_NAMES = {
    year: (f"Cuadro3_{year}.xls" if year <= 2019
           else f"nacimientos{year}-cuadro-definitivo-{year}.xls")
    for year in range(2008, 2023)
} | {
    2023: "anex-EEVV-Nacimientos2023pCuadroDefinivo-2023.xls",
    2024: "anex-EEVV-NacimientosCuadroAcumulado-2024.xlsx",
    2025: "anex-EEVV-NacimientosCuadroAcumulado-2025.xlsx",
}
VALUE_COLUMNS = [
    "total",
    "total_hombres", "total_mujeres",
    "cabecera_municipal_hombres", "cabecera_municipal_mujeres",
    "centro_poblado_hombres", "centro_poblado_mujeres",
    "rural_disperso_hombres", "rural_disperso_mujeres",
    "sin_informacion_hombres", "sin_informacion_mujeres",
    "total_indeterminado", "cabecera_municipal_indeterminado",
    "centro_poblado_indeterminado", "rural_disperso_indeterminado",
    "sin_informacion_indeterminado",
]
LABEL_COLUMN = "departamento_y_municipio_de_residencia_de_la_madre"
SOURCE_COLUMNS = [LABEL_COLUMN, *VALUE_COLUMNS]
OUTPUT_COLUMNS = [
    "ano", "codigo_departamento", "nombre_departamento",
    "codigo_municipio", "nombre_municipio", *VALUE_COLUMNS,
]


def normalize(text: str) -> str:
    """Convierte los encabezados del Excel a nombres de columna estables."""
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")


def source_header(sheet, year: int, label_column: int = 0,
                  value_start: int = 1, value_end: int | None = None) -> tuple[int, list[str]]:
    """Localiza y combina las dos filas del encabezado de cada versión."""
    candidates = [
        index for index in range(min(30, sheet.nrows - 1))
        if normalize(str(sheet.cell_value(index, label_column))) in {
            LABEL_COLUMN, "pais_de_residencia_de_la_madre",
        }
    ]
    if len(candidates) != 1:
        raise ValueError(f"Hoja {sheet.name!r}: no se encontró un encabezado único")
    header = candidates[0]
    title_years = {
        int(match.group(1))
        for index in range(header)
        if (match := re.search(r"(?:^|_)ano_(\d{4})(?:_|$)",
                               normalize(str(sheet.cell_value(index, label_column)))))
    }
    if title_years != {year}:
        raise ValueError(f"Hoja {sheet.name!r}: el año del encabezado no coincide con {year}")
    columns = [LABEL_COLUMN]
    area = ""
    for index in range(value_start, value_end if value_end is not None else sheet.ncols):
        top = str(sheet.cell_value(header, index)).strip()
        sex = str(sheet.cell_value(header + 1, index)).strip()
        if top:
            area = top
        columns.append(normalize(f"{area} {sex}").replace("indeterminados", "indeterminado"))
    if (len(columns) != len(set(columns))
            or not set([LABEL_COLUMN, *VALUE_COLUMNS[:11]]).issubset(columns)
            or not set(columns).issubset(SOURCE_COLUMNS)):
        raise ValueError(f"Hoja {sheet.name!r}: encabezados no reconocidos: {columns}")
    return header, columns


def count_values(values: list, context: str) -> list[int | None]:
    """Conserva vacíos y rechaza conteos negativos, fraccionarios o texto."""
    result = []
    for value in values:
        if value == "":
            result.append(None)
        elif isinstance(value, (int, float)) and value >= 0 and float(value).is_integer():
            result.append(int(value))
        else:
            raise ValueError(f"{context}: conteo inválido {value!r}")
    return result


def cast_births(frame: pd.DataFrame) -> pd.DataFrame:
    """Mantiene el mismo esquema Parquet para las dos estructuras Excel."""
    result = frame.reindex(columns=OUTPUT_COLUMNS).copy()
    result[VALUE_COLUMNS + ["ano"]] = result[VALUE_COLUMNS + ["ano"]].astype("Int64")
    for column in ("nombre_departamento", "codigo_departamento",
                   "codigo_municipio", "nombre_municipio"):
        result[column] = result[column].astype("string")
    return result


def open_births_workbook(source: Path):
    """Abre XLS normales o protegidos con la clave estándar de Excel."""
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
    """Expone las celdas A:T de openpyxl con la interfaz de hoja de xlrd."""

    def __init__(self, sheet):
        self.name = sheet.title
        self.rows = [
            tuple("" if value is None else value for value in row)
            for row in sheet.iter_rows(min_col=1, max_col=20, values_only=True)
        ]
        # Algunos archivos declaran miles de filas vacías con formato.
        while self.rows and not any(self.rows[-1]):
            self.rows.pop()
        self.nrows = len(self.rows)
        self.ncols = 20

    def cell_value(self, row: int, column: int):
        return self.rows[row][column]

    def row_values(self, row: int, start: int, end: int):
        return self.rows[row][start:end]


def read_modern_sheet(sheet, year: int) -> pd.DataFrame:
    """Lee Cuadro3 de 2020–2025: C:D identifican y E:T contienen conteos."""
    header, columns = source_header(sheet, year, label_column=2, value_start=4, value_end=20)
    if header != 7 or normalize(str(sheet.cell_value(9, 2))) != "total_nacional":
        raise ValueError(f"{year}: se esperaba el encabezado en 8–9 y el total nacional en 10")
    rows = []
    department_code = None
    department = None
    category = None
    for index in range(10, sheet.nrows):
        department_label, label, *values = sheet.row_values(index, 2, 20)
        if not any(value != "" for value in values):
            continue
        context = f"{year}, hoja {sheet.name!r}, fila {index + 1}"
        department_label = str(department_label).strip()
        label = str(label).strip()
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
            if normalize(label) not in {"total", "total_dpto"}:
                raise ValueError(f"{context}: se esperaba el Total del departamento/categoría")
            municipality_code = department_code
            municipality = "Total"
        else:
            if department is None:
                raise ValueError(f"{context}: municipio sin departamento")
            if normalize(label) == "sin_informacion":
                municipality_code, municipality = "-2", label
            else:
                pattern = r"(\d{3,5})\s+(.+)" if category == "foreign" else r"(\d{5})\s+(.+)"
                match = re.fullmatch(pattern, label)
                if match is None:
                    raise ValueError(f"{context}: municipio/país inesperado {label!r}")
                municipality_code, municipality = match.groups()
                if category == "department" and municipality_code[:2] != department_code:
                    raise ValueError(f"{context}: el municipio {municipality_code} no pertenece al departamento {department_code}")
                if normalize(municipality) == "sin_informacion":
                    municipality_code = "-2"
        if category == "foreign":
            municipality_code = "-1"
        elif category == "unknown":
            municipality_code = "-2"
        record = dict(zip(columns[1:], count_values(values, context)))
        record.update(ano=year, codigo_departamento=department_code,
                      nombre_departamento=department, codigo_municipio=municipality_code,
                      nombre_municipio=municipality)
        rows.append(record)
    if not rows:
        raise ValueError(f"{year}: no se encontraron datos en Cuadro3")
    return cast_births(pd.DataFrame(rows))


def read_births(source: Path) -> pd.DataFrame:
    """Lee un archivo anual y conserva totales y categorías especiales."""
    year = next((year for year, name in SOURCE_NAMES.items() if name == source.name), None)
    if year is None:
        raise ValueError(f"Archivo no admitido (2008–2025): {source.name}")
    if source.suffix.lower() == ".xlsx":
        workbook = load_workbook(source, read_only=True, data_only=True)
        try:
            return read_modern_sheet(XlsxSheet(workbook["Cuadro3"]), year)
        finally:
            workbook.close()
    workbook = open_births_workbook(source)
    frames = []
    try:
        if year >= 2020:
            return read_modern_sheet(workbook.sheet_by_name("Cuadro3"), year)
        for sheet in workbook.sheets():
            if normalize(sheet.name) in {"indice", "00"}:
                continue
            if not (re.fullmatch(r"\d{2}", sheet.name)
                    or normalize(sheet.name) in {"extranjeros", "sin_informacion"}):
                raise ValueError(f"Hoja inesperada: {sheet.name!r}")
            header, columns = source_header(sheet, year)
            department = re.sub(r"^\d{2}\s+", "", str(sheet.cell_value(header - 1, 0)).strip())
            if not department:
                raise ValueError(f"Hoja {sheet.name!r}: falta el nombre del departamento")
            rows = []
            for index in range(header + 2, sheet.nrows):
                row = sheet.row_values(index, 0, len(columns))
                # Descarta filas vacías y notas al pie sin conteos.
                if not any(value != "" for value in row[1:]):
                    continue
                label = str(row[0]).strip()
                code_pattern = r"\d{3,5}\s+.+" if normalize(sheet.name) == "extranjeros" else r"\d{5}\s+.+"
                if not (normalize(label) in {"total", "sin_informacion"}
                        or re.fullmatch(code_pattern, label)):
                    raise ValueError(f"Hoja {sheet.name!r}, fila {index + 1}: etiqueta inesperada {label!r}")
                values = count_values(row[1:], f"{year}, hoja {sheet.name!r}, fila {index + 1}")
                rows.append([label, *values])
            if not rows:
                raise ValueError(f"Hoja {sheet.name!r}: no hay datos")
            frame = pd.DataFrame(rows, columns=columns).reindex(columns=SOURCE_COLUMNS)
            frame["ano"] = year
            frame["nombre_departamento"] = department
            # Las hojas especiales no tienen un código de departamento DANE.
            frame["codigo_departamento"] = sheet.name if sheet.name.isdigit() else pd.NA
            identifiers = frame[LABEL_COLUMN].str.extract(r"^(\d{3,5})\s+(.+)$")
            frame["codigo_municipio"] = identifiers[0]
            frame["nombre_municipio"] = identifiers[1].fillna(frame[LABEL_COLUMN])
            is_total = frame["nombre_municipio"].str.casefold().eq("total")
            frame.loc[is_total, "codigo_municipio"] = frame["codigo_departamento"]
            is_unknown = frame["nombre_municipio"].map(normalize).eq("sin_informacion")
            frame.loc[is_unknown, "codigo_municipio"] = "-2"
            if normalize(sheet.name) == "extranjeros":
                frame["codigo_municipio"] = "-1"
            elif normalize(sheet.name) == "sin_informacion":
                frame["codigo_municipio"] = "-2"
            frame = frame[OUTPUT_COLUMNS]
            if sheet.name == "11" and 2008 <= year <= 2019:
                if not frame["codigo_municipio"].eq("11001").any():
                    totals = frame.loc[frame["nombre_municipio"].str.casefold().eq("total")]
                    if len(totals) != 1:
                        raise ValueError(f"{year}: se esperaba un único total de Bogotá")
                    municipality = totals.copy()
                    municipality["codigo_municipio"] = "11001"
                    municipality["nombre_municipio"] = department
                    frame = pd.concat([frame, municipality], ignore_index=True)
            frames.append(frame)
            LOGGER.debug("%s, %s (%s): %d filas", year, sheet.name, department, len(frame))
    finally:
        workbook.release_resources()
    if not frames:
        raise ValueError("No se encontraron hojas para consolidar")
    return cast_births(pd.concat(frames, ignore_index=True))


def read_all_births(input_dir: Path) -> pd.DataFrame:
    """Exige los dieciocho archivos y concatena las tablas anuales por nombre."""
    sources = [input_dir / name for name in SOURCE_NAMES.values()]
    missing = [str(source) for source in sources if not source.is_file()]
    if missing:
        raise FileNotFoundError("Faltan archivos anuales: " + ", ".join(missing))
    frames = []
    for source in sources:
        frame = read_births(source)
        frames.append(frame)
        LOGGER.info("%s: %d filas", source.name, len(frame))
    return pd.concat(frames, ignore_index=True)


def validate_totals(frame: pd.DataFrame) -> pd.DataFrame:
    """Compara solo `total` por año y departamento/categoría, sin duplicarlo."""
    keys = ["ano", "codigo_departamento", "nombre_departamento"]
    is_total = frame["nombre_municipio"].str.casefold().eq("total")
    reported = frame.loc[is_total, keys + ["total"]].rename(columns={"total": "total_publicado"})
    if reported.duplicated(keys).any():
        raise ValueError("Hay más de una fila Total por año y departamento/categoría")
    detail = frame.loc[~is_total]
    sums = detail.groupby(keys, dropna=False).agg(
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
    mismatch = has_detail & result["diferencia"].ne(0).fillna(False)
    issues = result.loc[incomplete | mismatch]
    if not issues.empty:
        raise ValueError("Los totales no coinciden o están incompletos:\n" + issues.to_string(index=False))
    result["estado"] = "sin desglose"
    result.loc[has_detail, "estado"] = "coincide"
    return result.drop(columns=["_merge", "valores_presentes"])


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    frame = read_all_births(args.input_dir.expanduser().resolve())
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
