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

        self.pcodes = {}
        self.ys, self.yms, self.ymds = {},{},{}
        for bucket in resp['aggregations']['ids']['buckets']:
            ptcode = bucket['key']
            pcode = ptcode.split('*')[0]
            yr = ptcode.split('*')[1].split('-')[0]
            mth = ptcode.split('*')[1].split('-')[1]
            day = ptcode.split('*')[1].split('-')[2]
            self.pcodes[pcode] = 1
            self.ys[yr] = 1
            self.yms[yr + '-' + mth] = 1
            self.ymds[yr + '-' + mth + '-' + day] = 1

    def check_ptcode(self, ptcode):
        pcode = ptcode.split('*')[0]
        yr = ptcode.split('*')[1].split('-')[0]
        mth = ptcode.split('*')[1].split('-')[1]
        day = ptcode.split('*')[1].split('-')[2]
        try:
            s1 = self.ys[yr]
            try:
                s2 = self.yms[yr + '-' + mth]
                try:
                    s3 = self.ymds[yr + '-' + mth + '-' + day]

                    try:
                        s4 = self.pcodes[pcode]
                        # Entry already exists
                        return False
                    except:
                        # New pcode-date combo
                        return True
                except:
                    # New ymd
                    return True
            except:
                # New ym
                return True
        except:
            # New year
            return True
            

if __name__ == "__main__":
    print(__file__)