import bson
import pytest


@pytest.mark.parametrize(
    'query',
    [
        {
            'authorized': False,
            'phone_id': '111111111111111111111111',
            'sourceid': 'source-id-simple',
            'application': 'application-simple',
            'user_id': 'user-id-simple',
        },
        {
            'authorized': False,
            'phone_id': '111111111111111111111111',
            'application': 'application-no-source',
            'user_id': 'user-id-no-source',
        },
    ],
)
@pytest.mark.config(
    CREATE_INTEGRATION_USERS_WITHOUT_SOURCE_ID_APPS=['application-no-source'],
)
@pytest.mark.now('2019-02-01T14:00:00Z')
async def test_update_simple(taxi_user_api, mongodb, query):
    user_doc_before = mongodb.users.find_one({'_id': query['user_id']})

    response = await taxi_user_api.post('users/integration/update', json=query)
    assert response.status_code == 200
    user_doc_after = mongodb.users.find_one({'_id': query['user_id']})

    assert user_doc_before['phone_id'] == bson.ObjectId(
        '5ab0319b611972dbc1a3d71b',
    )
    assert user_doc_before['authorized']

    assert user_doc_after['phone_id'] == bson.ObjectId(
        '111111111111111111111111',
    )
    assert user_doc_after.get('authorized') is None


@pytest.mark.parametrize(
    'body,code,description',
    [
        (
            {
                'phone_id': '4ab0319b611972dbc1a3d71b',
                'application': 'application',
                'user_id': 'user-id-simple',
            },
            'EMPTY_SOURCEID_NOT_ALLOWED',
            'Field \'sourceid\' is missing (and no '
            'CREATE_INTEGRATION_USERS_WITHOUT_SOURCE_ID_APPS configured)',
        ),
        (
            {
                'phone_id': 'phone_id',
                'sourceid': 'sourceid',
                'application': 'application',
                'user_id': 'user-id-simple',
            },
            '400',
            'Invalid oid phone_id',
        ),
    ],
)
@pytest.mark.config(
    CREATE_INTEGRATION_USERS_WITHOUT_SOURCE_ID_APPS=['application-no-source'],
)
async def test_bad_request(taxi_user_api, body, code, description):
    response = await taxi_user_api.post('users/integration/update', json=body)
    assert response.status_code == 400
    assert response.json()['code'] == code
