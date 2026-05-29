"""Definition of a Redacted Identifier (RID)"""

import re

from . import Field, ValidationError

# Regex for RIDXXXXXXXXXXXXXXXX, where X is a number or capital letter
_rid_re = re.compile(r"^RID[A-Z0-9]{16}$")


class RIDField(Field):
    """See base class Field for documentation of methods and attributes."""

    name = "rid"
    dtype = str
    description = "Redacted Identifier (RID)"
    is_identifier = True
    derived_from = None

    @staticmethod
    def validate(value: str) -> bool:
        if not _rid_re.match(value):
            raise ValidationError("Invalid format")
        return True

    @staticmethod
    def has_format(value: str) -> bool:
        raise NotImplementedError("has_format method not defined for this field")

    @staticmethod
    def patch(value):
        raise NotImplementedError("patch method not defined for this field")

    @staticmethod
    def generate(required_value):
        raise NotImplementedError("generate method not defined for this field")
