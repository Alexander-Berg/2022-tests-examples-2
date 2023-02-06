import pytest

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

        suggest = await dataset.suggest(order, type='box2shelf')
        tap.ok(suggest, 'подсказка сгенерирована')
        tap.eq(suggest.type, 'box2shelf', 'тип')
        tap.ok(suggest.count, 'количество есть')

        t = await api(user=user)
        await t.post_ok('api_tsd_order_done_box2shelf',
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

        suggest = await dataset.suggest(order, type='box2shelf')
        tap.ok(suggest, 'подсказка сгенерирована')
        tap.eq(suggest.type, 'box2shelf', 'тип')
        tap.ok(suggest.count, 'количество есть')

        for attemt in range(1, 3):
            t = await api(user=user)
            await t.post_ok('api_tsd_order_done_box2shelf',
                            json={
                                'suggest_id': suggest.suggest_id
                            })
            t.status_is(200, diag=True, desc=f'attemt: {attemt}')
            t.json_is('code', 'OK')
            t.json_is('message', 'Suggest was done.')

            tap.ok(await suggest.reload(), 'саджест перегружен')
            tap.eq(suggest.status, 'done', 'саджест завершён')
            tap.eq_ok(suggest.user_done, user.user_id, 'user_done')


async def test_done_zero(tap, dataset, api):
    with tap.plan(36, 'Завершение саджеста по заказу'):
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

        suggest = await dataset.suggest(order, type='box2shelf', count=3)
        tap.ok(suggest, 'подсказка сгенерирована')
        tap.eq(suggest.type, 'box2shelf', 'тип')
        tap.ok(suggest.count, 'количество есть')

        for attemt in range(1, 3):
            t = await api(user=user)
            await t.post_ok('api_tsd_order_done_box2shelf',
                            json={
                                'suggest_id': suggest.suggest_id,
                                'count': 0,
                            })
            t.status_is(400, diag=True, desc=f'attemt: {attemt}')
            t.json_is('code', 'ER_SUGGEST_CONDITION_ALL')

            tap.ok(await suggest.reload(), 'саджест перегружен')
            tap.eq(suggest.status, 'request', 'саджест не завершён')
            tap.eq_ok(suggest.user_done, None, 'user_done')

        for attemt in range(1, 3):
            t = await api(user=user)
            await t.post_ok('api_tsd_order_done_box2shelf',
                            json={
                                'suggest_id': suggest.suggest_id,
                                'count': None,
                            })
            t.status_is(200, diag=True, desc=f'attemt: {attemt}')
            t.json_is('code', 'OK')
            t.json_is('message', 'Suggest was done.')
            t.json_has('suggests.0', 'Suggest present')

            tap.ok(await suggest.reload(), 'саджест перегружен')
            tap.eq(suggest.status, 'done', 'саджест завершён')
            tap.eq_ok(suggest.user_done, user.user_id, 'user_done')


@pytest.mark.parametrize('attempts', [1, 2])
@pytest.mark.parametrize('reason',
                         [
                             {'code': 'SHELF_IS_FULL'},
                             {'code': 'LIKE_SHELF', 'shelf_id': '123'}
                         ])
async def test_error(tap, dataset, api, reason, attempts):
    with tap.plan(8 + attempts * 7,     # 8 тестов до for, 7 тестов в for
                  f'Завершение саджеста с ошибкой {reason}'):
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

        suggest = await dataset.suggest(order, type='box2shelf', count=22)
        tap.ok(suggest, 'подсказка сгенерирована')
        tap.eq(suggest.type, 'box2shelf', 'тип')
        tap.ok(suggest.count, 'количество есть')

        shelf = await dataset.shelf(store_id=user.store_id)
        if reason.get('shelf_id'):
            reason['shelf_id'] = shelf.shelf_id

        t = await api(user=user)
        for attempt in range(attempts):
            await t.post_ok('api_tsd_order_done_box2shelf',
                            json={
                                'suggest_id': suggest.suggest_id,
                                'status': 'error',
                                'reason': reason,
                            },
                            desc=f'Запрос {attempt}')
            t.status_is(200, diag=True)
            t.json_is('code', 'OK')
            t.json_is('message', 'Suggest was done.')

            tap.ok(await suggest.reload(), 'саджест перегружен')
            tap.eq(suggest.status, 'error', 'саджест завершён')
            tap.eq(suggest.reason, reason, 'reason')


async def test_valid(tap, dataset, api):
    with tap.plan(12, 'Завершение саджеста с указанием valid'):
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
            type='box2shelf',
            valid='2019-12-15'
        )
        tap.ok(suggest, 'подсказка сгенерирована')
        tap.eq(suggest.type, 'box2shelf', 'тип')
        tap.ok(suggest.count, 'количество есть')

        t = await api(user=user)
        await t.post_ok('api_tsd_order_done_box2shelf',
                        json={
                            'suggest_id': suggest.suggest_id,
                            'valid': '1974-12-15',
                        })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('message', 'Suggest was done.')
        t.json_has('suggests.0', 'Suggest present')
        t.json_is('suggests.0.valid', '2019-12-15')
        t.json_is('suggests.0.result_valid', '1974-12-15')


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
            type='box2shelf',
            weight=202,
        )
        tap.ok(suggest, 'подсказка сгенерирована')
        tap.eq(suggest.type, 'box2shelf', 'тип')
        tap.ok(suggest.count, 'количество есть')

        t = await api(user=user)
        await t.post_ok('api_tsd_order_done_box2shelf',
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


async def test_product_id(tap, dataset, api):
    with tap.plan(14, 'Завершение саджеста с указанием product_id'):
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
            type='box2shelf',
            weight=202,
        )
        tap.ok(suggest, 'подсказка сгенерирована')
        tap.eq(suggest.type, 'box2shelf', 'тип')
        tap.ok(suggest.count, 'количество есть')

        cproduct = await dataset.product(parent_id=suggest.product_id)
        tap.ok(cproduct, 'дочерний товар создан')

        t = await api(user=user)
        await t.post_ok('api_tsd_order_done_box2shelf',
                        json={
                            'suggest_id': suggest.suggest_id,
                            'weight': 101,
                            'product_id': cproduct.product_id,
                        })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('message', 'Suggest was done.')
        t.json_has('suggests.0', 'Suggest present')
        t.json_is('suggests.0.weight', 202)
        t.json_is('suggests.0.result_weight', 101)
        t.json_is('suggests.0.product_id', cproduct.product_id)


async def test_count(tap, dataset, api):
    with tap.plan(12, 'Завершение саджеста с указанием count'):
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
            type='box2shelf',
            count=25,
            conditions={'all': True}
        )
        tap.ok(suggest, 'подсказка сгенерирована')

        t = await api(user=user)
        await t.post_ok('api_tsd_order_done_box2shelf',
                        json={
                            'suggest_id': suggest.suggest_id,
                            'count': 40,
                        })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('message', 'Suggest was done.')
        t.json_has('suggests.0', 'Suggest present')
        t.json_is('suggests.0.count', 25)
        t.json_is('suggests.0.result_count', 40)

        tap.ok(await suggest.reload(), 'Перезабрал саджест')

        tap.eq(suggest.result_count, 40, 'Установлен result_count')


async def test_count_invalid(tap, dataset, api):
    with tap.plan(7, 'Завершение саджеста с указанием невалидного count'):
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
            type='box2shelf',
            count=1000,
            conditions={'all': True}
        )
        tap.ok(suggest, 'подсказка сгенерирована')

        t = await api(user=user)
        await t.post_ok('api_tsd_order_done_box2shelf',
                        json={
                            'suggest_id': suggest.suggest_id,
                            'count': 0.7,
                        })
        t.status_is(400, diag=True)

        tap.ok(await suggest.reload(), 'Перезабрал саджест')

        tap.eq(suggest.result_count, None, 'result_count не проставлен')


@pytest.mark.parametrize(
    'params',
    [
        {
            'conditions':
                {
                    'all': False,
                },
            'done_count': 200,
            'error': 'ER_SUGGEST_CONDITION_ALL',
            'error_code': 400,
        },
        {
            'conditions':
                {
                    'all': True,
                    'editable':  False,
                },
            'status': 'done',
            'done_count': 400,
            'done_reason': {'code': 'CHANGE_COUNT'},
            'error': 'ER_SUGGEST_IS_NOT_EDITABLE',
            'error_code': 410,

        },
        {
            'conditions':
                {
                    'error': False,
                },

            'done_status': 'error',
            'done_reason': {'code': 'SHELF_IS_FULL'},
            'error': 'ER_SUGGEST_ERROR_DENIDED',
            'error_code': 400,

        },
        {
            'conditions':
                {
                    'need_valid': True,
                },
            'done_count': 1000,
            'error': 'ER_SUGGEST_VALID_REQUIRED',
            'error_code': 400,

        },
        {
            'conditions':
                {
                    'cancelable': False,
                },
            'done_status': 'cancel',
            'error': 'ER_SUGGEST_IS_NOT_CANCELABLE',
            'error_code': 400,

        },
        {
            'conditions':
                {
                    'all': True,
                    'max_count': True,
                },
            'done_count': 2000,
            'error': 'ER_SUGGEST_COUNT',
            'error_code': 400,

        },
        {
            'conditions':
                {
                    'all': True,
                    'editable':  True,
                    'trash_reason': True,
                },
            'done_count': 400,
            'done_reason':{'code': 'CHANGE_COUNT'},
            'error': 'ER_SUGGEST_REASON_REQUIRED',
            'error_code': 400,

        },

        {
            'conditions':
                {
                    'need_weight': True,
                },
            'error': 'ER_SUGGEST_WEIGHT_REQUIRED',
            'error_code': 400,

        },

    ]

)
async def test_error_conditions(tap, dataset, api, params):
    with tap.plan(6, 'Проверяем ошибки'):

        user = await dataset.user(role='barcode_executer')
        tap.ok(user, 'пользователь сгенерирован')
        order = await dataset.order(
            status='processing',
            estatus='waiting',
            store_id=user.store_id,
            users=[user.user_id],
        )

        tap.ok(order, 'ордер сгенерирован')
        status = params['status'] if 'status' in params else 'request'
        suggest = await dataset.suggest(
            order,
            status=status,
            type='box2shelf',
            count=1000,
            valid = None,
            conditions=params['conditions']
        )
        tap.ok(suggest, 'подсказка сгенерирована')

        t = await api(user=user)
        json = {
            'suggest_id': suggest.suggest_id,
        }
        if 'done_count' in params:
            json['count'] = params['done_count']
        if 'done_status' in params:
            json['status'] = params['done_status']
        if 'done_reason' in params:
            json['reason'] = params['done_reason']

        await t.post_ok(
            'api_tsd_order_done_box2shelf',
            json=json
        )
        t.status_is(params['error_code'], diag=True)
        t.json_is('code', params['error'])


async def test_done_true_mark(tap, dataset, api):
    with tap.plan(15, 'Завершение марочного саджеста'):
        store = await dataset.store()
        user = await dataset.user(store=store)
        product = await dataset.product(true_mark=True)
        another_product = await dataset.product(true_mark=True)
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
        correct_true_mark_one = await dataset.true_mark_value(product=product)
        to_box_suggest = await dataset.suggest(
            type='shelf2box',
            order=order,
            conditions={'need_true_mark': True},
            product_id=stock.product_id,
            shelf_id=stock.shelf_id,
            count=1,
            result_count=1,
            status='request',
        )
        tap.ok(
            await to_box_suggest.done(
                status='done',
                store_job_event=False,
                true_mark=correct_true_mark_one,
            ),
            'Успешно закрыли саджест'
        )
        suggest_one = await dataset.suggest(
            type='box2shelf',
            order=order,
            conditions={'need_true_mark': True},
            product_id=stock.product_id,
            shelf_id=stock.shelf_id,
            count=1,
        )
        t = await api(user=user)
        await t.post_ok(
            'api_tsd_order_done_box2shelf',
            json={
                'suggest_id': suggest_one.suggest_id,
                'status': 'done',
                'count': 1,
            },
        )
        t.status_is(400, diag=True)
        t.json_is('code', 'ER_SUGGEST_TRUE_MARK_REQUIRED')

        await t.post_ok(
            'api_tsd_order_done_box2shelf',
            json={
                'suggest_id': suggest_one.suggest_id,
                'status': 'done',
                'count': 1,
                'true_mark': '123456789',
            },
        )
        t.status_is(400, diag=True)
        t.json_is('code', 'ER_SUGGEST_INVALID_TRUE_MARK')

        true_mark = await dataset.true_mark_value(product=another_product)

        await t.post_ok(
            'api_tsd_order_done_box2shelf',
            json={
                'suggest_id': suggest_one.suggest_id,
                'status': 'done',
                'count': 1,
                'true_mark': true_mark,
            },
        )
        t.status_is(400, diag=True)
        t.json_is('code', 'ER_SUGGEST_WRONG_PRODUCT_TRUE_MARK')

        await t.post_ok(
            'api_tsd_order_done_box2shelf',
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
