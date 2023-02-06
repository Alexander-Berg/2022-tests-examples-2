import pytest


async def test_signal(tap, dataset, api):
    with tap.plan(7, 'штатная отправка сигнала'):
        store = await dataset.store(estatus='inventory')
        tap.ok(store, 'склад создан')
        tap.eq(store.estatus, 'inventory', 'в режиме инвентаризации')

        user = await dataset.user(store=store)
        tap.eq(user.store_id, store.store_id, 'пользователь создан')

        order = await dataset.order(
            type='inventory',
            store=store,
            status='processing',
            estatus='waiting_signal',
        )
        tap.eq(order.store_id, store.store_id, 'ордер на складе создан')
        await dataset.order(
            type='inventory_check_product_on_shelf',
            store=store,
            status='complete',
            estatus='done',
            parent=[order.order_id]
        )

        t = await api(user=user)
        await t.post_ok('api_disp_orders_order_signal',
                        json={
                            'order_id': order.order_id,
                            'signal': 'inventory_done',
                        })
        t.status_is(200, diag=True)

        await order.reload()
        tap.eq(order.signals[0]['user_id'], user.user_id, 'user set')


async def test_inventory_done_child(tap, dataset, api):
    with tap.plan(6, 'ошибка из-за незавершенного дочернего'):
        store = await dataset.store(estatus='inventory')
        user = await dataset.user(store=store)

        order = await dataset.order(
            type='inventory',
            store=store,
            status='processing',
            estatus='waiting_signal',
        )
        tap.eq(order.store_id, store.store_id, 'ордер на складе создан')
        await dataset.order(
            type='inventory_check_product_on_shelf',
            store=store,
            status='complete',
            estatus='begin',
            parent=[order.order_id]
        )
        t = await api(user=user)
        await t.post_ok(
            'api_disp_orders_order_signal',
            json={
                'order_id': order.order_id,
                'signal': 'inventory_done',
            })
        t.status_is(423, diag=True)
        t.json_is('code', 'ER_ORDERS_IN_PROGRESS')

        tap.ok(await order.reload(), 'Обновили заказ')
        tap.ok(
            not [x for x in order.signals if x.type == 'inventory_done'],
            'Сигнал не сохранен'
        )


async def test_signal_access(tap, dataset, api):
    with tap.plan(6, 'отправка сигнала не в списке роли'):
        store = await dataset.store(estatus='inventory')
        tap.ok(store, 'склад создан')
        tap.eq(store.estatus, 'inventory', 'в режиме инвентаризации')

        user = await dataset.user(store=store)
        tap.eq(user.store_id, store.store_id, 'пользователь создан')

        order = await dataset.order(type='inventory', store=store)
        tap.eq(order.store_id, store.store_id, 'ордер на складе создан')

        t = await api(user=user)
        await t.post_ok('api_disp_orders_order_signal',
                        json={
                            'order_id': order.order_id,
                            'signal': 'test',
                        })
        t.status_is(403, diag=True)


async def test_signal_collected(tap, dataset, api):
    with tap.plan(8, 'отправка сигнала сollected'):
        store = await dataset.full_store()
        tap.ok(store, 'склад создан')

        user = await dataset.user(store=store)
        tap.eq(user.store_id, store.store_id, 'пользователь создан')

        product = await dataset.product()
        tap.ok(product, 'товар создан')

        order = await dataset.order(
            store=store,
            required=[
                {
                    'product_id': product.product_id,
                    'count': 124,
                }
            ],
            type='collect',
        )
        tap.eq(order.store_id, store.store_id, 'ордер создан')

        t = await api(user=user)
        await t.post_ok('api_disp_orders_order_signal',
                        json={
                            'order_id': order.order_id,
                            'signal': 'collected',
                        })
        t.status_is(200, diag=True)

        tap.ok(await order.reload(), 'перегружен')

        tap.ok(
            [s for s in order.signals if s.type == 'collected'],
            'сигнал в ордере есть'
        )


# pylint: disable=invalid-name
async def test_signal_collected_er_trylater(tap, dataset, api):
    with tap.plan(8, 'отправка сигнала сollected'):
        store = await dataset.full_store()
        tap.ok(store, 'склад создан')

        user = await dataset.user(store=store)
        tap.eq(user.store_id, store.store_id, 'пользователь создан')

        product = await dataset.product()
        tap.ok(product, 'товар создан')

        order = await dataset.order(
            store=store,
            required=[
                {
                    'product_id': product.product_id,
                    'count': 124,
                }
            ],
            type='collect',
        )
        tap.eq(order.store_id, store.store_id, 'ордер создан')

        order2 = await dataset.order(store=store, type='hand_move')
        tap.eq(order2.store_id, store.store_id, 'hand_move создан')

        t = await api(user=user)
        await t.post_ok('api_disp_orders_order_signal',
                        json={
                            'order_id': order.order_id,
                            'signal': 'collected',
                        })
        t.status_is(423, diag=True)
        t.json_is('code', 'ER_ORDERS_IN_PROGRESS')


@pytest.mark.parametrize('order_params, signal_type', [
    (
        {
            'vars': {
                'report': {},
                'third_party_assistance': True,
                'third_party_report_imported': True,
            },
            'status': 'processing',
            'type': 'inventory_check_more',
        },
        'inventory_approve',
    ),
    (
        {
            'vars': {
                'report': {
                    'shelf': {
                        'product': {
                            'tp_count': 11,
                            'count': 11,
                            'result_count': 11,
                        }
                    }
                },
                'third_party_assistance': True,
                'third_party_report_imported': True,
            },
            'status': 'processing',
            'type': 'inventory_check_more',
        },
        'inventory_approve',
    ),
    (
        {
            'vars': {
                'report': {
                    'shelf': {
                        'product': {
                            'tp_count': 12,
                            'count': 12,
                            'result_count': 13,
                        }
                    }
                },
                'third_party_assistance': True,
                'third_party_report_imported': True,
            },
            'status': 'processing',
            'type': 'inventory_check_more',
        },
        'inventory_recount',
    ),
    (
        {
            'vars': {
                'report': {
                    'shelf': {
                        'product': {
                            'tp_count': 12,
                            'count': 13,
                            'result_count': 12,
                        }
                    }
                },
                'third_party_assistance': True,
                'third_party_report_imported': True,
            },
            'status': 'processing',
            'type': 'inventory_check_product_on_shelf',
        },
        'inventory_approve',
    )
])
async def test_inventory_signal(tap, dataset, order_params, signal_type, api):
    with tap.plan(6, 'отправка сигналов inventory'):
        store = await dataset.store()
        user = await dataset.user(store=store)
        order = await dataset.order(store=store, **order_params)
        tap.ok(order, 'Ордер создан')
        t = await api(user=user)
        await t.post_ok(
            'api_disp_orders_order_signal',
            json={
                'order_id': order.order_id,
                'signal': signal_type,
            },
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        tap.ok(await order.reload(), 'Обновили заказ')
        tap.ok(
            [x for x in order.signals if x.type == signal_type],
            'Сигнал сохранен'
        )


@pytest.mark.parametrize('order_params, signal_type, expected_msg', [
    (
        {
            'vars': {'third_party_assistance': True},
            'status': 'complete',
            'type': 'inventory_check_more',
        },
        'inventory_recount',
        'Order is not processing',
    ),
    (
        {
            'status': 'processing',
            'type': 'inventory_check_more',
        },
        'inventory_snapshot',
        'Wrong signal for inventory: inventory_snapshot',
    ),
    (
        {
            'status': 'processing',
            'type': 'inventory_check_more',
        },
        'inventory_recount',
        'Wrong signal for inventory: inventory_recount',
    ),
    (
        {
            'vars': {'third_party_assistance': True},
            'status': 'processing',
            'type': 'inventory_check_more',
        },
        'inventory_recount',
        'Report is not generated yet',
    ),
    (
        {
            'vars': {
                'report': {
                    'shelf': {
                        'product': {
                            'tp_count': 12,
                            'count': 12,
                            'result_count': 12,
                        }
                    }
                },
                'third_party_assistance': True,
                'third_party_report_imported': True,
            },
            'status': 'processing',
            'type': 'inventory_check_product_on_shelf',
        },
        'inventory_recount',
        'No need to recount',
    ),
    (
        {
            'vars': {
                'report': {
                    'shelf': {
                        'product': {
                            'tp_count': 12,
                            'count': 12,
                            'result_count': 13,
                        }
                    }
                },
                'third_party_assistance': True,
                'third_party_report_imported': True,
            },
            'status': 'processing',
            'type': 'inventory_check_more',
        },
        'inventory_approve',
        'Difference in report',
    ),
    (
        {
            'vars': {
                'report': {},
                'third_party_assistance': True,
            },
            'status': 'processing',
            'type': 'inventory_check_more',
        },
        'inventory_approve',
        'Can\'t proceed without report imported',
    )
])
async def test_inventory_signal_err(
        tap, dataset, order_params, signal_type, api, expected_msg):
    with tap.plan(6, 'ошибка отправки сигналов inventory'):
        store = await dataset.store()
        user = await dataset.user(store=store)
        order = await dataset.order(store=store, **order_params)
        tap.ok(order, 'Ордер создан')
        t = await api(user=user)
        await t.post_ok(
            'api_disp_orders_order_signal',
            json={
                'order_id': order.order_id,
                'signal': signal_type,
            },
        )
        t.json_isnt('code', 'OK')
        t.json_is('message', expected_msg)

        tap.ok(await order.reload(), 'Обновили заказ')
        tap.ok(
            not [x for x in order.signals if x.type == signal_type],
            'Сигнал не сохранен'
        )


async def test_more_product_signal(tap, api, dataset, uuid, wait_order_status):
    with tap.plan(25, 'отправляем more_product'):
        store = await dataset.full_store(options={'exp_schrodinger': False})
        user = await dataset.user(role='admin', store=store)
        product = await dataset.product()
        order = await dataset.order(
            store=store,
            type='sale_stowage',
            status='processing',
        )

        await wait_order_status(order, ('processing', 'waiting'))

        sig_json = {
            'order_id': order.order_id,
            'signal': 'more_product',
        }
        t = await api(user=user)

        await t.post_ok('api_disp_orders_order_signal', json=sig_json)
        t.status_is(400)
        t.json_is('message', 'Product not found (more_product)')

        sig_json['data'] = {'product_id': product.product_id}
        await t.post_ok('api_disp_orders_order_signal', json=sig_json)
        t.status_is(200)

        store.options = {'exp_schrodinger': True}
        await store.save()
        await t.post_ok('api_disp_orders_order_signal', json=sig_json)
        t.status_is(400)
        t.json_is('message', 'Contractor not found (more_product)')

        parent_acc = await dataset.order(
            store=store, type='acceptance', attr={'contractor_id': uuid()}
        )
        order.parent = [parent_acc.order_id]
        await order.save()
        await t.post_ok('api_disp_orders_order_signal', json=sig_json)
        t.status_is(400)
        t.json_is('message', 'Assortment not found (more_product)')

        order.parent = []
        order.attr['contractor_id'] = uuid()
        await order.save()
        await t.post_ok('api_disp_orders_order_signal', json=sig_json)
        t.status_is(400)
        t.json_is('message', 'Assortment not found (more_product)')

        order.required = [{'product_id': product.product_id, 'count': 300}]
        await order.save()
        await t.post_ok('api_disp_orders_order_signal', json=sig_json)
        t.status_is(200)

        assortment = await dataset.assortment_contractor(
            store=store, contractor_id=order.attr['contractor_id']
        )
        order.required = []
        await order.save()
        await t.post_ok('api_disp_orders_order_signal', json=sig_json)
        t.status_is(400)
        t.json_is('message', 'Product not in assortment (more_product)')

        await dataset.assortment_contractor_product(
            assortment=assortment,
            product=product,
        )
        await t.post_ok('api_disp_orders_order_signal', json=sig_json)
        t.status_is(200)

        order = await dataset.order(
            store=store,
            type='sale_stowage',
            attr={'contractor_id': uuid(), 'ignore_assortment': True},
            status='processing',
        )
        await wait_order_status(order, ('processing', 'waiting'))

        sig_json['order_id'] = order.order_id
        await t.post_ok('api_disp_orders_order_signal', json=sig_json)
        t.status_is(200)


async def test_more_product_signal_child(
        tap, api, dataset, uuid, wait_order_status):
    with tap.plan(3, 'отправляем more_product с дочерним продуктом'):
        store = await dataset.full_store(options={'exp_schrodinger': True})
        user = await dataset.user(role='admin', store=store)
        parent_product = await dataset.product()
        product = await dataset.product(parent_id=parent_product.product_id)
        parent_acc = await dataset.order(
            store=store, type='acceptance', attr={'contractor_id': uuid()}
        )
        order = await dataset.order(
            store=store,
            type='sale_stowage',
            status='processing',
            parent=[parent_acc.order_id]
        )
        assortment = await dataset.assortment_contractor(
            store=store, contractor_id=parent_acc.attr['contractor_id']
        )
        await dataset.assortment_contractor_product(
            assortment=assortment,
            product=parent_product,
        )
        await wait_order_status(order, ('processing', 'waiting'))

        t = await api(user=user)
        await t.post_ok(
            'api_disp_orders_order_signal',
            json={
                'order_id': order.order_id,
                'signal': 'more_product',
                'data': {
                    'product_id': product.product_id,
                }
            }
        )
        t.status_is(200, diag=True)
