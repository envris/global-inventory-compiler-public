import csv
from dataclasses import dataclass

from ... import fields


@dataclass
class Gremlin:
    """Class to hold data for a gremlin. A gremlin is a chemical name that
    does not uniquely identify a substance - like a placeholder (e.g., no
    name provided) or chemical group name. A chemical name is flagged as
    a potential gremlin if it has occurred more than a specified number
    of times in a Data Frame.
    """

    chemical_name: str  # Chemical name flagged as a potential gremlin
    occurrences: int  # Number of times it has been encountered
    list_tags: set[str]  # Lists that it has been flagged as a gremlin


class GremlinsData:
    """Container for gremlins data."""

    def __init__(self, gremlins_file=""):
        self.gremlins: dict[str, Gremlin] = {}
        if gremlins_file:
            self.__from_csv(gremlins_file)

    def __add__(self, other: "GremlinsData") -> "GremlinsData":
        """Combine two GremlinsData instances."""
        combined = GremlinsData()
        combined.gremlins = self.gremlins.copy()
        for key, gremlin in other.gremlins.items():
            if key in combined.gremlins:
                combined.gremlins[key].occurrences += gremlin.occurrences
                combined.gremlins[key].list_tags.update(gremlin.list_tags)
            else:
                combined.gremlins[key] = gremlin
        return combined

    def __len__(self):
        return len(self.gremlins)

    def tally(self, chemical_names: list[str], list_tags: list[str]) -> None:
        """Tally chemical names. Creates or appends gremlins in a tentative
        state.

        :param chemical_names: List of chemical names to tally
        :param list_tags: List of list_tags associated with these names
        """
        for chemical_name in chemical_names:
            key = chemical_name.lower()
            if key in self.gremlins:
                self.gremlins[key].occurrences += 1
                self.gremlins[key].list_tags.update(list_tags)
            else:
                self.gremlins[key] = Gremlin(
                    chemical_name=key, occurrences=1, list_tags=set(list_tags)
                )

    def get_gremlins(self) -> list[Gremlin]:
        """Return a list of all gremlins, ordered by their occurrences
        (highest first)."""
        gremlins_list = list(self.gremlins.values())
        gremlins_list.sort(key=lambda g: g.occurrences, reverse=True)
        return gremlins_list

    def flush(self, cutoff: int):
        """Remove gremlins with occurrences less than cutoff."""
        self.gremlins = {
            k: v for k, v in self.gremlins.items() if v.occurrences >= cutoff
        }

    def is_gremlin(self, chemical_name: str, list_tags: set[str]) -> bool:
        """Check if chemical name is flagged as a potential gremlin by this instance.
        At least one of the list_tags must match the list_tags applicable to the
        gremlin.
        """
        key = chemical_name.lower()
        if key not in self.gremlins:
            return False
        gremlin = self.gremlins[key]
        return len(list_tags.intersection(gremlin.list_tags)) > 0

    def write(self, file_path: str) -> None:
        """Write gremlins to CSV file."""
        header = ["chemical_name", "occurrences", "list_tags"]
        with open(file_path, "w", encoding="utf-8", newline="") as csv_file:
            writer = csv.writer(csv_file, delimiter=",")
            writer.writerow(header)
            for gremlin in self.get_gremlins():
                writer.writerow(
                    [
                        gremlin.chemical_name,
                        gremlin.occurrences,
                        ";".join(gremlin.list_tags),
                    ]
                )

    def __from_csv(self, file_path: str):
        """Read Gremlins data from file."""
        with open(file_path, encoding="utf-8") as csv_file:
            reader = csv.reader(csv_file)
            next(reader)  # Skip header
            for row in reader:
                chemical_name = row[0].lower()
                fields.validate("chemical_name", chemical_name)
                occurrences = int(row[1])
                list_tags = row[2].split(";")
                for list_tag in list_tags:
                    fields.validate("list_tag", list_tag)
                self.gremlins[chemical_name] = Gremlin(
                    chemical_name, occurrences, set(list_tags)
                )
