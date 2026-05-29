"""List data management for GIC data structures."""

from ... import fields


class ListData:
    """Manage association between list tags and IDs."""

    def __init__(self):
        self.__list_tag_by_id: dict[int, str] = {}  # {id: list_tag}
        self.__id_by_list_tag: dict[str, int] = {}  # {list_tag: id}

    def __create(self, list_id: int, list_tag: str):
        """Create a new list tag ID."""
        self.__list_tag_by_id[list_id] = list_tag
        self.__id_by_list_tag[list_tag] = list_id

    def create_or_ignore(self, list_tag: str) -> int:
        """Create a new ID or ignore if already exists. Returns ID of
        list tag."""
        fields.validate("list_tag", list_tag)
        if list_tag in self.__id_by_list_tag:
            return self.__id_by_list_tag[list_tag]
        list_id = len(self.__list_tag_by_id) + 1
        self.__create(list_id, list_tag)
        return list_id

    def bulk_create_or_ignore(self, list_tags: list[str]) -> list[int]:
        """Create or ignore a list of list tags."""
        return [self.create_or_ignore(list_tag) for list_tag in list_tags]

    def get_list_tags(self, list_tag_ids: list[int]) -> list[str]:
        """Get list tags by IDs."""
        return [self.__list_tag_by_id[id] for id in list_tag_ids]

    def to_dict(self) -> dict[int, str]:
        """Output copy of list data as dictionary. {id: list_tag, ...}"""
        return self.__list_tag_by_id.copy()

    def from_dict(self, list_data: dict[int, str]):
        """Load complete list data from dictionary."""
        # Raise error if already assigned
        if self.__list_tag_by_id or self.__id_by_list_tag:
            raise ValueError("List data already exists in the data structure")
        for list_id, list_tag in list_data.items():
            if not isinstance(list_id, int):
                raise ValueError(f"List ID {list_id} is not an integer")
            fields.validate("list_tag", list_tag)
            self.__id_by_list_tag[list_tag] = list_id
            self.__list_tag_by_id[list_id] = list_tag
