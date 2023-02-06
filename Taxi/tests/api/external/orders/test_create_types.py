# pylint: disable=unused-variable

import pytest
from stall.model.order import Order


@pytest.mark.parametrize('order_type', ['order', 'shipment'])
async def test_create(tap, dataset, uuid, api, order_type):
    with tap.plan(16, order_type):
        t = await api(role='token:web.external.tokens.0')

        store = await dataset.store()
        product1 = await dataset.product()
        product2 = await dataset.product()

        stock1 = await dataset.stock(product=product1, store=store, count=1000)
        stock2 = await dataset.stock(product=product2, store=store, count=2000)

        external_id = uuid()

        await t.post_ok('api_external_orders_create',
                        json={
                            'external_id': external_id,
                            'required': [
                                {
                                    'product_id': product1.product_id,
                                    'count': 100,
                                },
                                {
                                    'product_id': product2.product_id,
                                    'count': 200,
                                }
                            ],
                            'store_id': store.store_id,
                            'approved': True,
                            'client_id': 'some_client_id',
                        })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'код')

        t.json_is('order.store_id', store.store_id, 'store_id')
        t.json_is('order.external_id', external_id, 'external_id в ответе')
        t.json_is('order.status', 'reserving', 'резервируется')

        order = await Order.load(t.res['json']['order']['order_id'])
        tap.ok(order, 'ордер загружен')

        tap.eq(len(order.required), 2, 'Товары в required')
        tap.eq(order.required[0].product_id, product1.product_id, 'product_id')
        tap.eq(order.required[0].count, 100, 'количество')
        tap.eq(order.required[1].product_id, product2.product_id, 'product_id')
        tap.eq(order.required[1].count, 200, 'количество')

        tap.ok(order.approved, 'Подтвержден')

        tap.ok(order.attr.get('doc_date'), 'doc_date is set')
        tap.ok(order.attr.get('doc_number'), 'doc_number is set')
        tap.eq(order.attr.get('client_id'), 'some_client_id', 'client_id')
