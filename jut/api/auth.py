"""
jut auth API

"""

import requests
import json
import time

from jut import defaults
from jut.api import environment
from jut.exceptions import JutException
from jut.common import debug, is_debug_enabled


class TokenManager(object):
    """
    jut authentication token manager which handles the refreshing of auth
    tokens as well as caching of valid authentication tokens
    """

    def __init__(self,
                 username=None,
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
        self.username = username
        self.password = password
        self.client_id = client_id
        self.client_secret = client_secret
        self.app_url = app_url

        self.access_token = None
        self.expires_at = 0

    def is_access_token_expired(self):
        """
        check if the current access token is expired or not

        """
        return self.access_token == None or self.expires_at < time.time()

    def get_access_token(self):
        """
        get a valid access token

        """
        if self.is_access_token_expired():

            if is_debug_enabled():
                debug('requesting new access_token')

            token = get_access_token(username=self.username,
                                     password=self.password,
                                     client_id=self.client_id,
                                     client_secret=self.client_secret,
                                     app_url=self.app_url)

            # lets make sure to refresh before we're halfway to expiring
            self.expires_at = time.time() + token['expires_in']/2
            self.access_token = token['access_token']

        return self.access_token


    def get_access_token_headers(self):
        """
        return the access token header

        """
        return {
            'Authorization': 'Bearer %s' % self.get_access_token(),
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }


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
            raise JutException('Failed /local check %s: %s' %
                               (response.status_code, response.text))

        response = sess.get(auth_url + '/status')
        if response.status_code != 200:
            raise JutException('Failed /status check %s: %s' %
                               (response.status_code, response.text))

        if not response.json()['authorized']:
            raise JutException('Failed authentication with (%s,%s), got %s' %
                               (username, password, response.text))

        response = sess.post(auth_url + '/token',
                             data={'grant_type': 'client_credentials'})

    if response.status_code != 200:
        raise JutException('Unable to get auth token %s: %s' %
                           (response.status_code, response.text))

    return response.json()

