#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re

from setuptools import setup, find_packages

VERSION_REGEX = '^__version__ = \'(.*)\'$'


def get_version():
    with open('freeswitch_testsuite/__init__.py') as f:
        return re.search(VERSION_REGEX, f.read()).group(1)


with open('README.md', encoding='utf-8') as f:
    readme = f.read()

setup(
    name='freeswitch_testsuite',
    version=get_version(),
    description=u'Testsuite for Taxi-FreeSWITCH',
    long_description=readme,
    author=u'Denis Fokin',
    author_email=u'sanvean@yandex-team.ru',
    url=u'https://a.yandex-team.ru/arc/trunk/arcadia/noc/iptel/tanya'
        u'/freeswitch_testsuite',
    packages=find_packages(exclude=('tests', 'docs')),
    install_requires=[
        'aiohttp',
        'grpcio',
        'pjsua2==2.11-ya-fs-ts',
        'protobuf',
        'termcolor'
    ],
    entry_points={
        'console_scripts': [
            'run_tests = freeswitch_testsuite.run_tests:main',
            'speechkit_mock = freeswitch_testsuite.speechkit:main',
        ],
    }
)
