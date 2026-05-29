"""Helper functions for input/output operations."""

from gic.fields import ALL_FIELDS


def get_output_order() -> list[str]:
    """Get the order of serializable fields for CSV/TSV output.

    :return: A list of field names in the order they
        should appear in CSV output.
    """
    identifier_fields = []
    data_fields = []
    for field in ALL_FIELDS:
        if field.name in {"sid", "list_tag"}:
            continue
        if field.is_identifier:
            identifier_fields.append(field.name)
        else:
            data_fields.append(field.name)

    return [
        "sid",
        *sorted(identifier_fields),
        *sorted(data_fields),
        "list_tag",
    ]
