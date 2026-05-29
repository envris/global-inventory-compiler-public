"""Custom exceptions used in data structures."""


class AssociatedValuesNotReady(Exception):
    """Raised if an AssociatedValues object has not been cleaned prior
    to implementing a method."""


class DataFrameNotReady(Exception):
    """Raised if a DataFrame object has not been prepared prior
    to implementing a method."""


class NotInInventoryError(Exception):
    """Raise when a value has been queried that is not in the inventory."""
