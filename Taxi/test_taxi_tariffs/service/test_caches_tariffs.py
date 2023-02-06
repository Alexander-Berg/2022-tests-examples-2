# pylint: disable=redefined-outer-name
# pylint: disable=protected-access

import datetime

import bson
import pytest


SETTINGS = {'memoize_time': 300, 'delay': 30}


@pytest.fixture
def cache_handler(db):
    from taxi_tariffs.caches import tariffs
    return tariffs.TariffsHandler(db, SETTINGS)


async def test_base(db, cache_handler):
    now = datetime.datetime.utcnow()

    # empty
    await cache_handler.refresh_cache()
    assert not cache_handler._cache.tariffs
    assert not cache_handler._cache.category_ids

    # insert few tariffs
    _id1 = bson.ObjectId()
    await db.tariffs.insert_one(
        {
            '_id': _id1,
            'home_zone': 'moscow',
            'date_from': now - datetime.timedelta(days=2),
            'date_to': now - datetime.timedelta(days=1),
            'categories': [
                {'id': 'cat_id1_1', 'name': 'econom'},
                {'id': 'cat_id1_2', 'name': 'comfort'},
            ],
        },
    )

    _id2 = bson.ObjectId()
    await db.tariffs.insert_one(
        {
            '_id': _id2,
            'home_zone': 'moscow',
            'date_from': now - datetime.timedelta(days=1),
            'categories': [
                {'id': 'cat_id2_1', 'name': 'econom'},
                {'id': 'cat_id2_2', 'name': 'econom'},
            ],
        },
    )

    _id3 = bson.ObjectId()
    await db.tariffs.insert_one(
        {
            '_id': _id3,
            'home_zone': 'balaha',
            'date_from': now - datetime.timedelta(days=1),
            'categories': [
                {'id': 'cat_id3_1', 'name': 'econom'},
                {'id': 'cat_id3_2', 'name': 'ultima'},
            ],
        },
    )

    await cache_handler.refresh_cache()
    assert cache_handler._cache.tariffs.keys() == {str(_id2), str(_id3)}
    assert cache_handler._cache.category_ids == {
        'cat_id2_1': str(_id2),
        'cat_id2_2': str(_id2),
        'cat_id3_1': str(_id3),
        'cat_id3_2': str(_id3),
    }

    # insert one, remove other
    _id4 = bson.ObjectId()
    await db.tariffs.insert_one(
        {
            '_id': _id4,
            'home_zone': 'new_balaha',
            'date_from': now - datetime.timedelta(days=1),
            'categories': [
                {'id': 'cat_id4_1', 'name': 'econom'},
                {'id': 'cat_id4_2', 'name': 'comfort'},
            ],
        },
    )

    await db.tariffs.delete_one({'_id': _id3})

    await cache_handler.refresh_cache()
    assert cache_handler._cache.tariffs.keys() == {str(_id2), str(_id4)}
    assert cache_handler._cache.category_ids == {
        'cat_id2_1': str(_id2),
        'cat_id2_2': str(_id2),
        'cat_id4_1': str(_id4),
        'cat_id4_2': str(_id4),
    }

    # modify one
    await db.tariffs.update_one(
        {'home_zone': 'new_balaha'},
        {'$set': {'date_to': now - datetime.timedelta(seconds=1)}},
    )
    _id5 = bson.ObjectId()
    await db.tariffs.insert_one(
        {
            '_id': _id5,
            'home_zone': 'new_balaha',
            'date_from': now - datetime.timedelta(seconds=1),
            'categories': [
                {'id': 'cat_id5_1', 'name': 'econom'},
                {'id': 'cat_id5_2', 'name': 'comfort'},
            ],
        },
    )

    await cache_handler.refresh_cache()
    assert cache_handler._cache.tariffs.keys() == {str(_id2), str(_id5)}
    assert cache_handler._cache.category_ids == {
        'cat_id2_1': str(_id2),
        'cat_id2_2': str(_id2),
        'cat_id5_1': str(_id5),
        'cat_id5_2': str(_id5),
    }
