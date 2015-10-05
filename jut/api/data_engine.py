"""
data engine API

"""

import json
import random
import requests
import socket

from websocket import create_connection

from jut import defaults
from jut.api import auth, deployments
from jut.common import debug, is_debug_enabled


def get_data_url(deployment_name,
                 endpoint_type='juttle',
                 access_token=None,
                 app_url=defaults.APP_URL):
    """
    get the data url for a specified endpoint_type, currently supported types
    are:

     * http-import: for importing data points
     * juttle: for running juttle programs

    """
    deployment_details = deployments.get_deployment_details(deployment_name,
                                                            access_token=access_token,
                                                            app_url=app_url)

    # use a random juttle endpoint
    endpoints = []
    for endpoint in deployment_details['endpoints']:
        if endpoint_type in endpoint['type']:
            endpoints.append(endpoint)

    return random.choice(endpoints)['uri']


def get_juttle_data_url(deployment_name,
                        access_token=None,
                        app_url=defaults.APP_URL):
    """
    return the juttle data url

    """
    return get_data_url(deployment_name,
                        endpoint_type='juttle',
                        app_url=app_url,
                        access_token=access_token)

def get_import_data_url(deployment_name,
                        access_token=None,
                        app_url=defaults.APP_URL):
    """
    return the import data url

    """
    return get_data_url(deployment_name,
                        endpoint_type='http-import',
                        app_url=app_url,
                        access_token=access_token)


def run(juttle,
        deployment_name,
        program_name=None,
        persist=True,
        access_token=None,
        app_url=defaults.APP_URL):
    """
    run a juttle program through the juttle streaming API and return the
    the various events that are part of running a Juttle program which
    include:
        
        
        * Initial job status details including information to associate
          multiple flowgraphs with their individual outputs (sinks):
          {
            "status": "ok",
            "job": {
              "channel_id": "56bde5f0",
              "_start_time": "2015-10-03T06:59:49.233Z",
              "alias": "jut-tools program 1443855588",
              "_ms_begin": 1443855589233,
              "user": "0fbbd98d-cf33-4582-8ca1-15a3d3fee510",
              "timeout": 5,
              "id": "b973bce6"
            },
            "now": "2015-10-03T06:59:49.230Z",
            "stats": ...
            "sinks": [
              {
                "location": {
                  "start": {
                    "column": 17,
                    "line": 1,
                    "offset": 16
                  },
                  "end": {
                    "column": 24,
                    "line": 1,
                    "offset": 23
                  },
                  "filename": "main"
                },
                "name": "table",
                "channel": "sink237",
                "options": {
                  "_jut_time_bounds": []
                }
              },
              ... as many sinks as there are flowgrpahs in your program
            ]
           }

        * Each set of points returned along with the indication of which sink
          they belong to:
          {
            "points": [ array of points ],
            "sink": sink_id
          }

        * Error event indicating where in your program the error occurred
          {
            "error": true,
            payload with "info" and "context" explaining exact error
          }

        * Warning event indicating where in your program the error occurred
          {
            "warning": true,
            payload with "info" and "context" explaining exact warning
          }

        * ...

    juttle: juttle program to execute
    deployment_name: the deployment name to execute the program on
    persist: if set to True then we won't wait for response data and will
             disconnect from the websocket leaving the program running in
             the background if it is uses a background output
             (http://docs.jut.io/juttle-guide/#background_outputs) and
             therefore becomes a persistent job.
    access_token: valid access toke obtained using auth.get_access_token
    app_url: optional argument used primarily for internal Jut testing
    """
    headers = auth.access_token_to_headers(access_token)

    data_url = get_juttle_data_url(deployment_name,
                                   app_url=app_url,
                                   access_token=access_token)

    url = '%s/api/v1/juttle/channel' %data_url.replace('https://', 'wss://')
    token_obj = {"accessToken": access_token['access_token']}

    if is_debug_enabled():
        debug("connecting to %s", url)

    websocket = create_connection(url)
    websocket.settimeout(10)
    websocket.send(json.dumps(token_obj))

    data = websocket.recv()
    channel_id_obj = json.loads(data)

    if is_debug_enabled():
        debug('got channel response %s', json.dumps(channel_id_obj))

    channel_id = channel_id_obj['channel_id']
    juttle_job = {
        'channel_id': channel_id,
        'alias': program_name,
        'program': juttle
    }

    response = requests.post('%s/api/v1/jobs' % data_url,
                             data=json.dumps(juttle_job),
                             headers=headers)

    if response.status_code != 200:
        yield {
            "error": True,
            "context": response.json()
        }
        return

    job_info = response.json()

    if is_debug_enabled():
        # yield job_info so the caller to this method can figure out which sinks
        # correlate to which flowgraphs
        yield job_info
        debug('started job %s', json.dumps(job_info))

    pong = json.dumps({
        'pong': True
    })

    if not persist:
        job_finished = False

        while not job_finished:
            data = json.loads(websocket.recv())

            if is_debug_enabled():
                debug('received %s' % json.dumps(data))

            if 'ping' in data.keys():
                # ping/pong (ie heartbeat) mechanism
                websocket.send(pong)

                if is_debug_enabled():
                    debug('sent %s' % json.dumps(pong))

            if 'job_end' in data.keys() and data['job_end'] == True:
                job_finished = True

            # return all channel messages
            yield data

    websocket.close()

