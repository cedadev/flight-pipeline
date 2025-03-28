'''
 --- Update Flight records ---
  - Mechanism for uploading new flight records
  - Use ES Client to determine array of ids that currently exists in the index
  - Push new records
'''
from flightpipe.flight_client import ESFlightClient
import importlib

import argparse

import os, sys

IS_FORCE = True
VERB = True

settings_file = 'settings.json'

def openConfig():
    if VERB:
        print('> (1/6) Opening Config File')
    f = open('dirconfig','r')
    content = f.readlines()
    f.close()
    try:
        return content[1].replace('\n',''), content[3].replace('\n','')
    except IndexError:
        print('Error: One or both paths missing from the dirconfig file - please fill these in')
        return '',''

def moveOldFiles(rootdir, archive, files):
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

    checked_list = []

    # ES client to determine array of ids
    if VERB:
        print('> (2/6) Setting up ES Flight Client')
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
    if len(checked_list) > 0:
        fclient.push_flights(checked_list)
        if VERB:
            print('> (5/6) Pushed flights to ES Index')
        if not repush:
            moveOldFiles(rootdir, archive, checked_list)
        if VERB:
            print('> (6/6) Removed local files from push directory')
    else:
        if VERB:
            print('> Exiting flight pipeline')

    # Move old records into an archive directory

def updateFlights(update):
    from flightpipe import updaters
    fclient = ESFlightClient('', settings_file)
    updaters[update](fclient)

def reindex(new_index):
    fclient = ESFlightClient('', settings_file)
    fclient.reindex(new_index)

if __name__ == '__main__':

    # flight_update.py add --overwrite

    parser = argparse.ArgumentParser(description='Run the flight pipeline to push or update flights')
    parser.add_argument('mode',    type=str, help='Mode to run for the pipeline (add/update/reindex)')

    parser.add_argument('--update', dest='update', type=str, help='Name of script in updates/ to use.')
    parser.add_argument('--new-index', dest='new_index', type=str, help='New elasticsearch index to move to.')


    args = parser.parse_args()

    IS_FORCE = False
    REPUSH = False

    if args.mode == 'add':
        root, archive = openConfig()
        if archive == '':
            print('Error: Please fill in second directory in dirconfig file')
            sys.exit()
        elif root == '':
            print('Error: Please fill in first directory in dirconfig file')
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
        updateFlights(args.update)

    elif args.mode == 'add_moles':
        updateFlights('moles')

    elif args.mode == 'reindex':
        reindex(args.new_index)
    else:
        print('Error: Mode unrecognised - ', args.mode)
        sys.exit()

