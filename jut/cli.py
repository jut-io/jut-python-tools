"""
main entry point for jut tools

"""

import argparse
import sys
import traceback

from jut import defaults, config

from jut.commands import configs, jobs, programs, run, upload

from jut.common import error, is_debug_enabled
from jut.exceptions import JutException


def parse_key_value(string):
    """
    internally used method to parse 'x=y' strings into a tuple (x,y)

    """
    return tuple(string.split('='))


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

    add_config.add_argument('-s', '--show-password',
                            action='store_true',
                            default=False,
                            help='shows password as you type it interactively')

    rm_config = config_commands.add_parser('rm',
                                           help='remove a configuration')

    rm_config.add_argument('-u', '--username',
                           help='username to use')

    rm_config.add_argument('-a', '--app-url',
                           default=defaults.APP_URL,
                           help='app url (default: https://app.jut.io INTERNAL USE)')

    # jobs commands
    jobs_parser = commands.add_parser('jobs',
                                      help='jobs management')

    jobs_commands = jobs_parser.add_subparsers(dest='jobs_subcommand')

    list_jobs = jobs_commands.add_parser('list',
                                         help='list running jobs')

    list_jobs.add_argument('-d', '--deployment',
                           default=None,
                           help='specify the deployment name')

    list_jobs.add_argument('-a', '--app-url',
                           default=defaults.APP_URL,
                           help='app url (default: https://app.jut.io INTERNAL USE)')

    list_jobs.add_argument('-f', '--format',
                           default='table',
                           help='available formats are text, table with '
                                'default: table')

    kill_job = jobs_commands.add_parser('kill',
                                        help='kill running job')

    kill_job.add_argument('job_id',
                          help='specify the job_id to kill')

    kill_job.add_argument('-d', '--deployment',
                          default=None,
                          help='specify the deployment name')

    kill_job.add_argument('-a', '--app-url',
                          default=defaults.APP_URL,
                          help='app url (default: https://app.jut.io INTERNAL USE)')

    kill_job.add_argument('-y', '--yes',
                          action='store_true',
                          default=False,
                          help='kill without prompting for confirmation')

    connect_job = jobs_commands.add_parser('connect',
                                           help='connect to a persistent job')

    connect_job.add_argument('job_id',
                             help='specify the job_id to connect to')

    connect_job.add_argument('-d', '--deployment',
                             default=None,
                             help='specify the deployment name')

    connect_job.add_argument('-a', '--app-url',
                             default=defaults.APP_URL,
                             help='app url (default: https://app.jut.io INTERNAL USE)')

    connect_job.add_argument('-s', '--show-progress',
                             action='store_true',
                             default=False,
                             help='writes the progress out to stderr on how '
                                  'many points were streamed thus far')

    connect_job.add_argument('--retry',
                             type=int,
                             default=0,
                             help='retry running the program N times,'
                                  'default 0. Use -1 to retry forever.')

    connect_job.add_argument('--retry-delay',
                             type=int,
                             default=10,
                             help='number of seconds to wait between retries.')

    connect_job.add_argument('-f', '--format',
                             default='json',
                             help='available formats are json, text, csv with '
                                  'default: json')

    # programs commands
    programs_parser = commands.add_parser('programs',
                                          help='programs management')

    programs_commands = programs_parser.add_subparsers(dest='programs_subcommand')

    list_programs = programs_commands.add_parser('list',
                                                 help='list programs')

    list_programs.add_argument('-d', '--deployment',
                               default=None,
                               help='specify the deployment name')

    list_programs.add_argument('-a', '--app-url',
                               default=defaults.APP_URL,
                               help='app url (default: https://app.jut.io INTERNAL USE)')

    list_programs.add_argument('-f', '--format',
                               default='table',
                               help='available formats are text, table with '
                                    'default: table')

    list_programs.add_argument('--all',
                               default=False,
                               help='list all programs, default is to list your'
                                    ' own programs')

    run_programs = programs_commands.add_parser('run',
                                                help='run a program in your local browser')

    run_programs.add_argument('program_name',
                              help='specify the program name you wish to kick off')


    pull_programs = programs_commands.add_parser('pull',
                                                 help='pull programs')

    pull_programs.add_argument('directory',
                               help='directory to pull remote programs into')

    pull_programs.add_argument('-d', '--deployment',
                               default=None,
                               help='specify the deployment name')

    pull_programs.add_argument('-a', '--app-url',
                               default=defaults.APP_URL,
                               help='app url (default: https://app.jut.io INTERNAL USE)')

    pull_programs.add_argument('-p', '--per-user-directory',
                               action='store_true',
                               default=False,
                               help='save the programs per user into a '
                                    'separate directory')

    pull_programs.add_argument('--all',
                               action='store_true',
                               default=False,
                               help='pull all programs, default is to list your'
                                    ' own programs')

    push_programs = programs_commands.add_parser('push',
                                                 help='push programs')

    push_programs.add_argument('directory',
                               help='directory to pick up programs to push to '
                                    'the running Jut instance')

    push_programs.add_argument('-d', '--deployment',
                               default=None,
                               help='specify the deployment name')

    push_programs.add_argument('-a', '--app-url',
                               default=defaults.APP_URL,
                               help='app url (default: https://app.jut.io INTERNAL USE)')

    push_programs.add_argument('--all',
                               default=False,
                               help='pull all programs, default is to list your'
                                    ' own programs')


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
                            help='available formats are json, text, csv with '
                                 'default: json')

    run_parser.add_argument('-n', '--name',
                            help='give your program a name to appear in the '
                                 'Jobs application')

    run_parser.add_argument('-p', '--persist',
                            action='store_true',
                            default=False,
                            help='allow the program containing background '
                                 'outputs to become a persistent job by '
                                 'disconnecting form the running job (ie '
                                 'essentially backgrounding your program)')

    run_parser.add_argument('-s', '--show-progress',
                            action='store_true',
                            default=False,
                            help='writes the progress out to stderr on how '
                                 'many points were streamed thus far')

    run_parser.add_argument('--retry',
                            type=int,
                            default=0,
                            help='retry running the program N times,'
                                 'default 0. Use -1 to retry forever.')

    run_parser.add_argument('--retry-delay',
                            type=int,
                            default=10,
                            help='number of seconds to wait between retries.')

    options = parser.parse_args()

    try:
        if options.subcommand == 'config':
            if options.config_subcommand == 'list':
                config.show()

            elif options.config_subcommand == 'add':
                configs.add_configuration(options)

            elif options.config_subcommand == 'rm':
                configs.rm_configuration(options)

            elif options.config_subcommand == 'defaults':
                configs.change_defaults(options)

            else:
                raise Exception('Unexpected config subcommand "%s"' % options.command)

        elif options.subcommand == 'jobs':
            if options.jobs_subcommand == 'list':
                jobs.list(options)

            elif options.jobs_subcommand == 'kill':
                jobs.kill(options)

            elif options.jobs_subcommand == 'connect':
                jobs.connect(options)

            else:
                raise Exception('Unexpected jobs subcommand "%s"' % options.command)

        elif options.subcommand == 'programs':
            if options.programs_subcommand == 'list':
                programs.list(options)

            elif options.programs_subcommand == 'pull':
                programs.pull(options)

            elif options.programs_subcommand == 'push':
                programs.push(options)
            
            elif options.programs_subcommand == 'run':
                programs.run(options)

            else:
                raise Exception('Unexpected programs subcommand "%s"' % options.command)

        elif options.subcommand == 'upload':
            upload.upload_file(options)

        elif options.subcommand == 'run':
            run.run_juttle(options)

        else:
            raise Exception('Unexpected jut command "%s"' % options.command)

    except JutException as exception:
        if is_debug_enabled():
            traceback.print_exc()

        error(str(exception))
        sys.exit(255)


if __name__ == '__main__':
    main()
