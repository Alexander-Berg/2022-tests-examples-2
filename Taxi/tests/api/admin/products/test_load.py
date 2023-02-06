import pytest


async def test_load(tap, api, dataset):
    with tap.plan(20):
        group = await dataset.product_group()
        product = await dataset.product(
            title='spam',
            long_title=None,
            description='spam and eggs',
            images=['https://localhost'],
            order=10,
            groups=[group.group_id],
            measure_unit='liter',
            vat='20.5',
            valid=9999,
            write_off_before=365,
            tags=['freezer'],
            vars={
                'imported': {
                    'pim1': 1,
                    'pim2': 2,
                }
            },
            amount='3.14',
            amount_unit='кусочки',
        )

        tap.ok(product, 'product created')

        t = await api(role='admin')

        await t.post_ok(
            'api_admin_products_load',
            json={'product_id': product.product_id},
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        t.json_is('product.product_id', product.product_id)
        t.json_is('product.external_id', product.external_id)
        t.json_is('product.title', product.title)
        t.json_is('product.long_title', product.long_title)
        t.json_is('product.description', product.description)
        t.json_is('product.images', product.images)
        t.json_is('product.order', product.order)
        t.json_is('product.groups', product.groups)
        t.json_is('product.measure_unit', product.measure_unit)
        t.json_is('product.vat', str(product.vat))
        t.json_is('product.tags', product.tags)
        t.json_is('product.valid', product.valid)
        t.json_is('product.write_off_before', product.write_off_before)
        t.json_is('product.vars', product.vars)
        t.json_is('product.amount', str(product.amount))
        t.json_is('product.amount_unit', product.amount_unit)


async def test_load_not_found(tap, api, uuid):
    with tap.plan(3):

        t = await api(role='admin')

        await t.post_ok(
            'api_admin_products_load',
            json={'product_id': uuid()},
        )

        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS')


@pytest.mark.parametrize('role', ['admin', 'store_admin',
                                  'executer', 'barcode_executer'])
async def test_load_multiple(tap, api, dataset, role):
    with tap.plan(5):
        t = await api(role=role)
        product1 = await dataset.product()
        product2 = await dataset.product()
        await t.post_ok(
            'api_admin_products_load',
            json={'product_id': [product1.product_id,
                                 product2.product_id]})
        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'код успеха')
        t.json_has('product', 'продукт есть в выдаче')
        res = t.res['json']['product']
        tap.eq_ok(
            sorted([res[0]['product_id'], res[1]['product_id']]),
            sorted([product1.product_id, product2.product_id]),
            'Пришли правильные продукты'
        )


@pytest.mark.parametrize('role', ['admin', 'store_admin',
                                  'executer', 'barcode_executer'])
async def test_load_multiple_fail(tap, api, dataset, uuid, role):
    with tap.plan(2):
        t = await api(role=role)
        product1 = await dataset.product()
        await t.post_ok(
            'api_admin_products_load',
            json={'product_id': [product1.product_id,
                                 uuid()]})
        t.status_is(403, diag=True)


@pytest.mark.parametrize('lang', ('ru_RU', 'en_US'))
async def test_locales(tap, api, dataset, lang):
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
            'api_admin_products_load',
            json={'product_id': products[0].product_id},
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('product.title', 'нет перевода')

        await t.post_ok(
            'api_admin_products_load',
            json={'product_id': [products[1].product_id]},
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('product.0.title', f'есть перевод {lang}')
