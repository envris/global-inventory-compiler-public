"""Calculate the number of substances with a specific number of lists."""

import logging

from .....datastructs import Inventory
from ..structs import StatsData


def _num_with_list_count(
    inventory: Inventory, num_lists: int, operator: str, exclude_lists: set[str]
) -> int:
    """Get count of substances with a specific number of lists."""
    operator_choices = ["eq", "lt", "gt"]
    if operator not in operator_choices:
        raise ValueError(f"Invalid operator. Choose from {operator_choices}.")
    count = 0
    for sid in inventory.get_sids():
        list_tags = [
            list_tag
            for list_tag in inventory.get_by_sids("list_tag", [sid])
            if list_tag not in exclude_lists
        ]
        num_list = len(list_tags)
        if operator == "eq" and num_list == num_lists:
            count += 1
        elif operator == "lt" and num_list < num_lists:
            count += 1
        elif operator == "gt" and num_list > num_lists:
            count += 1
    return count


def list_count_stats(
    inventory: Inventory, logger: logging.Logger, exclude_lists: set[str]
) -> list[StatsData]:
    """Batch function to find how many substances are shared by specified
    number of lists."""
    stats: list[StatsData] = []
    valid_list_tags = set(inventory.get_list_data().values())
    invalid_list_tags = exclude_lists - valid_list_tags
    if invalid_list_tags:
        raise ValueError(
            f"Invalid list tags in exclude_lists: {sorted(invalid_list_tags)}. "
            f"Valid list tags: {sorted(valid_list_tags)}"
        )
    runs = [
        ("Substances in no lists", 0, "eq"),
        ("Substances in exactly one list", 1, "eq"),
        ("Substances in exactly two lists", 2, "eq"),
        ("Substances in exactly three lists", 3, "eq"),
        ("Substances in exactly four lists", 4, "eq"),
        ("Substances in five or more lists", 4, "gt"),
    ]
    num_substances = len(inventory.get_sids())
    for run in runs:
        count = _num_with_list_count(inventory, run[1], run[2], exclude_lists)
        stat = StatsData(
            name=run[0],
            value=count,
            percent=count / num_substances * 100 if num_substances else 0.0,
        )
        logger.info(
            "%s: %s (%.1f%%)",
            stat.name,
            stat.value,
            stat.percent,
        )
        stats.append(stat)
    return stats
