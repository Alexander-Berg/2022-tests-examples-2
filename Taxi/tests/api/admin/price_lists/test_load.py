import pytest


@pytest.mark.parametrize('role', ['admin', 'category_manager'])
async def test_found(tap, api, dataset, role):
    with tap.plan(9):
        t = await api(role=role)

        price_list = await dataset.price_list()
        tap.ok(price_list, 'Price-list created')

        await t.post_ok(
            'api_admin_price_lists_load',
            json={'price_list_id': price_list.price_list_id},
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('price_list')

        t.json_is('price_list.price_list_id', price_list.price_list_id)
        t.json_is('price_list.title', price_list.title)
        t.json_has('price_list.created')
        t.json_has('price_list.updated')


@pytest.mark.parametrize('role', ['admin', 'expansioner'])
async def test_not_found(tap, api, uuid, role):
    with tap:
        t = await api(role=role)

        await t.post_ok(
            'api_admin_price_lists_load',
            json={'price_list_id': uuid()},
        )
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS')
        t.json_is('message', 'Access denied')


@pytest.mark.parametrize('role', ['admin', 'category_manager'])
async def test_permit_out_of_store(tap, api, dataset, role):
    with tap:
        price_list = await dataset.price_list()
        tap.ok(price_list, 'Price-list created')

        store = await dataset.store(price_list=price_list)
        tap.ok(store, 'Store created')

        user = await dataset.user(role=role)
        tap.ok(user, f'User with role {role} created')

        tap.ok(
            user.store_id != store.store_id, 'User assigned to another store',
        )

        t = await api()
        t.set_user(user)

        await t.post_ok(
            'api_admin_price_lists_load',
            json={'price_list_id': price_list.price_list_id},
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('price_list')


async def test_access(tap, api, dataset):
    with tap:
        store_a = await dataset.store()
        tap.ok(store_a, 'Store A created')

        price_list_a = await dataset.price_list(company_id=store_a.company_id)
        tap.ok(price_list_a, 'Price-list A created')

        store_a.price_list_id = price_list_a.price_list_id
        tap.ok(await store_a.save(), 'Price-list A assigned to store A')

        user_a = await dataset.user(store=store_a, role='store_admin')
        tap.ok(user_a, 'User A assigned to store A')

        t = await api()
        t.set_user(user_a)

        await t.post_ok(
            'api_admin_price_lists_load',
            json={'price_list_id': price_list_a.price_list_id},
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('price_list')
        t.json_is('price_list.price_list_id', price_list_a.price_list_id)

        user_b = await dataset.user(role='store_admin')
        tap.ok(user_b, 'User B assigned to store')

        t = await api()
        t.set_user(user_b)

        await t.post_ok(
            'api_admin_price_lists_load',
            json={'price_list_id': price_list_a.price_list_id},
        )
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS')
        t.json_is('message', 'Access denied')


@pytest.mark.parametrize('role', ['admin', 'category_manager'])
async def test_load_multiple(tap, api, dataset, role):
    with tap.plan(5):
        t = await api(role=role)
        price_list1 = await dataset.price_list()
        price_list2 = await dataset.price_list()
        await t.post_ok(
            'api_admin_price_lists_load',
            json={'price_list_id': [price_list1.price_list_id,
                                    price_list2.price_list_id]})
        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'код успеха')
        t.json_has('price_list', 'есть в выдаче')
        res = t.res['json']['price_list']
        tap.eq_ok(
            sorted([res[0]['price_list_id'], res[1]['price_list_id']]),
            sorted([price_list1.price_list_id, price_list2.price_list_id]),
            'Пришли правильные объекты'
        )


@pytest.mark.parametrize('role', ['admin', 'category_manager'])
async def test_load_multiple_fail(tap, api, dataset, uuid, role):
    with tap.plan(2):
        t = await api(role=role)
        price_list1 = await dataset.price_list()
        await t.post_ok(
            'api_admin_price_lists_load',
            json={'price_list_id': [price_list1.price_list_id,
                                    uuid()]})
        t.status_is(403, diag=True)


async def test_load_multiple_store(tap, api, dataset):
    with tap.plan(5):
        store = await dataset.store()
        price_list1 = await dataset.price_list(company_id=store.company_id)
        store.price_list_id = price_list1.price_list_id
        await store.save()
        user = await dataset.user(store=store, role='store_admin')
        t = await api()
        t.set_user(user)
        await t.post_ok(
            'api_admin_price_lists_load',
            json={'price_list_id': [price_list1.price_list_id]})
        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'код успеха')
        t.json_has('price_list', 'есть в выдаче')
        res = t.res['json']['price_list']
        tap.eq_ok(
            res[0]['price_list_id'],
            price_list1.price_list_id,
            'Пришли правильные объекты'
        )


async def test_foreign_company(tap, api, dataset):
    with tap.plan(11, 'загружать можно только из своей компании'):
        company_1 = await dataset.company()
        tap.ok(company_1, 'company_1 created')

        company_2 = await dataset.company()
        tap.ok(company_2, 'company_2 created')

        price_list = await dataset.price_list(company_id=company_1.company_id)
        tap.ok(price_list, 'price_list created')

        user_1 = await dataset.user(company_id=company_1.company_id,
                                    role='company_admin')
        tap.ok(user_1, 'user_1 created')

        user_2 = await dataset.user(company_id=company_2.company_id,
                                    role='company_admin')
        tap.ok(user_2, 'user_2 created')

        t = await api(user=user_1)

        await t.post_ok(
            'api_admin_price_lists_load',
            json={'price_list_id': price_list.price_list_id},
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        t.set_user(user_2)

        await t.post_ok(
            'api_admin_price_lists_load',
            json={'price_list_id': price_list.price_list_id},
        )
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS')
