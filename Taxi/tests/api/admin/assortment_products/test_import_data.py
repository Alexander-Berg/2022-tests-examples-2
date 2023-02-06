# pylint: disable=unused-argument

from stall.model.stash import Stash


async def test_job_created(tap, api, dataset, job, make_csv_str):
    # NOTE: получение job добавлено чтобы тест пошол в своих очередях
    with tap:
        store = await dataset.store()
        admin = await dataset.user(role='admin', store=store)

        a = await dataset.assortment()
        products = [await dataset.product() for _ in range(5)]

        t = await api()
        t.set_user(admin)

        csv_str = make_csv_str(
            ['external_id'],
            [{'external_id': i.external_id} for i in products],
        )
        await t.post_ok(
            'api_admin_assortment_products_import_data',
            json={
                'assortment_id': a.assortment_id,
                'status': 'active',
                'csv': csv_str,
            },
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_like('job_id', r'^\S+$')

        stash_name = f'assortment_import-{a.assortment_id}'
        stash = await Stash.unstash(name=stash_name)

        tap.ok(stash, 'Assortment in stash')
        tap.eq_ok(stash.value('user_id'), admin.user_id, 'user_id')
        tap.eq_ok(stash.value('store_id'), store.store_id, 'store_id')
        tap.eq_ok(
            stash.value('assortment_id'), a.assortment_id, 'assortment_id',
        )
        tap.ok(stash.value('products'), 'products')
        tap.eq_ok(stash.value('status'), 'active', 'status')


async def test_er_incorrect_status(tap, api, dataset):
    with tap:
        t = await api(role='admin')

        a = await dataset.assortment()

        await t.post_ok(
            'api_admin_assortment_products_import_data',
            json={
                'assortment_id': a.assortment_id,
                'status': 'excluded',
                'csv': '',
            },
        )

        t.status_is(400, diag=True)
        t.json_is('code', 'ER_BAD_REQUEST')
        t.json_like(
            'message', 'Incorrect status for product in base assortment'
        )


async def test_er_no_rows(tap, api, dataset):
    with tap:
        t = await api(role='admin')

        a = await dataset.assortment()

        await t.post_ok(
            'api_admin_assortment_products_import_data',
            json={
                'assortment_id': a.assortment_id,
                'status': 'active',
                'csv': 'a,b,c',
            },
        )

        t.status_is(400, diag=True)
        t.json_is('code', 'ER_BAD_REQUEST')
        t.json_is('message', 'CSV has 0 rows')


async def test_er_too_many_rows(tap, api, dataset, make_csv_str):
    with tap:
        t = await api(role='admin')

        a = await dataset.assortment()

        csv_str = make_csv_str(
            ['external_id'],
            [{'external_id': i} for i in range(10001)],
        )

        await t.post_ok(
            'api_admin_assortment_products_import_data',
            json={
                'assortment_id': a.assortment_id,
                'status': 'active',
                'csv': csv_str,
            },
        )

        t.status_is(400, diag=True)
        t.json_is('code', 'ER_BAD_REQUEST')
        t.json_like('message', 'CSV has more than')


async def test_er_bad_columns(tap, api, dataset, make_csv_str):
    with tap:
        t = await api(role='admin')

        a = await dataset.assortment()

        csv_str = make_csv_str(
            ['a', 'b'],
            [{'a': i, 'b': i} for i in range(10)],
        )

        await t.post_ok(
            'api_admin_assortment_products_import_data',
            json={
                'assortment_id': a.assortment_id,
                'status': 'active',
                'csv': csv_str,
            },
        )

        t.status_is(400, diag=True)
        t.json_is('code', 'ER_BAD_REQUEST')
        t.json_like(
            'message',
            'CSV required fields not found:'
        )


async def test_er_import_started(tap, api, dataset, make_csv_str):
    with tap:
        a = await dataset.assortment()
        products = [await dataset.product() for i in range(5)]

        t = await api(role='admin')

        csv_str = make_csv_str(
            ['external_id'],
            [{'external_id': i.external_id} for i in products],
        )
        await t.post_ok(
            'api_admin_assortment_products_import_data',
            json={
                'assortment_id': a.assortment_id,
                'status': 'active',
                'csv': csv_str,
            },
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_like('job_id', r'^\S+$')

        await t.post_ok(
            'api_admin_assortment_products_import_data',
            json={
                'assortment_id': a.assortment_id,
                'status': 'active',
                'csv': csv_str,
            },
        )

        t.status_is(400, diag=True)
        t.json_is('code', 'ER_BAD_REQUEST')
        t.json_like(
            'message',
            'CSV import already started by user:'
        )
