import os
import json

from utilities import (
	setup_logger,
	get_script_details,
	recursive_update,
)

# GLOBAL VARIABLES
SCRIPT_HOME, SCRIPT_NAME = get_script_details(script_path=__file__)
PATH_FILE_LOG = os.path.join(SCRIPT_HOME, 'var', 'log', SCRIPT_NAME + '.log')
PATH_FILE_OUTPUT = os.path.join(SCRIPT_HOME, 'var', 'lib', 'hash_inventory.json')

# DEFINING LOGGING SETTINGS
logger = setup_logger(
	name=SCRIPT_NAME,
	file_path=PATH_FILE_LOG,
)

# FUNCTIONS
def read_inventory(
		source_file:str,
):
	try:
		with open(source_file, 'r') as inventory_file:
			inventory_data = json.load(inventory_file)
			
	except FileNotFoundError:
		logger.info(
			f'Inventory file at file_path="source_file" '
			f'does not exist, initializing inventory...'
		)
		inventory_data = dict()
	
	return inventory_data

def store_inventory(
		file_dict:dict,
		lock
):

	logger.debug(
		f'Locking output_path="{PATH_FILE_OUTPUT}" in '
		f'order to store computed result'
	)
	lock.acquire()
	
	try:
		inventory_dict = read_inventory(
			source_file=PATH_FILE_OUTPUT
		)
		inventory_dict = recursive_update(
			src_item=inventory_dict,
			new_item=file_dict,
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