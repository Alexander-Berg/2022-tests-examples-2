from stall.model.product_components import ProductComponents, ProductVariant


async def test_instance(tap, uuid):
    with tap.plan(8, 'кофе с молоком'):
        pid1 = uuid()
        pid2 = uuid()
        pid3 = uuid()
        pid4 = uuid()

        components = ProductComponents(
            [
                [
                    {
                        'product_id': pid1,
                        'count': 3500,
                    },
                ],
                [
                    ProductVariant(
                        {
                            'product_id': pid2,
                            'count': 80,
                        }
                    )
                ],
                [
                    {
                        'product_id': pid3,
                    },
                    ProductVariant(
                        {
                            'product_id': pid4,
                        }
                    ),
                ],
                # пустоты пропускаем
                [],
            ]
        )

        tap.eq_ok(len(components), 3, 'Минимальное кофейное блюдо')

        tap.eq_ok(components[0][0].product_id, pid1, '1 вид кофе')
        tap.eq_ok(components[0][0].count, 3500, '3.5 г в мг')

        tap.eq_ok(
            components[1][0].product_id,
            pid2,
            'молоко 2 вариант',
        )

        tap.eq_ok(
            components[2][0].product_id,
            pid3,
            'тара 1 вариант',
        )
        tap.eq_ok(components[2][0].count, 1, 'дефолтное количество')
        tap.eq_ok(
            components[2][1].product_id,
            pid4,
            'тара 2 вариант',
        )
        tap.eq_ok(components[2][1].count, 1, 'дефолтное количество')


async def test_bool(tap, uuid):
    with tap.plan(2):
        components = ProductComponents(
            [
                [
                    {
                        'product_id': uuid(),
                        'count': 1,
                    },
                ],
            ],
        )
        tap.ok(bool(components) is True, 'не пустые компоненты -- правда')

        components = ProductComponents([])
        tap.ok(bool(components) is False, 'пустые компоненты -- ложь')


async def test_in(tap, uuid):
    with tap.plan(5):
        pid1 = uuid()
        pid2 = uuid()
        pid3 = uuid()

        components = ProductComponents(
            [
                [
                    {
                        'product_id': pid1,
                        'count': 1,
                    },
                ],
                [
                    {
                        'product_id': pid2,
                        'count': 1,
                    },
                    {
                        'product_id': pid3,
                        'count': 1,
                    },
                ],
            ],
        )
        tap.ok(pid1 in components, 'нашли')
        tap.ok(pid2 in components, 'нашли')
        tap.ok(pid3 in components, 'нашли')
        tap.ok(uuid() not in components, 'не нашли')

        components = ProductComponents([])
        tap.ok(uuid() not in components, 'не нашли')
