"""An ordered registry of all available statistic methods."""

import logging
from collections.abc import Callable
from functools import partial

from ..... import Inventory
from ..structs import StatsData
from . import num_by_list_count, num_identifiers


def get_all_methods(
    exclude_lists: set[str] | None = None,
) -> list[Callable[[Inventory, logging.Logger], list[StatsData]]]:
    """Get a list of all available statistic methods. All methods must
    accept an Inventory object and a Logger object, and return a list of
    StatsData objects.
    """
    return [
        num_identifiers.num_substances_stats,
        num_identifiers.identifier_stats,
        num_identifiers.identifiers_per_substance_stats,
        num_identifiers.only_identifier_stats,
        partial(
            num_by_list_count.list_count_stats,
            exclude_lists=exclude_lists if exclude_lists is not None else set(),
        ),
    ]
