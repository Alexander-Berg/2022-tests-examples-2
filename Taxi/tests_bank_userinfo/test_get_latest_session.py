async def test_no_session(taxi_bank_userinfo, mockserver):
    response = await taxi_bank_userinfo.post(
        '/userinfo-internal/v1/get_latest_session',
        json={'buid': '024e7db5-9bd6-4f45-a1cd-2a442e15ffff'},
    )
    assert response.status_code == 404


async def test_ok(taxi_bank_userinfo):
    response = await taxi_bank_userinfo.post(
        '/userinfo-internal/v1/get_latest_session',
        json={'buid': '024e7db5-9bd6-4f45-a1cd-2a442e15bdb1'},
    )

    assert response.status_code == 200
    assert response.json() == {
        'session_uuid': '024e7db5-9bd6-4f45-a1cd-2a442e15bdc3',
        'buid': '024e7db5-9bd6-4f45-a1cd-2a442e15bdb1',
        'yandex_uid': '024e7db5-9bd6-4f45-a1cd-2a442e15bde1',
        'phone_id': '024e7db5-9bd6-4f45-a1cd-2a442e15bdf1',
        'status': 'latest_session',
        'antifraud_info': {'device_id': 'device_id', 'dict': {'key': 'value'}},
        'created_at': '2021-10-31T00:03:00.0+00:00',
        'updated_at': '2021-10-31T00:07:00.0+00:00',
        'app_vars': 'X-Platform=fcm, app_name=sdk_example',
        'locale': 'ru',
    }


async def test_ok_few_fields(taxi_bank_userinfo):
    response = await taxi_bank_userinfo.post(
        '/userinfo-internal/v1/get_latest_session',
        json={'buid': '024e7db5-9bd6-4f45-a1cd-2a442e15bdb2'},
    )

    assert response.status_code == 200
    assert response.json() == {
        'session_uuid': '024e7db5-9bd6-4f45-a1cd-2a442e15bdc4',
        'buid': '024e7db5-9bd6-4f45-a1cd-2a442e15bdb2',
        'status': 'session_few_fields',
        'antifraud_info': {},
        'created_at': '2021-10-31T00:01:00.0+00:00',
        'updated_at': '2021-10-31T00:02:00.0+00:00',
        'app_vars': 'X-Platform=fcm, app_name=sdk_example',
        'locale': 'ru',
    }
