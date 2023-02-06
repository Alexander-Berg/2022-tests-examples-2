async def test_instance(tap, dataset):
    with tap.plan(7):
        price_list = await dataset.price_list(title='lavka 42')

        tap.ok(price_list, 'Price-list created')

        product = await dataset.product()

        tap.ok(product, 'Product created')

        pp = dataset.PriceListProduct(
            {
                'price_list_id': price_list.price_list_id,
                'product_id': product.product_id,
                'price': {
                    'store': '3.14',
                    'markdown': 42,
                }
            }
        )

        tap.ok(pp, 'Inited')
        tap.ok(not pp.pp_id, 'No id')
        tap.ok(await pp.save(), 'Saved')
        tap.ok(pp.pp_id, 'id assigned')
        tap.eq_ok(pp.price.markdown, 42, 'Correct markdown price')


async def test_dataset(tap, dataset):
    with tap.plan(3):
        pp = await dataset.price_list_product()
        tap.ok(pp.product_id, 'Product assigned to price-list')
        tap.eq_ok(pp.price.store, None, 'Store price undefined')
        tap.eq_ok(pp.price.markdown, None, 'Markdown price undefined')


async def test_price_rehash(tap, dataset):
    with tap.plan(3):
        price_list = await dataset.price_list(title='lavka 42')
        product = await dataset.product()
        pp = dataset.PriceListProduct(
            {
                'price_list_id': price_list.price_list_id,
                'product_id': product.product_id,
                'price': {'store': '3.14'},
            }
        )
        await pp.save()

        tap.eq_ok(pp.price.store, '3.14', 'Correct store price')
        tap.eq_ok(pp.price.markdown, None, 'Correct markdown price')

        pp.price = {
            'store': 1984,
            'markdown': 1984,
        }

        tap.ok(pp.rehashed('-check'), 'Model knows about changes')
