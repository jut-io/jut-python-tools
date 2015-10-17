"""
console utilities

"""

import getpass
import sys

def prompt(message, hide_input=False):
    """
    """
    if hide_input:
        sys.stdout.write(message)
        sys.stdout.flush()
        return getpass.getpass(prompt='')

    else:
        sys.stdout.write(message)
        sys.stdout.flush()
        return raw_input()


