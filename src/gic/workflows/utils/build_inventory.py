import logging
import os

from ...datastructs import DataFrame, Inventory
from ..utils.finders import find_jsonl_files
from ..utils.gremlins_data import GremlinsData
from ..utils.remove_gremlins import remove_gremlins


def build_or_update_inventory(
    jsonl_dir: str,
    inventory_file: str,
    gremlins_file: str,
    logger: logging.Logger,
) -> Inventory:
    """Build or update inventory from directory of JSONL files

    :param jsonl_dir: Directory containing JSONL files
    :param inventory_file: Path to existing inventory file (create new if blank)
    :param gremlins_file: Path to CSV file containing gremlins data
        (no gremlins removal if left blank)
    :param logger: Logger instance to print status messages.
    """
    # Init Inventory
    num_substances_before = 0
    if os.path.isfile(inventory_file):
        inventory = Inventory(inventory_file)
        num_substances_before = len(inventory.get_sids())
        logger.info(
            "Updating existing inventory %s with %d substances",
            inventory_file,
            num_substances_before,
        )
    else:
        inventory = Inventory()
        num_substances_before = 0
        logger.info("Creating new inventory")

    # Init gremlins
    apply_gremlins_removal = False
    if gremlins_file:
        logger.info("Loading gremlins data from %s", gremlins_file)
        g_data = GremlinsData(gremlins_file)
        apply_gremlins_removal = True

    # Detect JSONL files to import
    jsonl_files = find_jsonl_files(jsonl_dir)
    logger.info("Importing %d JSONL files", len(jsonl_files))

    # Load JSONL files, strip gremlins and import into inventory
    for filename in jsonl_files:
        df = DataFrame.from_jsonl(filename)
        if apply_gremlins_removal:
            removed = remove_gremlins(g_data, df)
            if removed:
                logger.info("Stripped gremlin identifiers from %s", filename)
                for chemical_name in removed:
                    logger.info("  Stripped %s", chemical_name)
        inventory.import_from_data_frame(df)
        num_substances_after = len(inventory.get_sids())
        num_substances_added = num_substances_after - num_substances_before
        num_substances_before = num_substances_after
        logger.info(
            "Inventory size after importing %s: %d substances (+%d)",
            filename,
            num_substances_after,
            num_substances_added,
        )

    return inventory
