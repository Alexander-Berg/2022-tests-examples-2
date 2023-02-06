import pytest

async def test_done_to_error(tap, dataset, api):
    with tap.plan(11, 'Закрытие саджеста в ошибку'):
        store = await dataset.store()
        tap.ok(store, 'склад создан')

        user = await dataset.user(role='executer', store=store)
        tap.eq(user.store_id, store.store_id, 'пользователь создан')

        order = await dataset.order(store=store,
                                    users=[user.user_id],
                                    status='processing',
                                    estatus='waiting')
        tap.eq((order.store_id, order.fstatus, order.users),
               (store.store_id, ('processing', 'waiting'), [user.user_id]),
               'заказ создан')

        suggest = await dataset.suggest(order, type='check_more')
        tap.eq((suggest.type, suggest.order_id, suggest.status),
               ('check_more', order.order_id, 'request'),
               'саджест создан')

        t = await api(user=user)

        await t.post_ok('api_tsd_order_done_check_more',
                        json={
                            'suggest_id': suggest.suggest_id,
                            'status': 'error',
                        })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('suggests.0', 'Suggest present')

        tap.ok(await suggest.reload(), 'Перегружен')
        tap.eq(suggest.status, 'error', 'Статус проставлен error')
        tap.eq(suggest.reason.code, 'PRODUCT_ABSENT', 'Код ризона')


async def test_done(tap, dataset, api):
    with tap.plan(10, 'Нормальное закрытие саджеста'):
        store = await dataset.store()
        tap.ok(store, 'склад создан')

        user = await dataset.user(role='executer', store=store)
        tap.eq(user.store_id, store.store_id, 'пользователь создан')

        order = await dataset.order(store=store,
                                    users=[user.user_id],
                                    status='processing',
                                    estatus='waiting')
        tap.eq((order.store_id, order.fstatus, order.users),
               (store.store_id, ('processing', 'waiting'), [user.user_id]),
               'заказ создан')

        suggest = await dataset.suggest(order, type='check_more')
        tap.eq((suggest.type, suggest.order_id, suggest.status),
               ('check_more', order.order_id, 'request'),
               'саджест создан')

        product = await dataset.product()
        tap.ok(product, 'товар создан')


        t = await api(user=user)

        await t.post_ok('api_tsd_order_done_check_more',
                        json={
                            'suggest_id': suggest.suggest_id,
                            'count': 35,
                            'product_id': product.product_id,
                        })
        t.status_is(200, diag=True)
        t.json_has('suggests.0', 'Suggest present')
        tap.ok(await suggest.reload(), 'перегружен')
        tap.eq_ok(suggest.user_done, user.user_id, 'user_done')


@pytest.mark.parametrize('what', ['product_id', 'count'])
async def test_done_err(tap, dataset, api, what):
    with tap.plan(7, f'отсутствует {what} в запросе'):
        store = await dataset.store()
        tap.ok(store, 'склад создан')

        user = await dataset.user(role='executer', store=store)
        tap.eq(user.store_id, store.store_id, 'пользователь создан')

        order = await dataset.order(store=store,
                                    users=[user.user_id],
                                    status='processing',
                                    estatus='waiting')
        tap.eq((order.store_id, order.fstatus, order.users),
               (store.store_id, ('processing', 'waiting'), [user.user_id]),
               'заказ создан')

        suggest = await dataset.suggest(order, type='check_more')
        tap.eq((suggest.type, suggest.order_id, suggest.status),
               ('check_more', order.order_id, 'request'),
               'саджест создан')

        product = await dataset.product()
        tap.ok(product, 'товар создан')


        t = await api(user=user)

        req = {
            'suggest_id': suggest.suggest_id,
            'count': 35,
            'product_id': product.product_id,
        }

        del req[what]

        await t.post_ok('api_tsd_order_done_check_more', json=req)
        t.status_is(400, diag=True)


async def test_done_weight(tap, dataset, api):
    with tap.plan(10, 'Нормальное закрытие саджеста с весом'):
        store = await dataset.store()
        tap.ok(store, 'склад создан')

        user = await dataset.user(role='executer', store=store)
        tap.eq(user.store_id, store.store_id, 'пользователь создан')

        order = await dataset.order(store=store,
                                    users=[user.user_id],
                                    status='processing',
                                    estatus='waiting')
        tap.eq((order.store_id, order.fstatus, order.users),
               (store.store_id, ('processing', 'waiting'), [user.user_id]),
               'заказ создан')

        suggest = await dataset.suggest(order, type='check_more')
        tap.eq((suggest.type, suggest.order_id, suggest.status),
               ('check_more', order.order_id, 'request'),
               'саджест создан')

        product = await dataset.product()
        tap.ok(product, 'товар создан')


        t = await api(user=user)

        await t.post_ok('api_tsd_order_done_check_more',
                        json={
                            'suggest_id': suggest.suggest_id,
                            'weight': 35,
                            'product_id': product.product_id,
                        })
        t.status_is(200, diag=True)
        t.json_has('suggests.0', 'Suggest present')
        tap.ok(await suggest.reload(), 'перегружен')
        tap.eq_ok(suggest.user_done, user.user_id, 'user_done')


async def test_done_product_no_stocks(tap, dataset, api):
    with tap.plan(6, 'Закрытие саджеста на продукт без остатка'):
        store = await dataset.store(options={'exp_condition_zero': False})
        user = await dataset.user(role='executer', store=store)
        order = await dataset.order(
            store=store,
            users=[user.user_id],
            status='processing',
            estatus='waiting',
            type='check_more'
        )
        shelf = await dataset.shelf(store=store)
        suggest = await dataset.suggest(order, type='check_more', shelf=shelf)
        product = await dataset.product()

        t = await api(user=user)
        payload = {
            'suggest_id': suggest.suggest_id,
            'count': 35,
            'product_id': product.product_id,
        }

        await t.post_ok(
            'api_tsd_order_done_check_more',
            json=payload
        )
        t.status_is(400, diag=True)
        t.json_is('code', 'ER_SUGGEST_WRONG_PRODUCT_ID')

        another_shelf = await dataset.shelf(store=store)
        await dataset.stock(
            product=product, store=store, count=0, shelf=another_shelf)

        await t.post_ok(
            'api_tsd_order_done_check_more',
            json=payload
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
