from ...datastructs import DataFrame
from .gremlins_data import GremlinsData


def remove_gremlins(g_data: GremlinsData, df: DataFrame) -> list[str]:
    """Remove gremlin chemical names from dataframe.

    :param g_data: GremlinsData object containing flagged gremlins
        and the lists they are applicable.
    :param df: Dataframe to remove gremlins. This is done in place.
    :returns: List of gremlins that were removed from the dataframe.
    """
    removed_gremlins = set()
    for row in df:
        identifiers = row.get_values("chemical_name")
        list_tags = set(row.get_values("list_tag"))
        filtered_ids = []
        for identifier in identifiers:
            if g_data.is_gremlin(identifier, list_tags):
                removed_gremlins.add(identifier)
            else:
                filtered_ids.append(identifier)
        row.set_values("chemical_name", filtered_ids)
    return list(removed_gremlins)
