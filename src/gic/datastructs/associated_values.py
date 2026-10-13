"""Data structure for storing and validating data pulled from a line/row of a file."""

import json

from .. import fields
from .utils.collection import (
    combine_lists,
    merge_dict_of_lists,
    remove_blanks_from_dict,
)
from .utils.error_logger import ErrorLog, ValidationErrorMsg
from .utils.exceptions import AssociatedValuesNotReady
from .utils.validation import IDENTIFIER_FIELDS, enforce_type


class AssociatedValues:
    """Stores associated data for a single line of input."""

    def __init__(self, data: dict[str, list]):
        """Initialise data structure with a dictionary of lists. While fields are
        validated, values are not cleaned or deserialised at this stage.

        :param data: Dictionary of lists of values, where the key is the field name.
        """
        self.is_clean = False
        data = remove_blanks_from_dict(data)
        if not data:
            raise ValueError("No data provided to initialise AssociatedValues")
        for field_name, values in data.items():
            fields.validate_field_name(field_name)
            values = list(values)  # Shallow copy to decouple from input data
            setattr(self, field_name, values)

    def __enforce_clean(self):
        """Raise AssociatedValuesNotReady if the data is not clean."""
        if self.is_clean is False:
            raise AssociatedValuesNotReady("Data must be cleaned before this operation")

    @property
    def is_clean(self) -> bool:
        """Whether the data has been cleaned."""
        return self.__is_clean

    @is_clean.setter
    def is_clean(self, value: bool) -> None:
        """Set the is_clean property."""
        enforce_type(value, "is_clean", bool)
        self.__is_clean = value

    def __field_names(self) -> list[str]:
        """Return stored data field names, excluding internal state."""
        return [
            field_name for field_name in self.__dict__ if not field_name.startswith("_")
        ]

    def __clean_values(self, field_name: str, values: list) -> list:
        """Patch, validate, and de-duplicate values for one field."""
        clean_values = []
        clean_values_serialised = set()
        for value in values:
            value = fields.patch(field_name, value)
            fields.validate(field_name, value)
            value_chk = fields.serialise(field_name, value)
            if value_chk not in clean_values_serialised:
                clean_values.append(value)
                clean_values_serialised.add(value_chk)
        return clean_values

    def as_dict(self, serialise=False) -> dict[str, list]:
        """Return data as a dictionary.

        :param serialise: Serialise values if True, otherwise return raw values.
        :return: Dictionary of lists of values, where the key is the field name.
        """
        data_dict = {}
        for field_name in self.__field_names():
            values = [value for value in getattr(self, field_name)]
            if serialise:
                self.__enforce_clean()
                values = [fields.serialise(field_name, value) for value in values]
            data_dict[field_name] = values
        return data_dict

    def clean(self) -> None:
        """Remove duplicates, patch or deserialise values, enforce validation."""
        for field_name in self.__field_names():
            clean_values = self.__clean_values(field_name, getattr(self, field_name))
            setattr(self, field_name, clean_values)
        self.is_clean = True

    def clean_and_log(self, error_log: ErrorLog, line_no: int) -> None:
        """Remove duplicates, patch or deserialise values, log validation errors.

        :param error_log: ErrorLog object to log validation errors.
        :param line_no: Line number of the data in the file.
        """
        for field_name in self.__field_names():
            clean_values = []
            clean_values_serialised = set()
            for value in getattr(self, field_name):
                try:
                    value = fields.patch(field_name, value)  # Incl. deserialise
                    fields.validate(field_name, value)
                    value_chk = fields.serialise(field_name, value)
                    if value_chk not in clean_values_serialised:
                        clean_values.append(value)
                        clean_values_serialised.add(value_chk)
                except fields.ValidationError as e:
                    error_log.append(
                        ValidationErrorMsg(field_name, value, str(e), line_no)
                    )
            setattr(self, field_name, clean_values)
        self.is_clean = True
        if not self.is_identified():
            error_log.append(
                ValidationErrorMsg("", "", "No valid identifiers found", line_no)
            )

    def copy(self) -> "AssociatedValues":
        """Create a copy of the object."""
        df_copy = AssociatedValues(self.as_dict())
        df_copy.is_clean = self.is_clean
        return df_copy

    @classmethod
    def from_json(cls, json_str: str) -> "AssociatedValues":
        """Create an AssociatedValues object from a JSON string."""
        data = cls(json.loads(json_str))
        data.clean()
        return data

    def generate(self, field_name: str) -> None:
        """Generate values for a field."""
        field_class = fields.get_field_by_name(field_name)
        self.__enforce_clean()
        if field_class.derived_from is None:
            raise ValueError(f"Field name {field_name} has no generator function")
        required_values = self.get_values(field_class.derived_from)
        generated_values = []
        for required_value in required_values:
            generated_values.append(field_class.generate(required_value))
        if generated_values:
            self.import_from_dict({field_name: generated_values}, overwrite=True)

    def get_identifiers(self) -> list[str]:
        """Extract all chemical identifiers except for sids."""
        self.__enforce_clean()
        identifiers = set()
        for field_name in IDENTIFIER_FIELDS:
            identifiers.update(self.get_values(field_name))
        return list(identifiers)

    def get_values(self, field_name: str) -> list:
        """Get values for a field."""
        fields.validate_field_name(field_name)
        self.__enforce_clean()
        return getattr(self, field_name, []).copy()

    def set_values(self, field_name: str, values: list) -> None:
        """Deserialise, validate, and set values for a field."""
        enforce_type(values, "values", list)
        if not values:
            raise ValueError("Cannot set empty values for a field")
        good_values = []
        for value in values:
            value = fields.patch(field_name, value)
            fields.validate(field_name, value)
            good_values.append(value)
        setattr(self, field_name, good_values)

    def get_fields(self) -> list[str]:
        """Get list of active field names."""
        return self.__field_names()

    def import_from_dict(self, data: dict[str, list], overwrite: bool = False) -> None:
        """Import new data from a dictionary.

        Incoming values are validated when at least one object is already clean.
        Otherwise values are stored as-is until clean() is called.

        :param data: Dictionary of lists of values, where the key is the field name.
        :param overwrite: Overwrite existing values if True, otherwise merge values.
        """
        for field_name in data:
            fields.validate_field_name(field_name)
        should_preserve_clean = self.is_clean
        for field_name, values in data.items():
            enforce_type(values, "values", list)
            if should_preserve_clean:
                values = self.__clean_values(field_name, values)
            if not overwrite and hasattr(self, field_name):
                values = combine_lists(getattr(self, field_name), values)
            setattr(self, field_name, values)
        self.is_clean = should_preserve_clean

    def is_empty(self) -> bool:
        """Object contains no fields or field values."""
        if not self.__field_names():
            return True
        return all(not getattr(self, field_name) for field_name in self.__field_names())

    def is_identified(self) -> bool:
        """Data has at least one value assigned to an identifier field."""
        self.__enforce_clean()
        for field_name in fields.get_identifier_field_names():
            if hasattr(self, field_name) and len(getattr(self, field_name)) > 0:
                return True
        return False

    def merge(self, other: "AssociatedValues") -> "AssociatedValues":
        """Merge data with another AssociatedValues object. Creates a new object."""
        merged_dict = merge_dict_of_lists(self.as_dict(), other.as_dict())
        merged_av = AssociatedValues(merged_dict)
        if self.is_clean or other.is_clean:
            merged_av.clean()
        return merged_av

    def reduce_to_fields(self, fields: list[str]) -> "AssociatedValues":
        """Return a new AssociatedValues object with only the specified fields."""
        reduced_data = {
            field: self.as_dict()[field] for field in fields if hasattr(self, field)
        }
        reduced_av = AssociatedValues(reduced_data)
        reduced_av.is_clean = self.is_clean
        return reduced_av

    def to_json(self) -> str:
        """Return data as a JSON string."""
        self.__enforce_clean()
        return json.dumps(self.as_dict(serialise=True))

    def remove_field(self, field_name: str) -> None:
        """Remove a field from the associated values object."""
        fields.validate_field_name(field_name)
        if hasattr(self, field_name):
            delattr(self, field_name)

    def remove_value(self, field_name: str, value: str) -> None:
        """Remove a specific value from a field.

        :param field_name: The name of the field.
        :param value: The value to remove from the field in serialised form.
        """
        fields.validate_field_name(field_name)
        enforce_type(value, "value", str)
        self.__enforce_clean()  # For safety if dealing with deserialised values
        if not hasattr(self, field_name):
            return
        values = getattr(self, field_name)
        new_values = [v for v in values if fields.serialise(field_name, v) != value]
        if not new_values:
            delattr(self, field_name)
            return
        setattr(self, field_name, new_values)
