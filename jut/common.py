"""
"""

import sys
import os

DEBUG = os.environ.get('JUT_DEBUG', False)

def info(message, *args, **kwargs):
    """
    write a message to stdout

    """
    if 'end' in kwargs:
        end = kwargs['end']
    else:
        end = '\n'

    if len(args) == 0:
        sys.stdout.write(message)
    else:
        sys.stdout.write(message % args)
    sys.stdout.write(end)
    sys.stdout.flush()


def error(message, *args, **kwargs):
    """
    write a message to stderr

    """
    if 'end' in kwargs:
        end = kwargs['end']
    else:
        end = '\n'

    if len(args) == 0:
        sys.stderr.write(message)
    else:
        sys.stderr.write(message % args)
    sys.stderr.write(end)
    sys.stderr.flush()


def debug(message, *args, **kwargs):
    """
    debug output goes to stderr so you can still redirect the stdout to a file
    or another program. Controlled by the JUT_DEBUG environment variable being
    present

    """
    if 'end' in kwargs:
        end = kwargs['end']
    else:
        end = '\n'

    if DEBUG: 
        if len(args) == 0:
            sys.stderr.write(message)
        else:
            sys.stderr.write(message % args)

        sys.stderr.write(end)
        sys.stderr.flush()


def is_debug_enabled():
    """
    useful method to know if debug is enabled or not and avoid constructing
    costly messages to pass to the debug method itself

    """
    return DEBUG
