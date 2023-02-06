async def test_get_devices_wrong_role(api, tap, dataset):
    with tap.plan(2):
        store = await dataset.store()
        user = await dataset.user(role='courier',
                                  store=store)
        await dataset.device(store=store)
        await dataset.device(store=store)
        t = await api(user=user)

        await t.post_ok('api_admin_devices_list',
                        json={'store_id': user.store_id})
        t.status_is(403, diag=True)


async def test_get_devices(api, tap, dataset):
    with tap.plan(5):
        store = await dataset.store()
        user = await dataset.user(role='admin',
                                  store=store)
        await dataset.device(store=store)
        await dataset.device(store=store)
        t = await api(user=user)

        await t.post_ok('api_admin_devices_list',
                        json={'store_id': user.store_id})
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        tap.eq_ok(len(t.res['json']['devices']), 2, 'Приехали 2 девайса')
        tap.ok('device_id' in t.res['json']['devices'][0], 'В ответе есть id')


async def test_get_devices_no_devices(api, tap, dataset):
    with tap.plan(4):
        store = await dataset.store()
        user = await dataset.user(role='admin',
                                  store=store)

        t = await api(user=user)

        await t.post_ok('api_admin_devices_list',
                        json={'store_id': user.store_id})
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        tap.eq_ok(len(t.res['json']['devices']), 0, 'Девайсов нет')
