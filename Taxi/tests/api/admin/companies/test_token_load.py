import pytest


@pytest.mark.parametrize('role', ['admin'])
async def test_load(tap, api, dataset, role):
    with tap.plan(4, 'Получение токена'):

        company = await dataset.company()

        t = await api(role=role)
        await t.post_ok(
            'api_admin_companies_token_load',
            json={'company_id': company.company_id},
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('token')


async def test_unknown(tap, api, uuid):
    with tap.plan(3, 'Компания не найдена'):

        t = await api(role='admin')
        await t.post_ok(
            'api_admin_companies_token_load',
            json={'company_id': uuid()},
        )

        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS')


@pytest.mark.parametrize('role', ['provider', 'executer'])
async def test_denied(tap, api, dataset, role):
    with tap.plan(3, 'Нет прав'):

        company = await dataset.company()

        t = await api(role=role)
        await t.post_ok(
            'api_admin_companies_token_load',
            json={'company_id': company.company_id},
        )

        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS')
