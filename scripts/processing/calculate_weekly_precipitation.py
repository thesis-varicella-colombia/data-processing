"""Suma de precipitación diaria UTC por municipio y semana epidemiológica."""

from __future__ import annotations

import argparse

import numpy as np

from climate_common import add_common_arguments, check_years, run_pipeline


def calculate(inputs: dict[str, np.ndarray]) -> dict[str, np.ndarray]:
    precipitation = inputs["tp"]
    # Pequeños negativos por redondeo se consideran cero; valores mayores son inválidos.
    valid = np.isfinite(precipitation) & (precipitation >= -1e-8)
    return {"precipitacion_total_mm": np.where(valid, np.maximum(precipitation, 0) * 1000, np.nan)}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    add_common_arguments(parser)
    args = parser.parse_args()
    check_years(parser, args)
    run_pipeline(args, "precipitation", ("tp",), ("precipitacion_total_mm",),
                 calculate, precipitation=True)


if __name__ == "__main__":
    main()
