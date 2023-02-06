# pylint: disable=redefined-outer-name
import asyncio
import collections
import logging
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

import asyncpg
import pytest

from taxi.billing.pgstorage.postgres import connection as pg_connection
from taxi.billing.pgstorage.postgres import shard_info
from taxi.logs import auto_log_extra

ExpectedError = asyncpg.exceptions.PostgresConnectionError


def check_error_logs(actual_logs, expected_error_logs):
    actual_error_logs = [
        log for log in actual_logs if log['level'] == 'WARNING'
    ]
    assert actual_error_logs == expected_error_logs, actual_error_logs


class FakeAsyncpgConnection:
    def __init__(self, errors: Optional[Dict[str, List[Any]]] = None):
        self.errors = errors or {}
        self.calls: Dict[str, int] = collections.defaultdict(int)

    def _maybe_raise(self, error_name):
        if error_name in self.errors and self.calls[error_name] <= len(
                self.errors[error_name],
        ):
            raise self.errors[error_name][self.calls[error_name] - 1]

    async def fetch(self, query, *args, **kwargs) -> list:
        self.calls['fetch'] += 1
        self._maybe_raise('fetch')
        return []

    async def execute(self, query, *args, **kwargs) -> str:
        self.calls['execute'] += 1
        self._maybe_raise('execute')
        return ''

    async def close(self, **kwargs):
        self.calls['close'] += 1
        self._maybe_raise('close')

    def transaction(self, isolation=None, readonly=None, deferrable=None):
        self.calls['transaction'] += 1
        self._maybe_raise('transaction')

    def __await__(self):
        self.calls['await'] += 1
        self._maybe_raise('await')
        return self


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


async def test_fetch_error(log_test):
    pg_conn = FakeAsyncpgConnection({'fetch': [ExpectedError('fetch')]})
    log_extra = auto_log_extra.get_log_extra()
    connection = pg_connection.Connection(
        pg_conn, shard_info.ShardInfo(pg_shard_id=0, cluster_id='1234'),
    )
    with pytest.raises(ExpectedError):
        await connection.fetch('SELECT 1', log_extra=log_extra)
    expected_logs = [
        {
            'level': 'WARNING',
            '_link': log_extra['_link'],
            'extdict': {'pg_shard_id': 0, 'pg_cluster_id': '1234'},
            'msg': 'PostgresError occurred: fetch',
            'exc_info': True,
        },
    ]
    check_error_logs(log_test, expected_logs)


async def test_execute_error(log_test):
    pg_conn = FakeAsyncpgConnection({'execute': [ExpectedError('execute')]})
    log_extra = auto_log_extra.get_log_extra()
    connection = pg_connection.Connection(
        pg_conn, shard_info.ShardInfo(pg_shard_id=0, cluster_id='1234'),
    )
    with pytest.raises(ExpectedError):
        await connection.execute('SELECT 1', log_extra=log_extra)
    expected_logs = [
        {
            'level': 'WARNING',
            '_link': log_extra['_link'],
            'extdict': {'pg_shard_id': 0, 'pg_cluster_id': '1234'},
            'msg': 'PostgresError occurred: execute',
            'exc_info': True,
        },
    ]
    check_error_logs(log_test, expected_logs)


async def test_close_error(log_test):
    pg_conn = FakeAsyncpgConnection({'close': [ExpectedError('close')]})
    log_extra = auto_log_extra.get_log_extra()
    connection = pg_connection.Connection(
        pg_conn, shard_info.ShardInfo(pg_shard_id=0, cluster_id='1234'),
    )
    with pytest.raises(ExpectedError):
        await connection.close(log_extra=log_extra)
    expected_logs = [
        {
            'level': 'WARNING',
            '_link': log_extra['_link'],
            'extdict': {'pg_shard_id': 0, 'pg_cluster_id': '1234'},
            'msg': 'PostgresError occurred: close',
            'exc_info': True,
        },
    ]
    check_error_logs(log_test, expected_logs)


async def test_transaction_error(log_test):
    pg_conn = FakeAsyncpgConnection(
        {'transaction': [ExpectedError('transaction')]},
    )
    log_extra = auto_log_extra.get_log_extra()
    connection = pg_connection.Connection(
        pg_conn, shard_info.ShardInfo(pg_shard_id=0, cluster_id='1234'),
    )
    with pytest.raises(ExpectedError):
        connection.transaction(log_extra=log_extra)
    expected_logs = [
        {
            'level': 'WARNING',
            '_link': log_extra['_link'],
            'extdict': {'pg_shard_id': 0, 'pg_cluster_id': '1234'},
            'msg': 'PostgresError occurred: transaction',
            'exc_info': True,
        },
    ]
    check_error_logs(log_test, expected_logs)


async def test_fetch_success_on_retry(log_test):
    pg_conn = FakeAsyncpgConnection({'fetch': [asyncio.TimeoutError('fetch')]})
    log_extra = auto_log_extra.get_log_extra()
    connection = pg_connection.Connection(
        pg_conn, shard_info.ShardInfo(pg_shard_id=0, cluster_id='1234'),
    )
    # with pytest.raises(asyncio.TimeoutError):
    await connection.fetch('SELECT 1', attempts=2, log_extra=log_extra)
    assert pg_conn.calls['fetch'] == 2
    expected_logs = [
        {
            '_link': log_extra['_link'],
            'exc_info': True,
            'extdict': {'pg_cluster_id': '1234', 'pg_shard_id': 0},
            'level': 'WARNING',
            'msg': 'The operation has exceeded the given deadline: fetch',
        },
    ]
    check_error_logs(log_test, expected_logs)


async def test_fetch_fail_on_timeout(log_test):
    pg_conn = FakeAsyncpgConnection(
        {
            'fetch': [
                asyncio.TimeoutError('fetch'),
                asyncio.TimeoutError('fetch'),
            ],
        },
    )
    log_extra = auto_log_extra.get_log_extra()
    connection = pg_connection.Connection(
        pg_conn, shard_info.ShardInfo(pg_shard_id=0, cluster_id='1234'),
    )
    with pytest.raises(asyncio.TimeoutError):
        await connection.fetch('SELECT 1', attempts=2, log_extra=log_extra)
    assert pg_conn.calls['fetch'] == 2
    expected_logs = [
        {
            '_link': log_extra['_link'],
            'exc_info': True,
            'extdict': {'pg_cluster_id': '1234', 'pg_shard_id': 0},
            'level': 'WARNING',
            'msg': 'The operation has exceeded the given deadline: fetch',
        },
        {
            '_link': log_extra['_link'],
            'exc_info': True,
            'extdict': {'pg_cluster_id': '1234', 'pg_shard_id': 0},
            'level': 'WARNING',
            'msg': 'The operation has exceeded the given deadline: fetch',
        },
        {
            '_link': log_extra['_link'],
            'exc_info': False,
            'extdict': {'pg_cluster_id': '1234', 'pg_shard_id': 0},
            'level': 'WARNING',
            'msg': 'PG retries limit exceeded',
        },
    ]
    check_error_logs(log_test, expected_logs)


async def test_execute_success_on_retry(log_test):
    pg_conn = FakeAsyncpgConnection(
        {'execute': [asyncio.TimeoutError('execute')]},
    )
    log_extra = auto_log_extra.get_log_extra()
    connection = pg_connection.Connection(
        pg_conn, shard_info.ShardInfo(pg_shard_id=0, cluster_id='1234'),
    )
    # with pytest.raises(asyncio.TimeoutError):
    await connection.execute('SELECT 1', attempts=2, log_extra=log_extra)
    assert pg_conn.calls['execute'] == 2
    expected_logs = [
        {
            '_link': log_extra['_link'],
            'exc_info': True,
            'extdict': {'pg_cluster_id': '1234', 'pg_shard_id': 0},
            'level': 'WARNING',
            'msg': 'The operation has exceeded the given deadline: execute',
        },
    ]
    check_error_logs(log_test, expected_logs)


async def test_execute_fail_on_timeout(log_test):
    pg_conn = FakeAsyncpgConnection(
        {
            'execute': [
                asyncio.TimeoutError('execute'),
                asyncio.TimeoutError('execute'),
            ],
        },
    )
    log_extra = auto_log_extra.get_log_extra()
    connection = pg_connection.Connection(
        pg_conn, shard_info.ShardInfo(pg_shard_id=0, cluster_id='1234'),
    )
    with pytest.raises(asyncio.TimeoutError):
        await connection.execute('SELECT 1', attempts=2, log_extra=log_extra)
    assert pg_conn.calls['execute'] == 2
    expected_logs = [
        {
            '_link': log_extra['_link'],
            'exc_info': True,
            'extdict': {'pg_cluster_id': '1234', 'pg_shard_id': 0},
            'level': 'WARNING',
            'msg': 'The operation has exceeded the given deadline: execute',
        },
        {
            '_link': log_extra['_link'],
            'exc_info': True,
            'extdict': {'pg_cluster_id': '1234', 'pg_shard_id': 0},
            'level': 'WARNING',
            'msg': 'The operation has exceeded the given deadline: execute',
        },
        {
            '_link': log_extra['_link'],
            'exc_info': False,
            'extdict': {'pg_cluster_id': '1234', 'pg_shard_id': 0},
            'level': 'WARNING',
            'msg': 'PG retries limit exceeded',
        },
    ]
    check_error_logs(log_test, expected_logs)
