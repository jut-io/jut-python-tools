"""
setup script

"""

from setuptools import setup, find_packages

setup(
    name='jut-tools',
    version='0.1',
    author='Rodney Gomes',
    author_email='rodney@jut.io',
    url='https://github.com/jut-io/jut-python-tools',
    download_url='https://github.com/jut-io/jut-python-tools/tarball/0.1',

    install_requires=[
        'requests==2.7.0',
        'websocket-client==0.29.0',
        'memoized==0.2'
    ],

    test_suite='tests',
    tests_install=[
        'sh==1.11'
    ],

    keywords=[''],

    packages=find_packages(exclude=['tests']),
    license='Apache 2.0 License',
    description='',
    long_description=open('README.md').read(),

    include_package_data=True,
    zip_safe=False,

    entry_points={
        'console_scripts': [
            'jut = jut.cli:main'
        ]
    },
)

