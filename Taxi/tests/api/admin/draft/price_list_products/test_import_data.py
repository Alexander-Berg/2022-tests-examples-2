import pytest

from stall.model.stash import Stash


async def test_job_created(tap, api, dataset, make_csv_str):
    with tap:
        store = await dataset.store()
        admin = await dataset.user(role='admin', store=store)

        pl = await dataset.draft_price_list(user_id=admin.user_id)
        products = [await dataset.product() for _ in range(5)]

        t = await api()
        t.set_user(admin)

        csv_str = make_csv_str(
            ['external_id', 'store', 'markdown'],
            [
                {'external_id': i.external_id, 'store': '3.14', 'markdown': .1}
                for i in products
            ],
        )
        await t.post_ok(
            'api_admin_draft_price_list_products_import_data',
            json={
                'price_list_id': pl.price_list_id,
                'csv': csv_str,
                'mark_removed': False,
            },
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_like('job_id', r'^\S+$')

        stash_name = f'draft_price_list_import-{pl.price_list_id}'
        stash = await Stash.unstash(name=stash_name)
        tap.ok(stash, 'Price-list in stash')
        tap.eq_ok(stash.value('user_id'), admin.user_id, 'user_id')
        tap.eq_ok(stash.value('store_id'), store.store_id, 'store_id')
        tap.eq_ok(
            stash.value('price_list_id'), pl.price_list_id, 'price_list_id',
        )


async def test_job_created_store_only(tap, api, dataset, make_csv_str):
    with tap:
        store = await dataset.store()
        admin = await dataset.user(role='admin', store=store)

        pl = await dataset.draft_price_list(user_id=admin.user_id)
        products = [await dataset.product() for _ in range(5)]

        new_store_prices = ['678.22', '890.22', '', '123.45', '']

        t = await api()
        t.set_user(admin)

        csv_str = make_csv_str(
            ['external_id', 'store'],
            [
                {'external_id': i.external_id, 'store': price}
                for i, price in zip(products, new_store_prices)
            ],
        )
        await t.post_ok(
            'api_admin_draft_price_list_products_import_data',
            json={
                'price_list_id': pl.price_list_id,
                'csv': csv_str,
                'mark_removed': False,
            },
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_like('job_id', r'^\S+$')

        stash_name = f'draft_price_list_import-{pl.price_list_id}'
        stash = await Stash.unstash(name=stash_name)
        tap.ok(stash, 'Price-list in stash')
        tap.eq_ok(stash.value('user_id'), admin.user_id, 'user_id')
        tap.eq_ok(stash.value('store_id'), store.store_id, 'store_id')
        tap.eq_ok(
            stash.value('price_list_id'), pl.price_list_id, 'price_list_id',
        )
        tap.eq_ok(
            stash.value('products'),
            [
                {
                    'external_id': p.external_id,
                    'store': price,
                }
                for p, price in zip(products, new_store_prices)
            ],
            'Correct products and prices'
        )


async def test_job_created_markdown_only(tap, api, dataset, make_csv_str):
    with tap:
        store = await dataset.store()
        admin = await dataset.user(role='admin', store=store)

        pl = await dataset.draft_price_list(user_id=admin.user_id)
        products = [await dataset.product() for _ in range(5)]

        new_markdown_prices = ['678.22', '890.22', '', '123.45', '']

        t = await api()
        t.set_user(admin)

        csv_str = make_csv_str(
            ['external_id', 'markdown'],
            [
                {'external_id': i.external_id, 'markdown': price}
                for i, price in zip(products, new_markdown_prices)
            ],
        )
        await t.post_ok(
            'api_admin_draft_price_list_products_import_data',
            json={
                'price_list_id': pl.price_list_id,
                'csv': csv_str,
                'mark_removed': False,
            },
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_like('job_id', r'^\S+$')

        stash_name = f'draft_price_list_import-{pl.price_list_id}'
        stash = await Stash.unstash(name=stash_name)
        tap.ok(stash, 'Price-list in stash')
        tap.eq_ok(stash.value('user_id'), admin.user_id, 'user_id')
        tap.eq_ok(stash.value('store_id'), store.store_id, 'store_id')
        tap.eq_ok(
            stash.value('price_list_id'), pl.price_list_id, 'price_list_id',
        )
        tap.eq_ok(
            stash.value('products'),
            [
                {
                    'external_id': p.external_id,
                    'markdown': price,
                }
                for p, price in zip(products, new_markdown_prices)
            ],
            'Correct products and prices'
        )


async def test_fail_user_id(tap, api, dataset, make_csv_str):
    with tap:
        store = await dataset.store()
        admin = await dataset.user(role='admin', store=store)
        another_user = await dataset.user(role='admin', store=store)

        pl = await dataset.draft_price_list(user_id=another_user.user_id)
        products = [await dataset.product() for _ in range(5)]

        t = await api()
        t.set_user(admin)

        csv_str = make_csv_str(
            ['external_id', 'store', 'markdown'],
            [
                {'external_id': i.external_id, 'store': '3.14', 'markdown': .1}
                for i in products
            ],
        )
        await t.post_ok(
            'api_admin_draft_price_list_products_import_data',
            json={
                'price_list_id': pl.price_list_id,
                'csv': csv_str,
                'mark_removed': False,
            },
        )

        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS')
        t.json_is('message', 'Only creator of draft can edit it')


async def test_er_bad_csv(tap, api, dataset):
    with tap:
        user = await dataset.user(role='admin')
        t = await api(user=user)

        pl = await dataset.draft_price_list(user_id=user.user_id)

        await t.post_ok(
            'api_admin_draft_price_list_products_import_data',
            json={
                'price_list_id': pl.price_list_id,
                'csv': '',
                'mark_removed': False,
            },
        )

        t.status_is(400, diag=True)
        t.json_is('code', 'ER_BAD_REQUEST')
        t.json_is('message', 'CSV has 0 rows')


async def test_er_no_rows(tap, api, dataset):
    with tap:
        user = await dataset.user(role='admin')
        t = await api(user=user)

        pl = await dataset.draft_price_list(user_id=user.user_id)

        await t.post_ok(
            'api_admin_draft_price_list_products_import_data',
            json={
                'price_list_id': pl.price_list_id,
                'csv': 'external_id,store',
                'mark_removed': False,
            },
        )

        t.status_is(400, diag=True)
        t.json_is('code', 'ER_BAD_REQUEST')
        t.json_is('message', 'CSV has 0 rows')


async def test_er_too_many_rows(tap, api, dataset, make_csv_str):
    with tap:
        user = await dataset.user(role='admin')
        t = await api(user=user)

        pl = await dataset.draft_price_list(user_id=user.user_id)

        csv_str = make_csv_str(
            ['external_id', 'store'],
            [{'external_id': i, 'store': i} for i in range(10001)],
        )

        await t.post_ok(
            'api_admin_draft_price_list_products_import_data',
            json={
                'price_list_id': pl.price_list_id,
                'csv': csv_str,
                'mark_removed': False,
            },
        )

        t.status_is(400, diag=True)
        t.json_is('code', 'ER_BAD_REQUEST')
        t.json_like('message', 'CSV has more than')


async def test_er_bad_columns(tap, api, dataset, make_csv_str):
    with tap:
        user = await dataset.user(role='admin')
        t = await api(user=user)

        pl = await dataset.draft_price_list(user_id=user.user_id)

        csv_str = make_csv_str(
            ['a', 'b'],
            [{'a': i, 'b': i} for i in range(10)],
        )

        await t.post_ok(
            'api_admin_draft_price_list_products_import_data',
            json={
                'price_list_id': pl.price_list_id,
                'csv': csv_str,
                'mark_removed': False,
            },
        )

        t.status_is(400, diag=True)
        t.json_is('code', 'ER_BAD_REQUEST')
        t.json_like(
            'message',
            '"external_id" column not found',
        )

        csv_str = make_csv_str(
            ['external_id', 'another_column'],
            [{'external_id': i, 'another_column': i} for i in range(10)],
        )

        await t.post_ok(
            'api_admin_draft_price_list_products_import_data',
            json={
                'price_list_id': pl.price_list_id,
                'csv': csv_str,
                'mark_removed': False,
            },
        )

        t.status_is(400, diag=True)
        t.json_is('code', 'ER_BAD_REQUEST')
        t.json_like(
            'message',
            'Neither "store" nor "markdown" column found'
        )


async def test_er_import_started(tap, api, dataset, make_csv_str):
    with tap:
        user = await dataset.user(role='admin')
        t = await api(user=user)
        pl = await dataset.draft_price_list(user_id=user.user_id)
        products = [await dataset.product() for _ in range(5)]

        csv_str = make_csv_str(
            ['external_id', 'store'],
            [
                {'external_id': i.external_id, 'store': '3.14'}
                for i in products
            ],
        )
        await t.post_ok(
            'api_admin_draft_price_list_products_import_data',
            json={
                'price_list_id': pl.price_list_id,
                'csv': csv_str,
                'mark_removed': False,
            },
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_like('job_id', r'^\S+$')

        await t.post_ok(
            'api_admin_draft_price_list_products_import_data',
            json={
                'price_list_id': pl.price_list_id,
                'csv': csv_str,
                'mark_removed': False,
            },
        )

        t.status_is(400, diag=True)
        t.json_is('code', 'ER_BAD_REQUEST')
        t.json_like(
            'message',
            'CSV import already started by user:'
        )


@pytest.mark.parametrize('status', ['ready', 'applied'])
async def test_er_gone(tap, api, dataset, status, make_csv_str):
    with tap:
        store = await dataset.store()
        admin = await dataset.user(role='admin', store=store)

        pl = await dataset.draft_price_list(status=status,
                                            user_id=admin.user_id)
        products = [await dataset.product() for _ in range(5)]

        t = await api()
        t.set_user(admin)

        csv_str = make_csv_str(
            ['external_id', 'store', 'markdown'],
            [
                {'external_id': i.external_id, 'store': '3.14', 'markdown': .1}
                for i in products
            ],
        )
        await t.post_ok(
            'api_admin_draft_price_list_products_import_data',
            json={
                'price_list_id': pl.price_list_id,
                'csv': csv_str,
                'mark_removed': False,
            },
        )

        t.status_is(410, diag=True)
        t.json_is('code', 'ER_GONE')


@pytest.mark.parametrize('role', ['category_manager'])
async def test_er_access(tap, api, dataset, role, make_csv_str):
    with tap:
        store = await dataset.store()
        user = await dataset.user(role=role, store=store)

        pl = await dataset.draft_price_list(user_id=user.user_id)
        products = [await dataset.product() for _ in range(5)]

        t = await api()
        t.set_user(user)

        csv_str = make_csv_str(
            ['external_id', 'store', 'markdown'],
            [
                {'external_id': i.external_id, 'store': '3.14', 'markdown': .1}
                for i in products
            ],
        )
        await t.post_ok(
            'api_admin_draft_price_list_products_import_data',
            json={
                'price_list_id': pl.price_list_id,
                'csv': csv_str,
                'mark_removed': False,
            },
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        await t.post_ok(
            'api_admin_draft_price_list_products_import_data',
            json={
                'price_list_id': pl.price_list_id,
                'csv': csv_str,
                'mark_removed': True,
            },
        )

        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS')
