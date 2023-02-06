import pytest


async def test_load_nf(tap, api, uuid):
    with tap.plan(4):
        t = await api(role='admin')

        await t.post_ok('api_admin_providers_load',
                        json={'provider_id': uuid()})

        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS', 'нет доступа к не нашим полкам')
        t.json_is('message', 'Access denied', 'текст')


@pytest.mark.parametrize('role', ['admin'])
async def test_load(tap, api, dataset, role):
    with tap.plan(6):

        provider = await dataset.provider()
        tap.ok(provider, 'полка сгенерирована')

        t = await api(role=role)

        await t.post_ok('api_admin_providers_load',
                        json={'provider_id': provider.provider_id})

        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'полка получена')

        t.json_is('provider.provider_id',
                  provider.provider_id, 'идентификатор полки')
        t.json_is('provider.title', provider.title, 'название')


@pytest.mark.parametrize('role', ['admin'])
async def test_load_multiple(tap, api, dataset, role):
    with tap.plan(5):
        t = await api(role=role)
        provider1 = await dataset.provider()
        provider2 = await dataset.provider()
        await t.post_ok(
            'api_admin_providers_load',
            json={'provider_id': [provider1.provider_id,
                                  provider2.provider_id]})
        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'код успеха')
        t.json_has('provider', 'есть в выдаче')
        res = t.res['json']['provider']
        tap.eq_ok(
            sorted([res[0]['provider_id'], res[1]['provider_id']]),
            sorted([provider1.provider_id,
                    provider2.provider_id]),
            'Пришли правильные объекты'
        )


@pytest.mark.parametrize('role', ['executer', 'barcode_executer',
                                  'expansioner', 'category_manager'])
async def test_load_multiple_fail(tap, api, dataset, uuid, role):
    with tap.plan(2):
        t = await api(role=role)
        provider1 = await dataset.provider()
        await t.post_ok(
            'api_admin_providers_load',
            json={'provider_id': [provider1.provider_id,
                                  uuid()]})
        t.status_is(403, diag=True)
