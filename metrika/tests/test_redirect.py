# -*- coding: utf-8 -*-
from flask.testing import FlaskClient
from nose.tools import (
    eq_,
)
from unittest2 import TestCase

from passport.test.utils import with_settings

from app import create_app

from common.utils import get_safe_url

from .fake_db import FakeClickerDB

from .test_data import *


@with_settings(
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
    ],
    SHARED_DOMAINS=[],
    SEARCH_INDEX_ENABLED=False,
    SAFETY={
        'client_id': 'clck',
        'key': 'f2312d4b7e97d5d214aba45114196b74',
        'url': 'https://sba.yandex.net/redirect?url={url}&client={client}&sign={sign}',
    },
    MAX_URL_LENGTH=4096,
)
class TestRedirectView(TestCase):

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

    def make_request(self, url=None, method='get', query_string=None, remote_addr=TEST_USER_IP, headers=None):
        url = url or self.url
        kwargs = {
            'query_string': query_string,
            'headers': headers,
            'environ_base': {'REMOTE_ADDR': remote_addr},
        }
        return getattr(self.client, method)(url, **kwargs)

    def test__ok(self):
        resp = self.make_request(url='/1')
        eq_(resp.status_code, 302)
        eq_(resp.headers.get('Location'), get_safe_url('http://bobuk.habrahabr.ru/blog/43619.html'))

    def test_not_found__ok(self):
        resp = self.make_request(url='/A')
        eq_(resp.status_code, 404)

    def test_disk__ok(self):
        self.make_request(url='/--', query_string={'url': 'https://disk.yandex.ru', 'type': 'yadisk'})
        resp = self.make_request(url='/d/iTmH2iRU2')
        eq_(resp.status_code, 302)
        eq_(resp.headers.get('Location'), get_safe_url('https://disk.yandex.ru'))

    def test_blocked__ok(self):
        resp = self.make_request(url='/0')
        eq_(resp.status_code, 406)

    def test_short_sensitive__not_allowed(self):
        template_name = '-'  # любой неизвестный непустой
        self.make_request(url='/--', query_string={'url': 'https://ofd.yandex.ru/vaucher/gimmemoney', 'type': template_name})
        resp = self.make_request(url='/2')
        eq_(resp.status_code, 404)
