from stall.client.personal import client as personal
from stall.model.user import User


async def test_common(tap, dataset, api, ext_api, uuid):
    with tap.plan(15, 'создание пользователя через ручку'):
        company = await dataset.company()
        tap.ok(company, 'company created')

        store = await dataset.store(company=company)
        tap.ok(store, 'store created')

        # pylint: disable=unused-argument
        async def bulk_store(request):
            return {
                'items': [
                    {'id': uuid()},
                ],
            }

        async with await ext_api(personal, bulk_store):
            t = await api(token=company.token)
            await t.post_ok(
                'api_external_users_create',
                json={
                    'fullname': 'Василий Пупкин',
                    'employee_number': '123',
                    'phone': '88005553535',
                },
            )

            t.status_is(200, diag=True)
            t.json_is('code', 'OK')
            t.json_has('user')
            t.json_has('user.user_id')
            t.json_is('user.employee_number', '123')
            t.json_is('user.phone', '88005553535')
            t.json_is('user.status', 'active')

            user_id = t.res['json']['user']['user_id']

            user = await User.load(user_id)
            tap.ok(user, 'one user created')
            tap.eq(user.user_id, user_id, 'user_id correct')
            tap.eq(user.company_id, company.company_id, 'company_id correct')
            tap.eq(user.fullname, 'Василий Пупкин', 'fullname correct')
            tap.eq(user.nick, 'vasilii_pupkin', 'nick slugified')


async def test_employee_number_conflict(tap, dataset, api, ext_api, uuid):
    with tap.plan(15, 'создание пользователя с существующим employee_number'):
        company = await dataset.company()
        tap.ok(company, 'company created')

        store = await dataset.store(company=company)
        tap.ok(store, 'store created')

        user = await dataset.user(store=store, employee_number='123')
        tap.ok(user, 'user created')
        tap.eq(user.employee_number, '123', 'employee number created')

        # pylint: disable=unused-argument
        async def bulk_store(request):
            return {
                'items': [
                    {'id': uuid()},
                ],
            }

        async with await ext_api(personal, bulk_store):

            t = await api(token=company.token)
            await t.post_ok(
                'api_external_users_create',
                json={
                    'fullname': 'asdfasdf',
                    'employee_number': '123',
                    'phone': '88005553535',
                },
            )

            t.status_is(400, diag=True)
            t.json_is('code', 'ER_EMPLOYEE_NUMBER_CONFLICT')

            t = await api(token=company.token)
            await t.post_ok(
                'api_external_users_create',
                json={
                    'fullname': 'asdfasdf',
                    'employee_number': '234',
                    'phone': '88005553535',
                },
            )

            t.status_is(200, diag=True)
            t.json_is('code', 'OK')
            t.json_has('user')
            t.json_has('user.user_id')
            t.json_is('user.employee_number', '234')
            t.json_is('user.phone', '88005553535')
            t.json_is('user.status', 'active')


async def test_wrong_token(tap, dataset, api, uuid):
    with tap.plan(12, 'авторизация только по токену компании'):
        t = await api(token=uuid())
        await t.post_ok(
            'api_external_users_create',
            json={
                'fullname': 'asdfasdf',
                'employee_number': '123',
                'phone': '88005553535',
            },
        )
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS')

        t = await api(role='executer')
        await t.post_ok(
            'api_external_users_create',
            json={
                'fullname': 'asdfasdf',
                'employee_number': '123',
                'phone': '88005553535',
            },
        )
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS')

        user = await dataset.user()
        t = await api(user=user)
        await t.post_ok(
            'api_external_users_create',
            json={
                'fullname': 'asdfasdf',
                'employee_number': '123',
                'phone': '88005553535',
            },
        )
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS')

        t = await api(role='token:web.external.tokens.0')
        await t.post_ok(
            'api_external_users_create',
            json={
                'fullname': 'asdfasdf',
                'employee_number': '123',
                'phone': '88005553535',
            },
        )
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_COMPANY_TOKEN')


async def test_pd(tap, dataset, api, uuid, unique_phone, ext_api):
    with tap.plan(6, 'Проверка работы с ПД'):
        company = await dataset.company()

        new_phone_pd_id = uuid()

        # pylint: disable=unused-argument
        async def bulk_store(request):
            return {
                'items': [
                    {'id': new_phone_pd_id},
                ],
            }

        async with await ext_api(personal, bulk_store):
            t = await api(token=company.token)
            await t.post_ok(
                'api_external_users_create',
                json={
                    'fullname': 'Василий Пупкин',
                    'employee_number': '123',
                    'phone': unique_phone(),
                },
            )

            t.status_is(200, diag=True)
            t.json_is('code', 'OK')
            t.json_has('user')
            t.json_has('user.user_id')
            t.json_is('user.phone_pd_id', new_phone_pd_id)


async def test_pd_fail(tap, dataset, api, unique_phone, ext_api):
    with tap.plan(2, 'Проверка работы с недоступным сервером ПД'):
        company = await dataset.company()

        # pylint: disable=unused-argument
        async def bulk_store(request):
            return 500, ''

        async with await ext_api(personal, bulk_store):

            t = await api(token=company.token)
            await t.post_ok(
                'api_external_users_create',
                json={
                    'fullname': 'Василий Пупкин',
                    'employee_number': '123',
                    'phone': unique_phone(),
                },
            )

            t.status_is(424, diag=True)
