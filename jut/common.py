"""
"""

import sys

DEBUG = False

def info(message, *kwargs):
    if len(kwargs) == 0:
        sys.stdout.write(message)
    else:
        sys.stdout.write(message % kwargs)
    sys.stdout.write('\n')
    sys.stdout.flush()

def error(message, *kwargs):
    if len(kwargs) == 0:
        sys.stderr.write(message)
    else:
        sys.stderr.write(message % kwargs)
    sys.stderr.write('\n')
    sys.stderr.flush()

def debug(message, *kwargs):
    if DEBUG: 
        if len(kwargs) == 0:
            sys.stdout.write(message)
        else:
            sys.stdout.write(message % kwargs)
        sys.stdout.write('\n')
        sys.stdout.flush()
