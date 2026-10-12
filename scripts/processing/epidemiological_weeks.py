"""Semanas epidemiológicas: domingo a sábado; semana 1 contiene el 4 de enero."""

from __future__ import annotations

from datetime import date, timedelta


def week_one_start(year: int) -> date:
    january_fourth = date(year, 1, 4)
    return january_fourth - timedelta(days=(january_fourth.weekday() + 1) % 7)


def weeks_in_range(start_year: int, end_year: int) -> list[tuple[int, int, date]]:
    weeks = []
    for year in range(start_year, end_year + 1):
        start = week_one_start(year)
        next_start = week_one_start(year + 1)
        number = 1
        while start < next_start:
            weeks.append((year, number, start))
            start += timedelta(days=7)
            number += 1
    return weeks


def day_to_week(weeks: list[tuple[int, int, date]]) -> dict[date, int]:
    return {start + timedelta(days=offset): index
            for index, (_, _, start) in enumerate(weeks) for offset in range(7)}


def calendar_years_needed(start_year: int, end_year: int) -> range:
    weeks = weeks_in_range(start_year, end_year)
    return range(weeks[0][2].year, (weeks[-1][2] + timedelta(days=6)).year + 1)
