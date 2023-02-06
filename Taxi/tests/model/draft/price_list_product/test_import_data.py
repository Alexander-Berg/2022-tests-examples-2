import pytest

from stall.model.draft.price_list_product import (DraftPriceListProduct,
                                                  import_data)


async def test_create(tap, dataset):
    with tap.plan(3):
        store = await dataset.store()
        user = await dataset.user(store=store)
        pl = await dataset.draft_price_list()
        products = [await dataset.product() for _ in range(5)]
        s = await dataset.stash(
            value={
                'store_id': store.store_id,
                'user_id': user.user_id,
                'price_list_id': pl.price_list_id,
                'products': [
                    {
                        'external_id': i.external_id,
                        'store': '3.14',
                        'markdown': 42,
                    }
                    for i in products
                ],
                'mark_removed': False,
            }
        )

        await import_data(s.stash_id)

        added_pps = await DraftPriceListProduct.list(
            by='full',
            conditions=[('price_list_id', '=', pl.price_list_id)],
        )

        tap.eq_ok(
            {i.product_id for i in added_pps},
            {i.product_id for i in products},
            'Price-list has correct products',
        )

        tap.eq_ok(
            {str(i.price['store']) for i in added_pps},
            {'3.14'},
            'Price-list has correct product prices for store type',
        )

        tap.eq_ok(
            {str(i.price['markdown']) for i in added_pps},
            {'42.00'},
            'Price-list has correct product prices for markdown type',
        )


@pytest.mark.parametrize('price_type', ['store', 'markdown'])
async def test_create_one_price_only(tap, dataset, price_type):
    with tap.plan(3):
        store = await dataset.store()
        user = await dataset.user(store=store)
        pl = await dataset.draft_price_list()
        products = [await dataset.product() for _ in range(5)]
        price_values = ['3.14', '15.00', '92.60', '2.71', '1.99']
        s = await dataset.stash(
            value={
                'store_id': store.store_id,
                'user_id': user.user_id,
                'price_list_id': pl.price_list_id,
                'products': [
                    {
                        'external_id': i.external_id,
                        price_type: price,
                    }
                    for i, price in zip(products, price_values)
                ],
                'mark_removed': False,
            }
        )

        await import_data(s.stash_id)

        added_pps = await DraftPriceListProduct.list(
            by='full',
            conditions=[('price_list_id', '=', pl.price_list_id)],
        )

        tap.eq_ok(
            {i.product_id for i in added_pps},
            {i.product_id for i in products},
            'Price-list has correct products',
        )

        tap.eq_ok(
            {str(i.price[price_type]) for i in added_pps},
            set(price_values),
            f'Price-list has correct product prices for {price_type} type',
        )
        other_price = next(iter({'store', 'markdown'} - {price_type}))
        tap.ok(
            all(other_price not in i.price for i in added_pps),
            f'Price {other_price} is not present'
        )


async def test_update_price(tap, dataset):
    with tap.plan(8):
        store = await dataset.store()
        user = await dataset.user(store=store)
        pl = await dataset.draft_price_list()
        products = [await dataset.product() for _ in range(5)]

        for p in products:
            pp = DraftPriceListProduct(
                {
                    'price_list_id': pl.price_list_id,
                    'product_id': p.product_id,
                    'price': {'store': 1984},
                }
            )
            await pp.save()
            tap.ok(pp.pp_id, 'Price saved')

        s = await dataset.stash(
            value={
                'store_id': store.store_id,
                'user_id': user.user_id,
                'price_list_id': pl.price_list_id,
                'products': [
                    {
                        'external_id': i.external_id,
                        'store': '3.14',
                        'markdown': '42',
                    }
                    for i in products
                ],
                'mark_removed': False,
            }
        )

        await import_data(s.stash_id)

        updated_pps = await DraftPriceListProduct.list(
            by='full',
            conditions=[('price_list_id', '=', pl.price_list_id)],
        )

        tap.eq_ok(
            {i.product_id for i in updated_pps},
            {i.product_id for i in products},
            'Price-list has correct products',
        )

        tap.eq_ok(
            {str(i.price['store']) for i in updated_pps},
            {'3.14'},
            'Price-list has correct product prices for store type',
        )

        tap.eq_ok(
            {str(i.price['markdown']) for i in updated_pps},
            {'42.00'},
            'Price-list has correct product prices for markdown type',
        )


async def test_update_store_only(tap, dataset):
    with tap.plan(6):
        store = await dataset.store()
        user = await dataset.user(store=store)
        pl = await dataset.draft_price_list()
        products = [await dataset.product() for _ in range(3)]

        initial_store_prices = ['123.11', '234.11', '345.11']
        new_store_prices = ['678.22', '890.22', '']
        initial_markdown_prices = ['12.01', '23.01', '34.01']

        for p, s, m in zip(products,
                           initial_store_prices,
                           initial_markdown_prices):
            pp = DraftPriceListProduct(
                {
                    'price_list_id': pl.price_list_id,
                    'product_id': p.product_id,
                    'price': {'store': s, 'markdown': m},
                }
            )
            await pp.save()
            tap.ok(pp.pp_id, 'Price saved')

        s = await dataset.stash(
            value={
                'store_id': store.store_id,
                'user_id': user.user_id,
                'price_list_id': pl.price_list_id,
                'products': [
                    {
                        'external_id': i.external_id,
                        'store': price,
                    }
                    for i, price in zip(products, new_store_prices)
                ],
                'mark_removed': False,
            }
        )

        await import_data(s.stash_id)

        updated_pps = await DraftPriceListProduct.list(
            by='full',
            conditions=[('price_list_id', '=', pl.price_list_id)],
        )

        tap.eq_ok(
            {i.product_id for i in updated_pps},
            {i.product_id for i in products},
            'Price-list has correct products',
        )

        tap.eq_ok(
            {str(i.price['store']) for i in updated_pps},
            {'678.22', '890.22', 'None'},
            'Price-list has correct product prices for store type',
        )

        tap.eq_ok(
            {str(i.price['markdown']) for i in updated_pps},
            set(initial_markdown_prices),
            'Price-list has correct product prices for markdown type',
        )


async def test_update_markdown_only(tap, dataset):
    with tap.plan(6):
        store = await dataset.store()
        user = await dataset.user(store=store)
        pl = await dataset.draft_price_list()
        products = [await dataset.product() for _ in range(3)]

        initial_store_prices = ['123.11', '234.11', '345.11']
        initial_markdown_prices = ['12.01', '23.01', '34.01']
        new_markdown_prices = ['678.22', '890.22', '']

        for p, s, m in zip(products,
                           initial_store_prices,
                           initial_markdown_prices):
            pp = DraftPriceListProduct(
                {
                    'price_list_id': pl.price_list_id,
                    'product_id': p.product_id,
                    'price': {'store': s, 'markdown': m},
                }
            )
            await pp.save()
            tap.ok(pp.pp_id, 'Price saved')

        s = await dataset.stash(
            value={
                'store_id': store.store_id,
                'user_id': user.user_id,
                'price_list_id': pl.price_list_id,
                'products': [
                    {
                        'external_id': i.external_id,
                        'markdown': price,
                    }
                    for i, price in zip(products, new_markdown_prices)
                ],
                'mark_removed': False,
            }
        )

        await import_data(s.stash_id)

        updated_pps = await DraftPriceListProduct.list(
            by='full',
            conditions=[('price_list_id', '=', pl.price_list_id)],
        )

        tap.eq_ok(
            {i.product_id for i in updated_pps},
            {i.product_id for i in products},
            'Price-list has correct products',
        )

        tap.eq_ok(
            {str(i.price['store']) for i in updated_pps},
            set(initial_store_prices),
            'Price-list has correct product prices for store type',
        )

        tap.eq_ok(
            {str(i.price['markdown']) for i in updated_pps},
            {'678.22', '890.22', 'None'},
            'Price-list has correct product prices for markdown type',
        )


async def test_update_status(tap, dataset):
    with tap.plan(8):
        store = await dataset.store()
        user = await dataset.user(store=store)
        pl = await dataset.draft_price_list()
        products = [await dataset.product() for _ in range(5)]

        for p in products:
            pp = DraftPriceListProduct(
                {
                    'price_list_id': pl.price_list_id,
                    'product_id': p.product_id,
                    'price': {'store': 1984},
                }
            )
            await pp.save()
            tap.ok(pp.pp_id, 'Price saved')

        s = await dataset.stash(
            value={
                'store_id': store.store_id,
                'user_id': user.user_id,
                'price_list_id': pl.price_list_id,
                'products': [
                    {
                        'external_id': products[0].external_id,
                        'store': '3.14',
                    },
                ],
                'mark_removed': True,
            }
        )

        await import_data(s.stash_id)

        updated_pps = await DraftPriceListProduct.list(
            by='full',
            conditions=[('price_list_id', '=', pl.price_list_id)],
        )

        tap.eq_ok(
            {i.product_id for i in updated_pps},
            {i.product_id for i in products},
            'Price-list has correct products',
        )

        tap.eq_ok(
            len([i.status for i in updated_pps if i.status == 'removed']),
            4,
            'Some products removed',
        )
        tap.eq_ok(
            len([i.status for i in updated_pps if i.status == 'active']),
            1,
            'Single product active',
        )


async def test_bad_price_field(tap, dataset):
    with tap:
        store = await dataset.store()
        user = await dataset.user(store=store)
        pl = await dataset.draft_price_list()
        products = [await dataset.product() for _ in range(5)]
        s = await dataset.stash(
            value={
                'store_id': store.store_id,
                'user_id': user.user_id,
                'price_list_id': pl.price_list_id,
                'products': [
                    {
                        'external_id': products[0]['external_id'],
                        'store': '3.14',
                        'markdown': '42',
                    },
                    {
                        'external_id': products[1]['external_id'],
                        'store': '3,14',
                        'markdown': '42,00',
                    },
                    {
                        'external_id': products[2]['external_id'],
                        'store': '-3.14',
                    },
                    {
                        'external_id': products[4]['external_id'],
                        'store': 'spam',
                    },
                ],
                'mark_removed': False,
            }
        )

        await import_data(s.stash_id)

        added_pps = await DraftPriceListProduct.list(
            by='full',
            conditions=[('price_list_id', '=', pl.price_list_id)],
        )

        tap.eq_ok(
            {i.product_id for i in added_pps},
            {products[0]['product_id'], products[1]['product_id']},
            'Only 2 products imported',
        )

        tap.eq_ok(
            {str(i.price['store']) for i in added_pps},
            {'3.14'},
            'With correct prices for store type',
        )

        tap.eq_ok(
            {str(i.price['markdown']) for i in added_pps},
            {'42.00'},
            'With correct prices for markdown type'
        )


async def test_add_new(tap, dataset):
    with tap.plan(2, 'не затираем цены для уже существующих продуктов'):
        store = await dataset.store()
        user = await dataset.user(store=store)
        pl = await dataset.draft_price_list()
        for _ in range(5):
            product = await dataset.product()
            await dataset.draft_price_list_product(
                price_list=pl,
                product=product,
                price={'store': 1},
            )

        added_pps = await DraftPriceListProduct.list(
            by='full',
            conditions=[('price_list_id', '=', pl.price_list_id)],
        )

        tap.eq_ok(
            sum([i.price['store'] for i in added_pps]),
            5,
            'задали цены для 5 продуктов',
        )

        new_product = await dataset.product()
        s = await dataset.stash(
            value={
                'store_id': store.store_id,
                'user_id': user.user_id,
                'price_list_id': pl.price_list_id,
                'products': [
                    {
                        'external_id': new_product.external_id,
                        'store': '2',
                    }
                ],
                'mark_removed': False,
            }
        )

        await import_data(s.stash_id)

        added_pps = await DraftPriceListProduct.list(
            by='full',
            conditions=[('price_list_id', '=', pl.price_list_id)],
        )

        tap.eq_ok(
            sum([i.price['store'] for i in added_pps]),
            7,
            'добавили в прайс еще один продукт',
        )
