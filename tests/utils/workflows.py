"""Utility functions for testing workflows."""

from gic.datastructs import DataFrame, Inventory
from gic.datastructs.inventory import IDENTIFIER_FIELDS


def compare_inventories(inv1: Inventory, inv2: Inventory) -> bool:
    """Compare two Inventory objects for equality. This is needed
    because to order of the dictionaries inside the Inventory may differ.
    """
    sids1 = set(inv1.get_sids())
    sids2 = set(inv2.get_sids())
    assert sids1 == sids2, f"Inventories have different SIDs: {sids1 ^ sids2}"

    for sid in sids1:
        for id_field in IDENTIFIER_FIELDS:
            ids1 = set(inv1.get_by_sids(id_field, [sid]))
            ids2 = set(inv2.get_by_sids(id_field, [sid]))
            assert ids1 == ids2, (
                f"Identifier values differ for SID {sid} and field "
                f"{id_field}: {ids1 ^ ids2}"
            )

            lists1 = set(inv1.get_by_sids("list_tag", [sid]))
            lists2 = set(inv2.get_by_sids("list_tag", [sid]))
            assert lists1 == lists2, (
                f"List tags differ for SID {sid}: {lists1 ^ lists2}"
            )

    return True


def compare_data_frames(df1: DataFrame, df2: DataFrame) -> bool:
    """Compare two DataFrame objects for equality. This is needed
    because to order of the AssociatedValues objects inside the DataFrame may differ.
    """
    assert len(df1) == len(df2), (
        f"DataFrames have different lengths: {len(df1)} vs {len(df2)}"
    )

    for index in range(len(df1)):
        av1_dict = df1.data[index].as_dict(serialise=True)
        av2_dict = df2.data[index].as_dict(serialise=True)
        keys1 = set(av1_dict.keys())
        keys2 = set(av2_dict.keys())
        assert keys1 == keys2, (
            f"AssociatedValues at index {index} have different fields: {keys1 ^ keys2}"
        )
        for key in keys1:
            values1 = set(av1_dict[key])
            values2 = set(av2_dict[key])
            assert values1 == values2, (
                f"Values for field {key} differ at index {index}: {values1 ^ values2}"
            )

    return True
