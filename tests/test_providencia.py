"""Comprueba la semántica horaria de ERA5 y la suma diaria UTC."""

import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np
import pandas as pd
import xarray as xr

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts/processing"))
from estimate_providencia import daily_from_hourly, hourly_times  # noqa: E402
import download_era5_providencia as downloader  # noqa: E402
import estimate_providencia as processing  # noqa: E402


class ProvidenciaHourlyTests(unittest.TestCase):
  def test_download_only_writes_hourly_and_processing_derives_daily(self):
    hours = hourly_times(2024, 2)
    grid = (np.array([13.5, 13.25]), np.array([278.5, 278.75]))
    shape = (len(hours), 2, 2)
    variables = {name: (("valid_time", "latitude", "longitude"),
                        np.full(shape, value), {"units": unit})
                 for name, value, unit in [("t2m", 300., "K"), ("d2m", 295., "K"),
                                           ("sp", 101000., "Pa"), ("tp", .001, "m")]}
    source = xr.Dataset(variables, coords={"valid_time": hours,
                                           "latitude": grid[0], "longitude": grid[1]})
    with tempfile.TemporaryDirectory() as directory:
      root = Path(directory)
      with patch.object(downloader, "RAW", root / "raw"), patch.object(processing, "DAILY", root / "daily"):
        hourly = downloader.download_month(source, 2024, 2, False, grid)
        self.assertTrue(hourly.is_file())
        self.assertEqual(len(list((root / "raw").glob("*.nc"))), 1)
        processing.derive_month(2024, 2, False)
        daily = processing.daily_path(2024, 2)
        self.assertTrue(daily.is_file())
        with xr.open_dataset(daily) as data:
          self.assertEqual(data.sizes["valid_time"], 29)
          self.assertTrue(np.allclose(data.tp.values, .024))

  def test_tp_hour_00_closes_previous_utc_day(self):
    hours = hourly_times(2024, 2)
    n = len(hours)
    shape = (n, 2, 2)
    data = {name: (("valid_time", "latitude", "longitude"),
                   np.full(shape, value, dtype=float), {"units": unit})
            for name, value, unit in [("t2m", 300, "K"), ("d2m", 295, "K"),
                                      ("sp", 101000, "Pa"), ("tp", 0, "m")]}
    hourly = xr.Dataset(data, coords={"valid_time": hours,
                                      "latitude": [13.5, 13.25],
                                      "longitude": [278.5, 278.75]})
    # Una hora de lluvia en 2024-03-01 00:00 pertenece a febrero 29.
    hourly["tp"].values[-1, :, :] = 0.01
    daily = daily_from_hourly(hourly, 2024, 2)
    self.assertEqual(len(daily.valid_time), 29)
    self.assertEqual(pd.Timestamp(daily.valid_time.values[-1]), pd.Timestamp("2024-02-29"))
    self.assertTrue(np.allclose(daily.tp.values[:-1], 0))
    self.assertTrue(np.allclose(daily.tp.values[-1], 0.01))
    self.assertTrue(np.allclose(daily.t2m.values, 300))
    hourly["tp"].values[-1, 0, 0] = np.nan
    incomplete = daily_from_hourly(hourly, 2024, 2)
    self.assertTrue(np.isnan(incomplete.tp.values[-1, 0, 0]))
    self.assertTrue(np.isfinite(incomplete.tp.values[-1, 1, 1]))
