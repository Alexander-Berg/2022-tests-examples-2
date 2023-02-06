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


@pytest.fixture(name='platform_confirm_point')
def _orders_confirm_point(taxi_cargo_orders):
    async def _wrapper(order_id: str, driver_id=None, park_id=None):
        if driver_id is None:
            driver_id = 'driver_id1'
        if park_id is None:
            park_id = 'park_id1'
        response = await taxi_cargo_orders.post(
            '/v1/pro-platform/exchange/confirm',
            json={
                'cargo_ref_id': 'order/' + order_id,
                'performer_params': {
                    'driver_profile_id': driver_id,
                    'park_id': park_id,
                    'app': {
                        'version_type': '',
                        'version': '10.06 (8891)',
                        'platform': 'android',
                    },
                    'remote_ip': '12.34.56.78',
                },
                'last_known_status': 'pickup_confirmation',
                'point_id': 1,
                'idempotency_token': 'some_token',
            },
            headers=DEFAULT_HEADERS,
        )
        return response

    return _wrapper


async def test_happy_path(
        platform_confirm_point,
        mock_dispatch_exchange_confirm,
        default_order_id,
        mock_waybill_info,
        my_waybill_info,
):
    response = await platform_confirm_point(default_order_id)
    assert response.status_code == 200
    assert response.json() == {
        'performer': TEST_SIMPLE_JSON_PERFORMER_RESULT,
        'waybill': my_waybill_info,
        'status': matching.AnyString(),
    }


async def test_conflict(
        platform_confirm_point,
        mock_dispatch_exchange_confirm,
        default_order_id,
        mockserver,
):
    mock_dispatch_exchange_confirm.response = mockserver.make_response(
        status=409,
        json={'code': 'state_mismatch', 'message': 'confirmation conflict'},
    )

    response = await platform_confirm_point(default_order_id)
    assert response.status_code == 409


@pytest.mark.parametrize(
    'last_status,result_code', [('complete', 200), ('new', 409)],
)
async def test_confirm_without_point(
        taxi_cargo_orders,
        default_order_id,
        last_status: str,
        result_code: int,
):
    response = await taxi_cargo_orders.post(
        '/v1/pro-platform/exchange/confirm',
        headers=DEFAULT_HEADERS,
        json={
            'cargo_ref_id': 'order/' + default_order_id,
            'performer_params': {
                'driver_profile_id': 'driver_id1',
                'park_id': 'park_id1',
                'app': {
                    'version_type': '',
                    'version': '10.06 (8891)',
                    'platform': 'android',
                },
                'remote_ip': '12.34.56.78',
            },
            'last_known_status': last_status,
            'idempotency_token': 'some_token',
        },
    )

    assert response.status_code == result_code


@pytest.mark.parametrize(
    'driver_profile_id, park_id', [('driver_id1', ''), ('driver', 'park_id1')],
)
async def test_no_auth(
        platform_confirm_point, default_order_id, driver_profile_id, park_id,
):
    response = await platform_confirm_point(
        default_order_id, driver_id=driver_profile_id, park_id=park_id,
    )
    assert response.status_code == 403
    assert response.json()['code'] == 'not_authorized'
    assert response.json()['message'] == 'Попробуйте снова'


async def test_confirm_request(
        platform_confirm_point,
        mock_dispatch_exchange_confirm,
        default_order_id,
):
    mock_dispatch_exchange_confirm.expected_request = {
        'last_known_status': 'pickup_confirmation',
        'point_id': 1,
        'performer_info': {
            'park_id': 'park_id1',
            'driver_id': 'driver_id1',
            'tariff_class': 'cargo',
            'transport_type': 'electric_bicycle',
        },
        'async_timer_calculation_supported': False,
    }

    response = await platform_confirm_point(default_order_id)
    assert response.status_code == 200


@pytest.mark.config(
    TAXIMETER_VERSION_SETTINGS_BY_BUILD={
        '__default__': {
            'feature_support': {'cargo_async_timer_calculation': '9.00'},
        },
    },
)
async def test_confirm_request_async_timer(
        platform_confirm_point,
        mock_dispatch_exchange_confirm,
        default_order_id,
):
    mock_dispatch_exchange_confirm.expected_request = {
        'last_known_status': 'pickup_confirmation',
        'point_id': 1,
        'performer_info': {
            'park_id': 'park_id1',
            'driver_id': 'driver_id1',
            'tariff_class': 'cargo',
            'transport_type': 'electric_bicycle',
        },
        'async_timer_calculation_supported': True,
    }

    response = await platform_confirm_point(default_order_id)
    assert response.status_code == 200


@pytest.mark.config(
    CARGO_ORDERS_PHOENIX_SETTINGS={
        'exchange_init_enabled': False,
        'exchange_confirm_enabled': True,
        'payment_not_found_tanker_key': 'errors.phoenix_payment_not_found',
        'cannot_check_payment_tanker_key': (
            'errors.cannot_check_phoenix_payment'
        ),
        'ignore_check_payment_admin_exchange_init': True,
    },
    CARGO_ORDERS_GET_PHOENIX_TRAITS_WITH_YT=True,
)
@pytest.mark.parametrize(
    'is_paid, '
    'claims_response_status, '
    'expected_status_code, '
    'code, '
    'message',
    [
        (True, 'success', 200, None, None),
        (False, 'success', 404, 'payment_not_found', 'Заказ не оплачен'),
        (
            True,
            'not_found',
            404,
            'order_not_found',
            'Нет возможности проверить оплату',
        ),
        (True, 'failed', 500, '500', 'Internal Server Error'),
    ],
)
async def test_phoenix_flow(
        platform_confirm_point,
        mock_dispatch_exchange_confirm,
        mock_claims_phoenix_traits,
        default_order_id,
        mockserver,
        is_paid,
        claims_response_status,
        expected_status_code,
        code,
        message,
):
    mock_claims_phoenix_traits.claims_response_status = claims_response_status

    @mockserver.json_handler(
        '/cargo-finance/internal/cargo-finance/v1/claims/payment-status',
    )
    def _mock_claim_state(request):
        assert request.args['claim_id'] == 'claim_uuid_1'
        return mockserver.make_response(json={'is_paid': is_paid}, status=200)

    response = await platform_confirm_point(default_order_id)
    assert response.status_code == expected_status_code
    if response.status_code != 200:
        assert response.json() == {'code': code, 'message': message}


@pytest.mark.config(
    CARGO_ORDERS_PHOENIX_SETTINGS={
        'exchange_init_enabled': False,
        'exchange_confirm_enabled': True,
        'payment_not_found_tanker_key': 'errors.phoenix_payment_not_found',
        'cannot_check_payment_tanker_key': (
            'errors.cannot_check_phoenix_payment'
        ),
        'ignore_check_payment_admin_exchange_init': True,
    },
    CARGO_ORDERS_GET_PHOENIX_TRAITS_WITH_YT=True,
)
async def test_phoenix_flow_cache_hit(
        platform_confirm_point,
        taxi_cargo_orders,
        mock_admin_claims_phoenix_traits,
        mock_dispatch_exchange_confirm,
        mock_claims_phoenix_traits,
        default_order_id,
        mockserver,
):
    @mockserver.json_handler(
        '/cargo-finance/internal/cargo-finance/v1/claims/payment-status',
    )
    def _mock_claim_state(request):
        assert request.args['claim_id'] == 'claim_uuid_1'
        return mockserver.make_response(json={'is_paid': True}, status=200)

    response = await taxi_cargo_orders.post(
        '/v1/phoenix/traits',
        json={'cargo_ref_id': f'order/{default_order_id}'},
    )
    assert response.status_code == 200

    response = await platform_confirm_point(default_order_id)
    assert response.status_code == 200
    assert mock_claims_phoenix_traits.handler.times_called == 0
