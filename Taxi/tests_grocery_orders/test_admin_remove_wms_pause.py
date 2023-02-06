from . import models


async def test_basic(
        taxi_grocery_orders, pgsql, grocery_depots, grocery_wms_gateway,
):
    order = models.Order(pgsql=pgsql, status='assembling')
    grocery_depots.add_depot(legacy_depot_id=order.depot_id)

    request = {'order_id': order.order_id}
    response = await taxi_grocery_orders.post(
        '/admin/orders/v1/actions/remove-assemble-pause', json=request,
    )
    assert response.status == 200
    assert grocery_wms_gateway.times_set_pause_called() == 1

    order.check_order_history('wms_pause', {'type': 'resume'})


async def test_bad_revision(taxi_grocery_orders, pgsql, grocery_depots):
    order = models.Order(pgsql=pgsql, status='assembling', order_revision=1)
    grocery_depots.add_depot(legacy_depot_id=order.depot_id)

    request = {'order_id': order.order_id, 'order_revision': 0}
    response = await taxi_grocery_orders.post(
        '/admin/orders/v1/actions/remove-assemble-pause', json=request,
    )
    assert response.status == 400


async def test_wms_409(
        taxi_grocery_orders, pgsql, grocery_depots, grocery_wms_gateway,
):
    order = models.Order(pgsql=pgsql, status='assembling')
    grocery_depots.add_depot(legacy_depot_id=order.depot_id)
    grocery_wms_gateway.set_http_resp(
        '{"code": "WMS_409", "message": "Not allowed"}', 409,
    )

    request = {'order_id': order.order_id}
    response = await taxi_grocery_orders.post(
        '/admin/orders/v1/actions/remove-assemble-pause', json=request,
    )
    assert response.status == 200

    order.check_order_history('wms_pause', {'type': 'resume'})
