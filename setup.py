"""
setup script

"""

from setuptools import setup, find_packages

_VERSION = '0.8'

setup(
    name='jut-tools',
    version=_VERSION,
    author='Rodney Gomes',
    author_email='rodney@jut.io',
    url='https://github.com/jut-io/jut-python-tools',
    download_url='https://github.com/jut-io/jut-python-tools/tarball/%s' % _VERSION,

    install_requires=[
        'requests==2.7.0',
        'websocket-client==0.32.0',
        'memoized==0.2',
        'tabulate==0.7.5'
    ],

    test_suite='tests',
    keywords=[''],

    packages=find_packages(exclude=['tests']),
    license='MIT License',
    description='jut command line tools',

    # pypi doesn't support markdown so we can't push the README.md as is
    long_description='https://github.com/jut-io/jut-python-tools/blob/master/README.md',

    include_package_data=True,
    zip_safe=False,

    entry_points={
        'console_scripts': [
            'jut = jut.cli:main'
        ]
    },
)

