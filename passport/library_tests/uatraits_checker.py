# -*- coding: utf-8 -*-
from collections import namedtuple
from itertools import groupby
import json
import unittest

from passport.backend.libs_checker.environment import StagingEnvironment


_browser = namedtuple('browser', 'id name')
_os = namedtuple('os', 'id name version')


def load(filename):
    with open(filename, 'r') as f:
        return json.load(f)


def filter_unknown(value):
    return None if value == 'Unknown' else value


def init_browsers(filename=None):
    browsers = tuple(
        _browser(id=record['id'], name=filter_unknown(record['BrowserName']))
        for record in load(filename or StagingEnvironment.env['uatraits']['browser_data'])
    )
    browser_encode = dict((browser.name, browser.id) for browser in browsers)
    browser_decode = dict((browser.id, browser.name) for browser in browsers)
    return browser_encode, browser_decode


def init_oses(filename=None):
    oses = tuple(
        _os(
            id=record['id'],
            name=filter_unknown(record.get('OSName')) or filter_unknown(record.get('OSFamily')),
            version=filter_unknown(record.get('OSVersion')),
        )
        for record in load(filename or StagingEnvironment.env['uatraits']['os_data'])
    )
    os_encode = dict(((os.name, os.version), os.id) for os in oses if os.name)
    os_dumb_encode = dict(
        (name, list(oses)[0].id)
        for name, oses in groupby(
            sorted(oses, key=lambda x: x.name or ''),
            lambda x: x.name,
        )
        if name
    )
    os_decode = dict((os.id, (os.name, os.version)) for os in oses)

    return os_encode, os_dumb_encode, os_decode


class TestUATraits(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.BROWSER_ENCODE, cls.BROWSER_DECODE = init_browsers()
        cls.OS_ENCODE, cls.OS_DUMB_ENCODE, cls.OS_DECODE = init_oses()

    def test_browser_data(self):
        assert all(value in self.BROWSER_DECODE.keys() for value in self.BROWSER_ENCODE.values())

    def test_os_data(self):
        assert all(value in self.OS_DECODE.keys() for value in self.OS_ENCODE.values())

    def test_os_dumb_data(self):
        assert all(value in self.OS_DECODE.keys() for value in self.OS_DUMB_ENCODE.values())
