"""Generic extractors for Excel and CSV files."""

from .. import fields
from ..datastructs import DataFrame
from ..datastructs.utils.error_logger import ErrorLog
from .utils.cleaner import Cleaner


class GenericExtractor:
    """Parameters and high level methods. Change the
    extraction_method to implement a new extractor."""

    def __init__(self) -> None:
        """Initialize parameters."""
        self.cleaner: Cleaner = Cleaner()
        self.__constants: dict[int, str] = {}
        self.__sheet_name: str = ""
        self.__start_row: int = 1
        self.__columns: dict[int, str] = {}
        self.__delimiter: str = ","
        self.__subdelimiter: str = ""
        self.__input_file: str = ""
        self.__output_file: str = ""
        self.__errors_file: str = ""
        self.__error_log: ErrorLog = ErrorLog()
        self.__df: DataFrame = DataFrame()

    @property
    def constants(self) -> dict:
        """Get the constants."""
        return self.__constants

    @constants.setter
    def constants(self, constants: dict) -> None:
        """Set the constants."""
        for field_name, values in constants.items():
            for value in values:
                fields.validate_field_name(field_name)
                fields.validate(field_name, value)
        self.__constants = constants

    @property
    def sheet_name(self) -> str:
        """Get the sheet name."""
        return self.__sheet_name

    @sheet_name.setter
    def sheet_name(self, value: str) -> None:
        """Set the sheet name."""
        self.__sheet_name = value

    @property
    def start_row(self) -> int:
        """Get the start row."""
        return self.__start_row

    @start_row.setter
    def start_row(self, value: int) -> None:
        """Set the start row."""
        if value < 1:
            raise ValueError(f"Invalid start row {value}. Rows must start from 1.")
        self.__start_row = value

    @property
    def columns(self) -> dict[int, str]:
        """Get the columns."""
        return self.__columns

    @columns.setter
    def columns(self, value: dict[int, str]) -> None:
        """Set the columns."""
        used_cols = set()
        for column_number, field_name in value.items():
            if column_number < 1:
                raise ValueError(
                    f"Invalid column {column_number}. Column must be numbered from 1."
                )
            if column_number in used_cols:
                raise ValueError(f"Column {column_number} is already in use")
            used_cols.add(column_number)
            fields.validate_field_name(field_name)
        self.__columns = value

    @property
    def delimiter(self) -> str:
        """Get the delimiter."""
        return self.__delimiter

    @delimiter.setter
    def delimiter(self, value: str) -> None:
        """Set the delimiter."""
        self.__delimiter = value

    @property
    def subdelimiter(self) -> str:
        """Get the subdelimiter."""
        return self.__subdelimiter

    @subdelimiter.setter
    def subdelimiter(self, value: str) -> None:
        """Set the subdelimiter."""
        self.__subdelimiter = value

    @property
    def input_file(self) -> str:
        """Get the input file."""
        return self.__input_file

    @input_file.setter
    def input_file(self, value: str) -> None:
        """Set the input file."""
        self.__input_file = value

    @property
    def output_file(self) -> str:
        """Get the output file."""
        return self.__output_file

    @output_file.setter
    def output_file(self, value: str) -> None:
        """Set the output file."""
        self.__output_file = value

    @property
    def errors_file(self) -> str:
        """Get the errors file."""
        return self.__errors_file

    @errors_file.setter
    def errors_file(self, value: str) -> None:
        """Set the errors file."""
        self.__errors_file = value

    @property
    def error_log(self) -> ErrorLog:
        """Get the error log."""
        return self.__error_log

    @error_log.setter
    def error_log(self, value: ErrorLog) -> None:
        """Set the error log."""
        self.__error_log = value

    @property
    def df(self) -> DataFrame:
        """Get the unmapped data."""
        return self.__df

    @df.setter
    def df(self, value: DataFrame) -> None:
        """Set the unmapped data."""
        self.__df = value

    def check(self) -> bool:
        """Check if the extractor is ready."""
        if not self.__columns:
            raise ValueError("No columns specified")
        if not self.__input_file:
            raise ValueError("No input file specified")
        return True

    def extraction_method(self):
        """Define method here."""
        raise NotImplementedError

    def extract(self) -> DataFrame:
        """Run the extractor."""
        self.check()
        self.extraction_method()
        if self.__output_file:
            self.__df.to_jsonl(self.__output_file)
        if self.__errors_file:
            self.__error_log.write(self.__errors_file)
        return self.__df
