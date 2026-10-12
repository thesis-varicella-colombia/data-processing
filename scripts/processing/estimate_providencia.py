"""Deriva días UTC y estima clima semanal de Providencia desde NetCDF horarios.

Los días conservan UTC. La precipitación de 00 UTC cierra el día anterior.
"""

from __future__ import annotations

import argparse
import sys
from datetime import timedelta
from pathlib import Path

import numpy as np
import pandas as pd
import xarray as xr

from calculate_weekly_humidity import calculate as humidity
from calculate_weekly_precipitation import calculate as precipitation
from calculate_weekly_temperature import calculate as temperature
from epidemiological_weeks import day_to_week, weeks_in_range
from spatial import build_weights, inspect_geometries, read_codes

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts/download"))
from download_era5_providencia import (CODE, UNITS, URL, VARIABLES,  # noqa: E402
                                      hourly_times, month_days, months_for_weeks,
                                      parse_month, raw_path, validate_hourly)

PROCESSED = ROOT / "data/processed/climate/providencia"
DAILY = PROCESSED / "daily"
OUTPUTS = {
    "temperature": ("temperatura_media_c",),
    "humidity": ("humedad_relativa_media_pct", "humedad_especifica_media_g_kg",
                 "humedad_absoluta_media_g_m3"),
    "precipitation": ("precipitacion_total_mm",),
}


def daily_path(year: int, month: int) -> Path:
    return DAILY / f"era5_atmosphere_daily_{year}_{month:02d}.nc"


def validate_daily(path: Path, year: int, month: int) -> tuple[np.ndarray, np.ndarray]:
    if not path.is_file() or path.stat().st_size == 0:
        raise ValueError(f"Archivo ausente o vacío: {path}")
    with xr.open_dataset(path, engine="netcdf4") as ds:
        if set(ds.data_vars) != set(VARIABLES):
            raise ValueError(f"Variables incorrectas en {path}")
        if not {"valid_time", "latitude", "longitude"}.issubset(ds.coords):
            raise ValueError(f"Coordenadas incompletas en {path}")
        if not pd.DatetimeIndex(ds.valid_time.values).equals(month_days(year, month)):
            raise ValueError(f"Días UTC incompletos en {path}")
        for name in VARIABLES:
            if ds[name].dims != ("valid_time", "latitude", "longitude"):
                raise ValueError(f"Dimensiones incorrectas de {name} en {path}")
            if ds[name].attrs.get("units") != UNITS[name]:
                raise ValueError(f"Unidad incorrecta de {name} en {path}")
            if not np.isfinite(ds[name].values).any():
                raise ValueError(f"Sin datos válidos de {name} en {path}")
        return ds.latitude.values.copy(), ds.longitude.values.copy()


def write_daily_atomic(ds: xr.Dataset, path: Path, year: int, month: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    part = path.with_name(path.name + ".part")
    try:
        ds.to_netcdf(part, engine="netcdf4")
        validate_daily(part, year, month)
        part.replace(path)
    finally:
        part.unlink(missing_ok=True)


def daily_from_hourly(hourly: xr.Dataset, year: int, month: int) -> xr.Dataset:
    """Instantes 00..23 para medias; tp de 01..00 siguiente para cada día UTC."""
    hours = hourly_times(year, month)
    if not pd.DatetimeIndex(hourly.valid_time.values).equals(hours):
        raise ValueError("Faltan horas para calcular los días UTC completos")
    days = month_days(year, month)
    n = len(days)
    result = {}
    for name in VARIABLES:
        values = np.asarray(hourly[name].values, dtype=np.float64)
        if name == "tp":
            groups = values[1:].reshape(n, 24, *values.shape[1:])
            valid = np.isfinite(groups) & (groups >= -1e-8)
            aggregate = np.where(valid, np.maximum(groups, 0), 0).sum(axis=1)
        else:
            groups = values[:-1].reshape(n, 24, *values.shape[1:])
            valid = np.isfinite(groups)
            aggregate = np.where(valid, groups, 0).sum(axis=1) / 24
        result[name] = (("valid_time", "latitude", "longitude"),
                        np.where(valid.all(axis=1), aggregate, np.nan),
                        dict(hourly[name].attrs))
    return xr.Dataset(result, coords={"valid_time": days, "latitude": hourly.latitude,
                                      "longitude": hourly.longitude},
                      attrs={"source": URL, "day_definition": "00:00–23:59 UTC",
                             "tp_accumulation": "01:00 UTC through next-day 00:00 UTC"})


def derive_month(year: int, month: int, overwrite: bool,
                 reference_grid: tuple[np.ndarray, np.ndarray] | None = None
                 ) -> tuple[np.ndarray, np.ndarray]:
    """Lee el horario local y publica un día UTC por fecha, sin consultar la red."""
    source = raw_path(year, month)
    grid = validate_hourly(source, year, month)
    if reference_grid is not None and not all(
            np.array_equal(a, b) for a, b in zip(reference_grid, grid)):
        raise ValueError(f"La grilla horaria cambió en {source}")
    destination = daily_path(year, month)
    if destination.exists() and not overwrite:
        try:
            daily_grid = validate_daily(destination, year, month)
            if not all(np.array_equal(a, b) for a, b in zip(grid, daily_grid)):
                raise ValueError("La grilla diaria difiere de la horaria")
            print(f"Ya existe {destination.name}; se omite", flush=True)
            return grid
        except (ValueError, OSError) as error:
            print(f"Regenerando {destination.name}: {error}", flush=True)
    with xr.open_dataset(source, engine="netcdf4") as hourly:
        daily = daily_from_hourly(hourly, year, month)
        write_daily_atomic(daily, destination, year, month)
    print(f"Derivado {destination} ({destination.stat().st_size / 2**20:.2f} MiB)", flush=True)
    return grid


def _normalise_longitudes(longitudes: np.ndarray) -> np.ndarray:
    if np.nanmin(longitudes) >= 0 and np.nanmax(longitudes) > 180:
        return ((longitudes + 180) % 360) - 180
    return longitudes


def process(weeks, bounds, name: str, overwrite: bool) -> list[Path]:
    years = sorted({year for year, _, _ in weeks})
    paths = [PROCESSED / name / f"{name}_weekly_providencia_{year}.parquet" for year in years]
    lookup = day_to_week(weeks)
    months = months_for_weeks(weeks)
    missing = [daily_path(y, m) for y, m in months if not daily_path(y, m).is_file()]
    if missing:
        raise FileNotFoundError(f"Falta {missing[0]}")
    outputs = OUTPUTS[name]
    numerator = {v: np.zeros(len(weeks)) for v in outputs}
    denominator = {v: np.zeros(len(weeks)) for v in outputs}
    valid_days = {v: np.zeros(len(weeks), dtype=np.int8) for v in outputs}
    reference_grid = None
    weights = None
    observed = set()
    names = read_codes()
    for year, month in months:
        path = daily_path(year, month)
        grid = validate_daily(path, year, month)
        if reference_grid is None:
            reference_grid = grid
            weights = build_weights(grid[0], _normalise_longitudes(grid[1]), [CODE], bounds)
        elif not all(np.array_equal(a, b) for a, b in zip(reference_grid, grid)):
            raise ValueError(f"Cambió la grilla en {path}")
        y, x, _, area, total_area = weights
        with xr.open_dataset(path, engine="netcdf4") as ds:
            dates = pd.DatetimeIndex(ds.valid_time.values)
            indices = [i for i, stamp in enumerate(dates) if stamp.date() in lookup]
            if not indices:
                continue
            observed.update(dates[i].date() for i in indices)
            values = {v: np.asarray(ds[v].isel(valid_time=indices).values, dtype=np.float64)
                      for v in VARIABLES}
        if name == "temperature":
            calculated = temperature(values)
        elif name == "humidity":
            calculated = humidity(values)
        else:
            calculated = precipitation(values)
        week_idx = np.array([lookup[dates[i].date()] for i in indices])
        for output, array in calculated.items():
            selected = array[:, y, x]
            valid = np.isfinite(selected)
            day_den = (valid * area).sum(axis=1)
            day_num = np.where(valid, selected, 0).dot(area)
            if name == "precipitation":
                day_mean = np.divide(day_num, day_den, out=np.zeros_like(day_num),
                                     where=day_den > 0)
                np.add.at(numerator[output], week_idx, day_mean)
                np.add.at(valid_days[output], week_idx, day_den > 0)
            else:
                np.add.at(numerator[output], week_idx, day_num)
            np.add.at(denominator[output], week_idx, day_den)
        print(f"Procesado {year}-{month:02d} ({name})", flush=True)
    if observed != set(lookup):
        raise ValueError(f"Faltan {len(set(lookup) - observed)} días para semanas completas")
    for year, path in zip(years, paths):
        indices = [i for i, (y, _, _) in enumerate(weeks) if y == year]
        selected_weeks = [weeks[i] for i in indices]
        if path.exists() and not overwrite:
            existing = pd.read_parquet(path)
            if (len(existing) != len(indices) or
                    not ({"codigo_municipio", "ano_epidemiologico", "fuente_dato",
                          "es_estimacion"} | set(OUTPUTS[name])).issubset(existing.columns) or
                    not (existing["codigo_municipio"] == CODE).all() or
                    not (existing["ano_epidemiologico"] == year).all() or
                    not (existing["fuente_dato"] == "ERA5_atmosphere_hourly_EDH").all() or
                    not existing["es_estimacion"].all()):
                raise ValueError(f"Salida existente incompleta: {path}; use --overwrite")
            print(f"Ya existe {path.name}; se omite", flush=True)
            continue
        frame = pd.DataFrame({
            "codigo_municipio": CODE,
            "nombre_municipio": names[CODE],
            "ano_epidemiologico": year,
            "semana_epidemiologica": [number for _, number, _ in selected_weeks],
            "inicio_semana": [start.isoformat() for _, _, start in selected_weeks],
            "fin_semana": [(start + timedelta(days=6)).isoformat() for _, _, start in selected_weeks],
            "fuente_dato": "ERA5_atmosphere_hourly_EDH",
            "es_estimacion": True,
        })
        for output in outputs:
            if name == "precipitation":
                result = numerator[output][indices].copy()
                result[valid_days[output][indices] != 7] = np.nan
            else:
                result = np.divide(numerator[output][indices], denominator[output][indices],
                                   out=np.full(len(indices), np.nan),
                                   where=denominator[output][indices] > 0)
            frame[output] = result
            coverage = ("fraccion_area_con_datos" if len(outputs) == 1 else
                        f"fraccion_area_con_datos_{output}")
            frame[coverage] = np.clip(denominator[output][indices] / (7 * total_area[0]), 0, 1)
        path.parent.mkdir(parents=True, exist_ok=True)
        part = path.with_name(path.name + ".part")
        try:
            frame.to_parquet(part, index=False)
            part.replace(path)
        finally:
            part.unlink(missing_ok=True)
        print(f"Guardado {path} ({len(frame)} semanas; {path.stat().st_size} bytes)", flush=True)
    return paths


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start-year", type=int, default=2007)
    parser.add_argument("--end-year", type=int, default=2025)
    parser.add_argument("--month", metavar="AAAA-MM", help="Derivar un mes diario de prueba, sin semanas")
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--validate-only", action="store_true", help="Comprobar archivos horarios requeridos")
    args = parser.parse_args()
    if args.start_year < 2007 or args.end_year > 2025 or args.start_year > args.end_year:
        parser.error("Los años epidemiológicos deben estar entre 2007 y 2025")
    month = parse_month(parser, args.month) if args.month else None
    names = read_codes()
    codes, bounds = inspect_geometries(set(names), {CODE})
    if codes != [CODE]:
        raise ValueError("No se encontró Providencia como MUNICIPIO")
    weeks = weeks_in_range(args.start_year, args.end_year)
    months = [month] if month else months_for_weeks(weeks)
    missing = [raw_path(year, number) for year, number in months
               if not raw_path(year, number).is_file()]
    print(f"Providencia {CODE}; bbox={bounds}; {len(months)} meses horarios locales; "
          f"faltan {len(missing)}", flush=True)
    if args.validate_only:
        for path in missing:
            print(f"Falta {path}", flush=True)
        return
    if missing:
        raise FileNotFoundError(f"Falta {missing[0]}; ejecute scripts/download/download_era5_providencia.py")
    grid = None
    for year, number in months:
        grid = derive_month(year, number, args.overwrite, grid)
    if not month:
        for name in OUTPUTS:
            process(weeks, bounds, name, args.overwrite)


if __name__ == "__main__":
    main()
