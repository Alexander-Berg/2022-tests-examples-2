# pylint: disable=too-many-statements,too-many-locals

from datetime import datetime, timedelta

import pytest

from libstall.util import now
from stall.model.order import Order
from stall.model.suggest import Suggest


@pytest.mark.parametrize('source', ['eda', '1c', 'woody'])
async def test_stowage(tap, dataset, wait_order_status, uuid, source):
    with tap.plan(48, 'Генерация идентификатора для заказа раскладки'):

        product1 = await dataset.product()
        product2 = await dataset.product()
        product3 = await dataset.product()
        product4 = await dataset.product()
        product5 = await dataset.product()

        store = await dataset.store()
        user  = await dataset.user(store=store)
        shelf = await dataset.shelf(store=store, type='incoming')

        order = await dataset.order(
            store=store,
            type = 'acceptance',
            source=source,
            status='reserving',
            estatus='begin',
            approved=now(),
            acks=[user.user_id],
            attr={'doc_number': '11111-22222',
                  'contractor': uuid(),
                  'doc_date': now().strftime('%F'),
                  'request_type': 'move_order',
                  },
            required = [
                {
                    'product_id': product1.product_id,
                    'count': 100,
                    'valid': datetime.utcnow() + timedelta(days=1)
                },
                {
                    'product_id': product3.product_id,
                    'count': 300
                },
                {
                    'product_id': product2.product_id,
                    'count': 200
                },
                {
                    'product_id': product4.product_id,
                    'count': 400
                },
            ],
        )
        tap.ok(order, 'Заказ создан')

        await wait_order_status(
            order,
            ('processing', 'waiting'),
            user_done=user,
        )

        suggests = dict((s.product_id, s)
                        for s in await Suggest.list_by_order(order))
        tap.eq(len(suggests), 4, 'Список саджестов')

        with suggests[product1.product_id] as suggest:
            tap.eq(
                suggest.product_id, product1.product_id,
                f'Саджест {suggest.suggest_id}'
            )
            tap.ok(
                await suggest.done('done', count=suggest.count),
                'Саджест закрыт'
            )

        with suggests[product3.product_id] as suggest:
            tap.eq(
                suggest.product_id, product3.product_id,
                f'Саджест {suggest.suggest_id}'
            )
            tap.ok(
                await suggest.done('done', count=250),
                'Саджес закрыт с меньшим количеством'
            )

        with suggests[product2.product_id] as suggest:
            tap.eq(
                suggest.product_id, product2.product_id,
                f'Саджест {suggest.suggest_id}'
            )
            tap.ok(
                await suggest.done(),   # 'done', count=450),
                'Закрываем точно'
            )

        with suggests[product4.product_id] as suggest:
            tap.eq(
                suggest.product_id, product4.product_id,
                f'Саджест {suggest.suggest_id}'
            )
            tap.ok(
                await suggest.done('done', count=0),
                'Саджест закрыт с нулем'
            )

        suggest5 = await dataset.suggest(
            order,
            type='check',
            shelf_id=shelf.shelf_id,
            product_id=product5.product_id,
            conditions={
                'all': True,
            }
        )
        with suggest5 as suggest:
            tap.ok(
                await suggest.done('done', count=110, valid=now().date()),
                'Саджест добавлен с новым продуктом, вне требований'
            )
            tap.ok(suggest, f'Саджест {suggest.suggest_id}')

        await wait_order_status(
            order,
            ('complete', 'stowage_save'),
            user_done=user,
        )

        order = await Order.load(order.order_id)
        tap.ok(order, 'Перезабрали заказ')
        tap.eq(order.status, 'complete', 'complete')
        tap.eq(order.estatus, 'stowage_save', 'estatus')
        tap.eq(order.target, 'complete', 'target: complete')

        tap.isa_ok(order.estatus_vars, dict, 'группы подготовлены')

        for g in order.estatus_vars.values():
            external_id = g['external_id']

        tap.ok(
            external_id,
            'Будущий идентификатор',
        )

        await order.business.order_changed()

        tap.ok(await order.reload(), 'Перезабрали заказ')
        tap.eq(order.status, 'complete', 'complete')
        tap.eq(order.estatus, 'suggests_drop', 'suggests_drop')
        tap.eq(order.target, 'complete', 'target: complete')

        tap.eq(len(order.problems), 0, 'Нет проблем')

        stowage = await Order.load(
            (store.store_id, external_id), by='conflict'
        )
        tap.ok(stowage, 'Заказ на раскладку')
        tap.eq(stowage.type, 'sale_stowage', 'sale_stowage')
        tap.eq(stowage.status, 'reserving', 'reserving')
        tap.eq(stowage.estatus, 'begin', 'begin')
        tap.eq(stowage.target, 'complete', 'target: complete')
        tap.eq(stowage.source, source, 'source inherited')

        tap.eq(len(stowage.required), 4, 'Требования переданы')

        tap.eq(stowage.company_id, order.company_id, 'company_id')

        tap.eq(stowage.attr.get('contractor'),
               order.attr.get('contractor'), 'Поставщик передан')
        tap.eq(stowage.attr['doc_number'],
               '11111-22222-1', 'Номер сформирован')
        tap.eq(stowage.attr.get('request_type'),
               'move_order', 'Тип передан')

        with stowage.required[0] as require:
            tap.eq(require.product_id, product1.product_id, 'product_id')
            tap.eq(require.count, 100, f'count={require.count}')
            tap.ok(require.valid, 'valid')

        with stowage.required[1] as require:
            tap.eq(require.product_id, product3.product_id, 'product_id')
            tap.eq(require.count, 250, f'count={require.count}')
            tap.ok(not require.valid, 'valid')

        with stowage.required[2] as require:
            tap.eq(require.product_id, product2.product_id, 'product_id')
            tap.eq(require.count, 200, f'count={require.count}')
            tap.ok(not require.valid, 'valid')

        with stowage.required[3] as require:
            tap.eq(require.product_id, product5.product_id, 'product_id')
            tap.eq(require.count, 110, f'count={require.count}')
            tap.ok(require.valid, 'valid')


@pytest.mark.parametrize(
    'products_tags',
    [
        [[], ['freezer']],
        [[]],
    ])
async def test_stowage_update_acceptance(
    tap, dataset, wait_order_status, cfg, products_tags,
):
    cnt_taps = 3 + 4*len(products_tags)
    with tap.plan(cnt_taps, 'прокидываем флажок в приемку из раскладок'):
        cfg.set('business.order.acceptance.stowage_limit', 1)
        store = await dataset.full_store(options={'exp_freegan_party': True})
        user = await dataset.user(store=store)
        for tags in products_tags:
            await dataset.shelf(store=store, tags=tags)
        products = [await dataset.product(tags=t) for t in products_tags]

        acc = await dataset.order(
            type='acceptance',
            store=store,
            approved=now(),
            required=[
                {
                    'product_id': p.product_id,
                    'count': 69,
                }
                for p in products
            ],
            acks=[user.user_id],
        )

        await wait_order_status(acc, ('complete', 'done'), user_done=user)

        stowages = await acc.get_descendants()
        tap.eq(len(stowages), len(products), f'{len(products)} детей')
        tap.ok(
            all(o.type == 'sale_stowage' for o in stowages),
            'раскладки',
        )

        for i, stowage in enumerate(stowages, start=1):
            await acc.reload()
            tap.ok(not acc.vars.get('all_children_done'), 'галочки нет')
            await wait_order_status(
                stowage, ('request', 'waiting'), user_done=user,
            )
            await stowage.ack(user)
            await wait_order_status(
                stowage, ('complete', 'done'), user_done=user,
            )
            await acc.reload()
            if i != len(products):
                tap.ok(not acc.vars.get('all_children_done'), 'галочки нет')
            else:
                tap.ok(acc.vars.get('all_children_done'), 'галочка есть')


async def test_weight_stowage_update_acc(tap, dataset, wait_order_status):
    with tap.plan(12, 'тестим проставление галочки из весовой раскладки'):
        store = await dataset.full_store()
        user = await dataset.user(store=store)
        weight = await dataset.weight_products()

        acc = await dataset.order(
            type='acceptance',
            store=store,
            approved=now(),
            required=[
                {
                    'product_id': weight[0].product_id,
                    'count': 69,
                }
            ],
            acks=[user.user_id],
        )

        await wait_order_status(acc, ('processing', 'waiting'), user_done=user)
        suggests = await Suggest.list_by_order(acc)
        tap.eq(len(suggests), 1, 'один саджест')
        tap.ok(
            await suggests[0].done(weight=100, user=user), 'саджест выполнен',
        )
        await wait_order_status(acc, ('complete', 'done'), user_done=user)

        stowages = await acc.get_descendants()
        tap.eq(len(stowages), 1, 'одна раскладка')
        tap.eq(stowages[0].type, 'weight_stowage', 'весовая раскладка')
        stowages[0].acks = [user.user_id]
        await stowages[0].save()

        await acc.reload()
        tap.ok(not acc.vars.get('all_children_done'), 'дочки не готовы')

        await wait_order_status(
            stowages[0], ('processing', 'waiting'), user_done=user,
        )
        suggests = await Suggest.list_by_order(stowages[0])
        tap.eq(len(suggests), 1, 'один саджест')
        tap.ok(
            await suggests[0].done(weight=100, user=user), 'саджест выполнен',
        )
        await wait_order_status(
            stowages[0], ('complete', 'done'), user_done=user,
        )

        await acc.reload()
        tap.ok(acc.vars.get('all_children_done'), 'дочки готовы')
