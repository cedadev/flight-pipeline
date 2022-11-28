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

    def __init__(self, rootdir, outdir):
        self.rootdir = rootdir
        self.outdir = outdir
        self.ids = []

        self.es = Elasticsearch(**self.connection_kwargs)
        if not self.es.indices.exists(self.index):
            self.es.indices.create(self.index)

    def bulk_iterator(self, file_list):
        for file in file_list:
            with open(self.outdir + '/' + file) as f:
                con = json.load(f)
                yield {
                    "_index":self.index,
                    "_type": "_doc",
                    "_id":con["es_id"],
                    "_score":0.0,
                    "_source":con
                }
    
    def push_flights(self):
        file_list = os.listdir(self.outdir)
        bulk(self.es, self.action_iterator(file_list))

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
        self.ids = []
        for bucket in resp['aggregations']['ids']['buckets']:
            self.ids.append(bucket['key'])

if __name__ == "__main__":
    print(__file__)