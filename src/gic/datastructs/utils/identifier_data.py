"""Identifier data management for GIC data structures."""

from ... import fields
from ..associated_values import AssociatedValues
from .list_data import ListData
from .validation import enforce_type


class Identifier:
    """Manage sids and list tags associated with identifier."""

    def __init__(self, sids: list[int], list_ids: list[int]):
        self.sids = sids
        self.list_ids = list_ids

    @property
    def sids(self) -> list[int]:
        return self._sids

    @sids.setter
    def sids(self, sids: list[int]):
        enforce_type(sids, "sids", list)
        for sid in sids:
            fields.validate("sid", sid)
        self._sids = sids

    @property
    def list_ids(self) -> list[int]:
        return self._list_ids

    @list_ids.setter
    def list_ids(self, list_ids: list[int]):
        enforce_type(list_ids, "list_ids", list)
        for list_id in list_ids:
            enforce_type(list_id, "list_id", int)
        self._list_ids = sorted(list(set(list_ids)))

    def append_sids(self, sids: list[int]):
        """Append unique sids to existing sids and sort."""
        enforce_type(sids, "sids", list)
        for sid in sids:
            fields.validate("sid", sid)
        self._sids = sorted(list(set(self._sids + sids)))

    def append_list_ids(self, list_ids: list[int]):
        """Append unique list IDs to existing list IDs and sort."""
        enforce_type(list_ids, "list_ids", list)
        for list_id in list_ids:
            enforce_type(list_id, "list_id", int)
        self._list_ids = sorted(list(set(self._list_ids + list_ids)))


class IdentifierData:
    """Manage association between identifiers, substance IDs, and list tags."""

    def __init__(self):
        self.__list_data = ListData()
        self.__data: dict[str, Identifier] = {}

    def get_sids(self, identifiers: list[str]) -> list[int]:
        """Get substance IDs by list of identifiers."""
        enforce_type(identifiers, "identifiers", list)
        sids = set()
        for identifier_value in identifiers:
            enforce_type(identifier_value, "identifier", str)
            if identifier_value in self.__data:
                sids.update(self.__data[identifier_value].sids)
        return sorted(list(sids))

    def get_list_ids(self, identifiers: list[str]) -> list[int]:
        """Get copy of list IDs associated with identifier."""
        enforce_type(identifiers, "identifiers", list)
        list_ids = set()
        for identifier_value in identifiers:
            enforce_type(identifier_value, "identifier", str)
            if identifier_value in self.__data:
                list_ids.update(self.__data[identifier_value].list_ids)
        return sorted(list(list_ids))

    def get_list_tags(self, identifiers: list[str]) -> list[str]:
        """Get list tags by identifiers."""
        return self.__list_data.get_list_tags(self.get_list_ids(identifiers))

    def update_list_ids_from_tags(self, identifier_value: str, list_tags: list[str]):
        """Update list IDs for an identifier from list tags. This is used to
        update list IDs when list tags are updated."""
        list_ids = self.__list_data.bulk_create_or_ignore(list_tags)
        if identifier_value not in self.__data:
            raise ValueError(f"Identifier {identifier_value} does not exist")
        self.__data[identifier_value].append_list_ids(list_ids)

    def replace_sid(self, identifier_value: str, old_sid: int, new_sid: int):
        """Replace an old SID with a new SID for an identifier. This is used to
        update SIDs when substances are merged or split."""
        if identifier_value not in self.__data:
            raise ValueError(f"Identifier {identifier_value} does not exist")
        if old_sid not in self.__data[identifier_value].sids:
            raise ValueError(
                f"Old SID {old_sid} is not associated with identifier "
                f"{identifier_value}"
            )
        self.__data[identifier_value].sids.remove(old_sid)
        self.__data[identifier_value].append_sids([new_sid])

    def update_from_associated_values(self, sid: int, data: AssociatedValues):
        """Create new identifiers or update existing ones from an
        AssociatedValues instance. All identifiers in the instance will be
        associated with the same SID and list tags.

        :param sid: Substance ID to associate with the identifiers.
        :param data: AssociatedValues instance containing identifiers and list tags.
        """
        identifiers = data.get_identifiers()
        list_tags = data.get_values("list_tag")
        list_ids = self.__list_data.bulk_create_or_ignore(list_tags)
        for identifier_value in identifiers:
            # Update existing identifier with new SID and list tags
            if identifier_value in self.__data:
                self.__data[identifier_value].append_sids([sid])
                self.__data[identifier_value].append_list_ids(list_ids)
                continue
            # Create a new identifier with SID and list tags
            self.__data[identifier_value] = Identifier(sids=[sid], list_ids=list_ids)

    def update_from_dict(self, sid: int, identifier_data: dict[str, list[int]]):
        """Create new identifiers or update existing ones from a dictionary. All
        identifiers in the dictionary will be associated with the same SID.

        :param sid: Substance ID to associate with the identifiers.
        :param identifier_data: Dictionary mapping identifier values to list of
            list IDs. Example: {identifier_value: [list_ids], ...}
        """
        for identifier_value, list_ids in identifier_data.items():
            if not isinstance(identifier_value, str):
                raise ValueError(f"Identifier value {identifier_value} is not a string")
            for list_id in list_ids:
                if not isinstance(list_id, int):
                    raise ValueError(f"List ID {list_id} is not an integer")
                if not self.__list_data.get_list_tags([list_id]):
                    raise ValueError(
                        f"List ID {list_id} does not exist in the data structure"
                    )
            if identifier_value in self.__data:
                self.__data[identifier_value].append_sids([sid])
                self.__data[identifier_value].append_list_ids(list_ids)
                continue
            self.__data[identifier_value] = Identifier(sids=[sid], list_ids=list_ids)

    def to_dict(self, identifier_value: str) -> dict[str, list[int]]:
        """Output identifier data as dictionary. {identifier_value: [list_ids], ...}"""
        return {identifier_value: self.get_list_ids([identifier_value])}

    def list_data_to_dict(self) -> dict[int, str]:
        """Get list data as dictionary. Used to write inventory
        file header. {id: list_tag, ...}"""
        return self.__list_data.to_dict()

    def list_data_from_dict(self, list_data: dict[int, str]):
        """Load list data from dictionary. {id: list_tag, ...}"""
        self.__list_data.from_dict(list_data)

    def remove_identifier(self, identifier_value: str):
        """Remove an identifier and all associated SIDs and list tags from
        the data structure."""
        if identifier_value in self.__data:
            del self.__data[identifier_value]

    def update_list_data(self, list_data: dict[int, str]):
        """Update list data. This is used to add new list tags to the data
        structure."""
        self.__list_data.from_dict(list_data)

    def wipe_sids(self):
        """Reset all SIDs to none. This is typically required when cleaning
        or re-ordering the inventory."""
        for identifier in self.__data.values():
            identifier.sids = []
