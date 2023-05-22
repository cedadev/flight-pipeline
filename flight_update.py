'''
 --- Update Flight records ---
  - Mechanism for uploading new flight records
  - Use ES Client to determine array of ids that currently exists in the index
  - Push new records
'''
from python_scripts.elastic_client import ESFlightClient
import importlib

import os, sys

IS_FORCE = False
VERB = True

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


def addFlights(rootdir, archive):

    files_list = os.listdir(rootdir)
    checked_list = []

    # ES client to determine array of ids
    if VERB:
        print('> (2/6) Setting up ES Flight Client')
    fclient = ESFlightClient(rootdir)
    if not IS_FORCE:
        if VERB:
            print('> (3/6) Obtaining existing IDs for comparison')
        fclient.obtain_ids()
        for flight in files_list:
            if fclient.check_ptcode(flight):
                checked_list.append(flight)
    else:
        if VERB:
            print('> (3/6) Obtaining Flight-Write list')
        checked_list = list(files_list)

    # Push new flights to index
    if VERB:
        print('> (4/6) Identified {} New flights to push'.format(len(checked_list)))
    if len(checked_list) > 0:
        fclient.push_flights(checked_list)
        if VERB:
            print('> (5/6) Pushed flights to ES Index')
        moveOldFiles(rootdir, archive, checked_list)
        if VERB:
            print('> (6/6) Removed local files from push directory')
    else:
        if VERB:
            print('> Exiting flight pipeline')

    # Move old records into an archive directory


    # Create Stac Records - if necessary

    # Obtained a list of unregistered flights that need to be added.

    '''
    for cpc in checked_pcodes.keys():
        cpc_data = checked_pcodes[cpc]

        stac_record = dict(stac_template)

        # Start with Archive Meta Search
        stac_record = ArchiveMeta(cpc_data).concatInfo(stac_record)

        # Get Spatial/Temporal Info
        l1b_data = ArchiveData(cpc_data)

        stac_record["geometry"]["display"] = l1b_data.getDisplay()
        stac_record["properties"]["start_datetime"] = l1b_data.getStart()
        stac_record["properties"]["end_datetime"] = l1b_data.getEnd()

        # send stac_record to fclient using 'yield'?

        # Write stac_record
        if IS_WRITE:
            jsonWrite(outdir, cpc, stac_record)
    '''

def updateFlights(update):
    edit = importlib.import_module(update)
    fclient = ESFlightClient('')
    fclient.obtain_ids()

    edit.update(fclient)

def reindex(new_index):
    fclient = ESFlightClient('')
    fclient.reindex(new_index)

if __name__ == '__main__':

    # flight_update.py add --overwrite

    try:
        mode = sys.argv[1]
    except:
        print('Error: No mode given (add or update)')
        sys.exit()

    try:
        IS_FORCE = ('--overwrite' in sys.argv)
    except:
        pass

    if mode == 'add':
        root, archive = openConfig()
        if archive == '':
            print('Error: Please fill in second directory in dirconfig file')
            sys.exit()
        elif root == '':
            print('Error: Please fill in first directory in dirconfig file')
            sys.exit()
        else:
            addFlights(root, archive)

    elif mode == 'update':
        try:
            pyfile = sys.argv[2]
        except IndexError:
            print('Error: No update script specified')
            sys.exit()
        updateFlights(pyfile)

    elif mode == 'reindex':
        try:
            new_index = sys.argv[2]
        except IndexError:
            print('Error: No new index specified')
            sys.exit()
        reindex(new_index)
    else:
        print('Error: Mode unrecognised - ', mode)
        sys.exit()

