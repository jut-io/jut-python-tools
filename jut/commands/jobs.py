"""
jut config command

"""

import tabulate

from collections import OrderedDict

from jut import config

from jut.api import auth, accounts, data_engine
from jut.common import info, error
from jut.exceptions import JutException

from jut.util.console import prompt


def _print_jobs(jobs, access_token, app_url, options):
    """
    internal method to print the provided jobs array in a nice tabular
    format

    """
    accountids = set()
    for job in jobs:
        accountids.add(job['user'])

    accounts_details = accounts.get_accounts(accountids,
                                             access_token=access_token,
                                             app_url=app_url)

    account_lookup = {}
    for account in accounts_details['accounts']:
        account_lookup[account['id']] = account

    if options.format == 'text':
        labels = OrderedDict()
        labels['id'] = 'Job ID'
        labels['alias'] = 'Juttle Name'
        labels['username'] = 'Owner'
        labels['_start_time'] = 'Start Date'
        labels['persistent'] = 'Persistent'

        max_lengths = {
            'id': 0,
            'alias': 0,
            'username': 0,
            '_start_time': 0,
            'persistent': 0,
        }

        for key in max_lengths.keys():
            max_lengths[key] = len(labels[key]) + 1

        # retrieve username and fix up persistent marker
        for job in jobs:
            job['username'] = account_lookup[job['user']]['username']
            job['persistent'] = 'YES' if job['timeout'] == 0 else 'NO'

        # calculate max length of each column
        for job in jobs:
            for key in labels.keys():
                if max_lengths[key] < len(job[key]):
                    max_lengths[key] = len(job[key]) + 1

        # print labels
        header = ''
        for key in labels.keys():
            header += (labels[key] + ' ' * (max_lengths[key] - len(labels[key])))

        info(header)

        for job in jobs:
            line = ''

            for key in labels.keys():
                line += (job[key] + ' ' * (max_lengths[key] - len(job[key])))

            info(line)

    elif options.format == 'table':
        headers = ['Job ID', 'Juttle Name', 'Owner', 'Start Date', 'Persistent']

        table = []
        for job in jobs:
            owner = account_lookup[job['user']]['username']
            persistent = 'YES' if job['timeout'] == 0 else 'NO'
            table.append([job['id'],
                          job['alias'],
                          owner,
                          job['_start_time'],
                          persistent])

        info(tabulate.tabulate(table, headers, tablefmt="orgtbl"))

    else:
        raise JutException('Unsupported output format "%s"' %
                           options.format)

def list(options):
    """
    show all currently running jobs

    """
    configuration = config.get_default()
    app_url = configuration['app_url']

    if options.deployment != None:
        deployment_name = options.deployment
    else:
        deployment_name = configuration['deployment_name']

    client_id = configuration['client_id']
    client_secret = configuration['client_secret']

    access_token = auth.get_access_token(client_id=client_id,
                                         client_secret=client_secret,
                                         app_url=app_url)

    jobs = data_engine.get_jobs(deployment_name,
                                access_token=access_token,
                                app_url=app_url)


    if len(jobs) == 0:
        error('No running jobs')

    else:
        _print_jobs(jobs, access_token, app_url, options)


def kill(options):
    """
    kill a specific job by id

    """
    configuration = config.get_default()
    app_url = configuration['app_url']

    if options.deployment != None:
        deployment_name = options.deployment
    else:
        deployment_name = configuration['deployment_name']

    client_id = configuration['client_id']
    client_secret = configuration['client_secret']

    access_token = auth.get_access_token(client_id=client_id,
                                         client_secret=client_secret,
                                         app_url=app_url)

    job_details = data_engine.get_job_details(options.job_id,
                                              deployment_name,
                                              access_token=access_token,
                                              app_url=app_url)

    options.format='table'

    if options.yes:
        decision = 'Y'
    else:
        _print_jobs([job_details], access_token, app_url, options)
        decision = prompt('Are you sure you want to delete the above job? (Y/N)')

    if decision == 'Y':
        data_engine.delete_job(options.job_id.strip(),
                               deployment_name,
                               access_token=access_token,
                               app_url=app_url)

    else:
        raise JutException('Unexpected option "%s"' % decision)
