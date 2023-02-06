# pylint: disable=redefined-outer-name
import datetime
import uuid

import bson
import psycopg2
import pytest

JOB_NAME = 'manual-dispatch-statistics-counter'
pytestmark = [  # pylint: disable=invalid-name
    pytest.mark.experiments3(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='manual_dispatch_override_rule',
        consumers=['manual-dispatch/handle-create'],
        clauses=[
            {
                'value': {'enabled': True},
                'predicate': {'init': {}, 'type': 'true'},
            },
        ],
        is_config=True,
        default_value={'tags': []},
    ),
]


def clean_stats(new_stats, old_stats):
    if old_stats is not None:
        new_stats = {
            key: value - old_stats.get(key, 0)
            for key, value in new_stats.items()
            if old_stats.get(key) != value
        }
    return new_stats


def get_finish_kwargs(order_status):
    if order_status == 'cancelled':
        return {
            'taxi_status': None,
            'status': 'cancelled',
            'has_performer': False,
        }
    if order_status == 'cancelled_by_taxi':
        return {
            'taxi_status': 'cancelled',
            'status': 'finished',
            'has_performer': False,
        }
    if order_status == 'search_failed':
        return {
            'taxi_status': 'expired',
            'status': 'finished',
            'has_performer': False,
        }
    if order_status == 'expired':
        return {
            'taxi_status': 'expired',
            'status': 'finished',
            'has_performer': True,
        }
    if order_status == 'finished':
        return {
            'taxi_status': 'complete',
            'status': 'finished',
            'has_performer': True,
        }
    if order_status == 'failed':
        return {
            'taxi_status': 'failed',
            'status': 'finished',
            'has_performer': True,
        }
    raise ValueError(f'unknown status: {order_status}')


@pytest.fixture
def run_transition(pgsql, stq_runner, get_order):
    cursor = pgsql['manual-dispatch'].conn.cursor(
        cursor_factory=psycopg2.extras.DictCursor,
    )

    async def wrapped(order_id, status, prev, lookup_version, delta=None):
        time = datetime.datetime.now(tz=datetime.timezone.utc) - (
            delta or datetime.timedelta(seconds=30)
        )
        if prev is not None:
            cursor.execute(
                'UPDATE manual_dispatch.order_audit SET event_time=%s '
                'WHERE order_id=%s AND status=%s',
                (time, order_id, prev),
            )
        if status == 'pending' and prev is None:
            await stq_runner.manual_dispatch_handle_create.call(
                task_id=order_id,
                args=[],
                kwargs={
                    'client_id': 'client_id_1',
                    'created': datetime.datetime.now(),
                    'tariffs': ['courier'],
                    'claim_id': 'claim_id_1',
                    'due': None,
                    'order_type': 'b2b',
                    'zone_id': 'moscow',
                    'user_tags': ['tag1', 'tag2'],
                },
            )
        elif status == 'pending' and prev == 'assigned':
            await stq_runner.manual_dispatch_handle_autoreorder.call(
                task_id=str(uuid.uuid4()),
                args=[],
                kwargs={
                    'order_id': order_id,
                    'lookup_version': lookup_version,
                },
            )
        elif status == 'assigned' and prev == 'pending':
            await stq_runner.manual_dispatch_handle_driving.call(
                task_id=str(uuid.uuid4()),
                args=[],
                kwargs={
                    'order_id': order_id,
                    'performer_dbid': 'someparkid',
                    'performer_uuid': 'someuuid',
                    'lookup_version': lookup_version,
                },
            )
        elif status in (
            'cancelled',
            'cancelled_by_taxi',
            'finished',
            'search_failed',
            'expired',
            'failed',
        ) and prev in ('assigned', 'pending'):
            await stq_runner.manual_dispatch_handle_finish.call(
                task_id=order_id,
                args=[],
                kwargs={
                    **get_finish_kwargs(status),
                    'lookup_version': lookup_version,
                },
                expect_fail=False,
            )
        else:
            raise ValueError(f'Unknown transition: {prev}->{status}')

        order = get_order(order_id)
        assert order['status'] == status
        return order['updated_ts'] - time

    return wrapped


@pytest.fixture
def emulate_order(mockserver, load_json, run_transition):
    @mockserver.json_handler(
        '/order-core/internal/processing/v1/order-proc/get-fields',
    )
    def _get_order_fields(request):
        return mockserver.make_response(
            status=200,
            content_type='application/bson',
            response=bson.BSON.encode(load_json('order_fields_response.json')),
        )

    @mockserver.json_handler(
        '/order-core/internal/processing/v1/order-proc/set-fields',
    )
    def _set_order_fields(request):
        return mockserver.make_response(
            status=200,
            content_type='application/bson',
            response=bson.BSON.encode(load_json('order_fields_response.json')),
        )

    @mockserver.json_handler(
        '/order-core/internal/processing/v1/event/start-lookup',
    )
    def _start_lookup(request):
        assert bson.BSON.decode(request.get_data()) == {
            'filters': {'status': 'pending'},
        }
        return mockserver.make_response('', status=200)

    async def wrapped(order_id, statuses):
        prev = None
        for lookup_version, curr in enumerate(statuses):
            await run_transition(order_id, curr, prev, lookup_version)
            prev = curr

    return wrapped


@pytest.mark.xfail(reason='CARGODEV-11510')
@pytest.mark.config(
    MANUAL_DISPATCH_STATISTICS_COUNTER_SETTINGS={
        'enabled': True,
        'sleep_time_ms': 0,
    },
    MANUAL_DISPATCH_STATISTICS_AGGREGATOR_SETTINGS={
        'enabled': True,
        'sleep_time_ms': 0,
        'throttle_ms': 0,
        'graph_ranges': [24],
    },
    MANUAL_DISPATCH_DISABLE_LEGACY_HANDLERS=True,
)
@pytest.mark.suspend_periodic_tasks('manual-dispatch-statistics-counter')
async def test_statistics_jobs(
        taxi_manual_dispatch,
        emulate_order,
        create_order,
        taxi_manual_dispatch_monitor,
        create_dispatch_attempt,
        pgsql,
        headers,
):
    for i, status_list in enumerate(
            [
                ['pending', 'assigned', 'pending', 'search_failed'],
                ['pending', 'search_failed'],
                ['pending', 'assigned', 'finished'],
                ['pending', 'assigned', 'finished'],
                ['pending', 'assigned', 'pending', 'cancelled'],
                ['pending', 'assigned', 'pending', 'cancelled'],
                ['pending', 'assigned', 'cancelled_by_taxi'],
                ['pending', 'assigned', 'cancelled_by_taxi'],
                ['pending', 'assigned', 'cancelled_by_taxi'],
                ['pending', 'assigned', 'failed'],
                ['pending', 'assigned', 'failed'],
                ['pending', 'expired'],
                ['pending', 'expired'],
            ],
    ):
        await emulate_order(f'order_id_{i}', status_list)

    create_order(
        order_id=f'order_id_100',
        status='pending',
        manual_switch_interval=datetime.timedelta(seconds=0),
        owner_operator_id='1234',
        lock_expiration_ts=datetime.datetime.now()
        + datetime.timedelta(hours=2),
    )
    create_order(
        order_id=f'order_id_101',
        status='pending',
        manual_switch_interval=datetime.timedelta(hours=2),
    )
    create_order(
        order_id=f'order_id_102',
        status='pending',
        manual_switch_interval=datetime.timedelta(hours=0),
    )
    create_dispatch_attempt(order_id='order_id_1')
    await taxi_manual_dispatch.run_task(
        'manual-dispatch-statistics-aggregator',
    )

    stats = await taxi_manual_dispatch_monitor.get_metric('md-stats-agg')
    assert stats['24h'] == {
        'assigned_manually': 0,
        'cancelled': 2,
        'failed': 2,
        'finished': 2,
        'has_attempts': 1,
        'locked': 0,
        'manual_error': 0,
        'reached_manual_ts': 0,
        'total': 13,
    }

    cursor = pgsql['manual-dispatch'].conn.cursor()
    cursor.execute('ANALYZE')  # update pg_stats
    await taxi_manual_dispatch.run_periodic_task(JOB_NAME)
    stats = await taxi_manual_dispatch_monitor.get_metric('md-stats')
    assert stats == {
        'status_counts': {
            'cancelled': 2,
            'cancelled_by_taxi': 3,
            'finished': 2,
            'search_failed': 2,
            'pending': 3,
            'failed': 2,
            'expired': 2,
            'total': 16,
        },
    }
    response = await taxi_manual_dispatch.get(
        '/v1/orders/statistics', headers=headers,
    )
    assert response.status_code == 200
    response = response.json()
    response['statistics'] = sorted(
        response['statistics'], key=lambda x: x['state'],
    )
    response['statistics'] = frozenset(
        [
            frozenset((k, v) for k, v in d.items())
            for d in response['statistics']
        ],
    )
    assert response == {
        'statistics': frozenset(
            [
                frozenset({('state', 'finished'), ('count', 2)}),
                frozenset({('state', 'in_progress'), ('count', 0)}),
                frozenset({('state', 'locked'), ('count', 1)}),
                frozenset({('state', 'pending'), ('count', 1)}),
                frozenset({('state', 'search_failed'), ('count', 2)}),
            ],
        ),
        'polling_delay_ms': 15000,
    }


@pytest.mark.config(MANUAL_DISPATCH_DISABLE_LEGACY_HANDLERS=True)
async def test_transition_stats(emulate_order, taxi_manual_dispatch_monitor):
    old_stats = await taxi_manual_dispatch_monitor.get_metric(
        'status-transitions',
    )

    for i, status_list in enumerate(
            [
                ['pending', 'assigned', 'pending', 'search_failed'],
                ['pending', 'search_failed'],
                ['pending', 'assigned', 'finished'],
                ['pending', 'assigned', 'pending', 'cancelled'],
                ['pending', 'assigned', 'cancelled_by_taxi'],
                ['pending', 'assigned', 'failed'],
                ['pending', 'expired'],
            ],
    ):
        await emulate_order(f'order_id_{i}', status_list)

    stats = await taxi_manual_dispatch_monitor.get_metric('status-transitions')
    assert stats is not None
    stats = clean_stats(stats, old_stats)
    assert stats == {
        'new-to-pending': 7,
        'assigned-to-pending': 2,
        'pending-to-assigned': 5,
        'assigned-to-finished': 1,
        'pending-to-search_failed': 2,
        'pending-to-cancelled': 1,
        'assigned-to-cancelled_by_taxi': 1,
        'assigned-to-failed': 1,
        'pending-to-expired': 1,
    }

    stats = await taxi_manual_dispatch_monitor.get_metric('status-durations')
    assert stats is not None
    for transition in (
            'assigned-to-cancelled_by_taxi',
            'assigned-to-failed',
            'assigned-to-finished',
            'assigned-to-pending',
            'pending-to-assigned',
            'pending-to-cancelled',
            'pending-to-expired',
            'pending-to-search_failed',
    ):
        assert stats[transition]['max'] >= 30, repr(stats)


@pytest.mark.config(
    MANUAL_DISPATCH_LOOKUP_SETTINGS={
        'assign_driver_seconds': 60,
        'enable_defreeze': False,
        'new_way_enabled': True,
        'fail_on_reject': False,
        'old_way_fallback_enabled': False,
    },
)
async def test_attempt_stats(
        stq_runner,
        taxi_manual_dispatch,
        taxi_manual_dispatch_monitor,
        create_order,
        headers,
        create_dispatch_attempt,
        get_dispatch_attempt,
):
    old_stats = await taxi_manual_dispatch_monitor.get_metric(
        'attempt-resolutions',
    )
    create_order(
        order_id='order_id_1',
        owner_operator_id='yandex_uid_1',
        lock_expiration_ts=datetime.datetime.now()
        + datetime.timedelta(days=1),
    )
    response = await taxi_manual_dispatch.post(
        'v1/dispatch/offer',
        headers=headers,
        json={
            'order_id': 'order_id_1',
            'park_id': 'dbid1',
            'driver_id': 'uuid1',
        },
    )
    assert response.status_code == 200
    await stq_runner.manual_dispatch_handle_driving.call(
        task_id=str(uuid.uuid4()),
        args=[],
        kwargs={
            'order_id': 'order_id_1',
            'performer_dbid': 'dbid1',
            'performer_uuid': 'parkid1',
            'lookup_version': 2,
        },
    )
    create_order(
        order_id='order_id_2',
        owner_operator_id='yandex_uid_2',
        lock_expiration_ts=datetime.datetime.now()
        + datetime.timedelta(days=1),
    )
    create_dispatch_attempt(
        order_id='order_id_2',
        expiration_ts=datetime.datetime.now(tz=datetime.timezone.utc)
        - datetime.timedelta(days=1),
    )
    response = await taxi_manual_dispatch.post(
        'v1/lookup', json={'foo': 'bar', 'order_id': 'order_id_2'},
    )
    assert response.status_code == 200
    stats = await taxi_manual_dispatch_monitor.get_metric(
        'attempt-resolutions',
    )
    stats = clean_stats(stats, old_stats)
    assert stats == {'pending': 1, 'expired': 1, 'overridden': 1}
