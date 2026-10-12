"""Verifica reanudación HTTP Range sin perder el archivo parcial."""

import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np
import pandas as pd
import xarray as xr
from PIL import Image, TiffImagePlugin

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts/download"))
from download_chirps_precipitation import (download_first_border, filename_for,
                                          first_border_tiff_path, stream_to_part)  # noqa: E402


class Response:
    def __init__(self, status: int, headers: dict, body: bytes = b""):
        self.status_code = status
        self.headers = headers
        self.body = body

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False

    def raise_for_status(self):
        if self.status_code >= 400:
            raise ValueError(f"HTTP {self.status_code}")

    def iter_content(self, chunk_size):
        for start in range(0, len(self.body), 3):
            yield self.body[start:start + 3]


class Session:
    def __init__(self, source: bytes):
        self.source = source
        self.requested_range = None

    def head(self, url, **_):
        return Response(200, {"Content-Length": str(len(self.source))})

    def get(self, url, headers, **_):
        self.requested_range = headers.get("Range")
        if self.requested_range:
            start = int(self.requested_range.removeprefix("bytes=").removesuffix("-"))
            return Response(206, {"Content-Range":
                                   f"bytes {start}-{len(self.source) - 1}/{len(self.source)}"},
                            self.source[start:])
        return Response(200, {"Content-Length": str(len(self.source))}, self.source)


class ChirpsResumeTests(unittest.TestCase):
    def test_daily_tiff_creates_observed_2006_border(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            annual = root / "2007" / filename_for(2007)
            annual.parent.mkdir()
            dates = pd.date_range("2007-01-01", "2007-12-31")
            xr.Dataset(
                {"precip": (("time", "latitude", "longitude"),
                            np.ones((365, 2, 2), dtype=np.float32), {"units": "mm/day"})},
                coords={"time": dates, "latitude": [59.925, 59.975],
                        "longitude": [-179.975, -179.925]},
            ).to_netcdf(annual, engine="netcdf4")
            tiff = first_border_tiff_path(root)
            tiff.parent.mkdir()
            tags = TiffImagePlugin.ImageFileDirectory_v2()
            tags[33550] = (0.05, 0.05, 0.0)
            tags[33922] = (0.0, 0.0, 0.0, -180.0, 60.0, 0.0)
            Image.fromarray(np.array([[1, -9999], [3, 4]], dtype=np.float32)).save(
                tiff, tiffinfo=tags)
            result = download_first_border(None, root)
            with xr.open_dataset(result) as border:
                self.assertEqual(str(border.time.values[0])[:10], "2006-12-31")
                self.assertEqual(border.precip.attrs["units"], "mm/day")
                self.assertEqual(border.attrs["source_format"], "GeoTIFF")
                self.assertTrue(np.allclose(border.precip.values[0, 0], [3, 4]))
                self.assertTrue(np.isnan(border.precip.values[0, 1, 1]))

    def test_resume_preserves_prefix_and_appends_remainder(self):
        source = b"abcdefghijklmno"
        with tempfile.TemporaryDirectory() as directory:
            part = Path(directory) / "year.nc.part"
            part.write_bytes(source[:8])
            session = Session(source)
            stream_to_part(session, "https://example.org/year.nc", part)
            self.assertEqual(session.requested_range, "bytes=0-")
            self.assertEqual(part.read_bytes(), source)

    def test_changed_source_never_appends_to_partial_file(self):
        with tempfile.TemporaryDirectory() as directory:
            part = Path(directory) / "year.nc.part"
            part.write_bytes(b"old-data")
            with self.assertRaisesRegex(ValueError, "fuente cambió"):
                stream_to_part(Session(b"new-data-more"), "https://example.org/year.nc", part)
            self.assertEqual(part.read_bytes(), b"old-data")

    def test_fresh_transfer_and_completed_part(self):
        source = b"precipitation"
        with tempfile.TemporaryDirectory() as directory:
            part = Path(directory) / "year.nc.part"
            session = Session(source)
            stream_to_part(session, "https://example.org/year.nc", part)
            self.assertIsNone(session.requested_range)
            self.assertEqual(part.read_bytes(), source)
            stream_to_part(session, "https://example.org/year.nc", part)
            self.assertEqual(part.read_bytes(), source)
