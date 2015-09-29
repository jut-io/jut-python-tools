"""
jut authorizations API

"""

import requests

from jut import defaults
from jut.api import auth, environment


def get_authorization(access_token,
                      app_url=defaults.APP_URL):
    """
    returns the authorization grant composed of the tuple client_id and
    client_secret provided with a valid access token

    access_token: valid access toke obtained using auth.get_access_token
    app_url: optional argument used primarily for internal Jut testing
    """
    auth_url = environment.get_auth_url(app_url=app_url)
    url = '%s/api/v1/authorizations' % auth_url

    headers = auth.access_token_to_headers(access_token)
    response = requests.post(url,
                             headers=headers)

    if response.status_code == 201:
        authorization = response.json()
        return (authorization['client_id'], authorization['client_secret'])

    else:
        raise Exception('Error Auth %s: %s' % (response.status_code, response.text))
