import yaml
import logging

LOG_LEVEL = logging.DEBUG
LOG_FORMATTER = logging.Formatter(
    '%(asctime)-15s - %(filename)s - %(levelname)s - %(message)s'
)

def setup_logger(name, log_file, level=LOG_LEVEL):
    """To setup as many loggers as you want"""

    handler = logging.FileHandler(log_file)
    handler.setFormatter(LOG_FORMATTER)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger

def get_settings(
        settings_file: str,
        parent_name: str,
        settings_type: str,
        logger_object,
):
    """
    Get settings from YAML configuration file
    """
    settings_dict = dict()


    logger_object.info(
        f'Loading settings for '
        f'key_type="{settings_type}" '
        f'from file_path="{settings_file}"'
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

    settings_data = settings_dict.get(
        parent_name,
        dict(),
    ).get(settings_type)

    return settings_data