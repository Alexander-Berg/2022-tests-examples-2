from stall.model.user import User


async def test_get_roles(tap, api, dataset):
    with tap.plan(12):
        t = await api(role='token:web.idm.tokens.0')

        # специально создадим неправильного пользователя
        await dataset.user(provider='yandex-team', company_id=None,
                           role='store_admin')

        for _ in range(101):
            await dataset.user(provider='yandex-team')

        first_batch = await User.list(
            by='look',
            conditions=(
                ('provider', 'yandex-team'),
                ('role', 'NOT IN', ('authen_guest', 'guest', 'courier',
                                    'executer', 'barcode_executer',
                                    'stocktaker', 'free_device')),
            ),
        )
        first_user = first_batch.list[0]
        first_user.status = 'disabled'
        first_user.provider = 'yandex-team'
        first_user.role = 'store_admin'
        await first_user.save()

        await t.get_ok('/api/idm/get-roles/')

        t.status_is(200, diag=True)
        t.json_is('code', 0)
        t.json_has('roles.99.path')
        t.json_has('roles.99.uid')
        t.json_has('next-url')

        t.json_is('roles.0.uid', first_user.provider_user_id,
                  'disabled user returned')

        next_url = t.res['json']['next-url']

        await t.get_ok(next_url)
        t.status_is(200, diag=True)
        t.json_is('code', 0)
        t.json_has('roles.0.path')
        t.json_has('roles.0.uid')
