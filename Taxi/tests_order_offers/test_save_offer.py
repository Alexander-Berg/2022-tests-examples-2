import datetime
import json

import bson
import pytest

from tests_order_offers import utils


OFFER_ID = '18d3a1133568d1c0fa5436123afbc370'
OFFER_CREATED = datetime.datetime(2021, 10, 20, 8, 23, 7)

SAVE_MDB_MONGO_MARKS = [
    pytest.mark.experiments3(
        name='order_offers_save_mdb_mongo',
        consumers=['order-offers/mongo-switch'],
        is_config=True,
        default_value={'lxc_mongo': 'disabled', 'mdb_mongo': 'enabled_main'},
    ),
]


def parse_tskv(source):
    return {
        item.split('=')[0]: '='.join(item.split('=')[1:])
        for item in source.split('\t')
    }


@pytest.mark.parametrize(
    'request_data, expected_error_code',
    [
        pytest.param('', 'BSON_PARSE_ERROR', id='invalid_bson'),
        pytest.param({}, 'MISSING_PAYLOAD', id='empty_bson'),
        pytest.param(
            {'not_payload': {}}, 'MISSING_PAYLOAD', id='missing_payload',
        ),
        pytest.param(
            {'payload': {}}, 'MISSING_OFFER_ID', id='missing_offer_id',
        ),
        pytest.param(
            {'payload': {'_id': OFFER_ID}},
            'MISSING_CREATED',
            id='missing_created',
        ),
    ],
)
@pytest.mark.parametrize(
    'use_mdb_mongo',
    [
        pytest.param(False, id='mdb_disabled'),
        pytest.param(True, marks=SAVE_MDB_MONGO_MARKS, id='mdb_enabled'),
    ],
)
async def test_offer_validate_error(
        taxi_order_offers, request_data, expected_error_code, use_mdb_mongo,
):
    response = await utils.make_save_request(taxi_order_offers, request_data)
    assert response.status_code == 400
    assert response.json()['code'] == expected_error_code


@pytest.mark.parametrize('request_file', ['empty_offer', 'full_offer'])
@pytest.mark.parametrize(
    'use_mdb_mongo',
    [
        pytest.param(False, id='mdb_disabled'),
        pytest.param(
            False,
            marks=[
                pytest.mark.experiments3(
                    name='order_offers_save_mdb_mongo',
                    consumers=['order-offers/mongo-switch'],
                    is_config=True,
                    default_value={
                        'lxc_mongo': 'enabled_main',
                        'mdb_mongo': 'disabled',
                    },
                ),
            ],
            id='mdb_disabled_explicit',
        ),
        pytest.param(True, marks=SAVE_MDB_MONGO_MARKS, id='mdb_enabled'),
    ],
)
async def test_basic(
        taxi_order_offers, mongodb, load_json, request_file, use_mdb_mongo,
):
    request_json = load_json(f'{request_file}_request.json')

    response = await utils.make_save_request(taxi_order_offers, request_json)
    assert response.status_code == 200

    response_json = bson.BSON.decode(response.content)
    assert response_json == {
        'document': {'_id': OFFER_ID, 'created': OFFER_CREATED},
    }

    db_offer_mdb = mongodb.order_offers_mdb.find_one({'_id': OFFER_ID})
    db_offer_lxc = mongodb.order_offers.find_one({'_id': OFFER_ID})
    if use_mdb_mongo:
        assert db_offer_lxc is None
        db_offer = db_offer_mdb
    else:
        assert db_offer_mdb is None
        db_offer = db_offer_lxc
    assert db_offer == request_json['payload']


@pytest.mark.parametrize(
    'requests_match',
    [
        pytest.param(False, id='requests_dont_match'),
        pytest.param(True, id='requests_match'),
    ],
)
@pytest.mark.parametrize(
    'conflict_check_enabled',
    [
        pytest.param(False, id='conflict_check_disabled'),
        pytest.param(
            True,
            marks=pytest.mark.config(
                ORDER_OFFERS_SAVE_CONFLICT_CHECK_ENABLED=True,
            ),
            id='conflict_check_enabled',
        ),
    ],
)
@pytest.mark.parametrize(
    'use_mdb_mongo',
    [
        pytest.param(False, id='mdb_disabled'),
        pytest.param(True, marks=SAVE_MDB_MONGO_MARKS, id='mdb_enabled'),
    ],
)
async def test_idempotency(
        taxi_order_offers,
        mongodb,
        load_json,
        requests_match,
        conflict_check_enabled,
        use_mdb_mongo,
):
    original_request = load_json('full_offer_request.json')
    request = load_json('full_offer_request.json')

    for request_index in range(3):
        response = await utils.make_save_request(taxi_order_offers, request)

        if requests_match:
            assert response.status_code == 200
        else:
            if conflict_check_enabled and request_index != 0:
                assert response.status_code == 409
            else:
                assert response.status_code == 200

        if not requests_match:
            # modify payload for the next request
            request['payload']['distance'] += 1000

    db_offer_mdb = mongodb.order_offers_mdb.find_one({'_id': OFFER_ID})
    db_offer_lxc = mongodb.order_offers.find_one({'_id': OFFER_ID})
    if use_mdb_mongo:
        assert db_offer_lxc is None
        db_offer = db_offer_mdb
    else:
        assert db_offer_mdb is None
        db_offer = db_offer_lxc
    assert db_offer == original_request['payload']


@pytest.mark.now('2021-10-28T16:07:31.014697+0000')
@pytest.mark.parametrize(
    'use_mdb_mongo',
    [
        pytest.param(False, id='mdb_disabled'),
        pytest.param(True, marks=SAVE_MDB_MONGO_MARKS, id='mdb_enabled'),
    ],
)
async def test_logbroker_message(
        taxi_order_offers, testpoint, load_json, use_mdb_mongo,
):
    @testpoint('logbroker_publish')
    def commit(data):
        assert data['name'] == 'order-offers-producer'

        message = parse_tskv(data['data'])
        assert set(message.keys()) == {'timestamp', 'id', 'created', 'doc'}

        assert message['timestamp'] == '2021-10-28T16:07:31.014697+0000'
        assert message['id'] == '18d3a1133568d1c0fa5436123afbc370'
        assert message['created'] == '2021-10-20T08:23:07+0000'
        assert json.loads(message['doc']) == {
            '_id': '18d3a1133568d1c0fa5436123afbc370',
            '_shard_id': 25,
            'created': '2021-10-20T08:23:07+0000',
        }

    response = await utils.make_save_request(
        taxi_order_offers, load_json('empty_offer_request.json'),
    )
    assert response.status_code == 200

    await commit.wait_call()


@pytest.mark.parametrize(
    'fs_fallback_enabled',
    [
        pytest.param(False, id='fs_fallback_disabled'),
        pytest.param(
            True,
            marks=pytest.mark.config(
                ORDER_OFFERS_LOGBROKER_DELIVERY_FS_FALLBACK_ENABLED=True,
            ),
            id='fs_fallback_enabled',
        ),
    ],
)
@pytest.mark.config(ORDER_OFFERS_LOGBROKER_DELIVERY_MAX_TASKS=0)
@pytest.mark.now('2021-10-28T16:07:31.014697+0000')
async def test_logbroker_max_tasks_fs_fallback(
        taxi_order_offers, testpoint, load_json, fs_fallback_enabled,
):
    @testpoint('logbroker_fs_fallback')
    def logbroker_fs_fallback(data):
        message = parse_tskv(data['message'])
        assert set(message.keys()) == {
            'timestamp',
            'timestamp_raw',
            'id',
            'created',
            'doc',
            'tskv',
        }
        assert message['timestamp'] == '2021-10-28T16:07:31.014697+0000'
        assert message['id'] == '18d3a1133568d1c0fa5436123afbc370'
        assert message['created'] == '2021-10-20T08:23:07+0000'
        assert json.loads(message['doc']) == {
            '_id': '18d3a1133568d1c0fa5436123afbc370',
            '_shard_id': 25,
            'created': '2021-10-20T08:23:07+0000',
        }

    response = await utils.make_save_request(
        taxi_order_offers, load_json('empty_offer_request.json'),
    )
    assert response.status_code == 200

    assert logbroker_fs_fallback.times_called == (
        1 if fs_fallback_enabled else 0
    )


@pytest.mark.parametrize(
    'fs_fallback_enabled',
    [
        pytest.param(False, id='fs_fallback_disabled'),
        pytest.param(
            True,
            marks=pytest.mark.config(
                ORDER_OFFERS_LOGBROKER_DELIVERY_FS_FALLBACK_ENABLED=True,
            ),
            id='fs_fallback_enabled',
        ),
    ],
)
@pytest.mark.now('2021-10-28T16:07:31.014697+0000')
async def test_logbroker_failure_fs_fallback(
        taxi_order_offers, testpoint, load_json, fs_fallback_enabled,
):
    @testpoint('logbroker_bts_finished')
    def logbroker_bts_finished(data):
        pass

    @testpoint('logbroker_fs_fallback')
    def logbroker_fs_fallback(data):
        message = parse_tskv(data['message'])
        assert set(message.keys()) == {
            'timestamp',
            'timestamp_raw',
            'id',
            'created',
            'doc',
            'tskv',
        }
        assert message['timestamp'] == '2021-10-28T16:07:31.014697+0000'
        assert message['id'] == '18d3a1133568d1c0fa5436123afbc370'
        assert message['created'] == '2021-10-20T08:23:07+0000'
        assert json.loads(message['doc']) == {
            '_id': '18d3a1133568d1c0fa5436123afbc370',
            '_shard_id': 25,
            'created': '2021-10-20T08:23:07+0000',
        }

    @testpoint('logbroker_callback')
    def logbroker_callback(data):
        return {'inject_failure': True}

    response = await utils.make_save_request(
        taxi_order_offers, load_json('empty_offer_request.json'),
    )
    assert response.status_code == 200

    await logbroker_callback.wait_call()
    await logbroker_bts_finished.wait_call()

    assert logbroker_fs_fallback.times_called == (
        1 if fs_fallback_enabled else 0
    )


@pytest.mark.now('2021-10-28T16:07:31.014697+0000')
@pytest.mark.parametrize(
    'use_mdb_mongo',
    [
        pytest.param(False, id='mdb_disabled'),
        pytest.param(True, marks=SAVE_MDB_MONGO_MARKS, id='mdb_enabled'),
    ],
)
async def test_compressed_request(taxi_order_offers, load_json, use_mdb_mongo):
    request = load_json('full_offer_request.json')

    response = await utils.make_save_request(
        taxi_order_offers, request, compress=True,
    )
    assert response.status_code == 200


@pytest.mark.parametrize(
    '',
    [
        pytest.param(
            marks=[
                pytest.mark.experiments3(
                    name='order_offers_save_mdb_mongo',
                    consumers=['order-offers/mongo-switch'],
                    is_config=True,
                    default_value={
                        'lxc_mongo': 'enabled_main',
                        'mdb_mongo': 'enabled_sync',
                    },
                ),
            ],
            id='lxc_main_mdb_sync',
        ),
        pytest.param(
            marks=[
                pytest.mark.experiments3(
                    name='order_offers_save_mdb_mongo',
                    consumers=['order-offers/mongo-switch'],
                    is_config=True,
                    default_value={
                        'lxc_mongo': 'enabled_async',
                        'mdb_mongo': 'enabled_main',
                    },
                ),
            ],
            id='lxc_async_mdb_main',
        ),
    ],
)
async def test_parallel_store(
        taxi_order_offers, mongodb, load_json, testpoint,
):
    @testpoint('order-offers-lxc-store')
    def mongo_lxc_store(data):
        pass

    @testpoint('order-offers-mdb-store')
    def mongo_mdb_store(data):
        pass

    request_json = load_json('full_offer_request.json')

    response = await utils.make_save_request(taxi_order_offers, request_json)
    assert response.status_code == 200

    response_json = bson.BSON.decode(response.content)
    assert response_json == {
        'document': {'_id': OFFER_ID, 'created': OFFER_CREATED},
    }

    await mongo_lxc_store.wait_call()
    await mongo_mdb_store.wait_call()

    db_offer_mdb = mongodb.order_offers_mdb.find_one({'_id': OFFER_ID})
    assert db_offer_mdb == request_json['payload']

    db_offer_lxc = mongodb.order_offers.find_one({'_id': OFFER_ID})
    assert db_offer_lxc == request_json['payload']


@pytest.mark.parametrize(
    'use_mdb_mongo',
    [
        pytest.param(
            False,
            marks=[
                pytest.mark.experiments3(
                    name='order_offers_save_mdb_mongo',
                    consumers=['order-offers/mongo-switch'],
                    is_config=True,
                    default_value={
                        'lxc_mongo': 'enabled_main',
                        'mdb_mongo': 'enabled_async',
                    },
                ),
            ],
            id='lxc_main_mdb_async',
        ),
        pytest.param(
            True,
            marks=[
                pytest.mark.experiments3(
                    name='order_offers_save_mdb_mongo',
                    consumers=['order-offers/mongo-switch'],
                    is_config=True,
                    default_value={
                        'lxc_mongo': 'enabled_async',
                        'mdb_mongo': 'enabled_main',
                    },
                ),
            ],
            id='lxc_async_mdb_main',
        ),
    ],
)
@pytest.mark.config(ORDER_OFFERS_MONGO_ASYNC_STORE_MAX_TASKS=0)
async def test_async_store_limit(
        taxi_order_offers, mongodb, load_json, testpoint, use_mdb_mongo,
):
    @testpoint('order-offers-lxc-store')
    def mongo_lxc_store(data):
        pass

    @testpoint('order-offers-mdb-store')
    def mongo_mdb_store(data):
        pass

    @testpoint('order-offers-async-store-limit')
    def mongo_async_store_limit(data):
        pass

    request_json = load_json('full_offer_request.json')

    response = await utils.make_save_request(taxi_order_offers, request_json)
    assert response.status_code == 200

    response_json = bson.BSON.decode(response.content)
    assert response_json == {
        'document': {'_id': OFFER_ID, 'created': OFFER_CREATED},
    }

    await mongo_async_store_limit.wait_call()

    if use_mdb_mongo:
        await mongo_mdb_store.wait_call()
        assert mongo_lxc_store.times_called == 0
    else:
        await mongo_lxc_store.wait_call()
        assert mongo_mdb_store.times_called == 0

    db_offer_mdb = mongodb.order_offers_mdb.find_one({'_id': OFFER_ID})
    db_offer_lxc = mongodb.order_offers.find_one({'_id': OFFER_ID})

    if use_mdb_mongo:
        assert db_offer_mdb == request_json['payload']
        assert db_offer_lxc is None
    else:
        assert db_offer_lxc == request_json['payload']
        assert db_offer_mdb is None
