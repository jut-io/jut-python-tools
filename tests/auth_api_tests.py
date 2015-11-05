"""
jut auth api tests

"""

from jut.api import auth, accounts, authorizations
from jut.exceptions import JutException

from tests.util import get_test_user_pass, get_test_app_url

import unittest


class AuthAPITests(unittest.TestCase):

    def test_valid_username_password(self):
        """
        given valid username and password obtain auth tokens and use them
        to get the details about the current account
        """
        username, password = get_test_user_pass()
        app_url = get_test_app_url()

        token_manager = auth.TokenManager(username=username,
                                          password=password,
                                          app_url=app_url)

        # use the token manager to retrieve the logged in user details
        account = accounts.get_logged_in_account(token_manager=token_manager,
                                                 app_url=app_url)

        self.assertEquals(account['username'], username)


    def test_invalid_username_password(self):
        """
        given invalid username and password combination verify that the correct
        exception is thrown when attempting to use that token manager
        """
        username, _ = get_test_user_pass()
        app_url = get_test_app_url()

        token_manager = auth.TokenManager(username=username,
                                          password='WRONG PASSWORd',
                                          app_url=app_url)

        try:
            # use the token manager to retrieve the logged in user details
            accounts.get_logged_in_account(token_manager=token_manager,
                                           app_url=app_url)

            raise Exception('Should have failed to authenticate above')
        except JutException as exception:
            self.assertIn('Failed authentication with (%s,WRONG PASSWORd)' % username,
                          exception.message)


    def test_valid_client_id_and_client_secret(self):
        """
        given valid client id and secret values verify that we can use the
        toke manager to access account details
        """
        username, password = get_test_user_pass()
        app_url = get_test_app_url()

        #
        # you would provide a client_id and client_secret by retrieve them
        # from your jut profile but for unit testing we have to use the
        # token manager to retrieve such
        #
        token_manager = auth.TokenManager(username=username,
                                          password=password,
                                          app_url=app_url)

        authorization = authorizations.get_authorization(token_manager,
                                                         app_url=app_url)

        client_id = authorization['client_id']
        client_secret = authorization['client_secret']

        token_manager = auth.TokenManager(client_id=client_id,
                                          client_secret=client_secret,
                                          app_url=app_url)

        # use the token manager to retrieve the logged in user details
        account = accounts.get_logged_in_account(token_manager=token_manager,
                                                 app_url=app_url)

        self.assertEquals(account['username'], username)


    def test_invalid_client_id_and_client_secret(self):
        """
        given invalid client id and secret combination verify that the correct
        exception is thrown when attempting to use that token manager
        """
        app_url = get_test_app_url()
        token_manager = auth.TokenManager(client_id='invalid',
                                          client_secret='invalid',
                                          app_url=app_url)

        try:
            # use the token manager to retrieve the logged in user details
            accounts.get_logged_in_account(token_manager=token_manager,
                                           app_url=app_url)

        except JutException as exception:
            self.assertIn('Unable to get auth token 401',
                          exception.message)
