"""
data engine API

"""

import json
import random
import requests
import socket
import time
import traceback

from websocket import create_connection

from jut import defaults
from jut.api import deployments
from jut.common import debug, is_debug_enabled
from jut.exceptions import JutException


def get_data_url(deployment_name,
                 endpoint_type='juttle',
                 token_manager=None,
                 app_url=defaults.APP_URL):
    """
    get the data url for a specified endpoint_type, currently supported types
    are:

     * http-import: for importing data points
     * juttle: for running juttle programs

    """
    deployment_details = deployments.get_deployment_details(deployment_name,
                                                            token_manager=token_manager,
                                                            app_url=app_url)

    # use a random juttle endpoint
    endpoints = []
    for endpoint in deployment_details['endpoints']:
        if endpoint_type in endpoint['type']:
            endpoints.append(endpoint)

    if len(endpoints) == 0:
        raise JutException('No data engine currently configured for '
                           'deployment "%s"' % deployment_name)

    return random.choice(endpoints)['uri']


def get_data_urls(deployment_name,
                  endpoint_type='juttle',
                  token_manager=None,
                  app_url=defaults.APP_URL):
    """
    get all of the data urls for a specified endpoint_type, currently supported types
    are:

     * http-import: for importing data points
     * juttle: for running juttle programs

    """
    deployment_details = deployments.get_deployment_details(deployment_name,
                                                            token_manager=token_manager,
                                                            app_url=app_url)

    # use a random juttle endpoint
    data_urls = []
    for endpoint in deployment_details['endpoints']:
        if endpoint_type in endpoint['type']:
            data_urls.append(endpoint['uri'])

    if len(data_urls) == 0:
        raise JutException('No data engine currently configured for '
                           'deployment "%s"' % deployment_name)

    return data_urls


def get_juttle_data_url(deployment_name,
                        token_manager=None,
                        app_url=defaults.APP_URL):
    """
    return the juttle data url

    """
    return get_data_url(deployment_name,
                        endpoint_type='juttle',
                        app_url=app_url,
                        token_manager=token_manager)


def get_import_data_url(deployment_name,
                        token_manager=None,
                        app_url=defaults.APP_URL):
    """
    return the import data url

    """
    return get_data_url(deployment_name,
                        endpoint_type='http-import',
                        app_url=app_url,
                        token_manager=token_manager)


def get_data_url_for_job(job_id,
                         deployment_name,
                         token_manager=None,
                         app_url=defaults.APP_URL):
    data_url = None
    jobs = get_jobs(deployment_name,
                    token_manager=token_manager,
                    app_url=app_url)

    for job in jobs:
        if job['id'] == job_id:
            data_url = job['data_url']
            break

    if data_url == None:
        raise JutException('Unable to find job with id "%s"' % job_id)

    return data_url

def __wss_connect(data_url,
                  token_manager,
                  job_id=None):
    """
    Establish the websocket connection to the data engine. When job_id is
    provided we're basically establishing a websocket to an existing
    program that was already started using the jobs API

    job_id: job id of a running program
    """
    url = '%s/api/v1/juttle/channel' % data_url.replace('https://', 'wss://')

    token_obj = {
        "accessToken": token_manager.get_access_token()
    }

    if job_id != None:
        token_obj['job_id'] = job_id

    if is_debug_enabled():
        debug("connecting to %s", url)

    websocket = create_connection(url)
    websocket.settimeout(10)

    if is_debug_enabled():
        debug("sent %s", json.dumps(token_obj))

    websocket.send(json.dumps(token_obj))
    return websocket


def connect_job(job_id,
                deployment_name,
                token_manager=None,
                app_url=defaults.APP_URL,
                persist=False,
                websocket=None,
                data_url=None):
    """
    connect to a running Juttle program by job_id

    """

    if data_url == None:
        data_url = get_data_url_for_job(job_id,
                                        deployment_name,
                                        token_manager=token_manager,
                                        app_url=app_url)

    if websocket == None:
        websocket = __wss_connect(data_url,
                                  token_manager,
                                  job_id=job_id)

    pong = json.dumps({
        'pong': True
    })

    if not persist:
        job_finished = False

        while not job_finished:
            try:
                data = websocket.recv()

                if data:
                    payload = json.loads(data)

                    if is_debug_enabled():
                        printable_payload = dict(payload)
                        if 'points' in payload:
                            # don't want to print out all the outputs when in
                            # debug mode
                            del printable_payload['points']
                            printable_payload['points'] = 'NOT SHOWN'

                        debug('received %s' % json.dumps(printable_payload))

                    if 'ping' in payload.keys():
                        # ping/pong (ie heartbeat) mechanism
                        websocket.send(pong)

                        if is_debug_enabled():
                            debug('sent %s' % json.dumps(pong))

                    if 'job_end' in payload.keys() and payload['job_end'] == True:
                        job_finished = True

                    if token_manager.is_access_token_expired():
                        debug('refreshing access token')
                        token_obj = {
                            "accessToken": token_manager.get_access_token()
                        }
                        # refresh authentication token
                        websocket.send(json.dumps(token_obj))

                    if 'error' in payload:
                        if payload['error'] == 'NONEXISTENT-JOB':
                            raise JutException('Job "%s" no longer running' % job_id)

                    # return all channel messages
                    yield payload

                else:
                    debug('payload was "%s", forcing websocket reconnect' % data)
                    raise IOError()

            except IOError:
                if is_debug_enabled():
                    traceback.print_exc()
                #
                # We'll retry for just under 30s since internally we stop
                # running non persistent programs after 30s of not heartbeating
                # with the client
                #
                retry = 1
                while retry <= 5:
                    try:
                        debug('network error reconnecting to job %s, '
                              'try %s of 5' % (job_id, retry))
                        websocket = __wss_connect(data_url, token_manager, job_id=job_id)
                        break

                    except socket.error:

                        if is_debug_enabled():
                            traceback.print_exc()

                        retry += 1
                        time.sleep(5)

                debug('network error reconnecting to job %s, '
                      'try %s of 5' % (job_id, retry))
                websocket = __wss_connect(data_url, token_manager, job_id=job_id)

    websocket.close()


def run(juttle,
        deployment_name,
        program_name=None,
        persist=False,
        token_manager=None,
        app_url=defaults.APP_URL):
    """
    run a juttle program through the juttle streaming API and return the
    various events that are part of running a Juttle program which include:

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
    token_manager: auth.TokenManager object
    app_url: optional argument used primarily for internal Jut testing
    """
    headers = token_manager.get_access_token_headers()

    data_url = get_juttle_data_url(deployment_name,
                                   app_url=app_url,
                                   token_manager=token_manager)

    websocket = __wss_connect(data_url, token_manager)

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
    # yield job_info so the caller to this method can figure out which sinks
    # correlate to which flowgraphs
    yield job_info
    job_id = job_info['job']['id']

    if is_debug_enabled():
        debug('started job %s', json.dumps(job_info))

    for data in connect_job(job_id,
                            deployment_name,
                            token_manager=token_manager,
                            app_url=app_url,
                            persist=persist,
                            websocket=websocket,
                            data_url=data_url):
        yield data


def get_jobs(deployment_name,
             token_manager=None,
             app_url=defaults.APP_URL):
    """
    return list of currently running jobs

    """
    headers = token_manager.get_access_token_headers()
    data_urls = get_data_urls(deployment_name,
                              app_url=app_url,
                              token_manager=token_manager)

    jobs = []

    for data_url in data_urls:
        url = '%s/api/v1/jobs' % data_url
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            # saving the data_url for the specific job so you know where to
            # connect if you want to interact with that job
            these_jobs = response.json()['jobs']

            for job in these_jobs:
                job['data_url'] = data_url

            jobs += these_jobs
        else:
            raise JutException('Error %s: %s' % (response.status_code, response.text))

    return jobs


def get_job_details(job_id,
                    deployment_name,
                    token_manager=None,
                    app_url=defaults.APP_URL):
    """
    return job details for a specific job id

    """

    jobs = get_jobs(deployment_name,
                    token_manager=token_manager,
                    app_url=app_url)

    for job in jobs:
        if job['id'] == job_id:
            return job

    raise JutException('Unable to find job with id "%s"' % job_id)


def delete_job(job_id,
               deployment_name,
               token_manager=None,
               app_url=defaults.APP_URL):
    """
    delete a job with a specific job id

    """
    headers = token_manager.get_access_token_headers()
    data_url = get_data_url_for_job(job_id,
                                    deployment_name,
                                    token_manager=token_manager,
                                    app_url=app_url)

    url = '%s/api/v1/jobs/%s' % (data_url, job_id)
    response = requests.delete(url, headers=headers)

    if response.status_code != 200:
        raise JutException('Error %s: %s' % (response.status_code, response.text))


