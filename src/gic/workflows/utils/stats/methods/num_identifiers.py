"""Simple methods to compute counts of various identifiers in an inventory."""

import logging

from ..... import Inventory
from .....datastructs.utils.validation import IDENTIFIER_FIELDS
from ..structs import StatsData


def get_num_identifiers(
    inventory: Inventory, identifier_type: str, count: int, operator: str
) -> int:
    """Get count of substances with a specific number identifier of type."""
    operator_choices = ["eq", "lt", "gt"]
    if operator not in operator_choices:
        raise ValueError(f"Invalid operator. Choose from {operator_choices}.")
    num_substances = 0
    for sid in inventory.get_sids():
        identifiers = inventory.get_by_sids(identifier_type, [sid])
        if operator == "eq" and len(identifiers) == count:
            num_substances += 1
        elif operator == "lt" and len(identifiers) < count:
            num_substances += 1
        elif operator == "gt" and len(identifiers) > count:
            num_substances += 1
    return num_substances


def get_num_only_identifier(inventory: Inventory, identifier_type: str) -> int:
    """Get count of substances with only a specific type of identifier."""
    other_idfs = [idf for idf in IDENTIFIER_FIELDS if idf != identifier_type]
    count = 0
    for sid in inventory.get_sids():
        identifiers = inventory.get_by_sids(identifier_type, [sid])
        if len(identifiers) == 0:
            continue
        only = True
        for idf in other_idfs:
            other_identifiers = inventory.get_by_sids(idf, [sid])
            if len(other_identifiers) > 0:
                only = False
                break
        if only:
            count += 1
    return count


def num_substances_stats(
    inventory_data: Inventory, logger: logging.Logger
) -> list[StatsData]:
    """Get a count of unique substances from the inventory."""
    count = len(inventory_data.get_sids())
    stat = StatsData(name="Total Substances", value=count, percent=100.0)
    logger.info(
        "%s: %s (%.1f%%)",
        stat.name,
        stat.value,
        stat.percent,
    )
    return [stat]


def identifier_stats(inventory: Inventory, logger: logging.Logger) -> list[StatsData]:
    """Get a count of unique identifiers for each identifier field in the inventory."""
    stats: list[StatsData] = []
    for identifier_field in IDENTIFIER_FIELDS:
        total = len(inventory.get_identifiers(identifier_field))
        if not total:
            continue
        stat = StatsData(name=f"Unique {identifier_field}s", value=total, percent=100.0)
        logger.info(
            "%s: %s (%.1f%%)",
            stat.name,
            stat.value,
            stat.percent,
        )
        stats.append(stat)
    return stats


def identifiers_per_substance_stats(
    inventory: Inventory, logger: logging.Logger
) -> list[StatsData]:
    """Get a count of substances with 0, 1, or >1 identifiers for each
    identifier field."""
    stats: list[StatsData] = []
    num_substances = len(inventory.get_sids())
    for identifier_field in IDENTIFIER_FIELDS:
        num_identifiers = inventory.get_identifiers(identifier_field)
        if not num_identifiers:
            continue
        for count, operator, label, is_plural in [
            (0, "eq", "without", False),
            (1, "eq", "with one", False),
            (1, "gt", "with multiple", True),
        ]:
            num = get_num_identifiers(inventory, identifier_field, count, operator)
            percent = (num / num_substances) * 100 if num_substances else 0.0
            if num == 0:
                continue
            plural = identifier_field + "s" if is_plural else identifier_field
            stat = StatsData(
                name=f"Substances {label} {plural}", value=num, percent=percent
            )
            logger.info(
                "%s: %s (%.1f%%)",
                stat.name,
                stat.value,
                stat.percent,
            )
            stats.append(stat)
    return stats


def only_identifier_stats(
    inventory: Inventory, logger: logging.Logger
) -> list[StatsData]:
    """Get a count of substances with only one type of identifier."""
    stats: list[StatsData] = []
    num_substances = len(inventory.get_sids())
    for identifier_field in IDENTIFIER_FIELDS:
        num_identifiers = inventory.get_identifiers(identifier_field)
        if not num_identifiers:
            continue
        num = get_num_only_identifier(inventory, identifier_field)
        percent = (num / num_substances) * 100 if num_substances else 0.0
        stat = StatsData(
            name=f"Substances with only {identifier_field}s", value=num, percent=percent
        )
        logger.info(
            "%s: %s (%.1f%%)",
            stat.name,
            stat.value,
            stat.percent,
        )
        stats.append(stat)
    return stats
