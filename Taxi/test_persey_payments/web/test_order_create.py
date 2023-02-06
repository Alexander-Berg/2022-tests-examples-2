import pytest


def get_order(pgsql):
    db = pgsql['persey_payments']

    cursor = db.cursor()
    cursor.execute(
        'SELECT order_id, payment_method_id, need_free '
        'FROM persey_payments.order',
    )

    rows = list(cursor)
    assert len(rows) == 1

    return rows[0]


@pytest.mark.parametrize(
    'status_code, error_message, need_free, payment',
    [
        (200, None, False, 'some_payment_method_id'),
        (200, None, True, None),
        (400, 'Missing payment_method_id on need_free=false', False, None),
        (
            400,
            'No need in payment_method_id on need_free=true',
            True,
            'some_payment_method_id',
        ),
    ],
)
async def test_simple(
        taxi_persey_payments_web,
        pgsql,
        status_code,
        error_message,
        need_free,
        payment,
):
    request_json = {'order_id': 'some_order', 'need_free': need_free}

    if payment is not None:
        request_json['payment_method_id'] = payment

    response = await taxi_persey_payments_web.post(
        '/v1/order/create', json=request_json,
    )

    assert response.status == status_code

    if status_code == 200:
        assert await response.json() == {}
        assert get_order(pgsql) == ('some_order', payment, need_free)
    else:
        assert await response.json() == {
            'code': 'INVALID_PAYMENT_INFO',
            'message': error_message,
        }


async def test_update(taxi_persey_payments_web, pgsql):
    response = await taxi_persey_payments_web.post(
        '/v1/order/create',
        json={
            'order_id': 'some_order',
            'payment_method_id': 'some_pmid',
            'need_free': False,
        },
    )

    assert response.status == 200
    assert await response.json() == {}
    assert get_order(pgsql) == ('some_order', 'some_pmid', False)

    response = await taxi_persey_payments_web.post(
        '/v1/order/create',
        json={
            'order_id': 'some_order',
            'payment_method_id': 'another_pmid',
            'need_free': False,
        },
    )

    assert response.status == 200
    assert await response.json() == {}
    assert get_order(pgsql) == ('some_order', 'another_pmid', False)

    response = await taxi_persey_payments_web.post(
        '/v1/order/create', json={'order_id': 'some_order', 'need_free': True},
    )

    assert response.status == 200
    assert await response.json() == {}
    assert get_order(pgsql) == ('some_order', None, True)
