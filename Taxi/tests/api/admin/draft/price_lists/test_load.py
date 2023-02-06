import pytest


@pytest.mark.parametrize('role', ['admin', 'category_manager'])
async def test_found(tap, api, dataset, role):
    with tap.plan(9):
        t = await api(role=role)

        price_list = await dataset.draft_price_list()
        tap.ok(price_list, 'Price-list created')

        await t.post_ok(
            'api_admin_draft_price_lists_load',
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
            'api_admin_draft_price_lists_load',
            json={'price_list_id': uuid()},
        )
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS')
        t.json_is('message', 'Access denied')


@pytest.mark.parametrize('role', ['admin', 'category_manager'])
async def test_permit_out_of_store(tap, api, dataset, role):
    with tap:
        price_list = await dataset.draft_price_list()
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
            'api_admin_draft_price_lists_load',
            json={'price_list_id': price_list.price_list_id},
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('price_list')


@pytest.mark.parametrize('role', ['admin', 'category_manager'])
async def test_load_multiple(tap, api, dataset, role):
    with tap.plan(5):
        t = await api(role=role)
        price_list1 = await dataset.draft_price_list()
        price_list2 = await dataset.draft_price_list()
        await t.post_ok(
            'api_admin_draft_price_lists_load',
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
        price_list1 = await dataset.draft_price_list()
        await t.post_ok(
            'api_admin_draft_price_lists_load',
            json={'price_list_id': [price_list1.price_list_id,
                                    uuid()]})
        t.status_is(403, diag=True)


async def test_foreign_company(tap, api, dataset):
    with tap.plan(10, 'загружать можно только из своей компании'):
        user = await dataset.user(role='company_admin')
        tap.ok(user, 'user created')

        price_list = await dataset.draft_price_list(company_id=user.company_id)
        tap.ok(price_list, 'price_list created')

        t = await api(user=user)

        await t.post_ok(
            'api_admin_draft_price_lists_load',
            json={'price_list_id': price_list.price_list_id}
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('price_list.company_id', user.company_id)

        foreign_user = await dataset.user(role='company_admin')
        tap.ok(foreign_user, 'foreign_user created')

        t.set_user(foreign_user)

        await t.post_ok(
            'api_admin_draft_price_lists_load',
            json={'price_list_id': price_list.price_list_id}
        )
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS')



async def test_not_found_without_permit(tap, api, uuid):
    with tap:
        t = await api(role='company_admin')

        await t.post_ok(
            'api_admin_draft_price_lists_load',
            json={'price_list_id': uuid()},
        )
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS')
        t.json_is('message', 'Access denied')
