import os
from PIL import Image
from PIL.ExifTags import TAGS
from datetime import datetime

from file_processor import get_creation_date
from utilities import setup_logger, read_settings, get_script_details

# GLOBAL VARIABLES
DATE_FORMAT = "%Y-%m-%d - %H:%M:%S"
EXIF_EXTRA_FIELDS = ["Make", "Model", "Artist"]

SCRIPT_HOME, SCRIPT_NAME = get_script_details(script_path=__file__)
PATH_FILE_LOG = os.path.join(SCRIPT_HOME,'var','log',SCRIPT_NAME + '.log')
PATH_FILE_SETTINGS = os.path.join(SCRIPT_HOME, 'etc', SCRIPT_NAME + '.yaml')
PATH_FILE_OUTPUT = os.path.join(SCRIPT_HOME, 'var', 'lib', SCRIPT_NAME + '.json')

# DEFINING LOGGING SETTINGS
logger = setup_logger(
	name=SCRIPT_NAME,
	file_path=PATH_FILE_LOG,
)

image_settings = read_settings(
	settings_file=PATH_FILE_SETTINGS,
	logger_object=logger,
)


# FUNCTIONS
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
    exif_date_timestamp = 0

    for field_settings in exif_settings:

        for current_field, current_confidence in field_settings.items():

            if current_field in exif_data:

                date_field = current_field
                date_confidence = current_confidence
                exif_date = exif_data.get(
                    current_field
                )

                exif_date_timestamp = datetime.timestamp(
                    datetime.strptime(
                        exif_date,
                        "%Y:%m:%d %H:%M:%S"
                    )
                )
                logger.info(
                    f'Found EXIF date_field="{date_field}" '
                    f'with date_confidence="{date_confidence}", '
                    f'collecting date_timestamp="{exif_date_timestamp}"'
                )

                return (
                    date_field,
                    date_confidence,
                    exif_date_timestamp,
                )

    return (
        date_field,
        date_confidence,
        exif_date_timestamp,
    )


def get_image_quality(
    file_path:str,
):
    image_object = Image.open(file_path)
    quality_dict = {
        "quality": {
            "resolution":
                {
                    "width": image_object.width,
                    "height": image_object.height,
                },
            "format": image_object.format.lower(),
            "mode": image_object.mode.lower(),
        }
    }
    return quality_dict

def get_image_settings(
    file_path: str,
):
    """
    Process an input image file to get settings

    TODO: CLEANUP by reducing number of lines in this method (sub-methods?)
    """
    image_info = dict()

    exif_settings = image_settings["date_confidence"]["exif"]

    logger.info(
        f'Processing file_path="{file_path}"'
    )

    exif_data = get_labeled_exif(
        file_path=file_path,
    )

    (
        date_field,
        date_confidence,
        date_timestamp,
    ) = get_exif_date(
        exif_settings=exif_settings,
        exif_data=exif_data,
    )

    if (
        date_field is None
        or date_confidence is None
        or date_timestamp == 0
    ):
        file_settings = image_settings["date_confidence"]["file"]

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

    date_human = datetime.strftime(
        datetime.fromtimestamp(
            date_timestamp,
        ),
        DATE_FORMAT,
    )

    image_info.update({
        "date":{
            "date_type":date_type,
            "date_field":date_field,
            "date_confidence":date_confidence,
            "date_timestamp":date_timestamp,
            "date_human":date_human,
        }
    })

    image_info.update(
        get_image_quality(
            file_path
        )
    )

    return image_info