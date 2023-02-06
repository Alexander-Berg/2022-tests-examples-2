import pytest

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


@pytest.fixture(name='orders_return_point')
def _orders_return_point(taxi_cargo_orders):
    async def _wrapper(order_id: str, claim_point_id: int = 1, **kwargs):
        response = await taxi_cargo_orders.post(
            '/driver/v1/cargo-claims/v1/cargo/return',
            json={
                'cargo_ref_id': 'order/' + order_id,
                'point_id': claim_point_id,
                'idempotency_token': 'some_token',
                'last_known_status': 'pickup_confirmation',
                **kwargs,
            },
            headers=DEFAULT_HEADERS,
        )
        return response

    return _wrapper


async def test_happy_path(
        taxi_cargo_orders,
        orders_return_point,
        mock_dispatch_return,
        mock_driver_tags_v1_match_profile,
        default_order_id,
        my_waybill_info,
):
    response = await orders_return_point(default_order_id)
    assert response.status_code == 200

    resp_body = response.json()
    assert resp_body['new_status'] == 'returning'
    assert resp_body['result'] == 'confirmed'
    assert resp_body['state_version'] == 'v0_1'

    assert mock_dispatch_return.handler.times_called == 1


async def test_return_request(
        orders_return_point,
        mock_dispatch_return,
        mock_driver_tags_v1_match_profile,
        default_order_id,
        my_waybill_info,
):
    mock_dispatch_return.expected_request = {
        'last_known_status': 'pickup_confirmation',
        'performer_info': {
            'driver_id': 'driver_id1',
            'park_id': 'park_id1',
            'phone_pd_id': 'phone_pd_id',
            'tariff_class': 'cargo',
            'transport_type': 'electric_bicycle',
        },
        'point_id': 1,
        'async_timer_calculation_supported': False,
        'need_create_ticket': False,
    }

    response = await orders_return_point(default_order_id)
    assert response.status_code == 200


def set_pickup_arrived(waybill):
    for segment in waybill['execution']['segments']:
        segment['status'] = 'pickup_arrived'


@pytest.mark.experiments3(filename='exp3_action_checks.json')
@pytest.mark.now('2020-06-17T19:39:00+00:00')
async def test_skip_source_point_check_actions(
        orders_return_point,
        mock_waybill_info,
        mock_dispatch_return,
        mock_driver_tags_v1_match_profile,
        default_order_id,
        my_batch_waybill_info,
):
    """
        Skip source point (aka. skip segment) action is forbidden
        by check actions due to waiting time on point.
    """
    set_pickup_arrived(my_batch_waybill_info)

    response = await orders_return_point(default_order_id, claim_point_id=1)
    assert response.status_code == 409
    assert mock_dispatch_return.handler.times_called == 0


def set_pickup_code_received(waybill):
    source_point = next(
        p
        for p in waybill['execution']['points']
        if p['claim_point_id'] == 642499
    )
    source_point['pickup_code_received_at'] = '2020-08-18T13:50:00+00:00'


async def test_check_pickup_code_received(
        orders_return_point,
        mock_driver_tags_v1_match_profile,
        default_order_id,
        my_waybill_info,
):
    """
        If pickup code is received on source point
        then cancel is prohibited (for antifraud reasons).
        More info CARGODEV-921
    """
    set_pickup_code_received(my_waybill_info)

    response = await orders_return_point(
        default_order_id, claim_point_id=642499,
    )
    assert response.status_code == 409


@pytest.mark.config(
    TAXIMETER_VERSION_SETTINGS_BY_BUILD={
        '__default__': {
            'feature_support': {'cargo_async_timer_calculation': '9.00'},
        },
    },
)
async def test_return_request_async_timer(
        orders_return_point,
        mock_driver_tags_v1_match_profile,
        mock_dispatch_return,
        default_order_id,
        my_waybill_info,
):
    mock_dispatch_return.expected_request = {
        'last_known_status': 'pickup_confirmation',
        'performer_info': {
            'driver_id': 'driver_id1',
            'park_id': 'park_id1',
            'phone_pd_id': 'phone_pd_id',
            'tariff_class': 'cargo',
            'transport_type': 'electric_bicycle',
        },
        'point_id': 1,
        'async_timer_calculation_supported': True,
        'need_create_ticket': False,
    }

    response = await orders_return_point(default_order_id)
    assert response.status_code == 200


@pytest.mark.experiments3(filename='exp3_return_restriction.json')
async def test_return_restriction(
        orders_return_point,
        mock_driver_tags_v1_match_profile,
        mock_dispatch_return,
        default_order_id,
        my_waybill_info,
):
    mock_dispatch_return.expected_request = {
        'last_known_status': 'pickup_confirmation',
        'performer_info': {
            'driver_id': 'driver_id1',
            'park_id': 'park_id1',
            'phone_pd_id': 'phone_pd_id',
            'tariff_class': 'cargo',
            'transport_type': 'electric_bicycle',
        },
        'point_id': 1,
        'async_timer_calculation_supported': True,
        'need_create_ticket': True,
    }

    response = await orders_return_point(default_order_id)
    assert response.status_code == 403
    assert response.json() == {
        'code': 'block_restriction',
        'message': 'За возвратом позвоните в поддержку.',
    }


@pytest.mark.experiments3(
    is_config=True,
    match={'predicate': {'init': {}, 'type': 'true'}, 'enabled': True},
    name='cargo_claims_action_checks',
    consumers=['cargo-claims/driver'],
    default_value={
        'return': {
            'enable': True,
            'min_waiting_time_seconds': 0,
            'allow_optional_return_by_driver': False,
        },
    },
)
@pytest.mark.experiments3(filename='exp3_return_restriction.json')
async def test_status_with_return_restriction(
        taxi_cargo_orders,
        orders_return_point,
        mock_dispatch_return,
        default_order_id,
        my_waybill_info,
        mock_driver_tags_v1_match_profile,
        waybill_state,
):
    waybill_state.set_segment_status('ready_for_delivery_confirmation')
    response = await taxi_cargo_orders.post(
        '/driver/v1/cargo-claims/v1/cargo/state',
        headers=DEFAULT_HEADERS,
        json={'cargo_ref_id': 'order/' + default_order_id},
    )
    assert response.status_code == 200

    expected_return_action = [
        {'need_confirmation': True, 'type': 'dropoff', 'conditions': []},
        {
            'blocked_restrictions': [
                {
                    'message': 'За возвратом позвоните в поддержку.',
                    'title': 'Невозможен возврат.',
                    'type': 'call_request',
                },
            ],
            'force_allowed': False,
            'force_punishments': [],
            'free_conditions': [],
            'need_return': True,
            'type': 'return',
        },
        {'type': 'show_act'},
    ]
    assert (
        expected_return_action == response.json()['current_point']['actions']
    )
