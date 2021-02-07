import os
import yaml
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