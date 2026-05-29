"""Function to find files in a directory."""

import glob
import os


def find_jsonl_files(jsonl_dir: str) -> list[str]:
    """Find all JSONL files in a directory and its subdirectories.

    :param jsonl_dir: Directory containing JSONL files
    :return: List of paths to JSONL files
    """
    if not os.path.isdir(jsonl_dir):
        raise NotADirectoryError(f"JSONL Directory {jsonl_dir} does not exist")
    files = glob.glob(jsonl_dir + "/**/*.jsonl", recursive=True)
    num_files = len(files)
    if num_files == 0:
        raise FileNotFoundError(f"No JSONL files found in {jsonl_dir}")
    return files
