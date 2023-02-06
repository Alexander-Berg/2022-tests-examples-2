import pytest


async def test_done_unknown(tap, api, uuid):
    with tap.plan(2):
        t = await api(role='executer')

        await t.post_ok('api_tsd_order_change_status',
                        json={'order_id': uuid()})
        t.status_is(403, diag=True)


async def test_done_no_processing(tap, api, dataset):
    with tap.plan(8):
        user = await dataset.user(role='barcode_executer')
        tap.ok(user, 'пользователь создан')

        order = await dataset.order(status='complete',
                                    store_id=user.store_id,
                                    users=[user.user_id])
        tap.ok(order, 'ордер создан')
        tap.eq(order.store_id, user.store_id, 'на складе')
        tap.ok(order.status, 'complete', 'статус')

        t = await api(user=user)
        await t.post_ok('api_tsd_order_change_status',
                        json={'order_id': order.order_id})
        t.status_is(410, diag=True)
        t.json_is('code', 'ER_GONE')
        t.json_is('message', 'Order is not processing')


async def test_done_complete(tap, api, dataset, wait_order_status):
    with tap.plan(14, 'Есть незавершённые саджесты'):
        user = await dataset.user(role='barcode_executer')
        tap.ok(user, 'пользователь создан')

        order = await dataset.order(status='processing',
                                    estatus='waiting',
                                    store_id=user.store_id,
                                    users=[user.user_id])
        tap.ok(order, 'ордер создан')
        tap.eq(order.store_id, user.store_id, 'на складе')
        tap.ok(order.status, 'complete', 'статус')

        suggest = await dataset.suggest(order, type='box2shelf', status='done')
        tap.ok(suggest, 'саджест сгенерирован')
        tap.eq(suggest.order_id, order.order_id, 'заказ')
        tap.eq(suggest.type, 'box2shelf', 'тип')
        tap.eq(suggest.status, 'done', 'выполнен')

        t = await api(user=user)
        await t.post_ok('api_tsd_order_change_status',
                        json={'order_id': order.order_id})
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('message', 'Status change request accepted')
        t.json_is('order.order_id', order.order_id)

        await wait_order_status(order, ('complete', 'done'))


# pylint: disable=invalid-name
async def test_order_check_from_proc_to_failed(
        tap, api, dataset, wait_order_status
):
    with tap.plan(11, 'перед failed & reason'):
        user = await dataset.user(role='barcode_executer')
        tap.ok(user, 'пользователь создан')

        order = await dataset.order(
            type='check_product_on_shelf',
            status='processing',
            estatus='begin',
            store_id=user.store_id,
            users=[user.user_id],
        )
        tap.ok(order, 'ордер создан')
        tap.eq(order.type, 'check_product_on_shelf', 'тип ордера')
        tap.eq(order.store_id, user.store_id, 'на складе')
        tap.eq(order.fstatus, ('processing', 'begin'), 'статус')

        suggest = await dataset.suggest(order, type='check', status='request')
        tap.ok(suggest, 'саджест сгенерирован')
        tap.eq(suggest.order_id, order.order_id, 'заказ')

        t = await api(user=user)
        await t.post_ok(
            'api_tsd_order_change_status',
            json={
                'order_id': order.order_id,
                'status': 'failed',
                'reason': 'comment',
                'comment': '11',
            }
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        await wait_order_status(order, ('failed', 'done'))


async def test_done_status(tap, api, dataset):
    with tap.plan(10, 'Передача температуры при закрытии'):
        user = await dataset.user(role='barcode_executer')
        tap.ok(user, 'пользователь создан')

        order = await dataset.order(
            type='check_product_on_shelf',
            status='processing',
            estatus='waiting',
            store_id=user.store_id,
            users=[user.user_id],
            attr={'hello': 'world'},
        )
        tap.ok(order, 'ордер создан')
        tap.eq(order.store_id, user.store_id, 'на складе')
        tap.ok(order.status, 'complete', 'статус')

        t = await api(user=user)
        await t.post_ok(
            'api_tsd_order_change_status',
            json={
                'order_id': order.order_id,
                'status': 'complete',
                'attr': {'truck_temperature': 123},
            }
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        tap.ok(await order.reload(), 'перегружен')
        tap.eq(order.attr['hello'], 'world', 'старый attr')
        tap.eq(
            order.attr['complete'],
            {'truck_temperature': 123},
            'температура'
        )


async def test_done_tp_inventory(tap, api, dataset):
    with tap.plan(8, 'Закрытие инвентаризации только WMS'):
        user = await dataset.user(role='admin')
        tap.ok(user, 'пользователь создан')

        order = await dataset.order(
            type='inventory_check_more',
            status='processing',
            estatus='waiting',
            store_id=user.store_id,
            users=[user.user_id],
            vars={'third_party_assistance': True}
        )
        tap.ok(order, 'ордер создан')
        tap.eq(order.store_id, user.store_id, 'на складе')

        t = await api(user=user)
        await t.post_ok(
            'api_tsd_order_change_status',
            json={
                'order_id': order.order_id,
                'status': 'complete',
            }
        )
        t.status_is(400, diag=True)
        t.json_is('code', 'ER_WMS_ONLY_ORDER')

        tap.ok(await order.reload(), 'перегружен')
        tap.eq(order.user_done, None, 'Пользователь не проставлен')


async def test_redone(tap, api, dataset):
    with tap.plan(6, 'Повторная передача заказа с done'):
        user = await dataset.user(role='barcode_executer')
        tap.ok(user, 'пользователь создан')

        order = await dataset.order(
            type='check_product_on_shelf',
            status='complete',
            estatus='done',
            store_id=user.store_id,
            users=[user.user_id],
            attr={'hello': 'world'},
        )
        tap.ok(order, 'ордер создан')
        tap.eq(order.store_id, user.store_id, 'на складе')
        tap.ok(order.status, 'complete', 'статус')

        t = await api(user=user)
        await t.post_ok(
            'api_tsd_order_change_status',
            json={
                'order_id': order.order_id,
                'status': 'complete',
            }
        )
        t.status_is(410, diag=True)


async def test_redone_other_user(tap, api, dataset):
    with tap.plan(6, 'Повторная передача заказа с done другим пользовталем'):
        user = await dataset.user(role='barcode_executer')
        user2 = await dataset.user(role='barcode_executer')

        tap.ok(user, 'пользователь создан')

        order = await dataset.order(
            type='check_product_on_shelf',
            status='complete',
            estatus='done',
            store_id=user.store_id,
            users=[user.user_id],
            attr={'hello': 'world'},
        )
        tap.ok(order, 'ордер создан')
        tap.eq(order.store_id, user.store_id, 'на складе')
        tap.ok(order.status, 'complete', 'статус')

        t = await api(user=user2)
        await t.post_ok(
            'api_tsd_order_change_status',
            json={
                'order_id': order.order_id,
                'status': 'complete',
            }
        )
        t.status_is(403, diag=True)


async def test_weight_stowage_complete(tap, api, dataset, now):
    with tap.plan(23, 'закрытие weight_stowage'):
        store = await dataset.full_store(
            options={'exp_chicken_run': True}
        )

        user = await dataset.user(store=store, role='admin')
        tap.ok(user, 'пользователь создан')

        products = await dataset.weight_products()
        tap.ok(products, 'товары созданы')

        order = await dataset.order(
            type='weight_stowage',
            store=store,
            status='processing',
            estatus='waiting',
            approved=now(),
            acks=[user.user_id],
            required=[
                {
                    'product_id': products[0].product_id,
                    'weight': 5000,
                    'count': 10,
                }
            ],
        )
        tap.ok(order, 'ордер создан')

        t = await api(user=user)
        await t.post_ok('api_tsd_order_change_status',
                        json={
                            'order_id': order.order_id,
                            'status': 'complete'
                        })
        t.status_is(409, diag=True)
        t.json_is('code', 'ER_CONFLICT')
        t.json_is('message', 'Not all products are placed')

        suggest = await dataset.suggest(
            order,
            type='box2shelf',
            status='done',
            result_count=10,
        )
        tap.ok(suggest, 'саджест создан')
        await t.post_ok('api_tsd_order_change_status',
                        json={
                            'order_id': order.order_id,
                            'status': 'complete'
                        })
        t.status_is(409, diag=True)
        t.json_is('code', 'ER_CONFLICT')
        t.json_is('message', 'The order stage is not final')

        order.vars['stage'] = 'trash'
        tap.ok(await order.save(), 'stage = trash')

        await t.post_ok('api_tsd_order_change_status',
                        json={
                            'order_id': order.order_id,
                            'status': 'complete'
                        })
        t.status_is(409, diag=True)
        t.json_is('code', 'ER_INCOMPLETE_SUGGESTS')
        t.json_is('message',
                  'No done shelf2box suggests with '
                  'request_count=0, result_weight=0')

        suggest = await dataset.suggest(
            order, type='shelf2box', status='done',
            result_count=0, result_weight=0
        )
        tap.ok(suggest, 'саджест сгенерирован')

        await t.post_ok('api_tsd_order_change_status',
                        json={
                            'order_id': order.order_id,
                            'status': 'complete'
                        })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('message', 'Status change request accepted')
        t.json_is('order.order_id', order.order_id)


async def test_weight_no_exp_chicken_run(tap, api, dataset, now):
    with tap.plan(10, 'закрытие weight_stowage'):
        store = await dataset.full_store()

        user = await dataset.user(store=store, role='admin')
        tap.ok(user, 'пользователь создан')

        products = await dataset.weight_products()
        tap.ok(products, 'товары созданы')

        order = await dataset.order(
            type='weight_stowage',
            store=store,
            status='processing',
            estatus='waiting',
            approved=now(),
            acks=[user.user_id],
            required=[
                {
                    'product_id': products[0].product_id,
                    'weight': 5000,
                    'count': 10,
                }
            ],
        )
        tap.ok(order, 'ордер создан')

        suggest = await dataset.suggest(
            order,
            type='box2shelf',
            status='done',
            result_count=10,
        )
        tap.ok(suggest, 'саджест создан')

        suggest = await dataset.suggest(
            order, type='shelf2box', status='done',
            result_count=0, result_weight=0
        )
        tap.ok(suggest, 'саджест сгенерирован')

        t = await api(user=user)
        await t.post_ok('api_tsd_order_change_status',
                        json={
                            'order_id': order.order_id,
                            'status': 'complete'
                        })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('message', 'Status change request accepted')
        t.json_is('order.order_id', order.order_id)


@pytest.mark.parametrize('order_type', ['sale_stowage', 'check_valid_short'])
async def test_no_request_sugg_complete(
        tap, api, dataset, now, order_type):
    with tap.plan(16, f'закрытие {order_type}'):
        store = await dataset.full_store()
        tap.ok(store, 'склад создан')

        user = await dataset.user(store=store, role='admin')
        tap.eq(user.store_id, store.store_id, 'пользователь создан')

        order = await dataset.order(
            store=store,
            type=order_type,
            status='processing',
            estatus='waiting',
            acks=[user.user_id],
            approved=now(),
        )
        tap.eq(order.store_id, store.store_id, 'ордер создан')

        t = await api(user=user)
        await t.post_ok('api_tsd_order_change_status',
                        json={
                            'order_id': order.order_id,
                            'status': 'complete'
                        })
        t.status_is(409, diag=True)
        t.json_is('code', 'ER_CONFLICT')
        t.json_is('message', 'The order stage is not final')

        order.vars['stage'] = 'trash'
        tap.ok(await order.save(), 'stage = trash')

        suggest = await dataset.suggest(
            order, type='check', status='request'
        )
        tap.ok(suggest, 'саджест сгенерирован')

        await t.post_ok('api_tsd_order_change_status',
                        json={
                            'order_id': order.order_id,
                            'status': 'complete'
                        })
        t.status_is(409, diag=True)
        t.json_is('code', 'ER_INCOMPLETE_SUGGESTS')
        t.json_is('message', 'Some suggests have to be done')

        tap.ok(await suggest.done(), 'завершён саджест')

        await t.post_ok('api_tsd_order_change_status',
                        json={
                            'order_id': order.order_id,
                            'status': 'complete'
                        })
        t.status_is(200, diag=True, desc='При закрытых саджестах всё ок')


async def test_visual_control_complete(tap, api, dataset):
    with tap.plan(19, 'закрытие visual_control'):
        store = await dataset.full_store()

        user = await dataset.user(store=store, role='admin')
        tap.ok(user, 'пользователь создан')

        order = await dataset.order(
            store=store,
            type='visual_control',
            status='processing',
            estatus='waiting',
            acks=[user.user_id]
        )
        tap.ok(order, 'ордер создан')

        suggest_box2shelf = await dataset.suggest(
            order, type='box2shelf', status='request'
        )
        tap.ok(suggest_box2shelf, 'саджест box2shelf сгенерирован')

        t = await api(user=user)
        await t.post_ok('api_tsd_order_change_status',
                        json={
                            'order_id': order.order_id,
                            'status': 'complete'
                        })
        t.status_is(409, diag=True)
        t.json_is('code', 'ER_CONFLICT')
        t.json_is('message', 'The order stage is not final')

        order.vars['stage'] = 'trash'
        tap.ok(await order.save(), 'stage = trash')

        await t.post_ok('api_tsd_order_change_status',
                        json={
                            'order_id': order.order_id,
                            'status': 'complete'
                        })
        t.status_is(409, diag=True)
        t.json_is('code', 'ER_INCOMPLETE_SUGGESTS')
        t.json_is('message',
                  'Some box2shelf suggests still in request. '
                  'Close all request suggests.')

        tap.ok(await suggest_box2shelf.done(), 'завершён box2shelf саджест')
        suggest_box2shelf = await dataset.suggest(
            order, type='shelf2box', status='request'
        )
        tap.ok(suggest_box2shelf, 'саджест shelf2box сгенерирован')

        await t.post_ok('api_tsd_order_change_status',
                        json={
                            'order_id': order.order_id,
                            'status': 'complete'
                        })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('message', 'Status change request accepted')
        t.json_is('order.order_id', order.order_id)


async def test_done_paused(tap, api, dataset):
    with tap.plan(7, 'если заказ на паузе, то не разрешаем закрыть'):
        user = await dataset.user(role='barcode_executer')

        order = await dataset.order(
            status='processing',
            estatus='waiting',
            store_id=user.store_id,
            users=[user.user_id],
        )

        order.set_paused_until(30)
        await order.save()
        tap.ok(order.paused_until, 'выставлена пауза')

        t = await api(user=user)

        await t.post_ok(
            'api_tsd_order_change_status',
            json={
                'order_id': order.order_id,
                'status': 'complete',
            }
        )
        t.status_is(409, diag=True)
        t.json_is('code', 'ER_ORDER_PAUSED')

        order.set_paused_until(0)
        await order.save()

        await t.post_ok(
            'api_tsd_order_change_status',
            json={
                'order_id': order.order_id,
                'status': 'complete',
            }
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')


async def test_sale_stowage_done(tap, dataset, api, wait_order_status):
    with tap.plan(25, 'проверяем check_done в раскладке'):
        store = await dataset.full_store(options={'exp_freegan_party': True})
        trash_shelf = await dataset.Shelf.get_one(
            store_id=store.store_id, type='trash'
        )
        user = await dataset.user(store=store)
        product = await dataset.product()
        order = await dataset.order(
            store=store,
            type='sale_stowage',
            acks=[user.user_id],
            required=[{'product_id': product.product_id, 'count': 23}],
        )
        await wait_order_status(order, ('processing', 'waiting'))
        suggests = await dataset.Suggest.list_by_order(order)
        tap.eq(len(suggests), 1, 'один саджест')
        tap.ok(
            await suggests[0].done(
                status='error',
                reason={
                    'code': 'LIKE_SHELF',
                    'shelf_id': trash_shelf.shelf_id,
                },
            ),
            'закрыли саджест в ошибку с LIKE_SHELF'
        )
        await wait_order_status(order, ('processing', 'waiting'))

        t = await api(user=user)
        await t.post_ok(
            'api_tsd_order_change_status',
            json={
                'order_id': order.order_id,
                'status': 'complete',
            },
        )
        t.status_is(409)
        t.json_is('code', 'ER_INCOMPLETE_SUGGESTS')
        t.json_is('message', 'Some suggests have to be done')
        suggests = await dataset.Suggest.list_by_order(order)
        tap.eq(len(suggests), 1, 'один саджест')
        tap.ok(await suggests[0].done(count=23), 'все списываем')

        await t.post_ok(
            'api_tsd_order_change_status',
            json={
                'order_id': order.order_id,
                'status': 'complete',
            },
        )
        t.status_is(200)
        t.json_is('code', 'OK')
        store_options = store.options.copy()
        store_options['exp_freegan_party'] = False
        store.options = store_options
        await store.save()
        await store.reload()
        tap.ok(not store.options['exp_freegan_party'], 'выключили эксперимент')

        await t.post_ok(
            'api_tsd_order_change_status',
            json={
                'order_id': order.order_id,
                'status': 'complete',
            },
        )
        t.status_is(409)
        t.json_is('code', 'ER_CONFLICT')
        t.json_is('message', 'The order stage is not final')
        tap.ok(await order.signal({'type': 'sale_stowage'}), 'сигнал послан')
        await wait_order_status(order, ('processing', 'close_signal'))
        await wait_order_status(order, ('processing', 'waiting'))
        await order.reload()
        order.user_done = None
        await order.save()
        tap.eq(order.vars('stage'), 'trash', 'стадия списания')

        await t.post_ok(
            'api_tsd_order_change_status',
            json={
                'order_id': order.order_id,
                'status': 'complete',
            },
        )
        t.status_is(200)
        t.json_is('code', 'OK')
