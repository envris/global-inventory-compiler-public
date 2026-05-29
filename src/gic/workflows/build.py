"""Workflow for building and refining a global inventory"""

import argparse
import os

from ..fields import validate_field_name
from .utils.build_inventory import build_or_update_inventory
from .utils.common_args import fix_args
from .utils.logging import get_logger


def parse_args(args: list[str]) -> argparse.Namespace:
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description=(
            "Build, update or refine a global chemicals inventory from "
            "directory of JSONL files."
        )
    )
    parser.add_argument(
        "-j",
        "--jsonl_dir",
        type=str,
        required=True,
        help=(
            "Directory containing JSONL files. These will be found "
            "recursively in subdirectories. (required)"
        ),
    )
    parser.add_argument(
        "-i",
        "--inventory_file",
        type=str,
        required=True,
        help=("Path to the inventory file that will be created or updated. (required)"),
    )
    parser.add_argument(
        "-l",
        "--log",
        type=str,
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).",
    )
    parser.add_argument(
        "-g",
        "--gremlins_file",
        type=str,
        default="",
        help=("Path to load CSV file containing gremlins data. (optional)"),
    )
    parser.add_argument(
        "-o",
        "--order_fields",
        type=str,
        default="",
        help=(
            "Comma-separated list of identifier fields to order substances by. "
            "Otherwise, substances will be in the order they are created. (optional)"
        ),
    )
    return parser.parse_args(args)


def main(args: list[str] | None = None) -> None:
    """Main entry point for build or refine workflow"""
    parsed = parse_args(fix_args(args))
    logger = get_logger(parsed.log)

    # Validate order fields before wasting time building inventory
    order_fields = []
    if parsed.order_fields:
        order_fields = [field.strip() for field in parsed.order_fields.split(",")]
        for field in order_fields:
            validate_field_name(field)

    # Build or update inventory
    inventory = build_or_update_inventory(
        parsed.jsonl_dir, parsed.inventory_file, parsed.gremlins_file, logger
    )

    # Reorder and output inventory
    if order_fields:
        logger.info("Applying substances ordering by fields: %s", order_fields)
        inventory.order(order_fields)

    if os.path.isfile(parsed.inventory_file):
        logger.info("Overwriting existing inventory file %s", parsed.inventory_file)
    else:
        logger.info("Saving inventory to %s", parsed.inventory_file)
    logger.info(
        "Number of substances in final inventory: %s", len(inventory.get_sids())
    )
    inventory.to_jsonl(parsed.inventory_file)
    logger.info("Workflow complete.")


if __name__ == "__main__":
    main()
