"""Store associated data for further mapping."""

import csv
from typing import overload

import openpyxl

from .. import fields
from .associated_values import AssociatedValues
from .utils.exceptions import AssociatedValuesNotReady, DataFrameNotReady
from .utils.io import get_output_order
from .utils.validation import enforce_type


class DataFrame:
    """List-like container for chemical records stored as AssociatedValues rows.

    The class supports row-level ingestion, aggregation and transformation of
    field values, optional indexing by identifier fields for fast lookups,
    merging rows that share a field value, generating derived fields, and
    serialising the dataset to JSONL, CSV, or XLSX.
    """

    def __init__(self) -> None:
        self.__data: list[AssociatedValues] = []
        self.__rows_by_identifier: dict[str, list[AssociatedValues]] = {}
        self.__indexed_by: str = ""

    def __add__(self, other: "DataFrame") -> "DataFrame":
        enforce_type(other, "other", DataFrame)
        new_data = DataFrame()
        new_data.data = self.data + other.data
        return new_data

    def __iter__(self):
        return iter(self.__data)

    @overload
    def __getitem__(self, key: int) -> AssociatedValues: ...

    @overload
    def __getitem__(self, key: slice) -> list[AssociatedValues]: ...

    def __getitem__(
        self, key: int | slice
    ) -> AssociatedValues | list[AssociatedValues]:
        """Allow list-style row access by index or slice."""
        return self.__data[key]

    def __len__(self) -> int:
        return len(self.data)

    @property
    def data(self) -> list[AssociatedValues]:
        """Get a copy of the list of Associated objects."""
        return self.__data.copy()

    @data.setter
    def data(self, data: list[AssociatedValues]):
        """Set data with a pre-populated list of AssociatedValues.

        :param data: List of AssociatedValues objects to set as data
        """
        enforce_type(data, "data", list)
        for row in data:
            enforce_type(row, "row", AssociatedValues)
        self.__data = data

    def append(self, data: AssociatedValues, ignore_unidentified=True) -> None:
        """Add a new row of data.

        :param data: AssociatedValues object to add as a new row
        :param ignore_unidentified: Ignore if the object is not identified
            with at least one substance identifier (e.g., orphan data)
        """
        enforce_type(data, "data", AssociatedValues)
        if not data.is_clean:
            raise AssociatedValuesNotReady(
                "AssociatedValues object must be cleaned before appending to DataFrame"
            )
        if ignore_unidentified and not data.is_identified():
            return
        self.__data.append(data)

    def count_empties(self, field_name: str) -> int:
        """Count the number of objects without a value set for field.

        :param field_name: The name of the field to check for empty values.
        """
        count = 0
        for data in self.__data:
            if len(data.get_values(field_name)) == 0:
                count += 1
        return count

    @classmethod
    def from_jsonl(cls, file_path: str) -> "DataFrame":
        """Initialise a DataFrame from a JSONL file.

        :param file_path: Path to JSONL file to read from
        """
        data = cls()
        with open(file_path, encoding="utf-8") as f:
            for line in f:
                av = AssociatedValues.from_json(line)
                data.append(av)
        return data

    def generate(self, field_name: str) -> None:
        """Generate field values from values using pre-populated required fields.

        :param field_name: The name of the field to generate.
        """
        fields.validate_field_name(field_name)
        active_fields = self.get_active_fields()
        field_class = fields.get_field_by_name(field_name)
        if field_class.derived_from not in active_fields:
            raise DataFrameNotReady(
                f"Required field {field_class.derived_from} not in any data"
            )
        for row in self.__data:
            row.generate(field_name)

    def get_active_fields(self) -> set[str]:
        """Return a set of field names used at least once throughout the data frame."""
        active_fields = set()
        for row in self.__data:
            active_fields.update(row.get_fields())
        return active_fields

    def get_values(self, field_name: str) -> list:
        """Get sorted list of unique values under a given field name.

        :param field_name: The name of the field to extract values from.
        """
        fields.validate_field_name(field_name)
        values = set()
        for row in self.__data:
            values.update(row.get_values(field_name))
        return fields.sort_values(field_name, list(values))

    def get_values_by_identifiers(
        self, field_name: str, identifiers: list[str], ignore_invalid=False
    ) -> list:
        """Get sorted unique values for a field name and list of identifiers.

        :param field_name: Field to extract values from
        :param identifiers: Extract values from rows containing this identifier
        :param ignore_invalid: Set as True if you want the identifiers to validated
            against the indexed field type
        """
        fields.validate_field_name(field_name)
        if not self.is_indexed_by_identifier():
            raise DataFrameNotReady(
                "Data must be indexed by an identifier before this method can be used"
            )
        values = set()
        for identifier in identifiers:
            if not ignore_invalid:
                fields.validate(self.__indexed_by, identifier)
            if identifier not in self.__rows_by_identifier:
                continue
            for row in self.__rows_by_identifier[identifier]:
                values.update(row.get_values(field_name))
        return fields.sort_values(field_name, list(values))

    def index_by_identifier(self, field_name: str) -> None:
        """Index data by a field name that corresponds to an identifier field.

        :param field_name: The name of the field to index by. Must be an identifier
        """
        if not fields.is_identifier_field(field_name):
            raise ValueError(f"Field name {field_name} is not a valid identifier field")
        self.__rows_by_identifier = {}
        for row in self.__data:
            identifiers = row.get_values(field_name)
            for identifier in identifiers:
                if identifier not in self.__rows_by_identifier:
                    self.__rows_by_identifier[identifier] = []
                self.__rows_by_identifier[identifier].append(row)
        self.__indexed_by = field_name

    def is_indexed_by_identifier(self) -> bool:
        """Check if data is indexed by an identifier."""
        return bool(self.__rows_by_identifier)

    def merge_rows_by_field(self, field_name: str) -> None:
        """Merge rows that share one or more values for a given field.

        Rows with no values for ``field_name`` are kept unchanged and appended
        after the merged rows.

        :param field_name: The field name used to group and merge rows.
        """
        data_dict: dict[str, AssociatedValues] = {}
        nulls: list[AssociatedValues] = []
        for row in self.__data:
            values = row.get_values(field_name)
            if len(values) == 0:
                nulls.append(row)
                continue
            for value in values:
                if value not in data_dict:
                    data_dict[value] = row.copy()
                else:
                    data_dict[value] = data_dict[value].merge(row)
        # Collect merged data, removing duplicates
        existing = set()
        new_data = []
        for _, row in data_dict.items():
            values = sorted(row.get_values(field_name))
            values = "".join([str(value) for value in values])
            if values in existing:
                continue  # Duplicates happen when rows have multiple indexing values
            existing.add(values)
            new_data.append(row)
        self.__data = new_data + nulls

    def remove_empty_rows(self) -> None:
        """Remove rows that have no data."""
        new_data = []
        for row in self.__data:
            if not row.is_empty():
                new_data.append(row)
        self.__data = new_data

    def remove_unidentified_rows(self) -> None:
        """Remove rows that have no identifier values."""
        new_data = []
        for row in self.__data:
            if row.is_identified():
                new_data.append(row)
        self.__data = new_data

    def to_jsonl(self, file_path: str) -> None:
        """Write data as a JSONL file."""
        with open(file_path, "w", newline="", encoding="utf-8") as f:
            for row in self.__data:
                f.write(row.to_json() + "\n")

    def to_csv(
        self,
        file_path: str,
        delimiter: str = ",",
        subdelimiter: str = ";",
    ) -> None:
        """Write data to a CSV file.

        :param file_path: Path to output file
        :param delimiter: Delimiter to separate fields (default: tab)
        :param subdelimiter: Delimiter to separate multiple values within a field
            (default: semicolon)
        """
        active_fields = self.get_active_fields()
        header = [
            field_name
            for field_name in get_output_order()
            if field_name in active_fields
        ]
        with open(file_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f, delimiter=delimiter)
            writer.writerow(header)
            for row in self.__data:
                row_out = []
                for field_name in header:
                    values = row.get_values(field_name)
                    values = [fields.serialise(field_name, value) for value in values]
                    values = [str(value) for value in values]
                    # Zero values should not occur since values should be cleaned
                    if len(values) == 1:
                        row_out.append(values[0])
                    else:
                        row_out.append(subdelimiter.join(values))
                writer.writerow(row_out)

    def to_xlsx(self, file_path: str, subdelimiter: str = ";") -> None:
        """Write data to an XLSX file.

        :param file_path: Path to output file
        :param subdelimiter: Delimiter to separate multiple values within a field
            (default: semicolon)
        """
        active_fields = self.get_active_fields()
        header = [
            field_name
            for field_name in get_output_order()
            if field_name in active_fields
        ]
        workbook = openpyxl.Workbook()
        sheet = workbook.active
        if sheet is None:
            sheet = workbook.create_sheet()
        sheet.append(header)
        for row in self.__data:
            row_out = []
            for field_name in header:
                values = row.get_values(field_name)
                values = [fields.serialise(field_name, value) for value in values]
                values = [str(value) for value in values]
                # Zero values should not occur since values should be cleaned
                if len(values) == 1:
                    row_out.append(values[0])
                else:
                    row_out.append(subdelimiter.join(values))
            sheet.append(row_out)
        workbook.save(file_path)
