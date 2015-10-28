"""
basic set of `jut config` tests

"""

import os
import unittest

from tests.util import jut, \
                       temp_jut_tools_home, \
                       create_user_in_default_deployment, \
                       delete_user_from_default_deployment

from jut import config, defaults

NO_CONFIG_MESSAGE = 'No configurations available, please run: `jut config add`\n'

def confline(index, username, app_url, default=False):
    """
    construct the configuration line as produced by `jut config list`

    """
    if default:
        if app_url == defaults.APP_URL:
            return ' %d: %s (default)\n' % (index, username)
        else:
            return ' %d: %s@%s (default)\n' % (index, username, app_url)
    else:
        if app_url == defaults.APP_URL:
            return ' %d: %s\n' % (index, username)
        else:
            return ' %d: %s@%s\n' % (index, username, app_url)


class JutConfigTests(unittest.TestCase):


    @classmethod
    def setUpClass(cls):
        create_user_in_default_deployment('Jut Tools User #1',
                                          'jut-tools-user01',
                                          'jut-tools-user01@jut.io',
                                          'bigdata')

        create_user_in_default_deployment('Jut Tools User #2',
                                          'jut-tools-user02',
                                          'jut-tools-user02@jut.io',
                                          'bigdata')



    def test_negative_config_defaults(self):
        """
        when calling `jut config defaults` if you haven't configured yet we
        should fail correctly and print the appropriate message

        """
        with temp_jut_tools_home():
            process = jut('config', 'defaults')
            process.expect_error(NO_CONFIG_MESSAGE)
            process.expect_status(255)
            process.expect_eof()


    def test_negative_config_list(self):
        """
        when calling `jut config list` if you haven't configured yet we
        should fail correctly and print the appropriate message

        """
        with temp_jut_tools_home():
            process = jut('config', 'list')
            process.expect_error(NO_CONFIG_MESSAGE)
            process.expect_status(255)
            process.expect_eof()


    def test_config_list(self):
        """
        list the saved configuration and verify it only contains the single
        test account with JUT_USER used by the jut unittests

        """
        jut_user = os.environ.get('JUT_USER')

        configuration = config.get_default()
        app_url = configuration['app_url']

        process = jut('config', 'list')
        process.expect_status(0)
        process.expect_output('Available jut configurations:\n')
        process.expect_output(confline(1, jut_user, app_url, default=True))
        process.expect_eof()


    def test_config_add_interactive(self):
        """
        verify that you can add a user interactively using `jut config add`

        """

        with temp_jut_tools_home():
            configuration = config.get_default()
            app_url = configuration['app_url']

            # -s because getpass reads from the tty and screws up automated testing
            process = jut('config',
                          'add',
                          '-a', app_url,
                          '-s')

            process.expect_output('Username: ')
            process.send('jut-tools-user01\n')
            process.expect_output('Password: ')
            process.send('bigdata\n')
            process.expect_status(0)

            # check the `jut config list` shows the right output
            process = jut('config', 'list')
            process.expect_status(0)
            process.expect_output('Available jut configurations:\n')
            process.expect_output(confline(1, 'jut-tools-user01', app_url, default=True))
            process.expect_eof()


    def test_config_add_non_interactive(self):
        """
        add a few tests accounts to the default configuration and then add
        those configurations to the current jut tools config

        """
        with temp_jut_tools_home():
            configuration = config.get_default()
            app_url = configuration['app_url']

            process = jut('config',
                          'add',
                          '-u', 'jut-tools-user01',
                          '-p', 'bigdata',
                          '-a', app_url)
            process.expect_status(0)

            process = jut('config', 'list')
            process.expect_status(0)
            process.expect_output('Available jut configurations:\n')
            process.expect_output(confline(1, 'jut-tools-user01', app_url, default=True))
            process.expect_eof()


    def test_config_defaults_interactive(self):
        """
        verify you can interactively modify the config default

        """

        with temp_jut_tools_home() as home_dir:
            jut_user = os.environ.get('JUT_USER')
            jut_pass = os.environ.get('JUT_PASS')
            configuration = config.get_default()
            app_url = configuration['app_url']

            process = jut('config',
                          'add',
                          '-u', jut_user,
                          '-p', jut_pass,
                          '-a', app_url)
            process.expect_status(0)

            process = jut('config',
                          'add',
                          '-u', 'jut-tools-user01',
                          '-p', 'bigdata',
                          '-a', app_url)
            process.expect_status(0)

            process = jut('config', 'list')
            process.expect_status(0)
            process.expect_output('Available jut configurations:\n')
            process.expect_output(confline(1, jut_user, app_url, default=True))
            process.expect_output(confline(2, 'jut-tools-user01', app_url, default=False))

            process = jut('config',
                          'defaults')

            process.expect_output('Available jut configurations:\n')
            process.expect_output(confline(1, jut_user, app_url, default=True))
            process.expect_output(confline(2, 'jut-tools-user01', app_url, default=False))
            process.expect_output('Set default configuration to: ')
            process.send('2\n')
            process.expect_output('Configuration updated at %s\n' % home_dir)
            process.expect_status(0)
            process.expect_eof()

            process = jut('config', 'list')
            process.expect_status(0)
            process.expect_output('Available jut configurations:\n')
            process.expect_output(confline(1, jut_user, app_url, default=False))
            process.expect_output(confline(2, 'jut-tools-user01', app_url, default=True))
            process.expect_eof()


    def test_config_defaults_non_interactive(self):
        """
        see that you can easily change the default configuration in use
        and that it switches back once you delete the default configuration

        """

        with temp_jut_tools_home() as home_dir:
            jut_user = os.environ.get('JUT_USER')
            jut_pass = os.environ.get('JUT_PASS')
            configuration = config.get_default()
            app_url = configuration['app_url']

            process = jut('config',
                          'add',
                          '-u', jut_user,
                          '-p', jut_pass,
                          '-a', app_url)
            process.expect_status(0)

            process = jut('config',
                          'add',
                          '-u', 'jut-tools-user01',
                          '-p', 'bigdata',
                          '-a', app_url)
            process.expect_status(0)

            process = jut('config', 'list')
            process.expect_status(0)
            process.expect_output('Available jut configurations:\n')
            process.expect_output(confline(1, jut_user, app_url, default=True))
            process.expect_output(confline(2, 'jut-tools-user01', app_url, default=False))
            process.expect_eof()

            process = jut('config',
                          'defaults',
                          '-u', 'jut-tools-user01',
                          '-a', app_url)
            process.expect_status(0)
            process.expect_output('Configuration updated at %s\n' % home_dir)
            process.expect_eof()

            process = jut('config', 'list')
            process.expect_status(0)
            process.expect_output('Available jut configurations:\n')
            process.expect_output(confline(1, jut_user, app_url, default=False))
            process.expect_output(confline(2, 'jut-tools-user01', app_url, default=True))
            process.expect_eof()


    def test_config_rm_non_default_interactive(self):
        """
        verify you can interactively remove a non default configuration

        """

        with temp_jut_tools_home():
            jut_user = os.environ.get('JUT_USER')
            jut_pass = os.environ.get('JUT_PASS')
            configuration = config.get_default()
            app_url = configuration['app_url']

            process = jut('config',
                          'add',
                          '-u', jut_user,
                          '-p', jut_pass,
                          '-a', app_url)
            process.expect_status(0)

            process = jut('config',
                          'add',
                          '-u', 'jut-tools-user01',
                          '-p', 'bigdata',
                          '-a', app_url)
            process.expect_status(0)

            process = jut('config', 'list')
            process.expect_status(0)
            process.expect_output('Available jut configurations:\n')
            process.expect_output(confline(1, jut_user, app_url, default=True))
            process.expect_output(confline(2, 'jut-tools-user01', app_url, default=False))
            process.expect_eof()

            process = jut('config', 'rm')
            process.expect_output('Available jut configurations:\n')
            process.expect_output(confline(1, jut_user, app_url, default=True))
            process.expect_output(confline(2, 'jut-tools-user01', app_url, default=False))
            process.expect_output('Which configuration to remove: ')
            process.send('2\n')
            process.expect_status(0)

            process = jut('config', 'list')
            process.expect_status(0)
            process.expect_output('Available jut configurations:\n')
            process.expect_output(confline(1, jut_user, app_url, default=True))
            process.expect_eof()


    def test_config_rm_default_interactive(self):
        """
        verify you can interactively remove a default configuration and
        be prompted to pick a new default

        """

        with temp_jut_tools_home():
            jut_user = os.environ.get('JUT_USER')
            jut_pass = os.environ.get('JUT_PASS')
            configuration = config.get_default()
            app_url = configuration['app_url']

            process = jut('config',
                          'add',
                          '-u', jut_user,
                          '-p', jut_pass,
                          '-a', app_url)
            process.expect_status(0)

            process = jut('config',
                          'add',
                          '-u', 'jut-tools-user01',
                          '-p', 'bigdata',
                          '-a', app_url)
            process.expect_status(0)

            process = jut('config',
                          'add',
                          '-u', 'jut-tools-user02',
                          '-p', 'bigdata',
                          '-a', app_url)
            process.expect_status(0)

            process = jut('config', 'list')
            process.expect_status(0)
            process.expect_output('Available jut configurations:\n')
            process.expect_output(confline(1, jut_user, app_url, default=True))
            process.expect_output(confline(2, 'jut-tools-user01', app_url, default=False))
            process.expect_output(confline(3, 'jut-tools-user02', app_url, default=False))

            process = jut('config', 'rm')
            process.expect_output('Available jut configurations:\n')
            process.expect_output(confline(1, jut_user, app_url, default=True))
            process.expect_output(confline(2, 'jut-tools-user01', app_url, default=False))
            process.expect_output(confline(3, 'jut-tools-user02', app_url, default=False))
            process.expect_output('Which configuration to remove: ')
            process.send('1\n')
            process.expect_output('Pick a default configuration from the list below\n')
            process.expect_output('Available jut configurations:\n')
            process.expect_output(confline(1, 'jut-tools-user01', app_url, default=False))
            process.expect_output(confline(2, 'jut-tools-user02', app_url, default=False))
            process.expect_output('Set default configuration to: ')
            process.send('2\n')
            process.expect_status(0)

            process = jut('config', 'list')
            process.expect_status(0)
            process.expect_output('Available jut configurations:\n')
            process.expect_output(confline(1, 'jut-tools-user01', app_url, default=False))
            process.expect_output(confline(2, 'jut-tools-user02', app_url, default=True))
            process.expect_eof()


    def test_config_rm_non_default_non_interactive(self):
        """
        verify you can non interactively remove a non default configuration

        """

        with temp_jut_tools_home():
            jut_user = os.environ.get('JUT_USER')
            jut_pass = os.environ.get('JUT_PASS')
            configuration = config.get_default()
            app_url = configuration['app_url']

            process = jut('config',
                          'add',
                          '-u', jut_user,
                          '-p', jut_pass,
                          '-a', app_url)
            process.expect_status(0)

            process = jut('config',
                          'add',
                          '-u', 'jut-tools-user01',
                          '-p', 'bigdata',
                          '-a', app_url)
            process.expect_status(0)

            process = jut('config', 'list')
            process.expect_status(0)
            process.expect_output('Available jut configurations:\n')
            process.expect_output(confline(1, jut_user, app_url, default=True))
            process.expect_output(confline(2, 'jut-tools-user01', app_url, default=False))

            process = jut('config',
                          'rm',
                          '-u', 'jut-tools-user01',
                          '-a', app_url)
            process.expect_status(0)

            process = jut('config', 'list')
            process.expect_status(0)
            process.expect_output('Available jut configurations:\n')
            process.expect_output(confline(1, jut_user, app_url, default=True))
            process.expect_eof()



    @classmethod
    def tearDownClass(cls):
        delete_user_from_default_deployment('jut-tools-user01', 'bigdata')
        delete_user_from_default_deployment('jut-tools-user02', 'bigdata')

