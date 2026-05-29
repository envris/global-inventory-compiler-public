"""Top-level classes"""

import importlib
import inspect
import pkgutil

from .base.exceptions import ValidationError
from .base.field import Field
from .base.testing import FieldTestCases

__all__ = ["FieldTestCases"]


def _get_all_field_subclasses() -> list[type[Field]]:
    """Return all Field subclasses in the fields package, excluding Field itself."""
    subclasses = set()
    package_path = __path__  # This is set for packages
    for _, module_name, is_pkg in pkgutil.iter_modules(package_path):
        if is_pkg:
            continue
        module = importlib.import_module(f"{__name__}.{module_name}")
        for _, cls in inspect.getmembers(module, inspect.isclass):
            if issubclass(cls, Field) and cls is not Field:
                subclasses.add(cls)
    return list(subclasses)


# Pre-determined global variables
ALL_FIELDS = _get_all_field_subclasses()
IDENTIFIER_FIELDS = [cls for cls in ALL_FIELDS if cls.is_identifier]
FIELD_BY_NAME = {cls.name: cls for cls in ALL_FIELDS}
IDENTIFIER_FIELDS_BY_NAME = {cls.name: cls for cls in IDENTIFIER_FIELDS}


def get_field_by_name(name: str) -> type[Field]:
    """Get a Field subclass by its name.

    :param name: The name of the field.
    :return: The Field subclass corresponding to the given name.
    :raises ValueError: If the field name is not found.
    """
    if name not in FIELD_BY_NAME:
        raise ValueError(f"Field with name '{name}' not found.")
    return FIELD_BY_NAME[name]


def get_identifier_field_names() -> list[str]:
    """Get names of all Field subclasses that are identifiers."""
    return list(IDENTIFIER_FIELDS_BY_NAME.keys())


def is_identifier_field(name: str) -> bool:
    """Returns True if the field name corresponds to an identifier field."""
    return name in IDENTIFIER_FIELDS_BY_NAME


def validate_field_name(name: str) -> bool:
    """Returns True if a field name is valid. Otherwise raises ValueError.

    :param name: The name of the field.
    :return: True if the field name is valid, otherwise raises ValueError.
    :raises ValueError: If the field name is not found.
    """
    if name not in FIELD_BY_NAME:
        raise ValueError(f"Field with name '{name}' not found.")
    return True


def validate(field_name: str, value) -> bool:
    """Validate a value against the specified field name.

    :param field_name: The name of the field.
    :param value: The value to validate.
    :return: True if the value is valid for the field, otherwise raises ValidationError.
    :raises ValidationError: If the value is not valid for the field.
    :raises ValueError: If the field name is not found.
    """
    field_class = get_field_by_name(field_name)
    if not isinstance(value, field_class.dtype):
        raise ValidationError(
            f"{field_class.name} value {value} not of type {field_class.dtype}."
        )
    try:
        field_class.validate(value)
    except NotImplementedError:
        pass
    return True


def patch(field_name: str, value):
    """Patch a value based on common issues that are expected. Includes
    deserialisation of values.

    :param field_name: The name of the field.
    :param value: The value to patch.
    :return: The patched equivalent of the value.
    :raises ValueError: If the field name is not found.
    """
    field_class = get_field_by_name(field_name)
    try:
        value = field_class.patch(value)
    except NotImplementedError:
        pass
    return value


def match(value: str, identifiers_only=False) -> str | None:
    """Match a value to a field name based on its format.

    :param value: The value to match.
    :param identifiers_only: If True, only consider identifier fields.
    :return: The name of the matching field or None if no match is found.
    """
    if identifiers_only:
        field_classes = IDENTIFIER_FIELDS
    else:
        field_classes = ALL_FIELDS
    for field_class in field_classes:
        try:
            if field_class.has_format(value):
                return field_class.name
        except NotImplementedError:
            continue
    return None


def serialise(field_name: str, value) -> str | int | float:
    """Serialise a value for a field name.

    :param field_name: The name of the field.
    :param value: The value to serialise.
    :return: The serialised equivalent of the value.
    """
    field_class = get_field_by_name(field_name)
    try:
        return field_class.serialise(value)
    except NotImplementedError:
        pass
    return value


def sort_values(field_name: str, values: list) -> list:
    """Sort a list of values for a field name.

    :param field_name: The name of the field.
    :param values: The list of values to sort.
    :return: The sorted list of values.
    """
    field_class = get_field_by_name(field_name)
    try:
        return field_class.sort_values(values)
    except NotImplementedError:
        pass
    return sorted(values)
