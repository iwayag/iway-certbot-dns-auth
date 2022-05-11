#!/usr/bin/env python

import os

from setuptools import find_packages, setup
from pip._internal.req import parse_requirements
from collections import defaultdict


def text_of(relpath):
    thisdir = os.path.dirname(__file__)
    file_path = os.path.join(thisdir, os.path.normpath(relpath))
    with open(file_path) as f:
        text = f.read()
    return text


NAME = 'iway-certbot-dns-auth'
VERSION = '0.1.0'
DESCRIPTION = 'Certbot hook for DNS challenge using iWay Portal API.'
KEYWORDS = 'certbot'
AUTHOR = 'Frank Bohnsack'
AUTHOR_EMAIL = 'frank.bohnsack@iway.ch'
URL = 'https://github.com/iwayag/iway-certbot-dns-auth'
LICENSE = text_of('LICENSE')
PACKAGES = find_packages(exclude=['tests', 'tests.*'])
PACKAGE_DATA = {}
DEPENDENCY_LINKS = []
INSTALL_REQUIRES = []
EXTRAS_REQUIRES = defaultdict(list)
for r in parse_requirements('requirements.txt', session='hack'):
    INSTALL_REQUIRES.append(str(r.req if hasattr(r, 'req') else r.requirement))
TESTS_REQUIRE = [
    str(r.req if hasattr(r, 'req') else r.requirement)
    for r in parse_requirements('requirements-test.txt', session='hack')
]
SETUP_REQUIRES = []
TEST_SUITE = 'tests'
CLASSIFIERS = [
    'Environment :: Console',
    'Intended Audience :: Developers',
    'Operating System :: OS Independent',
    'Programming Language :: Python :: 3.6',
]

params = {
    'name':                 NAME,
    'version':              VERSION,
    'description':          DESCRIPTION,
    'keywords':             KEYWORDS,
    'author':               AUTHOR,
    'author_email':         AUTHOR_EMAIL,
    'url':                  URL,
    'license':              LICENSE,
    'packages':             PACKAGES,
    'package_data':         PACKAGE_DATA,
    'include_package_data': True,
    'install_requires':     INSTALL_REQUIRES,
    'extras_require':       EXTRAS_REQUIRES,
    'dependency_links':     DEPENDENCY_LINKS,
    'setup_requires':       SETUP_REQUIRES,
    'tests_require':        TESTS_REQUIRE,
    'test_suite':           TEST_SUITE,
    'classifiers':          CLASSIFIERS,
}

setup(**params)
