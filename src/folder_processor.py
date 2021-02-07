import os
import json
import collections.abc

from multiprocessing import Process, Lock

from file_processor import get_file_settings
from image_processor import get_image_settings
from utilities import setup_logger, read_settings, get_script_details

# GLOBAL VARIABLES
SRC_PATH = r'C:\Users\pault\Pictures\Sélection Noël 2019'

SCRIPT_HOME, SCRIPT_NAME = get_script_details(script_path=__file__)
PATH_FILE_LOG = os.path.join(SCRIPT_HOME,'var','log',SCRIPT_NAME + '.log')
PATH_FILE_SETTINGS = os.path.join(SCRIPT_HOME, 'etc', SCRIPT_NAME + '.yaml')
PATH_FILE_OUTPUT = os.path.join(SCRIPT_HOME, 'var', 'lib', 'files_inventory.json')

FILE_TYPE="image"

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
def read_inventory(source_file):
	try:
		with open(source_file, 'r') as inventory_file:
			inventory_data = json.load(inventory_file)
			
	except FileNotFoundError:
		logger.info(
			f'Inventory file at file_path="source_file" '
			f'does not exist, initializing inventory...'
		)
		inventory_data = {FILE_TYPE:{}}
	
	return inventory_data

def store_inventory(file_dict, lock):

	logger.debug(
		f'Locking output_path="{PATH_FILE_OUTPUT}" in '
		f'order to store computed result'
	)
	lock.acquire()
	
	try:
		inventory_dict = read_inventory(
			source_file=PATH_FILE_OUTPUT
		)
		update(
			inventory_dict,
			file_dict,
		)

		with open(PATH_FILE_OUTPUT, 'w', encoding='utf8') as inventory_file:
			json.dump(
				inventory_dict,
				inventory_file,
				indent=4,
				sort_keys=True,
			)

	finally:
		logger.debug(
			f'Releasing lock on output_path="{PATH_FILE_OUTPUT}" '
			f'after storing computed results'
		)
		lock.release()


def update(d, u):
    for k, v in u.items():
        if isinstance(v, collections.abc.Mapping):
            d[k] = update(d.get(k, {}), v)
        else:
            d[k] = v
    return d		
		
def run_child(function, args):

	logger.debug(
		f'Atttempting to run function_name="{function}" '
		f'with arguments="{args}"'
	)
	try:
		new_process = Process(
			target=function,
			args=args,
		)
		new_process.start()
			
	except:
		logger.error(
			f'Error: unable to start thread '
			f'for function_name="{function}"'
		)

def process_file(file_path, lock):

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
		"files": {
				file_hash: file_details
		}
	}

	store_inventory(file_dict, lock)

def process_folder(folder_path, lock):

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
				function=process_file,
				args=(item_path, lock)
			)
			
		elif os.path.isdir(item_path):
			run_child(
				function=process_folder,
				args=(item_path, lock)
			)

		else:
			logger.warn(
				f'Could not determine type of current '
				f'object at item_path="{item_path}"'
			)
	

# MAIN CODE

if __name__ == '__main__':

	lock = Lock()
	run_child(
		process_folder,
		(SRC_PATH, lock),
	)
