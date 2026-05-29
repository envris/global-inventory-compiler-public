import argparse

from .utils.common_args import fix_args
from .utils.find_gremlins import find_gremlins
from .utils.logging import get_logger


def parse_args(args: list[str]) -> argparse.Namespace:
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description=(
            "Workflow to scan directory of JSONL files for chemical names "
            "that may cause issues when building an inventory."
        )
    )
    parser.add_argument(
        "-j",
        "--jsonl_dir",
        type=str,
        required=True,
        help=(
            "Directory containing JSONL files to scan. These will be found "
            "recursively in subdirectories. (required)"
        ),
    )
    parser.add_argument(
        "-g",
        "--gremlins_file",
        type=str,
        default="gremlins.csv",
        help=("Path to save CSV file containing gremlins data."),
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
        "--gremlins_cutoff",
        type=int,
        default=5,
        help=(
            "Number of times a name needs to appear in a dataframe "
            "to be considered a potential gremlin."
        ),
    )
    return parser.parse_args(args)


def main(args: list[str] | None = None) -> None:
    """Main entry point for gremlins workflow"""
    parsed = parse_args(fix_args(args))
    logger = get_logger(parsed.log)
    g_data = find_gremlins(parsed.jsonl_dir, parsed.gremlins_cutoff, logger)
    logger.info("Writing gremlins to %s", parsed.gremlins_file)
    g_data.write(parsed.gremlins_file)
    logger.info("Workflow complete.")


if __name__ == "__main__":
    main()
