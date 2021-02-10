import os
import multiprocessing

from folder_processor import process_folder
from utilities import (
	setup_logger,
	get_script_details,
	run_child,
)


# GLOBAL VARIABLES
SRC_PATH = r'C:\Users\pault\Pictures\Sélection Noël 2019'
CPU_FREE = 2

SCRIPT_HOME, SCRIPT_NAME = get_script_details(script_path=__file__)
PATH_FILE_LOG = os.path.join(SCRIPT_HOME, 'var', 'log', SCRIPT_NAME + '.log')

# DEFINING LOGGING SETTINGS
logger = setup_logger(
	name=SCRIPT_NAME,
	file_path=PATH_FILE_LOG,
)

# MAIN CODE
if __name__ == '__main__':

	logger = setup_logger(
		name=SCRIPT_NAME,
		file_path=PATH_FILE_LOG,
	)

	cpu_total = multiprocessing.cpu_count()
	cpu_used = max(cpu_total - CPU_FREE, 1)
	logger.info(
		f'Current host advertises cpu_total="{cpu_total}", '
		f'processing will use cpu_used="{cpu_used}, '
		f'which should leave cpu_free="{CPU_FREE} for OS'
	)

	lock = multiprocessing.Lock()
	pool = multiprocessing.Pool(
		processes=cpu_used,
	)

	run_child(
		pool=pool,
		function=process_folder,
		args=(pool, SRC_PATH, lock),
		logger_object=logger,
	)
