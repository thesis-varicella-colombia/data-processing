"""Humedades diarias por celda y medias semanales municipales en días UTC."""

from __future__ import annotations

import argparse

import numpy as np

from climate_common import add_common_arguments, check_years, run_pipeline


RV = 461.5  # J kg^-1 K^-1, constante específica del vapor de agua
EPSILON = 0.622  # razón de masas moleculares vapor/aire seco


def saturation_vapour_pressure(temperature_k: np.ndarray) -> np.ndarray:
    """Magnus sobre agua: presión de vapor de saturación en Pa."""
    temperature_c = temperature_k - 273.15
    return 611.2 * np.exp(17.67 * temperature_c / (temperature_c + 243.5))


def calculate(inputs: dict[str, np.ndarray]) -> dict[str, np.ndarray]:
    temperature = inputs["t2m"]
    dewpoint = inputs["d2m"]
    pressure = inputs["sp"]
    physically_valid = (np.isfinite(temperature) & np.isfinite(dewpoint) &
                        np.isfinite(pressure) & (temperature >= 180) &
                        (temperature <= 330) & (dewpoint >= 180) &
                        (dewpoint <= temperature + 0.5) &
                        (pressure > 0) & (pressure <= 120000))
    with np.errstate(divide="ignore", invalid="ignore", over="ignore"):
        vapour = saturation_vapour_pressure(dewpoint)
        saturation = saturation_vapour_pressure(temperature)
        relative = 100 * vapour / saturation
        specific = 1000 * EPSILON * vapour / (pressure - (1 - EPSILON) * vapour)
        absolute = 1000 * vapour / (RV * temperature)
    physically_valid &= (pressure > vapour) & (relative >= 0) & (relative <= 100.5)
    physically_valid &= (specific >= 0) & (absolute >= 0)
    return {
        "humedad_relativa_media_pct": np.where(physically_valid, np.minimum(relative, 100), np.nan),
        "humedad_especifica_media_g_kg": np.where(physically_valid, specific, np.nan),
        "humedad_absoluta_media_g_m3": np.where(physically_valid, absolute, np.nan),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    add_common_arguments(parser)
    args = parser.parse_args()
    check_years(parser, args)
    run_pipeline(args, "humidity", ("t2m", "d2m", "sp"),
                 ("humedad_relativa_media_pct", "humedad_especifica_media_g_kg",
                  "humedad_absoluta_media_g_m3"), calculate)


if __name__ == "__main__":
    main()
