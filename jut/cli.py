"""
main entry point for jut tools

"""

import argparse
import getpass
import json
import os
import sys

from jut import defaults, config

from jut.api import auth, \
                    authorizations, \
                    data_engine, \
                    deployments, \
                    environment, \
                    integrations

from jut.common import info, error
from jut.util import uploader


def parse_key_value(string):
    """
    internally used method to parse 'x=y' strings into a tuple (x,y)

    """
    return tuple(string.split('='))


def default_deployment(app_url, client_id, client_secret):
    """
    """
    if app_url.strip() == '':
        app_url = 'https://app.jut.io'

    access_token = auth.get_access_token(client_id=client_id,
                                         client_secret=client_secret,
                                         app_url=app_url)

    user_deployments = deployments.get_deployments(access_token=access_token,
                                                   app_url=app_url)

    if len(user_deployments) > 1:
        index = 0
        for deployment in user_deployments:
            info(' %d: %s', index + 1, deployment['name'])
            index += 1

        which = raw_input('Pick default deployment from above: ')

        return user_deployments[int(which)-1]['name']
    else:
        return user_deployments[0]['name']


def default_configuration(interactive=True):
    if config.length() == 1:
        # when there is only one configuration, that should be the default one
        config.set_default(index=1)

    else:
        if interactive:
            info('Pick a default configuration from the list below:')
            config.print_configurations()
            which = raw_input('Set default configuration to: ')
            config.set_default(index=int(which))
            configuration = config.get_default()

            default_deployment(configuration['app_url'],
                            configuration['client_id'],
                            configuration['client_secret'])


def add_configuration(options):
    """
    interactively add a new configuration

    """
    if options.username != None:
        username = options.username
    else:
        username = raw_input('Username: ')

    if options.password != None:
        password = options.password
    else:
        password = getpass.getpass('Pasword: ')

    if options.app_url != None:
        app_url = options.app_url
    else:
        app_url = raw_input('App URL (default: https://app.jut.io just hit enter): ')

    if app_url.strip() == '':
        app_url = 'https://app.jut.io'

    access_token = auth.get_access_token(username=username,
                                         password=password,
                                         app_url=app_url)

    client_id, client_secret = authorizations.get_authorization(access_token,
                                                                app_url=app_url)

    deployment_name = default_deployment(app_url,
                                         client_id,
                                         client_secret)

    section = '%s@%s' % (username, app_url)
    config.add_configuration(section, **{
        'app_url': app_url,
        'deployment_name': deployment_name,
        'username': username,
        'client_id': client_id,
        'client_secret': client_secret
    })

    if options.default:
        config.set_default(name=section)
    else:
        default_configuration(interactive=False)


def main():

    class JutArgParser(argparse.ArgumentParser):
        """
        custom argument parser so we show the full comand line help menu

        """
        def error(self, message):
            error(message)
            self.print_help()
            sys.exit(2)

    parser = JutArgParser(description='jut - jut command line tools')
    commands = parser.add_subparsers(dest='subcommand')

    # config commands

    config_parser = commands.add_parser('config',
                                        help='configuration management')

    config_commands = config_parser.add_subparsers(dest='config_subcommand')

    _ = config_commands.add_parser('list',
                                   help='list configurations')

    defaults_config = config_commands.add_parser('defaults',
                                                 help='change the configuration defaults')

    defaults_config.add_argument('-u', '--username',
                                 help='username to use')

    defaults_config.add_argument('-a', '--app-url',
                                 default=defaults.APP_URL,
                                 help='app url (default: https://app.jut.io '
                                      'INTERNAL USE)')

    add_config = config_commands.add_parser('add',
                                            help='add another configuration '
                                                 '(default when no sub command '
                                                 'is provided)')

    add_config.add_argument('-u', '--username',
                            help='username to use')

    add_config.add_argument('-p', '--password',
                            help='password to use')

    add_config.add_argument('-a', '--app-url',
                            default=defaults.APP_URL,
                            help='app url (default: https://app.jut.io INTERNAL USE)')

    add_config.add_argument('-d', '--default',
                            action='store_true',
                            help='sets this configuration to the default')

    rm_config = config_commands.add_parser('rm',
                                           help='remove a configuration')

    rm_config.add_argument('-u', '--username',
                           help='username to use')

    rm_config.add_argument('-a', '--app-url',
                           default=defaults.APP_URL,
                           help='app url (default: https://app.jut.io INTERNAL USE)')


    # upload commands
    upload_parser = commands.add_parser('upload',
                                        help='upload local JSON file(s) to Jut')

    if sys.stdin.isatty():
        upload_parser.add_argument('source',
                                   help='The name of a JSON file or directory '
                                        'containing JSON files to process')

    upload_parser.add_argument('-u', '--url',
                               help='The URL to POST data points to, if none is '
                                    'specified we will push to the webhook for '
                                    'the default configuration')

    upload_parser.add_argument('-d', '--deployment',
                               dest='deployment',
                               default=None,
                               help='specify the deployment name')

    upload_parser.add_argument('-s', '--space',
                               dest='space',
                               default='default',
                               help='specify the destination space')

    upload_parser.add_argument('--dry-run',
                               action='store_true',
                               dest='dry_run',
                               default=False,
                               help='Just log the data that would have been '
                                    'POSTed to the specified URL.')

    upload_parser.add_argument('--batch-size',
                               dest='batch_size',
                               default=100,
                               type=int,
                               help='Maximum set of data points to send in each '
                                    'POST, default: 100.')

    upload_parser.add_argument('--anonymize-fields',
                               metavar='field_name',
                               dest='anonymize_fields',
                               nargs='+',
                               default=[],
                               help='space separated field names to anonymize '
                                    'in the data before uploading. Currently '
                                    'we anonymize hashing the field value with '
                                    'md5 hash')

    upload_parser.add_argument('--remove-fields',
                               metavar='field_name',
                               dest='remove_fields',
                               nargs='+',
                               default=[],
                               help='space separated field names to remove '
                                    'from the data before uploading')

    upload_parser.add_argument('--rename-fields',
                               metavar='field_name=new_field_name',
                               dest='rename_fields',
                               type=parse_key_value,
                               nargs='+',
                               default=[],
                               help='space separated field names to rename '
                                    'from the data before uploading.')

    # run parser
    run_parser = commands.add_parser('run',
                                     help='run juttle program from the import '
                                          'command line')

    run_parser.add_argument('juttle',
                            help='juttle program to execute or the filename '
                                 'of a juttle program.')

    run_parser.add_argument('-d', '--deployment',
                            dest='deployment',
                            default=None,
                            help='specify the deployment name')

    run_parser.add_argument('-f', '--format',
                            default='json',
                            help='')

    run_parser.add_argument('--debug',
                            action='store_true',
                            dest='debug')

    options = parser.parse_args()

    if options.subcommand == 'config':

        if options.config_subcommand == 'list':
            config.print_configurations()

        elif options.config_subcommand == 'add':
            add_configuration(options)

        elif options.config_subcommand == 'rm':
            was_default = False

            if options.username != None:
                configuration = '%s@%s' % (options.username, options.app_url)
                was_default = config.is_default(name=configuration)
                config.remove(name=configuration)

            else:
                config.print_configurations()
                which = raw_input('Which configuration to delete: ')
                which = int(which)
                config.remove(index=which)
                was_default = config.is_default(index=which)

            if was_default:
                default_configuration()

        elif options.config_subcommand == 'defaults':
            if options.username != None:
                configuration = '%s@%s' % (options.username, options.app_url)
                config.set_default(name=configuration)
                configuration = config.get_default()

            else:
                info('Pick a default configuration from the list below:')
                config.print_configurations()
                which = raw_input('Set default configuration to: ')
                config.set_default(index=int(which))
                configuration = config.get_default()

            default_deployment(configuration['app_url'],
                               configuration['client_id'],
                               configuration['client_secret'])

    elif options.subcommand == 'upload':
        if not sys.stdin.isatty():
            json_file = sys.stdin

        else:
            json_file = open(options.source, 'r')

        url = options.url

        if url == None:

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

            url = integrations.get_webhook_url(deployment_name,
                                               space=options.space,
                                               access_token=access_token,
                                               app_url=app_url)

        info('Pushing to %s' % url)
        uploader.push_json_file(json_file,
                                url,
                                dry_run=options.dry_run,
                                batch_size=options.batch_size,
                                anonymize_fields=options.anonymize_fields,
                                remove_fields=options.remove_fields,
                                rename_fields=options.rename_fields)

    elif options.subcommand == 'run':
        if not config.is_configured():
            add_configuration(options)

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

        access_token = auth.get_access_token(client_id=client_id,
                                             client_secret=client_secret,
                                             app_url=app_url)
        if options.format == 'json':
            point_before = False
            info('[')
            for points in data_engine.run(juttle,
                                          deployment_name,
                                          app_url=app_url,
                                          access_token=access_token):

                for point in points:
                    if point_before:
                        info(',')
                    info(json.dumps(point, indent=4))
                    point_before = True

            info(']')

        elif options.format == 'text':
            for points in data_engine.run(juttle,
                                          deployment_name,
                                          app_url=app_url,
                                          access_token=access_token):
                for point in points:
                    line = []
                    if 'time' in point:
                        timestamp = point['time']
                        del point['time']
                        line.append(timestamp)

                    keys = sorted(point.keys())
                    line += [str(point[key]) for key in keys]
                    info(' '.join(line))

    else:
        raise Exception('Bad')


if __name__ == '__main__':
    main()
