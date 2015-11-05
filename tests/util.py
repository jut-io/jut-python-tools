"""
testing utilities

"""

import os
import select
import subprocess
import tempfile
import time

from contextlib import contextmanager

from jut import config

from jut.api import accounts, auth, data_engine, deployments
from jut.common import info, error


# data service only knows about space changes every 30s
SPACE_CREATE_TIMEOUT = 30

@contextmanager
def temp_jut_tools_home():
    """
    context manager to allow unit tests to switch the jut tools home and
    therefore not collide with each other or existing jut-tools configurations

    Usage:
        with temp_jut_tools_home():
            # do your thing

    """
    home_override = os.environ.get('HOME_OVERRIDE')
    try:
        new_home = os.path.abspath(tempfile.mkdtemp())
        os.environ['HOME_OVERRIDE'] = new_home
        yield new_home
    finally:
        os.environ['HOME_OVERRIDE'] = home_override

def get_test_user_pass():
    return os.environ.get('JUT_USER'), os.environ.get('JUT_PASS')


def get_test_app_url():
    return os.environ.get('JUT_APP_URL')


class Spawn(object):
    """
    expect like spawn class that has a limited but useful expect like functionality

    """

    def __init__(self, process):
        self.process = process


    def expect_output_eof(self):
        """
        expect the stdout to be closed

        """
        line = self.process.stdout.read()

        if line != '':
            raise Exception('Expected eof on stdout but got "%s"' % line)

    def expect_error_eof(self):
        """
        expect the stderr to be closed

        """
        line = self.process.stderr.read()

        if line != '':
            raise Exception('Expected eof on stderr but got "%s"' % line)


    def expect_eof(self):
        """
        expect eof from stdout and stderr

        """
        self.expect_output_eof()
        self.expect_error_eof()


    def expect_output(self, message):
        """
        expect the stdout contains the following message in its output before
        proceeding

        """
        # use select to timeout when there is no output
        read_ready, _, _ = select.select([self.process.stdout.fileno()], [], [], 5)

        if read_ready:
            length = len(message)
            line = self.process.stdout.read(length)

            if message == line:
                return

            info(self.read_output())
            error(self.read_error())
            raise Exception('Expected "%s" got "%s"' % (message, line))
        else:
            info(self.read_output())
            error(self.read_error())
            raise Exception('Expected "%s" got nothing' % message)


    def expect_error(self, message):
        """
        expect the stderr contains the following message in its output before
        proceeding

        """

        # use select to timeout when there is no output
        read_ready, _, _ = select.select([self.process.stderr.fileno()], [], [], 5)

        if read_ready:
            length = len(message)
            line = self.process.stderr.read(length)

            if message == line:
                return

            info(self.read_output())
            error(self.read_error())
            raise Exception('Expected "%s" got "%s"' % (message, line))
        else:
            info(self.read_output())
            error(self.read_error())
            raise Exception('Expected "%s" got nothing' % message)


    def read_output(self):
        """
        read and return the whole stdout output

        """

        data = None
        result = ''
        while data != '':
            data = self.process.stdout.read()
            result += data

        return result

    def read_error(self):
        """
        read and return the whole stderr output

        """

        data = None
        result = ''
        while data != '':
            data = self.process.stderr.read()
            result += data

        return result


    def send(self, message):
        """
        send the exact message to the stdin of the running process

        """
        self.process.stdin.write(message)
        self.process.stdin.flush()


    def wait(self):
        """
        wait for the process to complete and return the exit status code

        """
        return self.process.wait()


    def status(self):
        """
        return the exit status code for the process

        """
        return self.process.wait()


    def expect_status(self, expected_status):
        """
        expect the provided status exit code otherwise output the full stdout
        and stderr output at that specific point in time

        """
        status = self.wait()

        if status != expected_status:
            info(self.read_output())
            error(self.read_error())
            raise Exception('Expected status %s, got %s' % (expected_status, status))


    def send_signal(self, signal_name):
        """
        send the signal provided to the currently running process

        """

        self.process.send_signal(signal_name)

def jut(*args,
        **kwargs):
    """
    FOR TESTING ONLY:

    used to spawn jut tools command line invocation from the source directly
    and interact with that same command through expect like mechanism
    """

    if 'stdin' in kwargs:
        stdin = kwargs['stdin']
    else:
        stdin = subprocess.PIPE

    jut_cmd = ['python', 'jut/cli.py'] + list(args)
    return Spawn(subprocess.Popen(jut_cmd,
                                  stdin=stdin,
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE))


def create_user_in_default_deployment(name, username, email, password):
    """
    """
    configuration = config.get_default()
    app_url = configuration['app_url']
    deployment_name = configuration['deployment_name']
    client_id = configuration['client_id']
    client_secret = configuration['client_secret']

    token_manager = auth.TokenManager(client_id=client_id,
                                      client_secret=client_secret,
                                      app_url=app_url)

    delete_user_from_default_deployment(username, password)

    accounts.create_user(name,
                         username,
                         email,
                         password,
                         token_manager=token_manager,
                         app_url=app_url)

    deployments.add_user(username,
                         deployment_name,
                         token_manager=token_manager,
                         app_url=app_url)


def delete_user_from_default_deployment(username, password):
    """
    """

    configuration = config.get_default()
    app_url = configuration['app_url']
    client_id = configuration['client_id']
    client_secret = configuration['client_secret']

    token_manager = auth.TokenManager(client_id=client_id,
                                      client_secret=client_secret,
                                      app_url=app_url)

    if accounts.user_exists(username,
                            token_manager=token_manager,
                            app_url=app_url):

        delete_token_manager = auth.TokenManager(username=username,
                                                 password=password,
                                                 app_url=app_url)

        accounts.delete_user(username,
                             token_manager=delete_token_manager,
                             app_url=app_url)


def get_webhook_url(space):
    """

    """

    configuration = config.get_default()
    deployment_name = configuration['deployment_name']
    app_url = configuration['app_url']

    client_id = configuration['client_id']
    client_secret = configuration['client_secret']

    token_manager = auth.TokenManager(client_id=client_id,
                                      client_secret=client_secret,
                                      app_url=app_url)

    import_url = data_engine.get_import_data_url(deployment_name,
                                                 token_manager=token_manager,
                                                 app_url=app_url)

    api_key = deployments.get_apikey(deployment_name,
                                     token_manager=token_manager,
                                     app_url=app_url)

    return '%s/api/v1/import/webhook/?space=%s&data_source=webhook&apikey=%s' % \
           (import_url, space, api_key)


def create_space_in_default_deployment(space_name):
    configuration = config.get_default()
    deployment_name = configuration['deployment_name']
    app_url = configuration['app_url']

    client_id = configuration['client_id']
    client_secret = configuration['client_secret']

    token_manager = auth.TokenManager(client_id=client_id,
                                      client_secret=client_secret,
                                      app_url=app_url)

    if deployments.space_exists(deployment_name,
                                space_name,
                                token_manager=token_manager,
                                app_url=app_url):
        delete_space_from_default_deployment(space_name)

    deployments.create_space(deployment_name,
                             space_name,
                             token_manager=token_manager,
                             app_url=app_url)

    time.sleep(SPACE_CREATE_TIMEOUT)


def delete_space_from_default_deployment(space_name):
    configuration = config.get_default()
    deployment_name = configuration['deployment_name']
    app_url = configuration['app_url']

    client_id = configuration['client_id']
    client_secret = configuration['client_secret']

    token_manager = auth.TokenManager(client_id=client_id,
                                      client_secret=client_secret,
                                      app_url=app_url)

    deployments.delete_space(deployment_name,
                             space_name,
                             token_manager=token_manager,
                             app_url=app_url)


