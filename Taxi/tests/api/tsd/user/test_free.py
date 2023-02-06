from libstall.util import token

async def test_free(tap, api, dataset, uuid, cfg):
    with tap.plan(20, 'Снижение авторизации'):
        user = await dataset.user(role='barcode_executer')
        tap.ok(user, 'пользователь создан')

        device_id = uuid()

        t = await api()
        await t.post_ok('api_tsd_user_assign_device',
                        json={
                            'device': device_id,
                            'barcode': user.qrcode
                        },
                        desc='Логинимся по QR-коду')
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        tap.ok(await user.reload(), 'пользователь перегружен')
        tap.in_ok(device_id, user.device, 'device_id прописалось пользователю')
        stoken = user.token()


        await t.post_ok('api_tsd_user_free_device',
                        json={'device': device_id},
                        headers={'Authorization': f'bearer {stoken}'})
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('store', user.store_id)
        t.json_is('mode', 'wms')
        t.json_like('token', r'^\S+$', 'токен')

        tap.ok(await user.reload(), 'пользователь перегружен')
        tap.not_in_ok(device_id, user.device, 'device_id больше нет')


        stoken = t.res['json']['token']

        payload = token.unpack(cfg('web.auth.secret'), stoken)
        tap.isa_ok(payload, dict, 'Токен распакован')
        tap.eq(payload['force_role'], 'free_device', 'Роль сменилась')
        tap.eq(payload['user_id'], user.user_id, 'id сохранился')

        await t.post_ok('api_tsd_user_free_device',
                        json={'device': device_id},
                        headers={'Authorization': f'bearer {stoken}'})
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS')
