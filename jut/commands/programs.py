"""
jut programs command

EXPERIMENTAL COMMAND - "here be dragons"
"""

import codecs
import difflib
import json
import os
import tabulate
import urllib

from jut import config

from jut.api import accounts, auth, programs
from jut.common import info
from jut.exceptions import JutException
from jut.util import dates, console


def list(options):
    """
    list programs that belong to the authenticated user

    """
    configuration = config.get_default()
    app_url = configuration['app_url']

    if options.deployment != None:
        deployment_name = options.deployment
    else:
        deployment_name = configuration['deployment_name']

    client_id = configuration['client_id']
    client_secret = configuration['client_secret']

    token_manager = auth.TokenManager(client_id=client_id,
                                      client_secret=client_secret,
                                      app_url=app_url)

    if options.all == True:
        account_id = None

    else:
        account_id = accounts.get_logged_in_account_id(token_manager=token_manager,
                                                       app_url=app_url)

    programs_details = programs.get_programs(deployment_name,
                                             token_manager=token_manager,
                                             created_by=account_id,
                                             app_url=app_url)

    account_ids = set()
    for program in programs_details:
        account_ids.add(program['createdBy'])

    accounts_details = accounts.get_accounts(account_ids,
                                             token_manager=token_manager,
                                             app_url=app_url)

    account_lookup = {}
    for account in accounts_details['accounts']:
        account_lookup[account['id']] = account

    headers = ['Name', 'Last Saved', 'Created By']
    table = []

    for program in programs_details:
        username = account_lookup[program['createdBy']]['username']
        program_name = program['name']
        last_edited = program['lastEdited']
        table.append([program_name, last_edited, username])

    if options.format == 'table':
        info(tabulate.tabulate(table, headers, tablefmt='orgtbl'))

    elif options.format == 'text':
        info(tabulate.tabulate(table, headers, tablefmt='orgtbl', stralign='center'))

    else:
        raise JutException('Unsupported format "%s"' % options.format)


def escape_filename(filename):
    return filename.replace('/', '%2F%0A')


def pull(options):
    """
    pull all remote programs to a local directory

    """
    configuration = config.get_default()
    app_url = configuration['app_url']

    if options.deployment != None:
        deployment_name = options.deployment
    else:
        deployment_name = configuration['deployment_name']

    client_id = configuration['client_id']
    client_secret = configuration['client_secret']

    token_manager = auth.TokenManager(client_id=client_id,
                                      client_secret=client_secret,
                                      app_url=app_url)

    if options.all == True:
        account_id = None

    else:
        account_id = accounts.get_logged_in_account_id(token_manager=token_manager,
                                                       app_url=app_url)

    programs_details = programs.get_programs(deployment_name,
                                             token_manager=token_manager,
                                             created_by=account_id,
                                             app_url=app_url)

    if not os.path.exists(options.directory):
        os.mkdir(options.directory)

    account_ids = set()
    for program in programs_details:
        account_ids.add(program['createdBy'])

    accounts_details = accounts.get_accounts(account_ids,
                                             token_manager=token_manager,
                                             app_url=app_url)

    account_lookup = {}
    for account in accounts_details['accounts']:
        account_lookup[account['id']] = account

    decision = None
    for program in programs_details:
        program_name = program['name']
        juttle_filename = '%s.juttle' % escape_filename(program_name)

        if options.per_user_directory:
            username = account_lookup[program['createdBy']]['username']
            userdir = os.path.join(options.directory, username)

            if not os.path.exists(userdir):
                os.mkdir(userdir)

            juttle_filepath = os.path.join(userdir, juttle_filename)

        else:
            juttle_filepath = os.path.join(options.directory, juttle_filename)

        if os.path.exists(juttle_filepath) and decision != 'A':
            program_code = None
            with codecs.open(juttle_filepath, 'r', encoding='UTF-8') as program_file:
                program_code = program_file.read()

            local_last_edited = int(os.stat(juttle_filepath).st_mtime)
            remote_last_edited = dates.iso8601_to_epoch(program['lastEdited'])

            if local_last_edited != remote_last_edited:
                info('Juttle changed since last pull for "%s"' % program_name)
                decision = console.prompt('Would you like to '
                                          '(O - Override,'
                                          ' S - Skip,'
                                          ' R - Review Changes,'
                                          ' A - override All)?')

                if decision == 'R':
                    info('Following is what would change if we overrode using your copy:')
                    info('*'*80)
                    for line in difflib.ndiff(program['code'].split('\n'),
                                              program_code.split('\n')):
                        info(line)
                    info('*'*80)
                    decision = console.prompt('Would you like to '
                                              '(O - Override,'
                                              ' S - Skip)?')

                if decision == 'S':
                    # jump to the next file
                    continue

                elif decision == 'O':
                    pass

                elif decision == 'A':
                    pass

                else:
                    raise JutException('Unexpected option "%s"' % decision)

        info('importing program "%s" to %s' % (program['name'], juttle_filepath))
        with codecs.open(juttle_filepath, 'w', encoding='UTF-8') as program_file:
            program_file.write(program['code'])

        # update creation time to match the lastEdited field
        epoch = dates.iso8601_to_epoch(program['lastEdited'])
        os.utime(juttle_filepath, (epoch, epoch))


def push(options):
    configuration = config.get_default()
    app_url = configuration['app_url']

    if options.deployment != None:
        deployment_name = options.deployment
    else:
        deployment_name = configuration['deployment_name']

    client_id = configuration['client_id']
    client_secret = configuration['client_secret']

    token_manager = auth.TokenManager(client_id=client_id,
                                      client_secret=client_secret,
                                      app_url=app_url)


    if not os.path.exists(options.source):
        raise JutException('Source "%s" does not exists.')

    filenames = []
    if os.path.isdir(options.source):
        for filename in os.listdir(options.source):
            if filename.endswith('.juttle'):
                filenames.append(filename)

    else:
        filenames.append(options.source)

    decision = None
    for filename in filenames:
        filepath = os.path.join(options.source, filename)
        program_name = urllib.unquote_plus(os.path.basename(filepath).replace(r'.juttle', ''))
        info('Found program "%s"' % program_name)

        with codecs.open(filepath, 'r', encoding='UTF-8') as program_file:
            program_code = program_file.read()

        local_last_edited = int(os.stat(filepath).st_mtime)

        if programs.program_exists(program_name,
                                   deployment_name,
                                   token_manager=token_manager,
                                   app_url=app_url):

            # one last safety to check if the modification time of
            # the file still matches the lastEdited of the existing
            # copy on Jut otherwise we prompt the user for confirmation
            program = programs.get_program(program_name,
                                           deployment_name,
                                           token_manager=token_manager,
                                           app_url=app_url)

            remote_last_edited = dates.iso8601_to_epoch(program['lastEdited'])

            if local_last_edited != remote_last_edited and decision != 'A':
                info('Juttle changed since last pull for "%s"' % program_name)
                decision = console.prompt('Would you like to '
                                          '(O - Override,'
                                          ' S - Skip,'
                                          ' R - Review Changes,'
                                          ' A - override All)?')

                if decision == 'R':
                    info('Following is what would change if we overrode using your copy:')
                    info('*'*80)
                    for line in difflib.ndiff(program['code'].split('\n'),
                                              program_code.split('\n')):
                        info(line)
                    info('*'*80)
                    decision = console.prompt('Would you like to '
                                              '(O - Override,'
                                              ' S - Skip)?')

                if decision == 'S':
                    # jump to the next file
                    continue

                elif decision == 'O':
                    pass

                elif decision == 'A':
                    pass

                else:
                    raise JutException('Unexpected option "%s"' % decision)


            last_edited_iso = dates.epoch_to_iso8601(local_last_edited)
            programs.update_program(program_name,
                                    program_code,
                                    deployment_name,
                                    last_edited=last_edited_iso,
                                    token_manager=token_manager,
                                    app_url=app_url)
            os.utime(filepath, (local_last_edited, local_last_edited))

        else:
            last_edited_iso = dates.epoch_to_iso8601(local_last_edited)
            programs.save_program(program_name,
                                  program_code,
                                  deployment_name,
                                  last_edited=last_edited_iso,
                                  token_manager=token_manager,
                                  app_url=app_url)
            os.utime(filepath, (local_last_edited, local_last_edited))

