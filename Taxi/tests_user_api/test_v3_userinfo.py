import pytest


@pytest.mark.parametrize(
    'request_json',
    [
        {'id': 'no_user_object'},
        {'yandex_uid': 'no_user_object'},
        {'yandex_uid': '4008968952', 'application': 'no_user_object'},
        {'id': 'deleted-user-phone'},
    ],
)
async def test_v3_userinfo_not_found(taxi_user_api, request_json):
    response = await taxi_user_api.post('v3/userinfo', json=request_json)
    assert response.status_code == 404


@pytest.mark.parametrize(
    'request_json',
    [
        {'application': 'app'},
        {'id': 'user_id', 'yandex_uid': 'user_uid', 'application': 'app'},
        {'id': 'user_id', 'yandex_uid': 'user_uid'},
    ],
)
async def test_v3_userinfo_invalid_input(taxi_user_api, request_json):
    response = await taxi_user_api.post('v3/userinfo', json=request_json)
    assert response.status_code == 400


@pytest.mark.parametrize(
    'request_json, expected_response',
    [
        (
            {'id': '00027fea212645278c7c87c0ef417201'},
            {
                'id': '00027fea212645278c7c87c0ef417201',
                'authorized': True,
                'token_only': True,
                'yandex_uid': '4008968952',
                'yandex_uuid': '235f5f07f39be4d68a9b01ec1a8d5184',
                'name': 'Мишаня',
                'application': 'test_application',
                'application_version': '1.2.3',
                'last_order_nearest_zone': 'moscow',
                'device_id': 'test_device_id',
                'has_ya_plus': True,
                'has_cashback_plus': True,
                'phone': {
                    'id': '5825ba64c0d947f1eef0b501',
                    'personal_id': '5d4001bb51a948a6a9b7fc81a384b7e1',
                    'phone_hash': {
                        'hash': (
                            '72639c1cc1b3d068e007b1da06cdb5160c'
                            '34b6662abd0f00df282769fbf132bf'
                        ),
                        'salt': '7emBWW687ywm1xR+wTlFYJMNtlwL0xQKPzAf+jN101s=',
                    },
                    'loyal': True,
                },
            },
        ),
        (
            {'id': '00027fea212645278c7c87c0ef417202'},
            {
                'id': '00027fea212645278c7c87c0ef417202',
                'authorized': False,
                'token_only': False,
            },
        ),
        (
            {'yandex_uid': '4008968952', 'application': 'test_application'},
            {
                'id': '00027fea212645278c7c87c0ef417201',
                'authorized': True,
                'token_only': True,
                'yandex_uid': '4008968952',
                'yandex_uuid': '235f5f07f39be4d68a9b01ec1a8d5184',
                'name': 'Мишаня',
                'application': 'test_application',
                'application_version': '1.2.3',
                'last_order_nearest_zone': 'moscow',
                'device_id': 'test_device_id',
                'has_ya_plus': True,
                'has_cashback_plus': True,
                'phone': {
                    'id': '5825ba64c0d947f1eef0b501',
                    'personal_id': '5d4001bb51a948a6a9b7fc81a384b7e1',
                    'phone_hash': {
                        'hash': (
                            '72639c1cc1b3d068e007b1da06cdb5160c'
                            '34b6662abd0f00df282769fbf132bf'
                        ),
                        'salt': '7emBWW687ywm1xR+wTlFYJMNtlwL0xQKPzAf+jN101s=',
                    },
                    'loyal': True,
                },
            },
        ),
    ],
)
async def test_userinfo(taxi_user_api, request_json, expected_response):
    response = await taxi_user_api.post('v3/userinfo', json=request_json)
    assert response.status_code == 200
    assert response.json() == expected_response


@pytest.mark.parametrize(
    'user_id, expected_response',
    [
        # No personal_phone_id, no salt
        (
            'no-personal',
            {
                'id': 'no-personal',
                'authorized': False,
                'token_only': False,
                'phone': {
                    'id': 'dead005e4ca9a10000000000',
                    'personal_id': 'mocked-personal-id',
                },
            },
        ),
        # No phone hash no salt
        (
            '00027fea212645278c7c87c0ef417203',
            {
                'id': '00027fea212645278c7c87c0ef417203',
                'authorized': False,
                'token_only': False,
                'phone': {
                    'id': '5825ba64c0d947f1eef0b503',
                    'personal_id': '5d4001bb51a948a6a9b7fc81a384b7e3',
                },
            },
        ),
        # No hash
        (
            '00027fea212645278c7c87c0ef417204',
            {
                'id': '00027fea212645278c7c87c0ef417204',
                'authorized': False,
                'token_only': False,
                'phone': {
                    'id': '5825ba64c0d947f1eef0b504',
                    'personal_id': '5d4001bb51a948a6a9b7fc81a384b7e4',
                },
            },
        ),
        # No salt
        (
            '00027fea212645278c7c87c0ef417205',
            {
                'id': '00027fea212645278c7c87c0ef417205',
                'authorized': False,
                'token_only': False,
                'phone': {
                    'id': '5825ba64c0d947f1eef0b505',
                    'personal_id': '5d4001bb51a948a6a9b7fc81a384b7e5',
                },
            },
        ),
        # No hash no salt
        (
            '00027fea212645278c7c87c0ef417206',
            {
                'id': '00027fea212645278c7c87c0ef417206',
                'authorized': False,
                'token_only': False,
                'phone': {
                    'id': '5825ba64c0d947f1eef0b506',
                    'personal_id': '5d4001bb51a948a6a9b7fc81a384b7e6',
                    'loyal': False,
                },
            },
        ),
    ],
)
async def test_fallback(taxi_user_api, user_id, expected_response, mockserver):
    @mockserver.json_handler('/personal/v1/phones/store')
    def _phone_store_handler(request):
        return {'id': 'mocked-personal-id', 'value': request.json['value']}

    response = await taxi_user_api.post('v3/userinfo', json={'id': user_id})
    assert response.status_code == 200
    data = response.json()
    if 'phone' in data:
        assert 'phone_hash' in data['phone']
        assert 'hash' in data['phone']['phone_hash']
        assert 'salt' in data['phone']['phone_hash']
        del data['phone']['phone_hash']
    assert data == expected_response


@pytest.mark.filldb(users='nofallback', user_phones='nofallback_personal')
async def test_nofallback_personal(taxi_user_api):
    response = await taxi_user_api.post(
        'v3/userinfo', json={'id': 'no-fallback-possible'},
    )
    assert response.status_code == 500


@pytest.mark.filldb(users='nofallback', user_phones='nofallback_hash')
async def test_nofallback_hash(taxi_user_api):
    response = await taxi_user_api.post(
        'v3/userinfo', json={'id': 'no-fallback-possible'},
    )
    assert response.status_code == 500
