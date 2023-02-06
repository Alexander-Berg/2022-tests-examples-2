import pytest


async def test_wrong_store(api, tap, dataset, uuid):
    with tap.plan(4):

        store = await dataset.store()
        user  = await dataset.user(store=store, role='admin')

        t = await api(user=user)

        await t.post_ok(
            'api_admin_stores_join_store',
            json={'store_id': uuid()},
        )
        t.status_is(404, diag=True)

        t.json_is('code', 'ER_NOT_FOUND', 'code')
        t.json_is('message', 'Store not found', 'message')


async def test_wrong_company(api, tap, dataset):
    with tap.plan(3, 'Менять компании нельзя если нет пермита'):
        company1 = await dataset.company()
        company2 = await dataset.company()

        store1 = await dataset.store(company=company1)
        store2 = await dataset.store(company=company2)

        user = await dataset.user(store=store1, role='admin')

        # NOTE: разрешим менять склады но запретим менять компании
        with user.role as role:
            role.remove_permit('join_company')
            role.add_permit('join_store', True)

            t = await api(user=user)

            await t.post_ok(
                'api_admin_stores_join_store',
                json={'store_id': store2.store_id}
            )
            t.status_is(403, diag=True)
            t.json_is('code', 'ER_COMPANY_ACCESS')


async def test_join(api, tap, dataset):
    with tap.plan(8, 'Смена склада внутри компании'):
        company = await dataset.company()
        store1 = await dataset.store(company=company)
        store2 = await dataset.store(company=company)

        user = await dataset.user(store=store1, role='admin')
        tap.ne(
            user.store_id,
            store2.store_id,
            'пользователь неприсоединен на склад'
        )
        tap.eq(
            user.company_id,
            store2.company_id,
            'в той же компании'
        )

        t = await api(user=user)
        await t.post_ok('api_admin_stores_join_store',
                        json={'store_id': store2.store_id})
        t.status_is(200, diag=True)

        t.json_is('code', 'OK', 'code')
        t.json_is('message', f'joined store {store2.store_id}', 'message')

        user = await user.load(user.user_id)

        tap.eq(
            user.store_id,
            store2.store_id,
            'пользователь присоединен на склад'
        )
        tap.eq(
            user.company_id,
            store1.company_id,
            'компания не менялась'
        )


async def test_join_company(api, tap, dataset):
    with tap.plan(6, 'Смена между компаниями требует пермит'):
        company1 = await dataset.company()
        company2 = await dataset.company()

        store1 = await dataset.store(company=company1)
        store2 = await dataset.store(company=company2)

        user = await dataset.user(store=store1, role='admin')

        with user.role as role:
            # NOTE: разрешим менять склады и компании
            role.add_permit('join_company', True)
            role.add_permit('join_store', True)

            t = await api(user=user)
            await t.post_ok('api_admin_stores_join_store',
                            json={'store_id': store2.store_id})
            t.status_is(200, diag=True)

            t.json_is('code', 'OK', 'code')
            t.json_is('message', f'joined store {store2.store_id}', 'message')

            user = await user.load(user.user_id)

            tap.eq(
                user.store_id,
                store2.store_id,
                'пользователь присоединен на склад'
            )
            tap.eq(
                user.company_id,
                company2.company_id,
                'компания менялась'
            )


@pytest.mark.parametrize('role', ['admin', 'support'])
async def test_stores_allow(api, tap, dataset, role):
    with tap.plan(18, 'прикрепляемся к разрешенным лавкам'):

        company = await dataset.company()
        store1 = await dataset.store(company=company)
        store2 = await dataset.store(company=company)

        user = await dataset.user(role=role)
        tap.ok(user.has_permit('join_store'), 'может прилепляться к лавкам')
        tap.ok(
            user.stores_allow == [],
            'разрешенные лавки не заданы, можно крепиться ко всем',
        )

        t = await api()
        t.set_user(user)

        await t.post_ok(
            'api_admin_stores_join_store',
            json={'store_id': store1.store_id},
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        await user.reload()
        tap.eq_ok(user.store_id, store1.store_id, 'прилепился к лавке 1')

        await t.post_ok(
            'api_admin_stores_join_store',
            json={'store_id': store2.store_id},
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        await user.reload()
        tap.eq_ok(user.store_id, store2.store_id, 'прилепился к лавке 2')

        user.stores_allow = [store1.store_id]
        await user.save()

        await t.post_ok(
            'api_admin_stores_join_store',
            json={'store_id': store1.store_id},
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        await user.reload()
        tap.eq_ok(
            user.store_id,
            store1.store_id,
            'прилепился к лавке 1, так как она в разрешенных',
        )

        await t.post_ok(
            'api_admin_stores_join_store',
            json={'store_id': store2.store_id},
        )
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS')
        tap.eq_ok(
            user.store_id,
            store1.store_id,
            'не прилепился к лавке 2, так как она не в разрешенных',
        )
