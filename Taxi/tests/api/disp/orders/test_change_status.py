# pylint: disable=unused-variable
import pytest

async def test_done_unknown(tap, api, uuid):
    with tap.plan(2):
        t = await api(role='admin')

        await t.post_ok(
            'api_disp_orders_change_status',
            json={'order_id': uuid(), 'status': 'complete'},
        )
        t.status_is(403, diag=True)


async def test_done_no_processing(tap, api, dataset):
    with tap.plan(3, 'Завершение возможно только во время выполнения'):

        store = await dataset.store()
        user = await dataset.user(store=store, role='admin')

        order = await dataset.order(
            store=store,
            status='request',
            users=[user.user_id],
        )

        t = await api(user=user)
        await t.post_ok(
            'api_disp_orders_change_status',
            json={'order_id': order.order_id, 'status': 'complete'},
        )
        t.status_is(400, diag=True)
        t.json_is('code', 'ER_ORDER_IS_NOT_PROCESSING')


async def test_complete(tap, api, dataset, wait_order_status, now):
    with tap.plan(7, 'Завершение заказа'):

        store = await dataset.store()
        user = await dataset.user(store=store, role='admin')

        product = await dataset.product()
        stock   = await dataset.stock(store=store, product=product, count=100)

        order = await dataset.order(
            store=store,
            acks=[user.user_id],
            approved=now(),
            required = [
                {'product_id': product.product_id, 'count': 10},
            ],
        )

        await wait_order_status(order, ('processing', 'waiting'))

        t = await api(user=user)
        await t.post_ok(
            'api_disp_orders_change_status',
            json={'order_id': order.order_id, 'status': 'complete'},
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('message', 'Status change request accepted')
        t.json_is('order.order_id', order.order_id)

        await wait_order_status(order, ('complete', 'done'), user_done=user)


async def test_failed(tap, api, dataset, wait_order_status, now):
    with tap.plan(7, 'Срыв заказа'):

        store = await dataset.store()
        user = await dataset.user(store=store, role='admin')

        product = await dataset.product()
        stock   = await dataset.stock(store=store, product=product, count=100)

        order = await dataset.order(
            store=store,
            acks=[user.user_id],
            approved=now(),
            required = [
                {'product_id': product.product_id, 'count': 10},
            ],
        )

        await wait_order_status(order, ('processing', 'waiting'))

        t = await api(user=user)
        await t.post_ok(
            'api_disp_orders_change_status',
            json={
                'order_id': order.order_id,
                'status': 'failed',
                'reason': 'comment',
                'comment': 'test failed',
            },
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('message', 'Status change request accepted')
        t.json_is('order.order_id', order.order_id)

        await wait_order_status(order, ('failed', 'done'))


async def test_production(tap, dataset, api, now, wait_order_status, cfg):
    with tap.plan(4, 'Только в тестинге'):

        cfg.set('mode', 'production')

        store   = await dataset.store()
        user    = await dataset.user(store=store)

        product = await dataset.product()
        stock   = await dataset.stock(store=store, product=product, count=100)

        order = await dataset.order(
            store=store,
            acks=[user.user_id],
            approved=now(),
            required = [
                {'product_id': product.product_id, 'count': 10},
            ],
        )

        await wait_order_status(order, ('processing', 'waiting'))

        t = await api(user=user)
        await t.post_ok(
            'api_disp_orders_change_status',
            json={
                'order_id': order.order_id,
                'status': 'complete',
            },
        )
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_TESTING_ONLY')


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
        await t.post_ok('api_disp_orders_change_status',
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
        await t.post_ok('api_disp_orders_change_status',
                        json={
                            'order_id': order.order_id,
                            'status': 'complete'
                        })
        t.status_is(409, diag=True)
        t.json_is('code', 'ER_CONFLICT')
        t.json_is('message', 'The order stage is not final')

        order.vars['stage'] = 'trash'
        tap.ok(await order.save(), 'stage = trash')

        await t.post_ok('api_disp_orders_change_status',
                        json={
                            'order_id': order.order_id,
                            'status': 'complete'
                        })
        t.status_is(409, diag=True)
        t.json_is('code', 'ER_INCOMPLETE_SUGGESTS')
        t.json_is('message',
                  'No done shelf2box suggests with '
                  'request_count=0, result_weight=0'
                  )

        suggest = await dataset.suggest(
            order, type='shelf2box', status='done',
            result_count=0, result_weight=0
        )
        tap.ok(suggest, 'саджест сгенерирован')

        await t.post_ok('api_disp_orders_change_status',
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
        await t.post_ok('api_disp_orders_change_status',
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

        await t.post_ok('api_disp_orders_change_status',
                        json={
                            'order_id': order.order_id,
                            'status': 'complete'
                        })
        t.status_is(409, diag=True)
        t.json_is('code', 'ER_INCOMPLETE_SUGGESTS')
        t.json_is('message', 'Some suggests have to be done')

        tap.ok(await suggest.done(), 'завершён саджест')

        await t.post_ok('api_disp_orders_change_status',
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
        await t.post_ok('api_disp_orders_change_status',
                        json={
                            'order_id': order.order_id,
                            'status': 'complete'
                        })
        t.status_is(409, diag=True)
        t.json_is('code', 'ER_CONFLICT')
        t.json_is('message', 'The order stage is not final')

        order.vars['stage'] = 'trash'
        tap.ok(await order.save(), 'stage = trash')

        await t.post_ok('api_disp_orders_change_status',
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

        await t.post_ok('api_disp_orders_change_status',
                        json={
                            'order_id': order.order_id,
                            'status': 'complete'
                        })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('message', 'Status change request accepted')
        t.json_is('order.order_id', order.order_id)
