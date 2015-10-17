"""
basic set of `jut run` tests

"""

import json
import unittest

from tests.util import jut

BAD_PROGRAM = 'foo'
BAD_PROGRAM_ERROR = 'Error line 1, column 1 of main: Error: no such sub: foo'


class JutRunTests(unittest.TestCase):


    def test_jut_run_syntatically_incorrect_program_reports_error_with_format_json(self):
        """
        verify an invalid program reports the failure correctly when using json
        output format

        """
        process = jut('run', BAD_PROGRAM, '-f', 'json')
        process.expect_status(255)
        process.expect_error(BAD_PROGRAM_ERROR)


    def test_jut_run_syntatically_incorrect_program_reports_error_with_format_text(self):
        """
        verify an invalid program reports the failure correctly when using text
        output format

        """
        process = jut('run', BAD_PROGRAM, '-f', 'text')
        process.expect_status(255)
        process.expect_error(BAD_PROGRAM_ERROR)


    def test_jut_run_syntatically_incorrect_program_reports_error_with_format_csv(self):
        """
        verify an invalid program reports the failure correctly when using csv
        output format

        """
        process = jut('run', BAD_PROGRAM, '-f', 'json')
        process.expect_status(255)
        process.expect_error(BAD_PROGRAM_ERROR)


    def test_jut_run_emit_to_json(self):
        """
        use jut to run the juttle program:

            emit -from :2014-01-01T00:00:00.000Z: -limit 5

        and verify the output is in the expected JSON format
        """
        process = jut('run',
                      'emit -from :2014-01-01T00:00:00.000Z: -limit 5')
        process.expect_status(0)
        points = json.loads(process.read_output())
        process.expect_eof()

        self.assertEqual(points,
                         [
                             {'time': '2014-01-01T00:00:00.000Z'},
                             {'time': '2014-01-01T00:00:01.000Z'},
                             {'time': '2014-01-01T00:00:02.000Z'},
                             {'time': '2014-01-01T00:00:03.000Z'},
                             {'time': '2014-01-01T00:00:04.000Z'}
                         ])


    def test_jut_run_emit_to_text(self):
        """
        use jut to run the juttle program:

            emit -from :2014-01-01T00:00:00.000Z: -limit 5

        and verify the output is in the expected text format
        """

        process = jut('run',
                      '--format', 'text',
                      'emit -from :2014-01-01T00:00:00.000Z: -limit 5')
        process.expect_status(0)
        stdout = process.read_output()
        process.expect_eof()

        self.assertEqual(stdout, '2014-01-01T00:00:00.000Z\n'
                                 '2014-01-01T00:00:01.000Z\n'
                                 '2014-01-01T00:00:02.000Z\n'
                                 '2014-01-01T00:00:03.000Z\n'
                                 '2014-01-01T00:00:04.000Z\n')


    def test_jut_run_emit_to_csv(self):
        """
        use jut to run the juttle program:

            emit -from :2014-01-01T00:00:00.000Z: -limit 5

        and verify the output is in the expected csv format
        """

        process = jut('run',
                      '--format', 'csv',
                      'emit -from :2014-01-01T00:00:00.000Z: -limit 5')
        process.expect_status(0)
        stdout = process.read_output()
        process.expect_eof()

        self.assertEqual(stdout, '#time\n'
                                 '2014-01-01T00:00:00.000Z\n'
                                 '2014-01-01T00:00:01.000Z\n'
                                 '2014-01-01T00:00:02.000Z\n'
                                 '2014-01-01T00:00:03.000Z\n'
                                 '2014-01-01T00:00:04.000Z\n')

