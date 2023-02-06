import pytest


DEFAULT_HEADERS = {
    'Accept-Language': 'en',
    'Content-Type': 'application/json',
    'X-Remote-IP': '12.34.56.78',
    'X-YaTaxi-Driver-Profile-Id': 'driver_id1',
    'X-YaTaxi-Park-Id': 'park_id1',
    'X-Request-Application': 'taximeter',
    'X-Request-Application-Version': '9.60',
    'X-Request-Version-Type': '',
    'X-Request-Platform': 'android',
}


@pytest.mark.config(
    CARGO_PARTIAL_DELIVERY_PROVIDERS={
        'beed2277ae71428db1029c07394e542c': 'default',
    },
)
async def test_get_simple(mockserver, load_json, taxi_cargo_partial_delivery):
    @mockserver.json_handler('/cargo-claims/v2/claims/full')
    def _mock_claims_full(request):
        return load_json('claims_full_response.json')

    @mockserver.json_handler('/cargo-dispatch/v1/waybill/info')
    def _mock_waybill_info(request):
        return load_json('waybill_info_response.json')

    response = await taxi_cargo_partial_delivery.get(
        '/driver/v1/partial-delivery/items',
        params={
            'cargo_ref_id': 'order/970f1a5d-49dc-471e-9d7f-46c1833772eb',
            'point_id': 690201,
            'idempotency_token': 'dd62daa8-aa43-4c4f-b3b9-e75a89eb64b4',
        },
        headers=DEFAULT_HEADERS,
    )
    assert response.status_code == 200
    assert response.json() == {
        'assembly_cost': 0.0,
        'cost_currency': 'RUR',
        'delivery_cost': 0.0,
        'items': [
            {
                'cost_value': '10.20',
                'id': '1',
                'quantity': 50,
                'title': 'cargo_item_1',
            },
        ],
        'items_cost': 510,
        'payment_method': '',
    }


@pytest.fixture(name='mock_exchange_act')
def _mock_exchange_act(mockserver):
    @mockserver.json_handler('/cargo-claims/v2/claims/exchange/act')
    def mock(request):
        context.requests.append(request.json)
        if context.status_code == 200:
            return {}
        return mockserver.make_response(
            status=context.status_code,
            json={
                'code': context.error_code,
                'message': context.error_message,
            },
        )

    class Context:
        def __init__(self):
            self.requests = []
            self.status_code = 200
            self.error_code = 'bad_request'
            self.error_message = 'error message'
            self.handler = mock

    context = Context()

    return context


@pytest.fixture(name='post_simple_state')
async def _post_simple_state(
        mockserver,
        load_json,
        taxi_cargo_partial_delivery,
        mock_exchange_act,
        taxi_config,
):
    async def wrapper():
        @mockserver.json_handler('/cargo-claims/v2/claims/full')
        def _mock_claims_full(request):
            return load_json('claims_full_response.json')

        @mockserver.json_handler('/cargo-dispatch/v1/waybill/info')
        def _mock_waybill_info(request):
            return load_json('waybill_info_response.json')

        taxi_config.set_values(
            dict(
                CARGO_PARTIAL_DELIVERY_PROVIDERS={
                    'beed2277ae71428db1029c07394e542c': 'default',
                },
            ),
        )
        await taxi_cargo_partial_delivery.invalidate_caches()

    return wrapper


@pytest.fixture(name='post_partial_delivery_items')
async def _post_partial_delivery_items(taxi_cargo_partial_delivery):
    async def wrapper():
        return await taxi_cargo_partial_delivery.post(
            '/driver/v1/partial-delivery/items',
            params={
                'cargo_ref_id': 'order/970f1a5d-49dc-471e-9d7f-46c1833772eb',
                'point_id': 690201,
                'idempotency_token': 'dd62daa8-aa43-4c4f-b3b9-e75a89eb64b4',
            },
            headers=DEFAULT_HEADERS,
            json={'items': [{'id': '1', 'quantity': 10}]},
        )

    return wrapper


async def test_post_simple(
        post_simple_state, mock_exchange_act, post_partial_delivery_items,
):
    await post_simple_state()

    response = await post_partial_delivery_items()
    assert response.status_code == 200

    assert mock_exchange_act.requests == [
        {
            'items': [{'id': 1, 'quantity': 10}],
            'idempotency_token': 'dd62daa8-aa43-4c4f-b3b9-e75a89eb64b4',
        },
    ]


async def test_post_simple_exchange_bad_request(
        post_simple_state, mock_exchange_act, post_partial_delivery_items,
):
    await post_simple_state()
    mock_exchange_act.status_code = 400

    response = await post_partial_delivery_items()
    assert response.status_code == 400
    assert response.json() == {
        'code': 'exchange_act_bad_request',
        'message': 'error message',
    }
