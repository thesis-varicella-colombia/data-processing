"""Descarga ERA5-Land Daily UTC de Earth Data Hub, sin transformación temporal."""

from __future__ import annotations

import argparse
import calendar
import os
import sys
import time
from datetime import date
from netrc import NetrcParseError, netrc
from pathlib import Path

import numpy as np
import pandas as pd
import xarray as xr
from aiohttp import BasicAuth


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts/processing"))
from spatial import inspect_geometries, read_codes  # noqa: E402


URL = "https://data.earthdatahub.destine.eu/era5/era5-land-daily-utc-v1.zarr"
HOST = "data.earthdatahub.destine.eu"
OUTPUT = ROOT / "data/raw/era5_land"
VARIABLES = ("t2m", "d2m", "sp", "tp")
UNITS = {"t2m": "K", "d2m": "K", "sp": "Pa", "tp": "m"}


def credentials_options() -> dict:
    key = os.getenv("EARTHDATAHUB_API_KEY") or os.getenv("EDH_API_KEY")
    if key:
        return {"client_kwargs": {"auth": BasicAuth("edh", key), "trust_env": True}}
    try:
        credential = netrc().authenticators(HOST)
    except NetrcParseError as error:
        raise RuntimeError("~/.netrc debe tener permisos 600 y formato válido") from error
    except OSError:
        credential = None
    if credential is None or not credential[2]:
        raise RuntimeError("Configure EARTHDATAHUB_API_KEY o ~/.netrc para " + HOST)
    return {"client_kwargs": {"trust_env": True}}


def bbox_slice(values: np.ndarray, minimum: float, maximum: float) -> slice:
    return slice(minimum, maximum) if float(values[0]) < float(values[-1]) else slice(maximum, minimum)


def longitude_bounds(values: np.ndarray, west: float, east: float) -> tuple[float, float]:
    """Adapta Colombia a la convención 0..360 si la grilla la emplea."""
    if np.nanmin(values) >= 0 and np.nanmax(values) > 180:
        return west % 360, east % 360
    return west, east


def select_region(ds: xr.Dataset, bounds: tuple[float, float, float, float]) -> xr.Dataset:
    if not {"latitude", "longitude", "valid_time"}.issubset(ds.coords):
        raise ValueError("El Zarr no tiene coordenadas latitude/longitude/valid_time")
    missing = set(VARIABLES) - set(ds.data_vars)
    if missing:
        raise ValueError(f"Faltan variables en Earth Data Hub: {sorted(missing)}")
    west, south, east, north = bounds
    west, east = longitude_bounds(ds.longitude.values, west - 0.1, east + 0.1)
    subset = ds[list(VARIABLES)].sel(
        latitude=bbox_slice(ds.latitude.values, south - 0.1, north + 0.1),
        longitude=bbox_slice(ds.longitude.values, west, east),
    )
    if subset.sizes["latitude"] < 2 or subset.sizes["longitude"] < 2:
        raise ValueError("La selección geográfica quedó vacía o demasiado pequeña")
    return subset


def expected_dates(year: int, month: int | None = None) -> pd.DatetimeIndex:
    start = date(year, month or 1, 1)
    end = date(year, month, calendar.monthrange(year, month)[1]) if month else date(year, 12, 31)
    return pd.date_range(start, end, freq="D")


def validate_netcdf(path: Path, year: int, month: int | None = None,
                    expected_grid: tuple[np.ndarray, np.ndarray] | None = None) -> tuple[int, int, int]:
    if not path.is_file() or path.stat().st_size == 0:
        raise ValueError(f"Archivo ausente o vacío: {path}")
    with xr.open_dataset(path, engine="netcdf4") as ds:
        if set(ds.data_vars) != set(VARIABLES):
            raise ValueError(f"Variables inesperadas: {list(ds.data_vars)}")
        if not {"valid_time", "latitude", "longitude"}.issubset(ds.coords):
            raise ValueError("Faltan coordenadas valid_time/latitude/longitude")
        dates = pd.DatetimeIndex(ds.valid_time.values)
        if not dates.equals(expected_dates(year, month)):
            raise ValueError("La dimensión temporal no cubre exactamente los días solicitados en UTC")
        if any(ds[name].dims != ("valid_time", "latitude", "longitude") for name in VARIABLES):
            raise ValueError("Dimensiones de variables incompatibles")
        for name, unit in UNITS.items():
            if ds[name].attrs.get("units") != unit:
                raise ValueError(f"Unidad inesperada de {name}: {ds[name].attrs.get('units')}")
        lat, lon = ds.latitude.values, ds.longitude.values
        if len(lat) < 2 or len(lon) < 2 or not np.isfinite(lat).all() or not np.isfinite(lon).all():
            raise ValueError("Grilla espacial inválida")
        if expected_grid is not None and not (np.array_equal(lat, expected_grid[0]) and
                                              np.array_equal(lon, expected_grid[1])):
            raise ValueError("La grilla cambió respecto a otro año")
        # Leer todos los bloques comprueba que el payload NetCDF se puede recuperar,
        # además de verificar que la cabecera enumera los días y variables correctos.
        for name in VARIABLES:
            has_data = False
            for start in range(0, len(dates), 31):
                values = ds[name].isel(valid_time=slice(start, start + 31)).values
                has_data |= bool(np.isfinite(values).any())
            if not has_data:
                raise ValueError(f"{name} no contiene ningún dato válido")
        return len(dates), len(lat), len(lon)


def output_path(year: int, month: int | None = None) -> Path:
    suffix = f"_{month:02d}" if month is not None else ""
    return OUTPUT / f"era5_land_daily_{year}{suffix}.nc"


def download_period(source: xr.Dataset, year: int, month: int | None,
                    overwrite: bool, expected_grid: tuple[np.ndarray, np.ndarray]) -> None:
    output = output_path(year, month)
    if output.exists() and not overwrite:
        try:
            shape = validate_netcdf(output, year, month, expected_grid)
        except (OSError, ValueError, KeyError) as error:
            print(f"Archivo existente incompleto; se reemplazará: {output} ({error})", flush=True)
        else:
            print(f"Ya existe {output.name}: {shape}; se omite", flush=True)
            return
    dates = expected_dates(year, month)
    subset = source.sel(valid_time=slice(dates[0], dates[-1]))
    if not pd.DatetimeIndex(subset.valid_time.values).equals(dates):
        raise ValueError(f"Earth Data Hub no contiene todos los días de {year}" +
                         (f"-{month:02d}" if month else ""))
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_name(output.name + ".part")
    start = time.monotonic()
    print(f"Descargando {output.name}: {len(dates)} días, "
          f"{subset.sizes['latitude']} × {subset.sizes['longitude']} celdas", flush=True)
    try:
        temporary.unlink(missing_ok=True)
        subset.chunk({"valid_time": 15}).to_netcdf(temporary, engine="netcdf4")
        shape = validate_netcdf(temporary, year, month, expected_grid)
        temporary.replace(output)
    finally:
        temporary.unlink(missing_ok=True)
    print(f"Guardado {output} ({output.stat().st_size / 2**20:.1f} MiB, "
          f"dimensiones={shape}, {time.monotonic() - start:.1f} s)", flush=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start-year", type=int, default=2007)
    parser.add_argument("--end-year", type=int, default=2025)
    parser.add_argument("--month", metavar="AAAA-MM", help="Prueba de un mes; salida separada del archivo anual")
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--validate-only", action="store_true", help="Validar geometría y mostrar el plan sin acceder al Zarr")
    args = parser.parse_args()
    if args.start_year < 1950 or args.end_year > 2026 or args.start_year > args.end_year:
        parser.error("El intervalo debe estar entre 1950 y 2026 y en orden ascendente")
    month = None
    years = range(args.start_year, args.end_year + 1)
    if args.month:
        try:
            year_text, month_text = args.month.split("-")
            year, month = int(year_text), int(month_text)
            if len(args.month) != 7 or not 1 <= month <= 12 or not 1950 <= year <= 2026:
                raise ValueError
        except ValueError:
            parser.error("--month debe tener formato AAAA-MM, entre 1950 y 2026")
        years = range(year, year + 1)
    elif args.end_year == 2026:
        parser.error("El año 2026 aún no está completo; use --month 2026-01 para el borde")
    codes, bounds = inspect_geometries(set(read_codes()))
    print(f"Geografía válida: {len(codes)} municipios; bbox={bounds}; "
          f"períodos={years.start}–{years.stop - 1}; día UTC=00:00–23:59", flush=True)
    if args.validate_only:
        return
    options = credentials_options()
    with xr.open_dataset(URL, engine="zarr", zarr_format=3, chunks={},
                         storage_options=options) as remote:
        source = select_region(remote, bounds)
        grid = (source.latitude.values.copy(), source.longitude.values.copy())
        print(f"Subconjunto: latitude={len(grid[0])}, longitude={len(grid[1])}; "
              f"longitudes={float(grid[1][0]):.2f}..{float(grid[1][-1]):.2f}", flush=True)
        for year in years:
            download_period(source, year, month, args.overwrite, grid)


if __name__ == "__main__":
    main()
