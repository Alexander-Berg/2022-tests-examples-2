import datetime

import bson
import pytest

from tests_order_offers import utils


OFFER_ID_LXC = '18d3a1133568d1c0fa5436123afbc370'
OFFER_ID_MDB = '1331acd737e252f2eee2d4b933a0dcf0'
USER_ID = 'b9efee4710a84b42a765996ae9f86e2e'

MATCH_BY_MDB_MONGO_MARKS = [
    pytest.mark.experiments3(
        name='order_offers_match_mdb_mongo',
        consumers=['order-offers/mongo-switch'],
        is_config=True,
        default_value={'enabled': True},
    ),
]


@pytest.mark.parametrize(
    'request_data, expected_error_code',
    [
        pytest.param('', 'BSON_PARSE_ERROR', id='invalid_bson'),
        pytest.param({}, 'MISSING_FILTERS', id='empty_bson'),
        pytest.param(
            {'not_filters': {}}, 'MISSING_FILTERS', id='missing_filters',
        ),
        pytest.param(
            {'filters': 'not_an_object'},
            'MISSING_FILTERS',
            id='filters_bad_format',
        ),
    ],
)
@pytest.mark.parametrize(
    'use_mdb_mongo',
    [
        pytest.param(False, id='mdb_disabled'),
        pytest.param(True, marks=MATCH_BY_MDB_MONGO_MARKS, id='mdb_enabled'),
    ],
)
async def test_request_validate_error(
        taxi_order_offers, request_data, expected_error_code, use_mdb_mongo,
):
    response = await utils.make_match_request(taxi_order_offers, request_data)
    assert response.status_code == 400
    assert response.json()['code'] == expected_error_code


@pytest.mark.parametrize(
    'use_mdb_mongo',
    [
        pytest.param(False, id='mdb_disabled'),
        pytest.param(True, marks=MATCH_BY_MDB_MONGO_MARKS, id='mdb_enabled'),
    ],
)
async def test_mismatch_without_offer_and_user_ids(
        taxi_order_offers, taxi_order_offers_monitor, use_mdb_mongo,
):
    await taxi_order_offers.tests_control(reset_metrics=True)

    request = {'filters': {'requirements': {}}}

    response = await utils.make_match_request(taxi_order_offers, request)
    assert response.status_code == 200

    response_json = bson.BSON.decode(response.content)
    assert response_json == {'result': 'mismatch'}

    metrics = await taxi_order_offers_monitor.get_metrics()
    if use_mdb_mongo:
        assert metrics['match-offer-mdb-empty-query-not-matched'] == 1
    else:
        assert metrics['match-offer-lxc-empty-query-not-matched'] == 1


@pytest.mark.parametrize(
    'use_mdb_mongo, offer_id',
    [
        pytest.param(False, OFFER_ID_LXC),
        pytest.param(True, OFFER_ID_MDB, marks=MATCH_BY_MDB_MONGO_MARKS),
    ],
)
async def test_match_by_offer_id(
        taxi_order_offers,
        taxi_order_offers_monitor,
        mongodb,
        use_mdb_mongo,
        offer_id,
):
    await taxi_order_offers.tests_control(reset_metrics=True)

    request = {
        'filters': {
            'offer_id': offer_id,
            'user_id': USER_ID,
            'order': {
                'due': datetime.datetime(2021, 10, 20, 8, 38, 0),
                'route': [[37.642971, 55.734989], [37.534576, 55.750573]],
                'classes': ['econom'],
            },
        },
    }

    response = await utils.make_match_request(taxi_order_offers, request)
    assert response.status_code == 200

    if use_mdb_mongo:
        db_offer = mongodb.order_offers_mdb.find_one({'_id': offer_id})
    else:
        db_offer = mongodb.order_offers.find_one({'_id': offer_id})

    response_json = bson.BSON.decode(response.content)
    assert response_json == {'result': 'match', 'document': db_offer}

    metrics = await taxi_order_offers_monitor.get_metrics()
    if use_mdb_mongo:
        assert metrics['match-offer-mdb-by-offer-id-matched'] == 1
    else:
        assert metrics['match-offer-lxc-by-offer-id-matched'] == 1


@pytest.mark.parametrize(
    'use_mdb_mongo, offer_id',
    [
        pytest.param(False, OFFER_ID_MDB),
        pytest.param(True, OFFER_ID_LXC, marks=MATCH_BY_MDB_MONGO_MARKS),
    ],
)
async def test_mismatch_by_offer_id(
        taxi_order_offers,
        taxi_order_offers_monitor,
        mongodb,
        use_mdb_mongo,
        offer_id,
):
    await taxi_order_offers.tests_control(reset_metrics=True)

    request = {
        'filters': {
            'offer_id': offer_id,
            'user_id': USER_ID,
            'order': {
                'due': datetime.datetime(2021, 10, 20, 8, 38, 0),
                'route': [[37.642971, 55.734989], [37.534576, 55.750573]],
            },
        },
    }

    response = await utils.make_match_request(taxi_order_offers, request)
    assert response.status_code == 200

    response_json = bson.BSON.decode(response.content)
    assert response_json == {'result': 'mismatch'}

    metrics = await taxi_order_offers_monitor.get_metrics()
    if use_mdb_mongo:
        assert metrics['match-offer-mdb-by-offer-id-not-matched'] == 1
    else:
        assert metrics['match-offer-lxc-by-offer-id-not-matched'] == 1


@pytest.mark.parametrize(
    'use_mdb_mongo, expected_offer_id',
    [
        pytest.param(False, OFFER_ID_LXC),
        pytest.param(True, OFFER_ID_MDB, marks=MATCH_BY_MDB_MONGO_MARKS),
    ],
)
async def test_match_by_user_id(
        taxi_order_offers,
        taxi_order_offers_monitor,
        mongodb,
        use_mdb_mongo,
        expected_offer_id,
):
    await taxi_order_offers.tests_control(reset_metrics=True)

    request = {
        'filters': {
            'user_id': USER_ID,
            'order': {
                'due': datetime.datetime(2021, 10, 20, 8, 38, 0),
                'route': [[37.642971, 55.734989], [37.534576, 55.750573]],
                'classes': ['econom'],
            },
        },
    }

    response = await utils.make_match_request(taxi_order_offers, request)
    assert response.status_code == 200

    if use_mdb_mongo:
        db_offer = mongodb.order_offers_mdb.find_one(
            {'_id': expected_offer_id},
        )
    else:
        db_offer = mongodb.order_offers.find_one({'_id': expected_offer_id})

    response_json = bson.BSON.decode(response.content)
    assert response_json == {'result': 'match', 'document': db_offer}

    metrics = await taxi_order_offers_monitor.get_metrics()
    if use_mdb_mongo:
        assert metrics['match-offer-mdb-by-user-id-matched'] == 1
    else:
        assert metrics['match-offer-lxc-by-user-id-matched'] == 1


@pytest.mark.filldb(order_offers='same_created')
@pytest.mark.filldb(order_offers_mdb='same_created')
@pytest.mark.parametrize(
    'use_mdb_mongo',
    [pytest.param(False), pytest.param(True, marks=MATCH_BY_MDB_MONGO_MARKS)],
)
async def test_match_by_user_id_sort_order(
        taxi_order_offers, mongodb, use_mdb_mongo,
):
    request = {
        'filters': {
            'user_id': USER_ID,
            'order': {
                'due': datetime.datetime(2021, 10, 20, 8, 38, 0),
                'route': [[37.642971, 55.734989], [37.534576, 55.750573]],
                'classes': ['econom'],
            },
        },
    }

    response = await utils.make_match_request(taxi_order_offers, request)
    assert response.status_code == 200
    if use_mdb_mongo:
        db_offer = mongodb.order_offers_mdb.find_one({'_id': 'bbb'})
    else:
        db_offer = mongodb.order_offers.find_one({'_id': 'bbb'})
    response_json = bson.BSON.decode(response.content)
    assert response_json == {'result': 'match', 'document': db_offer}
