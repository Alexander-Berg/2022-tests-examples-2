import pytest


@pytest.fixture(name='mock_vgw_api')
def _mock_vgw_api(mockserver):
    @mockserver.json_handler('/vgw-api/v1/forwardings')
    def mock(request):
        if context.expected_request is not None:
            request.json.pop('nonce', None)
            assert request.json == context.expected_request
        if context.response is not None:
            return context.response
        return {
            'phone': '+71234567890',
            'ext': '100',
            'expires_at': '2020-04-01T11:35:00+00:00',
        }

    class Context:
        def __init__(self):
            self.expected_request = None
            self.response = None
            self.handler = mock

    context = Context()

    return context


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


@pytest.fixture(name='get_voiceforwarding')
async def _get_voiceforwarding(taxi_cargo_orders, default_order_id):
    async def wrapper(
            phone_type,
            *,
            point_id=642499,
            order_id=default_order_id,
            headers=None,
    ):
        if headers is None:
            headers = DEFAULT_HEADERS
        response = await taxi_cargo_orders.post(
            'driver/v1/cargo-claims/v1/cargo/voiceforwarding',
            headers=headers,
            json={
                'cargo_ref_id': f'order/{order_id}',
                'point_id': point_id,
                'phone_type': phone_type,
            },
        )
        assert response.status_code == 200
        return response.json()

    return wrapper


def _vgw_api_expected_request(
        coordinates,
        callee_phone='+70000000001',
        requester_phone='phone_pd',
        consumer_id=2,
):
    return {
        'call_location': coordinates,
        'callee': 'passenger',
        'callee_phone': callee_phone,
        'consumer': consumer_id,
        'external_ref_id': 'taxi-order',
        'min_ttl': 20,
        'new_ttl': 100,
        'requester': 'driver',
        'requester_phone': requester_phone,
    }


async def test_happy_path(
        taxi_cargo_orders, mock_vgw_api, default_order_id, my_waybill_info,
):
    mock_vgw_api.expected_request = _vgw_api_expected_request(
        coordinates=[37.642979, 55.734977],
    )

    response = await taxi_cargo_orders.post(
        'driver/v1/cargo-claims/v1/cargo/voiceforwarding',
        headers=DEFAULT_HEADERS,
        json={
            'cargo_ref_id': f'order/{default_order_id}',
            'point_id': 642499,
            'phone_type': 'source',
        },
    )
    assert response.status_code == 200


async def test_happy_path_c2c(
        taxi_cargo_orders, mock_vgw_api, default_order_id, waybill_info_c2c,
):
    mock_vgw_api.expected_request = _vgw_api_expected_request(
        coordinates=[37.642979, 55.734977],
    )

    response = await taxi_cargo_orders.post(
        'driver/v1/cargo-claims/v1/cargo/voiceforwarding',
        headers=DEFAULT_HEADERS,
        json={
            'cargo_ref_id': f'order/{default_order_id}',
            'point_id': 642499,
            'phone_type': 'source',
        },
    )
    assert response.status_code == 200


async def test_performer_not_found(
        taxi_cargo_orders, order_id_without_performer,
):
    response = await taxi_cargo_orders.post(
        '/driver/v1/cargo-claims/v1/cargo/voiceforwarding',
        headers=DEFAULT_HEADERS,
        json={
            'cargo_ref_id': f'order/' + order_id_without_performer,
            'point_id': 642499,
            'phone_type': 'source',
        },
    )
    assert response.status_code == 404
    assert response.json()['message'] == 'Performer was not found for order'


@pytest.mark.parametrize(
    ('phone_type', 'claim_point_id', 'expected_coordinates', 'expected_phone'),
    [
        ('emergency', 642500, [37.583, 55.9873], '+70000000000'),
        ('return', 642501, [37.583, 55.8873], '+70000000003'),
        ('source', 642499, [37.642979, 55.734977], '+70000000001'),
        ('destination', 642500, [37.583, 55.9873], '+70000000002'),
    ],
)
@pytest.mark.now('2020-04-01T10:35:00+0000')
async def test_voiceforwarding(
        taxi_cargo_orders,
        default_order_id,
        mock_vgw_api,
        exp_cargo_orders_payment_on_delivery_phone,
        phone_type: str,
        claim_point_id: int,
        expected_coordinates: dict,
        expected_phone: str,
        my_waybill_info,
):
    await exp_cargo_orders_payment_on_delivery_phone()
    mock_vgw_api.expected_request = _vgw_api_expected_request(
        coordinates=expected_coordinates, callee_phone=expected_phone,
    )

    response = await taxi_cargo_orders.post(
        'driver/v1/cargo-claims/v1/cargo/voiceforwarding',
        headers=DEFAULT_HEADERS,
        json={
            'cargo_ref_id': f'order/{default_order_id}',
            'point_id': claim_point_id,
            'phone_type': phone_type,
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        'phone': '+71234567890',
        'ext': '100',
        'ttl_seconds': 3600,
    }


@pytest.mark.parametrize(
    'expected_response_code',
    [
        pytest.param(
            200,
            id='direct_phone_default',
            marks=(
                pytest.mark.config(
                    CARGO_CLAIMS_VOICEFORWARDING_ERROR_HANDLING={
                        '__default__': 'direct_phone',
                    },
                )
            ),
        ),
        pytest.param(
            200,
            id='direct_phone_specific',
            marks=(
                pytest.mark.config(
                    CARGO_CLAIMS_VOICEFORWARDING_ERROR_HANDLING={
                        '__default__': 'throw_exception',
                        'RegionIsNotSupported': 'direct_phone',
                    },
                )
            ),
        ),
        pytest.param(
            404,
            id='not_found',
            marks=(
                pytest.mark.config(
                    CARGO_CLAIMS_VOICEFORWARDING_ERROR_HANDLING={
                        '__default__': 'not_found',
                    },
                )
            ),
        ),
        pytest.param(
            500,
            id='throw',
            marks=(
                pytest.mark.config(
                    CARGO_CLAIMS_VOICEFORWARDING_ERROR_HANDLING={
                        '__default__': 'throw_exception',
                    },
                )
            ),
        ),
    ],
)
@pytest.mark.now('2020-04-01T10:35:00+0000')
async def test_voiceforwarding_error(
        taxi_cargo_orders,
        mock_vgw_api,
        mockserver,
        default_order_id,
        expected_response_code: int,
        my_waybill_info,
        expected_phone='+70000000001',
        claim_point_id=642499,
):
    mock_vgw_api.response = mockserver.make_response(
        status=400,
        json={
            'code': 'RegionIsNotSupported',
            'message': 'Region is not supported',
            'error': {
                'code': 'RegionIsNotSupported',
                'message': 'Region is not supported',
            },
        },
    )

    response = await taxi_cargo_orders.post(
        'driver/v1/cargo-claims/v1/cargo/voiceforwarding',
        headers=DEFAULT_HEADERS,
        json={
            'cargo_ref_id': f'order/{default_order_id}',
            'point_id': claim_point_id,
            'phone_type': 'source',
        },
    )

    assert response.status_code == expected_response_code, response.json()
    if response.status_code == 200:
        assert response.json() == {
            'phone': expected_phone,
            'ext': '',
            'ttl_seconds': 100,
        }


async def test_no_vgw(
        taxi_cargo_orders,
        exp_cargo_voiceforwarding,
        default_order_id,
        my_waybill_info,
):
    await exp_cargo_voiceforwarding(enabled=False)

    response = await taxi_cargo_orders.post(
        'driver/v1/cargo-claims/v1/cargo/voiceforwarding',
        headers=DEFAULT_HEADERS,
        json={
            'cargo_ref_id': f'order/{default_order_id}',
            'point_id': 642499,
            'phone_type': 'source',
        },
    )
    assert response.status_code == 200

    assert response.json() == {
        'phone': '+70000000001',
        'ext': '',
        'ttl_seconds': 1000,
    }


async def test_raw_phone_on_vgw_error(
        taxi_cargo_orders,
        exp_cargo_voiceforwarding,
        mock_vgw_api,
        mockserver,
        default_order_id,
        my_waybill_info,
):
    mock_vgw_api.response = mockserver.make_response(
        status=400,
        json={
            'code': 'RegionIsNotSupported',
            'error': {
                'code': 'RegionIsNotSupported',
                'message': 'Region is not supported',
            },
        },
    )
    await exp_cargo_voiceforwarding(fallback_type='raw_personal')

    response = await taxi_cargo_orders.post(
        'driver/v1/cargo-claims/v1/cargo/voiceforwarding',
        headers=DEFAULT_HEADERS,
        json={
            'cargo_ref_id': f'order/{default_order_id}',
            'point_id': 642499,
            'phone_type': 'source',
        },
    )
    assert response.status_code == 200

    assert response.json() == {
        'phone': '+70000000001',
        'ext': '',
        'ttl_seconds': 1000,
    }


@pytest.mark.config(
    CARGO_CLAIMS_VOICEFORWARDING_SETTINGS_BY_CLIENT={
        '5e36732e2bc54e088b1466e08e31c486': {
            'min_ttl': 20,
            'new_ttl': 100,
            'consumer_id': 3,
        },
    },
)
async def test_consumer_id_forwarding(
        taxi_cargo_orders, mock_vgw_api, default_order_id,
):
    mock_vgw_api.expected_request = _vgw_api_expected_request(
        coordinates=[37.642979, 55.734977], consumer_id=3,
    )

    response = await taxi_cargo_orders.post(
        'driver/v1/cargo-claims/v1/cargo/voiceforwarding',
        headers=DEFAULT_HEADERS,
        json={
            'cargo_ref_id': f'order/{default_order_id}',
            'point_id': 642499,
            'phone_type': 'source',
        },
    )
    assert response.status_code == 200


@pytest.mark.parametrize(
    'bad_header', ['X-YaTaxi-Driver-Profile-Id', 'X-YaTaxi-Park-Id'],
)
async def test_no_auth(taxi_cargo_orders, default_order_id, bad_header: str):
    headers_bad_driver = DEFAULT_HEADERS.copy()
    headers_bad_driver[bad_header] = 'bad'

    response = await taxi_cargo_orders.post(
        '/driver/v1/cargo-claims/v1/cargo/voiceforwarding',
        headers=headers_bad_driver,
        json={
            'cargo_ref_id': 'order/' + default_order_id,
            'last_known_status': 'new',
            'idempotency_token': 'some_token',
            'phone_type': 'source',
            'point_id': 123123,
        },
    )
    assert response.status_code == 403
    assert response.json() == {
        'code': 'not_authorized',
        'message': 'Попробуйте снова',
    }


async def test_payment_on_delivery_support(
        exp_cargo_orders_payment_on_delivery_phone,
        exp_cargo_voiceforwarding,
        my_waybill_info,
        get_voiceforwarding,
):
    """
        Check support phone is returned
        for payment_on_delivery_support phone request.
    """
    await exp_cargo_voiceforwarding(enabled=False)
    await exp_cargo_orders_payment_on_delivery_phone()

    response = await get_voiceforwarding('payment_on_delivery_support')

    assert response == {
        'phone': '+74449990000',
        'ext': '',
        'ttl_seconds': 1000,
    }


@pytest.mark.parametrize(
    ['override_emergency', 'expected_phone'],
    [(True, '+74449990000'), (False, '+70000000000')],
)
async def test_payment_on_delivery_emergency(
        exp_cargo_orders_payment_on_delivery_phone,
        exp_cargo_voiceforwarding,
        my_waybill_info,
        get_voiceforwarding,
        override_emergency: bool,
        expected_phone: str,
):
    """
        Check support phone overrides emergency.
    """
    await exp_cargo_voiceforwarding(enabled=False)
    await exp_cargo_orders_payment_on_delivery_phone(
        override_emergency=override_emergency,
    )

    response = await get_voiceforwarding('emergency')

    assert response == {
        'phone': expected_phone,
        'ext': '',
        'ttl_seconds': 1000,
    }


@pytest.mark.config(CARGO_ORDERS_VOICEFORWARDING_PROFILE_RETRIEVE_ENABLED=True)
@pytest.mark.parametrize(
    ['deaf', 'expected_phone', 'expected_ext'],
    [
        (True, '+70000000001', ''),
        (False, '+71234567890', '100'),
        (None, '+71234567890', '100'),
    ],
)
async def test_deaf_driver(
        taxi_cargo_orders,
        mock_vgw_api,
        mockserver,
        default_order_id,
        experiments3,
        deaf: bool,
        expected_phone: str,
        expected_ext: str,
):
    experiments3.add_config(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='cargo_orders_voiceforwarding',
        consumers=['cargo-orders/voiceforwarding'],
        clauses=[
            {
                'predicate': {'init': {'arg_name': 'is_deaf'}, 'type': 'bool'},
                'value': {
                    'enabled': False,
                    'fallback_type': 'raw_personal',
                    'phone_ttl_sec': 1000,
                },
            },
        ],
        default_value={
            'enabled': True,
            'fallback_type': 'error',
            'phone_ttl_sec': 1000,
        },
    )
    await taxi_cargo_orders.invalidate_caches()

    @mockserver.json_handler('/driver-profiles/v1/driver/profiles/retrieve')
    def _mock_driver_profiles(request):
        if deaf is None:
            return {
                'profiles': [
                    {'park_driver_profile_id': 'some_unnecessary_id'},
                ],
            }

        return {
            'profiles': [
                {
                    'park_driver_profile_id': 'some_unnecessary_id',
                    'data': {'is_deaf': deaf},
                },
            ],
        }

    response = await taxi_cargo_orders.post(
        'driver/v1/cargo-claims/v1/cargo/voiceforwarding',
        headers=DEFAULT_HEADERS,
        json={
            'cargo_ref_id': f'order/{default_order_id}',
            'point_id': 642499,
            'phone_type': 'source',
        },
    )

    assert response.json()['phone'] == expected_phone
    assert response.json()['ext'] == expected_ext


@pytest.mark.parametrize(
    ['raw_phone', 'phone_additional_code'],
    [('+70000000002', None), ('+70000000002', '111 22 333')],
)
async def test_phone_with_additional_code(
        taxi_cargo_orders,
        default_order_id,
        experiments3,
        mockserver,
        mock_vgw_api,
        raw_phone,
        phone_additional_code,
        my_waybill_info,
):
    experiments3.add_config(
        match={'predicates': {'type': 'true'}, 'enabled': True},
        name='cargo_orders_voiceforwarding',
        consumers=['cargo-orders/voiceforwarding'],
        clauses=[
            {
                'predicate': {
                    'init': {'arg_name': 'has_phone_additional_code'},
                    'type': 'bool',
                },
                'value': {
                    'enabled': False,
                    'fallback_type': 'raw_personal',
                    'phone_ttl_sec': 1000,
                },
            },
        ],
        default_value={
            'enabled': True,
            'fallback_type': 'error',
            'phone_ttl_sec': 1000,
        },
    )
    await taxi_cargo_orders.invalidate_caches()

    @mockserver.json_handler('/cargo-dispatch/v1/waybill/info')
    def _mock_waybill_info(request):
        my_waybill_info['segments'][0]['points'][1]['contact'][
            'phone_additional_code'
        ] = phone_additional_code
        return mockserver.make_response(json=my_waybill_info, status=200)

    expected_phone = '+71234567890'

    @mockserver.json_handler('/vgw-api/v1/forwardings')
    def _mock_forwardings(request):
        return {
            'phone': expected_phone,
            'ext': '100',
            'expires_at': '2022-02-22T11:35:00+00:00',
        }

    response = await taxi_cargo_orders.post(
        'driver/v1/cargo-claims/v1/cargo/voiceforwarding',
        headers=DEFAULT_HEADERS,
        json={
            'cargo_ref_id': f'order/{default_order_id}',
            'point_id': 642500,
            'phone_type': 'destination',
        },
    )

    assert response.status_code == 200
    assert (
        response.json()['phone'] == expected_phone
        if phone_additional_code is None
        else raw_phone
    )


@pytest.mark.parametrize(
    ['sender_is_picker', 'expected_ext'],
    [(True, 'driver'), (False, 'passenger')],
)
async def test_sender_is_picker(
        taxi_cargo_orders,
        mockserver,
        mock_vgw_api,
        default_order_id,
        my_waybill_info,
        sender_is_picker: bool,
        expected_ext: str,
):
    """
        Check callee client type.
    """
    my_waybill_info['execution']['segments'][0]['custom_context'] = {
        'sender_is_picker': sender_is_picker,
    }

    @mockserver.json_handler('/vgw-api/v1/forwardings')
    def _mock(request):
        assert request.json['callee'] == expected_ext
        return {
            'phone': '+71234567890',
            'ext': '100',
            'expires_at': '2021-11-09T11:35:00+00:00',
        }

    response = await taxi_cargo_orders.post(
        'driver/v1/cargo-claims/v1/cargo/voiceforwarding',
        headers=DEFAULT_HEADERS,
        json={
            'cargo_ref_id': f'order/{default_order_id}',
            'point_id': 642499,
            'phone_type': 'source',
        },
    )

    assert response.status_code == 200


@pytest.mark.config(CARGO_ORDERS_FETCH_PERFORMER_CORE_ENABLED=True)
async def test_fetch_order_core(
        taxi_cargo_orders,
        order_id_without_performer,
        waybill_state,
        mockserver,
        mock_vgw_api,
):
    @mockserver.json_handler('/cargo-dispatch/v1/waybill/info')
    def _mock_waybill_info(request):
        return waybill_state.load_waybill(
            'cargo-dispatch/v1_waybill_info_tpl.json',
        )

    @mockserver.json_handler('/order-core/v1/tc/order-fields')
    def _mock_order_core(request):
        assert request.json['order_id'] == 'taxi-order2'
        return {
            'order_id': 'taxi-order2',
            'replica': 'secondary',
            'version': 'xxx',
            'fields': {
                'order': {
                    'performer': {
                        'uuid': 'driver_id1',
                        'db_id': 'park_id1',
                        'tariff': {'class': 'cargo'},
                    },
                },
            },
        }

    @mockserver.json_handler('/vgw-api/v1/forwardings')
    def _mock_forwardings(request):
        return {
            'phone': '+71234567890',
            'ext': '100',
            'expires_at': '2021-11-09T11:35:00+00:00',
        }

    response = await taxi_cargo_orders.post(
        'driver/v1/cargo-claims/v1/cargo/voiceforwarding',
        headers=DEFAULT_HEADERS,
        json={
            'cargo_ref_id': f'order/' + order_id_without_performer,
            'point_id': 642499,
            'phone_type': 'source',
        },
    )

    assert response.status_code == 200
