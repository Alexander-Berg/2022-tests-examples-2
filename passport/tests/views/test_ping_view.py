# -*- coding: utf-8 -*-

from sqlite3 import DatabaseError as SqliteDatabaseError

import mock
from passport.backend.vault.api.errors import (
    PingDatabaseError,
    PingfileError,
)
from passport.backend.vault.api.test.base_test_class import BaseTestClass
from passport.backend.vault.api.test.logging_mock import LoggingMock
from sqlalchemy.exc import DatabaseError as SADatabaseError


class _DBMock(object):
    def __init__(self):
        self.engine = self

    def connect(self):
        return self

    def execute(self, *args, **kwargs):
        raise SADatabaseError('Database disconnected', dict(), SqliteDatabaseError())


class TestPingView(BaseTestClass):
    def test_ok(self):
        with mock.patch('os.access', return_value=True):
            r = self.client.ping()
            self.assertResponseOk(r)
            self.assertEqual(r.text, 'Pong\n')

    def test_pingfile_error(self):
        with mock.patch('os.access', return_value=False):
            with LoggingMock() as logging_mock:
                r = self.client.ping()
                self.assertResponseError(r, PingfileError)

        errors_log = logging_mock.getLogger('exception_logger').entries
        self.assertEqual(len(errors_log), 1)
        self.assertEqual(errors_log[0][1], 'WARNING')
        self.assertIn(
            'message=Pingfile is not readable',
            errors_log[0][0],
        )

        self.assertListEqual(
            logging_mock.getLogger('statbox').entries,
            [({'action': 'enter', 'mode': 'ping'}, 'INFO', None, None),
             ({'action': 'error',
               'code': 'out_of_service',
               'message': 'Pingfile is not readable',
               'mode': 'ping',
               'pingfile': '/usr/lib/yandex/passport-vault/ping.html',
               'status': 'error'},
               'INFO',
               None,
               None)],
        )

    def test_database_error(self):
        with mock.patch('os.access', return_value=True):
            with mock.patch('passport.backend.vault.api.views.ping_view.get_db', return_value=_DBMock()):
                with LoggingMock() as logging_mock:
                    r = self.client.ping()
                    self.assertResponseError(r, PingDatabaseError)

        errors_log = logging_mock.getLogger('exception_logger').entries
        self.assertEqual(len(errors_log), 1)
        self.assertEqual(errors_log[0][1], 'ERROR')
        self.assertIn(
            'message=Database failed',
            errors_log[0][0],
        )

        self.assertListEqual(
            logging_mock.getLogger('statbox').entries,
            [({'action': 'enter', 'mode': 'ping'}, 'INFO', None, None),
             ({'action': 'error',
               'code': 'ping_failed',
               'database_error': "(_sqlite3.DatabaseError)  [SQL: 'Database disconnected'] "
                                 "(Background on this error at: http://sqlalche.me/e/4xp6)",
               'message': 'Database failed',
               'mode': 'ping',
               'status': 'error'},
              'INFO',
              None,
              None)]
        )
