import pytest


async def get_sdd_segments(pgsql):
    cursor = pgsql['cargo_sdd'].cursor()
    cursor.execute(
        """
        SELECT segment_id, revision, status
        FROM cargo_sdd.segments
        ORDER BY id
        """,
    )
    return cursor.fetchall()


async def get_sdd_segments_with_exp_title(pgsql):
    cursor = pgsql['cargo_sdd'].cursor()
    cursor.execute(
        """
        SELECT segment_id, revision, status, exp3_settings_alias
        FROM cargo_sdd.segments
        ORDER BY id
        """,
    )
    return cursor.fetchall()


@pytest.fixture(name='run_routing_runner')
def _run_routing_runner(run_task_once):
    async def _wrapper():
        return await run_task_once('routing-runner')

    return _wrapper


@pytest.mark.config(
    CARGO_SDD_ROUTING_RUNNER_SETTINGS={
        'enabled': True,
        'launches_pause_sec': 0,
    },
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
                ],
                'couriers': [{'park_id': 'park1', 'driver_id': 'driver1'}],
                'taxi_classes': [],
                'fake_depot': {'lon': 0, 'lat': 0},
            },
        ],
    },
)
@pytest.mark.now('2021-10-30T12:45:00+00:00')
async def test_happy_path(run_routing_runner, mockserver, pgsql, stq):
    cursor = pgsql['cargo_sdd'].cursor()
    cursor.execute(
        """
        INSERT INTO cargo_sdd.segments(
            segment_id, revision, corp_client_id,
            status, waybill_building_version, zone_id, created_ts
        )
        VALUES (
            'seg1', 1, 'corp_id',
            'waybill_building_awaited', 1, 'moscow',
            '2021-10-30T11:30:00+00:00'::TIMESTAMPTZ
        ),
        (
            'seg2', 1, 'corp_id',
            'waybill_building_awaited', 1, 'moscow',
            '2021-10-30T08:55:00+00:00'::TIMESTAMPTZ
        ),
        (
            'seg3', 1, 'corp_id',
            'waybill_building_awaited', 1, 'moscow',
            '2021-10-30T12:05:00+00:00'::TIMESTAMPTZ
        )

        """,
    )
    result = await run_routing_runner()
    assert result['segments-processed-count'] == 2

    assert stq.cargo_sdd_start_routing_by_zone.times_called == 1
    stq_call = stq.cargo_sdd_start_routing_by_zone.next_call()
    assert stq_call['id'] == 'moscow_2021_10_30_2021-10-30T12:00:00Z'
    assert stq_call['kwargs']['zone_id'] == 'moscow'
    assert stq_call['kwargs']['threshold'] == '2021-10-30T12:00:00+00:00'
    assert 'corp_client_ids' not in stq_call['kwargs']


@pytest.mark.config(
    CARGO_SDD_ROUTING_RUNNER_SETTINGS={
        'enabled': True,
        'launches_pause_sec': 0,
    },
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
                ],
                'couriers': [{'park_id': 'park1', 'driver_id': 'driver1'}],
                'taxi_classes': [],
                'fake_depot': {'lon': 0, 'lat': 0},
            },
        ],
    },
)
@pytest.mark.now('2021-10-30T12:05:00+00:00')
async def test_no_new_segments(run_routing_runner, mockserver, pgsql, stq):
    cursor = pgsql['cargo_sdd'].cursor()
    cursor.execute(
        """
        INSERT INTO cargo_sdd.segments(
            segment_id, revision, corp_client_id,
            status, waybill_building_version, zone_id, created_ts
        )
        VALUES (
            'seg1', 1, 'corp_id',
            'waybill_building_awaited', 1, 'moscow',
            '2021-10-30T12:30:00+00:00'::TIMESTAMPTZ
        )
        """,
    )

    result = await run_routing_runner()
    assert result['segments-processed-count'] == 0
    assert not stq.cargo_sdd_start_routing_by_zone.times_called


@pytest.mark.config(
    CARGO_SDD_ROUTING_RUNNER_SETTINGS={
        'enabled': True,
        'launches_pause_sec': 0,
    },
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
                ],
                'couriers': [{'park_id': 'park1', 'driver_id': 'driver1'}],
                'taxi_classes': [],
                'fake_depot': {'lon': 0, 'lat': 0},
            },
        ],
    },
)
@pytest.mark.now('2021-10-30T11:45:00+00:00')
async def test_no_intervals_fit(run_routing_runner, mockserver, pgsql, stq):
    cursor = pgsql['cargo_sdd'].cursor()
    cursor.execute(
        """
        INSERT INTO cargo_sdd.segments(
            segment_id, revision, corp_client_id,
            status, waybill_building_version, zone_id, created_ts
        )
        VALUES (
            'seg1', 1, 'corp_id',
            'waybill_building_awaited', 1, 'moscow',
            '2021-10-30T11:30:00+00:00'::TIMESTAMPTZ
        )
        """,
    )
    result = await run_routing_runner()
    assert result['segments-processed-count'] == 0
    assert not stq.cargo_sdd_start_routing_by_zone.times_called == 1


@pytest.mark.config(
    CARGO_SDD_ROUTING_RUNNER_SETTINGS={
        'enabled': True,
        'launches_pause_sec': 0,
    },
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
                        'orders_created_till': '1970-01-01T14:00:00+00:00',
                        'start_routing_at': '1970-01-01T14:00:00+00:00',
                        'pickup_till': '1970-01-01T15:00:00+00:00',
                        'deliver_till': '1970-01-01T18:00:00+00:00',
                        'waybill_building_deadline': (
                            '1970-01-01T15:00:00+00:00'
                        ),
                    },
                ],
                'couriers': [{'park_id': 'park1', 'driver_id': 'driver1'}],
                'taxi_classes': [],
                'fake_depot': {'lon': 0, 'lat': 0},
            },
        ],
    },
)
@pytest.mark.now('2021-10-30T13:35:00+00:00')
async def test_many_intervals_1(run_routing_runner, mockserver, pgsql, stq):
    cursor = pgsql['cargo_sdd'].cursor()
    cursor.execute(
        """
        INSERT INTO cargo_sdd.segments(
            segment_id, revision, corp_client_id,
            status, waybill_building_version, zone_id, created_ts
        )
        VALUES (
            'seg1', 1, 'corp_id',
            'waybill_building_awaited', 1, 'moscow',
            '2021-10-30T11:30:00+00:00'::TIMESTAMPTZ
        ),
        (
            'seg2', 1, 'corp_id',
            'waybill_building_awaited', 1, 'moscow',
            '2021-10-30T13:30:00+00:00'::TIMESTAMPTZ
        )
        """,
    )
    result = await run_routing_runner()
    assert result['segments-processed-count'] == 1
    assert stq.cargo_sdd_start_routing_by_zone.times_called == 1
    stq_call = stq.cargo_sdd_start_routing_by_zone.next_call()
    assert stq_call['id'] == 'moscow_2021_10_30_2021-10-30T12:00:00Z'
    assert stq_call['kwargs']['zone_id'] == 'moscow'
    assert stq_call['kwargs']['threshold'] == '2021-10-30T12:00:00+00:00'


@pytest.mark.config(
    CARGO_SDD_ROUTING_RUNNER_SETTINGS={
        'enabled': True,
        'launches_pause_sec': 0,
    },
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
                        'orders_created_till': '1970-01-01T14:00:00+00:00',
                        'start_routing_at': '1970-01-01T14:00:00+00:00',
                        'pickup_till': '1970-01-01T15:00:00+00:00',
                        'deliver_till': '1970-01-01T18:00:00+00:00',
                        'waybill_building_deadline': (
                            '1970-01-01T15:00:00+00:00'
                        ),
                    },
                ],
                'couriers': [{'park_id': 'park1', 'driver_id': 'driver1'}],
                'taxi_classes': [],
                'fake_depot': {'lon': 0, 'lat': 0},
            },
        ],
    },
)
@pytest.mark.now('2021-10-30T15:00:00+00:00')
async def test_many_intervals_2(run_routing_runner, mockserver, pgsql, stq):
    cursor = pgsql['cargo_sdd'].cursor()
    cursor.execute(
        """
        INSERT INTO cargo_sdd.segments(
            segment_id, revision, corp_client_id,
            status, waybill_building_version, zone_id, created_ts
        )
        VALUES (
            'seg1', 1, 'corp_id',
            'waybill_building_awaited', 1, 'moscow',
            '2021-10-30T11:30:00+00:00'::TIMESTAMPTZ
        ),
        (
            'seg2', 1, 'corp_id',
            'waybill_building_awaited', 1, 'moscow',
            '2021-10-30T13:30:00+00:00'::TIMESTAMPTZ
        )
        """,
    )
    result = await run_routing_runner()
    assert result['segments-processed-count'] == 2
    assert stq.cargo_sdd_start_routing_by_zone.times_called == 1
    stq_call = stq.cargo_sdd_start_routing_by_zone.next_call()
    assert stq_call['id'] == 'moscow_2021_10_30_2021-10-30T14:00:00Z'
    assert stq_call['kwargs']['zone_id'] == 'moscow'
    assert stq_call['kwargs']['threshold'] == '2021-10-30T14:00:00+00:00'


@pytest.mark.config(
    CARGO_SDD_ROUTING_RUNNER_SETTINGS={
        'enabled': True,
        'launches_pause_sec': 0,
    },
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
                ],
                'couriers': [{'park_id': 'park1', 'driver_id': 'driver1'}],
                'taxi_classes': [],
                'fake_depot': {'lon': 0, 'lat': 0},
            },
            {
                'corp_client_ids': ['111', '333'],
                'delivery_guarantees': [
                    {
                        'orders_created_till': '1970-01-01T12:00:00+00:00',
                        'start_routing_at': '1970-01-01T12:10:00+00:00',
                        'pickup_till': '1970-01-01T13:00:00+00:00',
                        'deliver_till': '1970-01-01T16:00:00+00:00',
                        'waybill_building_deadline': (
                            '1970-01-01T13:00:00+00:00'
                        ),
                    },
                ],
                'couriers': [{'park_id': 'park2', 'driver_id': 'driver2'}],
                'taxi_classes': [],
                'fake_depot': {'lon': 0, 'lat': 0},
            },
        ],
    },
)
@pytest.mark.now('2021-10-30T12:45:00+00:00')
async def test_different_corp_intervals(
        run_routing_runner, mockserver, pgsql, stq,
):
    cursor = pgsql['cargo_sdd'].cursor()
    cursor.execute(
        """
        INSERT INTO cargo_sdd.segments(
            segment_id, revision, corp_client_id,
            status, waybill_building_version, zone_id, created_ts
        )
        VALUES (
            'seg1', 1, '111',
            'waybill_building_awaited', 1, 'moscow',
            '2021-10-30T11:30:00+00:00'::TIMESTAMPTZ
        ),
        (
            'seg2', 1, '222',
            'waybill_building_awaited', 1, 'moscow',
            '2021-10-30T08:55:00+00:00'::TIMESTAMPTZ
        ),
        (
            'seg3', 1, '333',
            'waybill_building_awaited', 1, 'moscow',
            '2021-10-30T11:35:00+00:00'::TIMESTAMPTZ
        )

        """,
    )

    result = await run_routing_runner()
    assert result['segments-processed-count'] == 3
    assert stq.cargo_sdd_start_routing_by_zone.times_called == 2

    stq_call = stq.cargo_sdd_start_routing_by_zone.next_call()
    assert stq_call['id'].startswith('moscow_2021_10_30_2021-10-30T12:10:00Z_')
    assert stq_call['kwargs']['zone_id'] == 'moscow'
    assert stq_call['kwargs']['threshold'] == '2021-10-30T12:10:00+00:00'
    assert stq_call['kwargs']['corp_client_ids'] == ['111', '333']
    assert 'ignore_corp_ids' not in stq_call['kwargs']

    stq_call = stq.cargo_sdd_start_routing_by_zone.next_call()
    assert stq_call['id'] == 'moscow_2021_10_30_2021-10-30T12:00:00Z'
    assert stq_call['kwargs']['zone_id'] == 'moscow'
    assert stq_call['kwargs']['threshold'] == '2021-10-30T12:00:00+00:00'
    assert 'corp_client_ids' not in stq_call['kwargs']
    assert stq_call['kwargs']['ignore_corp_ids'] == ['111', '333']


@pytest.mark.config(
    CARGO_SDD_ROUTING_RUNNER_SETTINGS={
        'enabled': True,
        'launches_pause_sec': 0,
    },
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
                ],
                'couriers': [{'park_id': 'park1', 'driver_id': 'driver1'}],
                'taxi_classes': [],
                'fake_depot': {'lon': 0, 'lat': 0},
            },
        ],
    },
)
@pytest.mark.now('2021-10-30T12:45:00+00:00')
async def test_delivery_interval(run_routing_runner, mockserver, pgsql, stq):
    cursor = pgsql['cargo_sdd'].cursor()
    cursor.execute(
        """
        INSERT INTO cargo_sdd.segments(
            segment_id, revision, corp_client_id,
            status, waybill_building_version, zone_id, created_ts,
            delivery_interval_from, delivery_interval_to
        )
        VALUES (
            'seg1', 1, 'corp_id',
            'waybill_building_awaited', 1, 'moscow',
            '2021-10-30T11:30:00+00:00'::TIMESTAMPTZ,
            '2021-10-30T13:30:00+00:00'::TIMESTAMPTZ,
            '2021-10-30T17:30:00+00:00'::TIMESTAMPTZ
        )
        """,
    )
    result = await run_routing_runner()
    assert result['segments-processed-count'] == 0
    assert not stq.cargo_sdd_start_routing_by_zone.times_called == 1


@pytest.mark.config(
    CARGO_SDD_ROUTING_RUNNER_SETTINGS={
        'enabled': True,
        'launches_pause_sec': 0,
    },
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
                ],
                'couriers': [{'park_id': 'park1', 'driver_id': 'driver1'}],
                'taxi_classes': [],
                'fake_depot': {'lon': 0, 'lat': 0},
            },
        ],
    },
)
@pytest.mark.now('2021-10-30T12:45:00+00:00')
async def test_delivery_interval2(run_routing_runner, mockserver, pgsql, stq):
    cursor = pgsql['cargo_sdd'].cursor()
    cursor.execute(
        """
        INSERT INTO cargo_sdd.segments(
            segment_id, revision, corp_client_id,
            status, waybill_building_version, zone_id, created_ts,
            delivery_interval_from, delivery_interval_to
        )
        VALUES (
            'seg1', 1, 'corp_id',
            'waybill_building_awaited', 1, 'moscow',
            '2021-10-30T11:30:00+00:00'::TIMESTAMPTZ,
            '2021-10-30T11:45:00+00:00'::TIMESTAMPTZ,
            '2021-10-30T13:45:00+00:00'::TIMESTAMPTZ
        )
        """,
    )
    result = await run_routing_runner()
    assert result['segments-processed-count'] == 1
    assert stq.cargo_sdd_start_routing_by_zone.times_called == 1
    stq_call = stq.cargo_sdd_start_routing_by_zone.next_call()
    assert stq_call['id'] == 'moscow_2021_10_30_2021-10-30T12:00:00Z'
    assert stq_call['kwargs']['zone_id'] == 'moscow'
    assert stq_call['kwargs']['threshold'] == '2021-10-30T12:00:00+00:00'
    assert 'corp_client_ids' not in stq_call['kwargs']


@pytest.mark.config(
    CARGO_SDD_ROUTING_RUNNER_SETTINGS={
        'enabled': True,
        'launches_pause_sec': 0,
    },
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
                ],
                'couriers': [{'park_id': 'park1', 'driver_id': 'driver1'}],
                'taxi_classes': [],
                'fake_depot': {'lon': 0, 'lat': 0},
            },
            {
                'corp_client_ids': ['111', '333'],
                'delivery_guarantees': [],
                'couriers': [{'park_id': 'park2', 'driver_id': 'driver2'}],
                'taxi_classes': [],
                'fake_depot': {'lon': 0, 'lat': 0},
            },
        ],
    },
)
@pytest.mark.now('2021-10-30T12:45:00+00:00')
async def test_empty_corp_intervals(
        run_routing_runner, mockserver, pgsql, stq,
):
    cursor = pgsql['cargo_sdd'].cursor()
    cursor.execute(
        """
        INSERT INTO cargo_sdd.segments(
            segment_id, revision, corp_client_id,
            status, waybill_building_version, zone_id, created_ts
        )
        VALUES (
            'seg1', 1, '111',
            'waybill_building_awaited', 1, 'moscow',
            '2021-10-30T11:30:00+00:00'::TIMESTAMPTZ
        ),
        (
            'seg2', 1, '222',
            'waybill_building_awaited', 1, 'moscow',
            '2021-10-30T08:55:00+00:00'::TIMESTAMPTZ
        ),
        (
            'seg3', 1, '333',
            'waybill_building_awaited', 1, 'moscow',
            '2021-10-30T11:35:00+00:00'::TIMESTAMPTZ
        )

        """,
    )
    result = await run_routing_runner()
    assert result['segments-processed-count'] == 1
    assert stq.cargo_sdd_start_routing_by_zone.times_called == 1

    # Only default interval
    stq_call = stq.cargo_sdd_start_routing_by_zone.next_call()
    assert stq_call['id'] == 'moscow_2021_10_30_2021-10-30T12:00:00Z'
    assert stq_call['kwargs']['ignore_corp_ids'] == ['111', '333']


@pytest.mark.now('2021-10-30T12:45:00+00:00')
@pytest.mark.config(
    CARGO_SDD_ROUTING_RUNNER_SETTINGS={
        'enabled': True,
        'launches_pause_sec': 0,
    },
    CARGO_SDD_USE_NEW_ZONE_CONFIG=True,
)
async def test_update_clause_reason(
        run_routing_runner, pgsql, experiments3, stq,
):
    experiments3.add_config(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='cargo_sdd_delivery_settings_for_clients',
        consumers=['cargo-sdd/routing-runner'],
        clauses=[
            {
                'title': 'clause',
                'alias': 'clause_alias',
                'predicate': {
                    'init': {
                        'predicates': [
                            {
                                'init': {
                                    'arg_name': 'zone_name',
                                    'arg_type': 'string',
                                    'value': 'moscow',
                                },
                                'type': 'eq',
                            },
                        ],
                    },
                    'type': 'all_of',
                },
                'value': {
                    'settings': {
                        'delivery_guarantees': [
                            {
                                'orders_created_till': (
                                    '1970-01-01T12:00:00+00:00'
                                ),
                                'start_routing_at': (
                                    '1970-01-01T12:00:00+00:00'
                                ),
                                'pickup_till': '1970-01-01T13:00:00+00:00',
                                'deliver_till': '1970-01-01T16:00:00+00:00',
                                'waybill_building_deadline': (
                                    '1970-01-01T13:00:00+00:00'
                                ),
                            },
                        ],
                        'couriers': [],
                        'copy_fake_courier': {
                            'count': 1,
                            'courier_pattern': {
                                'park_id': 'park1',
                                'driver_id': 'driver1',
                            },
                        },
                        'taxi_classes': [],
                        'fake_depot': {'lon': 0, 'lat': 0},
                    },
                },
            },
        ],
        default_value={
            'settings': {
                'delivery_guarantees': [],
                'couriers': [{'park_id': 'park1', 'driver_id': 'driver1'}],
                'taxi_classes': [],
                'fake_depot': {'lon': 0, 'lat': 0},
            },
        },
    )

    cursor = pgsql['cargo_sdd'].cursor()
    cursor.execute(
        """
        INSERT INTO cargo_sdd.segments(
            segment_id, revision, corp_client_id,
            status, waybill_building_version, zone_id,
            start_point, created_ts
        )
        VALUES (
            'seg1', 1, 'corp_id',
            'waybill_building_awaited', 1, 'moscow',
            '(37.632745,55.774532)',
            '2021-10-30T11:30:00+00:00'::TIMESTAMPTZ
        ),
        (
            'seg2', 1, 'corp_id',
            'waybill_building_awaited', 1, 'moscow',
            '(37.632745,55.774532)',
            '2021-10-30T08:55:00+00:00'::TIMESTAMPTZ
        );
        """,
    )
    result = await run_routing_runner()
    assert result['segments-processed-count'] == 2
    assert stq.cargo_sdd_start_routing_by_zone.times_called == 1

    segments = await get_sdd_segments_with_exp_title(pgsql)
    assert sorted(segments, key=lambda x: x[0]) == [
        ('seg1', 2, 'waybill_building_awaited', 'clause_alias'),
        ('seg2', 2, 'waybill_building_awaited', 'clause_alias'),
    ]
    assert stq.cargo_sdd_start_routing_by_zone.times_called == 1
    stq_call = stq.cargo_sdd_start_routing_by_zone.next_call()
    assert stq_call['id'] == 'clause_alias_2021_10_30_2021-10-30T12:00:00Z'
    assert stq_call['kwargs']['clause_alias'] == 'clause_alias'
    assert stq_call['kwargs']['exp3_kwargs'] == {
        'start_point': {'lat': 55.774532, 'lon': 37.632745},
        'zone_name': 'moscow',
        'corp_client_id': 'corp_id',
    }
