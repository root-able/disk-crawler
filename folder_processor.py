import os
import json
import logging
import collections.abc

from hashlib import sha256 as hash_algo
from multiprocessing import Process, Lock

from image_processing import get_image_settings

# GLOBAL VARIABLES
TARGET_FOLDER_PATH = r'C:\Users\pault\Pictures\Sélection Noël 2019'
INVENTORY_FILE_PATH = r'C:\Users\pault\Documents\01 - Informatique\08 - Dev Zone\disk_crawler\image_inventory.json'
LOG_FILE_PATH = r'C:\Users\pault\Documents\01 - Informatique\08 - Dev Zone\disk_crawler\folder_processor.log'
FILE_TYPE = 'images'

# DEFINING LOGGING SETTINGS
LOG_FORMAT = '%(asctime)-15s - %(filename)s - %(levelname)s - %(message)s'
logging.basicConfig(
	filename=LOG_FILE_PATH,
	format=LOG_FORMAT,
	encoding='utf-8',
	level=logging.DEBUG,
)
logger = logging.getLogger()

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
		f'Locking output_path="{INVENTORY_FILE_PATH}" in '
		f'order to store computed result'
	)
	lock.acquire()
	
	try:
		inventory_dict = read_inventory(
			source_file=INVENTORY_FILE_PATH
		)
		update(
			inventory_dict,
			file_dict,
		)

		with open(INVENTORY_FILE_PATH, 'w') as inventory_file:
			json.dump(inventory_dict, inventory_file)
		
	finally:
		logger.debug(
			f'Releasing lock on output_path="{INVENTORY_FILE_PATH}" '
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

	file_hash = None
	
	with open(file_path,"rb") as file_descriptor:
		file_data = file_descriptor.read()
		file_hash = hash_algo(file_data).hexdigest()
	
	logger.info(
		f'Processed file_path="{file_path}" with '
		f'result file_hash={file_hash}"'
	)

	file_details = get_image_settings(file_path)
	file_details.update({
		"bytes": os.path.getsize(file_path)
	})

	file_dict = {
		FILE_TYPE:{
			file_hash:{
				file_path: file_details
			}
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
		(TARGET_FOLDER_PATH, lock),
	)
