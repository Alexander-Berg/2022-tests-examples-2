from stall.model.assortment_product import AssortmentProduct


async def test_list_by_look(tap, dataset):
    with tap.plan(7):
        assortment = await dataset.assortment()

        cursor = await AssortmentProduct.list(
            by='look',
            assortment_ids=[assortment.assortment_id],
        )
        tap.eq_ok(cursor.list, [], 'no items')

        products = [await dataset.product() for _ in range(5)]
        for product in products:
            await dataset.assortment_product(
                assortment_id=assortment.assortment_id,
                product_id=product.product_id,
            )

        cursor = await AssortmentProduct.list(
            by='look',
            assortment_ids=[assortment.assortment_id],
        )
        tap.eq_ok(
            len(cursor.list), len(products), 'correct number of products',
        )
        tap.eq_ok(
            {i.assortment_id for i in cursor.list},
            {assortment.assortment_id},
            'all products with correct assortment_id',
        )

        one_more_assortment = await dataset.assortment()
        one_more_product = await dataset.assortment_product(
            assortment_id=one_more_assortment.assortment_id
        )
        await dataset.assortment_product(
            assortment_id=one_more_assortment.assortment_id,
            product_id=one_more_product.product_id,
        )

        cursor = await AssortmentProduct.list(
            by='look',
            assortment_ids=[
                assortment.assortment_id,
                one_more_assortment.assortment_id,
            ],
            limit=5,
        )
        tap.eq_ok(len(cursor.list), 5, '5 products')
        tap.ok(cursor.cursor_str, 'try next page')

        cursor = await AssortmentProduct.list(
            by='look',
            assortment_ids=[
                assortment.assortment_id,
                one_more_assortment.assortment_id,
            ],
            cursor_str=cursor.cursor_str,
        )
        tap.eq_ok(len(cursor.list), 1, 'last product')
        tap.is_ok(cursor.cursor_str, None, 'latest page')


