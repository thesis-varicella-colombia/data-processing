"""Descarga únicamente ERA5 atmosférico horario para Providencia desde Earth Data Hub."""

from __future__ import annotations

import argparse
import sys
import time
from datetime import timedelta
from pathlib import Path

import numpy as np
import pandas as pd
import xarray as xr

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts/processing"))
from epidemiological_weeks import weeks_in_range  # noqa: E402
from spatial import inspect_geometries, read_codes  # noqa: E402
from download_era5_land import bbox_slice, credentials_options, longitude_bounds  # noqa: E402

URL = "https://data.earthdatahub.destine.eu/era5/era5-single-levels-atmosphere-v0.zarr"
RAW = ROOT / "data/raw/era5_atmosphere_providencia"
CODE = "88564"
VARIABLES = ("t2m", "d2m", "sp", "tp")
UNITS = {"t2m": "K", "d2m": "K", "sp": "Pa", "tp": "m"}


def month_days(year: int, month: int) -> pd.DatetimeIndex:
    first = pd.Timestamp(year, month, 1)
    return pd.date_range(first, first + pd.offsets.MonthEnd(0), freq="D")


def hourly_times(year: int, month: int) -> pd.DatetimeIndex:
    days = month_days(year, month)
    return pd.date_range(days[0], days[-1] + pd.Timedelta(days=1), freq="h")


def raw_path(year: int, month: int) -> Path:
    return RAW / f"era5_atmosphere_hourly_{year}_{month:02d}.nc"


def months_for_weeks(weeks: list) -> list[tuple[int, int]]:
    first = pd.Timestamp(weeks[0][2])
    last = pd.Timestamp(weeks[-1][2] + timedelta(days=6))
    return [(period.year, period.month) for period in pd.period_range(first, last, freq="M")]


def parse_month(parser: argparse.ArgumentParser, value: str) -> tuple[int, int]:
    try:
        period = pd.Period(value, freq="M")
        if len(value) != 7 or period.year < 1940 or period.year > 2026:
            raise ValueError
    except ValueError:
        parser.error("--month debe tener formato AAAA-MM, entre 1940 y 2026")
    return period.year, period.month


def validate_hourly(path: Path, year: int, month: int) -> tuple[np.ndarray, np.ndarray]:
    if not path.is_file() or path.stat().st_size == 0:
        raise ValueError(f"Archivo ausente o vacío: {path}")
    with xr.open_dataset(path, engine="netcdf4") as ds:
        if set(ds.data_vars) != set(VARIABLES):
            raise ValueError(f"Variables incorrectas en {path}")
        if not {"valid_time", "latitude", "longitude"}.issubset(ds.coords):
            raise ValueError(f"Coordenadas incompletas en {path}")
        if not pd.DatetimeIndex(ds.valid_time.values).equals(hourly_times(year, month)):
            raise ValueError(f"Horas UTC incompletas en {path}")
        for name in VARIABLES:
            if ds[name].dims != ("valid_time", "latitude", "longitude"):
                raise ValueError(f"Dimensiones incorrectas de {name} en {path}")
            if ds[name].attrs.get("units") != UNITS[name]:
                raise ValueError(f"Unidad incorrecta de {name} en {path}")
            if not np.isfinite(ds[name].values).any():
                raise ValueError(f"Sin datos válidos de {name} en {path}")
        return ds.latitude.values.copy(), ds.longitude.values.copy()


def select_region(ds: xr.Dataset, bounds) -> xr.Dataset:
    west, south, east, north = bounds
    west, east = longitude_bounds(ds.longitude.values, west - 0.25, east + 0.25)
    selected = ds[list(VARIABLES)].sel(
        latitude=bbox_slice(ds.latitude.values, south - 0.25, north + 0.25),
        longitude=bbox_slice(ds.longitude.values, west, east))
    if selected.sizes["latitude"] < 2 or selected.sizes["longitude"] < 2:
        raise ValueError("El recorte no contiene suficientes centros de celda")
    return selected


def download_month(source: xr.Dataset, year: int, month: int, overwrite: bool,
                   reference_grid: tuple[np.ndarray, np.ndarray]) -> Path:
    path = raw_path(year, month)
    hours = hourly_times(year, month)
    if path.exists() and not overwrite:
        try:
            grid = validate_hourly(path, year, month)
            if not all(np.array_equal(a, b) for a, b in zip(reference_grid, grid)):
                raise ValueError("La grilla cambió")
            print(f"Ya existe {path.name}; se omite", flush=True)
            return path
        except (ValueError, OSError) as error:
            print(f"Regenerando {path.name}: {error}", flush=True)
    subset = source.sel(valid_time=slice(hours[0], hours[-1]))
    if not pd.DatetimeIndex(subset.valid_time.values).equals(hours):
        raise ValueError(f"Earth Data Hub no cubre {year}-{month:02d}")
    path.parent.mkdir(parents=True, exist_ok=True)
    part = path.with_name(path.name + ".part")
    started = time.monotonic()
    print(f"Descargando {year}-{month:02d}: {len(hours)} horas × "
          f"{subset.sizes['latitude']} × {subset.sizes['longitude']} celdas", flush=True)
    try:
        subset.to_netcdf(part, engine="netcdf4")
        grid = validate_hourly(part, year, month)
        if not all(np.array_equal(a, b) for a, b in zip(reference_grid, grid)):
            raise ValueError(f"La grilla cambió en {year}-{month:02d}")
        part.replace(path)
    finally:
        part.unlink(missing_ok=True)
    print(f"Guardado {path} ({path.stat().st_size / 2**20:.2f} MiB; "
          f"{time.monotonic() - started:.1f} s)", flush=True)
    return path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start-year", type=int, default=2007)
    parser.add_argument("--end-year", type=int, default=2025)
    parser.add_argument("--month", metavar="AAAA-MM", help="Descargar únicamente un mes de prueba")
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--validate-only", action="store_true", help="Mostrar el plan sin consultar el Zarr")
    args = parser.parse_args()
    if args.start_year < 2007 or args.end_year > 2025 or args.start_year > args.end_year:
        parser.error("Los años epidemiológicos deben estar entre 2007 y 2025")
    months = ([parse_month(parser, args.month)] if args.month else
              months_for_weeks(weeks_in_range(args.start_year, args.end_year)))
    codes, bounds = inspect_geometries(set(read_codes()), {CODE})
    if codes != [CODE]:
        raise ValueError("No se encontró Providencia como MUNICIPIO")
    print(f"Providencia {CODE}; bbox={bounds}; {len(months)} meses horarios UTC", flush=True)
    if args.validate_only:
        for year, month in months:
            print(f"{year}-{month:02d} -> {raw_path(year, month)}", flush=True)
        return
    with xr.open_dataset(URL, engine="zarr", zarr_format=3, chunks={},
                         storage_options=credentials_options()) as remote:
        source = select_region(remote, bounds)
        grid = (source.latitude.values.copy(), source.longitude.values.copy())
        print(f"Grilla atmosférica {len(grid[0])} × {len(grid[1])} a 0,25°", flush=True)
        for year, month in months:
            download_month(source, year, month, args.overwrite, grid)


if __name__ == "__main__":
    main()
