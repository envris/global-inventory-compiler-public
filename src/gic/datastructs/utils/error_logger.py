"""Record invalid data and errors in a log file."""

import csv


class ValidationErrorMsg:
    def __init__(self, field_name: str, value: str, message: str, line_no: int):
        self.line_no = line_no
        self.field_name = field_name
        self.value = value
        self.message = message


class ErrorLog:
    def __init__(self):
        self.__log: list[ValidationErrorMsg] = []

    def __getitem__(self, key):
        return self.__log[key]

    def __len__(self):
        return len(self.__log)

    def append(self, error: ValidationErrorMsg) -> None:
        self.__log.append(error)

    def write(self, file_path: str) -> None:
        with open(file_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f, delimiter="\t")
            writer.writerow(["Line", "Field", "Value", "Message"])
            for error in self.__log:
                writer.writerow(
                    [error.line_no, error.field_name, error.value, error.message]
                )
