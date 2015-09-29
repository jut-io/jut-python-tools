"""
jut upload module

"""

import os
import json
import requests
import hashlib

from jut.common import info

# long lived requests session object to keep HTTP connections alive
SESSION = requests.Session()

def post(json_data,
         url,
         dry_run=False):

    """
    POST json data to the url provided and verify the requests was successful

    """

    if dry_run:
        info('POST: %s' % json.dumps(json_data, indent=4))
    else:
        response = SESSION.post(url,
                                data=json.dumps(json_data),
                                headers={'content-type': 'application/json'})

        if response.status_code != 200:
            raise Exception("Failed to import %s with %s: %s" %
                            (json_data, response.status_code, response.text))


def md5sum(data):
    return hashlib.md5(data).hexdigest()


def push_json_file(json_file,
                   url,
                   dry_run=False,
                   batch_size=100,
                   anonymize_fields=[],
                   remove_fields=[],
                   rename_fields=[]):
    """
    read the json file provided and POST in batches no bigger than the
    batch_size specified to the specified url.

    """
    batch = []
    json_data = json.loads(json_file.read())

    if isinstance(json_data, list):
        for item in json_data:

            # anonymize fields
            for field_name in anonymize_fields:
                if field_name in item:
                    item[field_name] = md5sum(item[field_name])

            # remove fields
            for field_name in remove_fields:
                if field_name in item:
                    del item[field_name]

            # rename fields
            for (field_name, new_field_name) in rename_fields:
                if field_name in item:
                    item[new_field_name] = item[field_name]
                    del item[field_name]

            batch.append(item)

            if len(batch) >= batch_size:
                post(batch,
                     url,
                     dry_run=dry_run)
                batch = []

        if len(batch) > 0:
            post(batch,
                 url,
                 dry_run=dry_run)

    else:
        post(json_data,
             url,
             dry_run=dry_run)

