import pytest


async def test_create(tap, api, dataset):
    with tap.plan(11):
        user = await dataset.user(role='admin')
        t = await api(user=user)

        price_list = await dataset.draft_price_list(user_id=user.user_id)
        product = await dataset.product()

        pp_data = {
            'price_list_id': price_list.price_list_id,
            'product_id': product.product_id,
            'price': {'store': '3.14'},
        }

        await t.post_ok('api_admin_draft_price_list_products_save',
                        json=pp_data)

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        t.json_has('price_list_product.pp_id')
        t.json_has('price_list_product.created')
        t.json_has('price_list_product.updated')
        t.json_is(
            'price_list_product.price_list_id', pp_data['price_list_id'],
        )
        t.json_is('price_list_product.product_id', pp_data['product_id'])
        t.json_is('price_list_product.price.store', pp_data['price']['store'])
        t.json_hasnt('price_list_product.price.markdown')
        t.json_is('price_list_product.user_id', user.user_id)


async def test_update(tap, api, dataset):
    with tap.plan(7):
        user = await dataset.user(role='admin')
        t = await api(user=user)

        price_list = await dataset.draft_price_list(user_id=user.user_id)
        pp = await dataset.draft_price_list_product(
            price={'store': 1984},
            price_list_id=price_list.price_list_id
        )
        tap.ok(pp, 'Price-list to product rel created')

        # ok case

        pp_data = {
            'pp_id': pp.pp_id,
            'price': {'store': '42.00', 'markdown': '3.14'},
            'user_id': 'hello'
        }

        await t.post_ok('api_admin_draft_price_list_products_save',
                        json=pp_data)

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('price_list_product.price.store', pp_data['price']['store'])
        t.json_is(
            'price_list_product.price.markdown', pp_data['price']['markdown'],
        )
        t.json_isnt('price_list_product.user_id', 'hello')


async def test_fail_applied_ready(tap, api, dataset):
    with tap.plan(7):
        user = await dataset.user(role='admin')
        t = await api(user=user)

        price_list = await dataset.draft_price_list(status='applied',
                                                    user_id=user.user_id)
        pp = await dataset.draft_price_list_product(
            price={'store': 1984},
            price_list_id=price_list.price_list_id
        )
        tap.ok(pp, 'Price-list to product rel created')

        # ok case

        pp_data = {
            'pp_id': pp.pp_id,
            'price': {'store': '42.00', 'markdown': '3.14'},
        }

        await t.post_ok('api_admin_draft_price_list_products_save',
                        json=pp_data)

        t.status_is(410, diag=True)
        t.json_is('code', 'ER_GONE')

        price_list.status = 'ready'
        await price_list.save()

        await t.post_ok('api_admin_draft_price_list_products_save',
                        json=pp_data)
        t.status_is(410, diag=True)
        t.json_is('code', 'ER_GONE')


@pytest.mark.parametrize('role', ['store_admin', 'expansioner'])
async def test_access(tap, dataset, api, role):
    with tap.plan(6):
        user = await dataset.user(role=role)
        price_list = await dataset.draft_price_list(user_id=user.user_id)
        tap.ok(price_list, 'Price-list created')

        product = await dataset.product()
        tap.ok(product, 'Product created')

        t = await api(user=user)

        await t.post_ok(
            'api_admin_draft_price_list_products_save',
            json={
                'price_list_id': price_list.price_list_id,
                'product_id': product.product_id,
            },
        )
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS')
        t.json_is('message', 'Access denied')


async def test_bad_data(tap, api):
    with tap.plan(3):
        t = await api(role='admin')

        await t.post_ok(
            'api_admin_draft_price_list_products_save',
            json={'spam': 'yes'},
        )

        t.status_is(400, diag=True)
        t.json_is('code', 'BAD_REQUEST')


async def test_access_non_author(tap, dataset, api):
    with tap.plan(5):
        user = await dataset.user(role='admin')
        author = await dataset.user(role='admin')
        price_list = await dataset.draft_price_list(user_id=author.user_id)
        tap.ok(price_list, 'Price-list created')

        product = await dataset.product()
        tap.ok(product, 'Product created')

        t = await api(user=user)

        await t.post_ok(
            'api_admin_draft_price_list_products_save',
            json={
                'price_list_id': price_list.price_list_id,
                'product_id': product.product_id,
            },
        )
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS')
