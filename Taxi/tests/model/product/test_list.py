from stall.model.product import Product


async def test_filter_by_title(tap, dataset, uuid):
    with tap.plan(4):
        title1 = uuid()

        cursor = await Product.list(by='look', title=title1)
        tap.eq_ok(cursor.list, [], 'no products with title1')

        for _ in range(5):
            await dataset.product(title=title1)

        cursor = await Product.list(by='look', title=title1)
        tap.eq_ok(len(cursor.list), 5, '5 products with title1')
        tap.ok(
            all(i.title.startswith(title1) for i in cursor.list),
            'all products with correct title',
        )

        title2 = uuid()

        for i in range(5):
            await dataset.product(title=f'{title2}-{i}')

        cursor = await Product.list(by='look', title=title2)
        tap.eq_ok(len(cursor.list), 5, '5 products with title2')




async def test_filter_by_ids(tap, dataset, uuid):
    with tap.plan(3):

        cursor = await Product.list(by='look', ids=[uuid(), uuid()])
        tap.eq_ok(cursor.list, [], 'no products with ids')

        products = [await dataset.product() for _ in range(5)]

        cursor = await Product.list(
            by='look', ids=[i.product_id for i in products],
        )
        tap.eq_ok(len(cursor.list), 5, '5 products with ids')
        tap.eq_ok(
            {i.product_id for i in cursor.list},
            {i.product_id for i in products},
            'all products with correct ids',
        )




async def test_cursor(tap, dataset, uuid):
    with tap.plan(6):
        title = uuid()

        for _ in range(5):
            await dataset.product(title=title)

        cursor = await Product.list(by='look', title=title, limit=2)
        tap.eq_ok(len(cursor.list), 2, '2 products with title')
        tap.ok(cursor.cursor_str, 'try next page')

        cursor = await Product.list(
            by='look',
            title=title,
            cursor_str=cursor.cursor_str,
        )
        tap.eq_ok(len(cursor.list), 2, '2 more products with title')
        tap.ok(cursor.cursor_str, 'try next page')

        cursor = await Product.list(
            by='look',
            title=title,
            cursor_str=cursor.cursor_str,
        )
        tap.eq_ok(len(cursor.list), 1, 'last product with title')
        tap.ok(not cursor.cursor_str, 'latest page')
