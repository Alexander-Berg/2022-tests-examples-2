import pytest

from tests_grocery_order_log import models


@pytest.mark.parametrize(
    'order_id,short_order_id',
    [('order_id', 'short_order_id'), ('order_id', None)],
)
async def test_basic(taxi_grocery_order_log, pgsql, order_id, short_order_id):
    index = models.OrderLogIndex(
        pgsql, order_id=order_id, short_order_id=short_order_id,
    )
    index.update_db()

    request_id = short_order_id
    if request_id is None:
        request_id = order_id

    request = {'order_id': request_id}

    response = await taxi_grocery_order_log.get(
        '/internal/orders/v1/get-order-id', params=request,
    )

    assert response.status_code == 200
    assert response.json()['order_id'] == index.order_id


async def test_not_found(taxi_grocery_order_log):
    request = {'order_id': 'order_id'}

    response = await taxi_grocery_order_log.get(
        '/internal/orders/v1/get-order-id', params=request,
    )
    assert response.status_code == 404
