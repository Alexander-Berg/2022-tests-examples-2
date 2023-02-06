import pymongo
import pytest


@pytest.mark.asyncio
async def test_ping(mongo: pymongo.MongoClient):
    result = mongo.admin.command('ping')
    assert result['ok'] == 1.0


@pytest.mark.asyncio
async def test_insert_one(mongo: pymongo.MongoClient):
    test_db = mongo['test_db']
    test_collection = test_db['test_collection']
    test_collection.insert_one({
        'key1': 'value1',
        'key2': 'value2'
    })

    items = list(test_collection.find({}))

    assert len(items) == 1
    assert items[0].get('key1') == 'value1'
