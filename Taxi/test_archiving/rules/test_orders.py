# pylint: disable=protected-access
import datetime

import pytest

from archiving import core
from archiving import cron_run
from test_archiving import consts


@pytest.mark.parametrize(
    'rule_name,expected_procs,archived_procs',
    [
        (
            'order_proc_1_tail',
            {
                'recent',
                'not_finished',
                'need_sync',
                'stale',
                'not_tailed',
                'not_tailed_shard2',
                '0',
                '1',
                '2',
            },
            {'actual', 'stale', '0', '1', '2'},
        ),
        (
            'order_proc_1',
            {
                'actual',
                'recent',
                'not_finished',
                'need_sync',
                'stale',
                'not_tailed_shard2',
                '0',
                '1',
                '2',
            },
            {'not_tailed'},
        ),
        (
            'order_proc_2',
            {
                'actual',
                'recent',
                'not_finished',
                'need_sync',
                'stale',
                'not_tailed',
                '0',
                '1',
                '2',
            },
            {'not_tailed_shard2'},
        ),
    ],
)
@pytest.mark.now('2016-11-20T11:00:00.0')
async def test_archive_order_proc(
        cron_context,
        load_all_mongo_docs,
        replication_state_min_ts,
        replication_sync_api,
        fake_task_id,
        patch_current_date,
        requests_handlers,
        rule_name,
        expected_procs,
        archived_procs,
):
    replication_state_min_ts.apply(consts.ORDER_PROCS_MIN_TS_MOCK)
    replication_sync_api.set_default_status(
        replication_sync_api.STATUS_MISMATCH,
    )
    replication_sync_api.apply(
        {
            'order_proc': {
                'actual': replication_sync_api.STATUS_MATCH,
                'not_tailed': replication_sync_api.STATUS_MATCH,
                'not_tailed_shard2': replication_sync_api.STATUS_MATCH,
            },
        },
    )
    archivers = await cron_run.prepare_archivers(
        cron_context, rule_name, fake_task_id,
    )
    archiver = next(iter(archivers.values()))
    await core.remove_documents(archiver, cron_context.client_solomon)
    order_procs = await load_all_mongo_docs(rule_name)
    assert set(order_procs) == expected_procs

    matched_procs = {'actual', 'not_tailed', 'not_tailed_shard2'}
    for updated_id in archived_procs - matched_procs:
        assert order_procs[updated_id]['updated'] == datetime.datetime.utcnow()

    assert replication_sync_api.handler.times_called == 1
    sync_api_request = replication_sync_api.handler.next_call()['request']
    assert sync_api_request.path.endswith('/order_proc')
    request_items = {item['id'] for item in sync_api_request.json['items']}
    assert request_items == archived_procs


@pytest.mark.parametrize(
    'rule_name,savepoint,expected_ids',
    [
        (
            'order_proc_tail',
            datetime.datetime(2016, 5, 15),
            {'0', 'actual', 'stale'},
        ),
        ('order_proc_tail', datetime.datetime(2016, 5, 14), {'0', 'stale'}),
        ('order_proc_tail', datetime.datetime(2016, 5, 13), {'0'}),
        ('order_proc_tail', datetime.datetime(2016, 5, 12), set()),
        (
            'order_proc_1_tail',
            datetime.datetime(2016, 5, 15),
            {'0', 'actual', 'stale'},
        ),
        ('order_proc_1_tail', datetime.datetime(2016, 5, 14), {'0', 'stale'}),
        ('order_proc_1_tail', datetime.datetime(2016, 5, 13), {'0'}),
        ('order_proc_1_tail', datetime.datetime(2016, 5, 12), set()),
        ('order_proc_1', datetime.datetime(2016, 5, 15), {'actual'}),
        ('order_proc_1', datetime.datetime(2016, 5, 14), {'stale'}),
        ('order_proc_1', datetime.datetime(2016, 5, 13), {'0'}),
        ('order_proc_1', datetime.datetime(2016, 5, 12), set()),
        ('order_proc_2', datetime.datetime(2016, 5, 15), set()),
        ('order_proc_2', datetime.datetime(2016, 5, 14), set()),
        ('order_proc_2', datetime.datetime(2016, 5, 13), set()),
        ('order_proc_2', datetime.datetime(2016, 5, 12), set()),
    ],
)
@pytest.mark.now('2016-11-20T11:00:00.0')
async def test_order_proc_cleaner(
        cron_context,
        replication_state_min_ts,
        rule_name,
        savepoint,
        expected_ids,
        fake_task_id,
        monkeypatch,
        requests_handlers,
):
    replication_state_min_ts.apply(consts.ORDER_PROCS_MIN_TS_MOCK)
    archivers = await cron_run.prepare_archivers(
        cron_context, rule_name, fake_task_id,
    )
    archiver = next(iter(archivers.values()))
    monkeypatch.setattr(archiver._removal_metadata, 'iterate_from', savepoint)
    candidates = await archiver._get_all_candidates_cursor()
    ids = set()
    async for obj in candidates:
        ids.add(obj['_id'])
    assert ids == expected_ids


@pytest.mark.now('2016-11-20T11:00:00.0')
@pytest.mark.parametrize(
    'rule_name,expected_orders,expected_candidates',
    [
        (
            'orders_hourly',
            {
                'refund',
                'expired_with_preexpiration',
                'hold',
                'hold2',
                'need_tips',
                'not_expired',
                'hourly_recently_updated',
                'debt',
                'daily_recently_updated',
                '0',
                'unfinished_invoice_operations',
                'unfinished_invoice_cashback_operations',
                'unfinished_invoice_compensation_operations',
                '1',
                '2',
                'no_refund_no_hold',
                'dup',
                'dirty',
                'has_negative_feedback_for_daily',
                'has_status_pending',
                #  'has_negative_feedback_for_hourly' - use order.feedback data
            },
            {
                'hourly_recently_updated',
                'to_be_archived_hourly',
                'finished_invoice_operations',
                'finished_invoice_cashback_operations',
                'finished_invoice_compensation_operations',
                'expired_with_preexpiration',
                'has_negative_feedback_for_hourly',
                'unfinished_invoice_operations',
                'unfinished_invoice_cashback_operations',
                'unfinished_invoice_compensation_operations',
            },
        ),
        (
            'orders_daily',
            {
                'refund',
                'expired_with_preexpiration',
                'hold',
                'hold2',
                'need_tips',
                'to_be_archived_hourly',
                'finished_invoice_operations',
                'finished_invoice_cashback_operations',
                'finished_invoice_compensation_operations',
                'unfinished_invoice_operations',
                'unfinished_invoice_cashback_operations',
                'unfinished_invoice_compensation_operations',
                'not_expired',
                'hourly_recently_updated',
                'debt',
                'daily_recently_updated',
                'has_negative_feedback_for_hourly',
                'has_status_pending',
            },
            {
                'refund',
                'debt',
                'hold2',
                'need_tips',
                '1',
                '0',
                '2',
                'dirty',
                'dup',
                'hold',
                'daily_recently_updated',
                'no_refund_no_hold',
                'has_negative_feedback_for_daily',
                'has_status_pending',
            },
        ),
    ],
)
async def test_archive_orders(
        cron_context,
        monkeypatch,
        load_all_mongo_docs,
        rule_name,
        expected_orders,
        expected_candidates,
        replication_sync_api,
        fake_task_id,
        replication_state_min_ts,
        requests_handlers,
):
    replication_state_min_ts.apply(
        {'orders': ('updated', datetime.datetime(2018, 1, 2, 0, 0, 29))},
    )
    replication_sync_api.set_default_status(
        replication_sync_api.STATUS_INSERTED,
    )
    archivers = await cron_run.prepare_archivers(
        cron_context, rule_name, fake_task_id,
    )
    archiver = next(iter(archivers.values()))
    original_get_candidates = archiver._get_all_candidates_cursor
    candidates = set()

    async def patched_get_candidates():
        original_candidates = await original_get_candidates()

        async def _get_candidates():
            async for candidate in original_candidates:
                candidates.add(candidate['_id'])
                yield candidate

        return _get_candidates()

    monkeypatch.setattr(
        archiver, '_get_all_candidates_cursor', patched_get_candidates,
    )

    await core.remove_documents(archiver, cron_context.client_solomon)

    orders = set(await load_all_mongo_docs(rule_name))
    assert orders == expected_orders
    assert candidates == expected_candidates

    assert replication_sync_api.handler.times_called == 1
    assert replication_state_min_ts.handler.times_called == 2


@pytest.mark.config(ARCHIVE_ORDERS_INTERVAL=864000)
@pytest.mark.now('2018-01-15T00:00:35.0')
@pytest.mark.parametrize(
    'rule_name,expected_orders',
    [('orders_hourly', {'to_be_archived_hourly_fresh_replicate_by'})],
)
@pytest.mark.filldb(orders='replicate_by')
async def test_archived_replicate_by_usage(
        cron_context,
        monkeypatch,
        load_all_mongo_docs,
        rule_name,
        expected_orders,
        replication_sync_api,
        fake_task_id,
        replication_state_min_ts,
        requests_handlers,
):
    replication_state_min_ts.apply(
        {'orders': ('updated', datetime.datetime(2018, 1, 2, 0, 0, 29))},
    )
    replication_sync_api.set_default_status(
        replication_sync_api.STATUS_INSERTED,
    )
    archivers = await cron_run.prepare_archivers(
        cron_context, rule_name, fake_task_id,
    )
    archiver = next(iter(archivers.values()))

    await core.remove_documents(archiver, cron_context.client_solomon)
    orders = set(await load_all_mongo_docs(rule_name))
    assert orders == expected_orders
