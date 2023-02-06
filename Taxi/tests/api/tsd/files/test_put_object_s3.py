import base64

from libstall import cfg


async def test_common(tap, api, dataset, uuid, s3_stubber):
    with tap.plan(4, 'тестируем загрузку файла в s3'):
        user = await dataset.user(role='admin')
        data = 'testtesttest'.encode('utf-8')

        external_id = uuid()
        filename = uuid()

        expected_bucket = cfg('s3.buckets.default')
        prefix = cfg('s3.prefixes.files_api')
        expected_key = f'{prefix}/{external_id}/{filename}'

        s3_stubber.for_put_object_ok(
            bucket=expected_bucket, key=expected_key, data=data
        )
        s3_stubber.activate()

        t = await api(user=user)
        await t.post_ok(
            'api_tsd_files_put_object_s3',
            json={
                'external_id': external_id,
                'filename': filename,
                'b64_data': base64.b64encode(data).decode()
            }
        )
        t.status_is(200, diag=True)

        t.json_is('data.bucket', expected_bucket)
        t.json_is('data.key', expected_key)


async def test_not_base64(tap, api, dataset, uuid):
    with tap.plan(3, 'тестируем загрузку файла в s3'):
        user = await dataset.user(role='admin')

        t = await api(user=user)
        await t.post_ok(
            'api_tsd_files_put_object_s3',
            json={
                'external_id': uuid(),
                'filename': uuid(),
                'b64_data': 'SGVsbG8gd29yb'
            }
        )
        t.status_is(400, diag=True)
        t.json_is('code', 'ER_NOT_BASE64')
