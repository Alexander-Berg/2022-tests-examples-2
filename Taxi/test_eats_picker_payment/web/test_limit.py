import pytest


@pytest.mark.parametrize(
    'params,status',
    [
        ({'card_type': 'TinkoffBank', 'card_value': '12345678'}, 404),
        ({'card_type': 'unknown-type', 'card_value': '1234567'}, 400),
        ({'card_type': 'TinkoffBank', 'card_value': 'bad-value'}, 400),
    ],
)
async def test_get_limit(taxi_eats_picker_payment_web, params, status):
    response = await taxi_eats_picker_payment_web.get(
        '/api/v1/limit', params=params,
    )

    assert response.status == status


@pytest.mark.config(
    EATS_PICKER_PAYMENT_INTEGRATION_STUBS={
        'enabled': False,
        'config': [
            {
                'card_type': 'TinkoffBank',
                'enabled': True,
                'get_limit': 100000.0,
            },
        ],
    },
)
async def test_get_limit_stub(taxi_eats_picker_payment_web):
    response = await taxi_eats_picker_payment_web.get(
        '/api/v1/limit',
        params={'card_type': 'TinkoffBank', 'card_value': 'any'},
    )
    assert (await response.json())['amount'] == 100000.0


async def test_set_limit_ok(taxi_eats_picker_payment_web, tinkoff_service):
    params = {'card_type': 'TinkoffBank', 'card_value': '10000000'}
    response = await taxi_eats_picker_payment_web.post(
        '/api/v1/limit',
        params=params,
        json={'order_id': 'order-id-1', 'amount': 1000},
    )
    assert response.status == 200

    response = await taxi_eats_picker_payment_web.get(
        '/api/v1/limit', params=params,
    )
    assert response.status == 200
    data = await response.json()
    assert data['amount'] == 1000

    tinkoff_service['_decrease_limit_remains']('10000000', 500)

    response = await taxi_eats_picker_payment_web.get(
        '/api/v1/limit', params=params,
    )
    assert response.status == 200
    data = await response.json()
    assert data['amount'] == 500


@pytest.mark.parametrize(
    'params,body,status',
    [
        (
            {'card_type': 'TinkoffBank', 'card_value': '10000000'},
            {'order_id': 'order-id-1', 'amount': 1000},
            200,
        ),
        (
            {'card_type': 'TinkoffBank', 'card_value': 'bad-cid'},
            {'order_id': 'order-id-1', 'amount': 1000},
            400,
        ),
        (
            {'card_type': 'TinkoffBank', 'card_value': '10000000'},
            {'order_id': 'order-id-1', 'amount': -1000},
            400,
        ),
    ],
)
async def test_set_limit_wrong_request(
        taxi_eats_picker_payment_web, params, body, status,
):
    response = await taxi_eats_picker_payment_web.post(
        '/api/v1/limit', params=params, json=body,
    )
    assert response.status == status
