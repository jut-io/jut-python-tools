"""
environment details API

NOT OFFICIAL API
"""

import memoized
import requests

from jut import defaults

@memoized.memoized
def get_details(app_url=defaults.APP_URL):
    """
    returns environment details for the app url specified

    """
    url = '%s/environment' % app_url
    response = requests.get(url)

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception('Unable to retrieve environment details from %s, got %s: %s' %
                        (url, response.status_code, response.text))


def get_auth_url(app_url=defaults.APP_URL):
    """
    return the auth url associated with the app url provided

    """
    return get_details(app_url=app_url)['auth_url']


def get_deployment_url(app_url=defaults.APP_URL):
    """
    return the deployment url associated with the app url provided

    """
    return get_details(app_url=app_url)['deployment_url']


