"""
deployments API

"""

import json
import requests

from jut import defaults

from jut.api import accounts, environment
from jut.exceptions import JutException

## deployments

def create_deployment(deployment_name,
                      token_manager=None,
                      app_url=defaults.APP_URL):
    """
    create a deployment with the specified name

    """
    headers = token_manager.get_access_token_headers()

    payload = {
        'name': deployment_name,
        'isAdmin': True
    }

    deployment_url = environment.get_deployment_url(app_url=app_url)
    response = requests.post('%s/api/v1/deployments' % deployment_url,
                             data=json.dumps(payload),
                             headers=headers)

    if response.status_code == 201:
        return response.json()

    else:
        raise JutException('Error %s: %s' % (response.status_code, response.text))


def get_deployments(token_manager=None,
                    app_url=defaults.APP_URL):
    """
    return the list of deployments that the current access_token gives you
    access to

    """
    headers = token_manager.get_access_token_headers()
    deployment_url = environment.get_deployment_url(app_url=app_url)
    response = requests.get('%s/api/v1/deployments' % deployment_url,
                            headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        raise JutException('Error %s: %s' % (response.status_code, response.text))


def get_deployment_id(deployment_name,
                      token_manager=None,
                      app_url=defaults.APP_URL):
    """
    return the deployment id for the deployment with the specified name

    """

    headers = token_manager.get_access_token_headers()
    deployment_url = environment.get_deployment_url(app_url=app_url)
    response = requests.get('%s/api/v1/deployments' % deployment_url,
                            headers=headers)

    if response.status_code == 200:
        deployments = response.json()

        for deployment in deployments:
            if deployment['name'] == deployment_name:
                return deployment['deployment_id']

        raise JutException('Unable to find deployment with name %s' % deployment_name)
    else:
        raise JutException('Error %s: %s' % (response.status_code, response.text))


def get_deployment_details(deployment_name,
                           token_manager=None,
                           app_url=defaults.APP_URL):
    """
    return the deployment details for the deployment with the specific name

    """

    deployment_id = get_deployment_id(deployment_name,
                                      token_manager=token_manager,
                                      app_url=app_url)

    headers = token_manager.get_access_token_headers()
    deployment_url = environment.get_deployment_url(app_url=app_url)
    response = requests.get('%s/api/v1/deployments/%s' %
                            (deployment_url, deployment_id),
                            headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        raise JutException('Error %s: %s' % (response.status_code, response.text))


def get_apikey(deployment_name,
               token_manager=None,
               app_url=defaults.APP_URL):
    deployment_id = get_deployment_id(deployment_name,
                                      token_manager=token_manager,
                                      app_url=app_url)

    headers = token_manager.get_access_token_headers()
    deployment_url = environment.get_deployment_url(app_url=app_url)
    response = requests.get('%s/api/v1/deployments/%s/apikey' %
                            (deployment_url, deployment_id),
                            headers=headers)

    if response.status_code == 200:
        return response.json()['apikey']
    else:
        raise JutException('Error %s: %s' % (response.status_code, response.text))


# spaces

def get_spaces(deployment_name,
               token_manager=None,
               app_url=defaults.APP_URL):
    """
    get the list of spaces currently in the deployment specified

    """
    deployment_id = get_deployment_id(deployment_name,
                                      token_manager=token_manager,
                                      app_url=app_url)

    headers = token_manager.get_access_token_headers()
    deployment_url = environment.get_deployment_url(app_url=app_url)
    response = requests.get('%s/api/v1/deployments/%s/spaces' %
                            (deployment_url, deployment_id),
                            headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        raise JutException('Error %s: %s' % (response.status_code, response.text))


def get_space_id(deployment_name,
                 space_name,
                 token_manager=None,
                 app_url=defaults.APP_URL):
    """
    get the space id that relates to the space name provided

    """
    spaces = get_spaces(deployment_name,
                        token_manager=token_manager,
                        app_url=app_url)

    for space in spaces:
        if space['name'] == space_name:
            return space['id']

    raise JutException('Unable to find space "%s" within deployment "%s"' %
                    (space_name, deployment_name))


def create_space(deployment_name,
                 space_name,
                 security_policy='public',
                 events_retention_days=0,
                 metrics_retention_days=0,
                 token_manager=None,
                 app_url=defaults.APP_URL):
    """
    create a space within the deployment specified and with the various
    rentention values set

    """
    deployment_id = get_deployment_id(deployment_name,
                                      token_manager=token_manager,
                                      app_url=app_url)

    payload = {
        'name': space_name,
        'security_policy': security_policy,
        'events_retention_days': events_retention_days,
        'metrics_retention_days': metrics_retention_days,
    }

    headers = token_manager.get_access_token_headers()
    deployment_url = environment.get_deployment_url(app_url=app_url)
    response = requests.post('%s/api/v1/deployments/%s/spaces' %
                             (deployment_url, deployment_id),
                             data=json.dumps(payload),
                             headers=headers)

    if response.status_code == 201:
        return response.json()
    else:
        raise JutException('Error %s: %s' % (response.status_code, response.text))


def delete_space(deployment_name,
                 space_name,
                 token_manager=None,
                 app_url=defaults.APP_URL):

    deployment_id = get_deployment_id(deployment_name,
                                      token_manager=token_manager,
                                      app_url=app_url)

    space_id = get_space_id(deployment_name,
                            space_name,
                            token_manager=token_manager,
                            app_url=app_url)

    headers = token_manager.get_access_token_headers()
    deployment_url = environment.get_deployment_url(app_url=app_url)
    response = requests.delete('%s/api/v1/deployments/%s/spaces/%s' %
                               (deployment_url, deployment_id, space_id),
                               headers=headers)

    if response.status_code == 204:
        return response.text
    else:
        raise JutException('Error %s: %s' % (response.status_code, response.text))


def space_exists(deployment_name,
                 space_name,
                 token_manager=None,
                 app_url=defaults.APP_URL):

    spaces = get_spaces(deployment_name,
                        token_manager=token_manager,
                        app_url=app_url)

    for space in spaces:
        if space['name'] == space_name:
            return True

    return False


# users

def get_users(deployment_name,
              token_manager=None,
              app_url=defaults.APP_URL):
    """
    get all users in the deployment specified

    """
    deployment_id = get_deployment_id(deployment_name,
                                      token_manager=token_manager,
                                      app_url=app_url)

    headers = token_manager.get_access_token_headers()
    deployment_url = environment.get_deployment_url(app_url=app_url)
    response = requests.get('%s/api/v1/deployments/%s/accounts' %
                            (deployment_url, deployment_id),
                            headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        raise JutException('Error %s: %s' % (response.status_code, response.text))


def add_user(username,
             deployment_name,
             token_manager=None,
             app_url=defaults.APP_URL):
    """
    add user to deployment

    """
    deployment_id = get_deployment_id(deployment_name,
                                      token_manager=token_manager,
                                      app_url=app_url)

    account_id = accounts.get_account_id(username,
                                         token_manager=token_manager,
                                         app_url=app_url)

    headers = token_manager.get_access_token_headers()
    deployment_url = environment.get_deployment_url(app_url=app_url)
    response = requests.put('%s/api/v1/deployments/%s/accounts/%s' %
                            (deployment_url, deployment_id, account_id),
                            headers=headers)

    if response.status_code == 204:
        return response.text
    else:
        raise JutException('Error %s: %s' % (response.status_code, response.text))

