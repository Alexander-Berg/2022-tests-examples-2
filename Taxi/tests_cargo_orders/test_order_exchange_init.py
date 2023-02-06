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


@pytest.mark.config(
    CARGO_ORDERS_PHOENIX_SETTINGS={
        'exchange_init_enabled': False,
        'payment_not_found_tanker_key': 'errors.phoenix_payment_not_found',
    },
)
@pytest.mark.parametrize(
    'dispatch_response_code, point_id, result_code',
    [
        (200, 100500, 200),
        (404, 100500, 404),
        (409, 100500, 409),
        (410, 100500, 410),
        (429, 100500, 429),
        (500, 100500, 500),
    ],
)
async def test_claims_exchange_statuses(
        taxi_cargo_orders,
        mockserver,
        default_order_id,
        dispatch_response_code: int,
        point_id: int,
        result_code: int,
):
    @mockserver.json_handler('/cargo-dispatch/v1/waybill/exchange/init')
    def _mock_segment_init(request):
        assert request.json == {
            'last_known_status': 'delivering',
            'idempotency_token': 'some_token',
            'point_id': 100500,
            'is_driver_request': True,
            'performer_info': {
                'driver_id': 'driver_id1',
                'park_id': 'park_id1',
                'tariff_class': 'cargo',
                'taximeter_app': {
                    'version': '9.40',
                    'version_type': '',
                    'platform': 'android',
                },
            },
        }
        return mockserver.make_response(
            json={'new_status': 'pickup_confirmation'}
            if dispatch_response_code == 200
            else {'code': 'not_found', 'message': 'some message'},
            status=dispatch_response_code,
        )

    response = await taxi_cargo_orders.post(
        '/driver/v1/cargo-claims/v1/cargo/exchange/init',
        headers=DEFAULT_HEADERS,
        json={
            'cargo_ref_id': 'order/' + default_order_id,
            'last_known_status': 'delivering',
            'point_id': point_id,
            'idempotency_token': 'some_token',
        },
    )

    assert response.status_code == result_code


@pytest.mark.parametrize(
    'last_status,result_code', [('complete', 200), ('new', 409)],
)
async def test_claims_exchange_without_point(
        taxi_cargo_orders,
        default_order_id,
        last_status: str,
        result_code: int,
):
    response = await taxi_cargo_orders.post(
        '/driver/v1/cargo-claims/v1/cargo/exchange/init',
        headers=DEFAULT_HEADERS,
        json={
            'cargo_ref_id': 'order/' + default_order_id,
            'last_known_status': last_status,
            'idempotency_token': 'some_token',
        },
    )

    assert response.status_code == result_code


@pytest.mark.parametrize(
    'bad_header', ['X-YaTaxi-Driver-Profile-Id', 'X-YaTaxi-Park-Id'],
)
async def test_no_auth(taxi_cargo_orders, default_order_id, bad_header: str):
    headers_bad_driver = DEFAULT_HEADERS.copy()
    headers_bad_driver[bad_header] = 'bad'

    response = await taxi_cargo_orders.post(
        '/driver/v1/cargo-claims/v1/cargo/exchange/init',
        headers=headers_bad_driver,
        json={
            'cargo_ref_id': 'order/' + default_order_id,
            'last_known_status': 'new',
            'idempotency_token': 'some_token',
            'point_id': 123123,
        },
    )
    assert response.status_code == 403
    assert response.json() == {
        'code': 'not_authorized',
        'message': 'Попробуйте снова',
    }


@pytest.mark.config(
    CARGO_ORDERS_PHOENIX_SETTINGS={
        'exchange_init_enabled': False,
        'payment_not_found_tanker_key': 'errors.phoenix_payment_not_found',
    },
)
async def test_init_request(taxi_cargo_orders, mockserver, default_order_id):
    @mockserver.json_handler('/cargo-dispatch/v1/waybill/exchange/init')
    def _mock_segment_init(request):
        assert request.json == {
            'last_known_status': 'delivering',
            'idempotency_token': 'some_token',
            'point_id': 1,
            'is_driver_request': True,
            'performer_info': {
                'driver_id': 'driver_id1',
                'park_id': 'park_id1',
                'tariff_class': 'cargo',
                'taximeter_app': {
                    'version': '9.40',
                    'version_type': '',
                    'platform': 'android',
                },
            },
        }
        return {'new_status': 'pickup_confirmation'}

    response = await taxi_cargo_orders.post(
        '/driver/v1/cargo-claims/v1/cargo/exchange/init',
        headers=DEFAULT_HEADERS,
        json={
            'cargo_ref_id': 'order/' + default_order_id,
            'last_known_status': 'delivering',
            'point_id': 1,
            'idempotency_token': 'some_token',
        },
    )
    assert response.status_code == 200


@pytest.mark.config(
    CARGO_ORDERS_PHOENIX_SETTINGS={
        'exchange_init_enabled': False,
        'payment_not_found_tanker_key': 'errors.phoenix_payment_not_found',
    },
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='cargo_batch_skip_arrive_screen',
    consumers=['cargo-orders/taximeter-api'],
    clauses=[],
    default_value={
        'enable': True,
        'skip_arrive_screen': True,
        'pickup_label_tanker_key': '123',
    },
)
async def test_init_after_skip_arrive_screen(
        taxi_cargo_orders,
        mockserver,
        default_order_id,
        my_batch_waybill_info,
        mock_driver_tags_v1_match_profile,
):
    """
    Point A1 == A2
    Skip action 'arrive_at_point'
    """
    coordinates = [1, 2]
    my_batch_waybill_info['execution']['points'][0]['location'][
        'coordinates'
    ] = coordinates
    my_batch_waybill_info['execution']['points'][1]['location'][
        'coordinates'
    ] = coordinates
    my_batch_waybill_info['execution']['segments'][1][
        'status'
    ] = 'performer_found'

    # Prepare order
    response = await taxi_cargo_orders.post(
        '/driver/v1/cargo-claims/v1/cargo/state',
        headers=DEFAULT_HEADERS,
        json={'cargo_ref_id': 'order/' + default_order_id},
    )
    assert response.status_code == 200

    @mockserver.json_handler('/cargo-dispatch/v1/waybill/exchange/init')
    def _mock_segment_init(request):
        assert request.json == {
            'last_known_status': 'delivering',
            'idempotency_token': 'some_token',
            'point_id': 1,
            'is_driver_request': True,
            'performer_info': {
                'driver_id': 'driver_id1',
                'park_id': 'park_id1',
                'tariff_class': 'cargo',
                'taximeter_app': {
                    'version': '9.40',
                    'version_type': '',
                    'platform': 'android',
                },
            },
            'do_arrive_at_point': True,
        }
        return {'new_status': 'pickup_confirmation'}

    response = await taxi_cargo_orders.post(
        '/driver/v1/cargo-claims/v1/cargo/exchange/init',
        headers=DEFAULT_HEADERS,
        json={
            'cargo_ref_id': 'order/' + default_order_id,
            'last_known_status': 'delivering',
            'point_id': 1,
            'idempotency_token': 'some_token',
        },
    )
    assert response.status_code == 200


async def test_exchange_init_wrong_params(taxi_cargo_orders):
    response = await taxi_cargo_orders.post(
        '/driver/v1/cargo-claims/v1/cargo/exchange/init',
        headers=DEFAULT_HEADERS,
        json={
            'cargo_ref_id': '',
            'last_known_status': 'new',
            'idempotency_token': 'some_token',
            'point_id': 123123,
        },
    )

    assert response.status_code == 400
    assert response.json() == {
        'code': 'bad_request',
        'message': 'Bad cargo_ref_id ',
    }
