import pytest
from stall.model.stock import Stock
from stall.model.suggest import Suggest


async def create_refund(tapp,
                        dataset,
                        wait_order_status,
                        uuid,
                        rm_stock = False,
                        different_shelves=False,
                        ):
    with tapp.subtest(16, 'Создаём refund') as tap:
        store = await dataset.store()
        tap.ok(store, 'склад создан')

        user = await dataset.user(role='admin', store=store)
        tap.eq(user.store_id, store.store_id, 'пользователь создан')

        stock = await dataset.stock(store=store, count=23, lot=uuid())
        tap.eq(stock.store_id, store.store_id, 'остаток создан')

        if different_shelves:
            stock2 = await dataset.stock(store=store,
                                         count=20,
                                         product_id=stock.product_id,
                                         lot=uuid())
        else:
            stock2 = await dataset.stock(store=store,
                                         count=20,
                                         product_id=stock.product_id,
                                         shelf_id=stock.shelf_id,
                                         lot=uuid())
        tap.eq(stock2.store_id, store.store_id, 'остаток создан')
        tap.ne(stock2.stock_id, stock.stock_id, 'Другой остаток')

        if different_shelves:
            tap.ne(stock2.shelf_id, stock.shelf_id, 'На другой полке')
        else:
            tap.eq(stock2.shelf_id, stock.shelf_id, 'на той же полке')

        order = await dataset.order_done(
            store=store,
            required=[
                {
                    'product_id': stock.product_id,
                    'count': 32,
                }
            ],
            type='order',
            approved='2012-01-02',
        )
        tap.eq(order.store_id, store.store_id, 'ордер создан')
        tap.eq(order.fstatus, ('complete', 'done'), 'статус')
        tap.eq(order.type, 'order', 'тип')
        tap.ok(await order.cancel(), 'отменён после завершения')
        if rm_stock:
            await stock2.rm()

        await wait_order_status(order,
                                ('canceled', 'done'), user_done=user, tap=tap)

        child_order = await order.load(order.vars('child_order_id'))
        tap.ok(child_order, 'дочерний ордер загружен')
        tap.eq(child_order.type, 'refund', 'type: refund')
        tap.eq(child_order.store_id, order.store_id, 'store_id')
        tap.eq(child_order.company_id, order.company_id, 'company_id')
        tap.in_ok(order.attr.get('doc_number'),
                  child_order.attr.get('doc_number'), 'doc_number')
        return child_order

@pytest.mark.parametrize('rm_stock', [False, True])
async def test_order(tap, dataset, wait_order_status, uuid, rm_stock):
    with tap.plan(37, 'Тесты полного цикла'):
        order = await create_refund(
            tapp=tap,
            dataset=dataset,
            uuid=uuid,
            wait_order_status=wait_order_status,
            rm_stock=rm_stock,
            )
        tap.ok(order, 'ордер создан')

        user = await dataset.user(store_id=order.store_id)
        tap.eq(user.store_id, order.store_id, 'Пользователь создан')

        trash = await dataset.shelf(store_id=order.store_id, type='trash')
        tap.eq((trash.type, trash.store_id),
               ('trash', order.store_id),
               'полка списания создана')

        lost = await dataset.shelf(store_id=order.store_id, type='lost')
        tap.eq((lost.type, lost.store_id),
               ('lost', order.store_id),
               'Пока потерь создана')

        await wait_order_status(order, ('request', 'waiting'))

        tap.ok(await order.ack(user), 'ack послан')
        await wait_order_status(order, ('processing', 'waiting'))

        suggests = await Suggest.list_by_order(order)
        tap.ok(suggests, 'саджесты получены')
        tap.eq(len(suggests), 1, 'один саджест')
        for s in suggests:
            tap.eq(s.type, 'box2shelf', 'тип')
            tap.eq(s.store_id, order.store_id, 'store_id')
            tap.ok(s.conditions.all, 'разрешены числа отличные от указанного')
            tap.ok(s.conditions.max_count,
                   'Разрешено вводить не больше чем в саджесте')
            tap.ok(not s.conditions.error, 'нельзя закрывать в ошибку')
            tap.eq(s.count, 32, 'количество')
            tap.eq(s.vars('stage'), 'store', 'саджест первичной раскладки')
            tap.ok(s.product_id, 'товар указан')

            tap.ok(await s.done(count=17), 'завершаем саджест меньшим кол-вом')
            await wait_order_status(order, ('processing', 'waiting'))

        suggests = await Suggest.list_by_order(order, status='request')
        tap.ok(suggests, 'саджесты получены')
        tap.eq(len(suggests), 1, 'ещё один саджест request')

        for s in suggests:
            tap.eq(s.type, 'box2shelf', 'тип')
            tap.eq(s.store_id, order.store_id, 'store_id')
            tap.ok(s.conditions.all, 'разрешены числа отличные от указанного')
            tap.eq(s.count, 32 - 17, 'количество')
            tap.eq(s.vars('stage'), 'trash', 'саджест списания')
            tap.ok(s.conditions.max_count,
                   'Разрешено вводить не больше чем в саджесте')
            tap.ok(not s.conditions.error, 'нельзя закрывать в ошибку')
            tap.ok(s.conditions.trash_reason,
                   'нужно передать причину закрытия')
            tap.ok(await s.done(
                count=1,
                reason={'code': 'TRASH_DECAYED'},
            ), 'завершаем саджест меньшим кол-вом')
            await wait_order_status(order,
                                    ('complete', 'done'),
                                    user_done=user)

            stocks = await Stock.list(
                by='full',
                conditions=[
                    {
                        'name': 'stock_id',
                        'value': s.vars('stock_id'),
                    }
                ]
            )
            if rm_stock:
                # TODO Проблема в удалениии не нулевого стока
                tap.in_ok(sum(s.count for s in stocks),
                          [11, 23],
                          'количество на стоках стало прежним')
            else:
                tap.eq(sum(s.count for s in stocks),
                       20 + 23 - 32 + 17,
                       'количество на стоках стало прежним')
            tap.eq(sum(s.reserve for s in stocks),
                   0,
                   'резерв в нуле')

            stocks = await Stock.list_by_shelf(
                store_id=order.store_id,
                shelf_id=trash.shelf_id,
            )
            tap.eq(len(stocks), 1, 'Списали просроченный остаток')

            with stocks[0] as stock:
                tap.eq(len(stock.vars['reasons']), 1, 'Записана причина')
                tap.eq(
                    stock.vars['reasons'][0][order.order_id]['reason_code'],
                    'TRASH_DECAYED',
                    'Код записан'
                )

# pylint: disable=too-many-statements
async def test_order_2stock(tap, dataset, wait_order_status, uuid):
    with tap.plan(32, 'Тесты полного цикла'):
        order = await create_refund(tap,
                                    dataset,
                                    wait_order_status,
                                    uuid,
                                    different_shelves=True)
        tap.ok(order, 'ордер создан')

        trash = await dataset.shelf(store_id=order.store_id, type='trash')
        tap.eq((trash.type, trash.store_id),
               ('trash', order.store_id),
               'полка списания создана')

        lost = await dataset.shelf(store_id=order.store_id, type='lost')
        tap.eq((lost.type, lost.store_id),
               ('lost', order.store_id),
               'Пока потерь создана')

        await wait_order_status(order, ('request', 'waiting'))

        user = await dataset.user(store_id=order.store_id)
        tap.eq(user.store_id, order.store_id, 'Пользователь создан')

        tap.ok(await order.ack(user), 'ack послан')
        await wait_order_status(order, ('processing', 'waiting'))

        suggests = await Suggest.list_by_order(order)
        tap.ok(suggests, 'саджесты получены')
        tap.eq(len(suggests), 2, 'Два саджеста')
        for i, s in enumerate(suggests):
            with tap.subtest(5, f'проверяем саджест {i}') as taps:
                taps.eq(s.type, 'box2shelf', 'тип')
                taps.eq(s.store_id, order.store_id, 'store_id')
                taps.ok(s.conditions.all, 'разрешены числа отличные')
                taps.eq(s.vars('stage'), 'store', 'саджест первичной раскладки')
                taps.ok(s.product_id, 'товар указан')

        tap.eq(sum(s.count for s in suggests), 32, 'общее количество')

        for i, s in enumerate(suggests):
            count = 11
            if s.count == 20:
                count = 6
            tap.ok(await s.done(count=count),
                   f'завершаем саджест {i} count={count}')
        await wait_order_status(order, ('processing', 'waiting'))

        suggests = await Suggest.list_by_order(order, status='request')
        tap.ok(suggests, 'саджесты получены')
        tap.eq(len(suggests), 2, 'ещё один два саджеста на треш')

        for i, s in enumerate(suggests):
            with tap.subtest(6, f'проверяем саджест {i}') as taps:
                taps.eq(s.type, 'box2shelf', 'тип')
                taps.eq(s.store_id, order.store_id, 'store_id')
                taps.ok(s.conditions.all, 'conditions.all')
                taps.eq(s.vars('stage'), 'trash', 'саджест списания')
                taps.eq(len(s.vars('stock_id')), 1, 'один сток на саджест')
                tap.ok(s.conditions.trash_reason,
                       'нужно передать причину закрытия')

                if i == 1:
                    taps.ok(await s.done(
                        count=1,
                        reason={'code': 'TRASH_DECAYED'},
                    ), 'завершаем единицей')
                else:
                    taps.ok(await s.done(
                        count=0,
                        reason={'code': 'TRASH_DECAYED'},
                    ), 'завершаем нулём')

        tap.eq(sum(s.count for s in suggests), 32 - 17, 'общая сумма')
        tap.eq(sum(s.result_count for s in suggests), 1, 'общая сумма закрытия')
        await wait_order_status(order,
                                ('complete', 'done'),
                                user_done=user)

        stocks = await Stock.list(
            by='full',
            conditions=[
                {
                    'name': 'stock_id',
                    'value': [s.vars('stock_id.0') for s in suggests],
                }
            ]
        )

        tap.eq(sum(s.count for s in stocks),
               20 + 23 - 32 + 17,
               'количество на стоках стало прежним')
        tap.eq(sum(s.reserve for s in stocks),
               0,
               'резерв в нуле')

        stocks = await Stock.list_by_product(
            product_id=suggests[0].product_id,
            shelf_type='trash',
            store_id=order.store_id,
        )

        tap.eq(len(stocks), 1, 'Одна запись про остатки на полке trash')
        with stocks[0] as s:
            tap.eq(s.count, 1, 'количество на полке списания')
            tap.eq(
                s.vars['reasons'][0][order.order_id]['reason_code'],
                'TRASH_DECAYED',
                'Код записан'
            )

        stocks = await Stock.list_by_product(
            product_id=suggests[0].product_id,
            shelf_type='lost',
            store_id=order.store_id,
        )

        tap.in_ok(len(stocks), (2, 1), 'Записи lost')
        tap.eq(sum(s.count for s in stocks),
               32 - 17 - 1,
               'количество на полке lost')


# pylint: disable=too-many-statements
async def test_order_canceling(tap, dataset, wait_order_status, uuid):
    with tap.plan(34, 'Тесты полного цикла'):
        order = await create_refund(tap,
                                    dataset,
                                    wait_order_status,
                                    uuid,
                                    different_shelves=True)
        tap.ok(order, 'ордер создан')

        trash = await dataset.shelf(store_id=order.store_id, type='trash')
        tap.eq((trash.type, trash.store_id),
               ('trash', order.store_id),
               'полка списания создана')

        lost = await dataset.shelf(store_id=order.store_id, type='lost')
        tap.eq((lost.type, lost.store_id),
               ('lost', order.store_id),
               'Пока потерь создана')

        await wait_order_status(order, ('request', 'waiting'))

        user = await dataset.user(store_id=order.store_id)
        tap.eq(user.store_id, order.store_id, 'Пользователь создан')

        tap.ok(await order.ack(user), 'ack послан')
        await wait_order_status(order, ('processing', 'waiting'))

        suggests = await Suggest.list_by_order(order)
        tap.ok(suggests, 'саджесты получены')
        tap.eq(len(suggests), 2, 'Два саджеста')
        for i, s in enumerate(suggests):
            with tap.subtest(6, f'проверяем саджест {i}') as taps:
                taps.eq(s.type, 'box2shelf', 'тип')
                taps.eq(s.store_id, order.store_id, 'store_id')
                taps.ok(s.conditions.all, 'разрешены числа отличные')
                taps.eq(s.vars('stage'), 'store', 'саджест первичной раскладки')
                taps.eq(s.vars('mode'), 'product', 'mode: product')
                taps.ok(s.product_id, 'товар указан')

        tap.eq(sum(s.count for s in suggests), 32, 'общее количество')

        for i, s in enumerate(suggests):
            count = 11
            if s.count == 20:
                count = 6
            tap.ok(await s.done(count=count),
                   f'завершаем саджест {i} count={count}')
        await wait_order_status(order, ('processing', 'waiting'))

        suggests = await Suggest.list_by_order(order, status='request')
        tap.ok(suggests, 'саджесты получены')
        tap.eq(len(suggests), 2, 'ещё один два саджеста на треш')

        for i, s in enumerate(suggests):
            with tap.subtest(7, f'проверяем саджест {i}') as taps:
                taps.eq(s.type, 'box2shelf', 'тип')
                taps.eq(s.store_id, order.store_id, 'store_id')
                taps.ok(s.conditions.all, 'conditions.all')
                taps.eq(s.vars('stage'), 'trash', 'саджест списания')
                taps.eq(s.vars('mode'), 'product', 'mode: product соранен')
                taps.eq(len(s.vars('stock_id')), 1, 'один сток на саджест')

                if i == 1:
                    taps.ok(await s.done(count=1), 'завершаем единицей')
                else:
                    taps.ok(await s.done(count=0), 'завершаем нулём')

        tap.eq(sum(s.count for s in suggests), 32 - 17, 'общая сумма')
        tap.eq(sum(s.result_count for s in suggests),
               1,
               'общая сумма закрытия')

        tap.ok(await order.cancel(), 'Ордер отменён')
        version = order.version
        await wait_order_status(order, ('processing', 'waiting'))
        tap.eq(order.target, 'canceled', 'target')
        tap.eq(order.vars('stage', 'store'), 'canceling', 'stage')

        suggests = await Suggest.list_by_order(order, status='request')
        tap.ok(suggests, 'саджесты получены')
        tap.eq(len(suggests),
               4 - 1,
               'сгенерировалось 3 саджеста (на ноль нет антонима)')
        tap.ok(version < order.version, 'версия ++')
        tap.eq([s.type for s in suggests], ['shelf2box'] * 3, 'типы')
        tap.eq([s.vars('stage') for s in suggests],
               ['canceling'] * 3, 'стейдж')
        tap.eq(sum(s.count for s in suggests
                   if s.vars('contr_stage') == 'store'),
               17,
               'Количество возврата возврата')

        tap.eq(sum(s.count for s in suggests
                   if s.vars('contr_stage') == 'trash'),
               1,
               'Количество возврата списания')

        await wait_order_status(order,
                                ('canceled', 'done'),
                                user_done=user)


# pylint: disable=too-many-locals
async def test_refund_kitchen(tap, dataset, wait_order_status, now):
    with tap.plan(34, 'при отмене заказа после комплита кухня идет в мусорку'):
        store = await dataset.store()
        tap.ok(store, 'склад создан')

        user = await dataset.user(role='admin', store=store)
        tap.eq(user.store_id, store.store_id, 'пользователь создан')

        component1 = await dataset.product()
        component2 = await dataset.product()

        shelf_components = await dataset.shelf(
            store=store, type='kitchen_components',
        )
        tap.ok(shelf_components, 'одна полка для компонент')

        stock_component1 = await dataset.stock(
            shelf=shelf_components, product=component1, count=16,
        )
        tap.ok(stock_component1, 'положили на полку компонент1')

        stock_component2 = await dataset.stock(
            shelf=shelf_components, product=component2, count=32,
        )
        tap.ok(stock_component2, 'положили на полку компонент2')

        shelf_on_demand = await dataset.shelf(
            store=store, type='kitchen_on_demand',
        )
        tap.ok(shelf_on_demand, 'одна полка для готовых блюд')

        shelf_lost = await dataset.shelf(
            store=store, type='lost',
        )
        tap.ok(shelf_lost, 'одна полка cписанки')

        product = await dataset.product(
            components=[
                [
                    {'product_id': component1.product_id, 'count': 1},
                ],
                [
                    {'product_id': component2.product_id, 'count': 2},
                ]
            ],
            tags=['refrigerator']
        )

        order = await dataset.order(
            type='order',
            store=store,
            required=[
                {
                    'product_id': product.product_id,
                    'count': 8,
                }
            ],
            approved=now(),
            acks=[user.user_id],
            status='reserving',
        )
        tap.eq(order.store_id, store.store_id, 'ордер создан')
        tap.eq(order.fstatus, ('reserving', 'begin'), 'статус')
        tap.eq(order.type, 'order', 'тип')

        await wait_order_status(order, ('complete', 'done'), user_done=user)

        shelf_trash = await dataset.shelf(store=store, type='trash')
        tap.ok(shelf_trash, 'полка списания')

        shelf_lost = await dataset.shelf(store=store, type='lost')
        tap.ok(shelf_lost, 'полка потерь')

        tap.ok(await order.cancel(), 'отменён после завершения')

        await wait_order_status(order, ('canceled', 'done'), user_done=user)

        child_order = await order.load(order.vars('child_order_id'))
        tap.ok(child_order, 'работаем с рефанд ордером')

        await wait_order_status(child_order, ('request', 'waiting'))

        tap.ok(await child_order.ack(user), 'ack послан')

        await wait_order_status(child_order, ('processing', 'waiting'))

        suggests = await Suggest.list_by_order(child_order, status='request')
        tap.ok(suggests, 'саджесты получены')
        tap.eq(len(suggests), 1, 'один саджест')

        tap.eq(suggests[0].type, 'box2shelf', 'тип')
        tap.eq(suggests[0].product_id, product.product_id, 'товар указан')
        tap.eq(suggests[0].count, 8, 'количество')
        tap.eq(
            suggests[0].vars('stage'),
            'trash_kitchen',
            'саджест кухня в мусорку',
        )
        tap.ok(
            await suggests[0].done(count=3), 'закрываем саджест зачем-то в 3',
        )

        stocks_on_demand = await Stock.list(
            by='full',
            conditions=(
                ('stock_id', suggests[0].vars('stock_id')),
                ('shelf_type', 'kitchen_on_demand'),
            ),
        )

        tap.eq(
            sum(s.count for s in stocks_on_demand),
            0,
            'на полке готовых блюд пусто',
        )
        tap.eq(
            sum(s.reserve for s in stocks_on_demand), 0, 'резерв в нуле',
        )

        await wait_order_status(child_order, ('processing', 'waiting'))

        suggests = await Suggest.list_by_order(child_order, status='request')
        tap.eq(len(suggests), 0, 'нет саджестов на треш')

        await wait_order_status(
            child_order, ('complete', 'done'), user_done=user,
        )

        stocks_trash = await Stock.list_by_product(
            product_id=product.product_id,
            store_id=store.store_id,
            shelf_type='trash',
        )

        tap.eq(len(stocks_trash), 1, 'кухня в мусорке')
        stock = stocks_trash[0]
        tap.eq(stock.count, 3, 'часть порций')
        tap.eq(
            stock.vars['reasons'][0][child_order.order_id]['reason_code'],
            'TRASH_DECAYED',
            'Код записан'
        )


async def test_done(tap, dataset, wait_order_status, uuid):
    with tap.plan(33, 'Проверяем, что нужно подтверждение от пользователя'):
        order = await create_refund(tap, dataset, wait_order_status, uuid)
        tap.ok(order, 'ордер создан')

        user = await dataset.user(store_id=order.store_id)
        tap.eq(user.store_id, order.store_id, 'Пользователь создан')

        trash = await dataset.shelf(store_id=order.store_id, type='trash')
        tap.eq((trash.type, trash.store_id),
               ('trash', order.store_id),
               'полка списания создана')

        lost = await dataset.shelf(store_id=order.store_id, type='lost')
        tap.eq((lost.type, lost.store_id), ('lost', order.store_id),
               'Пока потерь создана')

        await wait_order_status(order, ('request', 'waiting'))

        tap.ok(await order.ack(user), 'ack послан')
        await wait_order_status(order, ('processing', 'waiting'))

        suggests = await Suggest.list_by_order(order)
        tap.ok(suggests, 'саджесты получены')
        tap.eq(len(suggests), 1, 'один саджест')
        for s in suggests:
            tap.eq(s.type, 'box2shelf', 'тип')
            tap.eq(s.store_id, order.store_id, 'store_id')
            tap.ok(s.conditions.all, 'разрешены числа отличные от указанного')
            tap.ok(s.conditions.max_count,
                   'Разрешено вводить не больше чем в саджесте')
            tap.ok(not s.conditions.error, 'нельзя закрывать в ошибку')
            tap.eq(s.count, 32, 'количество')
            tap.eq(s.vars('stage'), 'store', 'саджест первичной раскладки')
            tap.ok(s.product_id, 'товар указан')

            tap.ok(await s.done(count=17), 'завершаем саджест меньшим кол-вом')
            await wait_order_status(order, ('processing', 'waiting'))

        suggests = await Suggest.list_by_order(order, status='request')
        tap.ok(suggests, 'саджесты получены')
        tap.eq(len(suggests), 1, 'ещё один саджест request')

        for s in suggests:
            tap.eq(s.type, 'box2shelf', 'тип')
            tap.eq(s.store_id, order.store_id, 'store_id')
            tap.ok(s.conditions.all, 'разрешены числа отличные от указанного')
            tap.eq(s.count, 32 - 17, 'количество')
            tap.eq(s.vars('stage'), 'trash', 'саджест списания')
            tap.ok(s.conditions.max_count,
                   'Разрешено вводить не больше чем в саджесте')
            tap.ok(not s.conditions.error, 'нельзя закрывать в ошибку')

            tap.ok(await s.done(count=1), 'завершаем саджест меньшим кол-вом')

        await order.business.order_changed()

        tap.eq(order.status, 'processing', 'Still in processing')
        tap.eq(order.estatus, 'waiting', 'Still waiting')
        await wait_order_status(order,
                                ('complete', 'done'),
                                user_done=user)


async def test_refund_change_stock(tap, dataset, uuid, wait_order_status):
    with tap.plan(15, 'Нашли остаток на другой полке'):
        store = await dataset.store()
        user = await dataset.user(role='admin', store=store)
        shelf = await dataset.shelf(store_id=store.store_id, type='store')
        stock_1 = await dataset.stock(store=store, count=5, lot=uuid())
        stock_2 = await dataset.stock(
            store=store,
            count=4,
            lot=uuid(),
            product_id=stock_1.product_id,
            shelf_id=shelf.shelf_id,
        )
        stock_3 = await dataset.stock(
            store=store,
            count=3,
            lot=uuid(),
            product_id=stock_1.product_id,
            shelf_id=shelf.shelf_id,
        )

        order = await dataset.order_done(
            store=store,
            required=[
                {
                    'product_id': stock_1.product_id,
                    'count': 12,
                }
            ],
            type='order',
            approved='2012-01-02',
        )
        tap.eq(order.fstatus, ('complete', 'done'), 'статус')
        tap.ok(await order.cancel(), 'отменён после завершения')
        await wait_order_status(
            order,
            ('canceled', 'done'),
            user_done=user,
            tap=tap
        )

        refund = await dataset.Order.load(order.vars('child_order_id'))
        tap.ok(refund, 'дочерний ордер загружен')

        shelf.type = 'parcel'
        tap.ok(await shelf.save(), 'Полке сменили тип')
        await dataset.shelf(store_id=order.store_id, type='trash')
        await dataset.shelf(store_id=order.store_id, type='lost')
        await wait_order_status(refund, ('request', 'waiting'))

        tap.ok(await refund.ack(user), 'ack послан')
        await wait_order_status(refund, ('complete', 'done'), user_done=user)

        stocks = await dataset.Stock.list(
            by='full',
            conditions=('store_id', store.store_id),
        )
        tap.eq(len(stocks.list), 3, 'Три остатка так и осталось')

        tap.ok(await stock_1.reload(), 'Перезабрали остаток 1')
        tap.eq(stock_1.count, 12, 'Все вернулись на первый сток')
        tap.ok(await stock_2.reload(), 'Перезабрали остаток 2')
        tap.eq(stock_2.count, 0, 'На втором остатке ничего')
        tap.ok(await stock_3.reload(), 'Перезабрали остаток 3')
        tap.eq(stock_3.count, 0, 'На третьем остатке ничего')


async def test_refund_change_shelf(tap, dataset, uuid, wait_order_status):
    with tap.plan(13, 'Нашли другую полку'):
        store = await dataset.store()
        user = await dataset.user(role='admin', store=store)
        await dataset.shelf(store_id=store.store_id, type='trash')
        await dataset.shelf(store_id=store.store_id, type='lost')
        shelf_1 = await dataset.shelf(store_id=store.store_id, type='store')
        shelf_2 = await dataset.shelf(store_id=store.store_id, type='store')
        stock = await dataset.stock(
            store=store,
            count=5,
            lot=uuid(),
            shelf_id=shelf_1.shelf_id,
        )

        order = await dataset.order_done(
            store=store,
            required=[
                {
                    'product_id': stock.product_id,
                    'count': 5,
                }
            ],
            type='order',
            approved='2012-01-02',
        )
        tap.eq(order.fstatus, ('complete', 'done'), 'статус')
        tap.ok(await order.cancel(), 'отменён после завершения')
        await wait_order_status(
            order,
            ('canceled', 'done'),
            user_done=user,
            tap=tap
        )

        refund = await dataset.Order.load(order.vars('child_order_id'))
        tap.ok(refund, 'дочерний ордер загружен')

        shelf_1.status = 'removed'
        tap.ok(await shelf_1.save(), 'Полке сменили статус')
        tap.ok(await stock.rm(), 'Удален остаток уже')

        await wait_order_status(refund, ('request', 'waiting'))
        tap.ok(await refund.ack(user), 'ack послан')
        await wait_order_status(refund, ('complete', 'done'), user_done=user)

        stocks = await dataset.Stock.list(
            by='full',
            conditions=('store_id', store.store_id),
        )
        tap.eq(len(stocks.list), 1, 'Один остаток')
        new_stock = stocks.list[0]
        tap.eq(new_stock.product_id, stock.product_id, 'тот продукт')
        tap.eq(new_stock.count, 5, 'пять на стоке')
        tap.eq(new_stock.shelf_id, shelf_2.shelf_id, 'Вторая полка')


async def test_refund_failure(tap, dataset, uuid, wait_order_status):
    with tap.plan(12, 'Не смогли подобрать полку'):
        store = await dataset.store()
        user = await dataset.user(role='admin', store=store)
        await dataset.shelf(store_id=store.store_id, type='trash')
        await dataset.shelf(store_id=store.store_id, type='lost')
        shelf = await dataset.shelf(store_id=store.store_id, type='store')
        stock = await dataset.stock(
            store=store,
            count=5,
            lot=uuid(),
            shelf_id=shelf.shelf_id,
        )

        order = await dataset.order_done(
            store=store,
            required=[
                {
                    'product_id': stock.product_id,
                    'count': 5,
                }
            ],
            type='order',
            approved='2012-01-02',
        )
        tap.eq(order.fstatus, ('complete', 'done'), 'статус')
        tap.ok(await order.cancel(), 'отменён после завершения')
        await wait_order_status(
            order,
            ('canceled', 'done'),
            user_done=user,
            tap=tap
        )

        refund = await dataset.Order.load(order.vars('child_order_id'))
        tap.ok(refund, 'дочерний ордер загружен')

        shelf.tags = ['refrigerator']
        tap.ok(await shelf.save(), 'Полке сменили тэги')

        await wait_order_status(refund, ('failed', 'done'))

        stocks = await dataset.Stock.list(
            by='full',
            conditions=('store_id', store.store_id),
        )
        tap.eq(len(stocks.list), 1, 'Один остаток')
        tap.ok(await stock.reload(), 'Перезабрали остаток')
        tap.eq(stock.count, 0, '0 на стоке')
        tap.eq(len(refund.problems), 1, 'Одна проблема')
        problem = refund.problems[0]
        tap.eq(problem.type, 'shelf_not_found', 'Проблема та')
        tap.eq(problem.shelf_type, 'store', 'Тип тот')


async def test_restore_stock(tap, dataset, uuid, wait_order_status):
    with tap.plan(15, 'Восстановили остаток'):
        store = await dataset.store()
        user = await dataset.user(role='admin', store=store)
        await dataset.shelf(store_id=store.store_id, type='trash')
        await dataset.shelf(store_id=store.store_id, type='lost')
        shelf_1 = await dataset.shelf(store_id=store.store_id, type='store')
        stock = await dataset.stock(
            store=store,
            count=5,
            lot=uuid(),
            shelf_id=shelf_1.shelf_id,
        )

        order = await dataset.order_done(
            store=store,
            required=[
                {
                    'product_id': stock.product_id,
                    'count': 5,
                }
            ],
            type='order',
            approved='2012-01-02',
        )
        tap.eq(order.fstatus, ('complete', 'done'), 'статус')
        tap.ok(await order.cancel(), 'отменён после завершения')
        await wait_order_status(
            order,
            ('canceled', 'done'),
            user_done=user,
            tap=tap
        )

        refund = await dataset.Order.load(order.vars('child_order_id'))
        tap.ok(refund, 'дочерний ордер загружен')

        await wait_order_status(refund, ('request', 'waiting'))
        tap.ok(await refund.ack(user), 'ack послан')
        await wait_order_status(refund, ('complete', 'begin'), user_done=user)

        stock_id_to_remove = refund.required[0].stock_id
        stock_remove = await dataset.Stock.load(stock_id_to_remove)
        tap.ok(stock_remove, 'Остаток на месте')
        tap.ok(await stock_remove.rm(), 'Удалили остаток')

        await wait_order_status(refund, ('complete', 'done'))

        expected_stocks = (await Stock.list(
            by='full',
            conditions=[
                ('product_id', stock_remove.product_id),
                ('shelf_id', stock_remove.shelf_id),
            ],
        )).list
        tap.eq(len(expected_stocks), 1, 'Один новый остаток')
        new_stock = expected_stocks[0]
        tap.ne_ok(
            new_stock.stock_id,
            stock_remove.stock_id,
            'Новый остаток'
        )
        tap.eq(new_stock.lot, stock_remove.lot, 'Тот же лот')
        tap.eq(new_stock.count, 5, 'Верное количество')
        tap.eq(new_stock.valid, stock_remove.valid, 'Верный СГ')
