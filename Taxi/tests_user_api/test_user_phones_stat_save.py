import bson
import pytest

ENDPOINT = 'user_phones/stat/save'


@pytest.mark.parametrize(
    'body, message',
    [
        ({'set': {'foo': True}}, 'Field \'phone_id\' is missing'),
        (
            {'phone_id': 213, 'set': [{'field': 'foo', 'value': True}]},
            (
                'Field \'phone_id\' is of a wrong type. '
                'Expected: stringValue, actual: intValue'
            ),
        ),
        (
            {'phone_id': '213', 'set': [{'field': 'foo', 'value': True}]},
            'Malformed id',
        ),
        (
            {'phone_id': '123459e1e7e5b1f539abcdef', 'set': 123},
            (
                'Field \'set\' is of a wrong type. Expected: arrayValue, '
                'actual: intValue'
            ),
        ),
        (
            {
                'phone_id': '123459e1e7e5b1f539abcdef',
                'inc': 123,
                'order_id_loyality_processed': 'order_id',
            },
            (
                'Field \'inc\' is of a wrong type. Expected: arrayValue, '
                'actual: intValue'
            ),
        ),
        (
            {'phone_id': '123459e1e7e5b1f539abcdef'},
            'At least inc or set must be set properly',
        ),
        (
            {
                'phone_id': '123459e1e7e5b1f539abcdef',
                'set': [],
                'inc': [],
                'order_id_loyality_processed': 'order_id',
            },
            'At least inc or set must be set properly',
        ),
        (
            {
                'phone_id': '123459e1e7e5b1f539abcdef',
                'inc': [{'field': 'foo', 'value': 1}],
            },
            'Inc should be used only with order_id_loyality_processed',
        ),
        (
            {
                'phone_id': '123459e1e7e5b1f539abcdef',
                'inc': [{'field': 'foo', 'value': 'bar'}],
                'order_id_loyality_processed': 'order_id',
            },
            (
                'Field \'inc[0].value\' is of a wrong type. '
                'Expected: intValue, actual: stringValue'
            ),
        ),
        (
            {
                'phone_id': '123459e1e7e5b1f539abcdef',
                'set': [{'field': 'foo', 'value': 'bar'}],
            },
            (
                'Field \'set[0].value\' is of a wrong type. '
                'Expected: booleanValue, actual: stringValue'
            ),
        ),
    ],
    ids=[
        'no phone_id',
        'int phone_id',
        'bad phone_id',
        'bad set',
        'bad inc',
        'no set and inc',
        'dummy set and inc',
        'inc without order_id',
        'bad inc value type',
        'bad set value type',
    ],
)
async def test_bad_request(taxi_user_api, body, message):
    response = await taxi_user_api.post(ENDPOINT, json=body)
    assert response.status_code == 400
    assert response.json()['code'] == '400'


async def test_not_found(taxi_user_api):
    response = await _save_stats(
        taxi_user_api,
        '123459e1e7e5b1f539abcdef',
        set_fields=[{'field': 'foo', 'value': True}],
    )
    assert response.status_code == 404
    assert response.json() == {
        'code': '404',
        'message': 'No such user_phone with id 123459e1e7e5b1f539abcdef',
    }


@pytest.mark.parametrize(
    'phone_id',
    ['539e99e1e7e5b1f5397adc5d', '123459e1e7e5b1f539abcdef'],
    ids=['real conflict', 'fake conflict'],
)
async def test_conflict(taxi_user_api, phone_id):
    response = await _save_stats(
        taxi_user_api,
        phone_id,
        inc_fields=[{'field': 'foo', 'value': 1}],
        order_id='order_id',
    )
    assert response.status_code == 409
    assert response.json() == {
        'code': 'possible_race',
        'message': 'Race during storing stats',
    }


async def test_inc(taxi_user_api, mongodb):
    response = await _save_stats(
        taxi_user_api,
        '539e99e1e7e5b1f5397adc5d',
        inc_fields=[{'field': 'foo', 'value': 1}],
        order_id='order_id1',
    )
    assert response.status_code == 200
    assert response.json() == {}
    phone_doc = mongodb.user_phones.find_one(
        bson.ObjectId('539e99e1e7e5b1f5397adc5d'),
        ['stat', 'loyalty_processed'],
    )
    assert phone_doc['stat']['foo'] == 1
    assert 'order_id1' in phone_doc['loyalty_processed']


async def test_inc_loyalty_processed_overflow(taxi_user_api, mongodb):
    response = await _save_stats(
        taxi_user_api,
        '539e99e1e7e5b1f5397adc5e',
        inc_fields=[{'field': 'total', 'value': 1}],
        order_id='order_id11',
    )
    assert response.status_code == 200
    assert response.json() == {}
    phone_doc = mongodb.user_phones.find_one(
        bson.ObjectId('539e99e1e7e5b1f5397adc5e'),
        ['stat', 'loyalty_processed'],
    )
    assert phone_doc['stat']['total'] == 101
    assert phone_doc['loyalty_processed'] == [
        'order_id2',
        'order_id3',
        'order_id4',
        'order_id5',
        'order_id6',
        'order_id7',
        'order_id8',
        'order_id9',
        'order_id10',
        'order_id11',
    ]


async def test_set(taxi_user_api, mongodb):
    response = await _save_stats(
        taxi_user_api,
        '539e99e1e7e5b1f5397adc5d',
        set_fields=[{'field': 'has_foo_orders', 'value': True}],
    )
    assert response.status_code == 200
    assert response.json() == {}
    phone_doc = mongodb.user_phones.find_one(
        bson.ObjectId('539e99e1e7e5b1f5397adc5d'), ['stat'],
    )
    assert phone_doc['stat']['has_foo_orders'] is True


async def test_updated_changed(taxi_user_api, mongodb):
    before = mongodb.user_phones.find_one(
        bson.ObjectId('539e99e1e7e5b1f5397adc5d'), ['updated'],
    )['updated']
    response = await _save_stats(
        taxi_user_api,
        '539e99e1e7e5b1f5397adc5d',
        set_fields=[{'field': 'has_foo_orders', 'value': True}],
    )
    assert response.status_code == 200
    assert response.json() == {}
    after = mongodb.user_phones.find_one(
        bson.ObjectId('539e99e1e7e5b1f5397adc5d'), ['updated'],
    )['updated']
    assert after > before


async def _save_stats(
        api, phone_id, inc_fields=None, set_fields=None, order_id=None,
):
    body = {'phone_id': phone_id}

    if inc_fields:
        body['inc'] = inc_fields

    if set_fields:
        body['set'] = set_fields

    if order_id:
        body['order_id_loyality_processed'] = order_id

    return await api.post(ENDPOINT, json=body)
