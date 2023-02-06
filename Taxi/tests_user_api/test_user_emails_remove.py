import bson
import pytest


ENDPOINT = 'user_emails/remove'


@pytest.mark.parametrize(
    'request_body',
    [
        {
            'confirmation_code': (
                '760639ec4017fd8ed54bbdd57337e9ac1e2962cc6e94f62819f00001'
            ),
            'phone_id': '666777e7ed2c89a5e0300001',
        },
        {'phone_id': '666777e7ed2c89a5e0300001', 'yandex_uid': '4004000001'},
        {
            'confirmation_code': (
                '760639ec4017fd8ed54bbdd57337e9ac1e2962cc6e94f62819f00001'
            ),
            'yandex_uid': '4004000001',
        },
        {
            'confirmation_code': (
                '760639ec4017fd8ed54bbdd57337e9ac1e2962cc6e94f62819f00001'
            ),
            'phone_id': '666777e7ed2c89a5e0300001',
            'yandex_uid': '4004000001',
        },
        {'phone_id': 'invalid_oid'},
        {'yandex_uids': 'yandex_uid'},
    ],
)
async def test_user_emails_remove_bad_request(taxi_user_api, request_body):
    response = await taxi_user_api.post(ENDPOINT, json=request_body)
    assert response.status_code == 400


@pytest.mark.parametrize(
    'request_body',
    [
        {
            'confirmation_code': (
                '760639ec4017fd8ed54bbdd57337e9ac1e2962cc6e94f62819f10500'
            ),
        },
        {'phone_id': '666777e7ed2c89a5e0310500'},
        {'yandex_uid': '4004100500'},
        {'yandex_uids': ['4004100500']},
        {'yandex_uids': ['4004000002'], 'brand_name': 'yauber'},
        {'phone_id': '666777e7ed2c89a5e0300002', 'brand_name': 'yauber'},
    ],
)
async def test_user_emails_remove_not_found(taxi_user_api, request_body):
    response = await taxi_user_api.post(ENDPOINT, json=request_body)
    assert response.status_code == 404


@pytest.mark.parametrize(
    'request_data',
    [
        {
            'confirmation_code': (
                '760639ec4017fd8ed54bbdd57337e9ac1e2962cc6e94f62819f00001'
            ),
        },
        {'phone_id': '666777e7ed2c89a5e0300001'},
        {'yandex_uid': '4004000001'},
        {'phone_id': '666777e7ed2c89a5e0300002', 'brand_name': 'yataxi'},
        {'phone_id': '666777e7ed2c89a5e0300003', 'brand_name': 'yataxi'},
    ],
)
async def test_user_emails_remove(taxi_user_api, mongodb, request_data):
    mongo_query = {
        key: val if key != 'phone_id' else bson.ObjectId(val)
        for key, val in request_data.items()
    }
    mongo_query.pop('brand_name', None)
    response = await taxi_user_api.post(ENDPOINT, json=request_data)
    assert response.status_code == 200
    assert mongodb.user_emails.find_one(mongo_query) is None


@pytest.mark.config(APPLICATION_BRAND_RELATED_BRANDS={'yataxi': ['yango']})
@pytest.mark.parametrize(
    'request_data, brands',
    [
        ({'yandex_uids': ['4004000001']}, None),
        ({'yandex_uids': ['4004000001', '4004000002']}, None),
        (
            {
                'yandex_uids': ['4004000001', '4004000002'],
                'brand_name': 'yataxi',
            },
            ['yataxi'],
        ),
        (
            {'yandex_uids': ['4004000100'], 'brand_name': 'yataxi'},
            ['yataxi', 'yango'],
        ),
    ],
)
async def test_user_emails_remove_many(
        taxi_user_api, mongodb, request_data, brands,
):
    mongo_query = {'yandex_uid': {'$in': request_data['yandex_uids']}}
    if request_data.get('brand_name'):
        mongo_query['brand_name'] = {'$in': brands}
    response = await taxi_user_api.post(ENDPOINT, json=request_data)
    assert response.status_code == 200
    assert list(mongodb.user_emails.find(mongo_query)) == []
