# -*- coding: utf-8 -*-
from collections import namedtuple
from unittest import TestCase

from flask.testing import FlaskClient
import mock
import MySQLdb
from nose.tools import eq_
from passport.backend.core.lazy_loader import LazyLoader
from passport.backend.core.test.test_utils.utils import (
    settings_context,
    with_settings,
)
from passport.backend.library.configurator.test import FakeConfig
from passport.infra.daemons.yasmsapi.api.app import create_app
from passport.infra.daemons.yasmsapi.db.config import (
    DB_QUEUE,
    DB_VALIDATOR,
    DEFAULT_CONFIGS,
)
from passport.infra.daemons.yasmsapi.db.connection import get_db_connection
import sqlalchemy.exc

from .fake_db import FakeYasmsDB


_host = namedtuple('host', 'name id dc')


@with_settings(
    CURRENT_FQDN='yasms-dev.passport.yandex.net',
    HOSTS=[_host(name='yasms-dev.passport.yandex.net', id=0x7F, dc='i')],
)
class PingTestCase(TestCase):
    url = '/ping'

    def setUp(self):
        self.fake_config = FakeConfig(
            'passport.infra.daemons.yasmsapi.api.configs.config',
            {
                'ping_test_file': '/usr/lib/yandex/yasms/ping.html',
                'daemon_heartbeat_period': 2,
                'daemon_heartbeat_delta': 2,
                'current_fqdn': 'yasms-dev.passport.yandex.net',
                'hosts': [_host(name='yasms-dev.passport.yandex.net', id=0x7F, dc='i')],
            },
        )
        self.fake_config.start()
        app = create_app()
        app.test_client_class = FlaskClient
        app.testing = True
        self.client = app.test_client()
        self.db = FakeYasmsDB()
        self.db.start()
        self.db.load_initial_data()

    def tearDown(self):
        self.db.stop()
        self.fake_config.stop()
        LazyLoader.flush('Host')

    def make_request(self, url=None, query=None):
        url = url or self.url
        return self.client.get(url, query_string=query)

    def assert_ok_response(self, resp):
        eq_(resp.status_code, 200)
        eq_(resp.data, 'Pong\n')

    def assert_error_response(self, resp, expected):
        eq_(resp.status_code, 503)
        eq_(resp.data, expected)

    def test_ok(self):
        resp = self.make_request()
        self.assert_ok_response(resp)

    def test_with_trailing_slash__ok(self):
        resp = self.make_request(url='{}/'.format(self.url))
        self.assert_ok_response(resp)

    def test_check_db_ok(self):
        connect_mock = mock.Mock()
        connect_mock.execute.return_value = True
        connect_mock.close.return_value = True
        with mock.patch.object(get_db_connection().get_engine(DB_VALIDATOR), 'connect', connect_mock):
            resp = self.make_request(query={'check': 'db,ignored '})
            self.assert_ok_response(resp)

    def test_daemon_is_dead(self):
        connect_mock = mock.Mock()
        connect_mock.execute.return_value = True
        connect_mock.close.return_value = True

        fqdn = 'phone-passport-dev.yandex.net'
        with FakeConfig(
            'passport.infra.daemons.yasmsapi.api.configs.config',
            {
                'ping_test_file': '/usr/lib/yandex/yasms/ping.html',
                'daemon_heartbeat_period': 1,
                'daemon_heartbeat_delta': 2,
                'current_fqdn': fqdn,
                'hosts': [_host(name=fqdn, id=0x7F, dc='i')],
            },
        ):
            with settings_context(
                CURRENT_FQDN=fqdn,
                HOSTS=[_host(name=fqdn, id=0x7F, dc='i')],
            ):
                with mock.patch.object(get_db_connection().get_engine(DB_VALIDATOR), 'connect', connect_mock):
                    resp = self.make_request(query={'check': 'db,daemon'})
                    errors = [
                        'Daemon is dead for %s' % fqdn,
                        'Daemon is unavailable',
                    ]
                    self.assert_error_response(resp, '\n'.join(errors))

    def test_daemon_is_dead_but_we_didnt_ask(self):
        connect_mock = mock.Mock()
        connect_mock.execute.return_value = True
        connect_mock.close.return_value = True

        fqdn = 'phone-passport-dev.yandex.net'
        with FakeConfig(
            'passport.infra.daemons.yasmsapi.api.configs.config',
            {
                'ping_test_file': '/usr/lib/yandex/yasms/ping.html',
                'daemon_heartbeat_period': 1,
                'daemon_heartbeat_delta': 2,
                'current_fqdn': fqdn,
                'hosts': [_host(name=fqdn, id=0x7F, dc='i')],
            },
        ):
            with settings_context(
                CURRENT_FQDN=fqdn,
                HOSTS=[_host(name=fqdn, id=0x7F, dc='i')],
            ):
                with mock.patch.object(get_db_connection().get_engine(DB_VALIDATOR), 'connect', connect_mock):
                    resp = self.make_request(query={'check': 'db'})
                    self.assert_ok_response(resp)

    def test_daemon_is_dead_and_validator_failed(self):
        connect_mock = mock.Mock()
        connect_mock.side_effect = sqlalchemy.exc.DatabaseError('', '', '')

        fqdn = 'phone-passport-dev.yandex.net'
        with FakeConfig(
            'passport.infra.daemons.yasmsapi.api.configs.config',
            {
                'ping_test_file': '/usr/lib/yandex/yasms/ping.html',
                'daemon_heartbeat_period': 1,
                'daemon_heartbeat_delta': 2,
                'current_fqdn': fqdn,
                'hosts': [_host(name=fqdn, id=0x7F, dc='i')],
            },
        ):
            with settings_context(
                CURRENT_FQDN=fqdn,
                HOSTS=[_host(name=fqdn, id=0x7F, dc='i')],
            ):
                with mock.patch.object(get_db_connection().get_engine(DB_VALIDATOR), 'connect', connect_mock):
                    resp = self.make_request(query={'check': 'db, daemon'})
                    errors = [
                        'Daemon is dead for %s' % fqdn,
                        'Database is unavailable: "%s" (%s)'
                        % (
                            DB_VALIDATOR,
                            DEFAULT_CONFIGS[DB_VALIDATOR]['host'],
                        ),
                        'Daemon is unavailable',
                    ]
                    self.assert_error_response(resp, '\n'.join(errors))

    def test_one_db_failed(self):
        side_effects = [
            sqlalchemy.exc.DatabaseError('', '', ''),
            sqlalchemy.exc.InterfaceError('', '', ''),
            MySQLdb.DatabaseError('', '', ''),
            MySQLdb.InterfaceError('', '', ''),
        ]
        connect_mock_not_ok = mock.Mock()
        not_available_db = DB_VALIDATOR
        db_host = DEFAULT_CONFIGS[not_available_db]['host']
        for side_effect in side_effects:
            with mock.patch.object(get_db_connection().get_engine(not_available_db), 'connect', connect_mock_not_ok):
                connect_mock_not_ok.side_effect = side_effect
                resp = self.make_request(query={'check': 'db'})
                errors = [
                    'Database is unavailable: "%s" (%s)'
                    % (
                        not_available_db,
                        db_host,
                    ),
                ]
                self.assert_error_response(resp, '\n'.join(errors))

    def test_both_db_failed(self):
        side_effects = [
            sqlalchemy.exc.DatabaseError('', '', ''),
            sqlalchemy.exc.InterfaceError('', '', ''),
            MySQLdb.DatabaseError('', '', ''),
            MySQLdb.InterfaceError('', '', ''),
        ]
        connect_mock_not_ok = mock.Mock()
        for side_effect in side_effects:
            with mock.patch.object(get_db_connection().get_engine(DB_VALIDATOR), 'connect', connect_mock_not_ok):
                connect_mock_not_ok.side_effect = side_effect
                self.db.set_side_effect(side_effect)
                resp = self.make_request(query={'check': 'db'})
                errors = [
                    'Database is unavailable: "%s" (%s)'
                    % (
                        DB_QUEUE,
                        DEFAULT_CONFIGS[DB_QUEUE]['host'],
                    ),
                    'Database is unavailable: "%s" (%s)'
                    % (
                        DB_VALIDATOR,
                        DEFAULT_CONFIGS[DB_VALIDATOR]['host'],
                    ),
                ]
                self.assert_error_response(resp, '\n'.join(errors))
