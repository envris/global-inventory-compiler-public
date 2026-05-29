"""Definition of a Chemical Name"""

from . import Field, ValidationError
from .utils import generic_invalid


class ChemicalNameField(Field):
    """See base class Field for documentation of methods and attributes."""

    name = "chemical_name"
    dtype = str
    description = "Chemical or Substance Name"
    is_identifier = True
    derived_from = None

    @staticmethod
    def validate(value: str) -> bool:
        val_lower = value.strip().lower()
        if len(value) > 2048:
            raise ValidationError("Exceeds 2048 characters")
        if val_lower in generic_invalid.NULL_VALUES:
            raise ValidationError("Is a null-meaning value")
        if val_lower in generic_invalid.PLACEHOLDERS:
            raise ValidationError("Is a non-specific placeholder")
        if any(value.startswith(c) for c in generic_invalid.BAD_STARTS):
            raise ValidationError("Starts with a potentially dangerous character")
        if any(c in value for c in generic_invalid.BAD_CHARS):
            raise ValidationError("Contains potentially dangerous characters")
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
