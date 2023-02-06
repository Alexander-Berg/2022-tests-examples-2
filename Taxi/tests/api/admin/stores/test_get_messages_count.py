async def test_get_messages_count(tap, api, dataset):
    with tap.plan(4):
        store = await dataset.store(messages_count=23)
        user = await dataset.user(store=store, role='admin')

        t = await api(user=user)

        await t.post_ok('api_admin_stores_get_messages_count')
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('count', 23)


async def test_no_store(tap, api, dataset):
    with tap.plan(3):
        user = await dataset.user(role='admin')
        user.store_id = None
        await user.save()

        t = await api(user=user)

        await t.post_ok('api_admin_stores_get_messages_count')
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS')


async def test_access_denied(tap, api):
    with tap.plan(3):
        t = await api(role='executer')

        await t.post_ok('api_admin_stores_get_messages_count')
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS')
