"""Utilities to find gremlins in JSONL files and inventory data."""

import logging

from ...datastructs import DataFrame
from ..utils.finders import find_jsonl_files
from .gremlins_data import GremlinsData


def find_gremlins_in_dataframe(df: DataFrame, cutoff: int) -> GremlinsData:
    """Find chemical names that appear more than specified number of times
    and flag is potential gremlin. Return gremlins as GremlinsData object.

    :param df: Dataframe to scan for gremlins.
    :param cutoff: Number of times a chemical name has to occur for it to be
        flagged as a potential gremlin.
    """
    g_data = GremlinsData()
    for row in df:
        list_tags = row.get_values("list_tag")
        chemical_names = row.get_values("chemical_name")
        g_data.tally(chemical_names, list_tags)
    g_data.flush(cutoff)
    return g_data


def find_gremlins(jsonl_dir: str, cutoff: int, logger: logging.Logger) -> GremlinsData:
    """Scan all JSONL files in directory for gremlins. Returns a combined
    GremlinsData object.

    :param jsonl_dir: Parent directory containing JSONL files.
    :param cutoff: Number of times a chemical name has to occur for it to be
        flagged as a potential gremlin.
    :param logger: Logger instance to print status messages.
    """
    jsonl_files = find_jsonl_files(jsonl_dir)
    logger.info(
        "Finding potential gremlin chemical names %d JSONL files", len(jsonl_files)
    )
    g_data = GremlinsData()
    for filename in jsonl_files:
        logger.info("Scanning %s", filename)
        df = DataFrame.from_jsonl(filename)
        g_data += find_gremlins_in_dataframe(df, cutoff)
    return g_data
