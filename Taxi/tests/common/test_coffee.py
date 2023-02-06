async def test_kitchen(tap, dataset):
    with tap:
        store = await dataset.store()
        shelves_meta = (
            ('store', 'store'),
            ('comp1', 'kitchen_components'),
            ('comp2', 'kitchen_components'),
        )
        stocks_meta = (
            ('comp1', 'coffee1', 1),
            ('comp1', 'coffee2', 1),
            ('comp1', 'milk1', 2),
            ('comp1', 'milk2', 2),
            ('comp1', 'glass1', 3),
            ('comp2', 'glass2', 3),
        )
        shelves, stocks, components, products = await dataset.coffee(
            shelves_meta=shelves_meta,
            stocks_meta=stocks_meta,
            store=store,
        )

        tap.eq(
            ('coffee1', 'coffee2', 'milk1', 'milk2', 'glass1', 'glass2'),
            tuple(components.keys()),
            'компоненты для приготовления кофе',
        )
        tap.eq(
            ('cappuccino', 'latte', 'lungo'),
            tuple(products.keys()),
            'рецепты кофе',
        )
        tap.eq(
            shelves_meta,
            tuple((i.title, i.type) for i in shelves.values()),
            'правильные полки',
        )

        for shelf_k, component_k, count in stocks_meta:
            stocks = await dataset.Stock.list_by_product(
                product_id=components[component_k].product_id,
                store_id=store.store_id,
                shelf_type=shelves[shelf_k].type,
            )
            tap.eq(len(stocks), 1, 'одна запись в остатках')

            tap.eq(
                stocks[0].count,
                count * components[component_k].quants,
                f'остаток в дольках для компонента {component_k}',
            )
            tap.eq(stocks[0].reserve, 0, 'резерва нет')
