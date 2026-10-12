"""Pruebas de los días de borde CHIRPS con archivos NetCDF pequeños."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np
import pandas as pd
import xarray as xr


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts/download"))
import download_chirps_precipitation as chirps  # noqa: E402


def annual_file(root: Path, year: int, value: float) -> None:
    dates = pd.date_range(f"{year}-01-01", f"{year}-12-31")
    values = np.full((len(dates), 1, 2), value, dtype=np.float32)
    values[:3, 0, 0] += np.arange(3)
    values[:3, 0, 1] = np.nan
    dataset = xr.Dataset(
        {"precip": (("time", "latitude", "longitude"), values, {"units": "mm/day"})},
        coords={"time": dates, "latitude": [0.0], "longitude": [0.0, 0.05]},
    )
    destination = root / str(year) / chirps.filename_for(year)
    destination.parent.mkdir(parents=True, exist_ok=True)
    dataset.to_netcdf(destination, engine="netcdf4")


class ChirpsBorderTests(unittest.TestCase):
    def test_observed_border_requires_2007_grid_for_tiff_validation(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with self.assertRaisesRegex(FileNotFoundError, "Se requiere 2007"):
                chirps.download_first_border(None, root)

    def test_imputes_each_day_by_cell_and_preserves_missing_cells(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for year in chirps.REFERENCE_YEARS:
                annual_file(root, year, float(year - 2006))
            destination = chirps.impute_last_border(root)
            chirps.validate_netcdf(destination, 2026, chirps.LAST_BORDER)
            with xr.open_dataset(destination) as dataset:
                np.testing.assert_allclose(dataset.precip[:, 0, 0], [10.0, 11.0, 12.0])
                self.assertTrue(np.isnan(dataset.precip[:, 0, 1]).all())
                self.assertEqual(dataset.attrs["border_data_status"], "imputed_not_observed")
                self.assertEqual(dataset.attrs["reference_years"], "2007-2025")


if __name__ == "__main__":
    unittest.main()
