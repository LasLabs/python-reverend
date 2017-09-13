# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from setuptools import Command, setup
from setuptools import find_packages
from unittest import TestLoader, TextTestRunner

from os import environ, path


PROJECT = 'reverend'
SHORT_DESC = 'Reverend is a general purpose Bayesian classifier ' \
             'python module.'
README_FILE = 'README.rst'

CLASSIFIERS = [
    "Development Status :: 7 - Inactive",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: GNU Library or Lesser General Public"
    " License (LGPL)",
    "Natural Language :: English",
    "Programming Language :: Python",
    "Topic :: Communications :: Email :: Filters",
    "Topic :: Software Development :: Libraries :: Python Modules",
    "Topic :: Text Processing",
]

version = environ.get('RELEASE') or environ.get('VERSION') or '0.0.0'

if environ.get('TRAVIS_BUILD_NUMBER'):
    version += 'b%s' % environ.get('TRAVIS_BUILD_NUMBER')


setup_vals = {
    'name': PROJECT,
    'author': 'Amir Bakhtiar',
    'author_email': 'amir hat divmod point org',
    'maintainer': 'LasLabs Inc.',
    'maintainer_email': 'support@laslabs.com',
    'description': SHORT_DESC,
    'url': 'https://laslabs.github.io/python-%s' % PROJECT,
    'download_url': 'https://github.com/LasLabs/python-%s' % PROJECT,
    'license': 'MIT',
    'classifiers': CLASSIFIERS,
    'version': version,
}


if path.exists(README_FILE):
    with open(README_FILE) as fh:
        setup_vals['long_description'] = fh.read()


install_requires = []
if path.exists('requirements.txt'):
    with open('requirements.txt') as fh:
        install_requires = fh.read().splitlines()


class FailTestException(Exception):
    """ It provides a failing build """
    pass


class Tests(Command):
    """ Run test & coverage, save reports as XML """

    user_options = []  # < For Command API compatibility

    def initialize_options(self, ):
        pass

    def finalize_options(self, ):
        pass

    def run(self, ):
        loader = TestLoader()
        tests = loader.discover('.', 'test_*.py')
        t = TextTestRunner(verbosity=1)
        res = t.run(tests)
        if not res.wasSuccessful():
            raise FailTestException()


if __name__ == "__main__":
    setup(
        packages=find_packages(exclude=('tests')),
        cmdclass={'test': Tests},
        tests_require=[
            'mock',
        ],
        install_requires=install_requires,
        **setup_vals
    )
