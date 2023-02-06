import pytest


async def test_load_nf(tap, api, uuid):
    with tap.plan(4, 'Неизвестный идентификатор'):
        t = await api(role='admin')

        await t.post_ok('api_admin_companies_load',
                        json={'company_id': uuid()})

        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS', 'нет доступа')
        t.json_is('message', 'Access denied', 'текст')


async def test_load(tap, api, dataset):
    with tap.plan(6, 'Успешная загрузка'):

        company = await dataset.company()

        t = await api(role='admin')

        await t.post_ok('api_admin_companies_load',
                        json={'company_id': company.company_id})

        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'получен')

        t.json_is('company.company_id', company.company_id)
        t.json_is('company.title', company.title)
        t.json_is('company.ownership', company.ownership)


@pytest.mark.parametrize('role', ['admin'])
async def test_load_multiple(tap, api, dataset, role):
    with tap.plan(5, 'Успешная загрузка списка'):
        t = await api(role=role)
        company1 = await dataset.company()
        company2 = await dataset.company()
        await t.post_ok(
            'api_admin_companies_load',
            json={'company_id': [company1.company_id,
                                 company2.company_id]})
        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'код успеха')
        t.json_has('company', 'есть в выдаче')
        res = t.res['json']['company']
        tap.eq_ok(
            sorted([res[0]['company_id'], res[1]['company_id']]),
            sorted([company1.company_id,
                    company2.company_id]),
            'Пришли правильные объекты'
        )


@pytest.mark.parametrize('role', ['admin'])
async def test_load_multiple_fail(tap, api, dataset, uuid, role):
    with tap.plan(2, 'Неизвестные идентификаторы в списке'):
        t = await api(role=role)
        company1 = await dataset.company()
        await t.post_ok(
            'api_admin_companies_load',
            json={'company_id': [company1.company_id,
                                 uuid()]})
        t.status_is(403, diag=True)


@pytest.mark.parametrize('role', ['admin', 'support'])
async def test_access_granted(tap, api, dataset, role):
    with tap.plan(2, 'Разрешаем смотреть не свои'):
        company1    = await dataset.company()
        company2    = await dataset.company()
        store       = await dataset.store(company=company1)
        user        = await dataset.user(store=store, role=role)

        t = await api(user=user)
        await t.post_ok(
            'api_admin_companies_load',
            json={'company_id': [company1.company_id,
                                 company2.company_id]})
        t.status_is(200, diag=True)


@pytest.mark.parametrize('role', ['store_admin', 'provider'])
async def test_access_denied(tap, api, dataset, role):
    with tap.plan(2, 'Запрещаем смотреть не свои'):
        company1    = await dataset.company()
        company2    = await dataset.company()
        store       = await dataset.store(company=company1)
        user        = await dataset.user(store=store, role=role)

        t = await api(user=user)
        await t.post_ok(
            'api_admin_companies_load',
            json={'company_id': [company1.company_id,
                                 company2.company_id]})
        t.status_is(403, diag=True)
