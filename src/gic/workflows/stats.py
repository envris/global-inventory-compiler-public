"""Workflow for calculating inventory statistics"""

import argparse
import csv

from .. import Inventory
from .utils.common_args import fix_args
from .utils.logging import get_logger
from .utils.stats.methods import get_all_methods
from .utils.stats.structs import StatsData


def parse_args(args: list[str]) -> argparse.Namespace:
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description=("Calculate inventory statistics."))
    parser.add_argument(
        "-i",
        "--inventory_file",
        type=str,
        required=True,
        help="Inventory file to calculate statistics from.",
    )
    parser.add_argument(
        "-s",
        "--stats_file",
        type=str,
        required=True,
        help="Path to write the statistics file (required).",
    )
    parser.add_argument(
        "-l",
        "--log",
        type=str,
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).",
    )
    return parser.parse_args(args)


def main(args: list[str] | None = None) -> None:
    """Main entry point for the statistic workflow."""
    parsed = parse_args(fix_args(args))
    logger = get_logger(parsed.log)

    logger.info("Calculating inventory statistics for %s", parsed.inventory_file)
    inventory = Inventory(parsed.inventory_file)

    # Calculate statistics
    all_stats: list[StatsData] = []
    analytics = get_all_methods()
    for method in analytics:
        stats_datas = method(inventory, logger)
        all_stats.extend(stats_datas)

    # Write statistics
    logger.info("Writing statistics to %s", parsed.stats_file)
    with open(parsed.stats_file, "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = ["Statistic", "Value", "Percent"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for stat in all_stats:
            writer.writerow(
                {
                    "Statistic": stat.name,
                    "Value": stat.value,
                    "Percent": round(stat.percent, 1),
                }
            )


if __name__ == "__main__":
    main()
