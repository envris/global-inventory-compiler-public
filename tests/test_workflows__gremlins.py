"""Test Gremlins detection workflow."""

import os

from gic.workflows.gremlins import main as gremlins_main


def test_gremlins_workflow():
    """Test the Gremlins detection workflow main function."""
    test_path = os.path.join(
        "tests", "data", "workflows__out", "gremlins__file__test.csv"
    )
    golden_path = os.path.join(
        "tests", "data", "workflows__out", "gremlins__file__golden.csv"
    )
    gremlins_main(
        [
            "-j",
            os.path.join("tests", "data", "workflows__in", "jsonl"),
            "-g",
            test_path,
            "-l",
            "WARNING",
            "--gremlins_cutoff",
            "5",
        ]
    )

    # Compare golden and test output files
    with (
        open(test_path, encoding="utf-8") as f_test,
        open(golden_path, encoding="utf-8") as f_golden,
    ):
        test_lines = f_test.readlines()
        golden_lines = f_golden.readlines()
        assert test_lines == golden_lines, "Gremlins output files do not match."

    # Clean up: delete the test output file
    os.remove(test_path)
