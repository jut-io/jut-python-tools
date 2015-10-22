"""
jut programs API

EXPERIMENTAL API - "here be dragons"
"""

import json
import requests

from jut import defaults

from jut.api import accounts, data_engine
from jut.exceptions import JutException
from jut.util import dates


def get_programs(deployment_name,
                 created_by=None,
                 token_manager=None,
                 app_url=defaults.APP_URL):
    """

    """
    headers = token_manager.get_access_token_headers()

    data_url = data_engine.get_juttle_data_url(deployment_name,
                                               token_manager=token_manager,
                                               app_url=app_url)

    url = "%s/api/v1/app/programs" % data_url

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        raise JutException('Error %s: %s' % (response.status_code, response.text))

    filtered_programs = []

    if created_by != None:
        programs = response.json()

        for program in programs:
            if program['createdBy'] == created_by:
                filtered_programs.append(program)

        return filtered_programs

    else:
        return response.json()


def program_exists(program_name,
                   deployment_name,
                   token_manager=None,
                   app_url=defaults.APP_URL):

    programs = get_programs(deployment_name,
                            token_manager=token_manager,
                            app_url=app_url)

    for program in programs:
        if program['alias'] == program:
            return True

    return False


def get_program(program_name,
                deployment_name,
                token_manager=None,
                app_url=defaults.APP_URL):

    programs = get_programs(deployment_name,
                            token_manager=token_manager,
                            app_url=app_url)

    for program in programs:
        if program['name'] == program_name:
            return program

    raise JutException('Unable to find program "%s"' % program_name)


def update_program(program_name,
                   program_code,
                   deployment_name,
                   last_edited=None,
                   token_manager=None,
                   app_url=defaults.APP_URL):
    headers = token_manager.get_access_token_headers()

    data_url = data_engine.get_juttle_data_url(deployment_name,
                                               token_manager=token_manager,
                                               app_url=app_url)

    account_id = accounts.get_logged_in_account_id(token_manager=token_manager,
                                                   app_url=app_url)

    program_id = get_program(program_name,
                             deployment_name,
                             token_manager=token_manager,
                             app_url=app_url)['id']

    if last_edited == None:
        last_edited = dates.now_iso8601()

    program = {
        'id': program_id,
        'name': program_name,
        'code': program_code,
        'createdBy': account_id,
        'lastEdited': last_edited,
        'canvasLayout': []
    }


    url = "%s/api/v1/app/programs" % data_url

    response = requests.put(url,
                            headers=headers,
                            data=json.dumps(program))

    if response.status_code != 204:
        raise JutException('Error %s: %s' % (response.status_code, response.text))

    return response.json()


def save_program(program_name,
                 program_code,
                 deployment_name,
                 last_edited=None,
                 token_manager=None,
                 app_url=defaults.APP_URL):

    headers = token_manager.get_access_token_headers()

    data_url = data_engine.get_juttle_data_url(deployment_name,
                                               token_manager=token_manager,
                                               app_url=app_url)

    account_id = accounts.get_logged_in_account_id(token_manager=token_manager,
                                                   app_url=app_url)

    if last_edited == None:
        last_edited = dates.now_iso8601()

    program = {
        'name': program_name,
        'code': program_code,
        'createdBy': account_id,
        'lastEdited': last_edited,
        'canvasLayout': []
    }

    url = "%s/api/v1/app/programs" % data_url

    response = requests.post(url,
                             headers=headers,
                             data=json.dumps(program))

    if response.status_code != 201:
        raise JutException('Error %s: %s' % (response.status_code, response.text))

    return response.json()


