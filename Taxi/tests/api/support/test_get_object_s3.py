async def test_get_object_s3(tap, api, dataset, s3_stubber):
    with tap.plan(3, 'тестируем получение файла из s3'):
        user = await dataset.user(role='admin')
        bucket = 'test-bucket'
        key = 'test/file.pdf'
        data = 'testtesttest'

        s3_stubber.for_get_object_ok(
            bucket=bucket, key=key, data=data.encode('utf-8')
        )
        s3_stubber.activate()

        t = await api(user=user)
        await t.get_ok(
            'api_support_get_object_s3',
            form={'bucket': bucket, 'key': key}
        )

        tap.eq_ok(t.res['status'], 200, 'response OK')
        tap.eq_ok(t.res['body'], data, 'file content OK')


async def test_get_object_s3_not_found(tap, api, dataset, s3_stubber):
    with tap.plan(2, 'тестируем запрос к s3 когда нет файла'):
        user = await dataset.user(role='admin')
        bucket = 'test-bucket'
        key = 'test/file.pdf'

        s3_stubber.for_get_object_error(
            bucket=bucket, key=key, error='NoSuchKey'
        )
        s3_stubber.activate()

        t = await api(user=user)
        await t.get_ok(
            'api_support_get_object_s3',
            form={'bucket': bucket, 'key': key}
        )

        tap.eq_ok(t.res['status'], 424, 'Failed dependency')
