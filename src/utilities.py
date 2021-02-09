import os
import copy
import yaml
import typing
import pathlib
import logging

from datetime import datetime

# GLOBAL VARIABLES
DATE_FORMAT = "%Y-%m-%d - %H:%M:%S"

LOG_LEVEL = logging.DEBUG
LOG_FORMATTER = logging.Formatter(
    '%(asctime)-15s - %(filename)s - %(levelname)s - %(message)s'
)

# FUNCTIONS
def get_formatted_date(
    timestamp: float,
):
    """
    Get a date following input format
    from raw timestamp with decimals
    """

    datetime_object = datetime.fromtimestamp(
        int(
            timestamp
        )
    )

    formatted_date = datetime_object.strftime(
        DATE_FORMAT
    )

    return formatted_date

def get_script_details(
        script_path:str,
):
    """Get settings on current script"""
    script_name, script_ext = os.path.splitext(
        os.path.basename(
            script_path
        )
    )

    script_home = pathlib.Path(script_path).parent.parent.absolute()

    return script_home, script_name

def setup_logger(
        name:str,
        file_path:str,
        level=LOG_LEVEL,
):
    """To setup as many loggers as you want"""

    handler = logging.FileHandler(file_path)
    handler.setFormatter(LOG_FORMATTER)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger

def read_settings(
        settings_file: str,
        logger_object,
):
    """
    Get settings from YAML configuration file
    """
    settings_dict = dict()


    logger_object.info(
        f'Loading settings from file_path="{settings_file}"'
    )

    with open(settings_file, 'r') as file_stream:

        try:
            settings_dict = yaml.safe_load(
                file_stream
            )

        except yaml.YAMLError as exception:

            logger_object.exception(
                exception
            )

    return settings_dict

def merge_list(
        src_list:list,
        new_list:list,
) -> list:
    """
    Merge two lists with duplicate checking
    """
    output = list(
        dict.fromkeys(
            src_list + new_list
        )
    )

    if len(output) == 1:
        output = output[0]

    return output

def merge_dict(
        src_dict:dict,
        new_dict:dict,
) -> dict:
    """
    Merge two dict without overriding existing values
    """
    output = copy.deepcopy(src_dict)

    for key, value in new_dict.items():
        if key in output.keys():
            output[key] = recursive_update(
                src_item=output.get(key),
                new_item=value,
            )
        else:
            output[key] = value

    return output

def recursive_update(
        src_item:typing.Any,
        new_item:typing.Any,
) -> typing.Any:
    """
    Recursively update various file types
    """
    if new_item is None:
        return src_item

    output = None
    src_type = src_item.__class__.__name__
    new_type = new_item.__class__.__name__

    if src_type == new_type:
        if src_type == "list":
            output = merge_list(src_item,new_item)
        elif src_type == "dict":
            output = merge_dict(src_item,new_item)
        else:
            output = merge_list([src_item],[new_item])

    else:
        if src_type == "list":
            output = merge_list(src_item,[new_item])
        elif new_type == "list":
            output = merge_list(new_item,[src_item])
        else:
            exit -1

    return output