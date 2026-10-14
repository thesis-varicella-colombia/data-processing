"""Agrega CHIRPS v3 Final/sat o Final/rnl a precipitación municipal semanal."""

from __future__ import annotations

import argparse
from datetime import timedelta
from pathlib import Path

import numpy as np
import pandas as pd
import xarray as xr

from epidemiological_weeks import calendar_years_needed, day_to_week, weeks_in_range
from spatial import build_weights, inspect_geometries, read_codes


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INPUT = ROOT / "data/raw/precipitation/chirps"
DEFAULT_OUTPUT = ROOT / "data/processed/chirps_precipitation"
BLOCK_DAYS = 31
MARGIN_DEGREES = 0.05


def source_path(input_dir: Path, year: int, variant: str) -> Path:
    if year == 2006:
        name = f"chirps-v3.0.{variant}.2006.epidemiological-border.observed.nc"
    elif year == 2026:
        name = f"chirps-v3.0.{variant}.2026.epidemiological-border.imputed.nc"
    else:
        name = f"chirps-v3.0.{variant}.{year}.days_p05.nc"
    return input_dir / str(year) / name


def expected_dates(year: int) -> pd.DatetimeIndex:
    if year == 2006:
        return pd.DatetimeIndex(["2006-12-31"])
    if year == 2026:
        return pd.date_range("2026-01-01", "2026-01-03")
    return pd.date_range(f"{year}-01-01", f"{year}-12-31")


def aggregate_day(
    field: np.ndarray,
    weights: tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray],
    municipality_count: int,
) -> tuple[np.ndarray, np.ndarray]:
    """Devuelve precipitación media y área válida por municipio para un día."""
    y, x, municipality, area, _ = weights
    rain = field[y, x]
    valid = np.isfinite(rain) & (rain >= 0)
    valid_area = np.bincount(
        municipality,
        weights=np.where(valid, area, 0.0),
        minlength=municipality_count,
    )
    rain_area = np.bincount(
        municipality,
        weights=np.where(valid, rain, 0.0) * area,
        minlength=municipality_count,
    )
    daily_mean = np.zeros(municipality_count, dtype=np.float64)
    np.divide(rain_area, valid_area, out=daily_mean, where=valid_area > 0)
    return daily_mean, valid_area


def process(
    start_year: int,
    end_year: int,
    input_dir: Path,
    output_dir: Path,
    requested: set[str] | None = None,
    validate_only: bool = False,
    overwrite: bool = False,
    variant: str = "sat",
) -> list[Path]:
    if variant not in ("sat", "rnl"):
        raise ValueError(f"Variante CHIRPS desconocida: {variant}")
    names = read_codes()
    codes, bounds = inspect_geometries(set(names), requested)
    weeks = weeks_in_range(start_year, end_year)
    lookup = day_to_week(weeks)
    years = calendar_years_needed(start_year, end_year)
    sources = {year: source_path(input_dir, year, variant) for year in years}
    missing = [path for path in sources.values() if not path.is_file()]
    suffix = "" if requested is None else "_" + "-".join(codes)
    variant_suffix = "_sat" if variant == "sat" else ""
    output_paths = [
        output_dir / f"chirps_precipitation_weekly_municipal{variant_suffix}_{year}{suffix}.parquet"
        for year in range(start_year, end_year + 1)
    ]
    print(
        f"CHIRPS {variant}: {len(codes)} municipios; {len(weeks)} semanas; "
        f"archivos calendario {years.start}–{years.stop - 1}; faltan {len(missing)}",
        flush=True,
    )
    if validate_only:
        if missing:
            print(f"Primer archivo pendiente: {missing[0]}", flush=True)
        return output_paths
    if missing:
        raise FileNotFoundError(f"Falta {missing[0]}")
    existing = next((path for path in output_paths if path.exists()), None)
    if existing and not overwrite:
        raise FileExistsError(f"Ya existe {existing}; use --overwrite")

    shape = (len(weeks), len(codes))
    weekly_total = np.zeros(shape, dtype=np.float64)
    weekly_valid_area = np.zeros(shape, dtype=np.float64)
    days_with_data = np.zeros(shape, dtype=np.uint8)
    imputed_days = np.zeros(len(weeks), dtype=np.uint8)
    reference_grid = None
    weights = None
    west, south, east, north = bounds

    for year, path in sources.items():
        with xr.open_dataset(path, engine="netcdf4") as dataset:
            if not {"time", "latitude", "longitude"}.issubset(dataset.coords):
                raise ValueError(f"Coordenadas incompletas en {path}")
            if "precip" not in dataset or dataset.precip.attrs.get("units") != "mm/day":
                raise ValueError(f"Variable precip o unidad inválida en {path}")
            if year == 2026 and dataset.attrs.get("border_data_status") != "imputed_not_observed":
                raise ValueError(f"El borde de 2026 no está marcado como imputado: {path}")

            dates = pd.DatetimeIndex(dataset.time.values)
            if not dates.equals(expected_dates(year)):
                raise ValueError(f"Calendario diario incompleto o inesperado en {path}")
            selected = [index for index, day in enumerate(dates.date) if day in lookup]
            needed = {day for day in lookup if day.year == year}
            if {dates[index].date() for index in selected} != needed:
                raise ValueError(f"Faltan fechas requeridas de {year} en {path}")

            cropped = dataset.precip.sel(
                latitude=slice(south - MARGIN_DEGREES, north + MARGIN_DEGREES),
                longitude=slice(west - MARGIN_DEGREES, east + MARGIN_DEGREES),
            ).transpose("time", "latitude", "longitude")
            grid = (cropped.latitude.values, cropped.longitude.values)
            if reference_grid is None:
                reference_grid = tuple(axis.copy() for axis in grid)
                weights = build_weights(grid[0], grid[1], codes, bounds)
            elif not all(np.array_equal(a, b) for a, b in zip(reference_grid, grid)):
                raise ValueError(f"La grilla CHIRPS cambió en {path}")

            for offset in range(0, len(selected), BLOCK_DAYS):
                indices = selected[offset:offset + BLOCK_DAYS]
                block = cropped.isel(time=indices).to_numpy()
                for index, field in zip(indices, block):
                    day = dates[index].date()
                    week_index = lookup[day]
                    daily_mean, valid_area = aggregate_day(field, weights, len(codes))
                    weekly_total[week_index] += daily_mean
                    weekly_valid_area[week_index] += valid_area
                    days_with_data[week_index] += (valid_area > 0).astype(np.uint8)
                    if year == 2026:
                        imputed_days[week_index] += 1
        print(f"Procesado año calendario {year}", flush=True)

    output_dir.mkdir(parents=True, exist_ok=True)
    for year, path in zip(range(start_year, end_year + 1), output_paths):
        indices = [i for i, (ep_year, _, _) in enumerate(weeks) if ep_year == year]
        total = weekly_total[indices].copy()
        total[days_with_data[indices] != 7] = np.nan
        coverage = np.clip(
            weekly_valid_area[indices] / (7 * weights[4][None, :]), 0, 1
        )
        frame = pd.DataFrame({
            "codigo_municipio": np.tile(codes, len(indices)),
            "nombre_municipio": np.tile([names[code] for code in codes], len(indices)),
            "ano_epidemiologico": np.repeat(year, len(indices) * len(codes)),
            "semana_epidemiologica": np.repeat([weeks[i][1] for i in indices], len(codes)),
            "inicio_semana": np.repeat([weeks[i][2].isoformat() for i in indices], len(codes)),
            "fin_semana": np.repeat([
                (weeks[i][2] + timedelta(days=6)).isoformat() for i in indices
            ], len(codes)),
            "precipitacion_total_mm": total.ravel(),
            "fraccion_area_con_datos": coverage.ravel(),
            "dias_con_datos": days_with_data[indices].ravel(),
            "dias_imputados": np.repeat(imputed_days[indices], len(codes)),
        })
        if variant == "sat":
            frame["variante_chirps"] = variant
        temporary = path.with_name(path.name + ".part")
        try:
            frame.to_parquet(temporary, index=False)
            temporary.replace(path)
        finally:
            temporary.unlink(missing_ok=True)
        print(f"Guardado {path} ({len(frame)} filas)", flush=True)
    return output_paths


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start-year", type=int, default=2007)
    parser.add_argument("--end-year", type=int, default=2025)
    parser.add_argument("--variant", choices=("sat", "rnl"), default="sat")
    parser.add_argument("--input-dir", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--municipality", action="append", metavar="CODIGO")
    parser.add_argument("--validate-only", action="store_true")
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    if args.start_year < 2007 or args.end_year > 2025 or args.start_year > args.end_year:
        parser.error("El intervalo epidemiológico debe estar entre 2007 y 2025")
    process(
        args.start_year,
        args.end_year,
        args.input_dir,
        args.output_dir,
        set(args.municipality) if args.municipality else None,
        args.validate_only,
        args.overwrite,
        args.variant,
    )


if __name__ == "__main__":
    main()
