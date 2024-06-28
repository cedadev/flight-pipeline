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
from flightpipe.utils import genID

from datetime import datetime

import re
import requests

import urllib3
urllib3.disable_warnings()

def resolve_link(path, ):
    mpath = str(path)

    uuid = None
    while len(path.split('/')) > 3 and not uuid:
        pattern = f'http://api.catalogue.ceda.ac.uk/api/v2/observations.json/?fields=uuid,result_field&result_field__dataPath={path}'
        try:
            resp = requests.get(pattern).text
            r = json.loads(resp)
            if r['results']:
                uuid = r['results'][0]['uuid']
        except:
            print(f'Unsuccessful link retrieval for {path} - proceeding without')
        path = '/'.join(path.split('/')[:-1])

    if not uuid:
        print(f'Recursive path search failed for: {mpath}')

    return uuid

class ESFlightClient():
    """
    Connects to an elasticsearch instance and exports the
    documents to elasticsearch."""

    def __init__(self, rootdir, es_config):
        self.rootdir = rootdir

        self.index = "stac-flightfinder-items"
        fieldmatch = "id"

        if isinstance(es_config,str):
            with open(es_config) as f:
                connection_kwargs = json.load(f)
        else:
            connection_kwargs = es_config

        with open('stac_template.json') as f:
            self.required_keys = json.load(f).keys()

        self.es = Elasticsearch(**connection_kwargs)

    def push_flights(self, file_list):
        
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
                    id = genID()
                    source['es_id'] = id
            else:
                id = genID()
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
                raise TypeError(f"File {file} is missing entries:{missing}")

            source['last_update'] = datetime.strftime(datetime.now(),'%Y-%m-%d %H:%M:%S')

            refs['_source'] = source

            yield refs
        
    def bulk_push(self, flights):
        print('Creating bulk push')
        bulk(self.es, self.push_flights(flights))

    def obtain_field(self, id, fieldnames):
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
            return resp['hits']['hits'][0]
        except IndexError: # No entry found
            return None

    def obtain_records(self):
        search = {
            "size":10000,
            "query": {
                "match_all":{}
            }
        }

        resp = self.es.search(
            index=self.index,
            body=search)

        try:
            return resp['hits']['hits']
        except IndexError: # No entry found
            return None

    def add_field(self, id, data, fieldname):
        # Update mapping
        self.es.update(index=self.index, doc_type='_doc', id=id, body={'doc':{fieldname:data}})

    def obtain_ids(self):
        search = {
            "size":10000,
            "query": {
                "match_all":{}
            }
        }

        resp = self.es.search(
            index=self.index,
            body=search)
        
        return resp['hits']['hits']

    def sort_codes(self):

        ids = [i['_source']['id'] for i in self.obtain_ids()]

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
