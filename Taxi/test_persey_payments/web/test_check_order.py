import pytest


@pytest.mark.pgsql('persey_payments', files=['check_order_simple.sql'])
async def test_simple(
        taxi_persey_payments_web, mock_trust_check_basket, load_json,
):
    check_basket = load_json('check_basket_simple.json')
    check_mock1 = mock_trust_check_basket(
        check_basket['first'], 'trust-basket-token',
    )
    check_mock2 = mock_trust_check_basket(
        check_basket['second'], 'trust-basket-token2',
    )

    response = await taxi_persey_payments_web.post(
        '/v1/order/check', json={'order_id': 'some_order'},
    )

    assert response.status == 200
    assert await response.json() == load_json(
        'check_order_response_simple.json',
    )

    assert check_mock1.times_called == 1
    assert check_mock2.times_called == 1


@pytest.mark.pgsql('persey_payments', files=['check_order_simple.sql'])
async def test_mark(
        taxi_persey_payments_web, mock_trust_check_basket, load_json,
):
    check_mock = mock_trust_check_basket(
        load_json('check_basket_simple.json')['first'],
    )

    response = await taxi_persey_payments_web.post(
        '/v1/order/check', json={'order_id': 'some_order', 'mark': 'main'},
    )

    assert response.status == 200

    data = await response.json()
    assert [b['mark'] for b in data['baskets']] == ['main']
    assert check_mock.times_called == 1


@pytest.mark.pgsql('persey_payments', files=['check_order_simple.sql'])
async def test_mark_not_found(
        taxi_persey_payments_web, mock_trust_check_basket,
):
    response = await taxi_persey_payments_web.post(
        '/v1/order/check',
        json={'order_id': 'some_order', 'mark': 'nonexistent'},
    )

    assert response.status == 200
    assert await response.json() == {'baskets': []}


async def test_not_found(taxi_persey_payments_web):
    response = await taxi_persey_payments_web.post(
        '/v1/order/check', json={'order_id': 'nonexistent'},
    )

    assert response.status == 404
    assert await response.json() == {
        'code': 'ORDER_NOT_FOUND',
        'message': 'No order_id=nonexistent in db',
    }
