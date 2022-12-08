'''
 --- Update Flight records ---
  - Mechanism for uploading new flight records
  - Use ES Client to determine array of ids that currently exists in the index
  - Push new records
'''
from python_scripts.elastic_client import ESFlightClient

import os, sys

IS_FORCE = False

def main(rootdir):

    files_list = os.listdir(rootdir)
    checked_list = []

    # ES client to determine array of ids
    fclient = ESFlightClient(rootdir)
    fclient.obtain_ids()
    if not IS_FORCE:
        for flight in files_list:
            pcode = flight.split('*')[0]
            if fclient.check_pcode(pcode):
                checked_list.append(flight)
    else:
        checked_list = list(files_list)

    # Push new flights to index
    print('New flights: {}'.format(len(checked_list)),end='')
    if len(checked_list) != len(files_list):
        print('({} already exist)'.format(len(files_list) - len(checked_list)))
    else:
        print('')
    fclient.push_flights(checked_list)



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


if __name__ == '__main__':

    try:
        root = sys.argv[1]
    except IndexError:
        print('Error: No root or out dirs specified')
        sys.exit()
    try:
        IS_FORCE = sys.argv[2] == '--overwrite'
    except:
        pass

    main('', root)

