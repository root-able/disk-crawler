import os
import yaml
import logging
import pathlib
import platform

from PIL import Image
from PIL.ExifTags import TAGS
from datetime import datetime

from utilities import setup_logger, get_settings

# GLOBAL VARIABLES
DATE_FORMAT = "%Y-%m-%d - %H:%M:%S"
DEFAULT_EPOCH_TIME = datetime.fromtimestamp(
        0
    ).strftime(
        DATE_FORMAT
    )

EXIF_EXTRA_FIELDS = ["Make", "Model", "Artist"]

HOME_PATH = pathlib.Path(__file__).parent.parent.absolute()
SETTINGS_FILE_NAME = os.path.join(HOME_PATH, r'etc\image_processor.yaml')
LOG_FILE_PATH = os.path.join(HOME_PATH, r'var\log\image_processor.log')
FILE_TYPE = 'images'

# DEFINING LOGGING SETTINGS
logger = setup_logger(
	name=__name__,
	log_file=LOG_FILE_PATH,
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


def get_labeled_exif(
    file_path: str,
):
    """
    Collect EXIF data from an image file
    with matching labels
    """

    exif_data_labeled = {}
    file_name, file_ext = os.path.splitext(file_path)

    if file_ext.lower() == ".png":
        return exif_data_labeled

    else:

        image = Image.open(file_path)
        image.verify()
        exif_data_raw = image.getexif()

        if exif_data_raw is not None:

            for (key, val) in exif_data_raw.items():
                exif_data_labeled[TAGS.get(key)] = val

        return exif_data_labeled


def get_exif_date(
    exif_settings: dict,
    exif_data: dict,
):
    """
    Get a date from EXIF data input
    """
    date_field = None
    date_confidence = None
    exif_date_formatted = DEFAULT_EPOCH_TIME

    for field_settings in exif_settings:

        for current_field, current_confidence in field_settings.items():

            if current_field in exif_data:

                date_field = current_field
                date_confidence = current_confidence
                exif_date = exif_data.get(
                    current_field
                )

                exif_date_formatted = datetime.strptime(
                    exif_date,
                    "%Y:%m:%d %H:%M:%S"
                ).strftime(
                    DATE_FORMAT
                )

                logger.info(
                    f'Found EXIF date_field="{date_field}" '
                    f'with date_confidence="{date_confidence}", '
                    f'collecting date_value="{exif_date_formatted}"'
                )

                return (
                    date_field,
                    date_confidence,
                    exif_date_formatted,
                )

    return (
        date_field,
        date_confidence,
        exif_date_formatted,
    )


def get_image_settings(
    file_path: str,
):
    """
    Process an input image file to get settings
    """
    image_info = dict()

    exif_settings = get_settings(
        settings_file=SETTINGS_FILE_NAME,
        parent_name="date_confidence",
        settings_type="exif",
        logger_object=logger,
    )

    logger.info(
        f'Processing file_path="{file_path}"'
    )

    exif_data = get_labeled_exif(
        file_path=file_path,
    )

    (
        date_field,
        date_confidence,
        date_value,
    ) = get_exif_date(
        exif_settings=exif_settings,
        exif_data=exif_data,
    )

    if (
        date_field is None
        or date_confidence is None
        or date_value == 0
    ):
        file_settings = get_settings(
            settings_file=SETTINGS_FILE_NAME,
            parent_name="date_confidence",
            settings_type="file",
            logger_object=logger,
        )

        date_type = "CREATION"

        (
            date_field,
            date_confidence,
            date_value,
        ) = get_creation_date(
            file_path=file_path,
            file_settings=file_settings,
        )

    else:
        date_type = "EXIF"

        exif_extras = dict()
        for field_name in EXIF_EXTRA_FIELDS:
            exif_extras.update({
                field_name : exif_data.get(field_name)
            })

        image_info.update({"device":exif_extras})


    image_info.update({
        "date":{
            "date_type":date_type,
            "date_field":date_field,
            "date_confidence":date_confidence,
            "date_value":date_value,
        }
    })

    return image_info