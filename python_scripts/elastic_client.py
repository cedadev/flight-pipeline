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
from .utils import genID

class ESFlightClient:
    """
    Connects to an elasticsearch instance and exports the
    documents to elasticsearch."""

    f = open('settings.json','r')
    connection_kwargs = json.load(f)
    f.close()


    index = "stac-flightfinder-items"

    def __init__(self, rootdir):
        self.rootdir = rootdir

        with open('stac_template.json') as f:
            self.required_keys = json.load(f).keys()

        self.es = Elasticsearch(**self.connection_kwargs)
        if not self.es.indices.exists(self.index):
            self.es.indices.create(self.index)

    def bulk_iterator(self, file_list):
        for file in file_list:
            with open(self.rootdir + '/' + file) as f:
                con = json.load(f)
                missing = []
                for rq in self.required_keys:
                    if rq not in con:
                        missing.append(rq)
                if len(missing) > 0:
                    raise TypeError(f"File {file} is missing entries:{missing}")
                try:
                    id = con["es_id"]
                    source = con
                except:
                    try:
                        id = con["_source"]["es_id"]
                        source = con["_source"]
                    except:
                        id = genID()
                        source = con["_source"]
                yield {
                    "_index":self.index,
                    "_type": "_doc",
                    "_id": id,
                    "_score":0.0,
                    "_source":source
                }
    
    def push_flights(self, file_list):
        bulk(self.es, self.bulk_iterator(file_list))
        
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

    def add_field(self, id, data, fieldname):
        # Update mapping
        self.es.update(index=self.index, doc_type='_doc', id=id, body={'doc':{fieldname:data}})

    def obtain_ids(self):
        aggs = {
            "size":0,
            "aggs":{
                "ids":{
                    "terms":{
                        "field":"id.keyword",
                        "size":10000
                    }
                }
            }
        }
        resp = self.es.search(
            index=self.index,
            body=aggs)

        self.ptcodes = {}
        self.ys, self.yms, self.ymds = {},{},{}
        for bucket in resp['aggregations']['ids']['buckets']:
            ptcode = bucket['key']
            yr = ptcode.split('*')[1].split('-')[0]
            mth = ptcode.split('*')[1].split('-')[1]
            day = ptcode.split('*')[1].split('-')[2]
            self.ptcodes[ptcode] = 1
            self.ys[yr] = 1
            self.yms[yr + '-' + mth] = 1
            self.ymds[yr + '-' + mth + '-' + day] = 1

    def check_ptcode(self, ptcode):
        yr = ptcode.split('*')[1].split('-')[0]
        mth = ptcode.split('*')[1].split('-')[1]
        day = ptcode.split('*')[1].split('-')[2]
        if yr not in self.ys:
            return True
        if yr + '-' + mth not in self.yms:
            return True
        if yr + '-' + mth + '-' + day not in self.ymds:
            return True
        if ptcode not in self.ptcodes:
            return True

        # If all filters have passed
        return False

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