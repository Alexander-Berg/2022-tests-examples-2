import pytest


@pytest.mark.parametrize('role', ['admin', 'barcode_executer'])
async def test_options(api, tap, dataset, role):
    with tap.plan(9, 'Получение настроек пользователя'):

        user = await dataset.user(role=role)

        t = await api(user=user)

        await t.get_ok('api_courier_user_options')
        t.status_is(200, diag=True)

        t.json_is('code', 'OK', 'code')
        t.json_has('user', 'user')
        t.json_has('permits', 'permits')
        t.json_has('constants')
        t.json_has('constants.backend_version')
        t.json_has('constants.store.options')
        t.json_like(
            'now',
            r'^\d{4}(-\d{2}){2}'
            r'[ Tt]'
            r'\d{2}(:\d{2}){2}'
            r'\s?[+-]\d{2}:?\d{2}$'
        )


async def test_options_guest(api, tap):
    with tap.plan(8, 'Получение настроек пользователя'):

        t = await api()

        await t.get_ok('api_courier_user_options')
        t.status_is(200, diag=True)

        t.json_is('code', 'OK', 'code')
        t.json_has('user', 'user')
        t.json_has('permits', 'permits')
        t.json_has('constants')
        t.json_has('constants.backend_version')
        t.json_is('constants.store', None)
