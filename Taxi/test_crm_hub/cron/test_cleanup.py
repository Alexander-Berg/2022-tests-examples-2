import asyncio
import datetime
from unittest import mock
import uuid

import pytest

from taxi.stq import async_worker_ng

from crm_hub.generated.cron import run_cron
from crm_hub.logic import cleanup
from crm_hub.repositories import batch_sending
from crm_hub.stq import start_history_cleaner


def _wrap_async_result(result):
    future = asyncio.Future()
    future.set_result(result)
    return future


@pytest.mark.pgsql('crm_hub', files=['init_sendings.sql'])
@pytest.mark.config(
    CRM_HUB_CLEANUP_RULES={
        'copy_chunk': 1000,
        'cleanup_enabled': True,
        'rules': [
            {
                'sending_statuses': ['FINISHED'],
                'ttl_days': 1,
                'clean_chunk': 10,
                'is_verify': True,
            },
            {
                'sending_statuses': ['FINISHED'],
                'ttl_days': 2,
                'clean_chunk': 10,
                'is_verify': False,
            },
            {
                'sending_statuses': ['CANCELED'],
                'ttl_days': 1,
                'clean_chunk': 10,
                'is_verify': True,
            },
            {
                'sending_statuses': ['ERROR'],
                'ttl_days': 10,
                'clean_chunk': 10,
                'is_verify': False,
            },
            {
                'sending_statuses': ['NEW', 'PROCESSING'],
                'ttl_days': 30,
                'clean_chunk': 10,
                'is_verify': False,
            },
        ],
    },
)
async def test_cron_cleanup_selection(web_context, stq):
    with mock.patch(
            'datetime.datetime.utcnow',
            return_value=datetime.datetime(
                year=2021, day=11, month=1, hour=12,
            ),
    ):
        await run_cron.main(['crm_hub.crontasks.sending_cleanup', '-t', '0'])

    assert not stq.crm_hub_sendings_cleanup.has_calls

    with mock.patch(
            'datetime.datetime.utcnow',
            return_value=datetime.datetime(
                year=2021, day=12, month=1, hour=12,
            ),
    ):
        await run_cron.main(['crm_hub.crontasks.sending_cleanup', '-t', '0'])

    assert stq.crm_hub_sendings_cleanup.has_calls
    assert stq['crm_hub_sendings_cleanup'].times_called == 1
    call = stq['crm_hub_sendings_cleanup'].next_call()
    assert call['args'] == ['00000000-0000-0000-0000-000000000001']

    with mock.patch(
            'datetime.datetime.utcnow',
            return_value=datetime.datetime(
                year=2021, day=14, month=1, hour=12,
            ),
    ):
        await run_cron.main(['crm_hub.crontasks.sending_cleanup', '-t', '0'])

    assert stq.crm_hub_sendings_cleanup.has_calls
    assert stq['crm_hub_sendings_cleanup'].times_called == 1
    call = stq['crm_hub_sendings_cleanup'].next_call()
    assert call['args'] == ['00000000-0000-0000-0000-000000000002']

    with mock.patch(
            'datetime.datetime.utcnow',
            return_value=datetime.datetime(
                year=2021, day=15, month=1, hour=12,
            ),
    ):
        await run_cron.main(['crm_hub.crontasks.sending_cleanup', '-t', '0'])

    assert stq.crm_hub_sendings_cleanup.has_calls
    assert stq['crm_hub_sendings_cleanup'].times_called == 1
    call = stq['crm_hub_sendings_cleanup'].next_call()
    assert call['args'] == ['00000000-0000-0000-0000-000000000003']

    with mock.patch(
            'datetime.datetime.utcnow',
            return_value=datetime.datetime(
                year=2021, day=20, month=1, hour=12,
            ),
    ):
        await run_cron.main(['crm_hub.crontasks.sending_cleanup', '-t', '0'])

    assert stq.crm_hub_sendings_cleanup.has_calls
    assert stq['crm_hub_sendings_cleanup'].times_called == 1
    call = stq['crm_hub_sendings_cleanup'].next_call()
    assert call['args'] == ['00000000-0000-0000-0000-000000000004']

    with mock.patch(
            'datetime.datetime.utcnow',
            return_value=datetime.datetime(year=2021, day=9, month=2, hour=12),
    ):
        await run_cron.main(['crm_hub.crontasks.sending_cleanup', '-t', '0'])

    assert stq.crm_hub_sendings_cleanup.has_calls
    assert stq['crm_hub_sendings_cleanup'].times_called == 2
    call = stq['crm_hub_sendings_cleanup'].next_call()
    assert call['args'] == ['00000000-0000-0000-0000-000000000005']
    call = stq['crm_hub_sendings_cleanup'].next_call()
    assert call['args'] == ['00000000-0000-0000-0000-000000000006']

    with mock.patch(
            'datetime.datetime.utcnow',
            return_value=datetime.datetime(year=2022, day=1, month=1, hour=12),
    ):
        await run_cron.main(['crm_hub.crontasks.sending_cleanup', '-t', '0'])

    assert not stq.crm_hub_sendings_cleanup.has_calls


@pytest.mark.pgsql('crm_hub', files=['init_sendings.sql'])
@pytest.mark.config(
    CRM_HUB_CLEANUP_RULES={
        'copy_chunk': 1000,
        'cleanup_enabled': False,
        'rules': [
            {
                'sending_statuses': ['FINISHED'],
                'ttl_days': 2,
                'clean_chunk': 10,
                'is_verify': False,
            },
            {
                'sending_statuses': ['CANCELED'],
                'ttl_days': 1,
                'clean_chunk': 10,
                'is_verify': False,
            },
            {
                'sending_statuses': ['ERROR'],
                'ttl_days': 10,
                'clean_chunk': 10,
                'is_verify': False,
            },
            {
                'sending_statuses': ['NEW', 'PROCESSING'],
                'ttl_days': 30,
                'clean_chunk': 10,
                'is_verify': False,
            },
        ],
    },
)
@pytest.mark.now('2022-01-01 12:00:00')
async def test_cron_cleanup_disabled(web_context, stq):
    await run_cron.main(['crm_hub.crontasks.sending_cleanup', '-t', '0'])
    assert not stq.crm_hub_sendings_cleanup.has_calls


@pytest.mark.config(
    CRM_HUB_CLEANUP_RULES={
        'cleanup_enabled': True,
        'copy_chunk': 10000,
        'paths': [
            {
                'entity_type': 'driver',
                'path': '//home',
                'name': 'driver_sending_history',
            },
            {
                'entity_type': 'user',
                'path': '//home/',
                'name': 'user_sending_history',
            },
        ],
    },
)
@pytest.mark.parametrize(
    'entity_type, pg_table, result, exc',
    [
        (
            'driver',
            'driver_table',
            '//home/driver/2021-01-25_driver_table',
            False,
        ),
        ('user', 'user_table', '//home/user/2021-01-25_user_table', False),
        ('unknown', 'unknown_table', None, True),
    ],
)
@pytest.mark.now('2021-01-25 01:00:00')
async def test_history_path(web_context, entity_type, pg_table, result, exc):
    cleanup_settings = cleanup.CleanupSettings.from_settings(
        web_context.config.CRM_HUB_CLEANUP_RULES,
    )

    def check_yt_path():
        return cleanup_settings.get_yt_replica_table_path(
            entity_type=entity_type, table_postfix=pg_table,
        )

    if exc:
        with pytest.raises(KeyError):
            check_yt_path()
    else:
        assert check_yt_path() == result


@pytest.mark.pgsql('crm_hub', files=['init_sendings_for_stq.sql'])
@pytest.mark.config(
    CRM_HUB_CLEANUP_RULES={
        'copy_chunk': 1000,
        'cleanup_enabled': True,
        'paths': [
            {
                'entity_type': 'driver',
                'path': '//home',
                'name': 'driver_sending_history',
            },
        ],
    },
)
@pytest.mark.yt
@pytest.mark.now('2021-08-02 01:00:00')
@pytest.mark.parametrize(
    'sending_id,pg_table,replication_state,expected_cleanup_state,yt_table,'
    'pg_tables_exist_before,pg_tables_exist_after,yt_table_exists_after,'
    'is_v2_sending',
    [
        (
            '00000000000000000000000000000001',
            'batch_00_00',
            cleanup.ReplicationState.NEW.as_sql(),
            cleanup.CleanupState.DELETED.as_sql(),
            '//home/driver/2021-08-02_batch_00_00',
            False,
            False,
            False,
            False,
        ),  # no pg tables exist at all
        (
            '00000000000000000000000000000002',
            'batch_11_22',
            cleanup.ReplicationState.NEW.as_sql(),
            cleanup.CleanupState.DELETED.as_sql(),
            '//home/driver/2021-08-02_batch_11_22',
            True,
            False,
            True,
            False,
        ),  # normal case
        (
            '00000000000000000000000000000003',
            'batch_33_44',
            cleanup.ReplicationState.NEW.as_sql(),
            cleanup.CleanupState.ERROR.as_sql(),
            '//home/driver/2021-08-02_batch_33_44',
            True,
            True,
            False,
            False,
        ),  # cleanup state is error, no cleanup/replication should happen
        (
            '00000000000000000000000000000004',
            'batch_55_66',
            cleanup.ReplicationState.DONE.as_sql(),
            cleanup.CleanupState.DELETED.as_sql(),
            '//home/driver/2021-08-02_batch_55_66',
            True,
            False,
            False,
            False,
        ),  # normal case, but sending already replicated according to status
        (
            '00000000000000000000000000000007',
            'batch_22_77',
            cleanup.ReplicationState.NEW.as_sql(),
            cleanup.CleanupState.DELETED.as_sql(),
            '//home/driver/2021-08-02_batch_22_77',
            True,
            False,
            True,
            True,
        ),  # normal case, v2 sending logic
    ],
)
async def test_cleanup_stq(
        stq3_context,
        sending_id,
        pg_table,
        replication_state,
        expected_cleanup_state,
        yt_table,
        pg_tables_exist_before,
        pg_tables_exist_after,
        yt_table_exists_after,
        is_v2_sending,
):
    async with stq3_context.pg.master_pool.acquire() as conn:
        assert (
            await cleanup.CleanupHandler.table_exists(
                stq3_context, conn, pg_table,
            )
            == pg_tables_exist_before
        )
        assert (
            is_v2_sending
            or await cleanup.CleanupHandler.table_exists(
                stq3_context, conn, pg_table + '_results',
            )
            == pg_tables_exist_before
        )
    await start_history_cleaner.task(
        context=stq3_context,
        task_info=async_worker_ng.TaskInfo(
            id='123', exec_tries=1, reschedule_counter=1, queue='',
        ),
        sending_id=sending_id,
    )
    async with stq3_context.pg.master_pool.acquire() as conn:
        sending_storage = batch_sending.BatchSendingStorage(stq3_context, conn)
        sending = await sending_storage.fetch(uuid.UUID(sending_id))
        assert sending.cleanup_state == expected_cleanup_state
        assert sending.replication_state == replication_state

        assert (
            await cleanup.CleanupHandler.table_exists(
                stq3_context, conn, pg_table,
            )
            == pg_tables_exist_after
        )
        assert (
            await cleanup.CleanupHandler.table_exists(
                stq3_context, conn, pg_table + '_results',
            )
            == pg_tables_exist_after
        )
