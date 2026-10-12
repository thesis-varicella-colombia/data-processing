"""Geometrías DANE y pesos de intersección geodésica municipio × celda."""

from __future__ import annotations

import csv
from pathlib import Path

import ijson
import numpy as np
from pyproj import Geod
from shapely import box
from shapely.geometry import shape
from shapely.strtree import STRtree


ROOT = Path(__file__).resolve().parents[2]
MUNICIPALITIES = ROOT / "data/raw/municipios"
DIVIPOLA = MUNICIPALITIES / "DIVIPOLA-_Códigos_municipios_20261007.csv"
GEOJSON = MUNICIPALITIES / "MGN_ADM_MPIO_GRAFICO.geojson"


def read_codes() -> dict[str, str]:
    with DIVIPOLA.open(encoding="utf-8-sig", newline="") as source:
        rows = list(csv.DictReader(source))
    codes = [row["Código Municipio"] for row in rows]
    if len(codes) != len(set(codes)) or any(len(code) != 5 for code in codes):
        raise ValueError("DIVIPOLA contiene códigos duplicados o inválidos")
    return {row["Código Municipio"]: row["Nombre Municipio"] for row in rows}


def features():
    with GEOJSON.open("rb") as source:
        yield from ijson.items(source, "features.item")


def inspect_geometries(csv_codes: set[str], requested: set[str] | None = None):
    with GEOJSON.open("rb") as source:
        crs = next(ijson.items(source, "crs"), None)
    if crs != {"type": "name", "properties": {"name": "urn:ogc:def:crs:OGC:1.3:CRS84"}}:
        raise ValueError("El GeoJSON debe estar en CRS84 (longitud, latitud)")
    seen: set[str] = set()
    selected: list[str] = []
    west, south, east, north = 180.0, 90.0, -180.0, -90.0
    for feature in features():
        properties = feature["properties"]
        code = properties["mpio_cdpmp"]
        if code in seen:
            raise ValueError(f"Código duplicado en GeoJSON: {code}")
        seen.add(code)
        geometry = shape(feature["geometry"])
        if geometry.is_empty or not geometry.is_valid:
            raise ValueError(f"Geometría vacía o inválida: {code}")
        if properties["mpio_tipo"] == "MUNICIPIO" and (requested is None or code in requested):
            selected.append(code)
            x1, y1, x2, y2 = geometry.bounds
            west, south = min(west, x1), min(south, y1)
            east, north = max(east, x2), max(north, y2)
    if seen != csv_codes:
        raise ValueError(f"Códigos sin pareja entre CSV y GeoJSON: "
                         f"CSV={len(csv_codes - seen)}, GeoJSON={len(seen - csv_codes)}")
    if not selected or (requested is not None and requested != set(selected)):
        raise ValueError("No hay municipios válidos para la selección solicitada")
    return sorted(selected), (west, south, east, north)


def axis_indices(values: np.ndarray, minimum: float, maximum: float) -> range:
    if len(values) < 2:
        raise ValueError("La grilla necesita al menos dos coordenadas por eje")
    half_cell = abs(float(np.median(np.diff(values)))) / 2
    indices = np.flatnonzero((values + half_cell >= minimum) &
                             (values - half_cell <= maximum))
    if len(indices) == 0:
        raise ValueError("El área municipal está fuera de la grilla ERA5-Land")
    return range(int(indices[0]), int(indices[-1]) + 1)


def build_weights(latitudes: np.ndarray, longitudes: np.ndarray,
                  codes: list[str], bounds):
    """Devuelve índices de celda, municipio y áreas reales de intersección (m²)."""
    lat_range = axis_indices(latitudes, bounds[1], bounds[3])
    lon_range = axis_indices(longitudes, bounds[0], bounds[2])
    lat_half = abs(float(np.median(np.diff(latitudes)))) / 2
    lon_half = abs(float(np.median(np.diff(longitudes)))) / 2
    cells = [box(float(longitudes[x] - lon_half), float(latitudes[y] - lat_half),
                 float(longitudes[x] + lon_half), float(latitudes[y] + lat_half))
             for y in lat_range for x in lon_range]
    cell_indices = [(y, x) for y in lat_range for x in lon_range]
    tree = STRtree(cells)
    positions = {code: i for i, code in enumerate(codes)}
    geod = Geod(ellps="WGS84")
    rows = []
    total_area = np.zeros(len(codes), dtype=np.float64)
    for feature in features():
        code = feature["properties"]["mpio_cdpmp"]
        if code not in positions:
            continue
        municipality = shape(feature["geometry"])
        for cell_index in tree.query(municipality, predicate="intersects"):
            cell_index = int(cell_index)
            overlap = municipality.intersection(cells[cell_index])
            if overlap.is_empty:
                continue
            area = abs(geod.geometry_area_perimeter(overlap)[0])
            if area > 0:
                y, x = cell_indices[cell_index]
                rows.append((y, x, positions[code], area))
                total_area[positions[code]] += area
    if np.any(total_area == 0):
        raise ValueError(f"Municipios sin grilla: "
                         f"{[codes[i] for i in np.flatnonzero(total_area == 0)]}")
    y, x, municipality, area = map(np.asarray, zip(*rows))
    return (y.astype(np.int32), x.astype(np.int32), municipality.astype(np.int32),
            area.astype(np.float64), total_area)
