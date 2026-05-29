"""Definition of a GIC Substance Identifier (SID)"""

from typing import Any

from . import Field, ValidationError


class SIDField(Field):
    """See base class Field for documentation of methods and attributes."""

    name = "sid"
    dtype = int
    description = "GIC Substance Identifier (SID)"
    is_identifier = True
    derived_from = None

    @staticmethod
    def validate(value: int) -> bool:
        if value < 1:
            raise ValidationError("SID must be greater than 0")
        return True

    @staticmethod
    def has_format(value: str) -> bool:
        raise NotImplementedError("has_format method not defined for this field")

    @staticmethod
    def patch(value: Any) -> Any:
        if isinstance(value, int):
            return value
        try:
            return int(value)
        except ValueError:
            return value

    @staticmethod
    def generate(required_value):
        raise NotImplementedError("generate method not defined for SID field")

    @staticmethod
    def serialise(value: int) -> str:
        return str(value)
