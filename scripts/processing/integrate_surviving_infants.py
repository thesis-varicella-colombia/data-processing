"""Integra nacimientos y mortalidad infantil y calcula el saldo del año anterior."""

from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data/processed/births_mortality_dane"
DEFAULT_BIRTHS = DATA_DIR / "births/births.parquet"
DEFAULT_MORTALITY = DATA_DIR / "mortality/mortality.parquet"
DEFAULT_OUTPUT = DATA_DIR / "integration/surviving_infants.parquet"
KEYS = ["ano", "codigo_departamento", "codigo_municipio"]
NAMES = ["nombre_departamento", "nombre_municipio"]
IDENTIFIERS = ["ano", "codigo_departamento", "nombre_departamento",
               "codigo_municipio", "nombre_municipio"]
METRICS = ["total_nacimientos", "total_defunciones_menor_1"]
OUTPUT_COLUMNS = [*IDENTIFIERS, *METRICS, "sobrevivientes_edad_1"]
INFANT_COLUMNS = ["edad_menor_1_hombres", "edad_menor_1_mujeres"]
LOGGER = logging.getLogger(__name__)


def prepare_input(frame: pd.DataFrame, origin: str) -> tuple[pd.DataFrame, int]:
    """Selecciona columnas, excluye totales y valida las claves completas."""
    values = ["total"] if origin == "births" else INFANT_COLUMNS
    required = [*IDENTIFIERS, *values]
    missing = sorted(set(required) - set(frame.columns))
    if missing:
        raise ValueError(f"{origin}: faltan columnas {missing}")
    frame = frame[required].copy()
    for column in IDENTIFIERS[1:]:
        frame[column] = frame[column].astype("string").str.strip()
    is_total = frame["nombre_municipio"].str.casefold().eq("total").fillna(False)
    removed = int(is_total.sum())
    frame = frame.loc[~is_total].copy()
    frame["ano"] = pd.to_numeric(frame["ano"], errors="raise").astype("Int64")
    if frame["ano"].isna().any():
        raise ValueError(f"{origin}: hay filas sin año")
    for column in ["codigo_departamento", "codigo_municipio"]:
        frame[column] = frame[column].replace("", pd.NA)
    for column in values:
        frame[column] = pd.to_numeric(frame[column], errors="raise").astype("Int64")
    if origin == "births":
        frame = frame.rename(columns={"total": "total_nacimientos"})
    if origin == "mortality":
        # Se requieren ambos sexos: no sustituye un componente ausente por cero.
        frame["total_defunciones_menor_1"] = frame[INFANT_COLUMNS].sum(axis=1, min_count=2).astype("Int64")
        frame = frame[[*IDENTIFIERS, "total_defunciones_menor_1"]]
    complete = frame[KEYS].notna().all(axis=1)
    duplicated = frame.loc[complete].duplicated(KEYS, keep=False)
    if duplicated.any():
        rows = frame.loc[complete].loc[duplicated, IDENTIFIERS]
        raise ValueError(f"{origin}: claves de unión duplicadas:\n{rows.to_string(index=False)}")
    return frame, removed


def integrate_frames(births: pd.DataFrame, mortality: pd.DataFrame):
    """Une por claves completas; conserva aparte las filas con claves nulas."""
    births, removed_births = prepare_input(births, "births")
    mortality, removed_mortality = prepare_input(mortality, "mortality")
    b_complete = births[KEYS].notna().all(axis=1)
    m_complete = mortality[KEYS].notna().all(axis=1)
    joined = births.loc[b_complete].merge(
        mortality.loc[m_complete], on=KEYS, how="outer", suffixes=("_births", "_mortality"),
        indicator=True, validate="one_to_one",
    )
    # Las claves son los códigos: los nombres no condicionan la unión.
    for name in NAMES:
        joined[name] = joined[f"{name}_births"].combine_first(joined[f"{name}_mortality"])
    assumed_zero = joined["_merge"].eq("left_only")
    joined.loc[assumed_zero, "total_defunciones_menor_1"] = 0
    unmatched = []
    unmatched_columns = [*IDENTIFIERS, *METRICS, "origen", "motivo"]
    for status, origin in [("right_only", "mortality")]:
        rows = joined.loc[joined["_merge"].eq(status), [*IDENTIFIERS, *METRICS]].copy()
        rows["origen"] = origin
        rows["motivo"] = "sin_correspondencia"
        unmatched.append(rows)

    result = joined[[*IDENTIFIERS, *METRICS]].copy()
    previous = result[[*KEYS, *METRICS]].copy()
    # Desplazar la clave del año exige t-1 exacto, incluso si hay huecos temporales.
    previous["ano"] += 1
    previous["sobrevivientes_edad_1"] = previous["total_nacimientos"] - previous["total_defunciones_menor_1"]
    result = result.merge(previous[[*KEYS, "sobrevivientes_edad_1"]],
                          on=KEYS, how="left", validate="one_to_one")

    invalid_rows = []
    for frame, complete, origin in [(births, b_complete, "births"),
                                     (mortality, m_complete, "mortality")]:
        rows = frame.loc[~complete].reindex(columns=[*IDENTIFIERS, *METRICS]).copy()
        rows["sobrevivientes_edad_1"] = pd.NA
        invalid_rows.append(rows)
        audit = rows.drop(columns="sobrevivientes_edad_1").copy()
        audit["origen"] = origin
        audit["motivo"] = "clave_incompleta"
        unmatched.append(audit)
    # Un departamento nulo nunca se empareja con otro nulo. Así los países
    # con código -1 se conservan sin producir un producto cartesiano.
    result = pd.concat([result, *invalid_rows], ignore_index=True)[OUTPUT_COLUMNS]
    result[["ano", *METRICS, "sobrevivientes_edad_1"]] = result[
        ["ano", *METRICS, "sobrevivientes_edad_1"]
    ].astype("Int64")
    for column in IDENTIFIERS[1:]:
        result[column] = result[column].astype("string")
    result = result.sort_values([*KEYS, "nombre_municipio"], na_position="last", kind="stable").reset_index(drop=True)
    audit = pd.concat(unmatched, ignore_index=True).reindex(columns=unmatched_columns)
    audit = audit.sort_values([*KEYS, "origen", "nombre_municipio"], na_position="last", kind="stable").reset_index(drop=True)
    annual = []
    for year, rows in result.groupby("ano", sort=True):
        annual.append({
            "ano": int(year), "filas": len(rows),
            "sobrevivientes_nulos": int(rows["sobrevivientes_edad_1"].isna().sum()),
        })
    report = {
        "claves_union": KEYS,
        "tipo_union": "outer; solo claves completas; nombres preferidos de births",
        "formula": "sobrevivientes_edad_1(t) = total_nacimientos(t-1) - total_defunciones_menor_1(t-1)",
        "totales_excluidos": {"births": removed_births, "mortality": removed_mortality},
        "filas_sin_totales": {"births": len(births), "mortality": len(mortality)},
        "filas_mortality_asumidas_cero": int(assumed_zero.sum()),
        "filas_con_join": int(joined["_merge"].eq("both").sum()),
        "filas_sin_join": {
            origin: {
                "total": int(audit["origen"].eq(origin).sum()),
                "sin_correspondencia": int((audit["origen"].eq(origin) & audit["motivo"].eq("sin_correspondencia")).sum()),
                "clave_incompleta": int((audit["origen"].eq(origin) & audit["motivo"].eq("clave_incompleta")).sum()),
            } for origin in ("births", "mortality")
        },
        "filas_salida": len(result),
        "sobrevivientes_nulos": int(result["sobrevivientes_edad_1"].isna().sum()),
        "sobrevivientes_negativos": int(result["sobrevivientes_edad_1"].lt(0).sum()),
        "perfil_anual": annual,
    }
    return result, audit, report


def process(births_path: Path, mortality_path: Path, output: Path) -> dict:
    result, audit, report = integrate_frames(pd.read_parquet(births_path), pd.read_parquet(mortality_path))
    report["entradas"] = {"births": str(births_path), "mortality": str(mortality_path)}
    output.parent.mkdir(parents=True, exist_ok=True)
    for target, frame in [(output, result), (output.parent / "unmatched_rows.csv", audit)]:
        temporary = target.with_name(target.name + ".part")
        try:
            if target == output:
                frame.to_parquet(temporary, engine="pyarrow", index=False)
            else:
                frame.to_csv(temporary, index=False)
            temporary.replace(target)
        finally:
            temporary.unlink(missing_ok=True)
    target = output.parent / "quality_report.json"
    temporary = target.with_name(target.name + ".part")
    try:
        temporary.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        temporary.replace(target)
    finally:
        temporary.unlink(missing_ok=True)
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--births", type=Path, default=DEFAULT_BIRTHS)
    parser.add_argument("--mortality", type=Path, default=DEFAULT_MORTALITY)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    report = process(args.births.expanduser().resolve(), args.mortality.expanduser().resolve(),
                     args.output.expanduser().resolve())
    LOGGER.info("Guardado %s: %d filas; %d claves con join", args.output,
                report["filas_salida"], report["filas_con_join"])
    for origin, counts in report["filas_sin_join"].items():
        LOGGER.info("%s: %s", origin, counts)
    LOGGER.info("Sobrevivientes: %d nulos, %d negativos", report["sobrevivientes_nulos"],
                report["sobrevivientes_negativos"])


if __name__ == "__main__":
    main()
