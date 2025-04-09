__author__    = "Ioana Circu"
__contact__   = "ioana.circu@stfc.ac.uk"
__copyright__ = "Copyright 2025 United Kingdom Research and Innovation"


import logging
import os

def setup_logging(enable_logging=True, console_logging=True) -> None:
    """
    Sets up logging configuration. If `enable_logging` is False, no logging will occur.
    
    :param enable_logging: Flag to enable/disable logging.
    """

    log_file = ""

    try:

        file = os.environ.get("CONFIG_FILE", None) or "dirconfig"

        with open(file) as f: # 'r' is default if not specified.
            content = [r.strip() for r in f.readlines()] # Removes the '\n' from all lines

        log_file = content[5].replace('\n','')

    except FileNotFoundError:
        print("Error: Config file not found.")
    
        return

    if log_file == '':
        print("Error: Please fill in the third directory in dirconfig file")

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


enable_logging = True

# Set up logging with a flag (True to enable logging, False to disable logging)
setup_logging(enable_logging)  # Change to False to disable logging

logger = logging.getLogger(__name__)

