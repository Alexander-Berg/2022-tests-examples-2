from stall.model.role import Role
from libstall.util import token


async def test_upgrade(tap, dataset, api, cfg):
    with tap.plan(31, 'апгрейд авторизации TSD'):
        store = await dataset.store()
        tap.ok(store, 'склад создан')

        user = await dataset.user(store=store, role='barcode_executer')
        tap.eq(user.store_id, store.store_id, 'пользователь создан')
        tap.eq(user.role, 'executer', 'роль')
        tap.eq(user.force_role, 'barcode_executer', 'роль авторизации')

        t = await api(user=user)
        await t.post_ok('api_tsd_user_options', json={})
        t.status_is(200, diag=True)
        t.json_has('permits')
        tap.eq(
            {
                p['value']
                for p in t.res['json']['permits']
                if p['name'] == 'tsd_upgrade'
            },
            {True},
            'роль неапгрейденного'
        )


        await t.post_ok('api_tsd_user_upgrade',
                        json={
                            'pin': '99999999',
                        })
        t.status_is(403, diag=True)

        for attempt in range(2):
            await t.post_ok('api_tsd_user_upgrade',
                            json={
                                'pin': user.pin,
                            },
                            desc=f'upgrade {attempt} попытка')
            t.status_is(200, diag=True)
            t.json_is('code', 'OK')
            t.json_has('token')
            tap.eq(
                {
                    p['value']
                    for p in t.res['json']['permits']
                    if p['name'] == 'tsd_upgrade'
                },
                {False},
                'роль апгрейденного'
            )

            token_str = t.res['json']['token']
            tp = token.unpack(cfg('web.auth.secret'), token_str)
            tap.isa_ok(tp, dict, 'токен распакован')
            tap.in_ok('force_role', tp, 'force_role есть')
            tap.eq(tp['force_role'], 'executer', 'роль итоговая')


        user.force_role = Role('executer')
        await t.post_ok('api_tsd_user_downgrade', json={})
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('token')
        tap.eq(
            {
                p['value']
                for p in t.res['json']['permits']
                if p['name'] == 'tsd_upgrade'
            },
            {True},
            'роль неапгрейденного'
        )
