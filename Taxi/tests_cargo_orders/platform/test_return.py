import pytest

from testsuite.utils import matching

DEFAULT_HEADERS = {'Accept-Language': 'en'}


TEST_SIMPLE_JSON_PERFORMER_RESULT = {
    'car_id': 'car_id1',
    'car_model': 'some_car_model',
    'car_number': 'some_car_number',
    'driver_id': 'driver_id1',
    'is_deaf': False,
    'lookup_version': 1,
    'name': 'Kostya',
    'order_alias_id': '1234',
    'order_id': '9db1622e-582d-4091-b6fc-4cb2ffdc12c0',
    'park_clid': 'park_clid1',
    'park_id': 'park_id1',
    'park_name': 'some_park_name',
    'park_org_name': 'some_park_org_name',
    'phone_pd_id': 'phone_pd_id',
    'revision': 1,
    'tariff_class': 'cargo',
    'transport_type': 'electric_bicycle',
}


@pytest.fixture(name='pro_platform_return')
def _pro_platform_return(taxi_cargo_orders):
    async def _wrapper(
            order_id: str,
            claim_point_id: int = 1,
            last_known_status='pickup_confirmation',
            driver_id='driver_id1',
            park_id='park_id1',
    ):
        response = await taxi_cargo_orders.post(
            '/v1/pro-platform/return',
            json={
                'cargo_ref_id': 'order/' + order_id,
                'point_id': claim_point_id,
                'idempotency_token': 'some_token',
                'last_known_status': last_known_status,
                'performer_params': {
                    'driver_profile_id': driver_id,
                    'park_id': park_id,
                    'app': {
                        'version_type': '',
                        'version': '9.40',
                        'platform': 'android',
                    },
                    'remote_ip': '12.34.56.78',
                },
            },
            headers=DEFAULT_HEADERS,
        )
        return response

    return _wrapper


async def test_happy_path(
        pro_platform_return,
        mock_dispatch_return,
        default_order_id,
        my_waybill_info,
        load_json,
):
    response = await pro_platform_return(default_order_id)
    assert response.status_code == 200

    expected_result = load_json('cargo-orders/v1_pro_platform_return.json')
    assert response.json() == {
        'status': matching.AnyString(),
        **expected_result,
    }

    assert mock_dispatch_return.handler.times_called == 1


async def test_happy_path_no_point_id(
        pro_platform_return,
        mock_dispatch_return,
        default_order_id,
        my_waybill_info,
        waybill_state,
        load_json,
):
    waybill_state.set_segment_status('complete')
    response = await pro_platform_return(default_order_id, None, 'complete')
    assert response.status_code == 200

    expected_result = load_json('cargo-orders/v1_pro_platform_return.json')
    expected_result['waybill']['execution']['segments'][0][
        'status'
    ] = 'complete'
    assert response.json() == {
        'status': matching.AnyString(),
        **expected_result,
    }
    assert mock_dispatch_return.handler.times_called == 0


@pytest.mark.parametrize(
    'driver_profile_id, park_id',
    [('driver_id1', ''), ('driver', 'park_id1'), ('', 'park_id1')],
)
async def test_not_authorized(
        pro_platform_return, default_order_id, driver_profile_id, park_id,
):
    response = await pro_platform_return(
        default_order_id, 1, 'pickup_confirmation', 'unauthorized',
    )
    assert response.status_code == 403

    assert response.json() == {
        'code': 'not_authorized',
        'message': 'Попробуйте снова',
    }


async def test_return_request(
        pro_platform_return,
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
        'need_create_ticket': False,
        'point_id': 1,
        'async_timer_calculation_supported': False,
    }

    response = await pro_platform_return(default_order_id)
    assert response.status_code == 200


def set_pickup_arrived(waybill):
    for segment in waybill['execution']['segments']:
        segment['status'] = 'pickup_arrived'


@pytest.mark.experiments3(filename='exp3_action_checks.json')
@pytest.mark.now('2020-06-17T19:39:00+00:00')
async def test_skip_source_point_check_actions(
        pro_platform_return,
        mock_waybill_info,
        mock_dispatch_return,
        default_order_id,
        my_batch_waybill_info,
):
    """
        Skip source point (aka. skip segment) action is forbidden
        by check actions due to waiting time on point.
    """
    set_pickup_arrived(my_batch_waybill_info)

    response = await pro_platform_return(default_order_id, claim_point_id=1)
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
        pro_platform_return, default_order_id, my_waybill_info,
):
    """
        If pickup code is received on source point
        then cancel is prohibited (for antifraud reasons).
        More info CARGODEV-921
    """
    set_pickup_code_received(my_waybill_info)

    response = await pro_platform_return(
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
        pro_platform_return,
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
        'need_create_ticket': False,
        'point_id': 1,
        'async_timer_calculation_supported': True,
    }

    response = await pro_platform_return(default_order_id)
    assert response.status_code == 200
