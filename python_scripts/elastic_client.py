'''
 --- Elastic Client ---
  - Extract all items from flight finder index by organisation
  - Save flight numbers to array - return array
'''

import json
import os, sys
import numpy as np

from elasticsearch import Elasticsearch

class ESFlightClient:
    """
    Connects to an elasticsearch instance and exports the
    documents to elasticsearch."""

    connection_kwargs = {
        "hosts": ["es9.ceda.ac.uk:9200"],
        "headers": {
            "x-api-key":  "b0cc021feec53216cb470b36bec8786b10da4aa02d60edb91ade5aae43c07ee6",
        },
        "use_ssl": True,
        "verify_certs": False,
        "ssl_show_warn": False,
    }
    index = "stac-flightfinder-items"

    def __init__(self, rootdir):
        self.rootdir = rootdir

        self.es = Elasticsearch(**self.connection_kwargs)
        if not self.es.indices.exists(self.index):
            self.es.indices.create(self.index)

    def bulk_iterator(self, file_list):
        for file in file_list:
            with open(self.rootdir + '/' + file) as f:
                con = json.load(f)
                yield {
                    "_index":self.index,
                    "_type": "_doc",
                    "_id":con["es_id"],
                    "_score":0.0,
                    "_source":con
                }
    
    def push_flights(self, file_list):
        bulk(self.es, self.action_iterator(file_list))
        
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
        pcode = ptcode.split('*')[0]
        yr = ptcode.split('*')[1].split('-')[0]
        mth = ptcode.split('*')[1].split('-')[1]
        day = ptcode.split('*')[1].split('-')[2]
        if yr not in self.ys:
            return True
        if yr + '-' + mth not in self.yms:
            return True
        if yr + '-' + mth + '-' + day not in self.ymds:
            return True
        if pcode not in self.pcodes:
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