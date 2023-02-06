# pylint: disable=C0302
import datetime as dt

import pytest

from testsuite.utils import matching


# cargo_route_watch.cpp:kRetryDelay
RETRY_DELAY_MILLISECONDS = 3000
RESCHEDULE_TEST_START_TIMESTAMP = dt.datetime(2020, 6, 30, 10, 10, 0)


def get_waybill_points(waybill_info):
    segments = {}
    for segment in waybill_info['execution']['segments']:
        segments[segment['id']] = {
            'claim_id': segment['claim_id'],
            'corp_client_id': segment['corp_client_id'],
        }
    points = []

    for point in waybill_info['execution']['points']:
        new_point = {
            'id': point['claim_point_id'],
            'address': {'coordinates': point['address']['coordinates']},
            'visit_order': point['visit_order'],
            'visit_status': point['visit_status'],
            'type': point['type'],
            'claim_id': segments[point['segment_id']]['claim_id'],
            'corp_client_id': segments[point['segment_id']]['corp_client_id'],
        }
        if 'external_order_id' in point:
            new_point['external_order_id'] = point['external_order_id']
        points.append(new_point)

    return points


@pytest.fixture(name='exp_cargo_waiting_times_by_point', autouse=True)
async def _exp_cargo_waiting_times_by_point(experiments3, taxi_cargo_dispatch):
    experiments3.add_config(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='cargo_waiting_times_by_point',
        consumers=['cargo-dispatch/cargo-route-watch'],
        clauses=[],
        default_value={
            'enabled': True,
            'source': 3,
            'destination': 3,
            'return': 3,
        },
    )
    await taxi_cargo_dispatch.invalidate_caches()


@pytest.mark.config(CARGO_ENABLE_ROUTE_WATCH={'reasons': ['next_point']})
async def test_start_watch(
        mockserver,
        stq_runner,
        happy_path_state_performer_found,
        read_waybill_info,
):
    @mockserver.json_handler('/driver-route-watcher/cargo/start-watch')
    def _mock_cargo_start_watch(request):
        assert request.json == {
            'courier': 'park_id_1_driver_id_1',
            'path': [
                {
                    'order_id': 'seg3',
                    'point': [37.5, 55.7],
                    'point_id': 'seg3_A1_p1',
                    'wait_time': 180,
                },
                {
                    'order_id': 'seg3',
                    'point': [37.5, 55.7],
                    'point_id': 'seg3_B1_p2',
                    'wait_time': 180,
                },
            ],
            'transport_type': 'car',
            'nearest_zone': 'moscow',
        }
        return {
            'courier': request.json['courier'],
            'position': [37.0, 55.0],
            'etas': [],
        }

    await stq_runner.cargo_route_watch.call(
        task_id='123',
        kwargs={
            'reason': 'next_point',
            'waybill_ref': 'waybill_fb_3',
            'waybill_revision': 1,
        },
    )

    assert _mock_cargo_start_watch.times_called == 1


@pytest.mark.config(CARGO_ENABLE_ROUTE_WATCH={'reasons': ['next_point']})
@pytest.mark.parametrize(
    'eats_fetch_waybill_enabled',
    [
        pytest.param(
            True,
            marks=[
                pytest.mark.config(
                    CARGO_DISPATCH_EATS_LOGISTICS_PERFORMER_PAYOUTS_FETCH_WAYBILL_ENABLED=True,  # noqa: E501
                ),
            ],
        ),
        pytest.param(
            False,
            marks=[
                pytest.mark.config(
                    CARGO_DISPATCH_EATS_LOGISTICS_PERFORMER_PAYOUTS_FETCH_WAYBILL_ENABLED=False,  # noqa: E501
                ),
            ],
        ),
    ],
)
async def test_all_points_resolved(
        eats_fetch_waybill_enabled,
        mockserver,
        stq_runner,
        happy_path_cancelled_by_user,
        stq,
):
    stq.eats_logistics_performer_payouts_fetch_waybill.flush()

    @mockserver.json_handler('/driver-route-watcher/cargo/stop-watch')
    def _mock_cargo_stop_watch(request):
        assert request.json == {
            'courier': 'park_id_1_driver_id_1',
            'orders': ['seg3'],
        }
        return {}

    await stq_runner.cargo_route_watch.call(
        task_id='123',
        kwargs={
            'reason': 'next_point',
            'waybill_ref': 'waybill_fb_3',
            'waybill_revision': 1,
        },
    )

    if not eats_fetch_waybill_enabled:
        assert not stq.eats_logistics_performer_payouts_fetch_waybill.has_calls
    else:
        assert stq.eats_logistics_performer_payouts_fetch_waybill.has_calls
        assert (
            stq.eats_logistics_performer_payouts_fetch_waybill.next_call()[
                'kwargs'
            ]['waybill_execution']
            == {
                'cargo_order_ids': [matching.AnyString()],
                'points': [
                    {
                        'changelog': [
                            {
                                'cargo_order_id': matching.AnyString(),
                                'status': 'pending',
                                'timestamp': matching.AnyString(),
                            },
                            {
                                'driver_id': 'driver_id1',
                                'status': 'arrived',
                                'timestamp': matching.AnyString(),
                            },
                            {
                                'status': 'skipped',
                                'timestamp': matching.AnyString(),
                            },
                        ],
                        'id': 'seg3_A1_p1',
                        'segment_id': 'seg3',
                        'location': {
                            'coordinates': [37.5, 55.7],
                            'id': 'seg3_A1',
                        },
                        'type': 'pickup',
                        'visit_order': 1,
                        'external_order_id': '1234-5678-seg3_A1',
                    },
                    {
                        'changelog': [
                            {
                                'cargo_order_id': matching.AnyString(),
                                'status': 'pending',
                                'timestamp': matching.AnyString(),
                            },
                            {
                                'driver_id': 'driver_id1',
                                'status': 'arrived',
                                'timestamp': matching.AnyString(),
                            },
                            {
                                'status': 'skipped',
                                'timestamp': matching.AnyString(),
                            },
                        ],
                        'id': 'seg3_B1_p2',
                        'segment_id': 'seg3',
                        'location': {
                            'coordinates': [37.5, 55.7],
                            'id': 'seg3_B1',
                        },
                        'type': 'destination',
                        'visit_order': 2,
                    },
                    {
                        'changelog': [
                            {
                                'cargo_order_id': matching.AnyString(),
                                'status': 'pending',
                                'timestamp': matching.AnyString(),
                            },
                            {
                                'driver_id': 'driver_id1',
                                'status': 'arrived',
                                'timestamp': matching.AnyString(),
                            },
                            {
                                'status': 'skipped',
                                'timestamp': matching.AnyString(),
                            },
                        ],
                        'id': 'seg3_A1_p3',
                        'segment_id': 'seg3',
                        'location': {
                            'coordinates': [37.5, 55.7],
                            'id': 'seg3_A1',
                        },
                        'type': 'return',
                        'visit_order': 3,
                        'external_order_id': '1234-5678-seg3_A1',
                    },
                ],
                'waybill_ref': 'waybill_fb_3',
            }
        )


@pytest.mark.config(CARGO_ENABLE_ROUTE_WATCH={'reasons': ['next_point']})
async def test_stop_watch_different_performer(
        mockserver, stq_runner, happy_path_state_performer_found,
):
    @mockserver.json_handler('/driver-route-watcher/cargo/stop-watch')
    def _mock_cargo_stop_watch(request):
        assert request.json == {
            'courier': 'park_id_1_driver_id_2',
            'orders': ['seg3'],
        }
        return {}

    @mockserver.json_handler('/driver-route-watcher/cargo/start-watch')
    def _mock_cargo_start_watch(request):
        assert request.json['courier'] == 'park_id_1_driver_id_1'
        return {
            'courier': request.json['courier'],
            'position': [37.0, 55.0],
            'etas': [],
        }

    await stq_runner.cargo_route_watch.call(
        task_id='123',
        kwargs={
            'reason': 'next_point',
            'waybill_ref': 'waybill_fb_3',
            'waybill_revision': 1,
            'previous_performer_id': 'park_id_1_driver_id_2',
        },
    )

    assert _mock_cargo_stop_watch.times_called == 1


@pytest.mark.config(CARGO_ENABLE_ROUTE_WATCH={'reasons': ['order_cancel']})
async def test_fail_without_performer(
        mockserver,
        stq_runner,
        happy_path_state_orders_created,
        happy_path_claims_segment_db,
        run_claims_segment_replication,
):
    waybill_id = 'waybill_fb_3'

    # Resolve order withour performer
    happy_path_claims_segment_db.cancel_segment_by_user('seg3')
    await run_claims_segment_replication()

    @mockserver.json_handler('/driver-route-watcher/cargo/stop-watch')
    def cargo_stop_watch(request):
        return {}

    @mockserver.json_handler('/cargo-orders/v1/performers/bulk-info')
    async def _handler(request):
        return {'performers': []}

    await stq_runner.cargo_route_watch.call(
        task_id='123',
        kwargs={
            'reason': 'order_cancel',
            'waybill_ref': waybill_id,
            'waybill_revision': 1,
        },
    )
    assert cargo_stop_watch.times_called == 0


@pytest.mark.config(CARGO_ENABLE_ROUTE_WATCH={'reasons': ['order_cancel']})
async def test_fail_with_performer(
        mockserver,
        stq_runner,
        happy_path_state_performer_found,
        happy_path_claims_segment_db,
        run_claims_segment_replication,
):
    waybill_id = 'waybill_fb_3'

    # Resolve order with performer
    happy_path_claims_segment_db.cancel_segment_by_user('seg3')
    await run_claims_segment_replication()

    @mockserver.json_handler('/driver-route-watcher/cargo/stop-watch')
    def cargo_stop_watch(request):
        assert request.json['orders'] == ['seg3']
        return {}

    await stq_runner.cargo_route_watch.call(
        task_id='123',
        kwargs={
            'reason': 'order_cancel',
            'waybill_ref': waybill_id,
            'waybill_revision': 1,
        },
    )
    assert cargo_stop_watch.times_called == 1


async def test_chain_order(mockserver, stq_runner, happy_path_chain_order):
    first_waybill = 'waybill_fb_3'
    second_waybill = 'waybill_smart_1'

    @mockserver.json_handler('/driver-route-watcher/cargo/stop-watch')
    def cargo_stop_watch(request):
        assert request.json == {
            'courier': 'park_id_1_driver_id_2',
            'orders': ['seg3'],
        }
        return {}

    @mockserver.json_handler('/driver-route-watcher/cargo/start-watch')
    def cargo_start_watch(request):
        assert request.json['courier'] == 'park_id_1_driver_id_1'
        return {
            'courier': request.json['courier'],
            'position': [37.0, 55.0],
            'etas': [],
        }

    # First waybill performer found
    await stq_runner.cargo_route_watch.call(
        task_id='123',
        kwargs={
            'reason': 'performer_found',
            'waybill_ref': first_waybill,
            'waybill_revision': 1,
        },
    )

    # Second waybill performer found
    await stq_runner.cargo_route_watch.call(
        task_id='123',
        kwargs={
            'reason': 'performer_found',
            'waybill_ref': second_waybill,
            'waybill_revision': 1,
        },
    )

    assert cargo_stop_watch.times_called == 0

    assert cargo_start_watch.times_called == 2

    driver_route_watch_request = {
        'courier': 'park_id_1_driver_id_1',
        'path': [
            # Chain parent points
            {
                'order_id': 'seg3',
                'point': [37.5, 55.7],
                'point_id': 'seg3_A1_p1',
                'wait_time': 180,
            },
            {
                'order_id': 'seg3',
                'point': [37.5, 55.7],
                'point_id': 'seg3_B1_p2',
                'wait_time': 180,
            },
            # Chain child points
            {
                'order_id': 'seg1',
                'point': [37.5, 55.7],
                'point_id': 'seg1_A1_p1',
                'wait_time': 180,
            },
            {
                'order_id': 'seg1',
                'point': [37.5, 55.7],
                'point_id': 'seg1_A2_p2',
                'wait_time': 180,
            },
            {
                'order_id': 'seg2',
                'point': [37.5, 55.7],
                'point_id': 'seg2_A1_p1',
                'wait_time': 180,
            },
            {
                'order_id': 'seg1',
                'point': [37.5, 55.7],
                'point_id': 'seg1_B1_p3',
                'wait_time': 180,
            },
            {
                'order_id': 'seg1',
                'point': [37.5, 55.7],
                'point_id': 'seg1_B2_p4',
                'wait_time': 180,
            },
            {
                'order_id': 'seg1',
                'point': [37.5, 55.7],
                'point_id': 'seg1_B3_p5',
                'wait_time': 180,
            },
            {
                'order_id': 'seg2',
                'point': [37.5, 55.7],
                'point_id': 'seg2_B1_p2',
                'wait_time': 180,
            },
        ],
        'transport_type': 'car',
        'nearest_zone': 'moscow',
    }

    # result path should be equal requesting it by child or parent order ids
    # DRW should have full path of courier

    # Chain parent order
    assert (
        cargo_start_watch.next_call()['request'].json
        == driver_route_watch_request
    )

    # Chain child order
    assert (
        cargo_start_watch.next_call()['request'].json
        == driver_route_watch_request
    )


@pytest.mark.parametrize(
    'performer_transport_type, router_type',
    [
        ('car', 'car'),
        ('pedestrian', 'masstransit'),
        ('courier_moto', 'car'),
        ('courier_car', 'car'),
    ],
)
@pytest.mark.config(CARGO_ENABLE_ROUTE_WATCH={'reasons': ['next_point']})
async def test_router_type(
        mockserver,
        stq_runner,
        happy_path_state_performer_found,
        read_waybill_info,
        mock_cargo_orders_performer_info,
        performer_transport_type,
        router_type,
):
    mock_cargo_orders_performer_info.transport_type = performer_transport_type

    @mockserver.json_handler('/driver-route-watcher/cargo/start-watch')
    def _mock_cargo_start_watch(request):
        assert request.json == {
            'courier': 'park_id_1_driver_id_1',
            'path': [
                {
                    'order_id': 'seg3',
                    'point': [37.5, 55.7],
                    'point_id': 'seg3_A1_p1',
                    'wait_time': 180,
                },
                {
                    'order_id': 'seg3',
                    'point': [37.5, 55.7],
                    'point_id': 'seg3_B1_p2',
                    'wait_time': 180,
                },
            ],
            'transport_type': router_type,
            'nearest_zone': 'moscow',
        }
        return {
            'courier': request.json['courier'],
            'position': [37.0, 55.0],
            'etas': [],
        }

    await stq_runner.cargo_route_watch.call(
        task_id='123',
        kwargs={
            'reason': 'next_point',
            'waybill_ref': 'waybill_fb_3',
            'waybill_revision': 1,
        },
    )
    assert _mock_cargo_start_watch.times_called == 1


@pytest.mark.config(CARGO_ENABLE_ROUTE_WATCH={'reasons': ['next_point']})
@pytest.mark.now(RESCHEDULE_TEST_START_TIMESTAMP.isoformat())
async def test_reschedule(
        mockserver,
        stq_runner,
        happy_path_state_performer_found,
        read_waybill_info,
        stq,
):
    @mockserver.json_handler('/driver-route-watcher/cargo/start-watch')
    def _mock_cargo_start_watch(request):
        assert request.json == {
            'courier': 'park_id_1_driver_id_1',
            'path': [
                {
                    'order_id': 'seg3',
                    'point': [37.5, 55.7],
                    'point_id': 'seg3_A1_p1',
                    'wait_time': 180,
                },
                {
                    'order_id': 'seg3',
                    'point': [37.5, 55.7],
                    'point_id': 'seg3_B1_p2',
                    'wait_time': 180,
                },
            ],
            'transport_type': 'car',
            'nearest_zone': 'moscow',
        }
        return {
            'courier': request.json['courier'],
            'position': [37.0, 55.0],
            'etas': [],
        }

    await stq_runner.cargo_route_watch.call(
        task_id='123',
        kwargs={
            'reason': 'next_point',
            'waybill_ref': 'waybill_fb_3',
            'waybill_revision': 1000,
        },
    )

    assert not _mock_cargo_start_watch.times_called

    assert stq.cargo_route_watch.times_called == 1

    expected_eta = RESCHEDULE_TEST_START_TIMESTAMP + dt.timedelta(
        milliseconds=RETRY_DELAY_MILLISECONDS,
    )
    next_call = stq.cargo_route_watch.next_call()
    assert next_call['eta'] == expected_eta


@pytest.mark.config(CARGO_ENABLE_ROUTE_WATCH={'reasons': ['next_point']})
async def test_resolved(
        mockserver,
        stq_runner,
        read_waybill_info,
        stq,
        taxi_cargo_dispatch,
        default_order_fail_request,
        state_cancelled_resolved,
):
    waybill_id = 'waybill_fb_3'

    response = await taxi_cargo_dispatch.post(
        '/v1/waybill/mark/order-fail',
        json=default_order_fail_request(waybill_id, fail_reason='failed'),
    )
    waybill = await read_waybill_info(waybill_id, True)

    @mockserver.json_handler('/driver-route-watcher/cargo/stop-watch')
    def _mock_cargo_stop_watch(request):
        assert request.json == {
            'courier': 'park_id_1_driver_id_1',
            'orders': ['seg3'],
        }
        return {}

    assert response.status_code == 200
    assert waybill['dispatch']['status'] == 'resolved'

    stq.cargo_route_watch.flush()
    stq.busy_drivers_logistics_events.flush()

    await stq_runner.cargo_route_watch.call(
        task_id='123',
        kwargs={
            'reason': 'next_point',
            'waybill_ref': waybill_id,
            'waybill_revision': 1,
        },
    )

    assert not stq.cargo_route_watch.has_calls
    assert stq.busy_drivers_logistics_events.has_calls


@pytest.mark.config(CARGO_ENABLE_ROUTE_WATCH={'reasons': []})
async def test_busy_drivers_notify(
        stq, stq_runner, happy_path_state_performer_found, read_waybill_info,
):
    await stq_runner.cargo_route_watch.call(
        task_id='123',
        kwargs={
            'reason': 'next_point',
            'waybill_ref': 'waybill_fb_3',
            'waybill_revision': 1,
        },
    )

    waybill = await read_waybill_info('waybill_fb_3')

    assert stq.busy_drivers_logistics_events.times_called == 1
    args = stq.busy_drivers_logistics_events.next_call()['kwargs']
    assert args['event'] == 'change'
    assert (
        args['cargo_ref_id']
        == 'order/' + waybill['execution']['cargo_order_info']['order_id']
    )
    assert args['updated_ts'] == waybill['dispatch']['updated_ts']
    assert args['destinations'] == [
        {'position': [37.5, 55.7], 'status': 'pending'},
        {'position': [37.5, 55.7], 'status': 'pending'},
    ]


@pytest.mark.config(CARGO_ENABLE_ROUTE_WATCH={'reasons': []})
async def test_busy_drivers_waybill_resolved(
        stq, stq_runner, happy_path_cancelled_by_user,
):
    await stq_runner.cargo_route_watch.call(
        task_id='123',
        kwargs={
            'reason': 'next_point',
            'waybill_ref': 'waybill_fb_3',
            'waybill_revision': 1,
        },
    )

    assert stq.busy_drivers_logistics_events.times_called == 1


@pytest.mark.config(CARGO_ENABLE_ROUTE_WATCH={'reasons': []})
async def test_busy_drivers_different_performer(
        stq, stq_runner, happy_path_state_performer_found,
):
    await stq_runner.cargo_route_watch.call(
        task_id='123',
        kwargs={
            'reason': 'next_point',
            'waybill_ref': 'waybill_fb_3',
            'waybill_revision': 1,
            'previous_performer_id': 'park_id_1_driver_id_2',
        },
    )

    assert stq.busy_drivers_logistics_events.times_called == 0


@pytest.mark.config(CARGO_ENABLE_ROUTE_WATCH={'reasons': []})
async def test_busy_drivers_chain_path(
        stq, stq_runner, happy_path_chain_order, read_waybill_info,
):
    first_waybill = 'waybill_fb_3'
    second_waybill = 'waybill_smart_1'

    # First waybill performer found
    await stq_runner.cargo_route_watch.call(
        task_id='123',
        kwargs={
            'reason': 'performer_found',
            'waybill_ref': first_waybill,
            'waybill_revision': 1,
        },
    )

    # Second waybill performer found
    await stq_runner.cargo_route_watch.call(
        task_id='123',
        kwargs={
            'reason': 'performer_found',
            'waybill_ref': second_waybill,
            'waybill_revision': 1,
        },
    )

    assert stq.busy_drivers_logistics_events.times_called == 2

    # Chain parent order
    waybill = await read_waybill_info(first_waybill)
    args = stq.busy_drivers_logistics_events.next_call()['kwargs']
    assert (
        args['cargo_ref_id']
        == 'order/' + waybill['execution']['cargo_order_info']['order_id']
    )
    assert args['destinations'] == [
        {'position': [37.5, 55.7], 'status': 'pending'},
        {'position': [37.5, 55.7], 'status': 'pending'},
    ]

    # Chain child order
    waybill = await read_waybill_info(second_waybill)
    args = stq.busy_drivers_logistics_events.next_call()['kwargs']
    assert (
        args['cargo_ref_id']
        == 'order/' + waybill['execution']['cargo_order_info']['order_id']
    )
    assert args['destinations'] == [
        {'position': [37.5, 55.7], 'status': 'pending'},
        {'position': [37.5, 55.7], 'status': 'pending'},
        {'position': [37.5, 55.7], 'status': 'pending'},
        {'position': [37.5, 55.7], 'status': 'pending'},
        {'position': [37.5, 55.7], 'status': 'pending'},
        {'position': [37.5, 55.7], 'status': 'pending'},
        {'position': [37.5, 55.7], 'status': 'pending'},
    ]


@pytest.mark.config(
    CARGO_CLAIMS_EMPLOYER_NAME_MAPPING={
        'corp_client_id_56789012345678912': 'eats',
    },
)
@pytest.mark.config(CARGO_ENABLE_ROUTE_WATCH={'reasons': []})
@pytest.mark.config(
    CARGO_DISPATCH_EATS_ORDERS_TRACKING_CARGO_WAYBILL_CHANGES_ENABLED=True,
)
async def test_eats_orders_tracking_cargo_waybill_changes_stq(
        stq, stq_runner, happy_path_state_performer_found, read_waybill_info,
):
    stq.cargo_route_watch.flush()
    stq.eats_orders_tracking_cargo_waybill_changes.flush()

    waybill_ref = 'waybill_fb_3'
    await stq_runner.cargo_route_watch.call(
        task_id='123',
        kwargs={
            'reason': 'next_point',
            'waybill_ref': waybill_ref,
            'waybill_revision': 1,
        },
    )

    points = get_waybill_points(await read_waybill_info(waybill_ref))

    args = stq.eats_orders_tracking_cargo_waybill_changes.next_call()['kwargs']
    assert args == {
        'log_extra': {'_link': matching.AnyString()},
        'points': points,
        'waybill_ref': waybill_ref,
        'waybill_revision': 5,
        'is_actual_waybill': True,
        'waybill_created_ts': matching.AnyString(),
        'performer_info': {
            'driver_id': 'driver_id_1',
            'park_id': 'park_id_1',
            'phone_pd_id': '+70000000000_id',
            'name': 'Kostya',
            'car_number': 'А001АА77',
            'car_model': 'KAMAZ',
            'transport_type': 'car',
        },
    }


@pytest.mark.config(
    CARGO_CLAIMS_EMPLOYER_NAME_MAPPING={
        'corp_client_id_56789012345678912': 'eats',
    },
)
@pytest.mark.config(CARGO_ENABLE_ROUTE_WATCH={'reasons': []})
@pytest.mark.config(
    CARGO_DISPATCH_EATS_ORDERS_TRACKING_CARGO_WAYBILL_CHANGES_ENABLED=True,
)
@pytest.mark.parametrize(
    'inject_failure_on',
    [
        'inject_failure_on_segment_point_type_cast',
        'inject_failure_on_visit_status_cast',
    ],
)
async def test_eats_orders_tracking_cargo_waybill_changes_stq_start_failed(
        stq,
        stq_runner,
        happy_path_state_performer_found,
        testpoint,
        inject_failure_on,
):
    stq.cargo_route_watch.flush()
    stq.eats_orders_tracking_cargo_waybill_changes.flush()

    @testpoint('cargo_waybill_changes_client_testpoint')
    def __inject_failure_on_segment_point_type_testpoint(data):
        return {inject_failure_on: True}

    waybill_ref = 'waybill_fb_3'
    await stq_runner.cargo_route_watch.call(
        task_id='123',
        kwargs={
            'reason': 'next_point',
            'waybill_ref': waybill_ref,
            'waybill_revision': 1,
        },
    )
    await __inject_failure_on_segment_point_type_testpoint.wait_call()
    assert not stq.eats_orders_tracking_cargo_waybill_changes.has_calls


@pytest.mark.config(
    CARGO_CLAIMS_EMPLOYER_NAME_MAPPING={
        'corp_client_id_56789012345678912': 'grocery',
        'corp_client_id_56789012345678913': (
            'eats'  # non grocery corp_client_id
        ),
    },
)
@pytest.mark.parametrize(
    'corp_client_id, stq_calls_count',
    (
        ('corp_client_id_56789012345678912', 1),
        ('corp_client_id_56789012345678913', 0),
        ('corp_client_id_56789012345678914', 0),
    ),
)
@pytest.mark.config(CARGO_ENABLE_ROUTE_WATCH={'reasons': []})
@pytest.mark.config(
    CARGO_DISPATCH_GROCERY_PERFORMER_WATCHER_WAYBILL_CHANGES_ENABLED=True,
)
async def test_grocery_performer_watcher_waybill_changes_stq(
        stq,
        stq_runner,
        mockserver,
        happy_path_state_performer_found,
        read_waybill_info,
        happy_path_claims_segment_db,
        corp_client_id: str,
        stq_calls_count: bool,
        waybill_ref='waybill_fb_3',
        depot_id='12345',
        segment_id='seg3',
):
    points = get_waybill_points(await read_waybill_info(waybill_ref))

    @mockserver.json_handler(
        '/stq-agent/queues/api/add/grocery_performer_watcher_waybill_changes',
    )
    def mock_stq(request):
        assert request.json['kwargs'] == {
            'log_extra': {'_link': matching.AnyString()},
            'claim_id': 'claim_uuid_1',
            'waybill_ref': waybill_ref,
            'depot_id': depot_id,
            'performer_id': 'park_id_1_driver_id_1',
            'is_pull_dispatch': False,
            'performer_info': {
                'driver_id': 'driver_id_1',
                'park_id': 'park_id_1',
                'phone_pd_id': '+70000000000_id',
                'name': 'Kostya',
                'car_number': 'А001АА77',
                'car_model': 'KAMAZ',
                'transport_type': 'car',
            },
            'points': points,
        }
        return {}

    stq.cargo_route_watch.flush()
    stq.grocery_performer_watcher_waybill_changes.flush()

    segment = happy_path_claims_segment_db.get_segment(segment_id)
    segment.json['custom_context'] = {
        'depot_id': depot_id,
        'order_id': '111a1816fc94457585d87058f2b02521-grocery',
        'dispatch_id': '7070e184-e593-4da8-898e-fb072a511a14',
        'dispatch_wave': 1,
        'weight': 1064,
        'created': '2022-04-22T15:41:48.096598+00:00',
        'region_id': 39,
        'delivery_flags': {},
    }
    segment.json['corp_client_id'] = corp_client_id

    await stq_runner.cargo_route_watch.call(
        task_id='123',
        kwargs={
            'reason': 'next_point',
            'waybill_ref': waybill_ref,
            'waybill_revision': 1,
        },
    )

    waybill_info = await read_waybill_info(waybill_ref)
    segments = {}
    for segment in waybill_info['execution']['segments']:
        segments[segment['id']] = {
            'claim_id': segment['claim_id'],
            'corp_client_id': corp_client_id,
        }

    assert mock_stq.times_called == stq_calls_count


@pytest.mark.config(
    CARGO_CLAIMS_EMPLOYER_NAME_MAPPING={
        'corp_client_id_56789012345678912': 'eats',
    },
)
@pytest.mark.config(CARGO_ENABLE_ROUTE_WATCH={'reasons': []})
@pytest.mark.config(
    CARGO_DISPATCH_EATS_ORDERS_TRACKING_CARGO_WAYBILL_CHANGES_ENABLED=True,
)
async def test_eats_chain_orders_tracking_cargo_waybill_changes_stq(
        mockserver, stq, stq_runner, happy_path_chain_order,
):
    first_waybill = 'waybill_fb_3'
    second_waybill = 'waybill_smart_1'

    @mockserver.json_handler('/driver-route-watcher/cargo/stop-watch')
    def cargo_stop_watch(request):
        assert request.json == {
            'courier': 'park_id_1_driver_id_2',
            'orders': ['seg3'],
        }
        return {}

    @mockserver.json_handler('/driver-route-watcher/cargo/start-watch')
    def cargo_start_watch(request):
        assert request.json['courier'] == 'park_id_1_driver_id_1'
        return {
            'courier': request.json['courier'],
            'position': [37.0, 55.0],
            'etas': [],
        }

    await stq_runner.cargo_route_watch.call(
        task_id='123',
        kwargs={
            'reason': 'performer_found',
            'waybill_ref': first_waybill,
            'waybill_revision': 1,
        },
    )

    await stq_runner.cargo_route_watch.call(
        task_id='123',
        kwargs={
            'reason': 'performer_found',
            'waybill_ref': second_waybill,
            'waybill_revision': 1,
        },
    )

    stq.cargo_route_watch.flush()
    stq.eats_orders_tracking_cargo_waybill_changes.flush()

    await stq_runner.cargo_route_watch.call(
        task_id='123',
        kwargs={
            'reason': 'next_point',
            'waybill_ref': second_waybill,
            'waybill_revision': 1,
        },
    )

    args = stq.eats_orders_tracking_cargo_waybill_changes.next_call()['kwargs']
    assert args['chain_parent_waybill_ref'] == first_waybill
    assert cargo_stop_watch.times_called == 0
    assert cargo_start_watch.times_called == 0
