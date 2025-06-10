import json
import os
from typing import Union

from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

import logging
logger = logging.getLogger(__name__)
from ceda_flight_pipeline.utils import logstream
logger.addHandler(logstream)
logger.propagate = False

def gen_id():
    import random
    chars = [*'0123456789abcdefghijklmnopqrstuvwxyz']
    xid = ''
    for i in range(39):
        j = random.randint(0,len(chars)-1)
        xid += chars[j]
    return xid
    # Probability of id reuse is negligible.

default_rec = {
    "_index": None,
    "_type": "_doc",
    "_id":None,
    "_score": 1.0,
    "_source":None
}

settings_default = {
    "hosts": [
        "https://elasticsearch.ceda.ac.uk"
    ],
    "headers": {
        "x-api-key": ""
    }
}

def create_settings(es_config='es_settings.json'):
    with open(es_config,'w') as f:
        f.write(json.dumps(settings_default))
    

class ResponseException(Exception):
    """
    Response Exception - Elasticsearch did not return an object with any 'hits'. This indicates an error,
    as even with 0 hits returned there should still be an empty 'hits' list here.
    """
    def __init__(self, keys=None):
        self.message = f'Received ({keys}) keys from response - No "hits" received'
        super().__init__(self.message)

class SimpleClient:
    """
    Simple Elasticsearch-Python client for bulk operations
    """
    def __init__(self, index: str, es_config: Union[dict,str]):
        """
        Initialise client, pull credentials from a configuration file if present
        and create an underlying client within this class.
        """
        self.index = index

        if isinstance(es_config,str):
            if not os.path.isfile(es_config):
                raise FileNotFoundError(f'File {es_config} not present, no settings loaded.')
            with open(es_config) as f:
                connection_kwargs = json.load(f)
        else:
            connection_kwargs = es_config

        self.es = Elasticsearch(**connection_kwargs)

    def preprocess_records(self, records):
        """
        Blank preprocessor method - override with preprocessing steps for specific
        client use-cases.
        """
        return records

    def process_records(self, records):
        """
        Final processing step to add ids to new records if they are not already present.
        """
        for r in records:
            yield r

    def get_size(self):
        md = self.es.cat.count(index=self.index, params={"format": "json"})[0]
        return md['count']

    def push_records(self, records):
        """
        Push records using bulk helper tool.
        """
        records = self.preprocess_records(records)
        for r in records:
            self.es.update(
                index=self.index,
                id=r['es_id'],
                body={'doc':r,'doc_as_upsert':True}
            )

    def pull_records(self):
        """
        Pull all records up to 10,000 and return all hits.
        """
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
        except IndexError:
            raise ResponseException(keys=resp.keys())

        