import datetime
import pytest
from libstall.util import now


@pytest.mark.parametrize('attempts', [1, 2, 3])
async def test_done_box2shelf(tap, dataset, api, attempts):
    with tap.plan(9 + 8 * attempts, 'Завершение саджеста по заказу'):
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

        suggest = await dataset.suggest(
            order,
            type='check',
            count=22,
            conditions={'all': True},
        )
        tap.ok(suggest, 'подсказка сгенерирована')
        tap.eq(suggest.type, 'check', 'тип')
        tap.ok(suggest.count, 'количество есть')
        tap.ok(suggest.valid, 'срок годности есть')

        for attempt in range(1, attempts + 1):
            t = await api(user=user)
            await t.post_ok('api_tsd_order_done_box2shelf',
                            json={
                                'suggest_id': suggest.suggest_id,
                                'valid': now().strftime('%F'),
                                'count': suggest.count - 1,
                            },
                            desc=f'done {attempt}')
            t.status_is(200, diag=True)
            t.json_is('code', 'OK')
            t.json_is('message', 'Suggest was done.')
            t.json_has('suggests.0', 'Suggest present')

            # valid = suggest.valid
            tap.ok(await suggest.reload(), 'саджест перегружен')
            tap.eq(suggest.status, 'done', 'саджест завершён')
            # TODO - как Рома пушнет - раскомментить
            # tap.eq(suggest.count, 21, 'количество')
            # tap.ne(suggest.valid, valid, 'Срок годности')
            tap.eq_ok(suggest.user_done, user.user_id, 'user_done')


@pytest.mark.parametrize('attempts', [1, 2, 3])
async def test_done_check(tap, dataset, api, attempts):
    with tap.plan(9 + 8 * attempts, 'Завершение саджеста по заказу'):
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

        suggest = await dataset.suggest(order, type='check', count=22)
        tap.ok(suggest, 'подсказка сгенерирована')
        tap.eq(suggest.type, 'check', 'тип')
        tap.ok(suggest.count, 'количество есть')
        tap.ok(suggest.valid, 'срок годности есть')

        for attempt in range(1, attempts + 1):
            t = await api(user=user)
            await t.post_ok('api_tsd_order_done_check',
                            json={
                                'suggest_id': suggest.suggest_id,
                                'valid': now().strftime('%F'),
                                'count': suggest.count - 1,
                            },
                            desc=f'done {attempt}')
            t.status_is(200, diag=True)
            t.json_is('code', 'OK')
            t.json_is('message', 'Suggest was done.')
            t.json_has('suggests.0', 'Suggest present')

            tap.ok(await suggest.reload(), 'саджест перегружен')
            tap.eq(suggest.status, 'done', 'саджест завершён')
            tap.eq_ok(suggest.user_done, user.user_id, 'user_done')


# pylint: disable=too-many-statements
async def test_done_check_repeat(tap, dataset, api):
    with tap.plan(47, 'Повторы/редактирование закрытия'):
        user = await dataset.user(role='barcode_executer')
        tap.ok(user, 'пользователь сгенерирован')
        new_valid = now().strftime('%F')

        order = await dataset.order(
            status='processing',
            estatus='waiting',
            store_id=user.store_id,
            users=[user.user_id],
        )

        tap.ok(order, 'ордер сгенерирован')
        tap.eq(order.fstatus, ('processing', 'waiting'), 'и выполняется')
        tap.eq(order.store_id, user.store_id, 'на складе')

        suggest = await dataset.suggest(
            order,
            type='check',
            count=22,
            conditions={'all': True, 'editable': True}
        )
        tap.ok(suggest, 'подсказка сгенерирована')
        tap.eq(suggest.status, 'request', 'статус')
        tap.eq(suggest.type, 'check', 'тип')
        tap.ok(suggest.count, 'количество есть')
        tap.ok(suggest.valid, 'срок годности есть')
        tap.ne(suggest.valid.strftime('%F'), new_valid, 'Дата годности')

        t = await api(user=user)
        await t.post_ok('api_tsd_order_done_check',
                        json={
                            'suggest_id': suggest.suggest_id,
                            'valid': new_valid,
                            'count': suggest.count - 1,
                        })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('message', 'Suggest was done.')
        t.json_has('suggests.0', 'Suggest present')

        tap.ok(await suggest.reload(), 'перегружен')
        tap.eq(suggest.status, 'done', 'закрыт')
        tap.eq(suggest.result_valid.strftime('%F'), new_valid, 'valid изменён')
        tap.eq(suggest.result_count, suggest.count - 1, 'количество')
        tap.eq_ok(suggest.user_done, user.user_id, 'user_done')


        new_valid = (now() + datetime.timedelta(days=5)).strftime('%F')

        await t.post_ok('api_tsd_order_done_check',
                        json={
                            'suggest_id': suggest.suggest_id,
                            'valid': new_valid,
                            'count': suggest.count - 3,
                            'reason': {
                                'code': 'CHANGE_COUNT_VALID',
                            }
                        })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('message', 'Suggest was done.')

        tap.ok(await suggest.reload(), 'перегружен')
        tap.eq(suggest.status, 'done', 'закрыт')
        tap.eq_ok(suggest.user_done, user.user_id, 'user_done')
        tap.eq(suggest.result_valid.strftime('%F'), new_valid, 'valid изменён')
        tap.eq(suggest.result_count, suggest.count - 3, 'количество')


        new_valid2 = (now() + datetime.timedelta(days=5)).strftime('%F')
        await t.post_ok('api_tsd_order_done_check',
                        json={
                            'suggest_id': suggest.suggest_id,
                            'valid': new_valid2,
                            'count': suggest.count - 10,
                            'reason': {
                                'code': 'CHANGE_COUNT',
                            }
                        })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('message', 'Suggest was done.')

        tap.ok(await suggest.reload(), 'перегружен')
        tap.eq(suggest.status, 'done', 'закрыт')
        tap.eq_ok(suggest.user_done, user.user_id, 'user_done')
        tap.eq(suggest.result_valid.strftime('%F'), new_valid, 'valid остался')
        tap.eq(suggest.result_count, suggest.count - 10, 'количество')


        await t.post_ok('api_tsd_order_done_check',
                        json={
                            'suggest_id': suggest.suggest_id,
                            'valid': new_valid2,
                            'count': suggest.count - 1,
                            'reason': {
                                'code': 'CHANGE_VALID',
                            }
                        })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('message', 'Suggest was done.')

        tap.ok(await suggest.reload(), 'перегружен')
        tap.eq(suggest.status, 'done', 'закрыт')
        tap.eq_ok(suggest.user_done, user.user_id, 'user_done')
        tap.eq(suggest.result_valid.strftime('%F'),
               new_valid2,
               'valid поменялся')
        tap.eq(suggest.result_count,
               suggest.count - 10,
               'количество не изменилось')


@pytest.mark.parametrize('weight', [101, None])
async def test_weight(tap, dataset, api, weight):
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
            type='check',
            weight=202,
        )
        tap.ok(suggest, 'подсказка сгенерирована')
        tap.eq(suggest.type, 'check', 'тип')
        tap.ok(suggest.count, 'количество есть')

        t = await api(user=user)
        await t.post_ok('api_tsd_order_done_check',
                        json={
                            'suggest_id': suggest.suggest_id,
                            'weight': weight,
                        })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('message', 'Suggest was done.')
        t.json_has('suggests.0', 'Suggest present')
        t.json_is('suggests.0.weight', 202)
        if weight:
            t.json_is('suggests.0.result_weight', weight)
        else:
            t.json_is('suggests.0.result_weight', 202)
