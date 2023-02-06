import pytest


async def test_bad_request_invalid_phone_id(taxi_user_api):
    response = await taxi_user_api.post(
        '/users/search', json={'phone_ids': ['xxx']},
    )
    assert response.status_code == 400
    assert response.json() == {
        'code': 'INVALID_INPUT',
        'message': 'Invalid phone_ids',
    }


async def test_bad_request_no_filter(taxi_user_api):
    response = await taxi_user_api.post('/users/search', json={})
    assert response.status_code == 400
    assert response.json() == {
        'code': 'MISSING_FILTER',
        'message': 'No filter given',
    }


@pytest.mark.parametrize(
    'query,expected_result',
    [
        ({'phone_ids': ['000000000000000000000000']}, {'items': []}),
        (
            {'phone_ids': ['5ab0319b611972dbc1a3d71b']},
            {
                'items': [
                    {
                        'application': 'android',
                        'authorized': True,
                        'created': '2019-08-23T13:00:00+0000',
                        'device_id': 'E9168F93-D098-43AF-8D4C-43E50702EB36',
                        'id': '8fa869dd9e684cbe945f7a73df621e25',
                        'phone_id': '5ab0319b611972dbc1a3d71b',
                        'uber_id': '00148347-c7b9-4058-88a8-4b44f7a2477c',
                        'updated': '2019-08-23T13:00:00+0000',
                        'yandex_uid': '4010989734',
                        'token_only': True,
                    },
                ],
            },
        ),
    ],
)
@pytest.mark.now('2019-08-23T14:00:00Z')
async def test_phone_id(taxi_user_api, query, expected_result):
    response = await taxi_user_api.post('/users/search', json=query)
    assert response.status_code == 200
    data = response.json()
    assert data == expected_result


@pytest.mark.config(USER_API_USERS_PAGE_MAXSIZE=3)
@pytest.mark.parametrize(
    'query,expected_ids,expected_cursor',
    [
        (
            {'phone_ids': ['000000000000000000000001']},
            ['multi5', 'multi4', 'multi3'],
            'multi3',
        ),
        (
            {'phone_ids': ['000000000000000000000001'], 'cursor': 'multi3'},
            ['multi2', 'multi1'],
            None,
        ),
        (
            {'phone_ids': ['000000000000000000000001'], 'cursor': 'multi5'},
            ['multi4', 'multi3', 'multi2'],
            'multi2',
        ),
        (
            {'phone_ids': ['000000000000000000000001'], 'cursor': 'multi4'},
            ['multi3', 'multi2', 'multi1'],
            'multi1',
        ),
        (
            {'phone_ids': ['000000000000000000000001'], 'cursor': 'multi1'},
            [],
            None,
        ),
    ],
)
@pytest.mark.now('2019-08-23T14:00:00Z')
async def test_multipage(taxi_user_api, query, expected_ids, expected_cursor):
    response = await taxi_user_api.post('/users/search', json=query)
    assert response.status_code == 200
    data = response.json()

    ids = [doc['id'] for doc in data['items']]
    assert data.get('cursor') == expected_cursor
    assert ids == expected_ids


@pytest.mark.parametrize(
    'query,expected_ids',
    [
        # No result
        ({'phone_ids': ['000000000000000000000000']}, []),
        ({'id': 'no_id'}, []),
        ({'ids': ['no_id']}, []),
        ({'yandex_uid_types': ['no_yandex_uid_type']}, []),
        ({'yandex_uid': 'no_yandex_uid'}, []),
        ({'yandex_uids': ['no_yandex_uid']}, []),
        ({'yandex_uuid': 'no_yandex_uuid'}, []),
        ({'sourceid': 'no_sourceid'}, []),
        ({'applications': ['no_application']}, []),
        # Single filter query
        ({'phone_ids': ['111111111111111111111111']}, ['test_filters']),
        ({'id': 'test_filters'}, ['test_filters']),
        ({'ids': ['test_filters']}, ['test_filters']),
        ({'yandex_uid_types': ['test_yandex_uid_type']}, ['test_filters']),
        ({'yandex_uid': 'yandex_uid'}, ['test_filters']),
        ({'yandex_uids': ['yandex_uid']}, ['test_filters']),
        ({'yandex_uuid': 'yandex_uuid'}, ['test_filters']),
        ({'uber_id': 'uber_id'}, ['test_filters']),
        ({'sourceid': 'test_sourceid'}, ['test_filters']),
        ({'authorized': False}, ['test_filters']),
        ({'applications': ['test_application']}, ['test_filters']),
        # Single filter list query
        (
            {
                'phone_ids': [
                    '111111111111111111111111',
                    '222222222222222222222222',
                ],
            },
            ['test_filters2', 'test_filters'],
        ),
        (
            {'ids': ['test_filters', 'test_filters2']},
            ['test_filters', 'test_filters2'],
        ),
        (
            {'id': 'test_filters', 'ids': ['test_filters2']},
            ['test_filters', 'test_filters2'],
        ),
        (
            {
                'yandex_uid_types': [
                    'test_yandex_uid_type',
                    'test_yandex_uid_type2',
                ],
            },
            ['test_filters', 'test_filters2'],
        ),
        (
            {'yandex_uids': ['yandex_uid', 'yandex_uid2']},
            ['test_filters', 'test_filters2'],
        ),
        (
            {'yandex_uid': 'yandex_uid', 'yandex_uids': ['yandex_uid2']},
            ['test_filters', 'test_filters2'],
        ),
        (
            {'applications': ['test_application', 'test_application2']},
            ['test_filters', 'test_filters2'],
        ),
        # all-in-one
        (
            {
                'phone_ids': ['111111111111111111111111'],
                'id': 'test_filters',
                'ids': ['test_filters'],
                'yandex_uid_types': ['test_yandex_uid_type'],
                'yandex_uid': 'yandex_uid',
                'yandex_uids': ['yandex_uid'],
                'yandex_uuid': 'yandex_uuid',
                'uber_id': 'uber_id',
                'sourceid': 'test_sourceid',
                'authorized': False,
                'applications': ['test_application'],
            },
            ['test_filters'],
        ),
    ],
)
@pytest.mark.now('2019-08-23T14:00:00Z')
async def test_filters(taxi_user_api, query, expected_ids):
    response = await taxi_user_api.post('/users/search', json=query)
    assert response.status_code == 200
    data = response.json()

    ids = [doc['id'] for doc in data['items']]
    assert sorted(ids) == sorted(expected_ids)


@pytest.mark.parametrize(
    'query,expected_result',
    [
        (
            {'phone_ids': ['5ab0319b611972dbc1a3d71b'], 'fields': []},
            {'items': [{'id': '8fa869dd9e684cbe945f7a73df621e25'}]},
        ),
        (
            {
                'phone_ids': ['5ab0319b611972dbc1a3d71b'],
                'fields': ['application'],
            },
            {
                'items': [
                    {
                        'id': '8fa869dd9e684cbe945f7a73df621e25',
                        'application': 'android',
                    },
                ],
            },
        ),
    ],
)
@pytest.mark.now('2019-08-23T14:00:00Z')
async def test_fileds_filter(taxi_user_api, query, expected_result):
    response = await taxi_user_api.post('/users/search', json=query)
    assert response.status_code == 200
    data = response.json()
    assert data == expected_result
