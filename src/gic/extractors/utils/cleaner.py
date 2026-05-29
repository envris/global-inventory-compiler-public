"""Clean up data."""

from ...fields.utils import generic_invalid


class Cleaner:
    """Clean up dictionary of data."""

    def __init__(self) -> None:
        """Initialise filter with a list of allowed values."""
        self.__to_ignore: set = generic_invalid.NULL_VALUES.copy()

    def filter_data(self, data: dict[str, list]) -> dict:
        """Filter out unwanted values from data."""
        new_data = {}
        for field_name, values in data.items():
            new_values = []
            for value in values:
                if value is None or value == "":
                    continue
                if isinstance(value, str):
                    value = value.strip()
                if isinstance(value, str) and value.lower() in self.__to_ignore:
                    continue
                if value not in new_values:
                    new_values.append(value)
            if new_values:
                new_data[field_name] = new_values
        return new_data

    def add_ignore(self, to_ignore: set[str] | list[str]) -> None:
        """Set values to ignore."""
        self.__to_ignore.update(to_ignore)
