from datetime import datetime
import pytest

# pylint: disable=unused-variable


async def test_list_store(tap, dataset, api, uuid):
    with tap.plan(15, 'Получение заказов'):
        product1 = await dataset.product()
        product2 = await dataset.product()
        store   = await dataset.store()
        order1 = await dataset.order(
            store=store,
            required=[
                {'product_id': product1.product_id, 'count': 10},
                {'product_id': product2.product_id, 'count': 20},
            ],
        )

        t = await api(role='token:web.external.tokens.0')
        await t.post_ok(
            'api_external_orders_demand',
            json={'cursor': 'now', 'store_id': store.store_id},
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('cursor')
        t.json_hasnt('orders.0')

        cursor = t.res['json']['cursor']

        order2 = await dataset.order(
            store=store,
            required=[
                {'product_id': product1.product_id, 'count': 11},
                {'product_id': product2.product_id, 'count': 22},
            ],
            client_address = {'fullname': 'ТЕСТ'},
            courier = {
                'external_id': uuid(),
            }
        )

        t = await api(role='token:web.external.tokens.0')
        await t.post_ok(
            'api_external_orders_demand',
            json={'cursor': cursor, 'store_id': store.store_id},
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('cursor')
        t.json_is('orders.0.order_id', order2.order_id)
        t.json_is('orders.0.external_id', order2.external_id)
        t.json_is('orders.0.items_count', 11+22)
        t.json_is('orders.0.client_address.fullname', 'ТЕСТ')
        t.json_is('orders.0.courier_external_id', order2.courier.external_id)
        t.json_has('orders.0.delivery_status')


@pytest.mark.parametrize('order_params, expected_params', [
    (
        {
            'delivery_promise': datetime(2020, 10, 11),
        },
        {
            'delivery_promise': '2020-10-10T21:00:00+00:00',
            'delivery_eta': None,
        }
    ),
    (
        {
            'delivery_promise': datetime(2020, 10, 22, 15),
            'attr': {'delivery_eta': '2007-04-12T12:00:00+03:00'}
        },
        {
            'delivery_promise': '2020-10-22T12:00:00+00:00',
            'delivery_eta': '2007-04-12T12:00:00+03:00',
        }
    )
])
async def test_delivery_fields(
        dataset, tap, api, uuid, order_params, expected_params):
    with tap:
        store = await dataset.store()
        tap.ok(store, 'Склад создан')
        order = await dataset.order(
            store=store,
            required=[
                {'product_id': uuid(), 'count': 22},
            ],
            **order_params
        )
        tap.ok(order, 'Заказ создан')

        t = await api(role='token:web.external.tokens.0')
        await t.post_ok(
            'api_external_orders_demand',
            json={'cursor': None, 'store_id': store.store_id},
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        tap.eq(len(t.res['json']['orders']), 1, 'Один заказ')

        t.json_is('orders.0.order_id', order.order_id)
        for key, value in expected_params.items():
            t.json_is(f'orders.0.{key}', value)


async def test_list_hotload(tap, dataset, api, cfg):
    cfg.set('business.order.order.demand_hotload', 1)

    with tap.plan(11, 'Получение заказов hotload'):
        product1 = await dataset.product()
        product2 = await dataset.product()
        store   = await dataset.store()
        order1 = await dataset.order(
            store=store,
            required=[
                {'product_id': product1.product_id, 'count': 10},
                {'product_id': product2.product_id, 'count': 20},
            ],
        )

        t = await api(role='token:web.external.tokens.0')
        await t.post_ok(
            'api_external_orders_demand',
            json={
                'cursor': 'hotload',
                'store_id': store.store_id
            },
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('cursor')
        t.json_hasnt('orders.0')

        cursor = t.res['json']['cursor']

        t = await api(role='token:web.external.tokens.0')
        await t.post_ok(
            'api_external_orders_demand',
            json={'cursor': cursor, 'store_id': store.store_id},
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('cursor')
        t.json_has('orders')

        tap.in_ok(
            order1.order_id,
            {o['order_id'] for o in t.res['json']['orders']},
            'Ордер присутствует в выдаче'
        )
