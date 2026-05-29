"""Test build workflow."""

import os

from gic.datastructs import Inventory
from gic.workflows.build import main as build_main

from .utils.workflows import compare_inventories


def test_build_workflow():
    """Test the build workflow main function."""
    test_path = os.path.join(
        "tests", "data", "workflows__out", "build__inventory__test.jsonl"
    )
    golden_path = os.path.join(
        "tests", "data", "workflows__out", "build__inventory__golden.jsonl"
    )
    build_main(
        [
            "-j",
            os.path.join("tests", "data", "workflows__in", "jsonl"),
            "-i",
            test_path,
            "-o",
            "ec_number,chemical_name",
            "-l",
            "WARNING",
        ]
    )

    # Compare test and expected (golden) inventories
    test_inventory = Inventory(test_path)
    golden_inventory = Inventory(golden_path)
    assert compare_inventories(test_inventory, golden_inventory), (
        "Inventories do not match."
    )

    # Clean up: delete the test output file
    os.remove(test_path)


def test_build_refine_workflow():
    """Test the build workflow main function, with refinement flags."""
    test_path = os.path.join(
        "tests", "data", "workflows__out", "build__inventory_refined__test.jsonl"
    )
    golden_path = os.path.join(
        "tests", "data", "workflows__out", "build__inventory_refined__golden.jsonl"
    )
    build_main(
        [
            "-j",
            os.path.join("tests", "data", "workflows__in", "jsonl"),
            "-i",
            test_path,
            "-l",
            "WARNING",
            "-g",
            os.path.join("tests", "data", "workflows__in", "build__gremlins_file.csv"),
            "-o",
            "ec_number,chemical_name",
        ]
    )

    # Compare test and expected (golden) inventories
    test_inventory = Inventory(test_path)
    golden_inventory = Inventory(golden_path)
    assert compare_inventories(test_inventory, golden_inventory), (
        "Inventories do not match."
    )

    # Clean up: delete the test output file
    os.remove(test_path)
