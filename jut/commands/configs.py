"""
jut config command

"""

from jut import config

from jut.api import auth, authorizations, deployments
from jut.common import info
from jut.exceptions import JutException
from jut.util.console import prompt


def default_deployment(app_url, client_id, client_secret):
    """
    """
    if app_url.strip() == '':
        app_url = 'https://app.jut.io'

    token_manager = auth.TokenManager(client_id=client_id,
                                      client_secret=client_secret,
                                      app_url=app_url)

    user_deployments = deployments.get_deployments(token_manager=token_manager,
                                                   app_url=app_url)

    if len(user_deployments) > 1:
        index = 0
        for deployment in user_deployments:
            info(' %d: %s', index + 1, deployment['name'])
            index += 1

        which = prompt('Pick default deployment from above: ')

        return user_deployments[int(which)-1]['name']
    else:
        return user_deployments[0]['name']


def default_configuration(interactive=True):
    if config.length() == 1:
        # when there is only one configuration, that should be the default one
        config.set_default(index=1)

    else:
        if interactive:
            info('Pick a default configuration from the list below')
            config.show()
            which = prompt('Set default configuration to: ')
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
        username = prompt('Username: ')

    if options.password != None:
        password = options.password
    else:
        password = prompt('Password: ', hide_input=not options.show_password)

    if options.app_url != None:
        app_url = options.app_url
    else:
        app_url = prompt('App URL (default: https://app.jut.io just hit enter): ')

    if app_url.strip() == '':
        app_url = 'https://app.jut.io'

    section = '%s@%s' % (username, app_url)

    if config.exists(section):
        raise JutException('Configuration for "%s" already exists' % section)

    token_manager = auth.TokenManager(username=username,
                                      password=password,
                                      app_url=app_url)

    authorization = authorizations.get_authorization(token_manager,
                                                     app_url=app_url)
    client_id = authorization['client_id']
    client_secret = authorization['client_secret']

    deployment_name = default_deployment(app_url,
                                         client_id,
                                         client_secret)

    config.add(section, **{
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


def rm_configuration(options):
    was_default = False

    if options.username != None:
        configuration = '%s@%s' % (options.username, options.app_url)
        was_default = config.is_default(name=configuration)
        config.remove(name=configuration)

    else:
        config.show()
        which = prompt('Which configuration to remove: ')
        which = int(which)
        was_default = config.is_default(index=which)
        config.remove(index=which)

    if was_default:
        default_configuration()


def change_defaults(options):
    if options.username != None:
        configuration = '%s@%s' % (options.username, options.app_url)
        config.set_default(name=configuration)
        configuration = config.get_default()

    else:
        config.show()
        which = prompt('Set default configuration to: ')
        config.set_default(index=int(which))
        configuration = config.get_default()

    default_deployment(configuration['app_url'],
                       configuration['client_id'],
                       configuration['client_secret'])

