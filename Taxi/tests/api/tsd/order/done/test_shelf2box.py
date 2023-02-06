import pytest
from libstall.util import now
from stall.model.suggest import Suggest


async def test_done(tap, dataset, api):
    with tap.plan(16, 'Завершение саджеста по заказу'):
        user = await dataset.user(role='barcode_executer')
        tap.ok(user, 'пользователь сгенерирован')

        order = await dataset.order(
            status='processing',
            estatus='waiting',
            store_id=user.store_id,
            users=[user.user_id],
        )

        tap.ok(order, 'ордер сгенерирован')
        tap.eq(order.estatus, 'waiting', 'ожидает действий пользователя')
        tap.eq(order.status, 'processing', 'и выполняется')
        tap.eq(order.store_id, user.store_id, 'на складе')

        suggest = await dataset.suggest(order, type='shelf2box')
        tap.ok(suggest, 'подсказка сгенерирована')
        tap.eq(suggest.type, 'shelf2box', 'тип')
        tap.ok(suggest.count, 'количество есть')

        t = await api(user=user)
        await t.post_ok('api_tsd_order_done_shelf2box',
                        json={
                            'suggest_id': suggest.suggest_id
                        })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('message', 'Suggest was done.')
        t.json_has('suggests.0', 'Suggest present')

        tap.ok(await suggest.reload(), 'саджест перегружен')
        tap.eq(suggest.status, 'done', 'саджест завершён')
        tap.eq_ok(suggest.user_done, user.user_id, 'user_done')


async def test_done_count(tap, dataset, api, wait_order_status):
    with tap.plan(12, 'Завершение саджеста по заказу'):
        product = await dataset.product(valid=10)
        store   = await dataset.store()
        user    = await dataset.user(store=store, role='barcode_executer')

        shelf   = await dataset.shelf(store=store, type='store')
        await dataset.shelf(store=store, type='trash')

        await dataset.stock(
            store=store,
            shelf=shelf,
            product=product,
            count=10,
            valid='2020-01-01',
        )

        order = await dataset.order(
            store=store,
            type = 'check_valid_short',
            status='reserving',
            estatus='begin',
            approved=now(),
            acks=[user.user_id],
            required = [],
        )
        await wait_order_status(order, ('processing', 'waiting'))

        suggests = await Suggest.list_by_order(order)
        tap.eq(len(suggests), 1, 'Список саджестов')
        suggest = suggests[0]

        t = await api(user=user)
        await t.post_ok('api_tsd_order_done_shelf2box',
                        json={
                            'suggest_id': suggest.suggest_id,
                            'count': 5,
                        })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('message', 'Suggest was done.')
        t.json_has('suggests.0', 'Suggest present')

        with await suggest.reload() as suggest:
            tap.ok(await suggest.reload(), 'саджест перегружен')
            tap.eq(suggest.status, 'done', 'саджест завершён')
            tap.eq(suggest.count, 10, 'count')
            tap.eq(suggest.result_count, 5, 'result_count')
            tap.eq_ok(suggest.user_done, user.user_id, 'user_done')


async def test_done_repeat(tap, dataset, api):
    with tap.plan(22, 'Завершение саджеста по заказу'):
        user = await dataset.user(role='barcode_executer')
        tap.ok(user, 'пользователь сгенерирован')

        order = await dataset.order(
            status='processing',
            estatus='waiting',
            store_id=user.store_id,
            users=[user.user_id],
        )

        tap.ok(order, 'ордер сгенерирован')
        tap.eq(order.estatus, 'waiting', 'ожидает действий пользователя')
        tap.eq(order.status, 'processing', 'и выполняется')
        tap.eq(order.store_id, user.store_id, 'на складе')

        suggest = await dataset.suggest(order, type='shelf2box')
        tap.ok(suggest, 'подсказка сгенерирована')
        tap.eq(suggest.type, 'shelf2box', 'тип')
        tap.ok(suggest.count, 'количество есть')

        for attemt in range(1, 3):
            t = await api(user=user)
            await t.post_ok('api_tsd_order_done_shelf2box',
                            json={
                                'suggest_id': suggest.suggest_id
                            })
            t.status_is(200, diag=True, desc=f'attemt: {attemt}')
            t.json_is('code', 'OK')
            t.json_is('message', 'Suggest was done.')

            tap.ok(await suggest.reload(), 'саджест перегружен')
            tap.eq(suggest.status, 'done', 'саджест завершён')
            tap.eq_ok(suggest.user_done, user.user_id, 'user_done')


@pytest.mark.parametrize('nf_count', [1, 10, 22])
async def test_error(tap, dataset, api, nf_count):
    with tap.plan(15, 'Завершение саджеста с ошибкой PRODUCT_ABSENT'):
        user = await dataset.user(role='barcode_executer')
        tap.ok(user, 'пользователь сгенерирован')

        order = await dataset.order(
            status='processing',
            estatus='waiting',
            store_id=user.store_id,
            users=[user.user_id],
        )

        tap.ok(order, 'ордер сгенерирован')
        tap.eq(order.estatus, 'waiting', 'ожидает действий пользователя')
        tap.eq(order.status, 'processing', 'и выполняется')
        tap.eq(order.store_id, user.store_id, 'на складе')

        suggest = await dataset.suggest(order, type='shelf2box', count=22)
        tap.ok(suggest, 'подсказка сгенерирована')
        tap.eq(suggest.type, 'shelf2box', 'тип')
        tap.ok(suggest.count, 'количество есть')

        t = await api(user=user)
        await t.post_ok('api_tsd_order_done_shelf2box',
                        json={
                            'suggest_id': suggest.suggest_id,
                            'status': 'error',
                            'reason': {
                                'code': 'PRODUCT_ABSENT',
                                'count': nf_count
                            }
                        })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('message', 'Suggest was done.')

        tap.ok(await suggest.reload(), 'саджест перегружен')
        tap.eq(suggest.status, 'error', 'саджест завершён')
        tap.eq(suggest.reason,
               {'code': 'PRODUCT_ABSENT', 'count': nf_count},
               'reason')


@pytest.mark.parametrize('nf_count', [23])
async def test_error_400(tap, dataset, api, nf_count):
    with tap.plan(12, 'Слишком большое значение count в reason'):
        user = await dataset.user(role='barcode_executer')
        tap.ok(user, 'пользователь сгенерирован')

        order = await dataset.order(
            status='processing',
            estatus='waiting',
            store_id=user.store_id,
            users=[user.user_id],
        )

        tap.ok(order, 'ордер сгенерирован')
        tap.eq(order.estatus, 'waiting', 'ожидает действий пользователя')
        tap.eq(order.status, 'processing', 'и выполняется')
        tap.eq(order.store_id, user.store_id, 'на складе')

        suggest = await dataset.suggest(order, type='shelf2box', count=22)
        tap.ok(suggest, 'подсказка сгенерирована')
        tap.eq(suggest.type, 'shelf2box', 'тип')
        tap.ok(suggest.count, 'количество есть')

        t = await api(user=user)
        await t.post_ok('api_tsd_order_done_shelf2box',
                        json={
                            'suggest_id': suggest.suggest_id,
                            'status': 'error',
                            'reason': {
                                'code': 'PRODUCT_ABSENT',
                                'count': nf_count
                            }
                        })
        t.status_is(400, diag=True)
        t.json_is('code', 'ER_BAD_REQUEST')
        t.json_is('message', 'reason.count > suggest.count')


@pytest.mark.parametrize('nf_count', [1])
async def test_error_repeat(tap, dataset, api, nf_count):
    with tap.plan(22, 'Повтор саджеста с ошибкой PRODUCT_ABSENT'):
        user = await dataset.user(role='barcode_executer')
        tap.ok(user, 'пользователь сгенерирован')

        order = await dataset.order(
            status='processing',
            estatus='waiting',
            store_id=user.store_id,
            users=[user.user_id],
        )

        tap.ok(order, 'ордер сгенерирован')
        tap.eq(order.estatus, 'waiting', 'ожидает действий пользователя')
        tap.eq(order.status, 'processing', 'и выполняется')
        tap.eq(order.store_id, user.store_id, 'на складе')

        suggest = await dataset.suggest(order, type='shelf2box', count=22)
        tap.ok(suggest, 'подсказка сгенерирована')
        tap.eq(suggest.type, 'shelf2box', 'тип')
        tap.ok(suggest.count, 'количество есть')

        t = await api(user=user)
        for attemt in range(1, 3):
            await t.post_ok('api_tsd_order_done_shelf2box',
                            json={
                                'suggest_id': suggest.suggest_id,
                                'status': 'error',
                                'reason': {
                                    'code': 'PRODUCT_ABSENT',
                                    'count': nf_count
                                }
                            })
            t.status_is(200, diag=True, desc=f'Попытка {attemt}')
            t.json_is('code', 'OK')
            t.json_is('message', 'Suggest was done.')

            tap.ok(await suggest.reload(), 'саджест перегружен')
            tap.eq(suggest.status, 'error', 'саджест завершён')
            tap.eq(suggest.reason,
                   {'code': 'PRODUCT_ABSENT', 'count': nf_count},
                   'reason')


async def test_weight(tap, dataset, api):
    with tap.plan(12, 'Завершение саджеста с указанием weight'):
        user = await dataset.user(role='barcode_executer')
        tap.ok(user, 'пользователь сгенерирован')

        order = await dataset.order(
            status='processing',
            estatus='waiting',
            store_id=user.store_id,
            users=[user.user_id],
        )

        tap.ok(order, 'ордер сгенерирован')

        suggest = await dataset.suggest(
            order,
            type='shelf2box',
            weight=202,
        )
        tap.ok(suggest, 'подсказка сгенерирована')
        tap.eq(suggest.type, 'shelf2box', 'тип')
        tap.ok(suggest.weight, 'вес есть')

        t = await api(user=user)
        await t.post_ok('api_tsd_order_done_shelf2box',
                        json={
                            'suggest_id': suggest.suggest_id,
                            'weight': 101,
                        })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('message', 'Suggest was done.')
        t.json_has('suggests.0', 'Suggest present')
        t.json_is('suggests.0.weight', 202)
        t.json_is('suggests.0.result_weight', 101)


async def test_done_true_mark(tap, dataset, api, uuid):
    with tap.plan(14, 'Завершение марочного саджеста'):
        store = await dataset.store()
        user = await dataset.user(store=store)
        product_barcode = '1' + uuid()[:13]
        product = await dataset.product(barcode=[product_barcode])
        stock = await dataset.stock(store=store, count=10, product=product)
        order = await dataset.order(
            store=store,
            type='order',
            status='processing',
            estatus='waiting',
            required=[
                {
                    'product_id': stock.product_id,
                    'count': 2,
                }
            ],
            acks=[user.user_id],
            users=[user.user_id],

        )
        suggest_one = await dataset.suggest(
            type='shelf2box',
            order=order,
            conditions={'need_true_mark': True},
            product_id=stock.product_id,
            shelf_id=stock.shelf_id,
            count=1,
        )
        t = await api(user=user)
        await t.post_ok(
            'api_tsd_order_done_shelf2box',
            json={
                'suggest_id': suggest_one.suggest_id,
                'status': 'done',
                'count': 1,
            },
        )
        t.status_is(400, diag=True)
        t.json_is('code', 'ER_SUGGEST_TRUE_MARK_REQUIRED')

        await t.post_ok(
            'api_tsd_order_done_shelf2box',
            json={
                'suggest_id': suggest_one.suggest_id,
                'status': 'done',
                'count': 1,
                'true_mark': '123456789',
            },
        )
        t.status_is(400, diag=True)
        t.json_is('code', 'ER_SUGGEST_INVALID_TRUE_MARK')

        true_mark = '0199999999999999215Qbag!\x1D93Zjqw'

        await t.post_ok(
            'api_tsd_order_done_shelf2box',
            json={
                'suggest_id': suggest_one.suggest_id,
                'status': 'done',
                'count': 1,
                'true_mark': true_mark,
            },
        )
        t.status_is(400, diag=True)
        t.json_is('code', 'ER_SUGGEST_WRONG_PRODUCT_TRUE_MARK')

        correct_true_mark_one = f'01{product_barcode}215Qbag!\x1D93Zjqw'
        await t.post_ok(
            'api_tsd_order_done_shelf2box',
            json={
                'suggest_id': suggest_one.suggest_id,
                'status': 'done',
                'count': 1,
                'true_mark': correct_true_mark_one,
            },
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        tap.ok(await suggest_one.reload(), 'Перезабрали саджест')

        tap.eq(
            suggest_one.vars('true_mark', None),
            correct_true_mark_one,
            'Марка нужная в саджесте',
        )
