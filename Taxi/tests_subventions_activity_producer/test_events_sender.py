import pytest

from tests_subventions_activity_producer import common


@pytest.fixture(name='billing_orders')
def mock_billing_orders(mockserver):
    class BOContext:
        def __init__(self):
            self.events = []

        def v1_process_event(self, doc):
            self.events.append(doc)

    ctx = BOContext()

    @mockserver.json_handler('/billing-orders/v1/process_event')
    def _v1_process_event(request):
        doc = request.json
        ctx.v1_process_event(doc)
        return {'doc': {'id': 1000}}

    return ctx


@pytest.fixture(name='billing_time_events')
def mock_billing_time_events(mockserver):
    class BTEContext:
        def __init__(self):
            self.events = []
            self.times_called = 0

        def v1_push(self, doc):
            self.events.append(doc)

    ctx = BTEContext()

    @mockserver.json_handler('/billing-time-events/v1/push')
    def _v1_process_event(request):
        doc = request.json
        ctx.v1_push(doc)
        ctx.times_called += 1
        return mockserver.make_response(status=200)

    return ctx


def _get_activity_events_unsent(pgsql, cluster, schema):
    cursor = pgsql[cluster].cursor()
    cursor.execute(
        """SELECT *
         FROM {}.activity_events_unsent;""".format(
            schema,
        ),
    )
    return list(cursor)


def _get_expected_bte_events(load_json, expected_drivers):
    drivers_dict = load_json('expected_bte_events.json')
    drivers = []
    for driver in expected_drivers:
        drivers.append(drivers_dict[driver])
    return drivers


def _get_expected_bo_ids(expected_drivers):
    base_bo_ids = [
        'taxi/geoarea_activity/unique_driver_id/udid1/2020-01-01T09:00',
        'taxi/geoarea_activity/unique_driver_id/udid2/2020-01-01T09:00',
        'taxi/geoarea_activity/unique_driver_id/udid3/2020-01-01T09:00',
        'taxi/geoarea_activity/unique_driver_id/udid4/2020-01-01T09:00',
        'taxi/geoarea_activity/unique_driver_id/udid5/2020-01-01T09:00',
        'taxi/geoarea_activity/unique_driver_id/udid6/2020-01-01T09:00',
        'taxi/geoarea_activity/unique_driver_id/udid7/2020-01-01T09:00',
    ]
    expected_bo_ids = []

    for bo_id in base_bo_ids:
        is_present = False
        for expected_driver in expected_drivers:
            if expected_driver in bo_id:
                is_present = True
                break
        if not is_present:
            expected_bo_ids.append(bo_id)
    return expected_bo_ids


@pytest.mark.servicetest
@pytest.mark.pgsql(
    'subventions-activity-producer', files=['init_activity_events_unsent.sql'],
)
@common.suspend_all_periodic_tasks
async def test_events_sender(
        taxi_subventions_activity_producer,
        testpoint,
        pgsql,
        taxi_config,
        billing_orders,
):
    await common.run_events_sender_once(
        taxi_subventions_activity_producer, taxi_config,
    )

    obj_ids = [ev['external_obj_id'] for ev in billing_orders.events]

    assert sorted(obj_ids) == [
        'taxi/geoarea_activity/unique_driver_id/udid1/2020-01-01T09:00',
        'taxi/geoarea_activity/unique_driver_id/udid2/2020-01-01T09:00',
        'taxi/geoarea_activity/unique_driver_id/udid3/2020-01-01T09:00',
        'taxi/geoarea_activity/unique_driver_id/udid4/2020-01-01T09:00',
    ]

    shard0_unsent_events = _get_activity_events_unsent(
        pgsql, 'subventions-activity-producer', 'shard0',
    )
    shard1_unsent_events = _get_activity_events_unsent(
        pgsql, 'subventions-activity-producer', 'shard1',
    )
    shard2_unsent_events = _get_activity_events_unsent(
        pgsql, 'subventions-activity-producer', 'shard2',
    )

    assert shard0_unsent_events == []
    assert shard1_unsent_events == []
    assert shard2_unsent_events == []


@pytest.mark.servicetest
@pytest.mark.pgsql(
    'subventions-activity-producer',
    files=['init_activity_events_unsent_different_zones.sql'],
)
@pytest.mark.parametrize(
    'expected_bte_drivers, billing_types_to_send_to_bte,'
    ' expected_times_called',
    [
        ([], [], 0),
        (['udid1', 'udid2', 'udid3'], ['driver_fix', 'shuttle'], 3),
        (
            ['udid1', 'udid2', 'udid3', 'udid4', 'udid5'],
            ['driver_fix', 'geo_booking', 'shuttle'],
            5,
        ),
    ],
)
@common.suspend_all_periodic_tasks
async def test_send_events_to_bte(
        taxi_subventions_activity_producer,
        testpoint,
        pgsql,
        taxi_config,
        load_json,
        billing_orders,
        billing_time_events,
        expected_bte_drivers,
        billing_types_to_send_to_bte,
        expected_times_called,
):
    await taxi_subventions_activity_producer.invalidate_caches()

    await common.run_events_sender_once(
        taxi_subventions_activity_producer,
        taxi_config,
        billing_types_to_send_to_bte,
    )

    bo_obj_ids = [ev['external_obj_id'] for ev in billing_orders.events]

    assert sorted(bo_obj_ids) == _get_expected_bo_ids(expected_bte_drivers)

    assert billing_time_events.times_called == expected_times_called

    bte_events = sorted(
        billing_time_events.events,
        key=lambda x: x['driver']['unique_driver_id'],
    )
    expected_bte_events = _get_expected_bte_events(
        load_json, expected_bte_drivers,
    )

    assert bte_events == expected_bte_events

    shard0_unsent_events = _get_activity_events_unsent(
        pgsql, 'subventions-activity-producer', 'shard0',
    )
    shard1_unsent_events = _get_activity_events_unsent(
        pgsql, 'subventions-activity-producer', 'shard1',
    )
    shard2_unsent_events = _get_activity_events_unsent(
        pgsql, 'subventions-activity-producer', 'shard2',
    )

    assert shard0_unsent_events == []
    assert shard1_unsent_events == []
    assert shard2_unsent_events == []


@pytest.mark.parametrize(
    'billing_types_to_send_to_bte',
    [
        pytest.param([], id='BO'),
        pytest.param(['driver_fix', 'geo_booking', 'shuttle'], id='BTE'),
    ],
)
@pytest.mark.parametrize('response_code', (500, 429, 400))
@pytest.mark.pgsql(
    'subventions-activity-producer',
    files=['init_activity_events_unsent_shard_0.sql'],
)
async def test_bad_response(
        taxi_subventions_activity_producer,
        taxi_config,
        mockserver,
        pgsql,
        billing_types_to_send_to_bte,
        response_code,
):
    @mockserver.json_handler('/billing-orders/v1/process_event')
    def _v1_process_event(request):
        return mockserver.make_response('error', status=response_code)

    @mockserver.json_handler('/billing-time-events/v1/push')
    def _v1_push(request):
        return mockserver.make_response('error', status=response_code)

    before = _get_activity_events_unsent(
        pgsql, 'subventions-activity-producer', 'shard0',
    )

    await taxi_subventions_activity_producer.invalidate_caches()

    await common.run_events_sender_once(
        taxi_subventions_activity_producer,
        taxi_config,
        billing_types_to_send_to_bte,
    )

    after = _get_activity_events_unsent(
        pgsql, 'subventions-activity-producer', 'shard0',
    )

    assert after == before


@pytest.mark.parametrize(
    'billing_types_to_send_to_bte',
    [
        pytest.param([], id='BO'),
        pytest.param(['driver_fix', 'geo_booking', 'shuttle'], id='BTE'),
    ],
)
@pytest.mark.pgsql(
    'subventions-activity-producer',
    files=['init_activity_events_unsent_shard_0.sql'],
)
async def test_handle_400(
        taxi_subventions_activity_producer,
        taxi_config,
        mockserver,
        pgsql,
        billing_types_to_send_to_bte,
):
    @mockserver.json_handler('/billing-orders/v1/process_event')
    def _v1_process_event(request):
        return mockserver.make_response('error', status=400)

    @mockserver.json_handler('/billing-time-events/v1/push')
    def _v1_push(request):
        return mockserver.make_response(
            '{"message":"Activity `start` is too old","code":"Bad request"}',
            status=400,
        )

    await taxi_subventions_activity_producer.invalidate_caches()

    await common.run_events_sender_once(
        taxi_subventions_activity_producer,
        taxi_config,
        billing_types_to_send_to_bte,
        drop_events_on_400=True,
    )

    events_after = _get_activity_events_unsent(
        pgsql, 'subventions-activity-producer', 'shard0',
    )

    assert events_after == []
