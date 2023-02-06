async def test_common(tap, dataset, api):
    with tap.plan(7, 'получение файла'):
        user = await dataset.user()
        file_meta = await dataset.file_meta(user_id=user.user_id)

        t = await api(user=user)
        await t.post_ok(
            'api_admin_file_list',
            json={
                'store_id': user.store_id,
            }
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('file_meta')
        t.json_has('file_meta.0')
        t.json_is('file_meta.0.file_meta_id', file_meta.file_meta_id)
        t.json_hasnt('file_meta.1')


async def test_empty(tap, dataset, api):
    with tap.plan(5, 'файлов нет'):
        user = await dataset.user()

        t = await api(user=user)
        await t.post_ok(
            'api_admin_file_list',
            json={
                'store_id': user.store_id,
            }
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('file_meta')
        t.json_hasnt('file_meta.0')


async def test_access(tap, dataset, api):
    with tap.plan(12, 'доступ только к своим файлам'):
        user = await dataset.user()
        file_meta = await dataset.file_meta(user_id=user.user_id)

        t = await api(role='admin')
        await t.post_ok(
            'api_admin_file_list',
            json={
                'store_id': user.store_id,
            }
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('file_meta')
        t.json_has('file_meta.0')
        t.json_is('file_meta.0.file_meta_id', file_meta.file_meta_id)
        t.json_hasnt('file_meta.1')

        t = await api(role='store_admin')
        await t.post_ok(
            'api_admin_file_list',
            json={
                'store_id': user.store_id,
            }
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('file_meta')
        t.json_hasnt('file_meta.0')


async def test_status(tap, dataset, api):
    with tap.plan(12, 'по-умолчанию удалённые скрываются'):
        user = await dataset.user()
        file_meta = await dataset.file_meta(
            user_id=user.user_id, status='removed'
        )

        t = await api(user=user)

        await t.post_ok(
            'api_admin_file_list',
            json={
                'store_id': user.store_id,
            }
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('file_meta')
        t.json_hasnt('file_meta.0')

        await t.post_ok(
            'api_admin_file_list',
            json={
                'store_id': user.store_id,
                'status': ['new', 'uploaded', 'removing', 'removed']
            }
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('file_meta')
        t.json_has('file_meta.0')
        t.json_is('file_meta.0.file_meta_id', file_meta.file_meta_id)
        t.json_hasnt('file_meta.1')
