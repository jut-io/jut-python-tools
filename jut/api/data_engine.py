"""
data engine API

"""

import json
import random
import requests

from websocket import create_connection

from jut import defaults
from jut.api import auth, deployments
from jut.exceptions import JutException
from jut.common import debug


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
    relevant information from running import that program as a generator of
    events which include:

        * { "points": [ array of points ] }
        * {
            "error": true,
            payload with "info" and "context" explaining exact error
          }
        * {
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

    debug("connecting to %s", url)

    websocket = create_connection(url)
    websocket.send(json.dumps(token_obj))

    data = websocket.recv()
    channel_id_obj = json.loads(data)

    debug('got channel response %s', json.dumps(channel_id_obj, indent=4))

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

    debug('started job %s', json.dumps(job_info, indent=2))

    if not persist:
        job_finished = False
        sinks_finished = False
        sinks = job_info['sinks']

        for sink in sinks:
            sink['done'] = False

        while not job_finished and not sinks_finished:
            data = json.loads(websocket.recv())
            debug('received %s' % json.dumps(data, indent=2))

            if 'eof' in data.keys():
                sink_channel = data['sink']

                for sink in sinks:
                    if sink['channel'] == sink_channel:
                        sink['done'] = True

            if 'ping' in data.keys():
                # ping/pong (ie heartbeat) mechanism
                debug('ping received on websocket')
                pong_obj = {'pong': True}
                websocket.send(json.dumps(pong_obj))
                debug('pong sent in response')

            if 'job_end' in data.keys() and data['job_end'] == True:
                job_finished = True

            for sink in sinks:
                sinks_finished &= sink['done']

            # return all channel messages
            yield data

    websocket.close()

