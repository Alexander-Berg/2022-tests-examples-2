import pytest


@pytest.mark.parametrize('role', ['admin', 'expansioner'])
async def test_load_unexists(tap, api, uuid, role):
    with tap.plan(4):
        t = await api(role=role)

        await t.post_ok('api_admin_assortments_load',
                        json={'assortment_id': uuid()})
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS', 'код ошибки')
        t.json_is('message', 'Access denied', 'текст ошибки')


@pytest.mark.parametrize('role', ['admin', 'category_manager'])
async def test_load(tap, api, dataset, role):
    with tap.plan(7):
        user = await dataset.user(role=role)
        t = await api(user=user)

        assortment = await dataset.assortment(company_id=user.company_id)
        tap.ok(assortment, 'ассортимент создан')

        await t.post_ok('api_admin_assortments_load',
                        json={'assortment_id': assortment.assortment_id})
        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'код успеха')
        t.json_has('assortment', 'ассортимент есть в выдаче')

        t.json_is('assortment.assortment_id',
                  assortment.assortment_id, 'assortment_id')
        t.json_is('assortment.title',
                  assortment.title, 'title')


async def test_load_access(tap, api, dataset):
    with tap.plan(24):

        assortment = await dataset.assortment()
        tap.ok(assortment, 'ассортимент сгенерирован')

        store = await dataset.store(company_id=assortment.company_id,
                                    assortment_id=assortment.assortment_id)
        tap.ok(store, 'склад сгенерирован')
        tap.eq(store.assortment_id,
               assortment.assortment_id,
               'ассортимент у склада')

        user = await dataset.user(store=store, role='store_admin')
        tap.ok(user, 'пользователь сгенерирован')
        tap.eq(user.store_id, store.store_id, 'на этом складе')
        tap.eq(user.role, 'store_admin', 'роль')

        user2 = await dataset.user(role='store_admin')
        tap.ok(user2, 'второй пользователь сгенерирован')
        tap.ne(user2.store_id, user.store_id, 'на другом складе')

        t = await api()
        t.set_user(user)

        await t.post_ok('api_admin_assortments_load',
                        json={'assortment_id': assortment.assortment_id})
        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'код успеха')
        t.json_has('assortment', 'ассортимент есть в выдаче')

        t.json_is('assortment.assortment_id',
                  assortment.assortment_id, 'assortment_id')
        t.json_is('assortment.title',
                  assortment.title, 'title')

        await t.post_ok('api_admin_assortments_load',
                        json={})
        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'код успеха')
        t.json_has('assortment', 'ассортимент есть в выдаче')

        t.json_is('assortment.assortment_id',
                  assortment.assortment_id, 'assortment_id')
        t.json_is('assortment.title',
                  assortment.title, 'title')

        t.set_user(user2)
        await t.post_ok('api_admin_assortments_load',
                        json={'assortment_id': assortment.assortment_id})
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS', 'код успеха')
        t.json_is('message', 'Access denied', 'нет доступа')


@pytest.mark.parametrize('role', ['admin', 'category_manager'])
async def test_load_multiple(tap, api, dataset, role):
    with tap.plan(6):
        user = await dataset.user(role=role)
        t = await api(user=user)
        assortment1 = await dataset.assortment(company_id=user.company_id)
        assortment2 = await dataset.assortment(company_id=user.company_id)

        assortment3 = await dataset.assortment()
        tap.ne(assortment3.company_id, user.company_id, 'foreign company')

        await t.post_ok(
            'api_admin_assortments_load',
            json={'assortment_id': [assortment1.assortment_id,
                                    assortment2.assortment_id]})
        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'код успеха')
        t.json_has('assortment', 'ассортимент есть в выдаче')
        res = t.res['json']['assortment']
        tap.eq_ok(
            sorted([res[0]['assortment_id'], res[1]['assortment_id']]),
            sorted([assortment1.assortment_id, assortment2.assortment_id]),
            'Пришли правильные ассортименты'
        )


@pytest.mark.parametrize('role', ['admin', 'category_manager'])
async def test_load_multiple_fail(tap, api, dataset, uuid, role):
    with tap.plan(2):
        t = await api(role=role)
        assortment1 = await dataset.assortment()
        await t.post_ok(
            'api_admin_assortments_load',
            json={'assortment_id': [assortment1.assortment_id,
                                    uuid()]})
        t.status_is(403, diag=True)


async def test_load_kitchen(tap, api, dataset):
    with tap.plan(10):
        company = await dataset.company()
        assortment = await dataset.assortment(
            company_id=company.company_id
        )
        kitchen_assortment = await dataset.assortment(
            company_id=company.company_id
        )
        store = await dataset.store(
            company_id=company.company_id,
            assortment_id=assortment.assortment_id,
            kitchen_assortment_id=kitchen_assortment.assortment_id,
        )
        user = await dataset.user(store=store, role='store_admin')
        t = await api(user=user)

        await t.post_ok(
            'api_admin_assortments_load',
            json={'assortment_id': kitchen_assortment.assortment_id})
        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'код успеха')
        t.json_has('assortment', 'ассортимент есть в выдаче')
        t.json_is('assortment.assortment_id',
                  kitchen_assortment.assortment_id, 'assortment_id')

        await t.post_ok(
            'api_admin_assortments_load',
            json={'assortment_id': [kitchen_assortment.assortment_id,
                                    assortment.assortment_id]})
        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'код успеха')
        t.json_has('assortment.0', 'ассортимент есть в выдаче')
        t.json_has('assortment.1', 'ассортимент есть в выдаче')


async def test_load_with_broken_store(tap, api, dataset):
    with tap.plan(4):
        user = await dataset.user(store_id='abrakadabra', role='store_admin')
        t = await api(user=user)

        await t.post_ok('api_admin_assortments_load', json={})
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS', 'код ошибки')
        t.json_is('message', 'Access denied', 'текст ошибки')


async def test_foreign_company(tap, api, dataset):
    with tap.plan(11, 'загружать можно только из своей компании'):
        user = await dataset.user(role='company_admin')
        tap.ok(user, 'user created')

        assortment = await dataset.assortment(company_id=user.company_id)
        tap.ok(assortment, 'assortment created')

        t = await api(user=user)

        await t.post_ok(
            'api_admin_assortments_load',
            json={'assortment_id': assortment.assortment_id}
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'код успеха')
        t.json_has('assortment', 'ассортимент есть в выдаче')

        t.json_is('assortment.assortment_id',
                  assortment.assortment_id, 'assortment_id')

        foreign_user = await dataset.user(role='company_admin')
        tap.ok(foreign_user, 'foreign_user created')

        t.set_user(foreign_user)

        await t.post_ok(
            'api_admin_assortments_load',
            json={'assortment_id': assortment.assortment_id}
        )
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS')
