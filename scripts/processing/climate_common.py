"""Lectura por bloques y agregación municipio × semana de ERA5-Land Daily UTC."""

from __future__ import annotations

import argparse
from datetime import timedelta
from pathlib import Path
from typing import Callable

import numpy as np
import pandas as pd
import xarray as xr

from epidemiological_weeks import calendar_years_needed, day_to_week, weeks_in_range
from spatial import build_weights, inspect_geometries, read_codes


ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data/raw/era5_land"
PROCESSED = ROOT / "data/processed/climate"
UNITS = {"t2m": "K", "d2m": "K", "sp": "Pa", "tp": "m"}


def raw_path(year: int) -> Path:
    return RAW / f"era5_land_daily_{year}.nc"


def input_paths(year: int, needed_dates: set) -> list[Path]:
    annual = raw_path(year)
    if annual.is_file():
        return [annual]
    months = sorted({day.month for day in needed_dates})
    monthly = [RAW / f"era5_land_daily_{year}_{month:02d}.nc" for month in months]
    if all(path.is_file() for path in monthly):
        return monthly
    return [annual]


def add_common_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--start-year", type=int, default=2007)
    parser.add_argument("--end-year", type=int, default=2025)
    parser.add_argument("--municipality", action="append", metavar="CODIGO")
    parser.add_argument("--validate-only", action="store_true")
    parser.add_argument("--overwrite", action="store_true")


def check_years(parser: argparse.ArgumentParser, args: argparse.Namespace) -> None:
    if args.start_year < 2007 or args.end_year > 2025 or args.start_year > args.end_year:
        parser.error("El intervalo epidemiológico debe estar entre 2007 y 2025")


def _normalise_longitudes(longitudes: np.ndarray) -> np.ndarray:
    if np.nanmin(longitudes) >= 0 and np.nanmax(longitudes) > 180:
        return ((longitudes + 180) % 360) - 180
    return longitudes


def run_pipeline(args: argparse.Namespace, category: str,
                 required: tuple[str, ...], outputs: tuple[str, ...],
                 calculate: Callable[[dict[str, np.ndarray]], dict[str, np.ndarray]],
                 precipitation: bool = False) -> list[Path]:
    names = read_codes()
    requested = set(args.municipality) if args.municipality else None
    codes, bounds = inspect_geometries(set(names), requested)
    weeks = weeks_in_range(args.start_year, args.end_year)
    lookup = day_to_week(weeks)
    years = calendar_years_needed(args.start_year, args.end_year)
    files_by_year = {year: input_paths(year, {day for day in lookup if day.year == year})
                     for year in years}
    missing = [path for paths in files_by_year.values() for path in paths if not path.is_file()]
    suffix = "" if requested is None else "_" + "-".join(codes)
    destination = PROCESSED / category
    paths = [destination / f"{category}_weekly_municipal_{year}{suffix}.parquet"
             for year in range(args.start_year, args.end_year + 1)]
    print(f"{len(codes)} municipios; {len(weeks)} semanas; archivos calendario "
          f"{years.start}–{years.stop - 1}; faltan {len(missing)}", flush=True)
    if args.validate_only:
        if missing:
            print("Primer archivo pendiente:", missing[0], flush=True)
        return paths
    if missing:
        raise FileNotFoundError(f"Falta {missing[0]}; las semanas de borde requieren "
                                "también los años calendario adyacentes")
    existing = next((path for path in paths if path.exists()), None)
    if existing and not args.overwrite:
        raise FileExistsError(f"Ya existe {existing}; use --overwrite")

    shape = (len(weeks), len(codes))
    numerator = {name: np.zeros(shape, dtype=np.float64) for name in outputs}
    denominator = {name: np.zeros(shape, dtype=np.float64) for name in outputs}
    complete_days = {name: np.zeros(shape, dtype=np.int8) for name in outputs} if precipitation else None
    reference_grid = None
    weights = None
    for calendar_year in years:
      observed_dates = set()
      for source_path in files_by_year[calendar_year]:
        with xr.open_dataset(source_path, engine="netcdf4") as ds:
            if not {"valid_time", "latitude", "longitude"}.issubset(ds.coords):
                raise ValueError(f"Coordenadas incompletas en {source_path}")
            for variable in required:
                if variable not in ds or ds[variable].attrs.get("units") != UNITS[variable]:
                    raise ValueError(f"Variable o unidad inválida: {variable} en {calendar_year}")
            grid = (ds.latitude.values, ds.longitude.values)
            if reference_grid is None:
                reference_grid = tuple(axis.copy() for axis in grid)
                weights = build_weights(grid[0], _normalise_longitudes(grid[1]), codes, bounds)
            elif not all(np.array_equal(a, b) for a, b in zip(reference_grid, grid)):
                raise ValueError(f"La grilla cambió en {calendar_year}")
            dates = pd.DatetimeIndex(ds.valid_time.values)
            if source_path == raw_path(calendar_year):
                expected = pd.date_range(f"{calendar_year}-01-01", f"{calendar_year}-12-31")
            else:
                month = int(source_path.stem[-2:])
                expected = pd.date_range(f"{calendar_year}-{month:02d}-01",
                                         (pd.Timestamp(calendar_year, month, 1) +
                                          pd.offsets.MonthEnd(0)))
            if not dates.equals(expected):
                raise ValueError(f"Calendario diario UTC incompleto en {source_path}")
            indices = [i for i, stamp in enumerate(dates) if stamp.date() in lookup]
            observed_dates.update(dates[i].date() for i in indices)
            y, x, municipality, area, total_area = weights
            for offset in range(0, len(indices), 10):
                block = indices[offset:offset + 10]
                inputs = {name: np.asarray(ds[name].isel(valid_time=block)
                                            .transpose("valid_time", "latitude", "longitude").values,
                                           dtype=np.float64)
                          for name in required}
                values_by_name = calculate(inputs)
                if set(values_by_name) != set(outputs):
                    raise ValueError("El cálculo no produjo todas las variables previstas")
                week_idx = np.asarray([lookup[dates[i].date()] for i in block], dtype=np.int32)
                for name, values in values_by_name.items():
                    if values.shape != inputs[required[0]].shape:
                        raise ValueError(f"Dimensiones inválidas de {name}")
                    selected = values[:, y, x]
                    valid = np.isfinite(selected)
                    weighted = np.where(valid, selected, 0.0) * area
                    if precipitation:
                        day_num = np.zeros((len(block), len(codes)), dtype=np.float64)
                        day_den = np.zeros_like(day_num)
                        day_idx = np.arange(len(block))[:, None]
                        np.add.at(day_num, (day_idx, municipality[None, :]), weighted)
                        np.add.at(day_den, (day_idx, municipality[None, :]), valid * area)
                        daily_mean = np.zeros_like(day_num)
                        np.divide(day_num, day_den, out=daily_mean, where=day_den > 0)
                        np.add.at(numerator[name], week_idx, daily_mean)
                        np.add.at(denominator[name], week_idx, day_den)
                        np.add.at(complete_days[name], week_idx, (day_den > 0).astype(np.int8))
                    else:
                        np.add.at(numerator[name], (week_idx[:, None], municipality[None, :]), weighted)
                        np.add.at(denominator[name], (week_idx[:, None], municipality[None, :]), valid * area)
      needed = {day for day in lookup if day.year == calendar_year}
      if observed_dates != needed:
          raise ValueError(f"Faltan {len(needed - observed_dates)} días de {calendar_year} "
                           "para completar las semanas epidemiológicas")
      print(f"Procesado año calendario {calendar_year}", flush=True)

    destination.mkdir(parents=True, exist_ok=True)
    for year, path in zip(range(args.start_year, args.end_year + 1), paths):
        indices = [i for i, (ep_year, _, _) in enumerate(weeks) if ep_year == year]
        selected_weeks = [weeks[i] for i in indices]
        count = len(codes)
        frame = pd.DataFrame({
            "codigo_municipio": np.tile(codes, len(indices)),
            "nombre_municipio": np.tile([names[code] for code in codes], len(indices)),
            "ano_epidemiologico": np.repeat(year, len(indices) * count),
            "semana_epidemiologica": np.repeat([week for _, week, _ in selected_weeks], count),
            "inicio_semana": np.repeat([start.isoformat() for _, _, start in selected_weeks], count),
            "fin_semana": np.repeat([(start + timedelta(days=6)).isoformat()
                                     for _, _, start in selected_weeks], count),
        })
        for name in outputs:
            if precipitation:
                result = numerator[name][indices].copy()
                result[complete_days[name][indices] != 7] = np.nan
            else:
                result = np.full((len(indices), count), np.nan)
                np.divide(numerator[name][indices], denominator[name][indices],
                          out=result, where=denominator[name][indices] > 0)
            frame[name] = result.ravel()
            coverage_name = ("fraccion_area_con_datos" if len(outputs) == 1 else
                             f"fraccion_area_con_datos_{name}")
            frame[coverage_name] = np.clip(
                denominator[name][indices] / (7 * total_area), 0, 1).ravel()
        temporary = path.with_name(path.name + ".part")
        try:
            frame.to_parquet(temporary, index=False)
            temporary.replace(path)
        finally:
            temporary.unlink(missing_ok=True)
        print(f"Guardado {path} ({len(frame)} filas, {path.stat().st_size / 2**20:.1f} MiB)", flush=True)
    return paths
