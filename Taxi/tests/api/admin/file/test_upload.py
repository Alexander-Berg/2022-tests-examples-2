import pytest


async def test_s3_upload(tap, dataset, api, s3_stubber, uuid):
    with tap.plan(9, 'загрузка файла в s3'):
        external_id = uuid()
        bucket = 'wms-files'
        key = f'user_files/{external_id}'

        s3_stubber.for_get_object_error(
            bucket=bucket, key=key, error='NoSuchKey'
        )
        s3_stubber.for_put_object_ok(
            bucket=bucket, key=key, data=b'__data__'
        )
        s3_stubber.activate()

        t = await api(role='admin')
        await t.post_ok(
            'api_admin_file_upload',
            json={
                'external_id': external_id,
                'filename': uuid(),
                'storage': 's3',
                'b64_data': 'X19kYXRhX18='  # "__data__"
            }
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('file_meta.external_id', external_id)

        file_meta = await dataset.FileMeta.load(by='external', key=external_id)
        tap.ok(file_meta, 'file_meta created')
        tap.eq(file_meta.status, 'uploaded', 'status ok')
        tap.eq(file_meta.storage, 's3', 'storage ok')
        tap.eq(file_meta.attr['bucket'], bucket, 'bucket ok')
        tap.eq(file_meta.attr['key'], key, 'key ok')


@pytest.mark.parametrize('s3_error', ['NoSuchBucket', 'InternalError'])
async def test_s3_upload_seek_error(
        tap, api, s3_stubber, uuid, s3_error
):
    with tap.plan(3, f'загрузка файла в s3 [seek:{s3_error}]'):
        external_id = uuid()
        bucket = 'wms-files'
        key = f'user_files/{external_id}'

        s3_stubber.for_get_object_error(
            bucket=bucket, key=key, error=s3_error
        )
        s3_stubber.activate()

        t = await api(role='admin')
        await t.post_ok(
            'api_admin_file_upload',
            json={
                'external_id': external_id,
                'filename': uuid(),
                'storage': 's3',
                'b64_data': 'X19kYXRhX18='  # "__data__"
            }
        )

        t.status_is(502, diag=True)
        t.json_is('code', 'ER_BAD_GATEWAY')


async def test_s3_upload_put_error(tap, api, s3_stubber, uuid):
    with tap.plan(3, 'загрузка файла в s3 [put:InternalError]'):
        external_id = uuid()
        bucket = 'wms-files'
        key = f'user_files/{external_id}'

        s3_stubber.for_get_object_error(
            bucket=bucket, key=key, error='NoSuchKey'
        )
        s3_stubber.for_put_object_error(
            bucket=bucket, key=key, data=b'__data__', error='InternalError'
        )
        s3_stubber.activate()

        t = await api(role='admin')
        await t.post_ok(
            'api_admin_file_upload',
            json={
                'external_id': external_id,
                'filename': uuid(),
                'storage': 's3',
                'b64_data': 'X19kYXRhX18='  # "__data__"
            }
        )

        t.status_is(502, diag=True)
        t.json_is('code', 'ER_BAD_GATEWAY')


async def test_s3_upload_exists(tap, dataset, api, s3_stubber, uuid):
    with tap:
        external_id = uuid()
        bucket = 'wms-files'
        key = f'user_files/{external_id}'

        s3_stubber.for_get_object_ok(
            bucket=bucket, key=key, data=b'__any_data__'
        )
        # put_object не будет вызван, так как файл уже существует
        s3_stubber.add_client_error('put_object', 'InternalError')
        s3_stubber.activate()

        t = await api(role='admin')
        await t.post_ok(
            'api_admin_file_upload',
            json={
                'external_id': external_id,
                'filename': uuid(),
                'storage': 's3',
                'b64_data': 'X19kYXRhX18='  # "__data__"
            }
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('file_meta.external_id', external_id)

        file_meta = await dataset.FileMeta.load(by='external', key=external_id)
        tap.ok(file_meta, 'file_meta created')
        tap.eq(file_meta.status, 'uploaded', 'status ok')
        tap.eq(file_meta.storage, 's3', 'storage ok')
        tap.eq(file_meta.attr['bucket'], bucket, 'bucket ok')
        tap.eq(file_meta.attr['key'], key, 'key ok')
