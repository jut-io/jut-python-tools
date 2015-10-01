"""
basic set of `jut run` tests

"""

import json
import unittest

from util import jut

class JutRunTests(unittest.TestCase):


    def test_jut_run_syntatically_incorrect_program_reports_error_with_format_json(self):
        """
        verify an invalid program reports the failure correctly

        """

        stdout, stderr = jut('run', 'foo', '-f', 'json', exit_code=255)
        self.assertTrue('Error line 1, column 1 of main: Error: no such sub: foo' in stderr)

        # stdout should still contain a valid JSON object
        self.assertEqual(stdout, '[\n]\n')


    def test_jut_run_syntatically_incorrect_program_reports_error_with_format_text(self):
        """
        verify an invalid program reports the failure correctly

        """

        stdout, stderr = jut('run', 'foo', '-f', 'text', exit_code=255)
        self.assertTrue('Error line 1, column 1 of main: Error: no such sub: foo' in stderr)
        self.assertEqual(stdout.strip(), '')


    def test_jut_run_emit_to_json(self):
        """
        use jut to run the juttle program:

            emit -from :2014-01-01T00:00:00.000Z: -limit 5

        and verify the output is JSON format
        """

        stdout, stderr = jut('run',
                             'emit -from :2014-01-01T00:00:00.000Z: -limit 5')

        points = json.loads(stdout)

        self.assertEquals(stderr, '')
        self.assertEqual(points,
                         [
                             {'time': '2014-01-01T00:00:00.000Z'},
                             {'time': '2014-01-01T00:00:01.000Z'},
                             {'time': '2014-01-01T00:00:02.000Z'},
                             {'time': '2014-01-01T00:00:03.000Z'},
                             {'time': '2014-01-01T00:00:04.000Z'}
                         ])


    def tesu_jut_run_emit_to_text(self):
        """
        use jut to run the juttle program:

            emit -from :2014-01-01T00:00:00.000Z: -limit 5

        and verify the output is in the text format
        """

        stdout, stderr = jut('run',
                             '--format', 'text',
                             'emit -from :2014-01-01T00:00:00.000Z: -limit 5')

        self.assertEquals(stderr, '')
        self.assertEqual(stdout, '2014-01-01T00:00:00.000Z\n'
                                 '2014-01-01T00:00:01.000Z\n'
                                 '2014-01-01T00:00:02.000Z\n'
                                 '2014-01-01T00:00:03.000Z\n'
                                 '2014-01-01T00:00:04.000Z\n')

