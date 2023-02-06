async def test_s3_touch(tap, dataset, api, s3_stubber, uuid):
    with tap.plan(9, 'файл линкуется с s3'):
        external_id = uuid()
        bucket = uuid()
        key = uuid()

        s3_stubber.for_get_object_ok(bucket, key, b'__data__')
        s3_stubber.activate()

        t = await api(role='admin')
        await t.post_ok(
            'api_admin_file_touch',
            json={
                'external_id': external_id,
                'filename': uuid(),
                'storage': 's3',
                's3_bucket': bucket,
                's3_key': key,
            },
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


async def test_s3_touch_no_such_key(tap, api, s3_stubber, uuid):
    with tap.plan(3, 'несуществующий ключ'):
        bucket = uuid()
        key = uuid()

        s3_stubber.for_get_object_error(bucket, key, 'NoSuchKey')
        s3_stubber.activate()

        t = await api(role='admin')
        await t.post_ok(
            'api_admin_file_touch',
            json={
                'external_id': uuid(),
                'filename': uuid(),
                'storage': 's3',
                's3_bucket': bucket,
                's3_key': key,
            },
        )

        t.status_is(400, diag=True)
        t.json_is('code', 'ER_FILE_NOT_EXISTS')


async def test_s3_touch_no_such_bucket(tap, api, s3_stubber, uuid):
    with tap.plan(3, 'несуществующий бакет'):
        bucket = uuid()
        key = uuid()

        s3_stubber.for_get_object_error(bucket, key, 'NoSuchBucket')
        s3_stubber.activate()

        t = await api(role='admin')
        await t.post_ok(
            'api_admin_file_touch',
            json={
                'external_id': uuid(),
                'filename': uuid(),
                'storage': 's3',
                's3_bucket': bucket,
                's3_key': key,
            },
        )

        t.status_is(400, diag=True)
        t.json_is('code', 'ER_NO_SUCH_S3_BUCKET')


async def test_s3_touch_error(tap, api, s3_stubber, uuid):
    with tap.plan(3, 'S3 лежит'):
        bucket = uuid()
        key = uuid()

        s3_stubber.for_get_object_error(bucket, key, 'InternalError')
        s3_stubber.activate()

        t = await api(role='admin')
        await t.post_ok(
            'api_admin_file_touch',
            json={
                'external_id': uuid(),
                'filename': uuid(),
                'storage': 's3',
                's3_bucket': bucket,
                's3_key': key,
            },
        )

        t.status_is(502, diag=True)
        t.json_is('code', 'ER_BAD_GATEWAY')
