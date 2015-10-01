"""
testing utilities

"""

import subprocess
import time

from jut.api import accounts, auth, data_engine, deployments, environment
from jut.common import info, error
from jut import config

DEFAULT_TEST_USERNAME = 'jut-tools-user'

# data service only knows about space changes every 30s
SPACE_CREATE_TIMEOUT = 30

def jut(*args,
        **kwargs):
    """
    calls the jut/cli.py code and returns the exact stdout, stdin as lists of
    lines that were written to each output

    """
    stdout = []
    stderr = []

    process = subprocess.Popen(['python', 'jut/cli.py'] + list(args),
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()

    if 'exit_code' in kwargs:
        exit_code = kwargs['exit_code']
    else:
        exit_code = 0

    if process.wait() != exit_code:
        error('Expected return code %s, got %s', exit_code, process.wait())
        info(stdout)
        error(stderr)

        raise Exception('Failure runing jut command')

    return stdout, stderr


def create_user_in_default_deployment(name, username, email, password):
    """
    """
    configuration = config.get_default()
    app_url = configuration['app_url']
    deployment_name = configuration['deployment_name']
    client_id = configuration['client_id']
    client_secret = configuration['client_secret']

    access_token = auth.get_access_token(client_id=client_id,
                                         client_secret=client_secret,
                                         app_url=app_url)

    delete_user_from_default_deployment(username, password)

    account_details = accounts.create_user(name,
                                           username,
                                           email,
                                           password,
                                           access_token=access_token,
                                           app_url=app_url)

    deployments.add_user(account_details['id'],
                         deployment_name,
                         access_token=access_token,
                         app_url=app_url)


def delete_user_from_default_deployment(username, password):
    """
    """

    configuration = config.get_default()
    app_url = configuration['app_url']
    client_id = configuration['client_id']
    client_secret = configuration['client_secret']

    access_token = auth.get_access_token(client_id=client_id,
                                         client_secret=client_secret,
                                         app_url=app_url)

    if accounts.user_exists(username,
                            access_token=access_token,
                            app_url=app_url):

        delete_access_token = auth.get_access_token(username=username,
                                                    password=password,
                                                    app_url=app_url)

        account_id = accounts.get_account_id(username,
                                             access_token=access_token,
                                             app_url=app_url)

        accounts.delete_user(account_id,
                             access_token=delete_access_token,
                             app_url=app_url)


def get_webhook_url(space):
    """

    """

    configuration = config.get_default()
    deployment_name = configuration['deployment_name']
    app_url = configuration['app_url']

    client_id = configuration['client_id']
    client_secret = configuration['client_secret']

    access_token = auth.get_access_token(client_id=client_id,
                                         client_secret=client_secret,
                                         app_url=app_url)

    import_url = data_engine.get_import_data_url(deployment_name,
                                                 access_token=access_token,
                                                 app_url=app_url)

    api_key = deployments.get_apikey(deployment_name,
                                     access_token=access_token,
                                     app_url=app_url)

    return '%s/api/v1/import/webhook/?space=%s&data_source=webhook&apikey=%s' % \
           (import_url, space, api_key)


def create_space_in_default_deployment(space_name):
    configuration = config.get_default()
    deployment_name = configuration['deployment_name']
    app_url = configuration['app_url']

    client_id = configuration['client_id']
    client_secret = configuration['client_secret']

    access_token = auth.get_access_token(client_id=client_id,
                                         client_secret=client_secret,
                                         app_url=app_url)

    if deployments.space_exists(deployment_name,
                                space_name,
                                access_token=access_token,
                                app_url=app_url):
        delete_space_from_default_deployment(space_name)

    deployments.create_space(deployment_name,
                             space_name,
                             access_token=access_token,
                             app_url=app_url)

    time.sleep(SPACE_CREATE_TIMEOUT)


def delete_space_from_default_deployment(space_name):
    configuration = config.get_default()
    deployment_name = configuration['deployment_name']
    app_url = configuration['app_url']

    client_id = configuration['client_id']
    client_secret = configuration['client_secret']

    access_token = auth.get_access_token(client_id=client_id,
                                         client_secret=client_secret,
                                         app_url=app_url)

    deployments.delete_space(deployment_name,
                             space_name,
                             access_token=access_token,
                             app_url=app_url)

