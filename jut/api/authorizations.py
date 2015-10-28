"""
jut authorizations API

"""

import requests

from jut import defaults
from jut.api import environment
from jut.exceptions import JutException


def get_authorization(token_manager,
                      app_url=defaults.APP_URL):
    """
    returns the authorization grant

    """
    auth_url = environment.get_auth_url(app_url=app_url)
    url = '%s/api/v1/authorizations' % auth_url

    headers = token_manager.get_access_token_headers()
    response = requests.post(url,
                             headers=headers)

    if response.status_code == 201:
        return response.json()

    else:
        raise JutException('Error Auth %s: %s' % (response.status_code, response.text))

