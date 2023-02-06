from stall.scripts import check_store_stocks


async def test_check_store_stocks(tap, dataset):
    with tap.plan(5):
        group_a = await dataset.product_group()
        group_aa = await dataset.product_group(
            parent_group_id=group_a.group_id,
        )
        group_aaa = await dataset.product_group(
            parent_group_id=group_aa.group_id,
        )
        group_ab = await dataset.product_group(
            parent_group_id=group_a.group_id,
        )

        product = await dataset.product(
            groups=[group_aaa.group_id, group_ab.group_id]
        )

        assortment_a = await dataset.assortment()
        await dataset.assortment_product(
            assortment=assortment_a, product=product,
        )

        store = await dataset.store(
            assortment_id=assortment_a.assortment_id,
            group_id=group_a.group_id,
        )

        stocks = []
        for _ in range(3):
            shelf = await dataset.shelf(store=store)
            stocks.append(
                await dataset.stock(
                    store=store, shelf=shelf, product=product, count=1,
                )
            )

        tap.eq_ok(
            len(await check_store_stocks.process(store.store_id)),
            0,
            'все прекрасно',
        )

        group_aa.status = 'disabled'
        await group_aa.save()

        tap.eq_ok(
            len(await check_store_stocks.process(store.store_id)),
            0,
            'одна из веток выключена, но все равно норм',
        )

        group_ab.status = 'disabled'
        await group_ab.save()

        tap.eq_ok(
            len(await check_store_stocks.process(store.store_id)),
            1,
            'во всех ветках есть выключенные групы',
        )

        group_aa.status = 'active'
        await group_aa.save()
        group_ab.status = 'active'
        await group_ab.save()

        group_d = await dataset.product_group()
        store.group_id = group_d.group_id
        await store.save()

        tap.eq_ok(
            len(await check_store_stocks.process(store.store_id)),
            1,
            'продукт не в группе склада',
        )

        assortment_b = await dataset.assortment()
        store.assortment_id = assortment_b.assortment_id
        await store.save()

        tap.eq_ok(
            len(await check_store_stocks.process(store.store_id)),
            1,
            'продукт не в ассортименте склада',
        )


async def test_check_tags(tap, dataset):
    group = await dataset.product_group()
    product1 = await dataset.product(tags=['freezer'], groups=[group.group_id])
    product2 = await dataset.product(tags=['freezer2_2'],
                                     groups=[group.group_id])
    assortment = await dataset.assortment()
    await dataset.assortment_product(
        assortment=assortment, product=product1,
    )
    await dataset.assortment_product(
        assortment=assortment, product=product2,
    )
    store = await dataset.store(assortment_id=assortment.assortment_id,
                                group_id=group.group_id)
    shelf = await dataset.shelf(tags=['freezer2_2'], store_id=store.store_id)
    await dataset.stock(shelf=shelf, product=product1, shelf_type='store')
    await dataset.stock(shelf=shelf, product=product2, shelf_type='store')

    bad_products = await check_store_stocks.process(store.store_id)

    tap.eq_ok(
        list(bad_products),
        [product1.product_id],
        'Correct product in problems'
    )
    tap.eq_ok(
        list(bad_products[product1.product_id]['problems']),
        ['tags'],
        'Correct type of problems'
    )
    tap.eq_ok(
        bad_products[product1.product_id]['problems']['tags'],
        'тэги продукта отличаются от тэгов полки',
        'Correct message'
    )
