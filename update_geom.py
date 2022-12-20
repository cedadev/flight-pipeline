#from python_scripts.elastic_client import ESFlightClient
import os, sys
import numpy as np

from python_scripts.utils import recursiveList, recursiveConvert, forceSearch

def update(fclient):

    # Retrieve the contents of each record in full?
    # Or push new field to the existing record structure.

    '''
    "geometry":{
        "display":{},
    }
    to
    "geometries":{
        "search":{},
        "display":{}
    }
    '''
    index = 0
    for ptcode in fclient.ptcodes.keys():
        index += 1
        print(index, len(fclient.ptcodes.keys()))
        id = [
            ptcode.split('*')[0],
            ptcode.split('*')[1].split('-')[0],
            ptcode.split('*')[1].split('-')[1],
            ptcode.split('*')[1].split('-')[2],
        ]
        print(ptcode)
        geometry = fclient.obtain_field(id, ['geometry','id'])
        if geometry and index > 133:
            identifier = geometry['_id']
            geometry = geometry['_source']['geometry']
            coords = geometry['display']['coordinates']
            # Check using python array methods - if needed
            # [maxs, mins] = forceSearch(coords, [-99, -189], [99, 189],0)
            coords = recursiveConvert(coords) # Destroys coord structure above lat/lon separation
            lats = coords[:,0]
            lons = coords[:,1]

            envelope = [
                [np.min(lats), np.max(lons)],
                [np.max(lats), np.min(lons)]
            ]

            # Update with search field
            geometries = {
                "search":{
                    "type":"envelope",
                    "coordinates": envelope
                }
            }

            # Add Geometries and Remove Geometry
            fclient.add_field(identifier, geometries, 'geometry')
            print('Added field')
            # Or simply replace all data - seems like a waste?

            ## Update geometry field
    # Obtain list of IDs
    # Retrieve geometry field for each ID
    # Calculate Search Envelope
    # Update by ID


if __name__ == '__main__':
    print(__file__)