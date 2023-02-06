import datetime

import bson
import pytest

from tests_order_offers import utils

_NOW = datetime.datetime(2022, 1, 1)


def get_order_shards_exp_mark(shards):
    return pytest.mark.experiments3(
        name='order_offers_mongo_shards',
        match={'predicate': {'type': 'true'}, 'enabled': True},
        consumers=['sharded-mongo-wrapper/shards'],
        clauses=[
            {
                'enabled': True,
                'predicate': {'type': 'true'},
                'value': {'shards': shards},
            },
        ],
        is_config=True,
    )


ORDER_SHARDS_EXP = get_order_shards_exp_mark(
    [{'id': 1, 'weight': 1}, {'id': 2, 'weight': 1}, {'id': 3, 'weight': 1}],
)


@ORDER_SHARDS_EXP
@pytest.mark.parametrize(
    'is_mdb_collection',
    [
        pytest.param(
            False,
            marks=[
                pytest.mark.config(
                    SHARDED_MONGO_LIB_SHARDS_MAPPING={
                        'sharded-mongo-wrapper-component-for-tests': {
                            'default_collection': 'order_offers',
                        },
                    },
                ),
            ],
        ),
        pytest.param(
            True,
            marks=[
                pytest.mark.config(
                    SHARDED_MONGO_LIB_SHARDS_MAPPING={
                        'sharded-mongo-wrapper-component-for-tests': {
                            'order_offers_mdb': [1, 2, 3],
                            'default_collection': 'order_offers',
                        },
                    },
                ),
            ],
        ),
    ],
)
@pytest.mark.parametrize('is_mdb_only_request', [True, False])
async def test_save_offer(
        taxi_order_offers,
        mongodb,
        load_json,
        is_mdb_collection,
        is_mdb_only_request,
):
    request_json = load_json('offer_request.json')
    request_json['mdb_only'] = is_mdb_only_request

    response = await taxi_order_offers.post(
        '/v1/test/save-offer',
        headers={'content-type': 'application/bson'},
        data=bson.BSON.encode(request_json),
    )
    assert response.status_code == 200

    response_json = bson.BSON.decode(response.content)
    assert response_json['document'].get('_id', None)

    if is_mdb_collection or is_mdb_only_request:
        db_offer = mongodb.order_offers_mdb.find_one()
        assert not mongodb.order_offers.find_one()
    else:
        db_offer = mongodb.order_offers.find_one()
        assert not mongodb.order_offers_mdb.find_one()
    db_offer.pop('_id')
    db_offer.pop('_shard_id')
    assert db_offer == request_json['payload']


@ORDER_SHARDS_EXP
async def test_save_offer_retry(taxi_order_offers, mongodb, load_json):
    offer_id = '1331acd737e252f2eee2d4b933a0dcf0'

    request_json = load_json('offer_request.json')
    request_json['payload']['_id'] = offer_id
    request_json['payload']['_shard_id'] = 17
    request_json['mdb_only'] = True

    response = await taxi_order_offers.post(
        '/v1/test/save-offer',
        headers={'content-type': 'application/bson'},
        data=bson.BSON.encode(request_json),
    )
    assert response.status_code == 200

    response = await taxi_order_offers.post(
        '/v1/test/save-offer',
        headers={'content-type': 'application/bson'},
        data=bson.BSON.encode(request_json),
    )
    assert response.status_code == 200

    response_json = bson.BSON.decode(response.content)
    assert response_json['document']['_id'] == offer_id

    db_offer = mongodb.order_offers_mdb.find_one()
    assert not mongodb.order_offers.find_one()
    assert db_offer == request_json['payload']


@pytest.mark.parametrize(
    'request_id, request_sort, expected_response',
    [
        (
            '123',
            [{'field': '_id', 'dir': -1}],
            [
                {
                    '_id': '444',
                    '_shard_id': 2,
                    'unused': 3,
                    'user_id': '123',
                    'date': _NOW + datetime.timedelta(seconds=3),
                },
                {
                    '_id': '333',
                    '_shard_id': 1,
                    'unused': 3,
                    'user_id': '123',
                    'date': _NOW + datetime.timedelta(seconds=2),
                },
                {
                    '_id': '222',
                    '_shard_id': 2,
                    'unused': 1,
                    'user_id': '123',
                    'date': _NOW + datetime.timedelta(seconds=1),
                },
                {
                    '_id': '111',
                    '_shard_id': 1,
                    'unused': 1,
                    'user_id': '123',
                    'date': _NOW,
                },
            ],
        ),
        (
            '123',
            [{'field': 'date', 'dir': 1}],
            [
                {
                    '_id': '111',
                    '_shard_id': 1,
                    'unused': 1,
                    'user_id': '123',
                    'date': _NOW,
                },
                {
                    '_id': '222',
                    '_shard_id': 2,
                    'unused': 1,
                    'user_id': '123',
                    'date': _NOW + datetime.timedelta(seconds=1),
                },
                {
                    '_id': '333',
                    '_shard_id': 1,
                    'unused': 3,
                    'user_id': '123',
                    'date': _NOW + datetime.timedelta(seconds=2),
                },
                {
                    '_id': '444',
                    '_shard_id': 2,
                    'unused': 3,
                    'user_id': '123',
                    'date': _NOW + datetime.timedelta(seconds=3),
                },
            ],
        ),
        (
            '123',
            [{'field': 'unused', 'dir': 1}, {'field': 'date', 'dir': -1}],
            [
                {
                    '_id': '222',
                    '_shard_id': 2,
                    'unused': 1,
                    'user_id': '123',
                    'date': _NOW + datetime.timedelta(seconds=1),
                },
                {
                    '_id': '111',
                    '_shard_id': 1,
                    'unused': 1,
                    'user_id': '123',
                    'date': _NOW,
                },
                {
                    '_id': '444',
                    '_shard_id': 2,
                    'unused': 3,
                    'user_id': '123',
                    'date': _NOW + datetime.timedelta(seconds=3),
                },
                {
                    '_id': '333',
                    '_shard_id': 1,
                    'unused': 3,
                    'user_id': '123',
                    'date': _NOW + datetime.timedelta(seconds=2),
                },
            ],
        ),
        (
            '123',
            [{'field': 'unused', 'dir': -1}, {'field': 'date', 'dir': 1}],
            [
                {
                    '_id': '333',
                    '_shard_id': 1,
                    'unused': 3,
                    'user_id': '123',
                    'date': _NOW + datetime.timedelta(seconds=2),
                },
                {
                    '_id': '444',
                    '_shard_id': 2,
                    'unused': 3,
                    'user_id': '123',
                    'date': _NOW + datetime.timedelta(seconds=3),
                },
                {
                    '_id': '111',
                    '_shard_id': 1,
                    'unused': 1,
                    'user_id': '123',
                    'date': _NOW,
                },
                {
                    '_id': '222',
                    '_shard_id': 2,
                    'unused': 1,
                    'user_id': '123',
                    'date': _NOW + datetime.timedelta(seconds=1),
                },
            ],
        ),
        ('not-found-user', None, []),
        (
            'user-lxc',
            None,
            [
                {
                    '_id': 'user-lxc-id',
                    '_shard_id': 1,
                    'unused': -1,
                    'user_id': 'user-lxc',
                },
            ],
        ),
        (
            'user-mdb',
            None,
            [
                {
                    '_id': 'user-mdb-id',
                    '_shard_id': 2,
                    'unused': -1,
                    'user_id': 'user-mdb',
                },
            ],
        ),
    ],
)
@pytest.mark.filldb(order_offers='search_offers')
@pytest.mark.filldb(order_offers_mdb='search_offers')
@pytest.mark.now(_NOW.isoformat())
async def test_search_offers(
        taxi_order_offers,
        mongodb,
        request_id,
        request_sort,
        expected_response,
):
    request = {
        'query': {'user_id': request_id},
        'fields': ['user_id', '_shard_id', '_id', 'date', 'unused'],
    }
    if request_sort:
        request['sort'] = request_sort

    response = await taxi_order_offers.post(
        '/v1/test/search-offers',
        headers={'content-type': 'application/bson'},
        data=bson.BSON.encode(request),
    )
    assert response.status_code == 200

    response_json = bson.BSON.decode(response.content)
    assert response_json['documents'] == expected_response


@pytest.mark.config(
    SHARDED_MONGO_LIB_SHARD_POOL_LIMIT={
        'sharded-mongo-wrapper-component-for-tests': {
            'enabled': True,
            'pool_limit_per_shard': 1,
            'timeout': 0,
        },
    },
)
@get_order_shards_exp_mark(shards=[{'id': 0, 'weight': 1}])
async def test_shard_pool_limit(
        taxi_order_offers, testpoint, load_json, taxi_order_offers_monitor,
):
    request_json = load_json('offer_request.json')

    testpoint_reached = False

    @testpoint('sharded-mongo-lib-shard-pool-lock-taken')
    async def testpoint_lock_taken(data):
        # If logic with lock doesn't work
        # we will reach testpoint again after calling
        # save-offer here, and then again and again.
        # In this case this crutch prevents endless loop,
        # which ends with incomprehensible error.
        nonlocal testpoint_reached
        assert not testpoint_reached
        testpoint_reached = True

        result2 = await taxi_order_offers.post(
            '/v1/test/save-offer',
            headers={'content-type': 'application/bson'},
            data=bson.BSON.encode(request_json),
        )
        assert result2.status_code == 500

    result = await taxi_order_offers.post(
        '/v1/test/save-offer',
        headers={'content-type': 'application/bson'},
        data=bson.BSON.encode(request_json),
    )
    assert result.status_code == 200
    assert testpoint_lock_taken.times_called == 1

    metrics = await taxi_order_offers_monitor.get_metric(
        'sharded-mongo-wrapper-component-for-tests',
    )
    assert metrics['by-shard']['0']['errors']['pool-limit'] == 1


@pytest.mark.parametrize(
    'shard_id',
    [
        pytest.param(
            1,
            marks=[get_order_shards_exp_mark(shards=[{'id': 1, 'weight': 1}])],
        ),
        pytest.param(
            2,
            marks=[get_order_shards_exp_mark(shards=[{'id': 2, 'weight': 1}])],
        ),
        pytest.param(
            3,
            marks=[get_order_shards_exp_mark(shards=[{'id': 3, 'weight': 1}])],
        ),
    ],
)
async def test_gen_shard_id(taxi_order_offers, shard_id):
    response = await taxi_order_offers.post(
        '/v1/test/gen-shard-id',
        headers={'Content-Type': 'application/bson'},
        data=bson.BSON.encode({}),
    )
    assert response.status_code == 200

    resp: dict = bson.BSON.decode(response.content)
    assert '_id' in resp
    assert utils.get_shard_id(resp['_id']) == shard_id


@ORDER_SHARDS_EXP
@pytest.mark.config(
    SHARDED_MONGO_LIB_USE_ALIVE_SHARD={
        'sharded-mongo-wrapper-component-for-tests': {
            'enabled': True,
            'excluded_limit': 2,
        },
    },
)
@pytest.mark.parametrize('not_excluding', [1, 2, 3])
async def test_shards_excluded_if_fallback(
        taxi_order_offers, mongodb, load_json, statistics, not_excluding,
):
    shards = set([1, 2, 3])
    shards.remove(not_excluding)
    fallback_name_prefix = 'order-offers'
    statistics.fallbacks = [
        '{}.mongo_shard_id{}.fallback'.format(fallback_name_prefix, shard)
        for shard in shards
    ]

    request_json = load_json('offer_request.json')
    response = await taxi_order_offers.post(
        '/v1/test/save-offer',
        headers={'Content-Type': 'application/bson'},
        data=bson.BSON.encode(request_json),
    )
    assert response.status_code == 200

    db_offer = mongodb.order_offers.find_one()
    assert db_offer['_shard_id'] == not_excluding


@ORDER_SHARDS_EXP
@pytest.mark.parametrize(
    'excluded_limit',
    [
        pytest.param(
            2,
            marks=[
                pytest.mark.config(
                    SHARDED_MONGO_LIB_USE_ALIVE_SHARD={
                        'sharded-mongo-wrapper-component-for-tests': {
                            'enabled': True,
                            'excluded_limit': 2,
                        },
                    },
                ),
            ],
        ),
        pytest.param(
            3,
            marks=[
                pytest.mark.config(
                    SHARDED_MONGO_LIB_USE_ALIVE_SHARD={
                        'sharded-mongo-wrapper-component-for-tests': {
                            'enabled': True,
                            'excluded_limit': 3,
                        },
                    },
                ),
            ],
        ),
    ],
)
async def test_shards_excluded_limit(
        taxi_order_offers, mongodb, load_json, statistics, excluded_limit,
):
    fallback_name_prefix = 'order-offers'
    statistics.fallbacks = [
        '{}.mongo_shard_id{}.fallback'.format(fallback_name_prefix, shard)
        for shard in [1, 2, 3]
    ]

    request_json = load_json('offer_request.json')
    response = await taxi_order_offers.post(
        '/v1/test/save-offer',
        headers={'Content-Type': 'application/bson'},
        data=bson.BSON.encode(request_json),
    )
    assert response.status_code == 200

    db_offer = mongodb.order_offers.find_one()
    # zero is a fallback shard
    if excluded_limit == 3:
        # should be chosen if other were excluded
        assert db_offer['_shard_id'] == 0
    else:
        # shouldn't be chosen if limit worked
        assert db_offer['_shard_id'] != 0


@pytest.mark.parametrize(
    'document_id',
    ['e9e24bcc3c13583abf2493b8cd949de5', '9b822344631669e5a79fa71b382350b2'],
)
@pytest.mark.config(
    SHARDED_MONGO_LIB_SHARDS_MAPPING={
        'sharded-mongo-wrapper-component-for-tests': {
            'order_offers': [1],
            'order_offers_mdb': [2, 3],
            'default_collection': 'order_offers',
        },
    },
)
@pytest.mark.filldb(order_offers='get_fields')
@pytest.mark.filldb(order_offers_mdb='get_fields')
@ORDER_SHARDS_EXP
async def test_get_fields(taxi_order_offers, document_id):
    request = {'filter': {'user_id': '123'}, 'fields': ['date']}

    response = await taxi_order_offers.post(
        '/v1/test/get-fields',
        headers={'content-type': 'application/bson'},
        params={'document_id': document_id},
        data=bson.BSON.encode(request),
    )
    assert response.status_code == 200

    res = bson.BSON.decode(response.content)
    assert res['document'].pop('date')
    assert res['document'].pop('_id') == document_id
    assert res['document'] == {}

    # making sure filter works
    request['filter']['user_id'] = '1234'
    response = await taxi_order_offers.post(
        '/v1/test/get-fields',
        headers={'content-type': 'application/bson'},
        params={'document_id': document_id},
        data=bson.BSON.encode(request),
    )
    assert response.status_code == 404


@pytest.mark.filldb(order_offers='get_fields')
async def test_get_fields_no_such_order(taxi_order_offers):
    request = {'filter': {}, 'fields': ['date']}

    response = await taxi_order_offers.post(
        '/v1/test/get-fields',
        headers={'content-type': 'application/bson'},
        params={'document_id': 'no_such_document_id'},
        data=bson.BSON.encode(request),
    )
    assert response.status_code == 404
