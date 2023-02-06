import datetime

import pytest

from testsuite.utils import matching


DEFAULT_HEADERS = {
    'Accept-Language': 'en',
    'X-Remote-IP': '12.34.56.78',
    'X-YaTaxi-Driver-Profile-Id': 'driver_id1',
    'X-YaTaxi-Park-Id': 'park_id1',
    'X-Request-Application': 'taximeter',
    'X-Request-Application-Version': '9.40',
    'X-Request-Version-Type': '',
    'X-Request-Platform': 'android',
}


TIMERS_SETTINGS = {
    'eta': {
        'before_calculated': {'subtitle_key': 'before_eta_calculated'},
        'after_calculated': {'subtitle_key': 'after_eta_calculated'},
        'after_calculated_for_batches_destination_points': {
            'subtitle_key': (
                'actions.timers.'
                'after_calculated_for_batches_destination_points'
            ),
        },
        'after_passed': {'subtitle_key': 'after_eta_passed'},
        'batches': {
            'before_calculated': {
                'subtitle_key': 'before_batches_eta_calculated',
            },
            'after_calculated_single_unique_point': {
                'subtitle_key': (
                    'after_batches_eta_calculated_single_unique_point'
                ),
            },
            'after_calculated_several_unique_points': {
                'subtitle_key': (
                    'after_batches_eta_calculated_several_unique_points'
                ),
            },
            'after_passed': {'subtitle_key': 'after_batches_eta_passed'},
        },
    },
    'waiting': {
        'paid': {'subtitle_key': 'paid_wait'},
        'free': {'subtitle_key': 'free_wait'},
        'paid_end': {'subtitle_key': 'paid_wait_end'},
        'batches': {
            'paid': {'subtitle_key': 'paid_batches_wait'},
            'free': {'subtitle_key': 'free_baches_wait'},
            'paid_end': {'subtitle_key': 'paid_batches_wait_end'},
        },
    },
}

# pylint: disable=invalid-name
pytestmark = [
    pytest.mark.experiments3(
        name='cargo_orders_timers_settings',
        consumers=['cargo-orders/build-actions'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[],
        default_value={'hide_eta': False},
        is_config=True,
    ),
    pytest.mark.experiments3(
        name='cargo_orders_taximeter_timers_settings',
        consumers=['cargo-orders/build-timer-action'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[],
        default_value=TIMERS_SETTINGS,
        is_config=True,
    ),
]


def _get_free_paid_wait_time_end(point_visit_time):
    free_wait_duration = datetime.timedelta(minutes=10)
    paid_wait_duration = datetime.timedelta(minutes=20)
    arrived_ts = datetime.datetime.fromisoformat(point_visit_time)
    return (
        (arrived_ts + free_wait_duration).strftime('%Y-%m-%dT%H:%M:%S+00:00'),
        (arrived_ts + free_wait_duration + paid_wait_duration).strftime(
            '%Y-%m-%dT%H:%M:%S+00:00',
        ),
    )


@pytest.fixture(name='mock_pricing_wait_time')
async def _mock_pricing_wait_time(mockserver):
    @mockserver.json_handler('/cargo-pricing/v1/taxi/calc-waiting-times')
    def mock(request):
        assert request.json['calc_id'] == matching.any_string
        assert request.json['waypoint']['type'] in ['pickup', 'dropoff']
        assert (
            request.json['waypoint']['first_time_arrived_at']
            == matching.datetime_string
        )
        assert len(request.json['waypoint']['position']) == 2

        free_wait_end, paid_wait_end = _get_free_paid_wait_time_end(
            request.json['waypoint']['first_time_arrived_at'],
        )

        return {
            'free_waiting_start_ts': request.json['waypoint'][
                'first_time_arrived_at'
            ],
            'paid_waiting_start_ts': free_wait_end,
            'paid_waiting_finish_ts': paid_wait_end,
        }

    return mock


@pytest.fixture(name='mock_pricing_wait_time_with_infinite_free_waiting')
async def _mock_pricing_wait_time_no_paid(mockserver):
    @mockserver.json_handler('/cargo-pricing/v1/taxi/calc-waiting-times')
    def mock(request):
        return {
            'free_waiting_start_ts': request.json['waypoint'][
                'first_time_arrived_at'
            ],
        }

    return mock


@pytest.fixture(name='mock_pricing_wait_time_with_infinite_paid_waiting')
async def _mock_pricing_wait_time_infinite_paid(mockserver):
    @mockserver.json_handler('/cargo-pricing/v1/taxi/calc-waiting-times')
    def mock(request):
        free_wait_end, _ = _get_free_paid_wait_time_end(
            request.json['waypoint']['first_time_arrived_at'],
        )

        return {
            'free_waiting_start_ts': request.json['waypoint'][
                'first_time_arrived_at'
            ],
            'paid_waiting_start_ts': free_wait_end,
        }

    return mock


async def test_show_eta_before_calculation(
        taxi_cargo_orders,
        mock_waybill_info,
        get_driver_cargo_state,
        default_order_id,
        waybill_info_with_same_source_point,
        mock_driver_tags_v1_match_profile,
):
    point = waybill_info_with_same_source_point['execution']['points'][0]
    point['eta_calculation_awaited'] = True

    response = await get_driver_cargo_state(default_order_id)
    assert response.status_code == 200

    actions = response.json()['current_point']['actions']
    timer_action = next(filter(lambda x: x['type'] == 'timer', actions), None)

    assert timer_action == {
        'intervals': [
            {
                'mode': 'no_timer',
                'is_reverse': False,
                'subtitle': 'before_eta_calculated',
                'tag': 'on_route',
            },
        ],
        'type': 'timer',
    }


async def test_show_eta_after_calculation(
        taxi_cargo_orders,
        mock_waybill_info,
        get_driver_cargo_state,
        default_order_id,
        waybill_info_with_same_source_point,
        mock_driver_tags_v1_match_profile,
):
    point_eta = (
        datetime.datetime.utcnow() - datetime.timedelta(hours=2)
    ).strftime('%Y-%m-%dT%H:%M:%S+00:00')
    point = waybill_info_with_same_source_point['execution']['points'][0]
    point['eta_calculation_awaited'] = False
    point['eta'] = point_eta

    response = await get_driver_cargo_state(default_order_id)
    assert response.status_code == 200
    actions = response.json()['current_point']['actions']
    timer_action = next(filter(lambda x: x['type'] == 'timer', actions), None)

    assert timer_action == {
        'intervals': [
            {
                'mode': 'descending',
                'is_reverse': False,
                'subtitle': 'after_eta_calculated',
                'tag': 'on_route',
            },
            {
                'mode': 'ascending',
                'is_reverse': False,
                'subtitle': 'after_eta_passed',
                'tag': 'on_route_late',
                'start_at': point_eta,
            },
        ],
        'type': 'timer',
    }


async def test_wait_timer_source_point(
        taxi_cargo_orders,
        default_order_id,
        waybill_state,
        mock_dispatch_arrive_at_point,
        mock_pricing_wait_time,
        set_order_calculations_ids,
        my_waybill_info,
        mock_driver_tags_v1_match_profile,
):
    waybill_state.set_segment_status('pickup_arrived')
    my_waybill_info['execution']['points'][0]['visit_status'] = 'arrived'
    set_order_calculations_ids(
        'cargo-pricing/somemagicid', 'cargo-pricing/somemagicid',
    )
    response = await taxi_cargo_orders.post(
        '/driver/v1/cargo-claims/v1/cargo/arrive_at_point',
        headers=DEFAULT_HEADERS,
        json={
            'cargo_ref_id': 'order/' + default_order_id,
            'last_known_status': 'new',
            'idempotency_token': 'some_token',
            'point_id': 642499,
        },
    )
    assert response.status_code == 200
    actions = response.json()['new_point']['actions']
    timer_action = next(filter(lambda x: x['type'] == 'timer', actions), None)
    assert timer_action == {
        'intervals': [
            {
                'mode': 'descending',
                'is_reverse': False,
                'subtitle': 'free_wait',
                'tag': 'free_waiting',
            },
            {
                'mode': 'descending',
                'is_reverse': False,
                'subtitle': 'paid_wait',
                'tag': 'paid_waiting',
                'start_at': _get_free_paid_wait_time_end(
                    my_waybill_info['execution']['points'][0][
                        'last_status_change_ts'
                    ],
                )[0],
            },
            {
                'mode': 'no_timer',
                'is_reverse': False,
                'subtitle': 'paid_wait_end',
                'tag': 'paid_waiting_end',
                'start_at': _get_free_paid_wait_time_end(
                    my_waybill_info['execution']['points'][0][
                        'last_status_change_ts'
                    ],
                )[1],
            },
        ],
        'type': 'timer',
    }


async def test_wait_timer_destination_point(
        taxi_cargo_orders,
        default_order_id,
        waybill_state,
        mock_dispatch_arrive_at_point,
        mock_pricing_wait_time,
        set_order_calculations_ids,
        my_waybill_info,
        mock_driver_tags_v1_match_profile,
):
    waybill_state.set_segment_status('delivery_arrived')
    my_waybill_info['execution']['points'][0]['visit_status'] = 'visited'
    my_waybill_info['execution']['points'][0]['is_resolved'] = True
    my_waybill_info['execution']['points'][1]['visit_status'] = 'arrived'
    set_order_calculations_ids(
        'cargo-pricing/somemagicid', 'cargo-pricing/somemagicid',
    )
    response = await taxi_cargo_orders.post(
        '/driver/v1/cargo-claims/v1/cargo/arrive_at_point',
        headers=DEFAULT_HEADERS,
        json={
            'cargo_ref_id': 'order/' + default_order_id,
            'last_known_status': 'new',
            'idempotency_token': 'some_token',
            'point_id': 642500,
        },
    )
    assert response.status_code == 200
    actions = response.json()['new_point']['actions']
    timer_action = next(filter(lambda x: x['type'] == 'timer', actions), None)
    assert timer_action == {
        'intervals': [
            {
                'mode': 'descending',
                'is_reverse': False,
                'subtitle': 'free_wait',
                'tag': 'free_waiting',
            },
            {
                'mode': 'descending',
                'is_reverse': False,
                'subtitle': 'paid_wait',
                'tag': 'paid_waiting',
                'start_at': _get_free_paid_wait_time_end(
                    my_waybill_info['execution']['points'][1][
                        'last_status_change_ts'
                    ],
                )[0],
            },
            {
                'mode': 'no_timer',
                'is_reverse': False,
                'subtitle': 'paid_wait_end',
                'tag': 'paid_waiting_end',
                'start_at': _get_free_paid_wait_time_end(
                    my_waybill_info['execution']['points'][1][
                        'last_status_change_ts'
                    ],
                )[1],
            },
        ],
        'type': 'timer',
    }


async def test_wait_timer_without_paid_waiting(
        taxi_cargo_orders,
        default_order_id,
        waybill_state,
        mock_dispatch_arrive_at_point,
        mock_pricing_wait_time_with_infinite_free_waiting,
        set_order_calculations_ids,
        my_waybill_info,
        mock_driver_tags_v1_match_profile,
):
    waybill_state.set_segment_status('delivery_arrived')
    my_waybill_info['execution']['points'][0]['visit_status'] = 'visited'
    my_waybill_info['execution']['points'][0]['is_resolved'] = True
    my_waybill_info['execution']['points'][1]['visit_status'] = 'arrived'
    set_order_calculations_ids(
        'cargo-pricing/somemagicid', 'cargo-pricing/somemagicid',
    )
    response = await taxi_cargo_orders.post(
        '/driver/v1/cargo-claims/v1/cargo/arrive_at_point',
        headers=DEFAULT_HEADERS,
        json={
            'cargo_ref_id': 'order/' + default_order_id,
            'last_known_status': 'new',
            'idempotency_token': 'some_token',
            'point_id': 642500,
        },
    )
    assert response.status_code == 200
    actions = response.json()['new_point']['actions']
    timer_action = next(filter(lambda x: x['type'] == 'timer', actions), None)
    assert timer_action == {
        'intervals': [
            {
                'mode': 'no_timer',
                'is_reverse': False,
                'subtitle': 'free_wait',
                'tag': 'free_waiting',
            },
        ],
        'type': 'timer',
    }


async def test_wait_timer_without_paid_waiting_limit(
        taxi_cargo_orders,
        default_order_id,
        waybill_state,
        mock_dispatch_arrive_at_point,
        mock_pricing_wait_time_with_infinite_paid_waiting,
        set_order_calculations_ids,
        my_waybill_info,
        mock_driver_tags_v1_match_profile,
):
    waybill_state.set_segment_status('delivery_arrived')
    my_waybill_info['execution']['points'][0]['visit_status'] = 'visited'
    my_waybill_info['execution']['points'][0]['is_resolved'] = True
    my_waybill_info['execution']['points'][1]['visit_status'] = 'arrived'
    set_order_calculations_ids(
        'cargo-pricing/somemagicid', 'cargo-pricing/somemagicid',
    )
    response = await taxi_cargo_orders.post(
        '/driver/v1/cargo-claims/v1/cargo/arrive_at_point',
        headers=DEFAULT_HEADERS,
        json={
            'cargo_ref_id': 'order/' + default_order_id,
            'last_known_status': 'new',
            'idempotency_token': 'some_token',
            'point_id': 642500,
        },
    )
    assert response.status_code == 200
    actions = response.json()['new_point']['actions']
    timer_action = next(filter(lambda x: x['type'] == 'timer', actions), None)
    assert timer_action == {
        'intervals': [
            {
                'mode': 'descending',
                'is_reverse': False,
                'subtitle': 'free_wait',
                'tag': 'free_waiting',
            },
            {
                'mode': 'no_timer',
                'is_reverse': False,
                'subtitle': 'paid_wait',
                'tag': 'paid_waiting',
                'start_at': _get_free_paid_wait_time_end(
                    my_waybill_info['execution']['points'][1][
                        'last_status_change_ts'
                    ],
                )[0],
            },
        ],
        'type': 'timer',
    }


async def test_batches_show_eta_before_calculation(
        taxi_cargo_orders,
        mock_waybill_info,
        get_driver_cargo_state,
        default_order_id,
        my_batch_waybill_info,
        mock_driver_tags_v1_match_profile,
):
    point = my_batch_waybill_info['execution']['points'][0]
    point['visit_status'] = 'pending'
    point['is_resolved'] = False
    point['eta_calculation_awaited'] = True

    response = await get_driver_cargo_state(default_order_id)
    assert response.status_code == 200

    actions = response.json()['current_point']['actions']
    timer_action = next(filter(lambda x: x['type'] == 'timer', actions), None)

    assert timer_action == {
        'intervals': [
            {
                'mode': 'no_timer',
                'is_reverse': False,
                'subtitle': 'before_batches_eta_calculated',
                'tag': 'batches_on_route',
            },
        ],
        'type': 'timer',
    }


def set_segments_place_id(waybill: dict, segment_ids: list, place_id: int):
    for i in segment_ids:
        if 'custom_context' in waybill['execution']['segments'][i]:
            waybill['execution']['segments'][i]['custom_context'][
                'place_id'
            ] = place_id
        else:
            waybill['execution']['segments'][i]['custom_context'] = {
                'place_id': place_id,
            }


def set_current_point(waybill: dict, point_id: int):
    for i, point in enumerate(waybill['execution']['points']):
        if i < point_id:
            point['visit_status'] = 'visited'
            point['is_resolved'] = True
        else:
            point['visit_status'] = 'pending'
            point['is_resolved'] = False


def set_point_eta(waybill: dict, point_id: int, eta: str):
    point = waybill['execution']['points'][point_id]
    point['eta_calculation_awaited'] = False
    point['eta'] = eta


@pytest.mark.translations(
    cargo={
        'after_batches_eta_calculated_single_unique_point': {
            'en': 'Arrive at sender',
        },
    },
)
async def test_batches_arrive_at_same_source_points_eta(
        taxi_cargo_orders,
        mock_waybill_info,
        get_driver_cargo_state,
        default_order_id,
        my_batch_waybill_info,
        mock_driver_tags_v1_match_profile,
):
    point_eta = (
        datetime.datetime.utcnow() - datetime.timedelta(hours=2)
    ).strftime('%Y-%m-%dT%H:%M:%S+00:00')

    expected_timer_action = {
        'intervals': [
            {
                'mode': 'descending',
                'is_reverse': False,
                'subtitle': 'Arrive at sender',
                'tag': 'batches_on_route',
            },
            {
                'mode': 'ascending',
                'is_reverse': False,
                'subtitle': 'after_batches_eta_passed',
                'tag': 'batches_on_route_late',
                'start_at': point_eta,
            },
        ],
        'type': 'timer',
    }

    # Make source points same
    set_segments_place_id(my_batch_waybill_info, [0, 1], 1234)

    set_current_point(my_batch_waybill_info, 0)
    set_point_eta(my_batch_waybill_info, 0, point_eta)

    response = await get_driver_cargo_state(default_order_id)
    assert response.status_code == 200
    actions = response.json()['current_point']['actions']
    timer_action = next(filter(lambda x: x['type'] == 'timer', actions), None)

    assert timer_action == expected_timer_action

    set_current_point(my_batch_waybill_info, 1)
    set_point_eta(my_batch_waybill_info, 1, point_eta)

    response = await get_driver_cargo_state(default_order_id)
    assert response.status_code == 200
    actions = response.json()['current_point']['actions']
    timer_action = next(filter(lambda x: x['type'] == 'timer', actions), None)

    assert timer_action == expected_timer_action


@pytest.mark.translations(
    cargo={
        'after_batches_eta_calculated_several_unique_points': {
            'en': 'Arrive at sender %(0)s',
        },
    },
)
async def test_batches_arrive_at_different_source_points_eta(
        taxi_cargo_orders,
        mock_waybill_info,
        get_driver_cargo_state,
        default_order_id,
        my_triple_batch_waybill_info,
        mock_driver_tags_v1_match_profile,
):
    point_eta = (
        datetime.datetime.utcnow() - datetime.timedelta(hours=2)
    ).strftime('%Y-%m-%dT%H:%M:%S+00:00')

    # Make first 2 source points same
    set_segments_place_id(my_triple_batch_waybill_info, [0, 1], 1234)

    set_current_point(my_triple_batch_waybill_info, 0)
    set_point_eta(my_triple_batch_waybill_info, 0, point_eta)

    response = await get_driver_cargo_state(default_order_id)
    assert response.status_code == 200
    actions = response.json()['current_point']['actions']
    timer_action = next(filter(lambda x: x['type'] == 'timer', actions), None)

    assert timer_action == {
        'intervals': [
            {
                'mode': 'descending',
                'is_reverse': False,
                'subtitle': 'Arrive at sender 1',
                'tag': 'batches_on_route',
            },
            {
                'mode': 'ascending',
                'is_reverse': False,
                'subtitle': 'after_batches_eta_passed',
                'tag': 'batches_on_route_late',
                'start_at': point_eta,
            },
        ],
        'type': 'timer',
    }

    set_current_point(my_triple_batch_waybill_info, 1)
    set_point_eta(my_triple_batch_waybill_info, 1, point_eta)

    response = await get_driver_cargo_state(default_order_id)
    assert response.status_code == 200
    actions = response.json()['current_point']['actions']
    timer_action = next(filter(lambda x: x['type'] == 'timer', actions), None)

    assert len(timer_action['intervals']) == 2
    assert timer_action['intervals'][0] == {
        'mode': 'descending',
        'is_reverse': False,
        'subtitle': 'Arrive at sender 1',
        'tag': 'batches_on_route',
    }

    set_current_point(my_triple_batch_waybill_info, 2)
    set_point_eta(my_triple_batch_waybill_info, 2, point_eta)

    response = await get_driver_cargo_state(default_order_id)
    assert response.status_code == 200
    actions = response.json()['current_point']['actions']
    timer_action = next(filter(lambda x: x['type'] == 'timer', actions), None)

    assert len(timer_action['intervals']) == 2
    assert timer_action['intervals'][0] == {
        'mode': 'descending',
        'is_reverse': False,
        'subtitle': 'Arrive at sender 2',
        'tag': 'batches_on_route',
    }


@pytest.mark.translations(
    cargo={
        'free_baches_wait': {
            'en': ['Pickup %(0)s parcel', 'Pickup %(0)s parcels'],
        },
    },
)
async def test_batches_pickup_at_different_source_points_eta(
        taxi_cargo_orders,
        mock_waybill_info,
        get_driver_cargo_state,
        default_order_id,
        set_order_calculations_ids,
        mock_pricing_wait_time,
        my_triple_batch_waybill_info,
        mock_driver_tags_v1_match_profile,
):
    set_order_calculations_ids(
        'cargo-pricing/somemagicid', 'cargo-pricing/somemagicid',
    )

    # Make first 2 source points same
    set_segments_place_id(my_triple_batch_waybill_info, [0, 1], 1234)

    set_current_point(my_triple_batch_waybill_info, 0)
    my_triple_batch_waybill_info['execution']['points'][0][
        'visit_status'
    ] = 'arrived'

    response = await get_driver_cargo_state(default_order_id)
    assert response.status_code == 200
    actions = response.json()['current_point']['actions']
    timer_action = next(filter(lambda x: x['type'] == 'timer', actions), None)

    assert timer_action == {
        'intervals': [
            {
                'mode': 'descending',
                'is_reverse': False,
                'subtitle': 'Pickup 2 parcels',
                'tag': 'batches_free_waiting',
            },
            {
                'mode': 'descending',
                'is_reverse': False,
                'subtitle': 'paid_batches_wait',
                'tag': 'batches_paid_waiting',
                'start_at': _get_free_paid_wait_time_end(
                    my_triple_batch_waybill_info['execution']['points'][0][
                        'last_status_change_ts'
                    ],
                )[0],
            },
            {
                'mode': 'no_timer',
                'is_reverse': False,
                'subtitle': 'paid_batches_wait_end',
                'tag': 'batches_paid_waiting_end',
                'start_at': _get_free_paid_wait_time_end(
                    my_triple_batch_waybill_info['execution']['points'][0][
                        'last_status_change_ts'
                    ],
                )[1],
            },
        ],
        'type': 'timer',
    }

    set_current_point(my_triple_batch_waybill_info, 1)
    my_triple_batch_waybill_info['execution']['points'][1][
        'visit_status'
    ] = 'arrived'

    response = await get_driver_cargo_state(default_order_id)
    assert response.status_code == 200
    actions = response.json()['current_point']['actions']
    timer_action = next(filter(lambda x: x['type'] == 'timer', actions), None)

    assert len(timer_action['intervals']) == 3
    assert timer_action['intervals'][0] == {
        'mode': 'descending',
        'is_reverse': False,
        'subtitle': 'Pickup 1 parcel',
        'tag': 'batches_free_waiting',
    }

    set_current_point(my_triple_batch_waybill_info, 2)
    my_triple_batch_waybill_info['execution']['points'][2][
        'visit_status'
    ] = 'arrived'

    response = await get_driver_cargo_state(default_order_id)
    assert response.status_code == 200
    actions = response.json()['current_point']['actions']
    timer_action = next(filter(lambda x: x['type'] == 'timer', actions), None)

    assert len(timer_action['intervals']) == 3
    assert timer_action['intervals'][0] == {
        'mode': 'descending',
        'is_reverse': False,
        'subtitle': 'Pickup 1 parcel',
        'tag': 'batches_free_waiting',
    }
