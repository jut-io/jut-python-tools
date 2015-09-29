"""
jut auth API

"""

import requests
import json

from jut import defaults
from jut.api import environment

def get_access_token(username=None,
                     password=None,
                     client_id=None,
                     client_secret=None,
                     app_url=defaults.APP_URL):
    """
    get the access token (http://docs.jut.io/api-guide/#unique_171637733),
    by either using the direct username, password combination or better yet by
    using the authorization grant you generated on jut with the client_id,
    client_secret combination

    auth_url: auth url for the jut application (defaults to production)

    Use either two of the following to authenticate:

    username: username used to login to Jut
    password: password used to login to Jut
    client_id: client_id generated through the Jut application or using the
               authorizations API
    client_secret: client_secret generated through the Jut appliation or using
                   the authorizations API
    """
    sess = requests.Session()
    auth_url = environment.get_auth_url(app_url=app_url)

    if client_id != None:
        headers = {
            'content-type': 'application/json'
        }
        response = sess.post(auth_url + "/token",
                             headers=headers,
                             data=json.dumps({
                                 'grant_type': 'client_credentials',
                                 'client_id': client_id,
                                 'client_secret': client_secret
                             }))
    else:
        form = {
            'username': username,
            'password': password
        }

        response = sess.post('%s/local' % auth_url, data=form)

        if response.status_code != 200:
            raise Exception('Failed /local check %s: %s' %
                            (response.status_code, response.text))

        response = sess.get(auth_url + '/status')
        if response.status_code != 200:
            raise Exception('Failed /status check %s: %s' %
                            (response.status_code, response.text))

        if not response.json()['authorized']:
            raise Exception('Failed authentication with (%s,%s), got %s' %
                            (username, password, response.text))

        response = sess.post(auth_url + '/token',
                             data={'grant_type': 'client_credentials'})

    if response.status_code != 200:
        raise Exception('Unable to get auth token %s: %s' %
                        (response.status_code, response.text))

    return response.json()


def access_token_to_headers(access_token):
    """
    return the necessary headers to interact with various Jut APIs with a valid
    access token

    access_token: the access token can be obtained with the auth.get_auth_token
                  method
    """

    if access_token == None:
        raise Exception('You must supply a valid access_token')

    if access_token['token_type'] == 'Bearer':
        return {
            'Authorization': 'Bearer %s' % access_token['access_token'],
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
    else:
        raise Exception('Token not supported %s' % access_token)


