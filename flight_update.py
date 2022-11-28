'''
 --- Update Flight records ---
  - Mechanism for finding new flight ids/paths
  - Use ES Client to determine array of ids that currently exists in the index
  - Construct Metadata 'properties' field
  - Determine Spatial Coordinates and Temporal dates
  - Push new records
'''
from python_scripts.calculate_coordinates import getCoords, getTimes
from python_scripts.elastic_client import ESFlightClient
from python_scripts.archive_meta import ArchiveMeta
from python_scripts.utils import jsonWrite

import os, sys

def invalid_dirs(root, out):
    return (root == out) or \
           (root == '') or \
           (out == '') 

def main(rootdir, outdir):
    if invalid_dirs(rootdir, outdir):
        print('Error invalid dir structure with root and out')
        sys.exit()
    # Mechanism for finding new ids
    new_pcodes     = {}
    checked_pcodes = {}

    if new_pcodes != {}:

        # ES client to determine array of ids
        fclient = ESFlightClient(rootdir, outdir)
        fclient.obtain_ids()
        for npc in new_pcodes.keys():
            if fclient.check_pcode(npc):
                checked_pcodes[npc] = new_pcodes[npc]

        # Obtained a list of unregistered flights that need to be added.

        for cpc in checked_pcodes.keys():
            cpc_data = checked_pcodes[cpc]

            # Start with Archive Meta Search
            stac_record = ArchiveMeta(cpc_data).concatInfo()

            # Get Spatial/Temporal Info
            l1b_data = ArchiveData(cpc_data)

            stac_record["geometry"]["display"] = l1b_data.getDisplay()
            stac_record["properties"]["start_datetime"] = l1b_data.getStart()
            stac_record["properties"]["end_datetime"] = l1b_data.getEnd()

            # Write stac_record
            if IS_WRITE:
                jsonWrite(outdir, cpc, stac_record)

        fclient.push_flights()
    else:
        print('No new flights detected - exiting')

if __name__ == '__main__':
    try:
        main('', sys.argv[1])
    except IndexError:
        print('Error: No root or out dirs specified')
