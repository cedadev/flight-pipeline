__author__ = "Ioana Circu"
__contact__ = "ioana.circu@stfc.ac.uk"
__copyright__ = "Copyright 2025 United Kingdom Research and Innovation"


import click
import sys

from ceda_flight_pipeline.logger import logger
import logging
import os
from ceda_flight_pipeline.flight_client import ESFlightClient

IS_FORCE = True
VERB = True


# Helper function for converting string to boolean
def str2bool(v):
    """
    Input parameter: Str
    Returns: Bool based on whether the string is part of list
    """
    return v.lower() in ("y", "yes", "true", "t", "1")


def openConfig():
    """
    Function to open configuration file and initialise paths to relevant directories.

    Returns:
        1. Path to flights to be pushed to ElasticSearch
        2. Path to directory for moving written flights
        3. Path to logging file
    """

    if VERB:
        # print('> (1/6) Opening Config File')
        logger.info("> (1/6) Opening Config File")

    f = open(os.environ.get("CONFIG_FILE"), "r")
    content = f.readlines()
    f.close()
    try:
        return content[1].replace("\n", ""), content[3].replace("\n", "")
    except IndexError:
        logger.error("One or both paths missing from the dirconfig file")
        print(
            "Error: One or both paths missing from the dirconfig file - please fill these in"
        )
        return "", ""


def moveOldFiles(rootdir, archive, files):
    """
    Move the written files from the root directory given in the config file to the archive

    If keyword DELETE given instead of archive then the flight records will be deleted after being pushed
    """

    # Move the written files from rootdir to the archive
    if archive != "DELETE":
        for file in files:
            path = os.path.join(rootdir, file.split("/")[-1])
            new_path = os.path.join(archive, file.split("/")[-1])
            os.system("mv {} {}".format(path, new_path))
    else:
        for file in files:
            path = os.path.join(rootdir, file.split("/")[-1])
            os.system("rm {}".format(path))


def addFlights(rootdir, archive, repush=False):
    """
    Initialising connection with ElasticSearch Flight Client and pushing flights to new location.

    Calling moveOldFiles() to delete flight records before exiting.
    """

    checked_list = []

    # ES client to determine array of ids
    if VERB:
        # print('> (2/6) Setting up ES Flight Client')
        logger.info("> (2/6) Setting up ES Flight Client")
    if repush:
        files_list = os.listdir(archive)
        fclient = ESFlightClient(archive, os.environ.get("SETTINGS_FILE", None))
    else:
        files_list = os.listdir(rootdir)
        fclient = ESFlightClient(rootdir, os.environ.get("SETTINGS_FILE", None))

    # All flights ok to repush - handled by new client.
    checked_list = list(files_list)

    # Push new flights to index
    if VERB:
        # print('> (4/6) Identified {} flights'.format(len(checked_list)))
        logger.info("> (4/6) Identified {} flights".format(len(checked_list)))
    if len(checked_list) > 0:
        fclient.push_flights(checked_list)
        if VERB:
            # print('> (5/6) Pushed flights to ES Index')
            logger.info("> (5/6) Pushed flights to ES Index")
        if not repush:
            moveOldFiles(rootdir, archive, checked_list)
        if VERB:
            # print('> (6/6) Removed local files from push directory')
            logger.info("> (6/6) Removed local files from push directory")
    else:
        if VERB:
            # print('> Exiting flight pipeline')
            logger.info("> Exiting flight pipeline")

    # Move old records into an archive directory


def updateFlights(update):
    """
    Update flights using resolve_link() from flightpipe/flight_client module.
    """
    from ceda_flight_pipeline import updaters

    fclient = ESFlightClient("", os.environ.get("SETTINGS_FILE", None))
    updaters[update](fclient)


def reindex(new_index):
    """
    Running a re-index using the source and destination from settings_file.
    """
    fclient = ESFlightClient("", os.environ.get("SETTINGS_FILE", None))
    fclient.reindex(new_index)

try:
    root, archive = openConfig()
except: # in case no env variable is set for the config file
    root = ""
    archive = ""


@click.group()
def main():
    """Command Line Interface for flight update"""
    pass


@main.command()
@click.option(
    "--archive_path",
    default=archive,
    required=True,
    help="Set archive path",
    prompt="Set archive path",
)
@click.option(
    "--flights_dir",
    default=root,
    required=True,
    help="Set path where flights will be pushed",
    prompt="Set path to flights to be pushed",
)
@click.option(
    "--add_mode",
    default="y",
    type=str,
    help="Set mode to just flights",
    prompt="Set mode to add flights (y/n)",
)
@click.option(
    "--update_mode",
    default="n",
    type=str,
    help="Name of script in updates/ to use",
    prompt="Name of script to update",
)
@click.option(
    "--update_id",
    default="n",
    type=str,
    help="New elasticsearch index to move to",
    prompt="Flight id to update",
)
# @click.option(
#     "--config_file",
#     default="n",
#     type=str,
#     help="Path to config file",
# )
# @click.option(
#     "--settings_file",
#     default="n",
#     type=str,
#     help="Path to settings file",
# )
# @click.option(
#     "--stac_template",
#     default="n",
#     type=str,
#     help="Path to STAC template",
# )

def flight_update(archive_path, flights_dir, add_mode, update_mode, update_id): #,config_file, settings_file, stac_template):
    """
    Main function running the flight update scripts based on the given command line parameters
    """
    IS_FORCE = False
    REPUSH = False


    # if config_file:
    #     os.environ["CONFIG_FILE"] = config_file

    # if settings_file:
    #     os.environ["SETTINGS_FILE"] = settings_file
    
    # if stac_template:
    #     os.environ["STAC_TEMPLATE"] = stac_template


    # Convert add_mode and update_mode from strings to booleans
    add_mode = str2bool(add_mode)
    update_mode = str2bool(update_mode)

    if add_mode:
        # Ensure archive_path and flights_dir are not empty
        if not archive_path:
            print("Error: Please provide an archive path.")
            sys.exit(1)
        elif not flights_dir:
            print("Error: Please provide a directory for flights.")
            sys.exit(1)
        else:
            addFlights(flights_dir, archive_path, repush=REPUSH)

    elif update_mode:
        updateFlights(update_mode)

    elif update_id:
        reindex(update_id)

    else:
        print("Error: Mode unrecognized. Please choose either add or update.")
        sys.exit(1)


if __name__ == "__main__":
    main()
