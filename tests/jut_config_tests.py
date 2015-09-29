"""
basic set of `jut config` tests

"""

import os
import unittest

from tests.util import jut, \
                       create_user_in_default_deployment, \
                       delete_user_from_default_deployment, \
                       DEFAULT_TEST_USERNAME

from jut import config, defaults

class JutConfigTests(unittest.TestCase):


    @classmethod
    def setUpClass(cls):
        create_user_in_default_deployment('Jut Tools User #1',
                                          DEFAULT_TEST_USERNAME,
                                          '%s@jut-tools.test' % DEFAULT_TEST_USERNAME,
                                          'bigdata')


    def assertContains(self,
                       stdout,
                       at_line,
                       index,
                       username,
                       app_url,
                       default=False):
        stdout_lines = stdout.split('\n')

        if default:
            if app_url == defaults.APP_URL:
                line = ' %d: %s (default)' % (index, username)
            else:
                line = ' %d: %s@%s (default)' % (index, username, app_url)
        else:
            if app_url == defaults.APP_URL:
                line = ' %d: %s' % (index, username)
            else:
                line = ' %d: %s@%s' % (index, username, app_url)

        self.assertTrue(line == stdout_lines[at_line])


    def test_config_list(self):
        """
        list the saved configuration and verify it only contains the single
        test account with JUT_USER used by the jut unittests

        """
        jut_user = os.environ.get('JUT_USER')

        configuration = config.get_default()
        app_url = configuration['app_url']

        stdout, stderr = jut('config', 'list')

        self.assertEquals(stderr, '')
        self.assertContains(stdout, 1, 1, jut_user, app_url, default=True)


    def test_config_add(self):
        """
        add a few tests accounts to the default configuration and then add
        those configurations to the current jut tools config

        """
        jut_user = os.environ.get('JUT_USER')

        configuration = config.get_default()
        app_url = configuration['app_url']

        jut('config',
            'add',
            '-u', DEFAULT_TEST_USERNAME,
            '-p', 'bigdata',
            '-a', app_url)

        stdout, stderr = jut('config', 'list')

        self.assertEquals(stderr, '')
        self.assertContains(stdout, 1, 1, jut_user, app_url, default=True)
        self.assertContains(stdout, 2, 2, DEFAULT_TEST_USERNAME, app_url)

        jut('config',
            'rm',
            '-u', DEFAULT_TEST_USERNAME,
            '-a', app_url)


    def test_config_defaults(self):
        """
        see that you can easily change the default configuration in use
        and that it switches back once you delete the default configuration

        """
        jut_user = os.environ.get('JUT_USER')
        jut_pass = os.environ.get('JUT_PASS')

        configuration = config.get_default()
        app_url = configuration['app_url']

        jut('config',
            'add',
            '-u', DEFAULT_TEST_USERNAME,
            '-p', 'bigdata',
            '-a', app_url)

        # switch the default configuration
        jut('config',
            'defaults',
            '-u', DEFAULT_TEST_USERNAME,
            '-a', app_url)

        stdout, stderr = jut('config', 'list')

        self.assertEquals(stderr, '')
        self.assertContains(stdout, 1, 1, jut_user, app_url)
        self.assertContains(stdout, 2, 2, DEFAULT_TEST_USERNAME, app_url, default=True)

        jut('config',
            'rm',
            '-u', DEFAULT_TEST_USERNAME,
            '-a', app_url)

        stdout, stderr = jut('config', 'list')

        self.assertEquals(stderr, '')
        self.assertContains(stdout, 1, 1, jut_user, app_url, default=True)


    @classmethod
    def tearDownClass(cls):
        delete_user_from_default_deployment(DEFAULT_TEST_USERNAME,
                                            'bigdata')
