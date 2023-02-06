import pytest


@pytest.mark.parametrize('role', ['admin'])
async def test_change(tap, api, dataset, role):
    with tap.plan(5, 'Получение токена'):

        company = await dataset.company()
        old_token = company.token

        t = await api(role=role)
        await t.post_ok(
            'api_admin_companies_token_change',
            json={'company_id': company.company_id},
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('token')
        t.json_isnt('token', old_token, 'Токен изменился')


async def test_unknown(tap, api, uuid):
    with tap.plan(3, 'Компания не найдена'):

        t = await api(role='admin')
        await t.post_ok(
            'api_admin_companies_token_change',
            json={'company_id': uuid()},
        )

        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS')


@pytest.mark.parametrize('role', ['provider', 'executer'])
async def test_denied(tap, api, dataset, role):
    with tap.plan(4, 'Нет прав'):

        company = await dataset.company()
        old_token = company.token

        t = await api(role=role)
        await t.post_ok(
            'api_admin_companies_token_change',
            json={'company_id': company.company_id},
        )

        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS')

        await company.reload()
        tap.eq(company.token, old_token, 'Токен не менялся')
