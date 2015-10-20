"""
basic set of `jut run` tests

"""

import json
import tempfile
import unittest
import uuid

from tests.util import jut, \
                       get_webhook_url, \
                       create_space_in_default_deployment, \
                       delete_space_from_default_deployment


class JutUploadTests(unittest.TestCase):

    test_space = 'jut_tools_testing'

    @classmethod
    def setUpClass(cls):
        create_space_in_default_deployment(JutUploadTests.test_space)

    @classmethod
    def tearDownClass(cls):
        delete_space_from_default_deployment(JutUploadTests.test_space)


    def test_jut_upload_to_url(self):
        """
        and verify the output is JSON format
        """

        _, json_filename = tempfile.mkstemp(suffix='.json')
        tag = str(uuid.uuid1())
        data = []

        for index in range(0, 10):
            data.append({
                "tag": tag,
                "index": index
            })

        with open(json_filename, 'w') as json_file:
            json_file.write(json.dumps(data))

        webhook_url = get_webhook_url(JutUploadTests.test_space)
        process = jut('upload',
                      json_filename,
                      '--url', webhook_url,
                      '--space', JutUploadTests.test_space,
                      stdin=None)
        process.expect_status(0)

        # read a few times till all the points appear as it takes a few seconds
        # before the data is committed permanently
        points = []
        retry = 0
        juttle = "read -space '%s' -last :5 minutes: tag='%s'" % \
                 (JutUploadTests.test_space, tag)

        while len(points) < 10 and retry < 10:
            process = jut('run', juttle)
            process.expect_status(0)
            points = json.loads(process.read_output())
            process.expect_eof()
            retry += 1

        process = jut('run', '%s | reduce count()' % juttle)
        process.expect_status(0)
        points = json.loads(process.read_output())
        process.expect_eof()


    def test_jut_upload_to_webhook_for_default_configuration(self):
        """
        and verify the output is JSON format
        """

        _, json_filename = tempfile.mkstemp(suffix='.json')
        tag = str(uuid.uuid1())
        data = []

        for index in range(0, 10):
            data.append({
                "tag": tag,
                "index": index
            })

        with open(json_filename, 'w') as json_file:
            json_file.write(json.dumps(data))

        process = jut('upload',
                      json_filename,
                      '--space', JutUploadTests.test_space,
                      stdin=None)

        process.expect_status(0)

        # read a few times till all the points appear as it takes a few seconds
        # before the data is committed permanently
        points = []
        retry = 0
        juttle = "read -space '%s' -last :5 minutes: tag='%s'" % \
                 (JutUploadTests.test_space, tag)

        while len(points) < 10 and retry < 10:
            process = jut('run', juttle)
            process.expect_status(0)
            points = json.loads(process.read_output())
            process.expect_eof()
            retry += 1

        process = jut('run', '%s | reduce count()' % juttle)
        process.expect_status(0)
        points = json.loads(process.read_output())
        process.expect_eof()
        self.assertEqual(points, [{'count': 10}])

