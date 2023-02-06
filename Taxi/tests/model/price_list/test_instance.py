from stall.model.price_list import PriceList


async def test_price_list(tap):
    with tap.plan(4):
        price_list = PriceList({'title': 'Test price-list'})

        tap.ok(price_list, 'Inited')
        tap.ok(not price_list.price_list_id, 'No id')
        tap.ok(await price_list.save(), 'Saved')
        tap.ok(price_list.price_list_id, 'id assigned')


async def test_dataset(tap, dataset):
    with tap.plan(2):
        price_list = await dataset.price_list(title='lavka 42')

        tap.ok(price_list, 'Created')
        tap.eq(price_list.title, 'lavka 42', 'Correct title')
