import pytest


@pytest.mark.parametrize('order_type', ['acceptance', 'shipment'])
async def test_success(tap, dataset, api, order_type):
    with tap.plan(15, 'нормальный воркфлоу'):
        store = await dataset.store()
        product1 = await dataset.product()
        product2 = await dataset.product()

        order = await dataset.order(
            store=store,
            type=order_type,
            status='approving',
            estatus='begin',
        )

        order.attr = {
            'foo': 'bar',
            'upd_number': '777',
        }

        order.required = [
            {
                'product_id': product1.product_id,
            }
        ]

        await order.save()
        tap.eq(order.attr['foo'], 'bar', 'добавили поле в аттр')
        tap.eq(
            order.attr['upd_number'], '777', 'добавили еще поле, ',
        )

        t = await api(role='token:web.external.tokens.0')

        await t.post_ok(
            'api_integration_orders_update_order',
            json={
                'order_id': order.order_id,
                'attr': {
                    'upd_number': '123-abc',
                    'upd_date': '1970-01-01',
                    'total_wo_vat': '100.01',
                    'total_sum': '100.01',
                    'vat_sum': '20',
                    'invoice_number': '123',
                    'invoice_date': '1970-01-01',
                },
                'required': [
                    {
                        'product_id': product2.product_id,
                    }
                ]
            },
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('order')
        t.json_has('order.attr')
        t.json_is('order.attr.upd_number', '123-abc')
        t.json_is('order.attr.upd_date', '1970-01-01')
        t.json_is('order.attr.total_wo_vat', '100.01')
        t.json_is('order.attr.total_sum', '100.01')
        t.json_is('order.attr.vat_sum', '20')
        t.json_is('order.attr.invoice_number', '123')
        t.json_is('order.attr.invoice_date', '1970-01-01')
        t.json_is('order.required.0.product_id', product2.product_id)


@pytest.mark.parametrize('status', ['complete', 'processing', 'canceled'])
async def test_order_done(tap, dataset, api, status):
    with tap.plan(5, 'попытка изменить attr в уже завершенном документе'):
        store = await dataset.store()

        order = await dataset.order(
            store=store,
            type='acceptance',
            status=status,
        )

        tap.eq(order.type, 'acceptance', 'ордер приемки создан')

        order.attr = {
            'foo': 'bar',
            'upd_number': '777',
        }

        await order.save()
        tap.eq(order.attr['foo'], 'bar', 'добавили поле в аттр')

        t = await api(role='token:web.external.tokens.0')

        await t.post_ok(
            'api_integration_orders_update_order',
            json={
                'order_id': order.order_id,
                'attr': {
                    'upd_number': '123-abc',
                },
            },
        )
        t.status_is(400, diag=True)
        t.json_is('code', 'ER_BAD_REQUEST')


async def test_no_parameters(tap, dataset, api):
    with tap.plan(5, 'не передаем параметры'):
        store = await dataset.store()

        order = await dataset.order(
            store=store,
            type='acceptance',
            status='approving',
            estatus='begin',
        )

        tap.eq(order.type, 'acceptance', 'ордер приемки создан')

        order.attr = {
            'foo': 'bar',
            'upd_number': '777',
        }

        await order.save()
        tap.eq(order.attr['foo'], 'bar', 'добавили поле в аттр')

        t = await api(role='token:web.external.tokens.0')

        await t.post_ok(
            'api_integration_orders_update_order',
            json={
                'order_id': order.order_id,
            },
        )
        t.status_is(400, diag=True)
        t.json_is('code', 'ER_BAD_REQUEST')
