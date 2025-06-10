__author__    = "Ioana Circu"
__contact__   = "ioana.circu@stfc.ac.uk"
__copyright__ = "Copyright 2025 United Kingdom Research and Innovation"


import logging
import os

logger = logging.getLogger(__name__)
from ceda_flight_pipeline.utils import logstream, formatter
logger.addHandler(logstream)
logger.propagate = False

levels = [
    logging.WARN,
    logging.INFO,
    logging.DEBUG,
]


def setup_logging(
        verbose: int = 0, 
        console_logging: bool = True, 
        log_file: str = "") -> None:
    """
    Sets up logging configuration. If `enable_logging` is False, no logging will occur.
    
    :param enable_logging: Flag to enable/disable logging.
    """

    fh = None

    if log_file != '':
        fh = logging.FileHandler(log_file),  # Write output to file
        fh.setLevel(levels[verbose])
        fh.setFormatter(formatter)

    for name in logging.root.manager.loggerDict:
        lg = logging.getLogger(name)
        lg.setLevel(levels[verbose])
        if fh is not None:
            lg.addHandler(fh)


def get_config(cfg_file) -> tuple:
    """
    Function to get logging info from config file
    """

    try:
        with open(cfg_file) as f: # 'r' is default if not specified.
            content = [r.strip() for r in f.readlines() if not r.startswith('#')] # Removes the '\n' from all lines
    
    except FileNotFoundError:
        logger.debug("Config file not found.")
        return None, None, None, None, None, None
    
    new_flights = content[0]
    archive     = content[1]
    logfile     = content[2]

    values = {i.split('=')[0] : i.split('=')[1] for i in content[3:]}

    verbose = values.get('verbose',None)
    console_logging = values.get('console_logger',None)
    stac_index = values.get('index',None)

    return new_flights, archive, logfile, verbose, console_logging, stac_index


def setup_from_config(
        new_flights: str = None, 
        archive: str = None, 
        logfile: str = None, 
        verbose: int = None, 
        console_logging: bool = None, 
        stac_index: str = None,
        cfg_file: str = 'dirconfig'):

    new_flights_d, archive_d, logfile_d, verbose_d, console_logging_d, stac_index_d = get_config(cfg_file)

    # Apply defaults from config
    new_flights = new_flights or new_flights_d
    archive = archive or archive_d
    logfile = logfile or logfile_d
    verbose = verbose or verbose_d
    console_logging = console_logging or console_logging_d
    stac_index = stac_index or stac_index_d

    try:

        # Set up logging with a flag (True to enable logging, False to disable logging)
        setup_logging(verbose, console_logging, logfile)  # Change to False to disable logging
    except:
        # Set up logging with default parameters
        setup_logging()

    return new_flights, archive, stac_index

