import pytest


@pytest.mark.now('2022-02-18T08:46:35+00:00')
@pytest.mark.pgsql(
    'cargo_trucks', files=['pg_carriers.sql', 'pg_shippers.sql'],
)
@pytest.mark.parametrize(
    ['entity'],
    (
        pytest.param('shipper', id='shipper'),
        pytest.param('carrier', id='carrier'),
    ),
)
async def test_registration_pay(
        taxi_cargo_trucks, mockserver, load_json, entity,
):
    @mockserver.json_handler('/billing-orders/v2/process/async')
    def _billing_orders_response(request):
        return mockserver.make_response(
            status=200,
            json={
                'orders': [
                    {
                        'topic': 'topic',
                        'external_ref': 'external_ref',
                        'doc_id': 123,
                    },
                ],
            },
        )

    response = await taxi_cargo_trucks.post(
        '/v1/pay/{}'.format(entity),
        headers={
            'accept-language': 'ru',
            'x-idempotency-token': '13245',
            'x-api-key': 'dGVzdF9zZWNyZXRfa2V5',
        },
        json=load_json('registration_request.json'),
    )
    assert response.status_code == 200
    assert _billing_orders_response.times_called == 1
    assert _billing_orders_response.next_call()['request'].json == load_json(
        'expected_{}_request.json'.format(entity),
    )


async def test_registration_pay_403(taxi_cargo_trucks, load_json):
    response = await taxi_cargo_trucks.post(
        '/v1/pay/shipper',
        headers={
            'accept-language': 'ru',
            'x-idempotency-token': '13245',
            'x-api-key': 'ololo',
        },
        json=load_json('registration_request.json'),
    )
    assert response.status_code == 403


async def test_registration_pay_404(taxi_cargo_trucks, load_json):
    request = load_json('registration_request.json')
    request['external_ref'] = '321'
    response = await taxi_cargo_trucks.post(
        '/v1/pay/shipper',
        headers={
            'accept-language': 'ru',
            'x-idempotency-token': '13245',
            'x-api-key': 'dGVzdF9zZWNyZXRfa2V5',
        },
        json=request,
    )
    assert response.status_code == 404
