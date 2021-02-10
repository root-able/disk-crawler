import os
import hashlib

from image_processor import get_image_settings
from inventory_processor import (
	store_inventory,
)
from utilities import (
    setup_logger,
    get_script_details,
    read_settings,
)

# GLOBAL VARIABLES

SCRIPT_HOME, SCRIPT_NAME = get_script_details(script_path=__file__)
PATH_FILE_LOG = os.path.join(SCRIPT_HOME,'var','log',SCRIPT_NAME + '.log')
PATH_FILE_SETTINGS = os.path.join(SCRIPT_HOME, 'etc', SCRIPT_NAME + '.yaml')

# DEFINING LOGGING SETTINGS
logger = setup_logger(
	name=SCRIPT_NAME,
	file_path=PATH_FILE_LOG,
)

file_settings = read_settings(
	settings_file=PATH_FILE_SETTINGS,
	logger_object=logger,
)

# FUNCTIONS
def get_file_settings(
    file_path: str,
):
    """
    Process an input file based only on OS settings
    """

    file_name, file_ext = os.path.splitext(file_path)
    file_name_clean = os.path.basename(file_name)
    file_ext_clean = file_ext.replace('.', '')


    with open(file_path, "rb") as file_descriptor:
        file_data = file_descriptor.read()
        hash_dict = dict()

        for name, state in file_settings["hash_algorithms"].items():
            if state == "enabled":
                hash_method = getattr(hashlib, name)
                file_hash = hash_method(file_data).hexdigest()
                hash_dict[name] = file_hash

    first_hash = next(
        iter(
            hash_dict.values()
        )
    )

    file_object = {
        "file": {
            "bytes": os.path.getsize(file_path),
            "type" : "unknown",
            "path" : file_path,
            "name" : file_name_clean.lower(),
            "extension" : file_ext_clean.lower(),
        },
        "hash": hash_dict,
    }

    return first_hash, file_object

def process_file(
        folder_settings:dict,
        file_path:str,
        lock
):
        file_type = "unknown"
        file_hash, file_details = get_file_settings(file_path)

        logger.info(
            f'Processing file_path="{file_path}" with '
            f'file_hash={file_hash}" and '
            f'file_ext="{file_details["file"]["extension"]}"'
        )

        for file_ext_type, file_ext_list in folder_settings["file_extensions"].items():
            if file_details["file"]["extension"] in file_ext_list:

                file_type = file_ext_type
                file_details["file"]["type"] = file_type
                logger.info(f'Found matching known file_type="{file_type}"')

                if file_details["file"]["type"] == "image":
                    file_details.update(
                        get_image_settings(file_path)
                    )

        file_dict = {
            "hashes": {
                file_hash: file_details
            }
        }

        store_inventory(file_dict, lock)