import pytest

from stall.model.stash import ClientStash
from stall.model.stock import Stock
from stall.model.stock_log import StockLog


# pylint: disable=too-many-locals,too-many-statements
@pytest.mark.parametrize('sampling', ['old', 'new'])
async def test_withdraw_samples(tap, dataset, wait_order_status,
                                now, sampling):
    with tap.plan(24, 'Списание сэмплов'):
        product1 = await dataset.product()
        product2 = await dataset.product()
        product3 = await dataset.product()
        product4 = await dataset.product()

        samples_data = [
            {
                'product_id': product2.product_id,
                'mode': 'optional',
                'count': 2,
                'tags': ['packaging'],
            },
            {
                'product_id': product3.product_id,
                'mode': 'optional',
                'count': 3,
                'tags': ['sampling'],
            },
            {
                'product_id': product4.product_id,
                'mode': 'optional',
                'count': 4,
                'tags': ['packaging'],
            },
        ]
        if sampling == 'old':
            kwargs = dict(samples=samples_data)
        else:
            kwargs = dict(samples_ids=[(await dataset.sample(**s)).sample_id
                                       for s in samples_data])
        store = await dataset.store(**kwargs)
        user = await dataset.user(store=store)

        stock1 = await dataset.stock(product=product1, store=store, count=100)
        stock2 = await dataset.stock(product=product2, store=store, count=200)
        stock3 = await dataset.stock(product=product3, store=store, count=300)
        stock4 = await dataset.stock(product=product4, store=store, count=5)

        order = await dataset.order(
            store=store,
            type='order',
            status='reserving',
            estatus='begin',
            acks=[user.user_id],
            approved=now(),
            required=[
                {
                    'product_id': product1.product_id,
                    'count': 10
                },
                {
                    'product_id': product2.product_id,
                    'count': 20
                },
            ],

        )

        await wait_order_status(
            order,
            ('complete', 'reserve_samples'),
            user_done=user,
        )

        # резервируем остаток другим заказом, чтобы этому не хватило
        await stock4.do_reserve(await dataset.order(type='order'), 5)

        tap.ok(await order.business.order_changed(), 'Резервирование')

        with await order.reload() as order:
            tap.eq(order.status, 'complete', 'complete')
            tap.eq(order.estatus, 'withdraw_samples', 'withdraw_samples')
            tap.eq(order.target, 'complete', 'target: complete')

            problems = dict(
                ((x.type, x.product_id), x) for x in order.problems)
            with problems[('low', product4.product_id)] as problem:
                tap.eq(
                    problem.count,
                    4,
                    'Проблема недостатка остатков для сэмпла'
                )

        with await stock1.reload() as stock:
            tap.eq(stock.count, 100, 'Количество не менялось')
            tap.eq(stock.reserve, 10, 'Зарезервировано по заказу')

        with await stock2.reload() as stock:
            tap.eq(stock.count, 200, 'Количество не менялось')
            tap.eq(stock.reserve, 20 + 2, 'Зарезервировано по заказу + сэмпл')

        with await stock3.reload() as stock:
            tap.eq(stock.count, 300, 'Количество не менялось')
            tap.eq(stock.reserve, 3, 'Зарезервировано по сэмплу')

        tap.ok(await order.business.order_changed(), 'Списали на сэмпл')

        with await order.reload() as order:
            tap.eq(order.status, 'complete', 'complete')
            tap.eq(order.estatus, 'sale', 'sale')
            tap.eq(order.target, 'complete', 'target: complete')

        with await stock1.reload() as stock:
            tap.eq(stock.count, 100, 'Количество не менялось')
            tap.eq(stock.reserve, 10, 'Зарезервировано по заказу')

        with await stock2.reload() as stock:
            tap.eq(stock.count, 200 - 2, 'Списан сэмпл')
            tap.eq(stock.reserve, 20, 'Резервы под сэмпл списаны, '
                                      'остался резерв под заказ')
            with (await stock2.list_log()).list[-1] as log:
                tap.eq(log.vars, {'tags': ['packaging']}, 'tags')

        with await stock3.reload() as stock:
            tap.eq(stock.count, 300 - 3, 'Списан сэмпл')
            tap.eq(stock.reserve, 0, 'Резерв под сэмпл списан')
            with (await stock3.list_log()).list[-1] as log:
                tap.eq(log.vars, {'tags': ['sampling']}, 'tags')


# pylint: disable=too-many-locals,too-many-statements
@pytest.mark.parametrize('sampling', ['old', 'new'])
async def test_multiple_stocks(tap, dataset, wait_order_status, now, sampling):
    with tap.plan(38, 'Списание сэмплов, когда один товар '
                      'зарезервирован на нескольких остатках'):
        product1 = await dataset.product()

        samples_data = [
            {
                'product_id': product1.product_id,
                'mode': 'optional',
                'count': 5,
                'tags': ['sampling'],
            },
        ]
        if sampling == 'old':
            kwargs = dict(samples=samples_data)
        else:
            kwargs = dict(samples_ids=[(await dataset.sample(**s)).sample_id
                                       for s in samples_data])
        store = await dataset.store(**kwargs)
        user = await dataset.user(store=store)

        stock1 = await dataset.stock(product=product1, store=store, count=4)
        stock2 = await dataset.stock(product=product1, store=store, count=4)
        stock3 = await dataset.stock(product=product1, store=store, count=4)
        stock4 = await dataset.stock(product=product1, store=store, count=50)

        order = await dataset.order(
            store=store,
            type='order',
            status='reserving',
            estatus='begin',
            acks=[user.user_id],
            approved=now(),
            required=[
                {
                    'product_id': product1.product_id,
                    'count': 10
                },
            ],
        )

        await stock1.do_reserve(order, 2)
        await stock2.do_reserve(order, 3)
        await stock3.do_reserve(order, 4)
        await stock4.do_reserve(order, 1)

        await wait_order_status(
            order,
            ('complete', 'reserve_samples'),
            user_done=user,
        )

        await stock1.reload()
        await stock2.reload()
        await stock3.reload()
        await stock4.reload()

        tap.eq(stock1.count, 4, 'stock1.count=4')
        tap.eq(stock1.reserve, 2, 'stock1.reserve=2')

        tap.eq(stock2.count, 4, 'stock2.count=4')
        tap.eq(stock2.reserve, 3, 'stock2.reserve=3')

        tap.eq(stock3.count, 4, 'stock3.count=4')
        tap.eq(stock3.reserve, 4, 'stock3.reserve=4')

        tap.eq(stock4.count, 50, 'stock3.count=50')
        tap.eq(stock4.reserve, 1, 'stock3.reserve=1')

        tap.ok(await order.business.order_changed(),
               'Резервирование под сэмплинг')

        await stock1.reload()
        await stock2.reload()
        await stock3.reload()
        await stock4.reload()

        tap.eq(stock1.count, 4, 'stock1.count=4')
        tap.eq(stock1.reserve, 2 + 2, 'stock1.reserve=4')

        tap.eq(stock2.count, 4, 'stock2.count=4')
        tap.eq(stock2.reserve, 3 + 1, 'stock2.reserve=4')

        tap.eq(stock3.count, 4, 'stock3.count=4')
        tap.eq(stock3.reserve, 4, 'stock3.reserve=4')

        tap.eq(stock4.count, 50, 'stock4.count=50')
        tap.eq(stock4.reserve, 1 + 2, 'stock4.reserve=3')

        await order.reload()

        tap.ok('actual_sample_reserves' in order.estatus_vars,
               'actual_sample_reserves выставлен в estatus_vars')
        actual_sample_reserves = order.estatus_vars['actual_sample_reserves']
        actual_sample_reserves = {
            res['stock_id']: res for res in actual_sample_reserves
        }
        tap.eq_ok(actual_sample_reserves[stock1.stock_id]['count'], 2,
                  'в stock1 дополнительно зарезервировано 2')
        tap.eq_ok(actual_sample_reserves[stock2.stock_id]['count'], 1,
                  'в stock2 дополнительно зарезервировано 1')
        tap.ok(stock3.stock_id not in actual_sample_reserves,
               'в stock3 дополнительно ничего не зарезервировано')
        tap.eq_ok(actual_sample_reserves[stock4.stock_id]['count'], 2,
                  'в stock4 дополнительно зарезервировано 2')

        tap.ok(await order.business.order_changed(),
               'Списание под сэмплинг')

        with await order.reload() as order:
            tap.eq(order.status, 'complete', 'complete')
            tap.eq(order.estatus, 'sale', 'sale')
            tap.eq(order.target, 'complete', 'target: complete')
            tap.eq(len(order.problems), 0, 'Нет проблем')

        await stock1.reload()
        await stock2.reload()
        await stock3.reload()
        await stock4.reload()

        tap.eq_ok(stock1.count + stock2.count + stock3.count + stock4.count,
                  4 + 4 + 4 + 50 - 5,
                  'total count decreased by 5 items')
        tap.eq_ok(stock1.reserve + stock2.reserve
                  + stock3.reserve + stock4.reserve,
                  4 + 4 + 4 + 3 - 5,
                  'total reserve decreased by 5 items')

        await wait_order_status(
            order,
            ('complete', 'done'),
        )

        tap.ok(await order.reload(), 'Перезабрали заказ')
        await stock1.reload()
        await stock2.reload()
        await stock3.reload()
        await stock4.reload()

        tap.eq_ok(stock1.count + stock2.count + stock3.count + stock4.count,
                  4 + 4 + 4 + 50 - 15,
                  'total count decreased by 10 items')
        tap.eq(stock1.reserve, 0, 'stock1.reserve=0')
        tap.eq(stock2.reserve, 0, 'stock2.reserve=0')
        tap.eq(stock3.reserve, 0, 'stock3.reserve=0')
        tap.eq(stock4.reserve, 0, 'stock4.reserve=0')

        stock_logs = await StockLog.list(
            by='full',
            conditions=[
                ['order_id', order.order_id],
                ['type', 'sample'],
            ],
            sort=(),
        )
        with tap.subtest() as taps:
            for stock_log in stock_logs.list:
                taps.eq_ok(stock_log.vars, {'tags': ['sampling']},
                           'tags: [sampling]')


@pytest.mark.parametrize('sampling', ['old', 'new'])
async def test_too_low(tap, dataset, wait_order_status, now, sampling):
    with tap.plan(31, 'Списание сэмплов, когда товара не хватает'):
        product1 = await dataset.product()

        samples_data = [
            {
                'product_id': product1.product_id,
                'mode': 'optional',
                'count': 5,
                'tags': ['sampling'],
            },
        ]
        if sampling == 'old':
            kwargs = dict(samples=samples_data)
        else:
            kwargs = dict(samples_ids=[(await dataset.sample(**s)).sample_id
                                       for s in samples_data])
        store = await dataset.store(**kwargs)
        user = await dataset.user(store=store)

        stock1 = await dataset.stock(product=product1, store=store, count=4)
        stock2 = await dataset.stock(product=product1, store=store, count=4)

        order = await dataset.order(
            store=store,
            type='order',
            status='reserving',
            estatus='begin',
            acks=[user.user_id],
            approved=now(),
            required=[
                {
                    'product_id': product1.product_id,
                    'count': 5
                },
            ],
        )

        await stock1.do_reserve(order, 2)
        await stock2.do_reserve(order, 3)

        await wait_order_status(
            order,
            ('complete', 'reserve_samples'),
            user_done=user,
        )

        await stock1.reload()
        await stock2.reload()

        tap.eq(stock1.count, 4, 'stock1.count=4')
        tap.eq(stock1.reserve, 2, 'stock1.reserve=2')

        tap.eq(stock2.count, 4, 'stock2.count=4')
        tap.eq(stock2.reserve, 3, 'stock2.reserve=3')

        tap.ok(await order.business.order_changed(),
               'Резервирование под сэмплинг')

        await stock1.reload()
        await stock2.reload()

        tap.eq(stock1.count, 4, 'stock1.count=4')
        tap.eq(stock1.reserve, 2 + 2, 'stock1.reserve=4')

        tap.eq(stock2.count, 4, 'stock2.count=4')
        tap.eq(stock2.reserve, 3 + 1, 'stock2.reserve=4')

        await order.reload()

        tap.ok('actual_sample_reserves' in order.estatus_vars,
               'actual_sample_reserves выставлен в estatus_vars')

        actual_sample_reserves = order.estatus_vars['actual_sample_reserves']
        actual_sample_reserves = {
            res['stock_id']: res for res in actual_sample_reserves
        }
        tap.eq_ok(actual_sample_reserves[stock1.stock_id]['count'], 2,
                  'в stock1 дополнительно зарезервировано 2')
        tap.eq_ok(actual_sample_reserves[stock2.stock_id]['count'], 1,
                  'в stock2 дополнительно зарезервировано 1')
        tap.eq(len(order.problems), 1, 'одна проблема')
        tap.eq(order.problems[0].product_id, product1.product_id,
               'продукт в проблеме')
        tap.eq(order.problems[0].count, 2,
               'в problem.count записано количество, которого не хватило (2)')

        tap.ok(await order.business.order_changed(),
               'Списание под сэмплинг')

        with await order.reload() as order:
            tap.eq(order.status, 'complete', 'complete')
            tap.eq(order.estatus, 'sale', 'sale')
            tap.eq(order.target, 'complete', 'target: complete')

        await stock1.reload()
        await stock2.reload()

        tap.eq(stock1.count, 2, 'stock1.count=2')
        tap.eq(stock1.reserve, 2, 'stock1.reserve=2')

        tap.eq(stock2.count, 3, 'stock2.count=3')
        tap.eq(stock2.reserve, 3, 'stock2.reserve=3')

        await wait_order_status(
            order,
            ('complete', 'done'),
        )

        tap.ok(await order.reload(), 'Перезабрали заказ')
        await stock1.reload()
        await stock2.reload()

        tap.eq(stock1.count, 0, 'stock1.count=0')
        tap.eq(stock1.reserve, 0, 'stock1.reserve=0')
        tap.eq(stock2.count, 0, 'stock2.count=0')
        tap.eq(stock2.reserve, 0, 'stock2.reserve=0')

        stock_logs = await StockLog.list(
            by='full',
            conditions=[
                ['order_id', order.order_id],
                ['type', 'sample'],
            ],
            sort=(),
        )
        with tap.subtest() as taps:
            for stock_log in stock_logs.list:
                taps.eq_ok(stock_log.vars, {'tags': ['sampling']},
                           'tags: [sampling]')


@pytest.mark.parametrize('sampling', ['old', 'new'])
async def test_product_in_two_samples(tap, dataset, wait_order_status,
                                      now, sampling):
    with tap.plan(19, 'Списание сэмплов, когда товара не хватает'):
        product1 = await dataset.product()

        samples_data = [
            {
                'product_id': product1.product_id,
                'mode': 'optional',
                'count': 1,
                'tags': ['sampling'],
            },
            {
                'product_id': product1.product_id,
                'mode': 'optional',
                'count': 1,
                'tags': ['packaging'],
            },
        ]
        if sampling == 'old':
            kwargs = dict(samples=samples_data)
        else:
            kwargs = dict(samples_ids=[(await dataset.sample(**s)).sample_id
                                       for s in samples_data])
        store = await dataset.store(**kwargs)
        user = await dataset.user(store=store)

        stock1 = await dataset.stock(product=product1, store=store, count=4)
        stock2 = await dataset.stock(product=product1, store=store, count=4)

        order = await dataset.order(
            store=store,
            type='order',
            status='reserving',
            estatus='begin',
            acks=[user.user_id],
            approved=now(),
            required=[
                {
                    'product_id': product1.product_id,
                    'count': 5
                },
            ],
        )

        await stock1.do_reserve(order, 2)
        await stock2.do_reserve(order, 3)

        await wait_order_status(
            order,
            ('complete', 'reserve_samples'),
            user_done=user,
        )

        await stock1.reload()
        await stock2.reload()

        tap.eq(stock1.count, 4, 'stock1.count=4')
        tap.eq(stock1.reserve, 2, 'stock1.reserve=2')

        tap.eq(stock2.count, 4, 'stock2.count=4')
        tap.eq(stock2.reserve, 3, 'stock2.reserve=3')

        tap.ok(await order.business.order_changed(),
               'Резервирование под сэмплинг')

        tap.ok(await order.business.order_changed(),
               'Списание под сэмплинг')

        with await order.reload() as order:
            tap.eq(order.status, 'complete', 'complete')
            tap.eq(order.estatus, 'sale', 'sale')
            tap.eq(order.target, 'complete', 'target: complete')

        await stock1.reload()
        await stock2.reload()

        tap.eq(stock1.reserve, 2, 'stock1.reserve=2')
        tap.eq(stock2.reserve, 3, 'stock2.reserve=3')

        await wait_order_status(
            order,
            ('complete', 'done'),
        )

        tap.ok(await order.reload(), 'Перезабрали заказ')

        tap.eq(len(order.problems), 0, 'проблем нет')

        await stock1.reload()
        await stock2.reload()

        tap.eq(stock1.count + stock2.count, 1, 'осталась 1 шт')
        tap.eq(stock1.reserve, 0, 'stock1.reserve=0')
        tap.eq(stock2.reserve, 0, 'stock2.reserve=0')

        stock_logs = await StockLog.list(
            by='full',
            conditions=[
                ['order_id', order.order_id],
                ['type', 'sample'],
            ],
            sort=(),
        )
        with tap.subtest() as taps:
            for stock_log in stock_logs.list:
                taps.ok('sampling' in stock_log.vars['tags'],
                        'sampling в тегах')
                taps.ok('packaging' in stock_log.vars['tags'],
                        'packaging в тегах')


@pytest.mark.parametrize('sampling', ['old', 'new'])
async def test_one_sample_one_client(
        tap, dataset, wait_order_status, now, uuid, sampling
):
    with tap.plan(20, 'справедливое распределение батонов среди клиентов'):
        client_id = uuid()

        samples = await ClientStash.samples(client_id)
        tap.ok(not samples, 'нет семплов')

        product = await dataset.product()

        sample1 = await dataset.product()
        sample2 = await dataset.product()
        sample3 = await dataset.product()

        samples_data = [
            {
                'product_id': sample1.product_id,
                'mode': 'optional',
                'count': 20,
                'tags': ['packaging'],
            },
            {
                'product_id': sample2.product_id,
                'mode': 'optional',
                'count': 30,
                'tags': ['sampling'],
            },
        ]
        if sampling == 'old':
            kwargs = dict(samples=samples_data)
        else:
            kwargs = dict(samples_ids=[(await dataset.sample(**s)).sample_id
                                       for s in samples_data])
        store = await dataset.store(**kwargs)

        user = await dataset.user(store=store)

        await dataset.stock(
            product=product, store=store, count=100,
        )
        stock_sample1 = await dataset.stock(
            product=sample1, store=store, count=200,
        )
        stock_sample2 = await dataset.stock(
            product=sample2, store=store, count=300,
        )
        stock_sample3 = await dataset.stock(
            product=sample3, store=store, count=400,
        )

        order = await dataset.order(
            store=store,
            type='order',
            status='reserving',
            acks=[user.user_id],
            approved=now(),
            required=[
                {
                    'product_id': product.product_id,
                    'count': 10
                },
            ],
            attr={'client_id': client_id},
        )

        await wait_order_status(
            order, ('complete', 'withdraw_samples'), user_done=user,
        )

        tap.ok(await order.business.order_changed(), 'списываем семплы')

        samples = await ClientStash.samples(client_id)
        tap.eq(len(samples), 2, 'есть семплы')
        tap.eq(
            set(samples.keys()),
            {sample1.product_id, sample2.product_id},
            'записали пакет и батон в историю семплов клиента',
        )

        tap.ok(
            await stock_sample1.reload(), 'перезапросили остаток для упаковки',
        )
        tap.eq(stock_sample1.count, 200 - 20, 'упаковку потратили')
        tap.ok(
            await stock_sample2.reload(), 'перезапросили остаток для батонов',
        )
        tap.eq(stock_sample2.count, 300 - 30, 'клиент получил батоны')

        samples_data = [
            {
                'product_id': sample1.product_id,
                'mode': 'optional',
                'count': 20,
                'tags': ['packaging'],
            },
            {
                'product_id': sample2.product_id,
                'mode': 'optional',
                'count': 30,
                'tags': ['sampling'],
            },
            {
                'product_id': sample3.product_id,
                'mode': 'optional',
                'count': 40,
                'tags': ['sampling'],
            },
        ]
        if sampling == 'old':
            store.samples=samples_data
        else:
            samples_ids = [(await dataset.sample(**s)).sample_id
                           for s in samples_data]
            store.samples_ids = samples_ids
        tap.ok(await store.save(), 'изменили семплы для лавки')

        order2 = await dataset.order(
            store=store,
            type='order',
            status='reserving',
            acks=[user.user_id],
            approved=now(),
            required=[
                {
                    'product_id': product.product_id,
                    'count': 10
                },
            ],
            attr={'client_id': client_id},
        )

        await wait_order_status(
            order2, ('complete', 'withdraw_samples'), user_done=user,
        )

        tap.ok(await order2.business.order_changed(), 'списываем семплы')

        samples = await ClientStash.samples(client_id)

        tap.eq(len(samples), 3, 'добавился еще семпл')
        tap.eq(
            set(samples.keys()),
            {sample1.product_id, sample2.product_id, sample3.product_id},
            'записали все семплы для клиента',
        )

        tap.ok(
            await stock_sample1.reload(), 'перезапросили остаток для упаковки',
        )
        tap.eq(stock_sample1.count, 200 - 20 - 20, 'упаковку потратили')
        tap.ok(
            await stock_sample2.reload(), 'перезапросили остаток для батонов',
        )
        tap.eq(
            stock_sample2.count, 300 - 30 - 0, 'клиент не завален батонами',
        )
        tap.ok(
            await stock_sample3.reload(), 'перезапросили остаток для чипсов',
        )
        tap.eq(
            stock_sample3.count, 400 - 40, 'клиент получил чипсы',
        )


# pylint: disable=too-many-locals
@pytest.mark.parametrize('sampling', ['old', 'new'])
async def test_run_after_fail(tap, dataset, wait_order_status, now, sampling):
    with tap.plan(24, 'Списание сэмплов'):
        product1 = await dataset.product()
        product2 = await dataset.product()
        product3 = await dataset.product()
        product4 = await dataset.product()

        samples_data = [
            {
                'product_id': product2.product_id,
                'mode': 'optional',
                'count': 2,
                'tags': ['packaging'],
            },
            {
                'product_id': product3.product_id,
                'mode': 'optional',
                'count': 3,
                'tags': ['sampling'],
            },
            {
                'product_id': product4.product_id,
                'mode': 'optional',
                'count': 4,
                'tags': ['packaging'],
            },
        ]
        if sampling == 'old':
            kwargs = dict(samples=samples_data)
        else:
            kwargs = dict(samples_ids=[(await dataset.sample(**s)).sample_id
                                       for s in samples_data])
        store = await dataset.store(**kwargs)
        user = await dataset.user(store=store)

        stock1 = await dataset.stock(product=product1, store=store, count=100)
        stock2 = await dataset.stock(product=product2, store=store, count=200)
        stock3 = await dataset.stock(product=product3, store=store, count=300)
        stock4 = await dataset.stock(product=product4, store=store, count=5)

        order = await dataset.order(
            store=store,
            type='order',
            status='reserving',
            estatus='begin',
            acks=[user.user_id],
            approved=now(),
            required=[
                {
                    'product_id': product1.product_id,
                    'count': 10
                },
                {
                    'product_id': product2.product_id,
                    'count': 20
                },
            ],

        )

        await wait_order_status(
            order,
            ('complete', 'reserve_samples'),
            user_done=user,
        )

        # резервируем остаток другим заказом, чтобы этому не хватило
        await stock4.do_reserve(await dataset.order(type='order'), 5)

        tap.ok(await order.business.order_changed(), 'Резервирование')

        with await order.reload() as order:
            tap.eq(order.status, 'complete', 'complete')
            tap.eq(order.estatus, 'withdraw_samples', 'withdraw_samples')
            tap.eq(order.target, 'complete', 'target: complete')

            problems = dict(
                ((x.type, x.product_id), x) for x in order.problems)
            with problems[('low', product4.product_id)] as problem:
                tap.eq(
                    problem.count,
                    4,
                    'Проблема недостатка остатков для сэмпла'
                )

        with await stock1.reload() as stock:
            tap.eq(stock.count, 100, 'Количество не менялось')
            tap.eq(stock.reserve, 10, 'Зарезервировано по заказу')

        with await stock2.reload() as stock:
            tap.eq(stock.count, 200, 'Количество не менялось')
            tap.eq(stock.reserve, 20 + 2, 'Зарезервировано по заказу + сэмпл')

        with await stock3.reload() as stock:
            tap.eq(stock.count, 300, 'Количество не менялось')
            tap.eq(stock.reserve, 3, 'Зарезервировано по сэмплу')

        # имитируем неудачную попытку обработать статус withdraw_samples
        actual_sample_reserves = order.estatus_vars['actual_sample_reserves']
        stocks = await Stock.list_by_order(
            order=order,
            shelf_type=('store', 'markdown', 'kitchen_on_demand'),
        )
        stocks = {s.stock_id: s for s in stocks}
        for value in actual_sample_reserves:
            count = value['count']
            stock = stocks[value['stock_id']]
            await stock.do_sample(order, count, tags=value['tags'])

        # теперь новая попытка обработать статус withdraw_samples
        tap.ok(await order.business.order_changed(), 'Списали на сэмпл')

        with await order.reload() as order:
            tap.eq(order.status, 'complete', 'complete')
            tap.eq(order.estatus, 'sale', 'sale')
            tap.eq(order.target, 'complete', 'target: complete')

        with await stock1.reload() as stock:
            tap.eq(stock.count, 100, 'Количество не менялось')
            tap.eq(stock.reserve, 10, 'Зарезервировано по заказу')

        with await stock2.reload() as stock:
            tap.eq(stock.count, 200 - 2, 'Списан сэмпл')
            tap.eq(stock.reserve, 20, 'Резервы под сэмпл списаны, '
                                      'остался резерв под заказ')
            with (await stock2.list_log()).list[-1] as log:
                tap.eq(log.vars, {'tags': ['packaging']}, 'tags')

        with await stock3.reload() as stock:
            tap.eq(stock.count, 300 - 3, 'Списан сэмпл')
            tap.eq(stock.reserve, 0, 'Резерв под сэмпл списан')
            with (await stock3.list_log()).list[-1] as log:
                tap.eq(log.vars, {'tags': ['sampling']}, 'tags')
