"""
basic set of `jut run` tests

"""

import json
import unittest

from util import jut

class JutRunTests(unittest.TestCase):


    def test_jut_run_emitter_to_json(self):
        """
        use jut to run the juttle program:

            emitter -from :2014-01-01T00:00:00.000Z: -limit 5

        and verify the output is JSON format
        """

        stdout, stderr = jut('run',
                             'emitter -from :2014-01-01T00:00:00.000Z: -limit 5')

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


    def test_jut_run_emittert_to_text(self):
        """
        use jut to run the juttle program:

            emitter -from :2014-01-01T00:00:00.000Z: -limit 5

        and verify the output is in the text format
        """

        stdout, stderr = jut('run',
                             '--format', 'text',
                             'emitter -from :2014-01-01T00:00:00.000Z: -limit 5')

        self.assertEquals(stderr, '')
        self.assertEqual(stdout, '2014-01-01T00:00:00.000Z\n'
                                 '2014-01-01T00:00:01.000Z\n'
                                 '2014-01-01T00:00:02.000Z\n'
                                 '2014-01-01T00:00:03.000Z\n'
                                 '2014-01-01T00:00:04.000Z\n')

