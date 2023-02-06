# -*- coding: utf-8 -*-
from flask.testing import FlaskClient

import mock
from nose.tools import (
    eq_,
    ok_,
)
from unittest2 import TestCase

from passport.test.utils import (
    with_settings,
    settings_context
)

from app import create_app

from .fake_db import FakeClickerDB
from .test_data import *

import sqlalchemy.exc

from clck_db.connection import (
    DBError,
    get_db_connection,
)


@with_settings(
    YANDEX_TEAM_DOMAIN='yandex-team.ru',
    PING_TEST_FILE='ping.html',
    #DB_CONFIG = {
    #    'master': {
    #        'host': 'cnt-dbm-test.passport.yandex.net',
    #        'port': 3306,
    #        'driver': 'mysql',
    #    },
    #},
    #DB_CREDENTIALS={
    #    'clckdb': {
    #        'db_user': '',
    #        'db_password': '',
    #    },
    #},
)
class TestPingView(TestCase):
    url = '/-ping-'

    def setUp(self):
        app = create_app()
        app.test_client_class = FlaskClient
        app.testing = True
        self.client = app.test_client()

        self.patches = []
        self.db = FakeClickerDB()

        self.db_mock = mock.Mock(return_value=self.db.db)

        self.patches.append(
            mock.patch(
                'os.access',
                side_effect=lambda filepath, mode: filepath == 'ping.html',
            ),
        )
        self.patches.append(self.db)
        #self.patches.append(mock.patch('clck_db.connection.get_db_connection', self.db_mock))
        self.patches.append(mock.patch('clck_db.connection.LazyLoader.get_instance', self.db_mock))
        for patch in self.patches:
            patch.start()

        #self.db.load_initial_data()

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

    def test_ping_ok(self):
        resp = self.make_request(url='/-ping-')
        eq_(resp.status_code, 200, msg='Got response: code="{0}", data="{1}"'.format(resp.status_code, resp.data))
        eq_(resp.data, 'Pong\n')

    def test_ping_no_ping_file(self):
        with settings_context(PING_TEST_FILE='pong.html'):
            resp = self.make_request(url='/-ping-')
            eq_(resp.status_code, 503, msg='Got response: code="{0}", data="{1}"'.format(resp.status_code, resp.data))
            print resp.data

    def test_ping_db_fail(self):
        connect_mock = mock.Mock()
        for side_effect in (
            sqlalchemy.exc.DatabaseError('', '', ''),
            sqlalchemy.exc.InterfaceError('', '', ''),
        ):
            connect_mock.side_effect = side_effect
            connect_mock.reset_mock()

            connect_patch = mock.patch('sqlalchemy.engine.Engine.connect', connect_mock)
            connect_patch.start()

            resp = self.make_request(url='/-ping-')
            eq_(connect_mock.called, True)
            eq_(resp.status_code, 503, msg='Got response: code="{0}", data="{1}"'.format(resp.status_code, resp.data))

            connect_patch.stop()
