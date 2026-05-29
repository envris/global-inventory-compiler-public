"""Definition of an EC Number"""

import re
from typing import Any

from . import Field, ValidationError

_ec_number_re = re.compile(
    r"^[1-9A-HJ-KM-NP-Z][0-9A-HJ-KM-NP-Z]{2}-[0-9A-HJ-KM-NP-Z]{3}-[0-9]$"
)


letter_to_number = {
    "A": 10,
    "B": 11,
    "C": 12,
    "D": 13,
    "E": 14,
    "F": 15,
    "G": 16,
    "H": 17,
    "J": 19,  # I not used
    "K": 20,
    "M": 22,
    "N": 23,  # L and O not used
    "P": 25,
    "Q": 26,
    "R": 27,
    "S": 28,
    "T": 29,
    "U": 30,
    "V": 31,
    "W": 32,
    "X": 33,
    "Y": 34,
    "Z": 35,
}


def to_digit(char: str) -> int:
    """Convert a character to its corresponding digit."""
    if char.isdigit():
        return int(char)
    return letter_to_number[char.upper()]


class ECNumberField(Field):
    """See base class Field for documentation of methods and attributes."""

    name = "ec_number"
    dtype = str
    description = "European Commission Number (EC Number)"
    is_identifier = True
    derived_from = None

    @staticmethod
    def validate(value: str) -> bool:
        if not _ec_number_re.match(value):
            raise ValidationError("Invalid format")
        number = value.replace("-", "")[:-1]
        chkdig = sum((i + 1) * to_digit(n) for i, n in enumerate(number)) % 11
        # chkdig of 10 truncated to 1
        if value[-1] != str(chkdig)[0]:
            raise ValidationError("Invalid check digit")
        return True

    @staticmethod
    def has_format(value: str) -> bool:
        return _ec_number_re.match(value) is not None

    @staticmethod
    def patch(value: Any) -> Any:
        # Already correctly formatted
        if isinstance(value, str) and "-" in value:
            return value
        # Handle EC Numbers without hyphens
        # pylint: disable=duplicate-code
        if isinstance(value, str):
            try:
                value = int(value)
            except ValueError:
                pass
        if isinstance(value, int):
            value = str(value)
            value = "-".join((value[:-4], value[-4:-1], value[-1:]))
        return value

    @staticmethod
    def generate(required_value):
        raise NotImplementedError("generate method not defined for EC Number field")

    @staticmethod
    def sort(values: list[str]) -> list[str]:
        """Custom sort EC Numbers by numeric value."""
        return sorted(values, key=lambda x: int(x.replace("-", "")))
