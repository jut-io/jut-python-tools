"""
jut run command
"""

import os
import time

from jut import config
from jut.api import auth, data_engine
from jut.commands import configs
from jut.common import info, error
from jut.exceptions import JutException
from jut.formatters import JSONFormatter, TextFormatter, CSVFormatter

def run_juttle(options):
    if not config.is_configured():
        configs.add_configuration(options)

    if os.path.exists(options.juttle):
        juttle = open(options.juttle, 'r').read()
    else:
        juttle = options.juttle

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

    program_name = options.name
    if program_name == None:
        program_name = 'jut-tools program %s' % int(time.time())

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

    done = False
    with_errors = False
    max_retries = options.retry
    retry_delay = options.retry_delay
    retry = 0

    while not done:
        try:
            if not options.persist:
                formatter.start()

            for data in data_engine.run(juttle,
                                        deployment_name,
                                        program_name=program_name,
                                        persist=options.persist,
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
