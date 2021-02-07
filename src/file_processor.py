import os
import hashlib
import platform

from utilities import setup_logger, get_script_details, read_settings, get_formatted_date

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
def get_creation_date(
    file_path: str,
    file_settings: dict,
):
    """
    Attempt to get the creation date according
    to current Operating System
    """
    date_field = None
    date_confidence = None
    creation_date = float(0)
    operating_system = str()

    if platform.system() == 'Windows':

        operating_system = 'Windows'
        date_field = 'ctime'
        creation_date = os.path.getctime(
            file_path
        )

    else:

        file_stats = os.stat(
            file_path
        )

        if st_birthtime in file_stats:

            creation_date = file_stats.st_birthtime
            operating_system = 'Mac OS'
            date_field = 'birthtime'

        else:

            creation_date = file_stats.st_birthtime
            operating_system = 'Linux'
            date_field = 'mtime'

    creation_date_formatted = get_formatted_date(
        creation_date,
    )

    for field_settings in file_settings:

        date_confidence = field_settings.get(
            date_field,
            date_confidence,
        )

    logger.info(
        f'Detected operating_system="{operating_system}", '
        f'using date_field="{date_field}", '
        f'with date_confidence="{date_confidence}", '
        f'collecting date_value="{creation_date_formatted}"'
    )

    return (
        date_field,
        date_confidence,
        creation_date_formatted,
    )

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