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
        'beed2277ae71428db1029c07394e542c': 'eats',
    },
)
async def test_post_simple(mockserver, load_json, taxi_cargo_partial_delivery):
    fetch_revisions_response = load_json('eats_fetch_revisions_response.json')

    def _transform_eats_order():
        items = fetch_revisions_response['items'][0]['revision']['items'][
            'items'
        ]
        items = [
            x
            for x in items
            if x['origin_id'] == '4697cbbc-413b-11e7-97c2-001517db825c'
        ]
        fetch_revisions_response['items'][0]['revision']['items'][
            'items'
        ] = items

    @mockserver.json_handler('/eats-checkout/orders/fetch-revisions')
    def _mock_orders_fetch_revisions(request):
        return fetch_revisions_response

    @mockserver.json_handler('/eats-checkout/order-changes/create')
    def _mock_order_changes_create(request):
        return {'change_id': 1, 'is_cost_increase_allowed': False}

    @mockserver.json_handler('/eats-checkout/order-changes/add-offer')
    def _mock_order_changes_add_offer(request):
        _transform_eats_order()
        return {'offer_id': 1}

    @mockserver.json_handler('/cargo-dispatch/v1/waybill/info')
    def _mock_waybill_info(request):
        return load_json('waybill_info_response.json')

    @mockserver.json_handler('/cargo-claims/v2/claims/exchange/act')
    def _mock_exchange_act(request):
        assert request.json == {
            'items': [
                {
                    'extra_id': '4697cbbc-413b-11e7-97c2-001517db825c',
                    'quantity': 1,
                },
            ],
            'idempotency_token': 'dd62daa8-aa43-4c4f-b3b9-e75a89eb64b4',
        }
        return {}

    response = await taxi_cargo_partial_delivery.post(
        '/driver/v1/partial-delivery/items',
        params={
            'cargo_ref_id': 'order/970f1a5d-49dc-471e-9d7f-46c1833772eb',
            'point_id': 690201,
            'idempotency_token': 'dd62daa8-aa43-4c4f-b3b9-e75a89eb64b4',
        },
        headers=DEFAULT_HEADERS,
        json={
            'items': [
                {'id': '4697cbbc-413b-11e7-97c2-001517db825c', 'quantity': 1},
            ],
        },
    )
    assert response.status_code == 200
