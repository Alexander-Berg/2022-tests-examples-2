# -*- coding: utf-8 -*-
from unittest import TestCase

import mock
from passport.backend.api.app import (
    configure_db_connection,
    prepare_ydb_connection,
)
from passport.backend.api.configs import config
from passport.backend.core.dbmanager import manager
from passport.backend.core.lazy_loader import LazyLoader
from passport.backend.core.test.test_utils.utils import (
    settings_context,
    with_settings,
)
from sqlalchemy.exc import ResourceClosedError


def test_config_is_not_empty():
    assert config
    assert config.get_config_by_basename('base.yaml') is not None
    assert 'application' in config
    assert 'gunicorn' in config


TEST_CONFIG = {
    'master': {
        'database': ':memory:',
        'connect_timeout': 0.1,
        'read_timeout': 1,
        'write_timeout': 8,
        'retries': 1,
        'type': 'master',
        'driver': 'sqlite',
    },
    'slave': {
        'driver': 'sqlite',
        'database': ':memory:',
        'type': 'slave',
    },
}


@with_settings(
    PREPARE_CONNECTION_ATTEMPTS=10,
)
class ConfigureDbConnectionTestCase(TestCase):
    def setUp(self):
        self.logger = mock.Mock()
        self.create_engine_mock = mock.Mock()
        self.create_engine_patch = mock.patch.object(manager, 'create_engine', self.create_engine_mock)
        self.create_engine_patch.start()

    def tearDown(self):
        self.create_engine_patch.stop()
        del self.create_engine_patch
        del self.create_engine_mock
        del self.logger

    def test_ok(self):
        configure_db_connection(
            logger=self.logger,
            db_name='test',
            config=TEST_CONFIG,
        )
        dbm = manager.get_dbm('test')
        assert self.create_engine_mock().connect().execute.call_count == 1
        assert self.logger.warning.call_count == 0  # не было ошибок, нечего логировать

    def test_errors(self):
        self.create_engine_mock().connect().execute.side_effect = ResourceClosedError
        configure_db_connection(
            self.logger,
            db_name='test',
            config=TEST_CONFIG,
        )
        dbm = manager.get_dbm('test')
        # два запроса были сделаны PREPARE_CONNECTION_ATTEMPTS раз
        assert self.create_engine_mock().connect().execute.call_count == 10
        assert self.logger.warning.call_count == 10  # все попытки окончились ошибкой


class PrepareYdbConnectionTestCase(TestCase):
    _basic_settings = dict(
        YDB_RETRIES=0,
        YDB_CONNECTION_TIMEOUT=1.0,
        YDB_GET_SESSION_TIMEOUT=0.1,
        YDB_DEADLINE=0.75,
        YDB_TIMEOUT=0.45,
        YDB_TOKEN='token',
        YDB_ENDPOINT='endpoint',
    )

    def setUp(self):
        self._patches = []

        self._ydb_driver_faker = mock.Mock()
        self._patches.append(
            mock.patch(
                'passport.backend.core.ydb.ydb.ydb',
                mock.Mock(
                    DriverConfig=self._ydb_driver_faker,
                ),
            ),
        )
        for patch in self._patches:
            patch.start()

        for instance in LazyLoader._instances.values():
            instance._instance = None

    def tearDown(self):
        for patch in reversed(self._patches):
            patch.stop()

    def updated_settings(self, **kwargs):
        settings = dict(self._basic_settings)
        settings.update(kwargs)
        return settings

    def setup_exception(self, function, exception):
        patch = mock.patch(
            'passport.backend.api.app.{}'.format(function),
            mock.Mock(side_effect=exception),
        )
        self._patches.append(patch)
        patch.start()

    def assert_called(self, database_args):
        self.assertEqual(
            len(self._ydb_driver_faker.mock_calls),
            len(database_args),
            'Calls {} len differs from len of expected database args {}'.format(
                self._ydb_driver_faker.mock_calls,
                database_args
            ),
        )
        real_database_args = [call.kwargs['database'] for call in self._ydb_driver_faker.mock_calls]
        self.assertEqual(real_database_args, database_args)

    def call(self):
        prepare_ydb_connection()

    def test_ok(self):
        with settings_context(
            **self.updated_settings(
                YDB_DATABASE='profile_database',
                YDB_PROFILE_ENABLED=True,
                YDB_DRIVE_DATABASE='drive_database',
                YDB_DRIVE_ENABLED=True,
                YDB_SUPPORT_CODE_DATABASE='support_code_database',
                YDB_SUPPORT_CODE_ENABLED=True,
                YDB_FAMILY_INVITE_DATABASE='family_invite_database',
                YDB_FAMILY_INVITE_ENABLED=True,
                YDB_TURBOAPP_PARTNERS_DATABASE='turboapp_partners',
                YDB_TURBOAPP_PARTNERS_ENABLED=True,
            )
        ):
            self.call()
        self.assert_called(
            database_args=[
                'profile_database',
                'drive_database',
                'support_code_database',
                'family_invite_database',
                'turboapp_partners',
            ],
        )

    def test_generic_exception(self):
        self.setup_exception(function='get_ydb_drive_session', exception=ValueError())
        with self.assertRaises(ValueError):
            with settings_context(
                **self.updated_settings(
                    YDB_DATABASE='profile_database',
                    YDB_PROFILE_ENABLED=True,
                )
            ):
                self.call()
        self.assert_called(
            database_args=[
                'profile_database',
            ],
        )

    def test_disabled_databases(self):
        with settings_context(
            **self.updated_settings(
                YDB_DATABASE='profile_database',
                YDB_PROFILE_ENABLED=False,
                YDB_DRIVE_DATABASE='drive_database',
                YDB_DRIVE_ENABLED=False,
                YDB_SUPPORT_CODE_DATABASE='support_code_database',
                YDB_SUPPORT_CODE_ENABLED=True,
                YDB_FAMILY_INVITE_DATABASE='family_invite_database',
                YDB_FAMILY_INVITE_ENABLED=False,
                YDB_TURBOAPP_PARTNERS_DATABASE='turboapp_partners',
                YDB_TURBOAPP_PARTNERS_ENABLED=False,
            )
        ):
            self.call()
        self.assert_called(
            database_args=[
                'support_code_database',
            ],
        )
