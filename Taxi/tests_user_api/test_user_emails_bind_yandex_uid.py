import bson


ENDPOINT = 'user_emails/bind_yandex_uid'


async def test_user_emails_bind_yandex_uid_bad_request(taxi_user_api):
    request = {'phone_id': 'invalid_oid', 'yandex_uid': '4004000001'}
    response = await taxi_user_api.post(ENDPOINT, json=request)
    assert response.status_code == 400


async def test_user_emails_bind_yandex_uid(taxi_user_api, mongodb):
    for _ in range(2):
        request = {
            'phone_id': '666777e7ed2c89a5e0300001',
            'yandex_uid': '4004000001',
        }
        response = await taxi_user_api.post(ENDPOINT, json=request)
        assert response.status_code == 200
        assert (
            mongodb.user_emails.find_one(
                {'phone_id': bson.ObjectId('666777e7ed2c89a5e0300001')},
            )['yandex_uid']
            == '4004000001'
        )


async def test_user_emails_bind_yandex_uid_not_found(taxi_user_api, mongodb):
    request = {
        'phone_id': '666777e7ed2c89a5e0300002',
        'yandex_uid': '4004000002',
    }
    response = await taxi_user_api.post(ENDPOINT, json=request)
    assert response.status_code == 200
    assert (
        mongodb.user_emails.find_one(
            {'phone_id': bson.ObjectId('666777e7ed2c89a5e0300002')},
        )
        is None
    )


async def test_user_emails_bind_yandex_uid_conflict(taxi_user_api, mongodb):
    request = {
        'phone_id': '666777e7ed2c89a5e0300003',
        'yandex_uid': '4004000003',
    }
    response = await taxi_user_api.post(ENDPOINT, json=request)
    assert response.status_code == 200
    assert (
        mongodb.user_emails.find_one(
            {'phone_id': bson.ObjectId('666777e7ed2c89a5e0300003')},
        )['yandex_uid']
        == '4004000033'
    )


async def test_user_emails_bind_yandex_uid_many(taxi_user_api, mongodb):
    request = {
        'phone_id': '666777e7ed2c89a5e0300004',
        'yandex_uid': '4004000004',
    }
    response = await taxi_user_api.post(ENDPOINT, json=request)
    assert response.status_code == 200
    for doc in mongodb.user_emails.find(
            {'phone_id': bson.ObjectId('666777e7ed2c89a5e0300004')},
    ):
        assert doc['yandex_uid'] == '4004000004'
