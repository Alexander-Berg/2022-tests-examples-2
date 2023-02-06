# pylint: disable=redefined-outer-name,unused-variable,raising-bad-type
import logging

import asyncpg
import pytest

from taxi.billing.pgstorage.postgres import pool as pg_pool
from taxi.billing.pgstorage.postgres import shard_info
from taxi.logs import auto_log_extra

ExpectedError = asyncpg.exceptions.PostgresConnectionError


def check_error_logs(actual_logs, expected_error_logs):
    actual_error_logs = [
        log for log in actual_logs if log['level'] == 'WARNING'
    ]
    assert actual_error_logs == expected_error_logs, actual_error_logs


class FakeAsyncpgPool:
    def __init__(self, errors):
        self.errors = errors

    def maybe_raise(self, error_name):
        if error_name in self.errors:
            raise self.errors[error_name]

    async def fetch(self, *args, **kwargs):
        self.maybe_raise('fetch')
        return []

    async def execute(self, *args, **kwargs):
        self.maybe_raise('execute')
        return ''

    async def close(self, **kwargs):
        self.maybe_raise('close')

    def acquire(self, **kwargs):
        self.maybe_raise('acquire')
        return FakeAcquireContext(self.errors)

    async def release(self, **kwargs):
        self.maybe_raise('release')
        return None  # fake connection


class FakeAcquireContext:
    def __init__(self, errors):
        self.errors = errors

    async def __aenter__(self):
        if 'enter' in self.errors:
            raise self.errors['enter']

    async def __aexit__(self, *exc):
        if 'exit' in self.errors:
            raise self.errors['exit']

    def __await__(self):
        yield


class FakeConnection:
    raw_connection = None

    def __init__(self, errors):
        self.errors = errors

    async def release(self, **kwargs):
        if 'release' in self.errors:
            raise self.errors['release']


@pytest.fixture
async def log_test(loop, collected_logs_with_link):
    log_settings = {
        'logger_names': ['taxi'],
        'ident': 'log_extra',
        'log_level': logging.INFO,
        'log_format': '',
    }
    from taxi.logs import log
    log.init_logger(**log_settings)
    yield collected_logs_with_link
    log.cleanup_logger(log_settings['logger_names'])


@pytest.fixture
def patch_create_pool(patch):
    def _patch(error=None, pool_errors=None):
        @patch('taxi.pg.create_pool')
        async def create_pool(*args, **kwargs):
            if error is not None:
                raise error
            return FakeAsyncpgPool(pool_errors or {})

    return _patch


async def test_create_pool_error(patch_create_pool, log_test):
    patch_create_pool(error=ExpectedError('create'))
    with pytest.raises(ExpectedError):
        await pg_pool.create_pool(
            shard_info=shard_info.ShardInfo(0, '1234'),
            dsn='dsn',
            log_extra=auto_log_extra.get_log_extra(),
        )
    expected_logs = [
        {
            'level': 'WARNING',
            '_link': auto_log_extra.get_log_extra()['_link'],
            'extdict': {'pg_shard_id': 0, 'pg_cluster_id': '1234'},
            'msg': 'PostgresError occurred: create',
            'exc_info': True,
        },
    ]
    check_error_logs(log_test, expected_logs)


async def test_close_error(patch_create_pool, log_test):
    patch_create_pool(pool_errors={'close': ExpectedError('close')})
    connection_pool = await pg_pool.create_pool(
        shard_info=shard_info.ShardInfo(0, '1234'), dsn='dsn', log_extra=None,
    )
    with pytest.raises(ExpectedError):
        await connection_pool.close(log_extra=auto_log_extra.get_log_extra())
    expected_logs = [
        {
            'level': 'WARNING',
            '_link': auto_log_extra.get_log_extra()['_link'],
            'extdict': {'pg_shard_id': 0, 'pg_cluster_id': '1234'},
            'msg': 'PostgresError occurred: close',
            'exc_info': True,
        },
    ]
    check_error_logs(log_test, expected_logs)


async def test_acquire_error(patch_create_pool, log_test):
    patch_create_pool(pool_errors={'acquire': ExpectedError('acquire')})
    connection_pool = await pg_pool.create_pool(
        shard_info=shard_info.ShardInfo(0, '1234'), dsn='dsn', log_extra=None,
    )
    with pytest.raises(ExpectedError):
        await connection_pool.acquire(log_extra=auto_log_extra.get_log_extra())
    expected_logs = [
        {
            'level': 'WARNING',
            '_link': auto_log_extra.get_log_extra()['_link'],
            'extdict': {'pg_shard_id': 0, 'pg_cluster_id': '1234'},
            'msg': 'PostgresError occurred: acquire',
            'exc_info': True,
        },
    ]
    check_error_logs(log_test, expected_logs)


async def test_release_error(patch_create_pool, log_test):
    patch_create_pool(pool_errors={})
    connection_pool = await pg_pool.create_pool(
        shard_info=shard_info.ShardInfo(0, '1234'), dsn='dsn', log_extra=None,
    )
    with pytest.raises(ExpectedError):
        await connection_pool.release(
            FakeConnection(errors={'release': ExpectedError('release')}),
            log_extra=auto_log_extra.get_log_extra(),
        )
    expected_logs = [
        {
            'level': 'WARNING',
            '_link': auto_log_extra.get_log_extra()['_link'],
            'extdict': {'pg_shard_id': 0, 'pg_cluster_id': '1234'},
            'msg': 'PostgresError occurred: release',
            'exc_info': True,
        },
    ]
    check_error_logs(log_test, expected_logs)


async def test_enter_error_in_with(patch_create_pool, log_test):
    patch_create_pool(pool_errors={'enter': ExpectedError('enter')})
    connection_pool = await pg_pool.create_pool(
        shard_info=shard_info.ShardInfo(0, '1234'), dsn='dsn', log_extra=None,
    )
    with pytest.raises(ExpectedError):
        async with connection_pool.acquire(
                log_extra=auto_log_extra.get_log_extra(),
        ):
            pass
    expected_logs = [
        {
            'level': 'WARNING',
            '_link': auto_log_extra.get_log_extra()['_link'],
            'extdict': {'pg_shard_id': 0, 'pg_cluster_id': '1234'},
            'msg': 'PostgresError occurred: enter',
            'exc_info': True,
        },
    ]
    check_error_logs(log_test, expected_logs)


async def test_exit_error_in_with(patch_create_pool, log_test):
    patch_create_pool(pool_errors={'exit': ExpectedError('exit')})
    connection_pool = await pg_pool.create_pool(
        shard_info=shard_info.ShardInfo(0, '1234'), dsn='dsn', log_extra=None,
    )
    with pytest.raises(ExpectedError):
        async with connection_pool.acquire(
                log_extra=auto_log_extra.get_log_extra(),
        ):
            pass
    expected_logs = [
        {
            'level': 'WARNING',
            '_link': auto_log_extra.get_log_extra()['_link'],
            'extdict': {'pg_shard_id': 0, 'pg_cluster_id': '1234'},
            'msg': 'PostgresError occurred: exit',
            'exc_info': True,
        },
    ]
    check_error_logs(log_test, expected_logs)
