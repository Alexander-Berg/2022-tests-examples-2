import pytest

from stall.model.store import STORE_STATUS


@pytest.mark.parametrize('role', ['admin', 'expansioner'])
async def test_load(api, dataset, tap, uuid, role):
    with tap.plan(16):
        store = await dataset.store(
            assortment_id=uuid(),
            kitchen_assortment_id=uuid(),
            markdown_assortment_id=uuid(),
            price_list_id=uuid(),
            samples=[
                {'product_id': '0'},
                {'product_id': '1', 'mode': 'disabled'},
                {'product_id': '2', 'mode': 'required', 'count': 1},
                {
                    'product_id': '2',
                    'mode': 'required',
                    'count': 1,
                    'tags': ['packaging'],
                },
            ],
            attr={
                'telephone': '88005553535',
                'telegram': 'some_telegram_id',
                'directions': 'пять шагов прямо, потом поверни налево',
            },
            courier_area_id=uuid(),
            courier_area_title=uuid(),
        )
        tap.ok(store, 'склад создан')

        user = await dataset.user(role=role, company_id=store.company_id)
        t = await api(user=user)
        await t.post_ok(
            'api_admin_stores_load',
            json={'store_id': store.store_id},
        )
        t.status_is(200, diag=True)

        t.json_is('code', 'OK')
        t.json_is('store.store_id', store.store_id)
        t.json_is('store.title', store.title)
        t.json_is('store.assortment_id', store.assortment_id)
        t.json_is('store.kitchen_assortment_id', store.kitchen_assortment_id)
        t.json_is('store.markdown_assortment_id', store.markdown_assortment_id)
        t.json_is('store.price_list_id', store.price_list_id)
        t.json_is('store.samples', store.samples)
        t.json_is('store.attr.telephone', '88005553535')
        t.json_is('store.attr.telegram', 'some_telegram_id')
        t.json_is(
            'store.attr.directions', 'пять шагов прямо, потом поверни налево',
        )
        t.json_is('store.courier_area_id', store.courier_area_id)
        t.json_is('store.courier_area_title', store.courier_area_title)


async def test_load_cluster_allow(api, dataset, tap, uuid):
    with tap.plan(4):
        cluster1_name = uuid()
        cluster2_name = uuid()

        store = await dataset.store(cluster=cluster1_name)

        user1 = await dataset.user(
            role='store_admin',
            store=store,
            clusters_allow=[cluster1_name]
        )
        user2 = await dataset.user(
            role='store_admin',
            store=store,
            clusters_allow=[cluster2_name]
        )

        t = await api(user=user1)
        await t.post_ok(
            'api_admin_stores_load',
            json={'store_id': store.store_id},
        )
        t.json_is('code', 'OK')

        t = await api(user=user2)
        await t.post_ok(
            'api_admin_stores_load',
            json={'store_id': store.store_id},
        )
        t.json_is('code', 'ER_ACCESS')


@pytest.mark.parametrize('status', STORE_STATUS)
async def test_status(api, dataset, tap, status):
    with tap.plan(6):
        store = await dataset.store(status=status)
        tap.ok(store, f'склад создан со статусом: {status}')

        user = await dataset.user(role='admin')
        t = await api(user=user)
        await t.post_ok(
            'api_admin_stores_load',
            json={'store_id': store.store_id},
        )
        t.status_is(200, diag=True)

        t.json_is('code', 'OK')
        t.json_is('store.store_id', store.store_id)
        t.json_is('store.title', store.title)


@pytest.mark.parametrize('role', ['admin', 'expansioner'])
async def test_load_multiple(tap, api, dataset, role):
    with tap.plan(5):
        company = await dataset.company()
        store1 = await dataset.store(company=company)
        store2 = await dataset.store(company=company)
        user = await dataset.user(role=role, company=company)
        t = await api(user=user)
        await t.post_ok(
            'api_admin_stores_load',
            json={'store_id': [store1.store_id,
                               store2.store_id]})
        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'код успеха')
        t.json_has('store', 'ассортимент есть в выдаче')
        res = t.res['json']['store']
        tap.eq_ok(
            sorted([res[0]['store_id'], res[1]['store_id']]),
            sorted([store1.store_id, store2.store_id]),
            'Пришли правильные ассортименты'
        )


@pytest.mark.parametrize('role', ['admin', 'expansioner'])
async def test_load_not_found(api, dataset, tap, uuid, role):
    with tap.plan(7):
        t = await api(role=role)

        await t.post_ok(
            'api_admin_stores_load',
            json={'store_id': uuid()},
        )
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS')

        store = await dataset.store()
        tap.ok(store, 'склад создан')
        await t.post_ok(
            'api_admin_stores_load',
            json={'store_id': [store.store_id, uuid()]},
        )
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS')


async def test_over_permit_out_store(tap, api, dataset):
    with tap.plan(7, 'Чужая лавка'):
        company1 = await dataset.company()

        store1 = await dataset.store(company=company1)
        store2 = await dataset.store(company=company1)

        user = await dataset.user(role='admin', store=store1)

        t = await api(user=user)
        with user.role as role:
            role.remove_permit('out_of_store')

            await t.post_ok('api_admin_stores_load',
                            json={'store_id': store2.store_id})
            t.status_is(403, diag=True)
            t.json_is('code', 'ER_ACCESS')

        with user.role:
            await t.post_ok('api_admin_stores_load',
                            json={'store_id': store2.store_id})
            t.status_is(200, diag=True)
            t.json_is('code', 'OK', 'объект получен')
            t.json_is('store.store_id', store2.store_id)


async def test_over_permit_out_company(tap, api, dataset):
    with tap.plan(10, 'Чужая компания'):
        store1 = await dataset.store()
        store2 = await dataset.store()

        user = await dataset.user(role='admin', company=store1)

        t = await api(user=user)
        with user.role as role:
            role.remove_permit('out_of_store')
            role.remove_permit('out_of_company')

            await t.post_ok('api_admin_stores_load',
                            json={'store_id': store2.store_id})
            t.status_is(403, diag=True)
            t.json_is('code', 'ER_ACCESS')

        with user.role as role:
            role.remove_permit('out_of_company')

            await t.post_ok('api_admin_stores_load',
                            json={'store_id': store2.store_id})
            t.status_is(403, diag=True)
            t.json_is('code', 'ER_ACCESS')

        with user.role:
            await t.post_ok('api_admin_stores_load',
                            json={'store_id': store2.store_id})
            t.status_is(200, diag=True)
            t.json_is('code', 'OK', 'объект получен')
            t.json_is('store.store_id', store2.store_id)
