"""Test workflow for calculating statistics on the inventory."""

import os

import pytest

from gic.datastructs import AssociatedValues, DataFrame, Inventory
from gic.workflows.stats import main as stats_main
from gic.workflows.utils.logging import get_logger
from gic.workflows.utils.stats.methods.num_by_list_count import list_count_stats
from gic.workflows.utils.stats.methods.num_identifiers import (
    identifier_stats,
    identifiers_per_substance_stats,
    num_substances_stats,
    only_identifier_stats,
)
from gic.workflows.utils.stats.structs import StatsData

DATA_DICTS = [
    {
        "chemical_name": ["Formaldehyde", "Methanal"],
        "ec_number": ["200-001-8"],
        "list_tag": ["List 1"],
    },
    {
        "chemical_name": ["Guanidine hydrochloride"],
        "ec_number": ["200-002-3", "200-011-2"],  # Second EC number from Metharbital
        "list_tag": ["List 1", "List 2"],
    },
    {
        "chemical_name": ["Dexamethasone"],
        "ec_number": ["200-003-9"],
        "list_tag": ["List 1", "List 2", "List 3"],
    },
    {
        "chemical_name": ["Hydrocortisone acetate"],
        "ec_number": ["200-004-4"],
        "list_tag": ["List 1", "List 2", "List 3", "List 4"],
    },
    {
        "chemical_name": ["Cortisone, 21-acetate"],
        "ec_number": ["200-006-5"],
        "list_tag": ["List 1", "List 2", "List 3", "List 4", "List 5"],
    },
    {
        "ec_number": ["200-007-0"],
        "list_tag": ["List 1", "List 2", "List 3", "List 4", "List 5", "List 6"],
    },
    {
        "chemical_name": ["Mitomycin C"],
        "list_tag": ["List 1", "List 2", "List 3", "List 4", "List 5", "List 6"],
    },
]


@pytest.fixture(name="inventory")
def fixture_inventory() -> Inventory:
    """Basic inventory for testing."""
    df = DataFrame()
    for row_dict in DATA_DICTS:
        ad = AssociatedValues(row_dict)
        ad.clean()
        df.append(ad)
    inv = Inventory()
    inv.import_from_data_frame(df)
    return inv


def test_stats_workflow():
    """Test the stats workflow main function."""
    stats_test_path = os.path.join(
        "tests", "data", "workflows__out", "stats__file__test.jsonl"
    )
    stats_golden_path = os.path.join(
        "tests", "data", "workflows__out", "stats__file__golden.jsonl"
    )
    stats_main(
        [
            "-i",
            os.path.join(
                "tests", "data", "workflows__in", "stats__inventory_unrefined.jsonl"
            ),
            "-s",
            stats_test_path,
            "-l",
            "WARNING",
        ]
    )

    # Compare stats test and expected (golden) output files
    with (
        open(stats_test_path, encoding="utf-8") as f_test,
        open(stats_golden_path, encoding="utf-8") as f_golden,
    ):
        test_lines = f_test.readlines()
        golden_lines = f_golden.readlines()
        assert test_lines == golden_lines, "Stats output files do not match."

    # Clean up: delete the test output files
    os.remove(stats_test_path)


def _match_expected(expected: dict[str, int], stats_datas: list[StatsData]):
    for stats_data in stats_datas:
        assert stats_data.value == expected[stats_data.name], (
            f"Expected {expected[stats_data.name]} for {stats_data.name}, "
            f"got {stats_data.value}"
        )
    assert len(expected) == len(stats_datas), (
        "Mismatched number of calculated and expected stats"
    )


def test_list_count_stats(inventory: Inventory):
    logger = get_logger("INFO")
    expected = {
        "Substances in no lists": 1,
        "Substances in exactly one list": 1,
        "Substances in exactly two lists": 1,
        "Substances in exactly three lists": 1,
        "Substances in exactly four lists": 1,
        "Substances in five or more lists": 2,
    }
    stats_datas = list_count_stats(inventory, logger, exclude_lists={"List 1"})
    _match_expected(expected, stats_datas)

    # Confirm that excluding a non-existent list raises a ValueError
    with pytest.raises(ValueError):
        list_count_stats(inventory, logger, exclude_lists={"NonExistentList"})


def test_num_substances_stats(inventory: Inventory):
    logger = get_logger("INFO")
    expected = {"Total Substances": 7}
    stats_datas = num_substances_stats(inventory, logger)
    _match_expected(expected, stats_datas)


def test_identifier_stats(inventory: Inventory):
    logger = get_logger("INFO")
    expected = {
        "Unique chemical_names": 7,
        "Unique ec_numbers": 7,
    }
    stats_datas = identifier_stats(inventory, logger)
    _match_expected(expected, stats_datas)


def test_identifiers_per_substance_stats(inventory: Inventory):
    logger = get_logger("INFO")
    expected = {
        "Substances without chemical_name": 1,
        "Substances with one chemical_name": 5,
        "Substances with multiple chemical_names": 1,
        "Substances without ec_number": 1,
        "Substances with one ec_number": 5,
        "Substances with multiple ec_numbers": 1,
    }
    stats_datas = identifiers_per_substance_stats(inventory, logger)
    _match_expected(expected, stats_datas)


def test_only_identifier_stats(inventory: Inventory):
    logger = get_logger("INFO")
    expected = {
        "Substances with only chemical_names": 1,
        "Substances with only ec_numbers": 1,
    }
    stats_datas = only_identifier_stats(inventory, logger)
    _match_expected(expected, stats_datas)
