import pytest


async def test_barcode(tap, api, dataset, uuid):
    with tap.plan(34, 'ищем по баркоду товары и посылки'):
        store = await dataset.store()
        user = await dataset.user(role='admin', store=store)

        t = await api(user=user)

        product = await dataset.product(barcode=[uuid(), uuid()])
        tap.ok(product, 'товар создан')
        tap.ok(product.barcode, 'шк есть')

        product2 = await dataset.product(barcode=[product.barcode[1]])
        tap.ok(product2, 'товар создан')
        tap.ok(product2.barcode, 'шк есть')
        tap.eq(
            product2.barcode[0],
            product.barcode[1],
            'одинаковый шк у 2 твоаров',
        )

        item = await dataset.item(barcode=[uuid()], store=store)
        tap.ok(item, 'посылка создана')
        tap.ok(item.barcode, 'шк есть')

        item2 = await dataset.item(barcode=[item.barcode[0]])
        tap.ok(item2, 'посылка создана')
        tap.ok(item2.barcode, 'шк есть')
        tap.eq(
            item2.barcode[0],
            item.barcode[0],
            'одинаковый шк у 2 посылок',
        )
        tap.ok(
            item2.store_id != item.store_id,
            'посылки прикреплены к разным складам',
        )

        await t.post_ok(
            'api_admin_search_barcode',
            json={'barcode': uuid()}
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        t.json_hasnt('products.1')
        t.json_hasnt('items.1')

        await t.post_ok(
            'api_admin_search_barcode',
            json={'barcode': product.barcode[0]}
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        t.json_is('products.0.product_id', product.product_id)
        t.json_hasnt('products.1')
        t.json_hasnt('items.1')

        await t.post_ok(
            'api_admin_search_barcode',
            json={'barcode': product.barcode[1]},
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        t.json_has('products.0')
        t.json_has('products.1')
        t.json_hasnt('items.1')

        await t.post_ok(
            'api_admin_search_barcode',
            json={'barcode': item.barcode[0]},
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        t.json_is('items.0.item_id', item.item_id)
        t.json_hasnt('items.1')
        t.json_hasnt('products.1')


@pytest.mark.parametrize('lang', ('ru_RU', 'en_US'))
async def test_locales(tap, api, dataset, uuid, lang):
    with tap.plan(4):
        user = await dataset.user(role='admin', lang=lang)

        t = await api(user=user)

        product = await dataset.product(
            barcode=[uuid()],
            vars={
                'locales': {
                    'title': {lang: f'есть перевод {lang}'},
                }
            },
        )

        await t.post_ok(
            'api_admin_search_barcode',
            json={'barcode': product.barcode[0]},
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('products.0.title', f'есть перевод {lang}')
