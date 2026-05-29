"""Utility for adding common workflow arguments to ArgumentParser."""

import sys


def fix_args(args: list[str] | None) -> list[str]:
    """Get args from a list or from a shell."""
    if args is None:
        args = sys.argv[1:]  # Shell
    return args
