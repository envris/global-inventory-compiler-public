"""Base structures for inventory statistics calculations."""

from dataclasses import dataclass


@dataclass
class StatsData:
    """Simple structure for storing statistic data with enforced types."""

    name: str
    value: int
    percent: float
