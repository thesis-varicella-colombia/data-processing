"""Temperatura media municipio × semana desde ERA5-Land Daily UTC."""

from __future__ import annotations

import argparse

import numpy as np

from climate_common import add_common_arguments, check_years, run_pipeline


def calculate(inputs: dict[str, np.ndarray]) -> dict[str, np.ndarray]:
    temperature = inputs["t2m"]
    return {"temperatura_media_c": np.where(
        np.isfinite(temperature) & (temperature >= 180) & (temperature <= 330),
        temperature - 273.15, np.nan)}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    add_common_arguments(parser)
    args = parser.parse_args()
    check_years(parser, args)
    run_pipeline(args, "temperature", ("t2m",), ("temperatura_media_c",), calculate)


if __name__ == "__main__":
    main()
