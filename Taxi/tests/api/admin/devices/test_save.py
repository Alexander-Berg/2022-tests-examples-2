async def test_update_status(api,
                             tap,
                             dataset):
    with tap.plan(4):
        store = await dataset.store()
        user = await dataset.user(role='admin',
                                  store=store)

        t = await api(user=user)

        device = await dataset.device(store=store,
                                      status='active')

        await t.post_ok('api_admin_devices_save',
                        json={'device_id': device.device_id,
                              'status': 'inactive'})
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        await device.reload()

        tap.eq(device.status, 'inactive', 'Статус изменился')


async def test_create_no_key(api,
                             tap,
                             dataset,
                             random_title):
    with tap.plan(2):
        store = await dataset.store()

        user = await dataset.user(role='admin',
                                  store=store)

        t = await api(user=user)

        await t.post_ok('api_admin_devices_save',
                        json={'title': random_title})
        t.status_is(403, diag=True)


async def test_update_title(api, tap, dataset):
    with tap.plan(4):
        store = await dataset.store()
        user = await dataset.user(role='admin',
                                  store=store)

        t = await api(user=user)

        device = await dataset.device(store=store,
                                      title='Самсунг')

        await t.post_ok('api_admin_devices_save',
                        json={'device_id': device.device_id,
                              'title': 'Элджи'})
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        await device.reload()

        tap.eq(device.title, 'Элджи', 'Наименование новое')


async def test_update_lang(api, tap, dataset):
    with tap.plan(5):
        store = await dataset.store()
        user = await dataset.user(role='admin',
                                  store=store)

        t = await api(user=user)

        device = await dataset.device(store=store,
                                      lang='en_US',
                                      title='Самсунг')

        await t.post_ok('api_admin_devices_save',
                        json={'device_id': device.device_id,
                              'lang': 'ru_RU',
                              'title': 'Элджи'})
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        await device.reload()

        tap.eq(device.title, 'Элджи', 'Наименование новое')
        tap.eq(device.lang, 'ru_RU', 'Язык поменялся')


async def test_update_wrong_role(api, tap, dataset):
    with tap.plan(2):
        store = await dataset.store()
        user = await dataset.user(role='courier',
                                  title='Самсунг',
                                  store=store)

        t = await api(user=user)

        device = await dataset.device(store=store, status='active')

        await t.post_ok('api_admin_devices_save',
                        json={'device_id': device.device_id,
                              'title': 'Элджи'})
        t.status_is(403, diag=True)


async def test_create_and_edit(api,
                               tap,
                               dataset,
                               random_secret_key,
                               random_title):
    with tap.plan(10):
        store = await dataset.store(lang='en_US')
        user = await dataset.user(role='admin',
                                  store=store)
        secret_key = random_secret_key
        title = random_title

        t = await api(user=user)

        await t.post_ok('api_admin_devices_save',
                        json={'secret_key': secret_key,
                              'title': title})
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        device_id = t.res['json']['device']['device_id']
        tap.eq(t.res['json']['device']['status'], 'active', 'Статус active')
        tap.eq(t.res['json']['device']['lang'], 'en_US', 'Язык как у стора')

        await t.post_ok('api_admin_devices_save',
                        json={'device_id': device_id,
                              'status': 'inactive'})
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        tap.eq(t.res['json']['device']['status'],
               'inactive',
               'Статус изменился')
        tap.eq(t.res['json']['device']['title'],
               random_title,
               'Наименование верное')


async def test_create_wrong_role(api,
                                 tap,
                                 dataset,
                                 random_secret_key,
                                 random_title):
    with tap.plan(2):
        store = await dataset.store()

        user = await dataset.user(role='courier',
                                  store=store)

        t = await api(user=user)

        await t.post_ok('api_admin_devices_save',
                        json={'secret_key': random_secret_key,
                              'title': random_title})
        t.status_is(403, diag=True)


async def test_created_device_in_list(api,
                                      tap,
                                      dataset,
                                      random_secret_key,
                                      random_title):
    with tap.plan(8):
        store = await dataset.store()
        user = await dataset.user(role='admin',
                                  store=store)
        secret_key = random_secret_key
        title = random_title

        t = await api(user=user)

        await t.post_ok('api_admin_devices_save',
                        json={'secret_key': secret_key,
                              'title': title})
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        device_id = t.res['json']['device']['device_id']

        await t.post_ok('api_admin_devices_list',
                        json={'store_id': user.store_id})
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        tap.eq_ok(len(t.res['json']['devices']), 1, 'Девайс приехал')
        tap.eq_ok(t.res['json']['devices'][0]['device_id'],
                  device_id,
                  'В ответе есть id')
