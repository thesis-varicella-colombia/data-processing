"""Comprobaciones pequeñas de calendario, recorte y agregación climática."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import numpy as np
import pandas as pd
import xarray as xr


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts/processing"))
sys.path.insert(0, str(ROOT / "scripts/download"))

import climate_common  # noqa: E402
import calculate_weekly_humidity  # noqa: E402
import calculate_weekly_precipitation  # noqa: E402
import download_era5_land  # noqa: E402
from epidemiological_weeks import week_one_start, weeks_in_range  # noqa: E402


class ClimatePipelineTests(unittest.TestCase):
    def test_epidemiological_year_crosses_calendar_year(self):
        weeks = weeks_in_range(2007, 2007)
        self.assertEqual(week_one_start(2007).isoformat(), "2006-12-31")
        self.assertEqual(weeks[0], (2007, 1, week_one_start(2007)))
        self.assertEqual(weeks[-1][2].isoformat(), "2007-12-23")

    def test_remote_selection_handles_descending_latitude_and_360_longitude(self):
        ds = xr.Dataset(
            {name: (("valid_time", "latitude", "longitude"), np.ones((1, 4, 5)))
             for name in download_era5_land.VARIABLES},
            coords={"valid_time": pd.date_range("2024-03-01", periods=1),
                    "latitude": [2., 1., 0., -1.],
                    "longitude": [278., 279., 280., 281., 282.]},
        )
        selected = download_era5_land.select_region(ds, (-81.1, -0.1, -79.9, 1.1))
        self.assertEqual(selected.sizes["latitude"], 2)
        self.assertEqual(selected.sizes["longitude"], 2)
        self.assertEqual(float(selected.longitude.values[0]), 279.)

    def test_humidity_uses_surface_pressure(self):
        t = np.array([[[293.15]], [[293.15]]])
        td = np.full_like(t, 283.15)
        pressure = np.array([[[100000.]], [[70000.]]])
        result = calculate_weekly_humidity.calculate({"t2m": t, "d2m": td, "sp": pressure})
        q = result["humedad_especifica_media_g_kg"][:, 0, 0]
        self.assertGreater(q[1], q[0])
        self.assertTrue(np.all((result["humedad_relativa_media_pct"] >= 0) &
                               (result["humedad_relativa_media_pct"] <= 100)))

    def test_precipitation_sums_seven_daily_area_means_and_rejects_missing_day(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            raw = root / "raw"
            raw.mkdir()
            for year, month in ((2006, 12), (2007, None)):
                dates = (pd.date_range("2006-12-01", "2006-12-31") if month else
                         pd.date_range("2007-01-01", "2007-12-31"))
                values = np.zeros((len(dates), 2, 2), dtype=np.float32)
                values[:, 0, 0] = 0.001
                values[:, 0, 1] = 0.003
                ds = xr.Dataset({"tp": (("valid_time", "latitude", "longitude"), values,
                                        {"units": "m"})},
                                coords={"valid_time": dates, "latitude": [1., 0.],
                                        "longitude": [-1., 0.]})
                suffix = f"_{month:02d}" if month else ""
                ds.to_netcdf(raw / f"era5_land_daily_{year}{suffix}.nc", engine="netcdf4")
            args = SimpleNamespace(start_year=2007, end_year=2007, municipality=None,
                                   validate_only=False, overwrite=False)
            weights = (np.array([0, 0]), np.array([0, 1]), np.array([0, 0]),
                       np.array([1., 3.]), np.array([4.]))
            with (patch.object(climate_common, "RAW", raw),
                  patch.object(climate_common, "PROCESSED", root / "processed"),
                  patch.object(climate_common, "read_codes", return_value={"00001": "Prueba"}),
                  patch.object(climate_common, "inspect_geometries",
                               return_value=(["00001"], (-1.1, -0.1, 0.1, 1.1))),
                  patch.object(climate_common, "build_weights", return_value=weights)):
                path = climate_common.run_pipeline(
                    args, "precipitation", ("tp",), ("precipitacion_total_mm",),
                    calculate_weekly_precipitation.calculate, precipitation=True)[0]
                frame = pd.read_parquet(path)
                self.assertAlmostEqual(frame.iloc[0]["precipitacion_total_mm"], 17.5, places=5)
                self.assertAlmostEqual(frame.iloc[0]["fraccion_area_con_datos"], 1.)

                with xr.open_dataset(raw / "era5_land_daily_2007.nc") as ds:
                    changed = ds.load()
                changed["tp"].loc[{"valid_time": "2007-01-02"}] = np.nan
                changed.to_netcdf(raw / "era5_land_daily_2007.nc", engine="netcdf4")
                args.overwrite = True
                climate_common.run_pipeline(
                    args, "precipitation", ("tp",), ("precipitacion_total_mm",),
                    calculate_weekly_precipitation.calculate, precipitation=True)
                frame = pd.read_parquet(path)
                self.assertTrue(np.isnan(frame.iloc[0]["precipitacion_total_mm"]))
                self.assertAlmostEqual(frame.iloc[0]["fraccion_area_con_datos"], 6 / 7)


if __name__ == "__main__":
    unittest.main()
