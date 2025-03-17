import logging

def setup_logging(enable_logging=True, console_logging=True):
    """
    Sets up logging configuration. If `enable_logging` is False, no logging will occur.
    
    :param enable_logging: Flag to enable/disable logging.
    """

    f = open('dirconfig','r')
    content = f.readlines()
    f.close()

    log_file = content[5].replace('\n','')

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
    