# -*- coding: utf-8 -*-
from unittest import TestCase

import mock
from nose.tools import (
    assert_raises,
    eq_,
)
from passport.infra.daemons.yasmsapi.db.connection import (
    DB_EXCEPTIONS,
    DBConnection,
    DBError,
)


class DbConnectionTestCase(TestCase):
    @property
    def configs(self):
        return {
            'test_sms': {
                'sock': 'mysql.sock',
                'database': 'test_db',
                'user': 'test_user',
                'password': 'pwd',
                'driver': 'mysql',
            },
            'test_smsqueue': {
                'host': 'localhost',
                'port': 3306,
                'database': 'test_q_db',
                'user': 'test_user2',
                'password': 'pwd2',
                'driver': 'mysql',
            },
        }

    def test_configure(self):
        conn = DBConnection(configs=self.configs)
        conn.configure()
        eq_(str(conn._engines['test_sms'].url), 'mysql://test_user:pwd@/test_db?unix_socket=mysql.sock')
        eq_(str(conn._engines['test_smsqueue'].url), 'mysql://test_user2:pwd2@localhost:3306/test_q_db')

    def test_get_engine(self):
        conn = DBConnection(configs=self.configs)
        engine = conn.get_engine('test_sms')
        eq_(str(engine.url), 'mysql://test_user:pwd@/test_db?unix_socket=mysql.sock')

    def test_no_engine_error(self):
        db_conn = DBConnection(configs=self.configs)
        with assert_raises(RuntimeError):
            db_conn.get_engine('unknown')

    @mock.patch('sqlalchemy.engine.Engine.execute')
    def test_execute_error(self, execute_mock):
        db_conn = DBConnection(configs=self.configs)
        for exc in DB_EXCEPTIONS:
            execute_mock.side_effect = exc('', '', '')
            with assert_raises(DBError):
                db_conn.execute('test_sms', '')
