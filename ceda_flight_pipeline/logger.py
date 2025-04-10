__author__    = "Ioana Circu"
__contact__   = "ioana.circu@stfc.ac.uk"
__copyright__ = "Copyright 2025 United Kingdom Research and Innovation"


import logging
import os


def setup_logging(enable_logging=True, console_logging=True, log_file = "") -> None:
    """
    Sets up logging configuration. If `enable_logging` is False, no logging will occur.
    
    :param enable_logging: Flag to enable/disable logging.
    """


    if log_file == '':
        print("Error: Please fill in the third directory in dirconfig file")
        return

    handlers = [
            logging.FileHandler(log_file),  # Write output to file
        ]

    if console_logging:
        handlers.append(logging.StreamHandler())   # Logs to the console if enabled


    if enable_logging:
        logging.basicConfig(
            level=logging.DEBUG, # Capture all levels
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=handlers
        )
    else:
        # Disable logging by setting a null handler
        logging.basicConfig(level=logging.CRITICAL)
        #NOTSET for no alerts at all


def get_config():
    """
    Function to get logging info from config file
    """

    file = os.environ.get("CONFIG_FILE", None) or "dirconfig"

    try:

        with open(file) as f: # 'r' is default if not specified.
            content = [r.strip() for r in f.readlines()] # Removes the '\n' from all lines
    
    except FileNotFoundError:
        print("Error: Config file not found.")
    
        return


    return content[5].replace('\n',''), content[7].replace('\n',''), content[9].replace('\n','')


config_info = get_config()
try:
    log_file, enable_logging, console_logging = config_info[0], config_info[1], config_info[2]

    # Set up logging with a flag (True to enable logging, False to disable logging)
    setup_logging(enable_logging, console_logging, log_file)  # Change to False to disable logging
except:
    # Set up logging with default parameters
    setup_logging()

logger = logging.getLogger(__name__)

