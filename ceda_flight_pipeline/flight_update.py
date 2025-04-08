'''
 --- Update Flight records ---
  - Mechanism for uploading new flight records
  - Use ES Client to determine array of ids that currently exists in the index
  - Push new records
'''
from ceda_flight_pipeline.flight_client import ESFlightClient
import importlib

import logging
from ceda_flight_pipeline.logger import logger

import argparse

import os, sys

IS_FORCE = True
VERB = True

settings_file = 'settings.json'

def openConfig():
    """
    Function to open configuration file and initialise paths to relevant directories.
    
    Returns: 
        1. Path to flights to be pushed to ElasticSearch
        2. Path to directory for moving written flights
        3. Path to logging file
    """

    if VERB:
        print('> (1/6) Opening Config File')
        logger.info('> (1/6) Opening Config File')

    f = open('../dirconfig','r')
    content = f.readlines()
    f.close()
    try:
        return content[1].replace('\n',''), content[3].replace('\n','')
    except IndexError:
        logger.error('One or both paths missing from the dirconfig file')
        print('Error: One or both paths missing from the dirconfig file - please fill these in')
        return '',''

def moveOldFiles(rootdir, archive, files):
    """
    Move the written files from the root directory given in the config file to the archive

    If keyword DELETE given instead of archive then the flight records will be deleted after being pushed
    """

    # Move the written files from rootdir to the archive
    if archive != 'DELETE':
        for file in files:
            path = os.path.join(rootdir, file.split('/')[-1])
            new_path = os.path.join(archive, file.split('/')[-1])
            os.system('mv {} {}'.format(path, new_path))
    else:
        for file in files:
            path = os.path.join(rootdir, file.split('/')[-1])
            os.system('rm {}'.format(path))


def addFlights(rootdir, archive, repush=False):
    """
    Initialising connection with ElasticSearch Flight Client and pushing flights to new location.

    Calling moveOldFiles() to delete flight records before exiting.
    """

    checked_list = []

    # ES client to determine array of ids
    if VERB:
        print('> (2/6) Setting up ES Flight Client')
        logger.info('> (2/6) Setting up ES Flight Client')
    if repush:
        files_list = os.listdir(archive)
        fclient = ESFlightClient(archive, settings_file)
    else:
        files_list = os.listdir(rootdir)
        fclient = ESFlightClient(rootdir, settings_file)

    # All flights ok to repush - handled by new client.
    checked_list = list(files_list)

    # Push new flights to index
    if VERB:
        print('> (4/6) Identified {} flights'.format(len(checked_list)))
        logger.info('> (4/6) Identified {} flights'.format(len(checked_list)))
    if len(checked_list) > 0:
        fclient.push_flights(checked_list)
        if VERB:
            print('> (5/6) Pushed flights to ES Index')
            logger.info('> (5/6) Pushed flights to ES Index')
        if not repush:
            moveOldFiles(rootdir, archive, checked_list)
        if VERB:
            print('> (6/6) Removed local files from push directory')
            logger.info('> (6/6) Removed local files from push directory')
    else:
        if VERB:
            print('> Exiting flight pipeline')
            logger.info('> Exiting flight pipeline')

    # Move old records into an archive directory

def updateFlights(update):
    """
    Update flights using resolve_link() from flightpipe/flight_client module.
    """
    from ceda_flight_pipeline import updaters
    fclient = ESFlightClient('', settings_file)
    updaters[update](fclient)

def reindex(new_index):
    """
    Running a re-index using the source and destination from settings_file.
    """
    fclient = ESFlightClient('', settings_file)
    fclient.reindex(new_index)

def main():
        # flight_update.py add --overwrite

    parser = argparse.ArgumentParser(description='Run the flight pipeline to push or update flights')
    parser.add_argument('mode',    type=str, help='Mode to run for the pipeline (add/update/reindex)')

    parser.add_argument('--update', dest='update', type=str, help='Name of script in updates/ to use.')
    parser.add_argument('--new-index', dest='new_index', type=str, help='New elasticsearch index to move to.')


    args = parser.parse_args()

    IS_FORCE = False
    REPUSH = False

    if args.mode == 'add':
        logger.debug("Mode set to add")
        root, archive = openConfig()

        logger.debug("Root directory set to %s", root)
        logger.debug("Archive set to %s", archive)

        if archive == '':
            print('Error: Please fill in second directory in dirconfig file')
            logger.error("Second directory in dirconfig file missing")
            sys.exit()
        elif root == '':
            print('Error: Please fill in first directory in dirconfig file')
            logger.error("First directory in dirconfig file missing")
            sys.exit()
        else:
            addFlights(root, archive, repush=REPUSH)

        """
        elif args.mode == 'retrieve':
            rootdir, archive = openConfig()
            fclient = ESFlightClient(rootdir)
            with open('check_paths.txt') as f:
                check_paths = [r.strip() for r in f.readlines()]
            fclient.check_set(check_paths)
        """

    elif args.mode == 'update':
        logger.debug("Mode set to update")
        updateFlights(args.update)

    elif args.mode == 'add_moles':
        logger.debug("Mode set to add moles")
        updateFlights('moles')

    elif args.mode == 'reindex':
        logger.debug("Mode set to reindex")
        reindex(args.new_index)
    else:
        logger.error("Mode unrecognised - ", args.mode)
        print('Error: Mode unrecognised - ', args.mode)
        sys.exit()



if __name__ == '__main__':

    main()