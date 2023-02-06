# -*- coding: utf-8 -*-
import json
from urlparse import urljoin

from flask.testing import FlaskClient
from nose.tools import (
    eq_,
    ok_,
)
from unittest2 import TestCase

from passport.test.utils import (
    settings_context,
    with_settings,
)

from app import create_app

from .fake_db import FakeClickerDB
from .test_data import *


DEFAULT_SETTINGS = dict(
    YANDEX_TEAM_DOMAIN='yandex-team.ru',
    URL_MAP={},
    DEFAULT_URL=TEST_DEFAULT_URL,
    UI_URL=TEST_DEFAULT_URL,
    LIMITS=[
        {
            'type': 'list',
            'name': 'blacklist',
            'action': 'reject',
        },
        {
            'type': 'list',
            'name': 'whitelist',
            'action': 'accept',
        },
        {
            'type': 'ratelimit',
            'period': 600,
            'window': 60,
            'limit': 10,
            'action': 'reject',
        },
    ],
    TEMPLATES=[
        {
            'code': 5002,
            'name': 'd',
            'type': 'disk',
            'selectable_as': 'yadisk',
        },
{
            'code': 5003,
            'name': 't',
            'type': 'disk',
            'selectable_as': 'ticket',
        },
    ],
    SHARED_DOMAINS=[],
    SEARCH_INDEX_ENABLED=False,
    MAX_URL_LENGTH=200,
    FORBID_SHORT_LINKS_BY_DEFAULT=False,
)


@with_settings(**DEFAULT_SETTINGS)
class TestShortenView(TestCase):
    url = '/--'

    def setUp(self):
        app = create_app()
        app.test_client_class = FlaskClient
        app.testing = True
        self.client = app.test_client()

        self.patches = []
        self.db = FakeClickerDB()
        self.patches.append(self.db)

        for patch in self.patches:
            patch.start()

        self.db.load_initial_data()

    def tearDown(self):
        for patch in reversed(self.patches):
            patch.stop()

    def make_request(self, url=None, method='get', query_string=None,
                     data=None, remote_addr=TEST_USER_IP, headers=None):
        url = url or self.url
        kwargs = {
            'query_string': query_string,
            'data': data,
            'headers': headers,
            'environ_base': {'REMOTE_ADDR': remote_addr},
        }
        return getattr(self.client, method)(url, **kwargs)

    def assert_ok_response(self, resp, url=TEST_DEFAULT_URL, with_json=False, not_changed=False):
        eq_(resp.status_code, 200)
        if with_json:
            eq_(resp.data, json.dumps([url, not_changed]))
        else:
            eq_(resp.data, url)

    def assert_error_response(self, resp, status_code=200):
        eq_(resp.status_code, status_code)
        ok_('Ссылка не соответствует ограничениям сервиса' in resp.data)

    def test__ok(self):
        resp = self.make_request(query_string={'url': TEST_NEW_URL}, method='post')
        self.assert_ok_response(resp, urljoin(TEST_DEFAULT_URL, '/2'))

    def test_long_url_by_default__ok(self):
        with settings_context(**dict(DEFAULT_SETTINGS, FORBID_SHORT_LINKS_BY_DEFAULT=True)):
            resp = self.make_request(query_string={'url': TEST_NEW_URL}, method='post')
        self.assert_ok_response(resp, urljoin(TEST_DEFAULT_URL, '/t/SVwM8LSX2'))

    def test_force_short_url__ok(self):
        with settings_context(**dict(DEFAULT_SETTINGS, FORBID_SHORT_LINKS_BY_DEFAULT=True)):
            resp = self.make_request(query_string={'url': TEST_NEW_URL, 'type': 'simple'}, method='post')
        self.assert_ok_response(resp, urljoin(TEST_DEFAULT_URL, '/2'))

    def test_json__ok(self):
        resp = self.make_request(query_string={'url': TEST_NEW_URL, 'json': 'yes'}, method='post')
        self.assert_ok_response(resp, urljoin(TEST_DEFAULT_URL, '/2'), with_json=True)

    def test_invalid_url__ok(self):
        resp = self.make_request(query_string={'url': ''})
        self.assert_error_response(resp)

    def test_shortened_url__ok(self):
        resp = self.make_request(query_string={'url': 'https://bit.ly/AbcD'})
        self.assert_ok_response(resp, 'https://bit.ly/AbcD')

    def test_nda__error(self):
        resp = self.make_request(query_string={'url': 'https://wiki.yandex-team.ru/yapic'}, headers={'X-Is-Ext': 'True'})
        self.assert_error_response(resp)

    def test_existing__ok(self):
        resp = self.make_request(query_string={'url': TEST_EXISTING_URL})
        self.assert_ok_response(resp, urljoin(TEST_DEFAULT_URL, '/0'))
        self.db.assert_db()

    def test_existing_but_other_type__ok(self):
        resp = self.make_request(query_string={'url': TEST_EXISTING_URL,  'type': 'yadisk'})
        self.assert_ok_response(resp, urljoin(TEST_DEFAULT_URL, '/d/-v0H0qTr2'))
        self.db.assert_db(total_count=3)

    def test_blacklisted__ok(self):
        resp = self.make_request(query_string={'url': 'https://banned.domain/test'})
        self.assert_error_response(resp)
        self.db.assert_db()

    def test_rate_limit__error(self):
        resp = self.make_request(query_string={'url': 'https://black.habrahabr.ru/test'})
        self.assert_error_response(resp)
        self.db.assert_db()

    def test_blacklist_whitelist__ok(self):
        self.db.assert_db()
        resp = self.make_request(query_string={'url': 'https://white.yandex.ru/test'})
        self.assert_ok_response(resp, urljoin(TEST_DEFAULT_URL, '/2'))
        self.db.assert_db(total_count=3, last_url='https://white.yandex.ru/test')

    def test_disk__ok(self):
        resp = self.make_request(query_string={'url': 'https://disk.yandex.ru', 'type': 'yadisk'})
        self.assert_ok_response(resp, urljoin(TEST_DEFAULT_URL, '/d/iTmH2iRU2'))
