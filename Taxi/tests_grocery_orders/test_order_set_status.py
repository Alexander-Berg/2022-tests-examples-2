import pytest

from . import headers
from . import models


@pytest.mark.parametrize(
    'status',
    # No 'draft' status as it is default for order in testsuite
    ['checked_out', 'canceled', 'assembling', 'delivering', 'closed'],
)
async def test_200(taxi_grocery_orders, pgsql, status):
    order = models.Order(pgsql=pgsql)
    prev_order_version = 1
    order.upsert(order_version=prev_order_version)

    response = await taxi_grocery_orders.post(
        '/lavka/v1/orders/v1/set-status',
        json={
            'order_id': order.order_id,
            'order_version': 1,
            'status': status,
        },
        headers=headers.DEFAULT_HEADERS,
    )
    assert response.status_code == 200

    order.update()
    assert order.status == status
    assert order.order_version == prev_order_version + 1


async def test_409(taxi_grocery_orders, pgsql):
    prev_status = 'checked_out'
    request_version = 5
    new_status = 'canceled'

    order = models.Order(pgsql=pgsql)
    order.upsert(order_version=request_version, status=prev_status)

    response = await taxi_grocery_orders.post(
        '/lavka/v1/orders/v1/set-status',
        json={
            'order_id': order.order_id,
            'order_version': request_version + 1,
            'status': new_status,
        },
        headers=headers.DEFAULT_HEADERS,
    )
    assert response.status_code == 409

    order.update()
    assert order.status == prev_status
    assert order.order_version == request_version


async def test_404(taxi_grocery_orders, pgsql):
    order = models.Order(pgsql=pgsql)
    order.upsert(order_version=2)

    response = await taxi_grocery_orders.post(
        '/lavka/v1/orders/v1/set-status',
        json={
            'order_id': order.order_id + '-xxx',
            'order_version': 1,
            'status': 'canceled',
        },
        headers=headers.DEFAULT_HEADERS,
    )
    assert response.status_code == 404


async def test_idempotency(taxi_grocery_orders, pgsql):
    order = models.Order(pgsql=pgsql)
    request_version = 5
    already_in_pg_version = request_version + 1
    status = 'checked_out'
    order.upsert(order_version=already_in_pg_version, status=status)

    response = await taxi_grocery_orders.post(
        '/lavka/v1/orders/v1/set-status',
        json={
            'order_id': order.order_id,
            'order_version': request_version,
            'status': status,
        },
        headers=headers.DEFAULT_HEADERS,
    )
    assert response.status_code == 200

    order.update()
    assert order.status == status
    assert order.order_version == already_in_pg_version
