"""Test workflow for calculating statistics on the inventory."""

import os

from gic.workflows.stats import main as stats_main


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
