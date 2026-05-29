"""Global inventory data structure."""

import json

from .. import fields
from .associated_values import AssociatedValues
from .data_frame import DataFrame
from .utils.collection import identifiers_as_tuples, redact_identifier
from .utils.exceptions import NotInInventoryError
from .utils.identifier_data import IdentifierData
from .utils.validation import (
    IDENTIFIER_FIELDS,
    enforce_choice,
    enforce_identifier_field,
    enforce_type,
)


class Inventory:
    """Substance inventory that consolidates identifiers, list tags, and SIDs.

    The class ingests AssociatedValues rows or JSONL inventory files, merges rows
    that resolve to the same substance, maintains lookup data between substance
    identifiers and regulatory list membership, supports querying by SID,
    identifier, or list tag, and can export, reorder, enrich, or redact the
    stored inventory data.
    """

    def __init__(self, inventory_file: str = "") -> None:
        """Initialise blank inventory or load from file.

        :param inventory_file: Optional path to JSONL file to load inventory from.
        """
        self.__data: list[AssociatedValues | None] = []
        self.__identifiers = IdentifierData()
        if inventory_file:
            self.__from_jsonl(inventory_file)

    def __add(self, data: AssociatedValues) -> list[int]:
        """Add identifiers and list tags from an AssociatedValues object.

        :param data: AssociatedValues object containing identifiers
            and list tags. Other fields will be ignored.
        :return: SIDs of substances that data was added to. Will be a new SID
            if no matching SIDs are found.
        """
        data = data.copy()  # Avoid modification of external DataFrame
        identifiers = data.get_identifiers()
        sids = self.__identifiers.get_sids(identifiers)

        # Create new substance if no matching SIDs
        if len(sids) == 0:
            sid = len(self.__data) + 1
            self.__identifiers.update_from_associated_values(sid, data)
            data = data.reduce_to_fields(IDENTIFIER_FIELDS)
            self.__data.append(data)
            return [sid]

        # Add identifiers and list tags to one existing substance
        if len(sids) == 1:
            sid = sids[0]
            self.__identifiers.update_from_associated_values(sid, data)
            data = data.reduce_to_fields(IDENTIFIER_FIELDS)
            self.__data[sid - 1] = self.__get_substance(sid).merge(data)
            return [sid]

        # Merge multiple matching substances into first matching substance
        for sid in sids[1:]:
            self.__merge(sids[0], sid)

        # Add incoming identifiers and list tags to merged substance
        self.__identifiers.update_from_associated_values(sids[0], data)
        data = data.reduce_to_fields(IDENTIFIER_FIELDS)
        self.__data[sids[0] - 1] = self.__get_substance(sids[0]).merge(data)
        return [sids[0]]

    def __add_auxiliary(
        self, data: AssociatedValues, add_identifiers: set[str]
    ) -> None:
        """Add list tags to matching identifiers, and optionally add new
        identifiers without merging or creating new substances.

        :param data: AssociatedValues object containing identifiers
            and list tags. Other fields will be ignored.
        :param add_identifiers: Identifier fields to add to inventory.
            Leave blank if none to be added. New identifiers may be mapped
            to multiple substances.
        """
        identifiers = data.get_identifiers()
        list_tags = data.get_values("list_tag")
        sids = self.__identifiers.get_sids(identifiers)

        # Entire incoming data out of inventory scope
        if not sids:
            return

        # Selectively add list_tags to only matching identifiers
        for identifier_type, identifier in identifiers_as_tuples(data):
            if not self.__identifiers.get_sids([identifier]) and not add_identifiers:
                continue

            # Add new identifier data without list info
            if identifier_type in add_identifiers:
                identifier_data = {identifier: []}
                import_dict = {identifier_type: [identifier]}
                # New identifier maps to all matching SIDs
                for sid in sids:
                    self.__identifiers.update_from_dict(sid, identifier_data)
                    self.__get_substance(sid).import_from_dict(import_dict)

            # Append list info to new or existing identifier
            self.__identifiers.update_list_ids_from_tags(identifier, list_tags)

    def __check_list_tags(self, list_tags: list[str]) -> None:
        """Validate list tags and confirm they are in the inventory.

        :param list_tags: List of list tags to validate.
        :raises ValidationError: If any list tag is not valid
        :raises NotInInventoryError: If any list tag is not in inventory
        """
        enforce_type(list_tags, "list_tags", list)
        existing_tags = {tag for _, tag in self.get_list_data().items()}
        not_exist = []
        for list_tag in list_tags:
            fields.validate("list_tag", list_tag)
            if list_tag not in existing_tags:
                not_exist.append(list_tag)
        if len(not_exist) == 0:
            return
        existing_tags_str = ", ".join(existing_tags)
        raise NotInInventoryError(
            f"list_tags {not_exist} do not exist in inventory. "
            f"Valid tags are: {existing_tags_str}"
        )

    def __clean(self) -> None:
        """Remove None voids in inventory and renumber SIDs."""
        self.__data = [data for data in self.__data if data is not None]
        self.__identifiers.wipe_sids()
        for sid in range(1, len(self.__data) + 1):
            substance = self.__get_substance(sid)
            self.__identifiers.update_from_associated_values(sid, substance)

    def __from_jsonl(self, file_path: str) -> None:
        """Load inventory from JSONL file.

        :param file_path: Path to JSONL file containing inventory data.
        """
        with open(file_path, encoding="utf-8") as inventory_file:
            header = json.loads(inventory_file.readline())
            list_data = {int(k): v for k, v in header["list_data"].items()}
            self.__identifiers.list_data_from_dict(list_data)
            for line in inventory_file:
                self.__substance_from_json(line)

    def __get_data_for_sid(self, sid: int) -> AssociatedValues:
        """Return substance data as AssociatedValues object.

        :param sid: Substance ID to query
        :raises NotInInventoryError: If SID is out of range of inventory
        :return: AssociatedValues object containing data for this substance
        """
        enforce_type(sid, "sid", int)
        try:
            data = self.__get_substance(sid).copy()
            identifiers = data.get_identifiers()
            list_tags = self.__identifiers.get_list_tags(identifiers)
            data.import_from_dict({"list_tag": list_tags, "sid": [sid]})
        except IndexError as exc:
            raise NotInInventoryError(f"SID {sid} not in inventory") from exc
        return data

    def __get_substance(self, sid: int) -> AssociatedValues:
        """Return AssociatedValues object belonging to SID in type-safe way.

        This is a helper method to avoid repeated type checking of self.__data[sid - 1]
        when accessing substance data expected to be non-None.
        """
        substance = self.__data[sid - 1]
        if substance is None:
            raise ValueError(f"SID {sid} is a None void.")
        return substance

    def __merge(self, sid_1: int, sid_2: int) -> None:
        """Merge data from SID 2 into SID 1 then remove SID 2.

        :param sid_1: Substance ID to merge into
        :param sid_2: Substance ID to merge from and remove
        """
        av_1: AssociatedValues = self.__get_substance(sid_1)
        av_2: AssociatedValues = self.__get_substance(sid_2)
        for identifier in av_2.get_identifiers():
            self.__identifiers.replace_sid(identifier, sid_2, sid_1)
        merged: AssociatedValues = av_1.merge(av_2)
        self.__data[sid_1 - 1] = merged
        self.__data[sid_2 - 1] = None

    def __substance_from_json(self, json_str: str) -> None:
        """Add a substance to the inventory from JSON line.

        :param json_str: JSON string containing substance data in the format
            {sid: {field_name: {identifier_value: [list_ids], ...}, ...}}
        :raises ValueError: If JSON string is not in the correct format or contains
            invalid data.
        :raises ValueError: If SIDs are not in sequential order.
        """
        data: dict[str, dict] = json.loads(json_str)
        sid_str = list(data.keys())[0]
        sid = int(sid_str)
        identifiers_data: dict[str, dict] = data[sid_str]
        if not isinstance(identifiers_data, dict):
            raise ValueError(f"Data for SID {sid} is not a dictionary")
        av_dict = {}
        for field_name, identifier_data in identifiers_data.items():
            self.__identifiers.update_from_dict(sid, identifier_data)
            av_dict[field_name] = identifier_data.keys()
        av = AssociatedValues(av_dict)
        try:
            av.clean()
        except fields.ValidationError as exc:
            raise ValueError(f"Error cleaning data {av_dict} for SID {sid}") from exc
        self.__data.append(av)
        if len(self.__data) != sid:
            raise ValueError(f"SID {sid} is not in sequential order")

    def __substance_to_json(self, sid: int) -> str:
        """Export substance data as JSON string.

        :param sid: Substance ID to export.
        :return: JSON string representing the substance data. Format is
            {sid: {field_name: {identifier_value: [list_ids], ...}, ...}}
        """
        data_dict = self.__get_substance(sid).as_dict()
        identifier_data = {}
        for field_name, identifiers in data_dict.items():
            identifier_data[field_name] = {}
            for identifier_value in identifiers:
                identifier_data[field_name][identifier_value] = (
                    self.__identifiers.get_list_ids([identifier_value])
                )
        return json.dumps({sid: identifier_data})

    def fill(
        self,
        data_frame: DataFrame,
        field_name: str,
    ) -> DataFrame:
        """Fill a DataFrame with values from the inventory.

        :param field_name: Field to populate. Valid field names are
            'list_tag', 'sid' or an identifier field.
        :param data_frame: DataFrame object to populate with inventory data.
        :return: The data frame, which will be modified in place but
            also returned for chaining.

        Note: Values will be duplicated in the data frame if multiple rows map
            to common SIDs.
        """
        enforce_type(data_frame, "data_frame", DataFrame)
        valid_fields = IDENTIFIER_FIELDS + ["list_tag", "sid"]
        enforce_choice(field_name, "field_name", valid_fields)
        for row in data_frame:
            identifiers = row.get_identifiers()
            sids = self.get_by_identifiers("sid", identifiers)
            sids += row.get_values("sid")
            if field_name == "sid":
                row.import_from_dict({field_name: sids})
                continue
            values = self.get_by_sids(field_name, sids)
            row.import_from_dict({field_name: values})
        return data_frame

    def import_from_data_frame(
        self,
        data_frame: DataFrame,
        auxiliary=False,
        add_identifiers: set[str] | None = None,
    ):
        """Import identifier data into inventory to be processed into substances.

        :param data_frame: DataFrame object containing identifiers.
        :param auxiliary: If True, only import list tags into existing
            identifiers without merging substances or introducing
            new identifiers. Default False.
        :param add_identifiers: Set of identifier field names to add to inventory.
            Leave blank if none to be added. New identifiers may be mapped
            to multiple substances. Only applies if auxiliary=True.
        """
        enforce_type(data_frame, "data_frame", DataFrame)
        if add_identifiers is None:
            add_identifiers = set()
        enforce_type(add_identifiers, "add_identifiers", set)
        for identifier_type in add_identifiers:
            enforce_choice(identifier_type, "identifier_type", IDENTIFIER_FIELDS)
        for row in data_frame:
            if auxiliary:
                self.__add_auxiliary(row, add_identifiers)
                continue
            self.__add(row)
        self.__clean()

    def to_jsonl(self, file_path: str):
        """Write inventory to JSONL file.

        :param file_path: Path to output file. Will be overwritten if
            it already exists.
        """
        self.__clean()
        with open(file_path, "w", encoding="utf-8") as inventory_file:
            header = {}
            header["list_data"] = self.__identifiers.list_data_to_dict()
            inventory_file.write(json.dumps(header) + "\n")
            for sid, _ in enumerate(self.__data, start=1):
                inventory_file.write(self.__substance_to_json(sid) + "\n")

    def get_list_data(self) -> dict[int, str]:
        """Return all list IDs and list tags in inventory as a dictionary."""
        return self.__identifiers.list_data_to_dict()

    def get_by_sids(self, field_name: str, sids: list[int | str]) -> list[str]:
        """Return a list of values of a specified field type associated with
        these SIDs.

        :param field_name: Field to return values for, typically 'list_tag' or
            an identifier field such as 'ec_number' or 'chemical_name'
        :param sids: List of SIDs to query
        :return: Sorted list of values of the requested type
        """
        enforce_type(sids, "sids", list)
        valid_fields = IDENTIFIER_FIELDS + ["list_tag"]
        enforce_choice(field_name, "field_name", valid_fields)
        result = set()
        for sid in sids:
            data = self.__get_data_for_sid(int(sid))
            result.update(data.get_values(field_name))
        return sorted(list(result))

    def get_by_identifiers(
        self, field_name: str, identifiers: list[str]
    ) -> list[str | int]:
        """Return a list of values of specified field_name associated with
        these identifiers.

        :param field_name: Field to return values for, typically 'list_tag' or an
            identifier field such as 'sid', 'ec_number' or 'chemical_name'
        :param identifiers: List of identifiers to query. Can be
            a mixture of different types.
        :return: Sorted list of values of the requested type, or an empty list
            if none are found
        """
        valid_fields = IDENTIFIER_FIELDS + ["list_tag", "sid"]
        enforce_choice(field_name, "field_name", valid_fields)

        # Return SIDs directly associated with identifiers
        if field_name == "sid":
            return list(self.__identifiers.get_sids(identifiers))

        # Return list tags directly associated with identifiers
        if field_name == "list_tag":
            return list(self.__identifiers.get_list_tags(identifiers))

        # Return identifiers of specified type associated with
        # substances of the queried identifiers
        result = set()
        sids = self.__identifiers.get_sids(identifiers)
        for sid in sids:
            data = self.__get_data_for_sid(sid)
            result.update(data.get_values(field_name))
        field_class = fields.get_field_by_name(field_name)
        return field_class.sort_values(list(result))

    def get_sids(self) -> list[int]:
        """Return a list of all substance IDs in this inventory."""
        return list(range(1, len(self.__data) + 1))

    def get_identifiers(self, field_name: str) -> list[str]:
        """Return a sorted list of all identifiers of the specified type.

        :param field_name: Identifier field to return values for (e.g. 'ec_number')
        :return: Sorted list of all identifiers of the specified type
        """
        enforce_identifier_field(field_name)
        field_class = fields.get_field_by_name(field_name)
        result = set()
        for sid in self.get_sids():
            data = self.__get_substance(sid)
            result.update(data.get_values(field_name))
        return field_class.sort_values(list(result))

    def get_by_list_tags(
        self, field_name: str, list_tags: list[str], shared: bool = False
    ) -> list[str | int]:
        """Return all SIDs or identifiers of a specified type associated
        with any of these list tags.

        :param field_name: 'sid' or an identifier field (e.g. 'ec_number')
        :param list_tags: List of list tags that an SID or identifier must
            have at least one of to be returned. Cannot be empty.
        :param shared: If True, a substance or identifier must have all
            specified list tags to be returned. Default False.
        :return: List of SIDs or identifiers satisfying the criteria
        """
        enforce_type(list_tags, "list_tags", list)
        enforce_choice(field_name, "field_name", IDENTIFIER_FIELDS + ["sid"])
        field_class = fields.get_field_by_name(field_name)
        self.__check_list_tags(list_tags)
        result = set()
        # SID mode
        if field_name == "sid":
            for sid, _ in enumerate(self.__data, start=1):
                list_tags_of_sid = self.get_by_sids("list_tag", [sid])
                relevant_list_tags = set(list_tags).intersection(list_tags_of_sid)
                if len(relevant_list_tags) == 0:
                    continue  # Does not have any required list tag
                if shared and len(list_tags) != len(relevant_list_tags):
                    continue  # Does not have all required list tags
                result.add(sid)
            return field_class.sort_values(list(result))
        # Identifier mode
        identifiers = self.get_identifiers(field_name)
        for identifier in identifiers:
            list_tags_of_identifier = self.__identifiers.get_list_tags([identifier])
            relevant_list_tags = set(list_tags).intersection(list_tags_of_identifier)
            if len(relevant_list_tags) == 0:
                continue  # Does not have any required list tag
            if shared and len(list_tags) != len(relevant_list_tags):
                continue  # Does not have all required list tags
            result.add(identifier)
        return field_class.sort_values(list(result))

    def get_by_list_tags_unique(
        self, field_name: str, list_tags: list[str], to_ignore: list[str] | None = None
    ) -> list[str | int]:
        """Return all SIDs or identifiers of a specified type with these
        list_tags, but not any others.

        :param field_name: 'sid' or any identifier field (e.g. 'ec_number')
        :param list_tags: List of list tags that an SID or identifier must
            have to be returned
        :param to_ignore: A list of list tags an SID or identifier can
            have without being excluded from the results
        :return: List of SIDs or identifiers satisfying the criteria
        """
        enforce_type(list_tags, "list_tags", list)
        if to_ignore is not None:
            enforce_type(to_ignore, "to_ignore", list)
        enforce_choice(field_name, "field_name", IDENTIFIER_FIELDS + ["sid"])
        field_class = fields.get_field_by_name(field_name)
        self.__check_list_tags(list_tags)
        to_ignore_set = set() if to_ignore is None else set(to_ignore)
        list_tags_set = set(list_tags)
        all_list_tags = {tag for _, tag in self.get_list_data().items()}
        to_exclude = all_list_tags.difference(list_tags_set.union(to_ignore_set))
        result = set()
        # SID mode
        if field_name == "sid":
            for sid, _ in enumerate(self.__data, start=1):
                list_tags_of_sid = set(self.get_by_sids("list_tag", [sid]))
                good_list_tags = list_tags_set.intersection(list_tags_of_sid)
                bad_list_tags = list_tags_of_sid.intersection(to_exclude)
                if len(list_tags_set) != len(good_list_tags):
                    continue
                if len(bad_list_tags) > 0:
                    continue
                result.add(sid)
            return field_class.sort_values(list(result))
        # Identifier mode
        identifiers = self.get_identifiers(field_name)
        for identifier in identifiers:
            list_tags_of_identifier = set(
                self.__identifiers.get_list_tags([identifier])
            )
            good_list_tags = list_tags_set.intersection(list_tags_of_identifier)
            bad_list_tags = list_tags_of_identifier.intersection(to_exclude)
            if len(list_tags_set) != len(good_list_tags):
                continue
            if len(bad_list_tags) > 0:
                continue
            result.add(identifier)
        return field_class.sort_values(list(result))

    def get_substance_data(self, sid: int) -> AssociatedValues:
        """Return a copy of the associated values data structure for this SID.

        :param sid: Substance ID to query
        :return: Copy of associated values data structure for this SID
        """
        return self.__get_data_for_sid(sid)

    def export_as_data_frame(self, sids: list[int]) -> DataFrame:
        """Export a portion of the inventory as a DataFrame.

        :param sids: List of substance IDs to export data.
        :return: A DataFrame instance of the identifiers and list_ids
            associated with the specified sids.
        """
        enforce_type(sids, "sids", list)
        df = DataFrame()
        for sid in sids:
            df.append(self.__get_data_for_sid(sid))
        return df

    def order(self, identifier_fields: list[str]) -> None:
        """Re-order substances in the inventory by specified identifier fields.

        :param identifier_fields: List of identifier fields to order by,
            in order of precedence.
        """
        used_sids: set[int] = set()
        ordered_sids: list[int] = []
        for identifier_type in identifier_fields:
            fields.validate_field_name(identifier_type)
        # Get target order of SIDs
        for identifier_type in identifier_fields:
            ordered_identifiers = self.get_identifiers(identifier_type)
            for identifier in ordered_identifiers:
                for sid in self.get_by_identifiers("sid", [identifier]):
                    sid_int = int(sid)
                    if sid_int not in used_sids:
                        ordered_sids.append(sid_int)
                        used_sids.add(sid_int)
        # Update with new positions
        new_data: list[AssociatedValues | None] = []
        self.__identifiers.wipe_sids()
        for sid in ordered_sids:
            av = self.__get_substance(sid)
            self.__identifiers.update_from_associated_values(len(new_data) + 1, av)
            new_data.append(av)
        self.__data = new_data

    def redact_identifiers(self, identifiers: set[str], random: bool = False) -> None:
        """Redact any identifier in the inventory matching any of these identifiers,
        replacing them with an rid.

        :param identifiers: Set of identifier values to redact. Can be a mixture of
            different identifier types.
        :param random: Whether to return a random redacted identifier or a hashed one.
        """
        enforce_type(identifiers, "identifiers", set)
        for sid, data in enumerate(self.__data, start=1):
            if not data:
                continue  # Skip None void
            for field, identifier in identifiers_as_tuples(data):
                # Do not redact identifier
                if identifier not in identifiers:
                    continue

                # Update data with redacted identifier
                redacted = redact_identifier(identifier, random)
                data.import_from_dict({"rid": [redacted]}, overwrite=False)
                data.remove_value(field, identifier)

                # Update lookup with redacted identifier
                list_ids = self.__identifiers.get_list_ids([identifier])
                identifier_data = {redacted: list_ids}
                self.__identifiers.update_from_dict(sid, identifier_data)
                self.__identifiers.remove_identifier(identifier)
