"""Definition of a list tag"""

from . import Field, ValidationError


class ListTagField(Field):
    """See base class Field for documentation of methods and attributes."""

    name = "list_tag"
    dtype = str
    description = "Short tag uniquely identifying a list"
    is_identifier = False
    derived_from = None

    @staticmethod
    def validate(value: str) -> bool:
        if len(value) < 3:
            raise ValidationError(value, "Smaller than 3 characters")
        if len(value) > 20:
            raise ValidationError(value, "Larger than 20 characters")
        return True

    @staticmethod
    def has_format(value: str) -> bool:
        raise NotImplementedError("has_format method not defined for this field")

    @staticmethod
    def patch(value: str) -> str:
        raise NotImplementedError("patch method not defined for this field")

    @staticmethod
    def generate(required_value):
        raise NotImplementedError("generate method not defined for this field")
