import pytest

from stall.backend_version import version
from stall.model.role import Role


async def test_options_guest(api, tap):
    with tap.plan(19):
        t = await api()

        await t.get_ok('api_profile_options')
        t.status_is(200, diag=True)

        t.json_is('code', 'OK', 'code')
        t.json_has('user', 'user')
        t.json_has('permits', 'permits')

        t.json_has('constants.shelf.types')
        t.json_has('constants.shelf.tags')

        t.json_has('constants.order.statuses')
        t.json_has('constants.order.types')
        t.json_has('constants.order.targets')
        t.json_has('constants.order.sources')

        t.json_has('constants.store.statuses')
        t.json_has('constants.store.types')
        t.json_has('constants.store.sources')
        t.json_hasnt('constants.store.options')
        t.json_hasnt('constants.store.options_setup')
        t.json_hasnt('constants.store.tz')

        t.json_is('constants.backend_version', version)
        t.json_like(
            'now',
            r'^\d{4}(-\d{2}){2}'
            r'[ Tt]'
            r'\d{2}(:\d{2}){2}'
            r'\s?[+-]\d{2}:?\d{2}$'
        )


@pytest.mark.parametrize('provider', ['yandex', 'yandex-team', 'test'])
async def test_options_admin(api, tap, dataset, provider):
    with tap.plan(12):
        user = await dataset.user(role='admin', provider=provider)
        tap.ok(user, 'пользователь создан')
        tap.eq(user.provider, provider, 'провайдер')
        tap.eq(user.role, 'admin', 'админ')

        t = await api()
        t.set_user(user)

        await t.get_ok('api_profile_options')
        t.status_is(200, diag=True)

        t.json_is('code', 'OK', 'code')
        t.json_has('user', 'user')
        t.json_has('permits', 'permits')
        t.json_has('constants')
        t.json_has('constants.store.options')
        t.json_has('constants.store.options_setup')
        t.json_has('constants.store.tz')


@pytest.mark.parametrize('role', Role.storable_roles())
async def test_options_role(api, tap, dataset, role):
    with tap.plan(5, f'options для роли {role}'):
        user = await dataset.user(role=role)
        tap.ok(user, f'пользователь создан {role}')

        t = await api(user=user)
        await t.get_ok('api_profile_options')
        t.json_is('code', 'OK', 'code')
        t.json_has('user', 'user')
        t.json_has('permits', 'permits')


@pytest.mark.parametrize('role', Role.storable_roles())
async def test_options_mutate(api, tap, dataset, role):
    with tap.plan(5, f'mutate для роли {role}'):
        user = await dataset.user(super_role=role)
        tap.ok(user, f'пользователь создан {role}')

        t = await api(user=user)
        await t.get_ok('api_profile_options')
        t.json_is('code', 'OK', 'code')
        t.json_has('user', 'user')
        expected_mutate = sorted(Role(role).permits().get('sub', []))
        t.json_is('mutate', expected_mutate)


async def test_disabled(api, tap, dataset):
    with tap.plan(10, 'Авторизованный но отключенный - гость'):
        user = await dataset.user()
        tap.ok(user, 'пользователь создан')

        t = await api(user=user)
        await t.get_ok('api_profile_options')

        t.json_is('code', 'OK', 'code')
        t.json_has('user', 'user')
        t.json_is('user.role', 'admin')

        user.status = 'disabled'
        tap.ok(await user.save(), 'выключен')

        t = await api(user=user)
        await t.get_ok('api_profile_options')

        t.json_is('code', 'OK', 'code')
        t.json_has('user', 'user')
        t.json_is('user.role', 'guest')
