from . import models


def enable_manual_update(experiments3, enable: bool):
    experiments3.add_config(
        name='grocery_orders_enable_manual_update',
        consumers=['grocery-orders/submit'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[
            {
                'title': 'Always enabled',
                'predicate': {'type': 'true'},
                'value': {'enabled': enable},
            },
        ],
    )


async def test_manual_update_not_enabled(
        taxi_grocery_orders, pgsql, experiments3,
):
    order = models.Order(pgsql=pgsql)

    enable_manual_update(experiments3, False)

    response = await taxi_grocery_orders.post(
        '/lavka/v1/orders/v1/manual-update',
        json={'order_id': order.order_id, 'status': 'delivering'},
    )
    assert response.status_code == 500


async def test_order_not_found(taxi_grocery_orders, pgsql, experiments3):
    order = models.Order(pgsql=pgsql)

    enable_manual_update(experiments3, True)

    response = await taxi_grocery_orders.post(
        '/lavka/v1/orders/v1/manual-update',
        json={'order_id': order.order_id + 'not-real', 'status': 'delivering'},
    )
    assert response.status_code == 404


async def test_update_order(taxi_grocery_orders, pgsql, experiments3):
    assembling_status = 'assembled'
    order = models.Order(
        pgsql=pgsql,
        state=models.OrderState(assembling_status=assembling_status),
    )

    enable_manual_update(experiments3, True)

    new_status = 'delivering'
    new_wms_reserve_status = 'success'
    new_driver_id = '1337'
    response = await taxi_grocery_orders.post(
        '/lavka/v1/orders/v1/manual-update',
        json={
            'order_id': order.order_id,
            'status': new_status,
            'wms_reserve_status': {'value': new_wms_reserve_status},
            'performer_info': {'driver_id': {'value': new_driver_id}},
        },
    )
    assert response.status_code == 200

    order.update()

    assert order.status == new_status
    assert order.state.wms_reserve_status == new_wms_reserve_status
    assert order.dispatch_performer.driver_id == new_driver_id
    assert order.manual_update_enabled

    # неуказанные поля не трогаются
    assert order.state.assembling_status == assembling_status


async def test_update_with_null(taxi_grocery_orders, pgsql, experiments3):
    assembling_status = 'assembled'
    order = models.Order(
        pgsql=pgsql,
        state=models.OrderState(assembling_status=assembling_status),
    )

    enable_manual_update(experiments3, True)

    response = await taxi_grocery_orders.post(
        '/lavka/v1/orders/v1/manual-update',
        json={'order_id': order.order_id, 'assembling_status': {}},
    )
    assert response.status_code == 200

    order.update()

    assert order.state.assembling_status is None
