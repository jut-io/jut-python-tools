"""
jut accounts api tests

"""

from jut.api import auth, accounts
from jut.exceptions import JutException

from tests.util import get_test_user_pass, get_test_app_url

import unittest


class AccountsAPITests(unittest.TestCase):


    def test_create_and_delete_account(self):
        """
        verify we can correctly create and delete a new account

        """
        username, password = get_test_user_pass()
        app_url = get_test_app_url()

        token_manager = auth.TokenManager(username=username,
                                          password=password,
                                          app_url=app_url)

        if accounts.user_exists('jut-tools-user03',
                                token_manager=token_manager,
                                app_url=app_url):
            user03_token_manager = auth.TokenManager(username='jut-tools-user03',
                                                     password='bigdata',
                                                     app_url=app_url)

            accounts.delete_user('jut-tools-user03',
                                 token_manager=user03_token_manager,
                                 app_url=app_url)

        account = accounts.create_user('Jut Tools User #3',
                                       'jut-tools-user03',
                                       'jut-tools-user03@jut.io',
                                       'bigdata',
                                       token_manager=token_manager,
                                       app_url=app_url)

        self.assertIn('id', account)

        user03_token_manager = auth.TokenManager(username='jut-tools-user03',
                                                 password='bigdata',
                                                 app_url=app_url)

        accounts.delete_user('jut-tools-user03',
                             token_manager=user03_token_manager,
                             app_url=app_url)


    def test_create_existing_account(self):
        """
        verify we get an appropriate error when creating an account with an
        already used username

        """
        username, password = get_test_user_pass()
        app_url = get_test_app_url()

        token_manager = auth.TokenManager(username=username,
                                          password=password,
                                          app_url=app_url)

        try:
            accounts.create_user('Jut Tools User Never',
                                 username,
                                 'jut-tools-user-never@jut.io',
                                 'bigdata',
                                 token_manager=token_manager,
                                 app_url=app_url)

        except JutException as exception:
            self.assertIn('username in use', exception.message)


    def test_delete_inexistent_account(self):
        """
        deleting an inexistent account reports the expected failure

        """
        username, password = get_test_user_pass()
        app_url = get_test_app_url()

        token_manager = auth.TokenManager(username=username,
                                          password=password,
                                          app_url=app_url)

        try:
            accounts.delete_user('blah',
                                 token_manager=token_manager,
                                 app_url=app_url)

        except JutException as exception:
            self.assertIn('Account not found', exception.message)


    def test_user_exists(self):
        """
        verify we can correctly create and delete a new account

        """
        username, password = get_test_user_pass()
        app_url = get_test_app_url()

        token_manager = auth.TokenManager(username=username,
                                          password=password,
                                          app_url=app_url)

        if not accounts.user_exists(username,
                                    token_manager=token_manager,
                                    app_url=app_url):
            raise Exception('User exists API failed for "%s"' % username)

