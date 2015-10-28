"""
basic set of `jut jobs` tests

"""

import re
import signal
import unittest

from tests.util import jut, \
                       temp_jut_tools_home, \
                       create_space_in_default_deployment, \
                       delete_space_from_default_deployment, \
                       create_user_in_default_deployment, \
                       delete_user_from_default_deployment

from jut import config


class JutJobsTests(unittest.TestCase):

    test_space = 'jut_tools_testing'


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

        create_user_in_default_deployment('Jut Tools User #3',
                                          'jut-tools-user03',
                                          'jut-tools-user03@jut.io',
                                          'bigdata')

        create_space_in_default_deployment(JutJobsTests.test_space)


    @classmethod
    def tearDownClass(cls):
        delete_space_from_default_deployment(JutJobsTests.test_space)
        delete_user_from_default_deployment('jut-tools-user01', 'bigdata')
        delete_user_from_default_deployment('jut-tools-user02', 'bigdata')
        delete_user_from_default_deployment('jut-tools-user03', 'bigdata')


    def test_jut_jobs_list_with_no_running_jobs(self):
        """

        """
        process = jut('jobs', 'list')
        process.expect_status(0)
        process.expect_error('No running jobs')


    def test_jut_jobs_with_running_jobs(self):
        """
        verify that a simple long running program can be displayed correctly
        when running `jut jobs list`

        """
        with temp_jut_tools_home():
            configuration = config.get_default()
            app_url = configuration['app_url']

            process = jut('config',
                          'add',
                          '-u', 'jut-tools-user01',
                          '-p', 'bigdata',
                          '-a', app_url,
                          '-d')

            process.expect_status(0)

            process = jut('run',
                          '--name', 'Persistent Job #1',
                          '-p',
                          'emit -limit 100 '
                          '| put source_type="event" '
                          '| write -space "%s"' % JutJobsTests.test_space)

            process.expect_status(0)
            job_id = process.read_output()

            process = jut('jobs',
                          'list',
                          '-f', 'text')

            process.expect_status(0)
            output = process.read_output()
            lines = output.split('\n')
            re.match(r'Job ID\w+Juttle Name\w+Owner\w+Start Date\w+Persistent', lines[0])
            re.match(r'%s\w+Persistent Job #1\w+jut-tools-user01.*YES' % job_id, lines[1])


    def test_jut_kill_on_persistent_job(self):
        """
        verify that a persistent job can be killed using `jut jobs kill`

        """
        with temp_jut_tools_home():
            configuration = config.get_default()
            app_url = configuration['app_url']

            process = jut('config',
                          'add',
                          '-u', 'jut-tools-user02',
                          '-p', 'bigdata',
                          '-a', app_url,
                          '-d')
            process.expect_status(0)

            process = jut('run',
                          '--name', 'Persistent Job #1',
                          '-p',
                          'emit -limit 10000 '
                          '| put source_type="event" '
                          '| write -space "%s"' % JutJobsTests.test_space)
            process.expect_status(0)
            job_id = process.read_output().strip()

            process = jut('jobs',
                          'list',
                          '-f', 'text')

            process.expect_status(0)
            output = process.read_output()
            lines = output.split('\n')
            re.match(r'Job ID\w+Juttle Name\w+Owner\w+Start Date\w+Persistent', lines[0])
            re.match(r'%s\w+Persistent Job #1\w+jut-tools-user02.*YES' % job_id, lines[1])

            process = jut('jobs',
                          'kill',
                          job_id,
                          '-y')
            process.expect_status(0)
            process.expect_eof()

            process = jut('jobs', 'list')
            process.expect_status(0)
            process.expect_error('No running jobs')


    def test_jut_jobs_connect_on_persistent_job(self):
        """
        verify we can reconnect to a persistent job

        """
        with temp_jut_tools_home():
            configuration = config.get_default()
            app_url = configuration['app_url']

            process = jut('config',
                          'add',
                          '-u', 'jut-tools-user03',
                          '-p', 'bigdata',
                          '-a', app_url,
                          '-d')
            process.expect_status(0)

            process = jut('run',
                          '--name', 'Persistent Job #3',
                          '-p',
                          'emit -limit 10000 '
                          '| put source_type="event", foo="bar"'
                          '| (write -space "%s"; keep foo | pass)' %
                          JutJobsTests.test_space)

            process.expect_status(0)
            job_id = process.read_output().strip()

            process = jut('jobs',
                          'connect',
                          job_id,
                          '-f', 'text')

            # verify that we output 'bar' a few times
            process.expect_output('bar\n')
            process.expect_output('bar\n')
            process.expect_output('bar\n')
            process.expect_output('bar\n')
            process.expect_output('bar\n')

            process.send_signal(signal.SIGTERM)
            process.expect_status(-signal.SIGTERM)

            process = jut('jobs',
                          'kill',
                          job_id,
                          '-y')
            process.expect_status(0)
            process.expect_eof()

            process = jut('jobs', 'list')
            process.expect_status(0)
            process.expect_error('No running jobs')


