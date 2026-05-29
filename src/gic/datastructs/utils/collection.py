"""Helpers for cleaning and merging collections."""

from __future__ import annotations

import os
from hashlib import sha256
from typing import TYPE_CHECKING

from .validation import IDENTIFIER_FIELDS

if TYPE_CHECKING:
    from ..associated_values import AssociatedValues


def combine_lists(list1: list, list2: list) -> list:
    """Combine two lists into one while avoiding duplicates."""
    combined_list = list1.copy()
    for item in list2:
        if item not in combined_list:
            combined_list.append(item)
    return combined_list


def merge_dict_of_lists(
    dict1: dict[str, list], dict2: dict[str, list]
) -> dict[str, list]:
    """Merge two dictionaries of lists, combining lists for shared keys."""
    merged_dict = {}
    for key in dict1.keys():
        merged_dict[key] = combine_lists(dict1[key], dict2.get(key, []))
    # Add any keys that are only in dict2
    for key in dict2.keys():
        if key not in merged_dict:
            merged_dict[key] = dict2[key]
    return merged_dict


def remove_blanks_from_dict(dict_: dict) -> dict:
    """Remove keys with empty values from a dictionary."""
    return {k: v for k, v in dict_.items() if v}


def identifiers_as_tuples(data: AssociatedValues) -> list[tuple[str, str]]:
    """Extract identifiers from AssociatedValues object into a list of
    tuples like [("ec_number", "200-002-3"), ...]"""
    id_tuples = []
    for identifier_type in IDENTIFIER_FIELDS:
        values = data.get_values(identifier_type)
        if not values:
            continue
        for value in values:
            id_tuples.append((identifier_type, value))
    return id_tuples


def redact_identifier(identifier: str, random: bool) -> str:
    """Redact and identifier to a format 'RIDXXXXXXXXXXXXXXXX'
    where X is a number or capital letter.

    :param identifier: The identifier to redact.
    :param random: Whether to return a random
        redacted identifier or a hashed one.
    """
    if not random:
        hashed_value = sha256(identifier.encode("utf-8")).hexdigest()[:16].upper()
        return f"RID{hashed_value}"
    random_hash = sha256(os.urandom(16)).hexdigest()[:16].upper()
    return f"RID{random_hash}"
