import os

from file_processor import process_file
from utilities import (
	setup_logger,
	read_settings,
	get_script_details,
	run_child,
)

# GLOBAL VARIABLES
SCRIPT_HOME, SCRIPT_NAME = get_script_details(script_path=__file__)
PATH_FILE_LOG = os.path.join(SCRIPT_HOME, 'var', 'log', SCRIPT_NAME + '.log')
PATH_FILE_SETTINGS = os.path.join(SCRIPT_HOME, 'etc', SCRIPT_NAME + '.yaml')

# DEFINING LOGGING SETTINGS
logger = setup_logger(
	name=SCRIPT_NAME,
	file_path=PATH_FILE_LOG,
)

folder_settings = read_settings(
	settings_file=PATH_FILE_SETTINGS,
	logger_object=logger,
)

# FUNCTIONS
def process_folder(pool, folder_path, lock):

	logger.info(
		f'Currently processing folder '
		f'at folder_path="{folder_path}"'
	)

	for item in os.listdir(folder_path):
		item_path = os.path.join(
			folder_path,
			item,
		)

		if os.path.isfile(item_path):
			run_child(
				pool=pool,
				function=process_file,
				args=(
					folder_settings,
					item_path,
					lock,
				)
			)
			
		elif os.path.isdir(item_path):
			run_child(
				pool=pool,
				function=process_folder,
				args=(item_path, lock)
			)

		else:
			logger.warn(
				f'Could not determine type of current '
				f'object at item_path="{item_path}"'
			)