import pytest
# pylint: disable=too-many-locals


@pytest.mark.parametrize('sampling', ['old', 'new'])
async def test_reserve_samples(tap, dataset, wait_order_status, now, sampling):
    with tap.plan(20, 'Резервирование сэмплов'):

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
                'tags': ['packaging'],
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
        store   = await dataset.store(**kwargs)
        user    = await dataset.user(store=store)

        stock1 = await dataset.stock(product=product1, store=store, count=100)
        stock2 = await dataset.stock(product=product2, store=store, count=200)
        stock3 = await dataset.stock(product=product3, store=store, count=300)

        order = await dataset.order(
            store=store,
            type = 'order',
            status='reserving',
            estatus='begin',
            acks=[user.user_id],
            approved=now(),
            required = [
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

        tap.ok(await order.business.order_changed(), 'Резервирование')

        with await order.reload() as order:
            tap.eq(order.status, 'complete', 'complete')
            tap.eq(order.estatus, 'withdraw_samples', 'withdraw_samples')
            tap.eq(order.target, 'complete', 'target: complete')

            problems = dict(((x.type, x.product_id), x) for x in order.problems)
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
            tap.eq(stock.reserve, 20+2, 'Зарезервировано по заказу + сэмпл')

        with await stock3.reload() as stock:
            tap.eq(stock.count, 300, 'Количество не менялось')
            tap.eq(stock.reserve, 3, 'Зарезервировано по сэмплу')

        await wait_order_status(
            order,
            ('complete', 'done'),
        )

        tap.ok(await order.reload(), 'Перезабрали заказ')

        with await stock1.reload() as stock:
            tap.eq(stock.count, 100 - 10, 'Продан товар')
            tap.eq(stock.reserve, 0, 'Резервы проданы')

        with await stock2.reload() as stock:
            tap.eq(stock.count, 200 - 20 - 2, 'Продан товар + сэмпл')
            tap.eq(stock.reserve, 0, 'Резервы проданы')

        with await stock3.reload() as stock:
            tap.eq(stock.count, 300 - 3, 'Продан сэмпл')
            tap.eq(stock.reserve, 0, 'Резервы проданы')


@pytest.mark.parametrize('sampling', ['old', 'new'])
async def test_sampling_condition(
        tap, wait_order_status, dataset, now, sampling):
    with tap.plan(20, 'Резервирование сэмплов с условиями'):
        group = await dataset.product_group(
            timetable=[{'type': 'everyday', 'begin': '00:00', 'end': '00:00'}])
        product1 = await dataset.product(groups=[group.group_id])
        product2 = await dataset.product()
        product3 = await dataset.product()

        samples_data = [
            {
                'product_id': product2.product_id,
                'mode': 'optional',
                'count': 1,
                'tags': ['sampling'],
                'condition': {
                    'condition_type': 'total_price_above',
                    'total_price': '1234.56'  # не пройдет
                },
            },
            {
                'product_id': product3.product_id,
                'mode': 'optional',
                'count': 3,
                'tags': ['sampling'],
                'condition': {
                    'condition_type': 'group_present',
                    'group_id': group.group_id,  # пройдет
                },
            },
        ]
        if sampling == 'old':
            kwargs = dict(samples=samples_data)
        else:
            kwargs = dict(samples_ids=[(await dataset.sample(**s)).sample_id
                                       for s in samples_data])
        store = await dataset.store(**kwargs)
        user = await dataset.user(store=store)

        stock1 = await dataset.stock(product=product1, store=store,
                                     count=100)
        stock2 = await dataset.stock(product=product2, store=store,
                                     count=200)
        stock3 = await dataset.stock(product=product3, store=store,
                                     count=300)

        order = await dataset.order(
            store=store,
            type='order',
            status='reserving',
            estatus='begin',
            acks=[user.user_id],
            total_price='1230.00',
            approved=now(),
            required=[
                {
                    'product_id': product1.product_id,
                    'count': 10
                },
            ],

        )

        await wait_order_status(
            order,
            ('complete', 'reserve_samples'),
            user_done=user,
        )

        tap.ok(await order.business.order_changed(), 'Резервирование')

        with await order.reload() as order:
            tap.eq(order.status, 'complete', 'complete')
            tap.eq(order.estatus, 'withdraw_samples', 'withdraw_samples')
            tap.eq(order.target, 'complete', 'target: complete')
            tap.eq(len(order.problems), 0, 'Нет проблем')

        with await stock1.reload() as stock:
            tap.eq(stock.count, 100, 'Количество не менялось')
            tap.eq(stock.reserve, 10, 'Зарезервировано по заказу')

        with await stock2.reload() as stock:
            tap.eq(stock.count, 200, 'Количество не менялось')
            tap.eq(stock.reserve, 0, 'Не резервировалось')

        with await stock3.reload() as stock:
            tap.eq(stock.count, 300, 'Количество не менялось')
            tap.eq(stock.reserve, 3, 'Зарезервировано по сэмплу')

        await wait_order_status(
            order,
            ('complete', 'done'),
        )

        tap.ok(await order.reload(), 'Перезабрали заказ')

        with await stock1.reload() as stock:
            tap.eq(stock.count, 100 - 10, 'Продан товар')
            tap.eq(stock.reserve, 0, 'Резервы проданы')

        with await stock2.reload() as stock:
            tap.eq(stock.count, 200, 'Количество не менялось')
            tap.eq(stock.reserve, 0, 'Не резервировалось')

        with await stock3.reload() as stock:
            tap.eq(stock.count, 300 - 3, 'Продан сэмпл')
            tap.eq(stock.reserve, 0, 'Резервы проданы')
