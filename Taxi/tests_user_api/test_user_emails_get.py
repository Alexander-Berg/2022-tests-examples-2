import pytest


ENDPOINT = 'user_emails/get'


@pytest.mark.parametrize(
    'request_body',
    [{}, {'ids': ['invalid_oid']}, {'phone_ids': ['invalid_oid']}],
)
async def test_user_emails_get_bad_request(taxi_user_api, request_body):
    response = await taxi_user_api.post(ENDPOINT, json=request_body)
    assert response.status_code == 400


@pytest.mark.parametrize(
    'user_email_id, expected_user_email_info',
    [
        (
            '566afbe7ed2c89a5e0300001',
            {
                'id': '566afbe7ed2c89a5e0300001',
                'phone_id': '666777e7ed2c89a5e0300001',
                'yandex_uid': '4004000001',
                'personal_email_id': '123456dcba00001',
                'confirmed': True,
                'confirmation_code': (
                    '760639ec4017fd8ed54bbdd57337e9ac1e2962cc6e94f62819f00001'
                ),
                'brand_name': 'yataxi',
                'updated': '2016-02-07T19:45:00.922+0000',
                'created': '2016-02-07T15:45:00.922+0000',
            },
        ),
        (
            '566afbe7ed2c89a5e0300008',
            {
                'id': '566afbe7ed2c89a5e0300008',
                'personal_email_id': '123456dcba00008',
                'confirmed': False,
                'confirmation_code': (
                    '760639ec4017fd8ed54bbdd57337e9ac1e2962cc6e94f62819f00008'
                ),
                'updated': '2016-02-07T19:11:00.922+0000',
                'created': '2016-02-07T15:11:00.922+0000',
            },
        ),
    ],
)
async def test_user_emails_get_document(
        taxi_user_api, user_email_id, expected_user_email_info,
):
    response = await taxi_user_api.post(
        ENDPOINT, json={'ids': [user_email_id]},
    )
    assert response.status_code == 200
    response_body = response.json()
    user_email_infos = response_body['items']
    assert len(user_email_infos) == 1
    assert user_email_infos[0] == expected_user_email_info


@pytest.mark.parametrize('primary_replica', [True, False])
async def test_user_emails_get_replica(taxi_user_api, primary_replica):
    response = await taxi_user_api.post(
        ENDPOINT,
        json={
            'ids': ['566afbe7ed2c89a5e0300008'],
            'primary_replica': primary_replica,
        },
    )
    assert response.status_code == 200
    assert response.json()['items'] == [
        {
            'id': '566afbe7ed2c89a5e0300008',
            'personal_email_id': '123456dcba00008',
            'confirmed': False,
            'confirmation_code': (
                '760639ec4017fd8ed54bbdd57337e9ac1e2962cc6e94f62819f00008'
            ),
            'updated': '2016-02-07T19:11:00.922+0000',
            'created': '2016-02-07T15:11:00.922+0000',
        },
    ]


@pytest.mark.parametrize(
    'requested_fields, expected_response',
    [
        ([], {'id': '566afbe7ed2c89a5e0300001'}),
        (['qwe'], {'id': '566afbe7ed2c89a5e0300001'}),
        (['id'], {'id': '566afbe7ed2c89a5e0300001'}),
        (
            ['personal_email_id'],
            {
                'id': '566afbe7ed2c89a5e0300001',
                'personal_email_id': '123456dcba00001',
            },
        ),
        (
            [
                'phone_id',
                'yandex_uid',
                'personal_email_id',
                'confirmed',
                'confirmation_code',
                'brand_name',
                'updated',
                'created',
            ],
            {
                'id': '566afbe7ed2c89a5e0300001',
                'phone_id': '666777e7ed2c89a5e0300001',
                'yandex_uid': '4004000001',
                'personal_email_id': '123456dcba00001',
                'confirmed': True,
                'confirmation_code': (
                    '760639ec4017fd8ed54bbdd57337e9ac1e2962cc6e94f62819f00001'
                ),
                'brand_name': 'yataxi',
                'updated': '2016-02-07T19:45:00.922+0000',
                'created': '2016-02-07T15:45:00.922+0000',
            },
        ),
    ],
)
async def test_user_emails_get_fields(
        taxi_user_api, requested_fields, expected_response,
):
    response = await taxi_user_api.post(
        ENDPOINT,
        json={'ids': ['566afbe7ed2c89a5e0300001'], 'fields': requested_fields},
    )
    assert response.status_code == 200
    response_body = response.json()
    user_email_infos = response_body['items']
    assert len(user_email_infos) == 1
    assert user_email_infos[0] == expected_response


@pytest.mark.config(APPLICATION_BRAND_RELATED_BRANDS={'yataxi': ['yango']})
@pytest.mark.parametrize(
    'request_body, expected_user_email_ids',
    [
        ({'ids': ['566afbe7ed2c89a5e0300001']}, ['566afbe7ed2c89a5e0300001']),
        (
            {'ids': ['566afbe7ed2c89a5e0300001', '566afbe7ed2c89a5e0300002']},
            ['566afbe7ed2c89a5e0300001', '566afbe7ed2c89a5e0300002'],
        ),
        (
            {'personal_email_ids': ['123456dcba00003']},
            ['566afbe7ed2c89a5e0300003'],
        ),
        (
            {'phone_ids': ['666777e7ed2c89a5e0300003']},
            ['566afbe7ed2c89a5e0300003'],
        ),
        (
            {
                'phone_ids': [
                    '666777e7ed2c89a5e0300001',
                    '666777e7ed2c89a5e0300002',
                ],
            },
            ['566afbe7ed2c89a5e0300001', '566afbe7ed2c89a5e0300002'],
        ),
        ({'yandex_uids': ['4004000007']}, ['566afbe7ed2c89a5e0300007']),
        (
            {'yandex_uids': ['4004000001', '4004000002']},
            ['566afbe7ed2c89a5e0300001', '566afbe7ed2c89a5e0300002'],
        ),
        (
            {
                'phone_ids': [
                    '666777e7ed2c89a5e0300001',
                    '666777e7ed2c89a5e0300002',
                ],
                'yandex_uids': ['4004000001', '4004000006'],
            },
            ['566afbe7ed2c89a5e0300001'],
        ),
        (
            {
                'phone_ids': ['666777e7ed2c89a5e0300002'],
                'yandex_uids': ['4004000001', '4004000006'],
            },
            [],
        ),
        (
            {
                'phone_ids': ['666777e7ed2c89a5e0300001'],
                'brand_name': 'yataxi',
            },
            ['566afbe7ed2c89a5e0300001'],
        ),
        (
            {
                'phone_ids': ['666777e7ed2c89a5e0300003'],
                'brand_name': 'yataxi',
            },
            ['566afbe7ed2c89a5e0300003'],
        ),
        (
            {
                'phone_ids': ['666777e7ed2c89a5e0300002'],
                'brand_name': 'unknown_brand',
            },
            [],
        ),
        (
            {
                'phone_ids': [
                    '666777e7ed2c89a5e0300001',
                    '666777e7ed2c89a5e0300002',
                ],
                'brand_name': 'specific_brand',
            },
            ['566afbe7ed2c89a5e0300002'],
        ),
        (
            {'yandex_uids': ['4004000100'], 'brand_name': 'yataxi'},
            ['566afbe7ed2c89a5e0300010', '566afbe7ed2c89a5e0300011'],
        ),
    ],
)
async def test_user_emails_get_queries(
        taxi_user_api, request_body, expected_user_email_ids,
):
    response = await taxi_user_api.post(ENDPOINT, json=request_body)
    assert response.status_code == 200
    response_body = response.json()
    user_email_ids = [
        user_email_info['id'] for user_email_info in response_body['items']
    ]
    assert sorted(user_email_ids) == sorted(expected_user_email_ids)
