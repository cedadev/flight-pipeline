'''
 --- Elastic Client ---
  - Extract all items from flight finder index by organisation
  - Save flight numbers to array - return array
'''

import json
import os, sys
import numpy as np

from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

from ceda_flight_pipeline.logger import logger

from ceda_flight_pipeline.simple_client import SimpleClient, gen_id

from datetime import datetime

import re
import requests

import urllib3
urllib3.disable_warnings()

def resolve_link(path):
    logger.debug("Debug: Resolving link for path %s", path)
    mpath = str(path)

    uuid = None
    while len(path.split('/')) > 3 and not uuid:
        pattern = f'http://api.catalogue.ceda.ac.uk/api/v2/observations.json/?fields=uuid,result_field&result_field__dataPath={path}'
        try:
            resp = requests.get(pattern).text
            r = json.loads(resp)
            if r['results']:
                uuid = r['results'][0]['uuid']
                logger.debug("Debug: Reslolving link, found uuid %s", str(uuid))
        except:
            print(f'Unsuccessful link retrieval for {path} - proceeding without')
        path = '/'.join(path.split('/')[:-1])

    if not uuid:
        logger.error("Error: Recursive path search failed for %s", mpath)
        print(f'Recursive path search failed for: {mpath}')

    return uuid

class ESFlightClient(SimpleClient):
    """
    Connects to an elasticsearch instance and exports the
    documents to elasticsearch.
    """

    def __init__(self, rootdir, es_config=os.environ.get("SETTINGS_FILE")):
        self.rootdir = rootdir
        logger.info("Info: Initialising ES Flight Client")

        super().__init__("stac-flightfinder-items-test", es_config=es_config)

        with open(os.environ.get("STAC_TEMPLATE")) as f:
            logger.info("Info: Reading stac templace JSON file")
            self.required_keys = json.load(f).keys()

    def push_flights(self, file_list):
        flight_list = []
        if isinstance(file_list[0], str):
            for file in file_list:
                with open(os.path.join(self.rootdir, file)) as f:
                    flight_list.append(json.load(f))
        elif isinstance(file_list[0], dict):
            flight_list = file_list
        else:
            logger.error("Error: Flight file not found %s", str(file_list[0]))
            raise FileNotFoundError(file_list[0])
        logger.info("Info: Flights to be pushed %s", str(flight_list))
        self.push_records(flight_list)
        
    def preprocess_records(self, file_list):
        logger.debug("Debug: Processing following records - %s", file_list)
        
        def set_defaults(refs):
            collection = refs['collection']
            flight_num = refs['properties']['flight_num']
            pcode = refs['properties']['pcode'][0]
            date = refs['properties']['pcode'][1]

            id = f'{collection}__{flight_num}__{pcode}__{date}'.replace(' ','')
            refs['id'] = id
            refs['type'] = 'Feature'
            refs['stac_version'] = '1.0.0'
            refs['stac_extensions'] = [""]
            refs['assets'] = {}
            refs['links'] = []
            return refs

        self.linked = 0
        self.total = len(file_list)
        records = []
        for refs in file_list:
            if '_source' in refs.keys():
                id = refs['_id']
                source = refs['_source']
                source['es_id'] = id
            source = set_defaults(source)

            if 'es_id' in source.keys():
                if source['es_id']:
                    id = source['es_id']
                else:
                    id = gen_id()
                    source['es_id'] = id
            else:
                id = gen_id()
                source['es_id'] = id

            source['catalogue_link'] = ''
            link = resolve_link(source['description_path'])
            if link:
                source['catalogue_link'] = f'https://catalogue.ceda.ac.uk/uuid/{link}'
                self.linked += 1
            else:
                del source['catalogue_link']

            missing = []
            for rq in self.required_keys:
                if rq not in source:
                    missing.append(rq)
            if len(missing) > 0:
                logger.error("Error: File is missing entries - %s", str(missing))
                raise TypeError(f"File {file} is missing entries:{missing}")

            source['last_update'] = datetime.strftime(datetime.now(),'%Y-%m-%d %H:%M:%S')

            refs['_source'] = source
            records.append(refs)

        return records

    def obtain_field(self, id, fieldnames):
        logger.info("Info: Performing query to obtain the following fields: %s", str(fieldnames))
        search = {
            "_source": fieldnames,
            "query": {
                "bool":{
                    "must":[{"term":{"id":i}} for i in id]
                }
            }
        }

        resp = self.es.search(
            index=self.index,
            body=search)

        try:
            logger.info("Info: Found following fields: %s", str(resp['hits']['hits'][0]))
            return resp['hits']['hits'][0]
        except IndexError: # No entry found
            logger.error("Error: No entry found.")
            return None

    def add_field(self, id, data, fieldname):
        logger.debug("Debug: Update mapping for id - %s", str(id))
        # Update mapping
        self.es.update(index=self.index, doc_type='_doc', id=id, body={'doc':{fieldname:data}})

    def sort_codes(self):

        ids = [i['_source']['id'] for i in self.pull_records()]

        self.ptcodes = {}
        self.ys, self.yms, self.ymds = {},{},{}

        for ptcode in ids:

            try:
                yr = ptcode.split('*')[1].split('-')[0]
                mth = ptcode.split('*')[1].split('-')[1]
                day = ptcode.split('*')[1].split('-')[2]
            except IndexError:
                try:
                    delim = '__'
                    date_index = 3
                    yr = ptcode.split(delim)[date_index].split('-')[0]
                    mth = ptcode.split(delim)[date_index].split('-')[1]
                    day = ptcode.split(delim)[date_index].split('-')[2]
                except IndexError:
                    pass
            self.ptcodes[ptcode] = 1
            self.ys[yr] = 1
            self.yms[yr + '-' + mth] = 1
            self.ymds[yr + '-' + mth + '-' + day] = 1

    def check_set(self, paths):
        for x, p in enumerate(paths):
            try:
                pcode = re.search(f'[a-z]\d\d\d', p).group()# Replace with re.match at some point
            except AttributeError:
                continue
            search = {
                #"_source": fieldnames,
                "query": {
                    "bool":{
                        "filter":{
                            "bool":{
                                "must":{"term":{"properties.flight_num":pcode}}
                            }
                        }
                    }
                }
            }
            resp = self.es.search(
                index=self.index,
                body=search)

            if resp['hits']['total']['value'] > 0:
                if 'coordinates' in resp['hits']['hits'][0]['geometry']['display']:
                    print(f'{x+1}. {pcode} appears to have coordinates')
                else:
                    print(f'{x+1}. {pcode} appears to not have coordinates')
            else:
                print(f'{x+1}. {pcode} does not have an entry')

    def check_ptcode(self, ptcode):
        if '*' in ptcode:
            return 300
        delim = '__'
        date_index = 3
        print(ptcode)
        yr = ptcode.split(delim)[date_index].split('-')[0]
        mth = ptcode.split(delim)[date_index].split('-')[1]
        day = ptcode.split(delim)[date_index].split('-')[2]
        if yr not in self.ys:
            return 200
        if yr + '-' + mth not in self.yms:
            return 200
        if yr + '-' + mth + '-' + day not in self.ymds:
            return 200
        if ptcode not in self.ptcodes:
            return 200

        # If all filters have passed
        return 100

    def reindex(self, new_index):
        logger.debug("Debug: Reindex for source %s and destination %s", self.index, new_index)

        self.es.reindex({
            "source":{
                "index":self.index
            },
            "dest":{
                "index": new_index
            }#, # Need to carry everything over except geometries.
            #"script":{
            #    "inline":"ctx._source.data.properties.geometry.remove('geometries')"
            #}
        })


if __name__ == "__main__":
    print(__file__)
