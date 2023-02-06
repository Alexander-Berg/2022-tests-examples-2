# pylint: disable=redefined-outer-name
# pylint: disable=protected-access
import copy
import datetime
import uuid

import bson
import pytest

# pylint: disable=import-only-modules
from corp_tariffs.caches.tariffs import CacheType

NOW = datetime.datetime.utcnow().replace(microsecond=0)
SETTINGS = {'get_by_id_memoize_time': 0, 'get_by_zone_memoize_time': 0}


def gen_uuid():
    return uuid.uuid4().hex


@pytest.fixture
def cache_handler(web_context):
    from corp_tariffs.caches import tariffs
    return tariffs.TariffsHandler(web_context, SETTINGS)


async def test_empty(db, cache_handler, individual_tariffs_mockserver):
    individual_tariffs_mockserver.tariffs_context.set_list_response([])
    await cache_handler.refresh_cache()
    assert not cache_handler._cache[CacheType.MongoCache].tariffs
    assert not cache_handler._cache[CacheType.MongoCache].home_zones
    assert not cache_handler._cache[CacheType.Cache].tariffs
    assert not cache_handler._cache[CacheType.Cache].home_zones


@pytest.mark.parametrize('refresh_disabled', [False, True])
async def test_refresh_disabled(
        web_context, db, cache_handler, refresh_disabled,
):
    web_context.config.CORP_TARIFFS_CACHE_SETTINGS = {
        'taxi_tariffs': {'refresh_disabled': refresh_disabled},
    }

    await db.tariffs.insert_one(
        {
            '_id': bson.ObjectId(),
            'home_zone': 'moscow',
            'date_from': NOW - datetime.timedelta(days=5),
            'categories': [
                {
                    'id': gen_uuid(),
                    'name': 'econom',
                    'category_type': 'application',
                },
            ],
        },
    )
    await cache_handler.refresh_cache()

    assert (
        bool(cache_handler._cache[CacheType.MongoCache].tariffs)
        != refresh_disabled
    )
    assert (
        bool(cache_handler._cache[CacheType.MongoCache].home_zones)
        != refresh_disabled
    )


@pytest.mark.parametrize(
    'disabled',
    [
        pytest.param(False, id='cache_enabled'),
        pytest.param(True, id='cache_disabled'),
    ],
)
@pytest.mark.parametrize(
    'refresh_disabled',
    [
        pytest.param(False, id='refresh_enabled'),
        pytest.param(True, id='refresh_disabled'),
    ],
)
async def test_get_by_id(
        web_context, db, cache_handler, disabled, refresh_disabled,
):
    web_context.config.CORP_TARIFFS_CACHE_SETTINGS = {
        'taxi_tariffs': {
            'disabled': disabled,
            'refresh_disabled': refresh_disabled,
        },
    }

    _id1 = bson.ObjectId()
    category_id = gen_uuid()

    await db.tariffs.insert_one(
        {
            '_id': _id1,
            'home_zone': 'moscow',
            'date_from': NOW - datetime.timedelta(days=5),
            'categories': [
                {
                    'id': category_id,
                    'name': 'econom',
                    'category_type': 'application',
                },
                {
                    'id': gen_uuid(),
                    'name': 'econom',
                    'category_type': 'call_center',
                },
            ],
        },
    )

    await cache_handler.refresh_cache()
    tariff = await cache_handler.get_by_id(str(_id1))
    assert tariff == {
        '_id': str(_id1),
        'categories': [
            {
                'disable_surge': False,
                'id': category_id,
                'category_name': 'econom',
                'category_type': 'application',
            },
        ],
        'home_zone': 'moscow',
    }


@pytest.mark.parametrize(
    'disabled',
    [
        pytest.param(False, id='cache_enabled'),
        pytest.param(True, id='cache_disabled'),
    ],
)
@pytest.mark.parametrize(
    'refresh_disabled',
    [
        pytest.param(False, id='refresh_enabled'),
        pytest.param(True, id='refresh_disabled'),
    ],
)
async def test_get_by_zone(
        web_context, db, cache_handler, disabled, refresh_disabled,
):
    web_context.config.CORP_TARIFFS_CACHE_SETTINGS = {
        'taxi_tariffs': {
            'disabled': disabled,
            'refresh_disabled': refresh_disabled,
        },
    }

    await db.tariffs.insert_one(
        {
            '_id': bson.ObjectId(),
            'home_zone': 'moscow',
            'date_from': NOW - datetime.timedelta(days=5),
            'date_to': NOW - datetime.timedelta(days=4),
            'categories': [
                {
                    'id': gen_uuid(),
                    'name': 'econom',
                    'category_type': 'application',
                },
                {
                    'id': gen_uuid(),
                    'name': 'econom',
                    'category_type': 'call_center',
                },
            ],
        },
    )

    _id1 = bson.ObjectId()
    category_id = gen_uuid()

    await db.tariffs.insert_one(
        {
            '_id': _id1,
            'home_zone': 'moscow',
            'date_from': NOW - datetime.timedelta(days=4),
            'categories': [
                {
                    'id': category_id,
                    'name': 'econom',
                    'category_type': 'application',
                },
                {
                    'id': gen_uuid(),
                    'name': 'econom',
                    'category_type': 'call_center',
                },
            ],
        },
    )

    await cache_handler.refresh_cache()
    tariff = await cache_handler.get_by_zone('moscow')
    assert tariff == {
        '_id': str(_id1),
        'categories': [
            {
                'disable_surge': False,
                'id': category_id,
                'category_name': 'econom',
                'category_type': 'application',
            },
        ],
        'home_zone': 'moscow',
    }


@pytest.mark.now(NOW.isoformat())
async def test_base(db, cache_handler):
    _id1 = bson.ObjectId()
    await db.tariffs.insert_one(
        {
            '_id': _id1,
            'home_zone': 'moscow',
            'date_from': NOW - datetime.timedelta(days=5),
            'date_to': NOW - datetime.timedelta(days=4),
            'categories': [
                {
                    'id': gen_uuid(),
                    'name': 'econom',
                    'category_type': 'application',
                },
            ],
        },
    )

    _id2 = bson.ObjectId()
    await db.tariffs.insert_one(
        {
            '_id': _id2,
            'home_zone': 'moscow',
            'date_from': NOW - datetime.timedelta(days=4),
            'date_to': NOW - datetime.timedelta(days=1),
            'categories': [
                {
                    'id': gen_uuid(),
                    'name': 'econom',
                    'category_type': 'application',
                },
            ],
        },
    )

    _id3 = bson.ObjectId()
    await db.tariffs.insert_one(
        {
            '_id': _id3,
            'home_zone': 'moscow',
            'date_from': NOW - datetime.timedelta(days=1),
            'categories': [
                {
                    'id': gen_uuid(),
                    'name': 'econom',
                    'category_type': 'application',
                },
            ],
        },
    )

    _id4 = bson.ObjectId()
    await db.tariffs.insert_one(
        {
            '_id': _id4,
            'home_zone': 'balaha',
            'date_from': NOW - datetime.timedelta(days=1),
            'date_to': NOW - datetime.timedelta(seconds=1),
            'categories': [
                {
                    'id': gen_uuid(),
                    'name': 'econom',
                    'category_type': 'application',
                },
            ],
        },
    )

    await cache_handler.refresh_cache()
    assert cache_handler._cache[CacheType.MongoCache].tariffs.keys() == {
        str(_id2),
        str(_id3),
        str(_id4),
    }
    assert cache_handler._cache[CacheType.MongoCache].home_zones == {
        'moscow': str(_id3),
    }


@pytest.mark.now(NOW.isoformat())
async def test_modified(db, cache_handler):
    _id1 = bson.ObjectId()
    await db.tariffs.insert_one(
        {
            '_id': _id1,
            'home_zone': 'moscow',
            'date_from': NOW - datetime.timedelta(days=2),
            'categories': [
                {
                    'id': gen_uuid(),
                    'name': 'econom',
                    'category_type': 'application',
                },
            ],
        },
    )

    await cache_handler.refresh_cache()
    assert cache_handler._cache[CacheType.MongoCache].tariffs.keys() == {
        str(_id1),
    }
    assert cache_handler._cache[CacheType.MongoCache].home_zones == {
        'moscow': str(_id1),
    }

    await db.tariffs.update_one(
        {'_id': _id1},
        {'$set': {'date_to': NOW - datetime.timedelta(seconds=1)}},
    )

    _id2 = bson.ObjectId()
    await db.tariffs.insert_one(
        {
            '_id': _id2,
            'home_zone': 'moscow',
            'date_from': NOW - datetime.timedelta(days=1),
            'categories': [
                {
                    'id': gen_uuid(),
                    'name': 'econom',
                    'category_type': 'application',
                },
            ],
        },
    )

    await cache_handler.refresh_cache()
    assert cache_handler._cache[CacheType.MongoCache].tariffs.keys() == {
        str(_id1),
        str(_id2),
    }
    assert cache_handler._cache[CacheType.MongoCache].home_zones == {
        'moscow': str(_id2),
    }


@pytest.mark.now(NOW.isoformat())
async def test_partially_modified(db, cache_handler):
    _id1 = bson.ObjectId()
    await db.tariffs.insert_one(
        {
            '_id': _id1,
            'home_zone': 'moscow',
            'date_from': NOW - datetime.timedelta(days=2),
            'categories': [
                {
                    'id': gen_uuid(),
                    'name': 'econom',
                    'category_type': 'application',
                },
            ],
        },
    )

    await cache_handler.refresh_cache()
    assert cache_handler._cache[CacheType.MongoCache].tariffs.keys() == {
        str(_id1),
    }
    assert cache_handler._cache[CacheType.MongoCache].home_zones == {
        'moscow': str(_id1),
    }

    await db.tariffs.update_one(
        {'_id': _id1},
        {'$set': {'date_to': NOW - datetime.timedelta(seconds=1)}},
    )

    await cache_handler.refresh_cache()
    assert cache_handler._cache[CacheType.MongoCache].tariffs.keys() == {
        str(_id1),
    }
    assert cache_handler._cache[CacheType.MongoCache].home_zones == {}


@pytest.mark.now(NOW.isoformat())
async def test_tariff_lifetime(db, cache_handler):
    _id1 = bson.ObjectId()
    await db.tariffs.insert_one(
        {
            '_id': _id1,
            'home_zone': 'moscow',
            'date_from': NOW - datetime.timedelta(days=2),
            'date_to': NOW - datetime.timedelta(seconds=61),
            'categories': [
                {
                    'id': gen_uuid(),
                    'name': 'econom',
                    'category_type': 'application',
                },
            ],
        },
    )

    await cache_handler.refresh_cache()
    assert cache_handler._cache[CacheType.MongoCache].tariffs.keys() == {
        str(_id1),
    }
    assert cache_handler._cache[CacheType.MongoCache].home_zones == {}


@pytest.mark.now(NOW.isoformat())
@pytest.mark.parametrize(
    'fallback',
    [
        pytest.param(
            'disabled',
            marks=(
                pytest.mark.client_experiments3(
                    file_with_default_response='exp3_fallback_disabled.json',
                ),
            ),
        ),
    ],
)
async def test_cache_with_individual_tariffs(
        web_context,
        cache_handler,
        individual_tariffs_mockserver,
        load_json,
        fallback,
):
    web_context.config.CORP_TARIFFS_INDIVIDUAL_TARIFFS_CACHE_SETTINGS = False

    async def cache_cycle(_id, expected):
        await cache_handler.refresh_cache()
        tariff_by_id = await cache_handler.get_by_id(_id)
        tariff_by_home_zone = await cache_handler.get_by_zone('moscow')
        if expected is not None:
            assert tariff_by_id == expected
            assert tariff_by_home_zone == expected
        else:
            assert tariff_by_id is None
            assert tariff_by_home_zone is None

    tariffs = load_json('individual_tariffs_v1_tariff_list.json')
    expected_tariffs = load_json('expected_tariffs.json')
    # from list response
    individual_tariffs_mockserver.tariffs_context.set_list_response(
        [tariffs[0]],
    )
    individual_tariffs_mockserver.tariffs_context.set_tariff_response(
        tariffs[0],
    )
    await cache_cycle('000000000000000000000001', expected_tariffs[0])

    # add tariff in list response
    individual_tariffs_mockserver.tariffs_context.set_list_response(
        [tariffs[0], tariffs[1]],
    )
    await cache_cycle('5caeed9d1bc8d21af5a07a24', expected_tariffs[1])

    # tariff not found in cache
    individual_tariffs_mockserver.tariffs_context.set_tariff_response(
        tariffs[0],
    )
    individual_tariffs_mockserver.tariffs_context.set_list_response([])
    await cache_cycle('000000000000000000000001', expected_tariffs[0])


@pytest.mark.now('2022-07-4T10:15:00+03:00')
@pytest.mark.parametrize(
    'fallback',
    [
        pytest.param(
            'disabled',
            marks=(
                pytest.mark.client_experiments3(
                    file_with_default_response='exp3_fallback_disabled.json',
                ),
            ),
        ),
    ],
)
async def test_base_with_individual_tariffs(
        web_context,
        cache_handler,
        individual_tariffs_mockserver,
        load_json,
        fallback,
):
    web_context.config.CORP_TARIFFS_INDIVIDUAL_TARIFFS_CACHE_SETTINGS = False

    individual_tariffs_mockserver.tariffs_context.set_list_response(
        load_json('individual_tariffs_v1_tariff_list.json'),
    )

    await cache_handler.refresh_cache()
    assert {*cache_handler._cache[CacheType.Cache].tariffs.keys()} == {
        '000000000000000000000001',
        '5caeed9d1bc8d21af5a07a24',
        '5caeed9d1bc8d21af5a07a25',
    }
    assert cache_handler._cache[CacheType.Cache].home_zones == {
        'moscow': '5caeed9d1bc8d21af5a07a24',
    }


@pytest.mark.now('2019-01-31T14:00:00+00:00')
@pytest.mark.parametrize(
    'fallback',
    [
        pytest.param(
            'disabled',
            marks=(
                pytest.mark.client_experiments3(
                    file_with_default_response='exp3_fallback_disabled.json',
                ),
            ),
        ),
    ],
)
async def test_modified_with_individual_tariffs(
        web_context,
        cache_handler,
        individual_tariffs_mockserver,
        load_json,
        fallback,
):
    web_context.config.CORP_TARIFFS_INDIVIDUAL_TARIFFS_CACHE_SETTINGS = False

    original_tariff = load_json('individual_tariffs_v1_tariff_list.json')[1]
    individual_tariffs_mockserver.tariffs_context.set_list_response(
        [original_tariff],
    )
    id1 = original_tariff['id']
    await cache_handler.refresh_cache()
    assert cache_handler._cache[CacheType.Cache].tariffs.keys() == {id1}
    assert cache_handler._cache[CacheType.Cache].home_zones == {'moscow': id1}

    modified_tariff = copy.deepcopy(original_tariff)
    original_tariff['date_to'] = '2020-01-31T14:00:00+00:00'
    id2 = '5caeed9d1bc8d21af5a07a25'
    modified_tariff['id'] = id2
    individual_tariffs_mockserver.tariffs_context.set_list_response(
        [original_tariff, modified_tariff],
    )
    await cache_handler.refresh_cache()
    assert cache_handler._cache[CacheType.Cache].tariffs.keys() == {id1, id2}
    assert cache_handler._cache[CacheType.Cache].home_zones == {'moscow': id2}
