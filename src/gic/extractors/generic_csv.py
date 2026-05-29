"""Generic CSV extractor."""

import csv

from ..datastructs import AssociatedValues
from .generic import GenericExtractor


class GenericCsvExtractor(GenericExtractor):
    """Extract data from a CSV file."""

    def extraction_method(self):
        """Extract data from a CSV file."""
        with open(self.input_file, encoding="utf-8") as f:
            reader = csv.reader(f, delimiter=self.delimiter)
            # Skip headers
            for _ in range(self.start_row - 1):
                next(reader)

            # Extract data
            for row in reader:
                data: dict[str, list] = {}
                for column_number, field in self.columns.items():
                    if self.subdelimiter:
                        values = row[column_number - 1].split(self.subdelimiter)
                    else:
                        values = [row[column_number - 1]]
                    if field not in data:
                        data[field] = []
                    for value in values:
                        value = value.strip()
                        if value not in data[field]:
                            data[field].append(value)
                data = self.cleaner.filter_data(data)
                associated_values = AssociatedValues(data)
                associated_values.import_from_dict(self.constants, overwrite=False)
                associated_values.clean_and_log(self.error_log, reader.line_num)
                self.df.append(associated_values)
