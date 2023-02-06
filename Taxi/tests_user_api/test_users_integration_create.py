import bson
import pytest


@pytest.mark.parametrize(
    'query,expected_response',
    [
        (
            {
                'phone_id': '5ab0319b611972dbc1a3d71b',
                'sourceid': 'source-id-simple',
                'application': 'application-simple',
            },
            {
                'id': 'user-id-simple',
                'phone_id': '5ab0319b611972dbc1a3d71b',
                'authorized': True,
                'sourceid': 'source-id-simple',
                'application': 'application-simple',
            },
        ),
        (
            {
                'phone_id': '5ab0319b611972dbc1a3d71b',
                'sourceid': 'source-id-simple-uid',
                'application': 'application-simple-uid',
                'yandex_uid': '4010989734',
            },
            {
                'id': 'user-id-simple-uid',
                'phone_id': '5ab0319b611972dbc1a3d71b',
                'authorized': True,
                'sourceid': 'source-id-simple-uid',
                'application': 'application-simple-uid',
                'yandex_uid': '4010989734',
            },
        ),
        (
            {
                'phone_id': '5ab0319b611972dbc1a3d71b',
                'sourceid': 'source-id-full',
                'application': 'application-full',
                'yandex_uid': '4010989734',
            },
            {
                'id': 'user-id-full',
                'phone_id': '5ab0319b611972dbc1a3d71b',
                'authorized': True,
                'sourceid': 'source-id-full',
                'application': 'application-full',
                'yandex_uid': '4010989734',
                'given_name': 'given-name',
                'coupon_code': 'coupon-code',
                'dont_ask_name': True,
            },
        ),
        (
            {
                'phone_id': '5ab0319b611972dbc1a3d71b',
                'sourceid': 'source-id-full',
                'application': 'application-full',
                'given_name': 'new-given-name',
                'coupon_code': 'new-coupon-code',
                'dont_ask_name': False,
            },
            {
                'id': 'user-id-full',
                'phone_id': '5ab0319b611972dbc1a3d71b',
                'authorized': True,
                'sourceid': 'source-id-full',
                'application': 'application-full',
                'yandex_uid': '4010989734',
                'given_name': 'new-given-name',
                'coupon_code': 'new-coupon-code',
                'dont_ask_name': False,
            },
        ),
        (
            {
                'phone_id': '5ab0319b611972dbc1a3d71b',
                'sourceid': 'source-id-simple-uid',
                'application': 'application-simple-uid',
                'yandex_uid': '4010989734',
                'given_name': 'new-given-name',
                'coupon_code': 'new-coupon-code',
                'dont_ask_name': True,
            },
            {
                'id': 'user-id-simple-uid',
                'phone_id': '5ab0319b611972dbc1a3d71b',
                'authorized': True,
                'sourceid': 'source-id-simple-uid',
                'application': 'application-simple-uid',
                'yandex_uid': '4010989734',
                'given_name': 'new-given-name',
                'coupon_code': 'new-coupon-code',
                'dont_ask_name': True,
            },
        ),
    ],
)
@pytest.mark.parametrize('sort_enabled', [True, False])
@pytest.mark.now('2019-02-01T14:00:00Z')
async def test_user_get_simple(
        taxi_user_api,
        mongodb,
        taxi_config,
        sort_enabled,
        query,
        expected_response,
):
    taxi_config.set_values({'USER_API_USERS_CREATION_SORT': sort_enabled})
    await _user_get_test(taxi_user_api, mongodb, query, expected_response)


@pytest.mark.parametrize(
    'query,expected_response',
    [
        (
            {
                'phone_id': '5ab0319b611972dbc1a3d71b',
                'sourceid': 'source-id-duplicate',
                'application': 'application-duplicate',
            },
            {
                'id': 'user-id-duplicate-2',
                'phone_id': '5ab0319b611972dbc1a3d71b',
                'authorized': True,
                'sourceid': 'source-id-duplicate',
                'application': 'application-duplicate',
            },
        ),
    ],
)
@pytest.mark.config(USER_API_USERS_CREATION_SORT=True)
@pytest.mark.now('2019-02-01T14:00:00Z')
async def test_user_get_multi(
        taxi_user_api, mongodb, query, expected_response,
):
    await _user_get_test(taxi_user_api, mongodb, query, expected_response)


async def _user_get_test(taxi_user_api, mongodb, query, expected_response):
    users_count_before = mongodb.users.count()

    response = await taxi_user_api.post('users/integration/create', json=query)
    assert response.status_code == 200

    assert mongodb.users.count() == users_count_before

    response_json = response.json()
    response_json = _pop_datetime_fields(response_json)
    assert response_json == expected_response

    response_id = response_json.pop('id')
    response_phone_id = response_json.pop('phone_id')

    expected_mongo_doc = response_json
    expected_mongo_doc['_id'] = response_id
    expected_mongo_doc['phone_id'] = bson.ObjectId(response_phone_id)

    user_doc = mongodb.users.find_one({'_id': response_id})
    user_doc = _pop_datetime_fields(user_doc)
    assert user_doc == expected_mongo_doc


@pytest.mark.config(
    CREATE_INTEGRATION_USERS_WITHOUT_SOURCE_ID_APPS=['no-sourceid-app'],
)
@pytest.mark.parametrize(
    'query,expected_response',
    [
        (
            {
                'phone_id': '5ab0319b611972dbc1a3d710',
                'sourceid': 'source-id-simple',
                'application': 'application-simple',
            },
            {
                'phone_id': '5ab0319b611972dbc1a3d710',
                'authorized': True,
                'sourceid': 'source-id-simple',
                'application': 'application-simple',
            },
        ),
        (
            {
                'phone_id': '5ab0319b611972dbc1a3d71b',
                'sourceid': 'source-id-not-authorized',
                'application': 'application-not-authorized',
            },
            {
                'phone_id': '5ab0319b611972dbc1a3d71b',
                'authorized': True,
                'sourceid': 'source-id-not-authorized',
                'application': 'application-not-authorized',
            },
        ),
        (
            {
                'phone_id': '5ab0319b611972dbc1a3d71b',
                'sourceid': 'source-id-not-authorized',
                'application': 'application-not-authorized',
                'given_name': 'new-given-name',
                'coupon_code': 'new-coupon-code',
                'dont_ask_name': False,
            },
            {
                'phone_id': '5ab0319b611972dbc1a3d71b',
                'authorized': True,
                'sourceid': 'source-id-not-authorized',
                'application': 'application-not-authorized',
                'given_name': 'new-given-name',
                'coupon_code': 'new-coupon-code',
                'dont_ask_name': False,
            },
        ),
        (
            {
                'phone_id': '5ab0319b611972dbc1a3d710',
                'application': 'no-sourceid-app',
            },
            {
                'phone_id': '5ab0319b611972dbc1a3d710',
                'authorized': True,
                'application': 'no-sourceid-app',
            },
        ),
    ],
)
@pytest.mark.now('2019-02-01T14:00:00Z')
async def test_user_create(taxi_user_api, mongodb, query, expected_response):
    users_count_before = mongodb.users.count()

    response = await taxi_user_api.post('users/integration/create', json=query)
    assert response.status_code == 200

    assert mongodb.users.count() == users_count_before + 1

    response_json = response.json()
    response_id = response_json.pop('id')
    response_json = _pop_datetime_fields(response_json)
    assert response_json == expected_response

    response_phone_id = response_json.pop('phone_id')

    expected_mongo_doc = response_json
    expected_mongo_doc['_id'] = response_id
    expected_mongo_doc['phone_id'] = bson.ObjectId(response_phone_id)

    user_doc = mongodb.users.find_one({'_id': response_id})
    user_doc = _pop_datetime_fields(user_doc)
    assert user_doc == expected_mongo_doc


@pytest.mark.parametrize(
    'body,message',
    [
        (
            {'sourceid': 'sourceid', 'application': 'application'},
            'Field \'phone_id\' is missing',
        ),
        (
            {'phone_id': '5ab0319b611972dbc1a3d71b', 'sourceid': 'sourceid'},
            'Field \'application\' is missing',
        ),
        (
            {
                'phone_id': 'phone_id',
                'sourceid': 'sourceid',
                'application': 'application',
            },
            'Invalid oid phone_id',
        ),
    ],
)
async def test_bad_request(taxi_user_api, body, message):
    response = await taxi_user_api.post('users/integration/create', json=body)
    assert response.status_code == 400
    assert response.json()['code'] == '400'


@pytest.mark.parametrize(
    'body,code,description',
    [
        (
            {
                'phone_id': '4ab0319b611972dbc1a3d71b',
                'application': 'applicationn',
            },
            'EMPTY_SOURCEID_NOT_ALLOWED',
            'Field \'sourceid\' is missing (and no '
            'CREATE_INTEGRATION_USERS_WITHOUT_SOURCE_ID_APPS configured)',
        ),
    ],
)
async def test_custom_bad_request(taxi_user_api, body, code, description):
    response = await taxi_user_api.post('users/integration/create', json=body)
    assert response.status_code == 400
    assert response.json()['code'] == code


def _pop_datetime_fields(doc):
    doc.pop('updated')
    doc.pop('created')
    return doc
