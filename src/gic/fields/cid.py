"""Definition of a Pubchem CID"""

import re
from typing import Any

from . import Field, ValidationError

# Regex for "CID12345678"
_cid_re = re.compile(r"^CID(\d+)$")


class CIDField(Field):
    """See base class Field for documentation of methods and attributes."""

    name = "cid"
    dtype = str
    description = "PubChem Compound Identifier (CID)"
    is_identifier = True
    derived_from = None

    @staticmethod
    def validate(value: str) -> bool:
        if not _cid_re.match(value):
            raise ValidationError("Invalid format")
        return True

    @staticmethod
    def has_format(value: str) -> bool:
        return _cid_re.match(value) is not None

    @staticmethod
    def patch(value: Any) -> Any:
        # Already correctly formatted
        if isinstance(value, str) and value.startswith("CID"):
            return value
        # Handle integer CIDs
        if isinstance(value, int):
            value = str(value)
        if isinstance(value, str):
            value = "CID" + value
        return value

    @staticmethod
    def generate(required_value):
        raise NotImplementedError("CID generation is not supported")
