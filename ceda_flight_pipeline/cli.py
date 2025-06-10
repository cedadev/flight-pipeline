__author__ = "Ioana Circu"
__contact__ = "ioana.circu@stfc.ac.uk"
__copyright__ = "Copyright 2025 United Kingdom Research and Innovation"


import click
import sys

from ceda_flight_pipeline.logger import setup_from_config
import logging
import os
import glob
from ceda_flight_pipeline.flight_client import ESFlightClient

logger = logging.getLogger(__name__)
from ceda_flight_pipeline.utils import logstream
logger.addHandler(logstream)
logger.propagate = False

IS_FORCE = True
VERB = True

# Helper function for converting string to boolean
def str2bool(v):
    """
    Input parameter: Str
    Returns: Bool based on whether the string is part of list
    """
    return v.lower() in ("y", "yes", "true", "t", "1")

@click.group()
def main():
    """Command Line Interface for flight update"""
    pass


@main.command()
@click.option(
    "--archive_path",
    default=None,
    help="Set path for archiving pushed flights",
)

@click.option(
    "--new_flights_dir",
    default=None,
    required=False,
    help="Set path to new set of flights",
)

@click.option(
    "--update",
    default=None,
    type=str,
    help="Name of script in updates/ to use",
)

@click.option(
    "--reindex",
    default=None,
    type=str,
    help="New elasticsearch index to move to",
)

@click.option(
    "--config_file",
    default=None,
    type=str,
    help="Path to config file",
)

@click.option(
    "--settings_file",
    default=None,
    type=str,
    help="Path to settings file",
)

@click.option(
    "--stac_template",
    default=None,
    type=str,
    help="Path to STAC template",
)

@click.option(
    "--verbose",
    "-v",
    default=0,
    count=True,
    type=int,
    help="Verbosity",
)

@click.option(
    "--console_log",
    default=True,
    type=bool,
    help="Log to console",
)

@click.option(
    "--stac_index",
    default=None,
    type=str,
    help="Main STAC index to reference",
)

@click.option(
    "--keep_files",
    is_flag=True,
    default=False,
    help="Move files after pushing",
)

def flight_update(
        archive_path, 
        new_flights_dir, 
        update, 
        reindex,
        config_file, 
        settings_file, 
        stac_template,
        verbose,
        console_log,
        stac_index,
        keep_files):
    """
    Main function running the flight update scripts based on the given command line parameters
    """

    move_files = not keep_files

    REPUSH = False
    add = True

    if update is not None or reindex is not None:
        add = False

    if not config_file:
        config_file = os.environ.get("FLIGHT_CONFIG")

    if not settings_file:
        settings_file = os.environ.get("FLIGHT_CONNECTION")
    
    if not stac_template:
        stac_template = os.environ.get("STAC_TEMPLATE")

    new_flights_dir, archive_path, stac_index = setup_from_config(
        new_flights=new_flights_dir,
        archive=archive_path,
        verbose=verbose,
        console_logging=console_log,
        stac_index=stac_index,
        cfg_file=config_file)
    
    fclient = ESFlightClient(stac_index, settings_file, stac_template=stac_template)

    if add:
        # Ensure archive_path and new_flights_dir are not empty
        if not archive_path:
            print("Error: Please provide an archive path.")
            sys.exit(1)
        elif not new_flights_dir:
            print("Error: Please provide a directory for flights.")
            sys.exit(1)
        else:
            fclient.addFlights(
                archive_path,
                new_flights_dir, 
                repush=REPUSH,
                move_files=move_files)

    elif update is not None:
        fclient.updateFlights(update)

    elif reindex is not None:
        fclient.reindex(reindex)

    else:
        print("Error: Mode unrecognized. Please choose either add or update.")
        sys.exit(1)


if __name__ == "__main__":
    main()
