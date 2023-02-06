import pytest

from stall.model.order import Order


async def test_update_invoice(tap, dataset, uuid, api):
    with tap.plan(6):
        t = await api(role='token:web.external.tokens.0')


        order = await dataset.order(attr={'hello': 'medved'})
        tap.ok(order, 'ордер создан')

        number = uuid()

        await t.post_ok('api_external_orders_update_data',
                        json={
                            'store_id': order.store_id,
                            'external_id': order.external_id,
                            'invoices': [
                                {
                                    'invoice_number': number,
                                    'invoice_sum': '123.34',
                                    'invoice_date':
                                        '2018-01-02T23:54:45+03:00',
                                    'invoice_type': 'payment',
                                }
                            ]
                        })
        t.status_is(200, diag=True)
        t.json_is('order.attr.hello', 'medved')
        t.json_is('order.attr.invoices.0.invoice_number', number)
        t.json_is('order.order_id', order.order_id)


async def test_update_invoice_nv(tap, dataset, uuid, api):
    with tap.plan(4):
        t = await api(role='token:web.external.tokens.0')


        order = await dataset.order(attr={'hello': 'medved'})
        tap.ok(order, 'ордер создан')

        number = uuid()

        await t.post_ok('api_external_orders_update_data',
                        json={
                            'store_id': order.store_id,
                            'external_id': uuid(),
                            'invoices': [
                                {
                                    'invoice_number': number,
                                    'invoice_sum': '123.34',
                                    'invoice_date':
                                        '2018-01-02T23:54:45+03:00',
                                    'invoice_type': 'payment',
                                }
                            ]
                        })
        t.status_is(404, diag=True)
        t.json_is('message', 'Order not found')

@pytest.mark.skip(reason="Решили пока эту проверку убрать")
async def test_update_invoice_complete(tap, dataset, uuid, api):
    with tap.plan(4):
        t = await api(role='token:web.external.tokens.0')


        order = await dataset.order(status='complete')
        tap.eq(order.status, 'complete', 'ордер создан')

        await t.post_ok('api_external_orders_update_data',
                        json={
                            'store_id': order.store_id,
                            'external_id': order.external_id,
                            'invoices': [
                                {
                                    'invoice_number': uuid(),
                                    'invoice_sum': '123.34',
                                    'invoice_date':
                                        '2018-01-02T23:54:45+03:00',
                                    'invoice_type': 'payment',
                                }
                            ]
                        })
        t.status_is(410, diag=True)
        t.json_is('message', 'Order status is already "complete"')


async def test_update_cart_data(tap, dataset, api):
    with tap:
        t = await api(role='token:web.external.tokens.0')

        order = await dataset.order()
        tap.ok(order, 'ордер создан')
        tap.ok('external_order_revision' not in order.attr,
               'external_order_revision is not set')

        async def process_update(order_, external_order_revision_):
            json_data = {
                'store_id': order_.store_id,
                'external_id': order_.external_id,
            }
            if external_order_revision_:
                json_data['external_order_revision'] = external_order_revision_

            await t.post_ok('api_external_orders_update_data', json=json_data)
            t.status_is(200, diag=True)
            t.json_is('code', 'OK', 'код ОК')

            return t.res['json']['order']['order_id']

        external_order_revision = 'v1'
        order_id = await process_update(order, external_order_revision)
        result_order = await Order.load(order_id)
        tap.ok('external_order_revision' in result_order.vars,
               'external_order_revision is set')
        tap.eq(result_order.vars['external_order_revision'],
               external_order_revision,
               f'external_order_revision = "{external_order_revision}"')

        external_order_revision = 'v2'
        order_id = await process_update(order, external_order_revision)
        result_order = await Order.load(order_id)
        tap.ok('external_order_revision' in result_order.vars,
               'external_order_revision is set')
        tap.eq(result_order.vars['external_order_revision'],
               external_order_revision,
               f'external_order_revision = "{external_order_revision}"')

        # Не указываем external_order_revision – он должен остаться старым
        order_id = await process_update(order, None)
        result_order = await Order.load(order_id)
        tap.ok('external_order_revision' in result_order.vars,
               'external_order_revision is set')
        tap.eq(result_order.vars['external_order_revision'],
               external_order_revision,
               f'external_order_revision = "{external_order_revision}"')
