import pytest


async def test_common(tap, dataset, api):
    with tap.plan(7, 'получение файла'):
        user = await dataset.user()
        file_meta = await dataset.file_meta(user_id=user.user_id)

        t = await api(user=user)
        await t.post_ok(
            'api_admin_file_load',
            json={
                'file_meta_id': file_meta.file_meta_id,
            }
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('file_meta')
        t.json_is('file_meta.file_meta_id', file_meta.file_meta_id)
        t.json_is('data_type', 'original')
        t.json_is('data', None)


async def test_load_foreign(tap, dataset, api):
    with tap.plan(10, 'попытка получения чужого файла'):
        user = await dataset.user()
        file_meta = await dataset.file_meta(user_id=user.user_id)

        t = await api(role='admin')
        await t.post_ok(
            'api_admin_file_load',
            json={
                'file_meta_id': file_meta.file_meta_id,
            }
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('file_meta')
        t.json_is('file_meta.file_meta_id', file_meta.file_meta_id)
        t.json_is('data_type', 'original')
        t.json_is('data', None)

        t = await api(role='store_admin')
        await t.post_ok(
            'api_admin_file_load',
            json={
                'file_meta_id': file_meta.file_meta_id,
            }
        )

        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS')


async def test_s3_download_ok(tap, dataset, api, s3_stubber, uuid):
    with tap.plan(6, 'загрузка данных из s3'):
        user = await dataset.user()
        file_meta = await dataset.file_meta(
            user_id=user.user_id,
            status='uploaded',
            attr={'bucket': uuid(), 'key': uuid()}
        )

        s3_stubber.for_get_object_ok(
            file_meta.attr['bucket'],
            file_meta.attr['key'],
            b'__data__'
        )
        s3_stubber.activate()

        t = await api(user=user)
        await t.post_ok(
            'api_admin_file_load',
            json={
                'file_meta_id': file_meta.file_meta_id,
                'download': True,
            }
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('file_meta.file_meta_id', file_meta.file_meta_id)
        t.json_is('data_type', 'base64')

        # encoded "__data__"
        t.json_is('data', 'X19kYXRhX18=')


@pytest.mark.parametrize('s3_error', ['NoSuchKey', 'NoSuchBucket'])
async def test_s3_download_file_gone(
        tap, dataset, api, s3_stubber, uuid, s3_error,
):
    with tap.plan(3, f'загрузка данных из s3 [{s3_error}]'):
        user = await dataset.user()
        file_meta = await dataset.file_meta(
            user_id=user.user_id,
            status='uploaded',
            attr={'bucket': uuid(), 'key': uuid()}
        )

        s3_stubber.for_get_object_error(
            file_meta.attr['bucket'],
            file_meta.attr['key'],
            s3_error
        )
        s3_stubber.activate()

        t = await api(user=user)
        await t.post_ok(
            'api_admin_file_load',
            json={
                'file_meta_id': file_meta.file_meta_id,
                'download': True,
            }
        )
        t.status_is(410, diag=True)
        t.json_is('code', 'ER_S3_FILE_GONE')


async def test_s3_download_client_error(
        tap, dataset, api, s3_stubber, uuid,
):
    with tap.plan(3, 'загрузка данных из s3 [InternalError]'):
        user = await dataset.user()
        file_meta = await dataset.file_meta(
            user_id=user.user_id,
            status='uploaded',
            attr={'bucket': uuid(), 'key': uuid()}
        )

        s3_stubber.for_get_object_error(
            file_meta.attr['bucket'],
            file_meta.attr['key'],
            'InternalError'
        )
        s3_stubber.activate()

        t = await api(user=user)
        await t.post_ok(
            'api_admin_file_load',
            json={
                'file_meta_id': file_meta.file_meta_id,
                'download': True,
            }
        )
        t.status_is(502, diag=True)
        t.json_is('code', 'ER_BAD_GATEWAY')
