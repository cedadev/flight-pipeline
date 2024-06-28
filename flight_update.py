'''
 --- Update Flight records ---
  - Mechanism for uploading new flight records
  - Use ES Client to determine array of ids that currently exists in the index
  - Push new records
'''
from flightpipe.elastic_client import ESFlightClient
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

test = {
        "description_path": "/neodc/arsf/2002/00_02",
        "es_id": "092cc8760ca44d66e9534b50cda977d95290f205",
        "geometry": {
            "display": {
                "coordinates": [
                    [
                        [
                            -4.017899,
                            57.0826952
                        ],
                        [
                            -4.0150244,
                            57.0837034
                        ],
                        [
                            -4.012297,
                            57.0847855
                        ],
                        [
                            -4.0096279,
                            57.0858878
                        ],
                        [
                            -4.006985,
                            57.0870138
                        ],
                        [
                            -4.0042917,
                            57.0881457
                        ],
                        [
                            -4.0015045,
                            57.0892878
                        ],
                        [
                            -3.9986163,
                            57.090438
                        ],
                        [
                            -3.9956629,
                            57.091604
                        ],
                        [
                            -3.9926722,
                            57.0927883
                        ],
                        [
                            -3.989661,
                            57.0939946
                        ],
                        [
                            -3.9866696,
                            57.0952401
                        ],
                        [
                            -3.9837207,
                            57.0965217
                        ],
                        [
                            -3.9808004,
                            57.0978144
                        ],
                        [
                            -3.977886,
                            57.0991014
                        ],
                        [
                            -3.9749585,
                            57.1003744
                        ],
                        [
                            -3.9720213,
                            57.1016408
                        ],
                        [
                            -3.9690777,
                            57.1029012
                        ],
                        [
                            -3.9661268,
                            57.1041472
                        ],
                        [
                            -3.9631829,
                            57.105386
                        ],
                        [
                            -3.9602733,
                            57.1066231
                        ],
                        [
                            -3.9574227,
                            57.1078601
                        ],
                        [
                            -3.9546271,
                            57.1090948
                        ],
                        [
                            -3.9518687,
                            57.1103243
                        ],
                        [
                            -3.9491303,
                            57.1115448
                        ],
                        [
                            -3.9464064,
                            57.1127557
                        ],
                        [
                            -3.9436777,
                            57.1139549
                        ],
                        [
                            -3.9409397,
                            57.1151498
                        ],
                        [
                            -3.9381834,
                            57.1163379
                        ],
                        [
                            -3.9354131,
                            57.1175255
                        ]
                    ],
                    [
                        [
                            -3.9184596,
                            57.1119002
                        ],
                        [
                            -3.9215371,
                            57.1105882
                        ],
                        [
                            -3.9246265,
                            57.1092483
                        ],
                        [
                            -3.9277538,
                            57.1078754
                        ],
                        [
                            -3.9309346,
                            57.1064816
                        ],
                        [
                            -3.9341952,
                            57.1051065
                        ],
                        [
                            -3.9374816,
                            57.1037509
                        ],
                        [
                            -3.9407347,
                            57.1024099
                        ],
                        [
                            -3.943958,
                            57.1011103
                        ],
                        [
                            -3.9471453,
                            57.0998469
                        ],
                        [
                            -3.9503185,
                            57.0986016
                        ],
                        [
                            -3.9535027,
                            57.0973635
                        ],
                        [
                            -3.9566927,
                            57.0961132
                        ],
                        [
                            -3.9598828,
                            57.0948314
                        ],
                        [
                            -3.9630611,
                            57.0934964
                        ],
                        [
                            -3.9662202,
                            57.0920978
                        ],
                        [
                            -3.9693962,
                            57.0906691
                        ],
                        [
                            -3.9725742,
                            57.0892365
                        ],
                        [
                            -3.975768,
                            57.0878343
                        ],
                        [
                            -3.9789704,
                            57.0864636
                        ],
                        [
                            -3.9821743,
                            57.0851281
                        ],
                        [
                            -3.9853524,
                            57.0838198
                        ],
                        [
                            -3.9885065,
                            57.0825387
                        ],
                        [
                            -3.9916442,
                            57.0812745
                        ],
                        [
                            -3.9948191,
                            57.080023
                        ],
                        [
                            -3.9980353,
                            57.0787722
                        ],
                        [
                            -4.0012414,
                            57.0774806
                        ],
                        [
                            -4.0044159,
                            57.0761358
                        ],
                        [
                            -4.0075062,
                            57.0747138
                        ],
                        [
                            -4.0103984,
                            57.0731602
                        ]
                    ]
                ],
                "type": "MultiLineString"
            }
        },
        "collection": "arsf",
        "properties": {
            "data_format": "HDF4",
            "flight_num": "00_02",
            "altitude": "",
            "variables": [
                "ATM 0.42-13.5mm"
            ],
            "principle": "",
            "instruments": [],
            "start_datetime": "2002-09-01T09:00:26",
            "end_datetime": "2002-09-01T09:08:38",
            "pcode": [
                "00_02",
                "2002-09-01"
            ],
            "aircraft": "",
            "location": [
                "Insh Marshes"
            ],
            "platform": ""
        },
        "id": "arsf__00_02__00_02__2002-09-01",
        "type": "Feature",
        "stac_version": "1.0.0",
        "stac_extensions": [
            ""
        ],
        "assets": {},
        "links": []
}

def special():
    import json
    fclient = ESFlightClient('', settings_file)
    fclient.add_records([test])

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

    elif args.mode == 'special':
        special()

    elif args.mode == 'reindex':
        reindex(args.new_index)
    else:
        print('Error: Mode unrecognised - ', args.mode)
        sys.exit()

