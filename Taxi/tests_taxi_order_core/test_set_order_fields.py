import datetime

import pytest


ORDER_ID = '71e78aa6276c38c08f12def2af04799e'
USER_ID = 'c066912d9e6410fe516c4af3f948a882'
VERSION = 'DAAAAAAABgAMAAQABgAAAApngRltAQAA'

ALLOWED_FIELDS = [
    'set_field',
    'new_field',
    'some_object.nested_object',
    'unset_field',
    'array_field',
    'inc_field',
]


@pytest.mark.config(ORDER_CORE_SET_FIELDS_WHITELIST=ALLOWED_FIELDS)
async def test_set_order_fields_basic(taxi_order_core, mongodb, mockserver):
    body = {
        'order_id': ORDER_ID,
        'version': VERSION,
        'user_id': USER_ID,
        'call_processing': True,
        'update': {
            'set': {
                'set_field': 'new_set_field_value',
                'new_field': 'some_new_value',
                'some_object.nested_object.nested_field': 'nested_field_value',
            },
            'unset': {'unset_field': ''},
            'push': {'array_field': {'arr_field3': 'arr_val3'}},
            'inc': {'inc_field': 2},
        },
    }
    response = await taxi_order_core.post('/v1/tc/set-order-fields', json=body)
    assert response.status_code == 200

    proc = mongodb.order_proc.find_one({'_id': ORDER_ID})
    assert proc['updated'] > datetime.datetime(2019, 9, 10, 4, 49, 33, 962000)
    proc.pop('updated')
    expected = {
        '_id': '71e78aa6276c38c08f12def2af04799e',
        '_shard_id': 7,
        'array_field': [
            {'arr_field1': 'arr_val1'},
            {'arr_field2': 'arr_val2'},
            {'arr_field3': 'arr_val3'},
        ],
        'inc_field': 3,
        'new_field': 'some_new_value',
        'order': {'user_id': 'c066912d9e6410fe516c4af3f948a882', 'version': 5},
        'processing': {'version': 15},
        'set_field': 'new_set_field_value',
        'some_object': {
            'nested_object': {'nested_field': 'nested_field_value'},
        },
    }
    assert proc == expected


@pytest.mark.config(ORDER_CORE_SET_FIELDS_WHITELIST=['changes.objects'])
async def test_set_order_fields_date(taxi_order_core, mongodb):
    body = {
        'order_id': ORDER_ID,
        'version': VERSION,
        'user_id': USER_ID,
        'update': {
            'push': {
                'changes.objects': {
                    'c': {'$date': '2020-04-23T08:05:10.561Z'},
                    't': {'$date': '2020-04-23T08:05:10.561+00:00'},
                    'si': {'t': {'$date': '2020-04-23T08:05:10.561+0000'}},
                },
            },
        },
    }
    response = await taxi_order_core.post('/v1/tc/set-order-fields', json=body)
    assert response.status_code == 200

    proc = mongodb.order_proc.find_one({'_id': ORDER_ID})
    proc.pop('updated')

    expected = {
        '_id': '71e78aa6276c38c08f12def2af04799e',
        '_shard_id': 7,
        'changes': {
            'objects': [
                {
                    'c': datetime.datetime(2020, 4, 23, 8, 5, 10, 561000),
                    't': datetime.datetime(2020, 4, 23, 8, 5, 10, 561000),
                    'si': {
                        't': datetime.datetime(2020, 4, 23, 8, 5, 10, 561000),
                    },
                },
            ],
        },
        'order': {'user_id': 'c066912d9e6410fe516c4af3f948a882', 'version': 5},
        'processing': {'version': 15},
        'array_field': [
            {'arr_field1': 'arr_val1'},
            {'arr_field2': 'arr_val2'},
        ],
        'inc_field': 1,
        'set_field': 'set_value',
        'some_object': {'nested_object': {}},
        'unset_field': 'unset_value',
    }
    assert proc == expected


@pytest.mark.config(ORDER_CORE_SET_FIELDS_WHITELIST=['new_field'])
async def test_set_order_fields_date_wrong_format(taxi_order_core, mongodb):
    body = {
        'order_id': ORDER_ID,
        'version': VERSION,
        'user_id': USER_ID,
        'update': {'set': {'new_field': {'$date': 'May 1, 2020'}}},
    }
    response = await taxi_order_core.post('/v1/tc/set-order-fields', json=body)
    assert response.status_code == 500


@pytest.mark.config(ORDER_CORE_SET_FIELDS_WHITELIST=['new_field'])
async def test_set_order_fields_incorrect_names_with_dollar_sign(
        taxi_order_core, mongodb,
):
    body = {
        'order_id': ORDER_ID,
        'version': VERSION,
        'user_id': USER_ID,
        'update': {'set': {'new_field': {'$date': 'date', '$time': 'time'}}},
    }
    response = await taxi_order_core.post('/v1/tc/set-order-fields', json=body)
    assert response.status_code == 500


@pytest.mark.config(ORDER_CORE_SET_FIELDS_WHITELIST=ALLOWED_FIELDS)
async def test_set_order_version_mismatch(taxi_order_core, mongodb):
    bad_version = 'CAAAAAAABgAMAAQABgAAAApngRltAQAA'
    body = {
        'order_id': ORDER_ID,
        'version': bad_version,
        'user_id': USER_ID,
        'update': {'set': {'set_field': 'new_value'}},
    }
    response = await taxi_order_core.post('/v1/tc/set-order-fields', json=body)
    assert response.status_code == 409
    assert response.json()['message'] == 'Proc version mismatch'


async def test_set_order_field_not_allowed(taxi_order_core):
    body = {
        'order_id': ORDER_ID,
        'version': VERSION,
        'user_id': USER_ID,
        'update': {'set': {'set_field': 'new_value'}},
    }
    response = await taxi_order_core.post('/v1/tc/set-order-fields', json=body)
    assert response.status_code == 400
    response = response.json()
    assert (
        response['message'] == 'Changes in field \'set_field\' are not allowed'
    )


@pytest.mark.config(ORDER_CORE_SET_FIELDS_WHITELIST=ALLOWED_FIELDS)
async def test_set_order_field_restart_not_allowed_not_call_restart(
        taxi_order_core,
):
    body = {
        'order_id': ORDER_ID,
        'version': VERSION,
        'user_id': USER_ID,
        'call_processing': False,
        'update': {
            'set': {
                'set_field': 'new_set_field_value',
                'new_field': 'some_new_value',
                'some_object.nested_object.nested_field': 'nested_field_value',
            },
            'unset': {'unset_field': ''},
            'push': {'array_field': {'arr_field3': 'arr_val3'}},
            'inc': {'inc_field': 2},
        },
    }
    response = await taxi_order_core.post('/v1/tc/set-order-fields', json=body)
    assert response.status_code == 200


@pytest.mark.config(ORDER_CORE_SET_FIELDS_WHITELIST=ALLOWED_FIELDS)
async def test_set_order_order_not_found(taxi_order_core):
    bad_id = '81e78aa6276c38c08f12def2af04799e'
    body = {
        'order_id': bad_id,
        'version': VERSION,
        'user_id': USER_ID,
        'update': {'set': {'set_field': 'new_value'}},
    }
    response = await taxi_order_core.post('/v1/tc/set-order-fields', json=body)
    assert response.status_code == 404
    response = response.json()
    assert response['message'] == 'Order not found'


async def test_set_order_empty_update(taxi_order_core):
    body = {
        'order_id': ORDER_ID,
        'version': VERSION,
        'user_id': USER_ID,
        'update': {'set': {}},
    }
    response = await taxi_order_core.post('/v1/tc/set-order-fields', json=body)
    assert response.status_code == 400
    response = response.json()
    assert response['message'] == 'Empty update'
