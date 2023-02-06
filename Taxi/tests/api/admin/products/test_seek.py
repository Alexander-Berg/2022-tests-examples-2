import pytest


async def test_seek(tap, dataset, api, uuid):
    with tap.plan(6):
        for _ in range(5):
            await dataset.product(title=uuid())

        t = await api(role='admin')

        await t.post_ok('api_admin_products_seek', json={'cursor': ''})

        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'code')
        t.json_has('products', 'products')
        t.json_has('cursor', 'cursor')

        tap.ok(len(t.res['json']['products']) >= 5, '5 or more products')


async def test_seek_by_title(tap, dataset, api, uuid):
    with tap.plan(7, 'тест фильтра по названию'):
        title = uuid()

        for i in range(5):
            await dataset.product(title=f'{title}-{i}')

        t = await api(role='admin')

        await t.post_ok(
            'api_admin_products_seek', json={'title': title, 'cursor': ''}
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'code')
        t.json_has('products', 'products')
        t.json_has('cursor', 'cursor')

        products = t.res['json']['products']
        tap.eq_ok(len(products), 5, '5 products with title')
        tap.ok(
            all(i['title'].startswith(title) for i in products),
            'products with correct title',
        )


async def test_seek_by_ids(tap, dataset, api):
    with tap.plan(7, 'тест фильтра по id'):

        products = [await dataset.product() for _ in range(5)]

        t = await api(role='admin')

        await t.post_ok(
            'api_admin_products_seek',
            json={
                'product_ids': [i.product_id for i in products],
            }
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'code')
        t.json_has('products', 'products')
        t.json_has('cursor', 'cursor')

        tap.eq_ok(len(t.res['json']['products']), len(products), '5 products')
        tap.eq_ok(
            {i['product_id'] for i in t.res['json']['products']},
            {i.product_id for i in products},
            'products with correct ids',
        )


async def test_seek_groups(tap, dataset, api, uuid):
    with tap.plan(7, 'тест фильтра по группам'):
        group = uuid()
        products = [await dataset.product(groups=[group]) for _ in range(5)]

        t = await api(role='admin')

        await t.post_ok(
            'api_admin_products_seek',
            json={
                'product_groups': [group],
                'cursor': None
            }
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'code')
        t.json_has('products', 'products')
        t.json_has('cursor', 'cursor')

        tap.eq_ok(len(t.res['json']['products']), len(products), '5 products')
        tap.eq_ok(
            {i['product_id'] for i in t.res['json']['products']},
            {i.product_id for i in products},
            'products with correct ids',
        )


async def test_seek_by_eid(tap, dataset, api, uuid):
    with tap.plan(6, 'тест фильтра по external_id'):
        eid = uuid()

        await dataset.product(external_id=eid)

        t = await api(role='admin')

        await t.post_ok(
            'api_admin_products_seek', json={'external_id': eid, 'cursor': ''}
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'code')
        t.json_has('products', 'products')
        t.json_has('cursor', 'cursor')

        products = t.res['json']['products']
        tap.eq_ok(len(products), 1, '1 products with external_id')


async def test_seek_by_barcode(tap, dataset, api, uuid):
    with tap.plan(6, 'тест фильтра по barcode'):
        barcode = uuid()

        await dataset.product(barcode=[barcode])

        t = await api(role='admin')

        await t.post_ok(
            'api_admin_products_seek', json={'barcode': barcode, 'cursor': ''}
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'code')
        t.json_has('products', 'products')
        t.json_has('cursor', 'cursor')

        products = t.res['json']['products']
        tap.eq_ok(len(products), 1, '1 products with external_id')


@pytest.mark.parametrize('role', ('admin', 'company_admin_ro'))
async def test_seek_by_products_scope(tap, dataset, api, role):
    with tap.plan(7, 'тест фильтра по products_scope'):
        company1 = await dataset.company(products_scope=['japan'])
        company2 = await dataset.company(products_scope=['england'])
        product1 = await dataset.product(products_scope=company1.products_scope)
        product2 = await dataset.product(products_scope=company2.products_scope)

        user = await dataset.user(
            role=role,
            company_id=company1.company_id,
        )

        t = await api(user=user)

        await t.post_ok(
            'api_admin_products_seek',
            json={'products_scope': company1.products_scope}
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'code')
        t.json_has('products', 'products')
        t.json_has('cursor', 'cursor')
        products = t.res['json']['products']
        products = [prod['product_id'] for prod in products]
        tap.in_ok(
            product1.product_id,
            products,
            'продукт в отданных параметрах'
        )
        tap.not_in_ok(
            product2.product_id,
            products,
            'product_scope не совпадает'
        )


async def test_seek_by_scope_no_out(tap, dataset, api):
    with tap.plan(7, 'тест фильтра по products_scope_for_company_admin_ro'):
        company1 = await dataset.company(products_scope=['japan'])
        company2 = await dataset.company(products_scope=['england'])
        product1 = await dataset.product(products_scope=company1.products_scope)
        product2 = await dataset.product(products_scope=company2.products_scope)

        user = await dataset.user(
            role='company_admin_ro',
            company_id=company1.company_id,
        )

        t = await api(user=user)

        await t.post_ok('api_admin_products_seek', json={})

        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'code')
        t.json_has('products', 'products')
        t.json_has('cursor', 'cursor')
        products = t.res['json']['products']
        products = [prod['product_id'] for prod in products]
        tap.in_ok(
            product1.product_id,
            products,
            'продукт в отданных параметрах'
        )
        tap.not_in_ok(
            product2.product_id,
            products,
            'product_scope не совпадает'
        )


@pytest.mark.parametrize('lang', ('ru_RU', 'en_US'))
async def test_locales(tap, dataset, api, lang):
    with tap.plan(8):
        user = await dataset.user(role='admin', lang=lang)

        products = [
            await dataset.product(
                title='нет перевода',
            ),
            await dataset.product(
                title='есть перевод',
                vars={
                    'locales': {
                        'title': {lang: f'есть перевод {lang}'},
                    }
                },
            ),
        ]

        t = await api(user=user)

        await t.post_ok(
            'api_admin_products_seek',
            json={
                'product_ids': [products[0].product_id],
                'cursor': None,
            }
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('products.0.title', 'нет перевода')

        await t.post_ok(
            'api_admin_products_seek',
            json={
                'product_ids': [products[1].product_id],
                'cursor': None,
            }
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('products.0.title', f'есть перевод {lang}')
