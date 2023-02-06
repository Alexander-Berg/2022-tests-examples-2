import pytest


@pytest.fixture(name='reserved_components')
def reserved_components_fixture():
    return {
        'latte': [
            [
                {'product_id': 'coffee1', 'count': 4, 'portions': 1},
                {'product_id': 'coffee2', 'count': 4, 'portions': 1},
                {'product_id': 'coffee3', 'count': 4, 'portions': 1},
            ],
            [
                {'product_id': 'milk1', 'count': 120, 'portions': 3},
            ],
            [
                {'product_id': 'glass1', 'count': 1, 'portions': 3},
            ]
        ],
        'lungo': [
            [
                {'product_id': 'coffee1', 'count': 4, 'portions': 4},
            ],
            [
                {'product_id': 'glass1', 'count': 1, 'portions': 4},
            ]
        ],
    }


async def test_add(tap, dataset):
    with tap.plan(16, 'добавление в reserved_components'):
        order = await dataset.order()

        tap.eq(order.components.value, {}, 'чистый варс')

        order.components.add(
            'latte',
            [
                {'product_id': 'coffee1', 'count': 4},
                {'product_id': 'milk1', 'count': 120},
                {'product_id': 'glass1', 'count': 1},
            ]
        )
        tap.eq(order.components.total('latte'), 1, 'одна порция латте создана')
        tap.eq(order.components.total('coffee1'), 4, 'кофе1')
        tap.eq(order.components.total('milk1'), 120, 'молоко1')
        tap.eq(order.components.total('glass1'), 1, 'стакан1')

        order.components.add(
            'latte',
            [
                {'product_id': 'coffee2', 'count': 4},
                {'product_id': 'milk1', 'count': 120},
                {'product_id': 'glass1', 'count': 1},
            ]
        )
        tap.eq(
            order.components.total('latte'),
            2,
            'добавили порцию латте с кофе2',
        )
        tap.eq(order.components.total('coffee1'), 4, 'кофе1')
        tap.eq(order.components.total('coffee2'), 4, 'кофе2')
        tap.eq(order.components.total('milk1'), 120 * 2, 'молоко1')
        tap.eq(order.components.total('glass1'), 1 * 2, 'стакан1')

        with tap.raises(AssertionError, 'все компоненты порции или ничего'):
            order.components.add(
                'latte',
                [
                    {'product_id': 'glass1', 'count': 1},
                ]
            )

        order.components.add(
            'lungo',
            [
                {'product_id': 'coffee2', 'count': 4},
                {'product_id': 'glass1', 'count': 1},
            ]
        )
        tap.eq(
            order.components.total('lungo'),
            1,
            'новая позиция -- лунго',
        )
        tap.eq(order.components.total('coffee1'), 4, 'кофе1')
        tap.eq(order.components.total('coffee2'), 4 * 2, 'кофе2')
        tap.eq(order.components.total('milk1'), 120 * 2, 'молоко1')
        tap.eq(order.components.total('glass1'), 1 * 3, 'стакан1')


async def test_rm_over(tap, dataset, reserved_components):
    with tap.plan(7, 'убираем лишние порции'):
        order = await dataset.order(
            vars={'reserved_components': reserved_components},
        )
        tap.eq(order.components.total('latte'), 3, 'три латте')
        tap.eq(order.components.total('lungo'), 4, 'четыре лунго')

        order.components.rm_over('latte', 3)
        tap.eq(order.components.total('latte'), 3, 'латте не изменилось')

        order.components.rm_over('lungo', 3)
        tap.eq(order.components.total('lungo'), 3, 'лунго теперь три')

        order.components.rm_over('latte', 0)
        tap.eq(order.components.total('latte'), 0, 'все латте по нулям')
        tap.ok('latte' not in order.components, 'убрали латте')

        tap.eq(len(order.components), 1, 'остался один товар')


async def test_total_by_product(tap, dataset, reserved_components, uuid):
    with tap.plan(3, 'общее количество порций для товара'):
        order = await dataset.order(
            vars={'reserved_components': reserved_components},
        )
        tap.eq(order.components.total('latte'), 3, 'три латте')
        tap.eq(order.components.total('lungo'), 4, 'четыре лунго')
        tap.eq(order.components.total(uuid()), 0, 'нет такого товара')


async def test_total_by_component(tap, dataset, reserved_components, uuid):
    with tap.plan(6, 'общее количество минимальных единиц для компонента'):
        order = await dataset.order(
            vars={'reserved_components': reserved_components},
        )
        tap.eq(
            order.components.total('coffee1'),
            4 * 1 + 4 * 4,
            'кофе1',
        )
        tap.eq(
            order.components.total('coffee2'),
            4 * 1,
            'кофе2',
        )
        tap.eq(
            order.components.total('coffee3'),
            4 * 1,
            'кофе3',
        )
        tap.eq(
            order.components.total('milk1'),
            120 * 3,
            'молоко1',
        )
        tap.eq(
            order.components.total('glass1'),
            1 * 3 + 1 * 4,
            'стакан1',
        )
        tap.eq(
            order.components.total(uuid()),
            0,
            'нет такого компонента',
        )


async def test_contains(tap, dataset, reserved_components, uuid):
    with tap.plan(5, 'поиск товара/компонента по айди'):
        order1 = await dataset.order()
        tap.eq(
            order1.components.value,
            dict(),
            'пустой варс',
        )
        tap.ok(
            uuid() not in order1.components, 'не падаем на пустом варс'
        )

        order2 = await dataset.order(
            vars={'reserved_components': reserved_components},
        )
        tap.is_ok(
            order2.components.value,
            order2.vars['reserved_components'],
            'не пустой варс',
        )
        tap.ok('latte' in order2.components, 'нашли товар')
        tap.ok('coffee1' in order2.components, 'нашли компонент')


async def test_proxy(tap, dataset, reserved_components):
    with tap.plan(2, 'получаем нужный ключ из варс'):
        order1 = await dataset.order()
        tap.eq(
            order1.components.value,
            dict(),
            'пустой варс',
        )

        order2 = await dataset.order(
            vars={'reserved_components': reserved_components},
        )
        tap.is_ok(
            order2.components.value,
            order2.vars['reserved_components'],
            'не пустой варс',
        )


async def test_side_effects(tap, dataset, reserved_components):
    with tap.plan(2, 'объект не шарит данные'):
        order1 = await dataset.order(
            vars={'reserved_components': reserved_components},
        )
        order2 = await dataset.order(
            vars={'reserved_components': reserved_components},
        )

        tap.eq(
            order1.components.total('lungo'),
            order2.components.total('lungo'),
            'одинаковое количество порций на старте',
        )

        order1.components.add(
            'lungo',
            [
                {'product_id': 'coffee2', 'count': 4, 'portions': 1},
                {'product_id': 'glass2', 'count': 1, 'portions': 1},
            ]
        )

        tap.ne_ok(
            order1.components.total('lungo'),
            order2.components.total('lungo'),
            'в первом заказе стало больше порций',
        )


async def test_list_variants(tap, dataset, reserved_components):
    with tap.plan(4, 'проход по вариантам'):
        order = await dataset.order(
            vars={'reserved_components': reserved_components},
        )

        tap.eq(
            [i['product_id'] for i in order.components.list_variants()],
            [
                'coffee1',
                'coffee2',
                'coffee3',
                'milk1',
                'glass1',
                'coffee1',
                'glass1',
            ],
            'варианты для все составных продуктов',
        )

        tap.eq(
            [
                i['product_id']
                for i in order.components.list_variants('latte')
            ],
            ['coffee1', 'coffee2', 'coffee3', 'milk1', 'glass1'],
            'варианты для латте',
        )

        tap.eq(
            [
                i['product_id']
                for i in order.components.list_variants('lungo')
            ],
            ['coffee1', 'glass1'],
            'варианты для лунго',
        )

        tap.eq(
            [
                i['product_id']
                for i in order.components.list_variants('xxx')
            ],
            [],
            'варианты для несуществующего продукта',
        )
