"""

"""

import os
import sys
import tempfile

from jut.common import info, error


def init():
    """
    initialize the testing configuration

    """

    # set PYTHONPATH to the cwd directory because we want to test this
    # source and not any installed version of the jut tools
    os.environ.setdefault('PYTHONPATH', '.')

    if os.environ.get('JUT_USER') == None or \
    os.environ.get('JUT_PASS') == None:
        info('')
        info('You need to set JUT_USER and JUT_PASS to a valid jut admin user ')
        info('like so:')
        info('')
        info(' JUT_USER=username JUT_PASS=password python setup.py test')
        info('')
        sys.exit(1)

    info('')
    info('*'*80)
    info('During testing we will create a few test accounts and spaces to ')
    info('verify different features in the jut-tools. We will do our best to ')
    info('clean those up but if you see anything starting with jut-tools you ')
    info('will now that was left behind by the unit tests here')
    info('*'*80)
    info('')

    # we set the HOME_OVERRIDE for testing
    os.environ.setdefault('HOME_OVERRIDE', tempfile.mkdtemp())

    # configure the default account
    setup_command = 'python jut/cli.py config add -u %s -p %s -d' % \
                    (os.environ.get('JUT_USER'), os.environ.get('JUT_PASS'))

    if os.environ.get('JUT_APP_URL') != None:
        setup_command += ' -a "%s"' % os.environ.get('JUT_APP_URL')

    if os.system(setup_command) != 0:
        error('Failed to create testing configuration')
        sys.exit(-1)

init()
