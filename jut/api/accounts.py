"""
jut users API
"""

import requests
import json

from jut import defaults
from jut.api import auth, environment
from jut.exceptions import JutException


def create_user(name,
                username,
                email,
                password,
                access_token=None,
                app_url=defaults.APP_URL):
    """
    create a new user with the specified name, username email and password

    """
    headers = auth.access_token_to_headers(access_token)
    auth_url = environment.get_auth_url(app_url=app_url)
    url = "%s/api/v1/accounts" % auth_url

    payload = {
        'name': name,
        'username': username,
        'email': email,
        'password': password
    }

    response = requests.post(url,
                             data=json.dumps(payload),
                             headers=headers)

    if response.status_code == 201:
        return response.json()

    else:
        raise JutException('Error %s: %s' % (response.status_code, response.text))


def delete_user(username,
                access_token=None,
                app_url=defaults.APP_URL):
    """
    delete a user by its account_id and with the access_token from that same
    user as only a user may delete him/her-self

    """
    account_id = get_account_id(username,
                                access_token=access_token,
                                app_url=app_url)

    headers = auth.access_token_to_headers(access_token)
    auth_url = environment.get_auth_url(app_url=app_url)
    url = "%s/api/v1/accounts/%s" % (auth_url, account_id)
    response = requests.delete(url, headers=headers)

    if response.status_code == 204:
        return response.text

    else:
        raise JutException('Error %s; %s' % (response.status_code, response.text))


def get_account_id(username,
                   access_token=None,
                   app_url=defaults.APP_URL):
    """
    get the account id for the username specified

    """
    headers = auth.access_token_to_headers(access_token)
    auth_url = environment.get_auth_url(app_url=app_url)
    url = "%s/api/v1/accounts?username=%s" % (auth_url, username)

    response = requests.get(url,
                            headers=headers)

    if response.status_code == 200:
        return response.json()['id']

    else:
        raise JutException('Error %s; %s' % (response.status_code, response.text))


def get_logged_in_account_id(access_token=None,
                             app_url=defaults.APP_URL):
    """
    get the account id for logged in account of the provided access_token

    """
    headers = auth.access_token_to_headers(access_token)
    auth_url = environment.get_auth_url(app_url=app_url)
    url = "%s/api/v1/account" % auth_url

    response = requests.get(url,
                            headers=headers)

    if response.status_code == 200:
        return response.json()['id']

    else:
        raise JutException('Error %s; %s' % (response.status_code, response.text))



def user_exists(username,
                access_token=None,
                app_url=defaults.APP_URL):
    """
    check if the user exists with the specified username

    """
    headers = auth.access_token_to_headers(access_token)
    auth_url = environment.get_auth_url(app_url=app_url)
    url = "%s/api/v1/accounts?username=%s" % (auth_url, username)
    response = requests.get(url, headers=headers)

    if response.status_code == 404:
        return False
    elif response.status_code == 200:
        return True
    else:
        raise JutException('Error %s: %s' % (response.status_code, response.text))


def get_accounts(account_ids,
                 access_token=None,
                 app_url=defaults.APP_URL):
    """
    get the account details for each of the account ids in the account_ids list

    """
    headers = auth.access_token_to_headers(access_token)
    auth_url = environment.get_auth_url(app_url=app_url)

    url = "%s/api/v1/accounts/%s" % (auth_url, ','.join(account_ids))

    response = requests.get(url,
                            headers=headers)

    if response.status_code == 200:
        return response.json()

    else:
        raise JutException('Error %s; %s' % (response.status_code, response.text))


