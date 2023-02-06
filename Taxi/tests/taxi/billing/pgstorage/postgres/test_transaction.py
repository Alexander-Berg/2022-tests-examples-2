# pylint: disable=redefined-outer-name
import logging

import asyncpg
import pytest

from taxi.billing.pgstorage.postgres import shard_info
from taxi.billing.pgstorage.postgres import transaction as pg_trans
from taxi.logs import auto_log_extra

ExpectedError = asyncpg.exceptions.InvalidTransactionStateError


def check_error_logs(actual_logs, expected_error_logs):
    actual_error_logs = [
        log for log in actual_logs if log['level'] == 'WARNING'
    ]
    assert actual_error_logs == expected_error_logs, actual_error_logs


class FakeAsyncpgTransaction:
    def __init__(self, errors=None):
        self.errors = errors or {}

    async def __aenter__(self):
        if 'enter' in self.errors:
            raise self.errors['enter']
        return self

    async def __aexit__(self, *exc):
        if 'exit' in self.errors:
            raise self.errors['exit']


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


async def test_enter_error_in_with(log_test):
    pg_tran = FakeAsyncpgTransaction({'enter': ExpectedError('enter')})
    transaction = pg_trans.Transaction(
        pg_tran,
        shard_info=shard_info.ShardInfo(pg_shard_id=0, cluster_id='1234'),
    )
    with pytest.raises(ExpectedError):
        async with transaction:
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


async def test_exit_error_in_with(log_test):
    pg_tran = FakeAsyncpgTransaction({'exit': ExpectedError('exit')})
    transaction = pg_trans.Transaction(
        pg_tran,
        shard_info=shard_info.ShardInfo(pg_shard_id=0, cluster_id='1234'),
    )
    with pytest.raises(ExpectedError):
        async with transaction:
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
