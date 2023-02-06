import pytest

WORKER_STATS_MONITOR = 'cargo-sdd-worker-stats-monitor'
WORKER_STATS_MONITOR_CONFIG = {
    'is_enabled': True,
    'launches_pause_ms': 0,
    'disabled_pause_ms': 10000,
    'routing_runner_settings': {
        'is_enabled': True,
        'query_queue_size': True,
        'query_segments_in_routing': True,
        'query_segments_dropped': True,
        'query_routing_response_rate': True,
        'query_oldest_segment_lag': True,
    },
    'query_segment_resolution_time': True,
    'query_autoreorder_iteration': True,
}


@pytest.fixture(name='run_worker_stats_monitor')
def _run_worker_stats_monitor(run_task_once):
    async def _wrapper():
        return await run_task_once(WORKER_STATS_MONITOR)

    return _wrapper


@pytest.mark.config(CARGO_SDD_WORKER_STATS_MONITOR=WORKER_STATS_MONITOR_CONFIG)
async def test_no_stats(run_worker_stats_monitor):
    result = await run_worker_stats_monitor()
    assert result == {
        'routing-runner': {
            'oldest-segment-lag-ms': 0,
            'queue-size': 0,
            'segments-in-routing': 0,
            'segments-dropped': 0,
            'response-rate-stats-1min': {
                'p50': 0,
                'p95': 0,
                'p98': 0,
                'p99': 0,
                'p100': 0,
            },
        },
        'segment-resolution-time-1min': {
            'p50': 0,
            'p95': 0,
            'p98': 0,
            'p99': 0,
            'p100': 0,
        },
        'autoreorder-iteration': {
            'p50': 0,
            'p95': 0,
            'p98': 0,
            'p99': 0,
            'p100': 0,
        },
    }


@pytest.mark.config(CARGO_SDD_WORKER_STATS_MONITOR=WORKER_STATS_MONITOR_CONFIG)
@pytest.mark.now('2021-10-30T12:44:00+00:00')
async def test_autoreorder_and_resolution_time(
        pgsql, run_worker_stats_monitor,
):
    cursor = pgsql['cargo_sdd'].cursor()
    cursor.execute(
        """
        INSERT INTO cargo_sdd.segments(
            segment_id, revision, corp_client_id,
            status, waybill_building_version, zone_id,
            updated_ts, proposition_ref, routing_task_id
        )
        VALUES (
            'seg1', 1, 'corp_id',
            'waybill_proposed', 1, 'moscow',
            '2021-10-30T12:15:00+00:00'::TIMESTAMPTZ,
            'cargo_same_day_delivery_router/task_id_1/park1_driver1_1',
            'task_id_1'
        ),
        (
            'seg2', 2, 'corp_id',
            'waybill_proposed', 1, 'moscow',
            '2021-10-30T12:15:00+00:00'::TIMESTAMPTZ,
            'cargo_same_day_delivery_router/task_id_1/park1_driver1_1',
            'task_id_1'
        ),
        (
            'seg3', 1, 'corp_id',
            'waybill_proposed', 1, 'moscow',
            '2021-10-30T12:15:00+00:00'::TIMESTAMPTZ,
            'cargo_same_day_delivery_router/task_id_1/park1_driver1_1',
            'task_id_1'
        ),
        (
            'seg_4', 1, 'corp_id',
            'waybill_proposed', 1, 'moscow',
            '2021-10-30T12:00:00+00:00'::TIMESTAMPTZ,
            'cargo_same_day_delivery_router/task_id_2/park1_driver1_6',
            'task_id_2'
        );
        INSERT INTO cargo_sdd.routing_tasks(
        id, task_id, idempotency_token, status, zone_id, segments_count,
        couriers_count, created_ts, updated_ts, finish_ts
        )
        VALUES (
            '1', 'task_id_1', 'token1',
            'SOLVED', 'moscow', 1, 1,
            '2021-10-30T12:00:00+00:00'::TIMESTAMPTZ,
            '2021-10-30T12:20:00+00:00'::TIMESTAMPTZ,
            '2021-10-30T12:20:00+00:00'::TIMESTAMPTZ
        ),
        (
            '2', 'task_id_2', 'token2',
            'SOLVED', 'moscow', 1, 1,
            '2021-10-30T12:00:00+00:00'::TIMESTAMPTZ,
            '2021-10-30T12:05:00+00:00'::TIMESTAMPTZ,
            '2021-10-30T12:05:00+00:00'::TIMESTAMPTZ
        );
        """,
    )

    result = await run_worker_stats_monitor()
    assert result['segment-resolution-time-1min']['p50'] == 29
    assert result['segment-resolution-time-1min']['p95'] == 44
    assert result['autoreorder-iteration']['p50'] == 1
    assert result['autoreorder-iteration']['p95'] == 6


@pytest.mark.config(
    CARGO_SDD_ZONE_SETTINGS_BY_CLIENTS={
        'moscow': [
            {
                'delivery_guarantees': [
                    {
                        'orders_created_till': '1970-01-01T12:00:00+00:00',
                        'start_routing_at': '1970-01-01T12:00:00+00:00',
                        'pickup_till': '1970-01-01T13:00:00+00:00',
                        'deliver_till': '1970-01-01T16:00:00+00:00',
                        'waybill_building_deadline': (
                            '1970-01-01T13:00:00+00:00'
                        ),
                    },
                    {
                        'orders_created_till': '1970-01-01T12:10:00+00:00',
                        'start_routing_at': '1970-01-01T12:10:00+00:00',
                        'pickup_till': '1970-01-01T13:00:00+00:00',
                        'deliver_till': '1970-01-01T17:00:00+00:00',
                        'waybill_building_deadline': (
                            '1970-01-01T13:00:00+00:00'
                        ),
                    },
                    {
                        'orders_created_till': '1970-01-01T11:40:00+00:00',
                        'start_routing_at': '1970-01-01T11:40:00+00:00',
                        'pickup_till': '1970-01-01T13:00:00+00:00',
                        'deliver_till': '1970-01-01T16:00:00+00:00',
                        'waybill_building_deadline': (
                            '1970-01-01T13:00:00+00:00'
                        ),
                    },
                ],
                'couriers': [
                    {'park_id': 'park1', 'driver_id': 'driver1'},
                    {'park_id': 'park2', 'driver_id': 'driver2'},
                ],
                'taxi_classes': [],
                'fake_depot': {'lon': 0, 'lat': 0},
            },
        ],
    },
)
@pytest.mark.now('2021-10-30T12:10:02+0000')
@pytest.mark.config(CARGO_SDD_WORKER_STATS_MONITOR=WORKER_STATS_MONITOR_CONFIG)
async def test_routing_runner_stats(pgsql, run_worker_stats_monitor):
    cursor = pgsql['cargo_sdd'].cursor()
    cursor.execute(
        """
        INSERT INTO cargo_sdd.segments(
            segment_id, revision, corp_client_id,
            status, waybill_building_version, zone_id, created_ts,
            delivery_interval_from
        )
        VALUES (
            'seg1', 1, 'corp_id',
            'waybill_building_awaited', 1, 'moscow',
            '2021-10-30T11:30:00+00:00'::TIMESTAMPTZ,
            '2021-10-30T12:10:00+00:00'
        ),
        (
            'seg2', 2, 'corp_id',
            'inactive', 1, 'moscow',
            '2021-10-30T08:55:00+00:00'::TIMESTAMPTZ,
            NULL
        ),
        (
            'seg3', 1, 'corp_id',
            'waybill_building_awaited', 1, 'moscow',
            '2021-10-30T11:59:00+00:00'::TIMESTAMPTZ,
            NULL
        ),
        (
            'seg_4', 1, 'corp_id',
            'routing_launched', 1, 'moscow',
            '2021-10-30T11:30:00+00:00'::TIMESTAMPTZ,
            NULL
        ),
        (
            'seg_5', 1, 'corp_id',
            'waybill_proposed', 1, 'moscow',
            '2021-10-30T11:30:00+00:00'::TIMESTAMPTZ,
            NULL
        ),
        (
            'seg_6', 1, 'corp_id',
            'routing_launched', 1, 'moscow',
            '2021-10-30T11:30:00+00:00'::TIMESTAMPTZ,
            NULL
        ),
        (
            'seg_7', 1, 'corp_id',
            'dropped', 1, 'moscow',
            '2021-10-30T11:30:00+00:00'::TIMESTAMPTZ,
            NULL
        )
        """,
    )

    result = await run_worker_stats_monitor()
    assert result['routing-runner']['queue-size'] == 2
    assert result['routing-runner']['segments-in-routing'] == 2
    assert result['routing-runner']['segments-dropped'] == 1
    assert result['routing-runner']['oldest-segment-lag-ms'] == 2000


@pytest.mark.config(CARGO_SDD_WORKER_STATS_MONITOR=WORKER_STATS_MONITOR_CONFIG)
async def test_response_rate_stats(pgsql, run_worker_stats_monitor):
    cursor = pgsql['cargo_sdd'].cursor()
    cursor.execute(
        """
        INSERT INTO cargo_sdd.segments(
            segment_id, revision, corp_client_id,
            status, waybill_building_version, zone_id,
            created_ts, routing_task_id
        )
        VALUES (
            'seg1', 1, 'corp_id',
            'waybill_proposed', 1, 'moscow',
            '2021-10-30T11:30:00+00:00'::TIMESTAMPTZ,
            'task_id_1'
        ),
        (
            'seg2', 2, 'corp_id',
            'waybill_proposed', 1, 'moscow',
            '2021-10-30T11:30:00+00:00'::TIMESTAMPTZ,
            'task_id_2'
        ),
        (
            'seg3', 1, 'corp_id',
            'waybill_proposed', 1, 'moscow',
            '2021-10-30T11:30:00+00:00'::TIMESTAMPTZ,
            'task_id_2'
        ),
        (
            'seg_4', 1, 'corp_id',
            'waybill_proposed', 1, 'moscow',
            '2021-10-30T11:30:00+00:00'::TIMESTAMPTZ,
            'task_id_2'
        );
        INSERT INTO cargo_sdd.routing_tasks(
        id, task_id, idempotency_token, status, zone_id, segments_count,
        couriers_count, created_ts, updated_ts, finish_ts
        )
        VALUES (
            '1', 'task_id_1', 'token1',
            'SOLVED', 'moscow', 1, 1,
            '2021-10-30T12:00:00+00:00'::TIMESTAMPTZ,
            '2021-10-30T12:20:00+00:00'::TIMESTAMPTZ,
            '2021-10-30T12:20:00+00:00'::TIMESTAMPTZ
        ),
        (
            '2', 'task_id_2', 'token2',
            'SOLVED', 'moscow', 1, 1,
            '2021-10-30T12:00:00+00:00'::TIMESTAMPTZ,
            '2021-10-30T12:05:00+00:00'::TIMESTAMPTZ,
            '2021-10-30T12:05:00+00:00'::TIMESTAMPTZ
        )
        """,
    )
    result = await run_worker_stats_monitor()

    assert result['routing-runner']['response-rate-stats-1min']['p50'] == 5
    assert result['routing-runner']['response-rate-stats-1min']['p95'] == 20
