# pylint: disable=too-many-locals
from datetime import timedelta

import pytest

from stall.model.stash import ClientStash, Stash
from stall.model.suggest import Suggest


@pytest.mark.parametrize('sampling', ['old', 'new'])
async def test_suggests_samples_generate(tap, wait_order_status, dataset,
                                         now, sampling):
    with tap.plan(17, 'Генерация саджестов'):

        product1 = await dataset.product()
        product2 = await dataset.product()
        product3 = await dataset.product()
        product4 = await dataset.product()
        product5 = await dataset.product()
        product6 = await dataset.product()
        product7 = await dataset.product()

        samples_data = [
            {
                'product_id': product2.product_id,  # пройдёт
                'mode': 'optional',
                'count': 1,
                'tags': ['packaging'],
            },
            {
                'product_id': product3.product_id,  # не пройдёт
                'mode': 'disabled',
                'count': 1,
                'tags': ['packaging'],
            },
            {
                'product_id': product4.product_id,  # пройдёт
                'mode': 'optional',
                'count': 1,
                'tags': ['packaging'],
                'dttm_start': now() - timedelta(days=1),
            },
            {
                'product_id': product5.product_id,  # не пройдёт
                'mode': 'optional',
                'count': 1,
                'tags': ['packaging'],
                'dttm_till': now() - timedelta(days=1),
            },
            {
                'product_id': product6.product_id,  # пройдёт
                'mode': 'optional',
                'count': 1,
                'tags': ['packaging'],
                'dttm_start': now() - timedelta(days=1),
                'dttm_till': now() + timedelta(days=1),
            },
            {
                'product_id': product7.product_id,  # не пройдёт
                'mode': 'optional',
                'count': 1,
                'tags': ['packaging'],
                'dttm_start': now() - timedelta(days=2),
                'dttm_till': now() - timedelta(days=1),
            },
        ]
        if sampling == 'old':
            kwargs = dict(samples=samples_data)
        else:
            kwargs = dict(samples_ids=[(await dataset.sample(**s)).sample_id
                                       for s in samples_data])
        store = await dataset.store(**kwargs)
        shelf1 = await dataset.shelf(store=store, order=1)
        shelf2 = await dataset.shelf(store=store, order=2)
        shelf3 = await dataset.shelf(store=store, order=2)

        await dataset.stock(
            product=product1,
            shelf=shelf1,
            count=100,
        )
        await dataset.stock(
            product=product2,
            shelf=shelf2,
            count=200,
        )
        await dataset.stock(
            product=product3,
            shelf=shelf3,
            count=300,
        )
        await dataset.stock(
            product=product4,
            shelf=shelf1,
            count=300,
        )
        await dataset.stock(
            product=product5,
            shelf=shelf2,
            count=200,
        )
        await dataset.stock(
            product=product6,
            shelf=shelf3,
            count=100,
        )
        await dataset.stock(
            product=product7,
            shelf=shelf3,
            count=300,
        )

        order = await dataset.order(
            store=store,
            type = 'order',
            status='reserving',
            estatus='begin',
            required = [
                {
                    'product_id': product1.product_id,
                    'count': 10
                },
            ],
        )
        tap.ok(order, 'Заказ создан')

        await wait_order_status(
            order,
            ('reserving', 'suggests_samples_generate'),
        )

        tap.ok(await order.business.order_changed(), 'Исполняем')

        tap.ok(await order.reload(), 'Перезабрали заказ')
        tap.eq(order.status, 'reserving', 'reserving')
        tap.eq(
            order.estatus,
            'suggests_kitchen_generate',
            'suggests_kitchen_generate',
        )
        tap.eq(order.target, 'complete', 'target: complete')

        tap.eq(len(order.problems), 0, 'Нет проблем')

        suggests = await Suggest.list_by_order(order)
        tap.eq(len(suggests), 4, 'Список саджестов')

        samples_true = set([
            samples_data[0]['product_id'],
            samples_data[2]['product_id'],
            samples_data[4]['product_id'],
        ])
        samples_check = {i.product_id for i in suggests}
        samples_check -= set([product1.product_id])
        tap.eq(samples_check, samples_true, 'Сэмплы выбраны верно')

        suggests = dict(((x.shelf_id, x.product_id), x) for x in suggests)

        with suggests[shelf1.shelf_id, product1.product_id] as suggest:
            tap.eq(suggest.count, 10, 'count')
            tap.ok('sample' not in suggest.conditions.tags, 'tags')
            tap.ok('packaging' not in suggest.conditions.tags, 'tags')

        with suggests[shelf2.shelf_id, product2.product_id] as suggest:
            tap.eq(suggest.count, 1, 'count')
            tap.ok('sample' in suggest.conditions.tags, 'tags')
            tap.ok('packaging' in suggest.conditions.tags, 'tags')
            tap.ok(suggest.conditions.all, 'all is True for packaging')


@pytest.mark.parametrize('sampling', ['old', 'new'])
async def test_sampling_condition(
        tap, wait_order_status, dataset, sampling):
    with tap.plan(16, 'Генерация саджестов'):
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
                'count': 1,
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
        shelf1 = await dataset.shelf(store=store, order=1)
        shelf2 = await dataset.shelf(store=store, order=2)
        shelf3 = await dataset.shelf(store=store, order=2)

        await dataset.stock(
            product=product1,
            shelf=shelf1,
            count=100,
        )
        await dataset.stock(
            product=product2,
            shelf=shelf2,
            count=200,
        )
        await dataset.stock(
            product=product3,
            shelf=shelf3,
            count=300,
        )

        order = await dataset.order(
            store=store,
            type='order',
            status='reserving',
            estatus='begin',
            total_price='1234.56',
            required=[
                {
                    'product_id': product1.product_id,
                    'count': 10,
                },
            ],
        )
        tap.ok(order, 'Заказ создан')

        await wait_order_status(
            order,
            ('reserving', 'suggests_samples_generate'),
        )

        tap.ok(await order.business.order_changed(), 'Исполняем')

        tap.ok(await order.reload(), 'Перезабрали заказ')
        tap.eq(order.status, 'reserving', 'reserving')
        tap.eq(
            order.estatus,
            'suggests_kitchen_generate',
            'suggests_kitchen_generate',
        )
        tap.eq(order.target, 'complete', 'target: complete')

        tap.eq(len(order.problems), 0, 'Нет проблем')

        suggests = await Suggest.list_by_order(order)
        tap.eq(len(suggests), 2, 'Список саджестов')
        suggests = dict(((x.shelf_id, x.product_id), x) for x in suggests)

        with suggests[shelf1.shelf_id, product1.product_id] as suggest:
            tap.eq(suggest.count, 10, 'count')
            tap.ok('sample' not in suggest.conditions.tags, 'tags')
            tap.ok('packaging' not in suggest.conditions.tags, 'tags')

        with suggests[shelf3.shelf_id, product3.product_id] as suggest:
            tap.eq(suggest.count, 1, 'count')
            tap.ok('sample' in suggest.conditions.tags, 'tags')
            tap.ok('packaging' not in suggest.conditions.tags, 'tags')
            tap.ok(not suggest.conditions.all, 'all is False')


@pytest.mark.parametrize('sampling', ['old', 'new'])
async def test_condition_children(
        tap, wait_order_status, dataset, sampling):
    with tap.plan(16, 'Генерация саджестов'):
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
                    'condition_type': 'and',
                    'children': [
                        {
                            'condition_type': 'total_price_above',
                            'total_price': '1234.56'
                        },
                        {
                            'condition_type': 'or',
                            'children': [
                                {
                                    'condition_type': 'group_present',
                                    'group_id': group.group_id,
                                },
                                {
                                    'condition_type': 'product_present',
                                    'product_id': 'abrakadabra',
                                },
                            ],
                        },
                    ],
                },
            },
        ]
        if sampling == 'old':
            kwargs = dict(samples=samples_data)
        else:
            kwargs = dict(samples_ids=[(await dataset.sample(**s)).sample_id
                                       for s in samples_data])
        store = await dataset.store(**kwargs)
        shelf1 = await dataset.shelf(store=store, order=1)
        shelf2 = await dataset.shelf(store=store, order=2)
        shelf3 = await dataset.shelf(store=store, order=2)

        await dataset.stock(
            product=product1,
            shelf=shelf1,
            count=100,
        )
        await dataset.stock(
            product=product2,
            shelf=shelf2,
            count=200,
        )
        await dataset.stock(
            product=product3,
            shelf=shelf3,
            count=300,
        )

        order = await dataset.order(
            store=store,
            type='order',
            status='reserving',
            estatus='begin',
            total_price='1234.58',
            required=[
                {
                    'product_id': product1.product_id,
                    'count': 10,
                },
            ],
        )
        tap.ok(order, 'Заказ создан')

        await wait_order_status(
            order,
            ('reserving', 'suggests_samples_generate'),
        )

        tap.ok(await order.business.order_changed(), 'Исполняем')

        tap.ok(await order.reload(), 'Перезабрали заказ')
        tap.eq(order.status, 'reserving', 'reserving')
        tap.eq(
            order.estatus,
            'suggests_kitchen_generate',
            'suggests_kitchen_generate',
        )
        tap.eq(order.target, 'complete', 'target: complete')

        tap.eq(len(order.problems), 0, 'Нет проблем')

        suggests = await Suggest.list_by_order(order)
        tap.eq(len(suggests), 2, 'Список саджестов')
        suggests = dict(((x.shelf_id, x.product_id), x) for x in suggests)

        with suggests[shelf1.shelf_id, product1.product_id] as suggest:
            tap.eq(suggest.count, 10, 'count')
            tap.ok('sample' not in suggest.conditions.tags, 'tags')
            tap.ok('packaging' not in suggest.conditions.tags, 'tags')

        with suggests[shelf2.shelf_id, product2.product_id] as suggest:
            tap.eq(suggest.count, 1, 'count')
            tap.ok('sample' in suggest.conditions.tags, 'tags')
            tap.ok('packaging' not in suggest.conditions.tags, 'tags')
            tap.ok(not suggest.conditions.all, 'all is False')


@pytest.mark.parametrize('sampling', ['old', 'new'])
async def test_one_baton_one_client(tap, dataset, wait_order_status,
                                    uuid, sampling):
    with tap.plan(7, 'клиент получает семпл ровно один раз'):
        product = await dataset.product()
        sample1 = await dataset.product()
        sample2 = await dataset.product()
        sample3 = await dataset.product()

        samples_data = [
            {
                'product_id': sample1.product_id,
                'mode': 'optional',
                'count': 2,
                'tags': ['packaging'],
            },
            {
                'product_id': sample2.product_id,
                'mode': 'optional',
                'count': 3,
                'tags': ['sampling'],
            },
            {
                'product_id': sample3.product_id,
                'mode': 'optional',
                'count': 4,
                'tags': ['sampling'],
            },
        ]
        if sampling == 'old':
            kwargs = dict(samples=samples_data)
        else:
            kwargs = dict(samples_ids=[(await dataset.sample(**s)).sample_id
                                       for s in samples_data])
        store = await dataset.store(**kwargs)

        await dataset.stock(
            product=product, store=store, count=100,
        )
        await dataset.stock(
            product=sample1, store=store, count=200,
        )
        await dataset.stock(
            product=sample2, store=store, count=300,
        )
        await dataset.stock(
            product=sample3, store=store, count=400,
        )

        client_id = uuid()

        samples = await ClientStash.samples(
            client_id, [sample1.product_id, sample2.product_id],
        )

        tap.ok(samples, 'сделали вид, что клиент уже получал семплы')

        order = await dataset.order(
            store=store,
            type='order',
            status='reserving',
            required=[
                {
                    'product_id': product.product_id,
                    'count': 10
                },
            ],
            attr={'client_id': client_id},
        )

        await wait_order_status(
            order, ('reserving', 'suggests_samples_generate'),
        )

        tap.ok(await order.business.order_changed(), 'генерируем саджесты')

        suggests = {
            s.product_id: s for s in await Suggest.list_by_order(order)
        }

        tap.eq(len(suggests), 3, 'получили саджесты')
        tap.ok(suggests[product.product_id], 'есть саджест для товара')
        tap.ok(suggests[sample1.product_id], 'есть саджест для пакета')
        tap.ok(
            suggests[sample3.product_id],
            'есть саджест для семпла, который еще не получал клиента',
        )


@pytest.mark.parametrize('sampling', ['old', 'new'])
async def test_same_client_ttl(tap, dataset, wait_order_status,
                               uuid, now, sampling):
    with tap.plan(8, 'клиент получает семпл не слишком часто'):
        product = await dataset.product()
        sample1 = await dataset.product()
        sample2 = await dataset.product()
        sample3 = await dataset.product()
        sample4 = await dataset.product()
        sample5 = await dataset.product()

        samples_data = [
            {
                'product_id': sample1.product_id,
                'mode': 'optional',
                'count': 2,
                'tags': ['packaging'],
            },
            {
                'product_id': sample2.product_id,
                'mode': 'optional',
                'count': 3,
                'tags': ['sampling'],
                'same_client_ttl': 10,
            },
            {
                'product_id': sample3.product_id,
                'mode': 'optional',
                'count': 4,
                'tags': ['sampling'],
                'same_client_ttl': 20,
            },
            {
                'product_id': sample4.product_id,
                'mode': 'optional',
                'count': 1,
                'tags': ['sampling'],
                'same_client_ttl': 0,
            },
            {
                'product_id': sample5.product_id,
                'mode': 'optional',
                'count': 1,
                'tags': ['sampling'],
                'same_client_ttl': None,
            },
        ]
        if sampling == 'old':
            kwargs = dict(samples=samples_data)
        else:
            kwargs = dict(samples_ids=[(await dataset.sample(**s)).sample_id
                                       for s in samples_data])
        store = await dataset.store(**kwargs)

        await dataset.stock(
            product=product, store=store, count=100,
        )
        await dataset.stock(
            product=sample1, store=store, count=200,
        )
        await dataset.stock(
            product=sample2, store=store, count=300,
        )
        await dataset.stock(
            product=sample3, store=store, count=400,
        )
        await dataset.stock(
            product=sample4, store=store, count=400,
        )
        await dataset.stock(
            product=sample5, store=store, count=400,
        )

        client_id = uuid()

        stash = Stash({
            'name': f'{client_id}:samples',
            'value': {
                sample1.product_id: now() - timedelta(days=1),
                sample2.product_id: now() - timedelta(days=9),
                sample3.product_id: now() - timedelta(days=21),
                sample4.product_id: now(),
                sample5.product_id: now() - timedelta(days=29),
            },
            'expired': now() + timedelta(days=30),
        })
        await stash.save()

        tap.note('сделали вид, что клиент уже получал семплы, '
                 'один 9 дней назад, другой 21 день назад, '
                 'третий совсем недавно, четвертый 29 дней назад')

        order = await dataset.order(
            store=store,
            type='order',
            status='reserving',
            required=[
                {
                    'product_id': product.product_id,
                    'count': 10
                },
            ],
            attr={'client_id': client_id},
        )

        await wait_order_status(
            order, ('reserving', 'suggests_samples_generate'),
        )

        tap.ok(await order.business.order_changed(), 'генерируем саджесты')

        suggests = {
            s.product_id: s for s in await Suggest.list_by_order(order)
        }

        tap.eq(len(suggests), 5, 'получили саджесты')
        tap.ok(suggests.get(product.product_id), 'есть саджест для товара')
        tap.ok(suggests.get(sample1.product_id), 'есть саджест для пакета')
        tap.ok(
            suggests.get(sample3.product_id),
            'есть саджест для семпла, у которого TTL 20, '
            'а выдавался он 21 день назад',
        )
        tap.ok(
            suggests.get(sample4.product_id),
            'есть саджест для семпла, который можно класть без ограничений',
        )
        tap.ok(
            suggests.get(sample5.product_id),
            'есть саджест для семпла, у которого TTL None, '
            'а выдавался он 29 дней назад',
        )
