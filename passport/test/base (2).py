# -*- coding: utf-8 -*-
from passport.backend.core.test.test_utils import PassportTestCase
from passport.backend.perimeter.auth_api.db.connection import (
    FETCH_NONE,
    get_db_connection,
)
from passport.backend.perimeter.auth_api.db.schemas import metadata
from passport.backend.utils.warnings import enable_strict_bytes_mode


TEST_SETTINGS = {
    'DB_HOST': None,
    'DB_PORT': None,
    'DB_USER': None,
    'DB_PASSWORD': None,
    'DB_DRIVER': 'sqlite',
    'DB_DATABASE': ':memory:',
    'DB_RETRIES': 1,
    'DB_CONNECT_ARGS': {},
}


class BaseTestCase(PassportTestCase):
    MOCKED_SETTINGS = TEST_SETTINGS

    @staticmethod
    def try_get_real_settings():
        try:
            from passport.backend.perimeter import settings as perimeter_settings
        except ImportError:
            perimeter_settings = None
        return perimeter_settings

    @classmethod
    def setUpClass(cls):
        super(BaseTestCase, cls).setUpClass()
        enable_strict_bytes_mode()


class BaseDbTestCase(BaseTestCase):
    def setUp(self):
        self.db_connection = get_db_connection()
        self.db_connection.connect()
        self.db_connection.initialize_schema(metadata)

    def tearDown(self):
        metadata.drop_all(self.db_connection._engine)

    def insert_data(self, table, **kwargs):
        self.db_connection._execute(
            query=table.insert().values(**kwargs),
            fetch=FETCH_NONE,
        )
