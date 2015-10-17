"""
jut internal configuration module

"""

import ConfigParser
import os

from os.path import expanduser

from jut import defaults
from jut.common import info
from jut.exceptions import JutException

_CONFIG = None
_CONFIG_FILEPATH = None
_JUT_HOME = None


def init():
    global _CONFIG, _CONFIG_FILEPATH, _JUT_HOME

    _CONFIG = ConfigParser.RawConfigParser()

    # HOME_OVERRIDE for testing purposes
    if os.environ.get('HOME_OVERRIDE') != None:
        _JUT_HOME = os.environ.get('HOME_OVERRIDE')
    else:
        home = expanduser('~')
        _JUT_HOME = os.path.join(home, '.jut')

    if not os.path.exists(_JUT_HOME):
        os.makedirs(_JUT_HOME)

    _CONFIG_FILEPATH = os.path.join(_JUT_HOME, 'config')

    if os.path.exists(_CONFIG_FILEPATH):
        _CONFIG.read(_CONFIG_FILEPATH)


def show():
    """
    print the available configurations directly to stdout

    """
    if not is_configured():
        raise JutException('No configurations available, please run: `jut config add`')

    info('Available jut configurations:')
    index = 0
    for configuration in _CONFIG.sections():
        username = _CONFIG.get(configuration, 'username')
        app_url = _CONFIG.get(configuration, 'app_url')

        if app_url != defaults.APP_URL:
            if _CONFIG.has_option(configuration, 'default'):
                info(' %d: %s@%s (default)', index + 1, username, app_url)
            else:
                info(' %d: %s@%s', index + 1, username, app_url)

        else:
            if _CONFIG.has_option(configuration, 'default'):
                info(' %d: %s (default)' % (index + 1, username))
            else:
                info(' %d: %s' % (index + 1, username))

        index += 1


def is_configured():
    return len(_CONFIG.sections()) > 0


def length():
    return len(_CONFIG.sections())


def set_default(name=None, index=None):
    """
    set the default configuration by name

    """
    default_was_set = False
    count = 1

    for configuration in _CONFIG.sections():
        if index != None:
            if count == index:
                _CONFIG.set(configuration, 'default', True)
                default_was_set = True
            else:
                _CONFIG.remove_option(configuration, 'default')

        if name != None:
            if configuration == name:
                _CONFIG.set(configuration, 'default', True)
                default_was_set = True
            else:
                _CONFIG.remove_option(configuration, 'default')

        count += 1

    if not default_was_set:
        raise JutException('Unable to find %s configuration' % name)

    with open(_CONFIG_FILEPATH, 'w') as configfile:
        _CONFIG.write(configfile)

    info('Configuration updated at %s' % _JUT_HOME)

def exists(name):
    """
    """
    return _CONFIG.has_section(name)

def add(name, **kwargs):
    """
    add a new configuration with the name specified and all of the keywords
    as attributes of that configuration.

    """
    _CONFIG.add_section(name)

    for (key, value) in kwargs.items():
        _CONFIG.set(name, key, value)

    with open(_CONFIG_FILEPATH, 'w') as configfile:
        _CONFIG.write(configfile)

    info('Configuration updated at %s' % _JUT_HOME)


def get_default():
    """
    return the attributes associated with the default configuration

    """

    if not is_configured():
        raise JutException('No configurations available, please run `jut config add`')

    for configuration in _CONFIG.sections():
        if _CONFIG.has_option(configuration, 'default'):
            return dict(_CONFIG.items(configuration))


def remove(name=None, index=None):
    """
    remove the specified configuration

    """

    removed = False
    count = 1
    for configuration in _CONFIG.sections():
        if index != None:
            if count == index:
                _CONFIG.remove_section(configuration)
                removed = True
                break

        if name != None:
            if configuration == name:
                _CONFIG.remove_section(configuration)
                removed = True
                break

        count += 1

    if not removed:
        raise JutException('Unable to find %s configuration' % name)

    with open(_CONFIG_FILEPATH, 'w') as configfile:
        _CONFIG.write(configfile)


def is_default(name=None, index=None):
    """
    returns True if the specified configuration is the default one

    """

    if not is_configured():
        raise JutException('No configurations available, please run `jut config add`')

    count = 1
    for configuration in _CONFIG.sections():

        if index != None:
            if _CONFIG.has_option(configuration, 'default') and count == index:
                return True

        if name != None:
            if _CONFIG.has_option(configuration, 'default') and configuration == name:
                return True

        count += 1

    return False

init()
