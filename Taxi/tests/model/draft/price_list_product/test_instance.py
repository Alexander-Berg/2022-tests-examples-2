import pytest

from stall.model.draft.price_list_product import DraftPriceListProduct


async def test_instance(tap, dataset):
    with tap.plan(6):
        draft_p = await dataset.draft_price_list(title='lavka 42')
        product = await dataset.product()

        draft_pp = DraftPriceListProduct(
            {
                'price_list_id': draft_p.price_list_id,
                'product_id': product.product_id,
                'price': {
                    'store': '3.14',
                    'markdown': 42,
                }
            }
        )

        tap.ok(draft_pp, 'Inited')
        tap.ok(not draft_pp.pp_id, 'No id')
        tap.ok(await draft_pp.save(), 'Saved')
        tap.ok(draft_pp.pp_id, 'id assigned')
        tap.eq_ok(draft_pp.price['store'], 3.14, 'Correct store price')
        tap.eq_ok(draft_pp.price['markdown'], 42, 'Correct markdown price')


async def test_dataset(tap, dataset):
    with tap.plan(1):

        draft = await dataset.draft_price_list_product()
        tap.ok(draft.product_id, 'Product assigned to price-list')


@pytest.mark.parametrize('price', [
    {
        'store': '3.14',
        'markdown': '42.01',
    },
    {
        'markdown': '42.01',
    },
    {
        'store': '3.14',
    },
    {},
])
async def test_coerce_price(tap, dataset, price):
    with tap:
        draft_price_list = await dataset.draft_price_list()
        product = await dataset.product()
        pp = DraftPriceListProduct({
            'price_list_id': draft_price_list.price_list_id,
            'product_id': product.product_id,
            'price': price
        })
        await pp.save()

        if 'store' in price:
            tap.eq_ok(pp.price['store'], price['store'], 'Correct store')
        else:
            tap.ok('store' not in pp.price, 'store not present')

        if 'markdown' in price:
            tap.eq_ok(pp.price['markdown'], price['markdown'],
                      'Correct markdown')
        else:
            tap.ok('markdown' not in pp.price,
                   'markdown not present')
