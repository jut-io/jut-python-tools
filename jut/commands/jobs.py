"""
jut config command

"""

import tabulate
import time

from collections import OrderedDict

from jut import config

from jut.api import auth, accounts, data_engine
from jut.common import info, error
from jut.commands import configs
from jut.exceptions import JutException
from jut.formatters import JSONFormatter, TextFormatter, CSVFormatter

from jut.util.console import prompt


def _print_jobs(jobs, token_manager, app_url, options):
    """
    internal method to print the provided jobs array in a nice tabular
    format

    """
    accountids = set()
    for job in jobs:
        if job['user'] != 'jut.internal.user':
            accountids.add(job['user'])

    account_lookup = {
        'jut.internal.user': {
            'username': 'Jut Internal'
        }
    }

    if accountids:
        accounts_details = accounts.get_accounts(accountids,
                                                 token_manager=token_manager,
                                                 app_url=app_url)

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
            name = ''

            if 'alias' in job:
                name = job['alias']

            table.append([job['id'],
                          name,
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

    token_manager = auth.TokenManager(client_id=client_id,
                                      client_secret=client_secret,
                                      app_url=app_url)

    jobs = data_engine.get_jobs(deployment_name,
                                token_manager=token_manager,
                                app_url=app_url)


    if len(jobs) == 0:
        error('No running jobs')

    else:
        _print_jobs(jobs, token_manager, app_url, options)


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

    token_manager = auth.TokenManager(client_id=client_id,
                                      client_secret=client_secret,
                                      app_url=app_url)

    job_details = data_engine.get_job_details(options.job_id,
                                              deployment_name,
                                              token_manager=token_manager,
                                              app_url=app_url)

    options.format = 'table'

    if options.yes:
        decision = 'Y'
    else:
        _print_jobs([job_details], token_manager, app_url, options)
        decision = prompt('Are you sure you want to delete the above job? (Y/N)')

    if decision == 'Y':
        data_engine.delete_job(options.job_id.strip(),
                               deployment_name,
                               token_manager=token_manager,
                               app_url=app_url)

    else:
        raise JutException('Unexpected option "%s"' % decision)


def connect(options):
    options.persist = False

    if not config.is_configured():
        configs.add_configuration(options)

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

    total_points = 0

    def show_progress():
        if options.show_progress:
            error('streamed %s points', total_points, end='\r')

    def show_error_or_warning(data):
        """
        handle error and warning reporting

        """
        if 'error' in data:
            prefix = 'Error'

        elif 'warning' in data:
            prefix = 'Warning'

        else:
            raise Exception('Unexpected error/warning received %s' % data)

        message = None
        location = None

        if 'context' in data:
            message = data['context']['message']

            # not all errors or warnings have location information
            if 'location' in data['context']['info']:
                location = data['context']['info']['location']
                line = location['start']['line']
                column = location['start']['column']

        else:
            message = '%s: %s' % (prefix, message)

        if location != None:
            error('%s line %s, column %s of %s: %s' %
                  (prefix, line, column, location['filename'], message))

        else:
            error(message)

    if options.format == 'json':
        formatter = JSONFormatter(options)

    elif options.format == 'text':
        formatter = TextFormatter(options)

    elif options.format == 'csv':
        formatter = CSVFormatter(options)

    else:
        raise JutException('Unsupported output format "%s"' %
                           options.format)

    job_id = options.job_id

    done = False
    with_errors = False
    max_retries = options.retry
    retry_delay = options.retry_delay
    retry = 0

    while not done:
        try:
            if not options.persist:
                formatter.start()

            for data in data_engine.connect_job(job_id,
                                                deployment_name,
                                                token_manager=token_manager,
                                                app_url=app_url):
                show_progress()

                if 'job' in data:
                    # job details
                    if options.persist:
                        # lets print the job id
                        info(data['job']['id'])

                if 'points' in data:
                    points = data['points']
                    for point in points:
                        formatter.point(point)

                    total_points += len(points)

                elif 'error' in data:
                    show_error_or_warning(data)
                    with_errors = True

                elif 'warning' in data:
                    show_error_or_warning(data)

            done = True

        except JutException:
            retry += 1

            if max_retries != -1 and retry > max_retries:
                raise

            time.sleep(retry_delay)

        finally:
            if options.show_progress:
                # one enter to retain the last value of progress output
                info('')

            if not options.persist:
                formatter.stop()

            if with_errors:
                raise JutException('Error while running juttle')
