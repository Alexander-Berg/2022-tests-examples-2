from collections import defaultdict

import pytest

from stall.scripts import autoorder

# pylint: disable-msg=too-many-locals


async def test_gen_stocks(tap, dataset):
    with tap.plan(5, 'Генерация остатков для расчета автозаказа'):
        store1 = await dataset.store(status='active', source='wms')
        store2 = await dataset.store(status='disabled', source='wms')
        store3 = await dataset.store(status='active', source='1c')

        store1_shelf1 = await dataset.shelf(store=store1, type='store')
        store1_shelf2 = await dataset.shelf(store=store1, type='store')
        store1_shelf3 = await dataset.shelf(store=store1, type='markdown')
        store1_shelf4 = await dataset.shelf(store=store1, type='office')
        store2_shelf1 = await dataset.shelf(store=store2, type='store')
        store3_shelf1 = await dataset.shelf(store=store3, type='store')

        product1 = await dataset.product()
        product2 = await dataset.product(status='disabled')
        product3 = await dataset.product(
            vars={
                'imported': {
                    'nomenclature_type': 'consumable',
                }
            }
        )

        await dataset.stock(
            store=store1, shelf=store1_shelf1, product=product1, count=1,
        )
        await dataset.stock(
            store=store1, shelf=store1_shelf2, product=product1, count=3,
        )
        await dataset.stock(
            store=store1, shelf=store1_shelf3, product=product1, count=5,
        )
        await dataset.stock(
            store=store1, shelf=store1_shelf4, product=product3, count=2,
        )

        await dataset.stock(
            store=store2, shelf=store2_shelf1, product=product1, count=1,
        )
        await dataset.stock(
            store=store2, shelf=store2_shelf1, product=product2, count=7,
        )

        await dataset.stock(
            store=store3, shelf=store3_shelf1, product=product1, count=1,
        )

        stocks = {}
        async for i in autoorder.gen_stocks(
                store_id=[
                    store1.store_id,
                    store2.store_id,
                    store3.store_id,
                ],
                product_id=[
                    product1.product_id,
                    product2.product_id,
                    product3.product_id,
                ],
        ):
            key = (i['warehouse_id'], i['lavka_id'])
            stocks[key] = i

        tap.eq_ok(
            stocks[(store1.external_id, product1.external_id)]['qty'],
            4,
            'Остаток из первой лавки для первого продукта '
            'с трех полок схлопнулся',
        )
        tap.eq_ok(
            stocks[(store1.external_id, product3.external_id)]['qty'],
            2,
            'Остаток из первой лавки для третьего продукта ',
        )
        tap.eq_ok(
            stocks[(store2.external_id, product1.external_id)]['qty'],
            1,
            'Остаток из второй лавки для первого продукта',
        )
        tap.eq_ok(
            stocks[(store2.external_id, product2.external_id)]['qty'],
            7,
            'Остаток из второй лавки для второго продукта',
        )

        tap.ok(
            (store3.external_id, product1.external_id) not in stocks,
            'Только ВМСные лавки',
        )


@pytest.mark.parametrize(
    'variant',
    [
        (
            'дефолтный квант -- суммируем остатки',
            1,
            {'store': 1, 'kitchen_components': 2, 'markdown': 3},
            1 + 2,
        ),
        (
            'на ПФ полке остаток делится на квант',
            3,
            {'store': 8, 'kitchen_components': 9, 'markdown': 3, 'office': 1},
            8 + 9 / 3 + 1,
        ),
        (
            'на ПФ полке остаток округляем до целого в меньшую сторону',
            3,
            {'store': 8, 'kitchen_components': 10, 'markdown': 3},
            8 + int(10 / 3),
        ),
    ],
)
async def test_quants(tap, dataset, variant):
    msg, quants, stocks, result_qty = variant

    with tap.plan(1, msg):

        store = await dataset.store(status='active', source='wms')
        product = await dataset.product(quants=quants)

        for shelf_type, count in stocks.items():
            shelf = await dataset.shelf(store=store, type=shelf_type)
            await dataset.stock(shelf=shelf, product=product, count=count)

        result = defaultdict(int)
        async for i in autoorder.gen_stocks(
                store_id=store.store_id,
                product_id=product.product_id,
        ):
            result[(i['warehouse_id'], i['lavka_id'])] += i['qty']

        tap.eq(
            result[store.external_id, product.external_id],
            result_qty,
            'корректное количество',
        )
