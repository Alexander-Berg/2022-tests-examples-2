async def test_wrong_id(api, tap, uuid, dataset):
    with tap.plan(4, 'Неверный идентификатор компании'):

        store = await dataset.store()
        user  = await dataset.user(store=store, role='admin')

        t = await api(user=user)

        await t.post_ok('api_admin_companies_join_company',
                        json={'company_id': uuid()})
        t.status_is(404, diag=True)

        t.json_is('code', 'ER_NOT_FOUND', 'code')
        t.json_is('message', 'Company not found', 'message')


async def test_no_permit(api, tap, dataset):
    with tap.plan(3, 'Менять компании нельзя если нет пермита'):
        company1 = await dataset.company()
        company2 = await dataset.company()

        store1 = await dataset.store(company=company1)

        user = await dataset.user(store=store1, role='admin')

        with user.role as role:
            # NOTE: разрешим менять склады но запретим менять компании
            role.remove_permit('join_company')

            t = await api(user=user)

            await t.post_ok(
                'api_admin_companies_join_company',
                json={'company_id': company2.company_id}
            )
            t.status_is(403, diag=True)
            t.json_is('code', 'ER_ACCESS')


async def test_join(api, tap, dataset):
    with tap.plan(6, 'Смена компании'):
        company1 = await dataset.company()
        company2 = await dataset.company()

        store1 = await dataset.store(company=company1)

        user = await dataset.user(store=store1, role='admin')

        with user.role as role:
            role.add_permit('join_company', True)
            role.add_permit('join_store', True)

            t = await api(user=user)
            await t.post_ok('api_admin_companies_join_company',
                            json={'company_id': company2.company_id})
            t.status_is(200, diag=True)

            t.json_is('code', 'OK', 'code')
            t.json_is(
                'message', f'joined company {company2.company_id}', 'message')

            user = await user.load(user.user_id)

            tap.eq(
                user.company_id,
                company2.company_id,
                'пользователь присоединен на склад'
            )
            tap.eq(user.store_id, None, 'Склад сброшен')


async def test_lose(api, tap, dataset):
    with tap.plan(3, 'Защита от потери склада'):
        company1 = await dataset.company()
        company2 = await dataset.company()

        store1 = await dataset.store(company=company1)

        user = await dataset.user(store=store1, role='admin')

        with user.role as role:
            role.add_permit('join_company', True)
            # Уберем возможность пользователя прекрепляться к складу
            role.add_permit('join_store', False)

            t = await api(user=user)
            await t.post_ok('api_admin_companies_join_company',
                            json={'company_id': company2.company_id})
            t.status_is(403, diag=True)
            t.json_is('code', 'ER_STORE_LOSE')
