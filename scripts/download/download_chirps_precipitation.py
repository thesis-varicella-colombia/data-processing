"""Descarga CHIRPS v3 Final/rnl y completa los días de borde de 2007–2025."""

from __future__ import annotations

import argparse
import csv
import logging
import re
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import requests
import numpy as np
import xarray as xr
from PIL import Image


LOGGER = logging.getLogger(__name__)
ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / "data/raw/precipitation/chirps"
BASE_URL = (
    "https://data.chc.ucsb.edu/products/CHIRPS/v3.0/"
    "daily/final/rnl/netcdf/byYear"
)
DAILY_TIFF_BASE = "https://data.chc.ucsb.edu/products/CHIRPS/v3.0/daily/final/rnl"
CHUNK_SIZE = 1024 * 1024
MAX_ATTEMPTS = 4
TIMEOUT = (15, 90)  # conexión, lectura de cada bloque (segundos)
MANIFEST_COLUMNS = ("year", "filename", "source_url", "downloaded_at_utc", "bytes")
MANIFEST_LOCK = threading.Lock()
RANGE_OVERLAP = 64 * 1024
FIRST_BORDER = date(2006, 12, 31)
LAST_BORDER = (date(2026, 1, 1), date(2026, 1, 2), date(2026, 1, 3))
REFERENCE_YEARS = range(2007, 2026)


def filename_for(year: int) -> str:
    """Devuelve el nombre publicado por CHC para un año de CHIRPS v3 rnl."""
    return f"chirps-v3.0.rnl.{year}.days_p05.nc"


def url_for(year: int) -> str:
    return f"{BASE_URL}/{filename_for(year)}"


def validate_netcdf(path: Path, year: int, days: tuple[date, ...] | None = None) -> None:
    """Comprueba cabecera, variable diaria y calendario sin cargar toda la grilla."""
    if not path.is_file() or path.stat().st_size == 0:
        raise ValueError(f"Archivo vacío o ausente: {path}")
    with xr.open_dataset(path, engine="netcdf4") as dataset:
        if "time" not in dataset.coords:
            raise ValueError(f"Falta la coordenada time en {path}")
        if not any("time" in field.dims for field in dataset.data_vars.values()):
            raise ValueError(f"No hay una variable diaria en {path}")
        first = date(year, 1, 1)
        expected = ([day.isoformat() for day in days] if days is not None else
                    [(first + timedelta(days=offset)).isoformat()
                     for offset in range((date(year + 1, 1, 1) - first).days)])
        actual = list(dataset["time"].dt.strftime("%Y-%m-%d").values)
        if actual != expected:
            raise ValueError(f"El calendario diario de {path} no cubre todo {year}")


def valid_existing(path: Path, year: int, days: tuple[date, ...] | None = None) -> bool:
    """Permite reanudar sin descargar otra vez un año aparentemente completo."""
    if not path.exists():
        return False
    try:
        validate_netcdf(path, year, days)
    except (OSError, ValueError, KeyError, TypeError, AttributeError) as error:
        LOGGER.warning("Archivo local inválido; se descargará de nuevo: %s (%s)", path, error)
        return False
    return True


def border_path(output_dir: Path, year: int) -> Path:
    kind = "observed" if year == 2006 else "imputed"
    return output_dir / str(year) / f"chirps-v3.0.rnl.{year}.epidemiological-border.{kind}.nc"


def first_border_tiff_url() -> str:
    return f"{DAILY_TIFF_BASE}/2006/chirps-v3.0.rnl.2006.12.31.tif"


def first_border_tiff_path(output_dir: Path) -> Path:
    return output_dir / "2006" / "chirps-v3.0.rnl.2006.12.31.tif"


def write_border(dataset: xr.Dataset, destination: Path, year: int,
                 days: tuple[date, ...]) -> Path:
    """Publica un recorte o imputación solo si el calendario es correcto."""
    destination.parent.mkdir(parents=True, exist_ok=True)
    part = destination.with_name(destination.name + ".part")
    try:
        encoding = {name: {"zlib": True, "complevel": 4}
                    for name in dataset.data_vars}
        dataset.to_netcdf(part, engine="netcdf4", encoding=encoding)
        validate_netcdf(part, year, days)
        part.replace(destination)
    finally:
        part.unlink(missing_ok=True)
    return destination


def download_first_border(session: requests.Session, output_dir: Path) -> Path:
    """Convierte el GeoTIFF diario oficial de 2006-12-31 al NetCDF de borde."""
    destination = border_path(output_dir, 2006)
    if valid_existing(destination, 2006, (FIRST_BORDER,)):
        return destination
    reference = output_dir / "2007" / filename_for(2007)
    if not valid_existing(reference, 2007):
        raise FileNotFoundError(f"Se requiere 2007 para validar la grilla del GeoTIFF: {reference}")
    tiff = first_border_tiff_path(output_dir)
    part = tiff.with_name(tiff.name + ".part")
    if not tiff.is_file():
        tiff.parent.mkdir(parents=True, exist_ok=True)
        for attempt in range(1, MAX_ATTEMPTS + 1):
            try:
                stream_to_part(session, first_border_tiff_url(), part)
                with Image.open(part) as image:
                    image.verify()
                part.replace(tiff)
                break
            except (requests.RequestException, OSError, ValueError) as error:
                if (isinstance(error, requests.HTTPError) and error.response is not None
                        and error.response.status_code < 500
                        and error.response.status_code != 429):
                    raise
                if attempt == MAX_ATTEMPTS:
                    raise RuntimeError("No se pudo descargar el GeoTIFF de 2006-12-31") from error
                time.sleep(min(2 ** attempt, 30))
    with xr.open_dataset(reference, engine="netcdf4") as annual:
        lat = annual.latitude.values.copy()
        lon = annual.longitude.values.copy()
        precip_attrs = dict(annual.precip.attrs)
    with Image.open(tiff) as image:
        if image.size != (len(lon), len(lat)):
            raise ValueError(f"La grilla del GeoTIFF no coincide con 2007: {image.size}")
        pixel = image.tag_v2.get(33550)
        tie = image.tag_v2.get(33922)
        if not pixel or not tie or not np.isclose(pixel[0], 0.05, atol=1e-6) or not np.isclose(pixel[1], 0.05, atol=1e-6):
            raise ValueError("Resolución GeoTIFF inesperada")
        west, north = float(tie[3]), float(tie[4])
        if not (np.isclose(lon[0], west + pixel[0] / 2, atol=1e-3) and
                np.isclose(lon[-1], west + (len(lon) - 0.5) * pixel[0], atol=1e-3) and
                np.isclose(lat[-1], north - pixel[1] / 2, atol=1e-3) and
                np.isclose(lat[0], north - (len(lat) - 0.5) * pixel[1], atol=1e-3)):
            raise ValueError("Las coordenadas GeoTIFF difieren del NetCDF de 2007")
        values = np.asarray(image, dtype=np.float32)[::-1].copy()
    values[values == -9999] = np.nan
    if not np.isfinite(values).any() or np.any(np.isfinite(values) & (values < 0)):
        raise ValueError("Precipitación inválida en el GeoTIFF de 2006-12-31")
    selected = xr.Dataset(
        {"precip": (("time", "latitude", "longitude"), values[None], precip_attrs)},
        coords={"time": np.array([FIRST_BORDER], dtype="datetime64[ns]"),
                "latitude": lat, "longitude": lon},
        attrs={"border_data_status": "observed_CHIRPS_v3_Final_rnl",
               "source_url": first_border_tiff_url(), "source_format": "GeoTIFF",
               "source_day": FIRST_BORDER.isoformat()})
    result = write_border(selected, destination, 2006, (FIRST_BORDER,))
    LOGGER.info("Borde observado 2006 desde GeoTIFF diario: %s", result)
    return result


def impute_last_border(output_dir: Path) -> Path:
    """Media por celda y día calendario de 2007–2025, ignorando faltantes."""
    destination = border_path(output_dir, 2026)
    if valid_existing(destination, 2026, LAST_BORDER):
        return destination
    sources = [output_dir / str(year) / filename_for(year) for year in REFERENCE_YEARS]
    for year, source in zip(REFERENCE_YEARS, sources):
        if not valid_existing(source, year):
            raise FileNotFoundError(f"Falta un año válido para la imputación: {source}")

    total = count = reference_grid = None
    precip_attrs = None
    for year, source in zip(REFERENCE_YEARS, sources):
        with xr.open_dataset(source, engine="netcdf4") as dataset:
            if "precip" not in dataset:
                raise ValueError(f"Falta precip en {source}")
            grid = (dataset.latitude.values, dataset.longitude.values)
            if reference_grid is None:
                reference_grid = tuple(axis.copy() for axis in grid)
                precip_attrs = dict(dataset.precip.attrs)
            elif not all(np.array_equal(a, b) for a, b in zip(reference_grid, grid)):
                raise ValueError(f"La grilla difiere en {source}")
            values = dataset.precip.sel(time=[f"{year}-01-0{day}" for day in (1, 2, 3)]).values
            valid = np.isfinite(values) & (values >= 0)
            if total is None:
                total = np.zeros(values.shape, dtype=np.float64)
                count = np.zeros(values.shape, dtype=np.uint8)
            total += np.where(valid, values, 0)
            count += valid.astype(np.uint8)
    estimate = np.full(total.shape, np.nan, dtype=np.float32)
    np.divide(total, count, out=estimate, where=count > 0, casting="unsafe")
    template = xr.Dataset(coords={
        "time": np.array(LAST_BORDER, dtype="datetime64[ns]"),
        "latitude": reference_grid[0], "longitude": reference_grid[1],
    })
    template["precip"] = (("time", "latitude", "longitude"), estimate, precip_attrs)
    template.attrs = {
        "title": "CHIRPS v3 Final/rnl: días de borde epidemiológico imputados",
        "border_data_status": "imputed_not_observed",
        "imputation_method": "media aritmética por celda y día calendario; valores finitos >= 0",
        "reference_years": "2007-2025",
        "reference_product": "CHIRPS v3.0 Final/rnl daily",
        "minimum_valid_years_per_cell_day": "1",
        "missing_reference_rule": "NaN si no hay ningún año válido para la celda y fecha",
    }
    return write_border(template, destination, 2026, LAST_BORDER)


def stream_to_part(session: requests.Session, url: str, part: Path) -> None:
    """Continúa .part por HTTP Range; compara el solapamiento antes de añadir bytes."""
    with session.head(url, timeout=TIMEOUT, allow_redirects=True) as metadata:
        metadata.raise_for_status()
        total_size = int(metadata.headers.get("Content-Length", "0"))
    if total_size <= 0:
        raise ValueError(f"El servidor no informó el tamaño de {url}")
    existing = part.stat().st_size if part.exists() else 0
    if existing > total_size:
        raise ValueError(f".part mayor que la fuente: {existing}/{total_size}; conservar para revisión")
    if existing == total_size:
        LOGGER.info("%s: transferencia completa; se validará", part.name)
        return
    overlap = min(existing, RANGE_OVERLAP)
    start = existing - overlap
    headers = {"Range": f"bytes={start}-"} if existing else {}
    with session.get(url, headers=headers, stream=True, timeout=TIMEOUT) as response:
        response.raise_for_status()
        if existing:
            content_range = response.headers.get("Content-Range", "")
            match = re.fullmatch(r"bytes (\d+)-(\d+)/(\d+)", content_range)
            if response.status_code != 206 or not match or int(match[1]) != start or int(match[3]) != total_size:
                raise ValueError(f"El servidor no aceptó la reanudación de {part.name}: {content_range}")
            with part.open("rb") as source:
                source.seek(start)
                original_tail = source.read(overlap)
            LOGGER.info("Reanudando %s desde %.1f%% (%d/%d bytes)", part.name,
                        existing * 100 / total_size, existing, total_size)
        elif response.status_code != 200 or int(response.headers.get("Content-Length", "0")) != total_size:
            raise ValueError(f"Respuesta HTTP inesperada para {url}")
        downloaded = existing
        compared = 0
        next_report = ((downloaded * 10 // total_size) + 1) * 10
        with part.open("ab" if existing else "wb") as destination:
            for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                if not chunk:
                    continue
                if compared < overlap:
                    check = min(len(chunk), overlap - compared)
                    if chunk[:check] != original_tail[compared:compared + check]:
                        raise ValueError(f"La fuente cambió o el .part no corresponde a {url}")
                    compared += check
                    chunk = chunk[check:]
                if not chunk:
                    continue
                destination.write(chunk)
                downloaded += len(chunk)
                if next_report <= 100 and downloaded * 100 >= next_report * total_size:
                    LOGGER.info("%s: %d%% (%d bytes)", part.name, next_report, downloaded)
                    next_report += 10
        if compared != overlap:
            raise IOError(f"No se pudo verificar el solapamiento de {part.name}")
        if downloaded != total_size:
            raise IOError(f"Descarga incompleta: {downloaded}/{total_size} bytes ({url})")


def download_year(session: requests.Session, year: int, output_dir: Path) -> Path:
    """Descarga, valida y publica un año; reintenta fallos transitorios."""
    destination = output_dir / str(year) / filename_for(year)
    if valid_existing(destination, year):
        LOGGER.info("Ya existe y es válido: %s", destination)
        return destination

    destination.parent.mkdir(parents=True, exist_ok=True)
    part = destination.with_name(destination.name + ".part")
    url = url_for(year)
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            LOGGER.info("Descargando %d (%d/%d): %s", year, attempt, MAX_ATTEMPTS, url)
            stream_to_part(session, url, part)
            validate_netcdf(part, year)
            part.replace(destination)
            record_download(output_dir, year, destination, url)
            LOGGER.info("Guardado: %s (%d bytes)", destination, destination.stat().st_size)
            return destination
        except (requests.RequestException, OSError, ValueError) as error:
            if (isinstance(error, requests.HTTPError) and error.response is not None
                    and error.response.status_code < 500
                    and error.response.status_code != 429):
                raise
            if attempt == MAX_ATTEMPTS:
                raise RuntimeError(f"No se pudo descargar {year} tras {MAX_ATTEMPTS} intentos") from error
            wait = min(2 ** attempt, 30)
            LOGGER.warning("Error en %d: %s. Reintento en %d s", year, error, wait)
            time.sleep(wait)
    raise AssertionError("No se alcanzó una salida del ciclo de descarga")


def record_download(output_dir: Path, year: int, path: Path, url: str) -> None:
    """Registra la fecha real de descarga sin modificar los NetCDF originales."""
    manifest = output_dir / "download_manifest.csv"
    with MANIFEST_LOCK:
        rows: dict[int, dict[str, str]] = {}
        if manifest.exists():
            with manifest.open(newline="", encoding="utf-8") as source:
                rows = {int(row["year"]): row for row in csv.DictReader(source)}
        rows[year] = {
            "year": str(year),
            "filename": path.name,
            "source_url": url,
            "downloaded_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "bytes": str(path.stat().st_size),
        }
        temporary = manifest.with_name(manifest.name + ".part")
        try:
            with temporary.open("w", newline="", encoding="utf-8") as output:
                writer = csv.DictWriter(output, fieldnames=MANIFEST_COLUMNS)
                writer.writeheader()
                writer.writerows(rows[year] for year in sorted(rows))
            temporary.replace(manifest)
        finally:
            temporary.unlink(missing_ok=True)


def download_year_worker(year: int, output_dir: Path) -> Path:
    """Cada hilo crea su propia sesión HTTP; solo el manifiesto es compartido."""
    with requests.Session() as session:
        session.headers.update({"User-Agent": "data-processing-thesis/1.0 (CHIRPS download)"})
        return download_year(session, year, output_dir)


def download_first_border_worker(output_dir: Path) -> Path:
    """Permite obtener el borde de 2006 junto a otros años pendientes."""
    with requests.Session() as session:
        session.headers.update({"User-Agent": "data-processing-thesis/1.0 (CHIRPS download)"})
        return download_first_border(session, output_dir)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start-year", type=int, default=2007)
    parser.add_argument("--end-year", type=int, default=2025)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--workers", type=int, default=1,
                        help="Descargas anuales simultáneas (1–4; recomendado: 2)")
    parser.add_argument("--include-2006-border", action="store_true",
                        help="Obtener 2006-12-31 aunque el intervalo comience después de 2007")
    parser.add_argument("--border-only", action="store_true",
                        help="Crear solo el borde observado 2006-12-31; requiere el anual 2007")
    parser.add_argument("--dry-run", action="store_true",
                        help="Mostrar el plan sin descargar archivos")
    args = parser.parse_args()
    if (args.start_year < 1981 or args.end_year >= datetime.now(timezone.utc).year
            or args.start_year > args.end_year):
        parser.error("Seleccione años completos desde 1981 hasta el año anterior al actual")
    if not 1 <= args.workers <= 4:
        parser.error("--workers debe estar entre 1 y 4")

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    years = range(args.start_year, args.end_year + 1)
    need_first_border = args.start_year == 2007 or args.include_2006_border or args.border_only
    LOGGER.info("CHIRPS v3 Final/rnl: %d años, %d–%d; salida: %s",
                len(years), args.start_year, args.end_year, args.output_dir)
    if args.dry_run:
        if not args.border_only:
            for year in years:
                LOGGER.info("%d: %s -> %s", year, url_for(year),
                            args.output_dir / str(year) / filename_for(year))
        if need_first_border:
            LOGGER.info("Borde observado %s: %s -> %s", FIRST_BORDER, first_border_tiff_url(),
                        border_path(args.output_dir, 2006))
        if args.end_year == 2025 and not args.border_only:
            LOGGER.info("Borde imputado %s–%s: media 2007–2025 -> %s",
                        LAST_BORDER[0], LAST_BORDER[-1], border_path(args.output_dir, 2026))
        return
    with requests.Session() as session:
        session.headers.update({"User-Agent": "data-processing-thesis/1.0 (CHIRPS download)"})
        if args.border_only:
            LOGGER.info("Borde 2006: %s", download_first_border(session, args.output_dir))
            return
        if args.workers == 1:
            for position, year in enumerate(years, start=1):
                LOGGER.info("Año %d/%d", position, len(years))
                download_year(session, year, args.output_dir)
            if need_first_border:
                LOGGER.info("Borde 2006: %s", download_first_border(session, args.output_dir))
        else:
            reference = args.output_dir / "2007" / filename_for(2007)
            border_can_run_now = need_first_border and valid_existing(reference, 2007)
            with ThreadPoolExecutor(max_workers=args.workers) as executor:
                border_job = (executor.submit(download_first_border_worker, args.output_dir)
                              if border_can_run_now else None)
                jobs = {executor.submit(download_year_worker, year, args.output_dir): year
                        for year in years}
                pending = list(jobs) + ([border_job] if border_job else [])
                for job in as_completed(pending):
                    if job == border_job:
                        LOGGER.info("Borde 2006 completado: %s", job.result())
                    else:
                        LOGGER.info("Año %d completado: %s", jobs[job], job.result())
            if need_first_border and not border_can_run_now:
                LOGGER.info("Borde 2006: %s", download_first_border(session, args.output_dir))
    if args.end_year == 2025:
        LOGGER.info("Borde 2026 imputado: %s", impute_last_border(args.output_dir))


if __name__ == "__main__":
    main()
