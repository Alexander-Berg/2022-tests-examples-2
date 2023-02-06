# -*- coding: utf-8 -*-
from passport.backend.perimeter.auth_api.db import (
    DBConnection,
    get_db_connection,
)
from passport.backend.perimeter.auth_api.test import BaseTestCase


class TestConnection(BaseTestCase):
    def test_dsn_parameters(self):
        """
        Проверяем правильность автоматического конструирования DSN.
        """

        def comparator(params, dsn):
            assert str(DBConnection(**params).dsn) == dsn

        test_data = [
            (
                {},
                'sqlite:///:memory:',
            ),
            (
                dict(driver='mysql+mysqlconnector', database='testdb'),
                'mysql+mysqlconnector:///testdb',
            ),
            (
                {
                    'username': 'test_user',
                    'password': 'test_pass',
                    'host': 'test_host',
                    'port': 12345,
                    'database': 'testdb',
                    'driver': 'mysql',
                },
                'mysql://test_user:test_pass@test_host:12345/testdb',
            ),
        ]
        for init_params, result_dsn in test_data:
            comparator(init_params, result_dsn)

    def test_connection_repr(self):
        """
        Проверяем, что восстановленный из repr объект равняется исходному.
        """
        conn = DBConnection(
            username='test_user',
            password='test_pass',
            host='test_host',
            port=12345,
            database='testdb',
            driver='mysql',
        )
        assert eval(repr(conn))

    def test_get_connection(self):
        """
        Проверяем, что get_db_connection возвращает один и тот же объект.
        """
        assert get_db_connection() is get_db_connection()
