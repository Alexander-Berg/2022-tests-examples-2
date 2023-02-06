import typing

import pytest

TAXI_DRIVING = 'driving'
TAXI_WAITING = 'waiting'
TAXI_TRANSPORTING = 'transporting'
TAXI_CANCELLED = 'cancelled'
TAXI_FAILED = 'failed'
TAXI_COMPLETE = 'complete'


def set_technical_failure(waybill_info):
    waybill_info['dispatch']['status'] = 'resolved'
    waybill_info['dispatch']['resolution'] = 'technical_fail'


# Copied from cargo-dispatch
def set_point_visit_status(point, new_status):
    point['visit_status'] = new_status

    if new_status in ('visited', 'skipped'):
        point['is_resolved'] = True
        point['is_return_required'] = new_status == 'skipped'
        point['resolution'] = {
            'is_skipped': new_status == 'skipped',
            'is_visited': new_status == 'visited',
        }


def set_arrived_at_first_point(v1_waybill_info_response):
    set_point_visit_status(
        v1_waybill_info_response['execution']['points'][0], 'arrived',
    )


def set_visited_at_first_point(v1_waybill_info_response):
    set_point_visit_status(
        v1_waybill_info_response['execution']['points'][0], 'visited',
    )


def set_every_point_resolved(v1_waybill_info_response):
    for point in v1_waybill_info_response['execution']['points']:
        set_point_visit_status(point, 'visited')


def skip_first_points_segment(v1_waybill_info_response):
    v1_waybill_info_response['execution']['points'][0][
        'is_segment_skipped'
    ] = True


@pytest.mark.parametrize(
    'status, new_status, waybill_mock_injections, expected_action_disabled',
    [
        pytest.param(
            TAXI_DRIVING, TAXI_CANCELLED, [], False, id='driving_cancelled_ok',
        ),
        pytest.param(
            TAXI_DRIVING,
            TAXI_TRANSPORTING,
            [],
            True,  # forbidden due to driver not arrived to any point yet
            id='driving_transporting_forbidden_not_arrived',
        ),
        pytest.param(
            TAXI_DRIVING,
            TAXI_TRANSPORTING,
            [set_arrived_at_first_point],
            False,
            id='driving_transporting_ok',
        ),
        pytest.param(
            TAXI_TRANSPORTING,
            TAXI_CANCELLED,
            [set_arrived_at_first_point],
            False,  # not forbidden due to already arrived at point
            id='transporting_cancelled_ok',
        ),
        pytest.param(
            TAXI_TRANSPORTING,
            TAXI_CANCELLED,
            [set_visited_at_first_point],
            True,  # forbidden due to confirmed at point
            id='transporting_cancelled_forbidden_confirmed_point',
        ),
        pytest.param(
            TAXI_TRANSPORTING,
            TAXI_FAILED,
            [set_visited_at_first_point],
            True,  # forbidden due to confirmed at point
            id='transporting_failed_forbidden_confirmed_point',
        ),
        pytest.param(
            TAXI_TRANSPORTING,
            TAXI_COMPLETE,
            [],
            True,  # forbidden due to not all points resolved yet
            id='transporting_complete_forbidden_points_not_resolved',
        ),
        pytest.param(
            TAXI_TRANSPORTING,
            TAXI_COMPLETE,
            [set_every_point_resolved],
            False,
            id='transporting_complete_ok',
        ),
    ],
)
async def test_point_execution(
        taxi_cargo_orders,
        default_order_id,
        status: str,
        new_status: str,
        waybill_mock_injections: typing.List[typing.Callable[[dict], dict]],
        expected_action_disabled: bool,
        my_waybill_info,
        segment_id='segment_id_1',
):
    for fix in waybill_mock_injections:
        fix(my_waybill_info)

    response = await taxi_cargo_orders.post(
        'v1/order/driver-changes',
        json={
            'cargo_ref_id': f'order/{default_order_id}',
            'driver_id': 'driver_id',
            'park_id': 'park_id',
            'status': status,
            'new_status': new_status,
        },
    )

    assert response.status_code == 200

    assert response.json()['action_disabled'] == expected_action_disabled


@pytest.mark.config(
    CARGO_CLAIMS_FORBID_DRIVER_CANCELLATION_WHEN_CODE_RECEIPT=True,
)
async def test_pickup_code_received(
        taxi_cargo_orders,
        mock_segments_bulk_info,
        default_order_id,
        my_waybill_info,
        segment_id='segment_id_1',
):
    # set pickup_code received for every point (3 unresolved points)
    mock_segments_bulk_info.set_pickup_code_received_at(
        '2020-06-17T22:40:00+0300',
    )

    response = await taxi_cargo_orders.post(
        'v1/order/driver-changes',
        json={
            'cargo_ref_id': f'order/{default_order_id}',
            'driver_id': 'driver_id',
            'park_id': 'park_id',
            'status': TAXI_DRIVING,
            'new_status': TAXI_CANCELLED,
        },
    )

    assert response.status_code == 200

    assert response.json()['action_disabled']
    assert response.json()['reason'] == (
        'Taxi order transition to cancelled is prohibited '
        'due to pickup code was received'
    )


async def test_order_not_found(taxi_cargo_orders):
    response = await taxi_cargo_orders.post(
        'v1/order/driver-changes',
        json={
            'cargo_ref_id': 'order/00000000-0000-0000-0000-000000000000',
            'driver_id': 'driver_id',
            'park_id': 'park_id',
            'status': TAXI_DRIVING,
            'new_status': TAXI_CANCELLED,
        },
    )

    assert response.status_code == 410


async def test_batch_order_with_cancelled_segment(
        taxi_cargo_orders, default_order_id, my_waybill_info,
):
    """
    Batch order. Segment with point A was cancelled by user
    Change taxi status to transporting.
    Only after that taximeter will show correct address for next point
    """
    skip_first_points_segment(my_waybill_info)
    response = await taxi_cargo_orders.post(
        'v1/order/driver-changes',
        json={
            'cargo_ref_id': f'order/{default_order_id}',
            'driver_id': 'driver_id',
            'park_id': 'park_id',
            'status': TAXI_DRIVING,
            'new_status': TAXI_TRANSPORTING,
        },
    )
    assert response.status_code == 200
    assert response.json() == {'action_disabled': False}


@pytest.mark.config(CARGO_ORDERS_NEW_TRANSPORTING_CHECKS_ENABLED=True)
@pytest.mark.parametrize(
    'status, new_status, waybill_mock_injections, expected_action_disabled',
    [
        pytest.param(
            TAXI_DRIVING,
            TAXI_TRANSPORTING,
            [],
            True,  # forbidden due to driver not arrived to any point yet
            id='driving_transporting_forbidden_not_arrived',
        ),
        pytest.param(
            TAXI_DRIVING,
            TAXI_TRANSPORTING,
            [set_arrived_at_first_point],
            True,
            id='driving_transporting_forbidden_not_visited',
        ),
        pytest.param(
            TAXI_WAITING,
            TAXI_TRANSPORTING,
            [set_arrived_at_first_point],
            True,
            id='waiting_transporting_forbidden_not_visited',
        ),
        pytest.param(
            TAXI_DRIVING,
            TAXI_TRANSPORTING,
            [set_visited_at_first_point],
            False,
            id='driving_transporting_ok',
        ),
        pytest.param(
            TAXI_WAITING,
            TAXI_TRANSPORTING,
            [set_visited_at_first_point],
            False,
            id='waiting_transporting_ok',
        ),
    ],
)
async def test_new_transporting_logic(
        taxi_cargo_orders,
        default_order_id,
        status: str,
        new_status: str,
        waybill_mock_injections: typing.List[typing.Callable[[dict], dict]],
        expected_action_disabled: bool,
        my_waybill_info,
        segment_id='segment_id_1',
):
    for fix in waybill_mock_injections:
        fix(my_waybill_info)

    response = await taxi_cargo_orders.post(
        'v1/order/driver-changes',
        json={
            'cargo_ref_id': f'order/{default_order_id}',
            'driver_id': 'driver_id',
            'park_id': 'park_id',
            'status': status,
            'new_status': new_status,
        },
    )

    assert response.status_code == 200
    assert response.json()['action_disabled'] == expected_action_disabled
    if expected_action_disabled:
        assert (
            response.json()['reason']
            == 'Taxi order transition to transporting is '
            'prohibited due to no visited cargo order point yet'
        )


@pytest.mark.config(CARGO_ORDERS_NEW_WAITING_CHECKS_ENABLED=True)
@pytest.mark.parametrize(
    'status, new_status, waybill_mock_injections, expected_action_disabled',
    [
        pytest.param(
            TAXI_DRIVING,
            TAXI_WAITING,
            [],
            True,  # forbidden due to driver not arrived to any point yet
            id='driving_waiting_forbidden_not_arrived',
        ),
        pytest.param(
            TAXI_DRIVING,
            TAXI_WAITING,
            [set_arrived_at_first_point],
            False,
            id='driving_waiting_ok',
        ),
    ],
)
async def test_new_waiting_logic(
        taxi_cargo_orders,
        default_order_id,
        status: str,
        new_status: str,
        waybill_mock_injections: typing.List[typing.Callable[[dict], dict]],
        expected_action_disabled: bool,
        my_waybill_info,
        segment_id='segment_id_1',
):
    for fix in waybill_mock_injections:
        fix(my_waybill_info)

    response = await taxi_cargo_orders.post(
        'v1/order/driver-changes',
        json={
            'cargo_ref_id': f'order/{default_order_id}',
            'driver_id': 'driver_id',
            'park_id': 'park_id',
            'status': status,
            'new_status': new_status,
        },
    )

    assert response.status_code == 200
    assert response.json()['action_disabled'] == expected_action_disabled
    if expected_action_disabled:
        assert (
            response.json()['reason']
            == 'Taxi order transition to waiting is prohibited due '
            'to point A was not arrived'
        )


@pytest.mark.parametrize(
    ('waybill_injections', 'expected'),
    [
        ([], {'action_disabled': False}),
        (
            [set_visited_at_first_point],
            {
                'action_disabled': True,
                'reason': (
                    'Taxi order transition to failed is prohibited due '
                    'to already confirmed at cargo point'
                ),
            },
        ),
        (
            [set_visited_at_first_point, set_technical_failure],
            {'action_disabled': False},
        ),
    ],
)
async def test_tech_failure_failed_transition(
        taxi_cargo_orders,
        mock_segments_bulk_info,
        default_order_id,
        my_waybill_info,
        waybill_injections,
        expected,
):
    for fix in waybill_injections:
        fix(my_waybill_info)

    response = await taxi_cargo_orders.post(
        'v1/order/driver-changes',
        json={
            'cargo_ref_id': f'order/{default_order_id}',
            'driver_id': 'driver_id',
            'park_id': 'park_id',
            'status': 'finished',
            'new_status': 'failed',
        },
    )

    assert response.status_code == 200
    assert response.json() == expected


@pytest.mark.config(
    CARGO_ORDERS_DRIVER_CHANGES_ALLOW_LIST={
        'allow_list': [
            {'new_status': TAXI_CANCELLED, 'tariff_class': 'cargo'},
        ],
    },
)
async def test_allow_list(
        taxi_cargo_orders,
        default_order_id,
        my_waybill_info,
        segment_id='segment_id_1',
):
    set_visited_at_first_point(my_waybill_info)

    response = await taxi_cargo_orders.post(
        'v1/order/driver-changes',
        json={
            'cargo_ref_id': f'order/{default_order_id}',
            'driver_id': 'driver_id',
            'park_id': 'park_id',
            'status': TAXI_TRANSPORTING,
            'new_status': TAXI_CANCELLED,
        },
    )

    assert response.status_code == 200
    assert not response.json()['action_disabled']
