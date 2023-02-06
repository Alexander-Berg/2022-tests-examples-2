import bson
import pytest


@pytest.fixture
def mongodb_collections():
    return ['drivers']


async def test_save(db):
    driver_id = '100500_7d7a94a3fee84eda95de736b5e000000'

    await db.drivers.save(
        {
            '_id': driver_id,
            'first_name': 'Igor',
            'updated_ts': bson.timestamp.Timestamp(0, 0),
        },
    )
    expected = {
        '_id': '100500_7d7a94a3fee84eda95de736b5e000000',
        'first_name': 'Igor',
    }
    result = await db.drivers.find_one(driver_id)
    expected['updated_ts'] = result['updated_ts']
    assert expected == result


async def test_insert(db):
    driver_1_id = '100500_7d7a94a3fee84eda95de736b5e000001'
    driver_2_id = '100500_7d7a94a3fee84eda95de736b5e000002'
    expectations = [
        {
            '_id': '100500_7d7a94a3fee84eda95de736b5e000001',
            'first_name': 'Oleg',
        },
        {
            '_id': '100500_7d7a94a3fee84eda95de736b5e000002',
            'first_name': 'Peter',
        },
    ]
    await db.drivers.remove()
    await db.drivers.insert(
        {
            '_id': driver_1_id,
            'first_name': 'Oleg',
            'updated_ts': bson.timestamp.Timestamp(0, 0),
        },
    )
    await db.drivers.insert(
        [
            {
                '_id': driver_2_id,
                'first_name': 'Peter',
                'updated_ts': bson.timestamp.Timestamp(0, 0),
            },
        ],
    )
    results = [
        await db.drivers.find_one(driver_1_id),
        await db.drivers.find_one(driver_2_id),
    ]
    for result, expected in zip(results, expectations):
        expected['updated_ts'] = result['updated_ts']
        assert expected == result


async def test_insert_one(db):
    driver_1_id = '100500_7d7a94a3fee84eda95de736b5e000001'
    expected = {
        '_id': '100500_7d7a94a3fee84eda95de736b5e000001',
        'first_name': 'Oleg',
    }
    await db.drivers.remove()
    await db.drivers.insert_one(
        {
            '_id': driver_1_id,
            'first_name': 'Oleg',
            'updated_ts': bson.timestamp.Timestamp(0, 0),
        },
    )
    result = await db.drivers.find_one(driver_1_id)
    expected['updated_ts'] = result['updated_ts']
    assert expected == result


async def test_insert_many(db):
    driver_1_id = '100500_7d7a94a3fee84eda95de736b5e000001'
    driver_2_id = '100500_7d7a94a3fee84eda95de736b5e000002'
    expectations = [
        {
            '_id': '100500_7d7a94a3fee84eda95de736b5e000001',
            'first_name': 'Oleg',
        },
        {
            '_id': '100500_7d7a94a3fee84eda95de736b5e000002',
            'first_name': 'Peter',
        },
    ]
    await db.drivers.remove()
    await db.drivers.insert_many(
        [
            {
                '_id': driver_2_id,
                'first_name': 'Peter',
                'updated_ts': bson.timestamp.Timestamp(0, 0),
            },
            {
                '_id': driver_1_id,
                'first_name': 'Oleg',
                'updated_ts': bson.timestamp.Timestamp(0, 0),
            },
        ],
    )
    results = [
        await db.drivers.find_one(driver_1_id),
        await db.drivers.find_one(driver_2_id),
    ]
    for result, expected in zip(results, expectations):
        expected['updated_ts'] = result['updated_ts']
        assert expected == result


async def test_update(db):
    driver_1_id = '100500_7d7a94a3fee84eda95de736b5e000001'
    query = {'_id': '100500_7d7a94a3fee84eda95de736b5e000001'}
    update = {
        '$set': {'last_name': 'Smith'},
        '$currentDate': {'updated_ts': {'$type': 'timestamp'}},
    }
    expected = {
        '_id': '100500_7d7a94a3fee84eda95de736b5e000001',
        'db_id': '6fefc330ceea40358924705a6990724b',
        'locale': 'en',
        'taximeter_version': '8.71',
        'uuid': '7d7a94a3fee84eda95de736b5e000001',
        'last_name': 'Smith',
    }

    await db.drivers.update(query, update)
    result = await db.drivers.find_one(driver_1_id)
    expected['updated_ts'] = result['updated_ts']
    assert expected == result


async def test_update_document(db):
    driver_1_id = '100500_7d7a94a3fee84eda95de736b5e000001'
    expected = {
        '_id': '100500_7d7a94a3fee84eda95de736b5e000001',
        'first_name': 'Oleg',
    }
    query = {'_id': '100500_7d7a94a3fee84eda95de736b5e000001'}
    await db.drivers.update(
        query,
        {'first_name': 'Oleg', 'updated_ts': bson.timestamp.Timestamp(0, 0)},
    )
    result = await db.drivers.find_one(driver_1_id)
    expected['updated_ts'] = result['updated_ts']
    assert expected == result


async def test_update_one(db):
    driver_1_id = '100500_7d7a94a3fee84eda95de736b5e000001'
    query = {'_id': '100500_7d7a94a3fee84eda95de736b5e000001'}
    update = {
        '$set': {'first_name': 'Bobby'},
        '$currentDate': {'updated_ts': {'$type': 'timestamp'}},
    }
    expected = {
        '_id': '100500_7d7a94a3fee84eda95de736b5e000001',
        'db_id': '6fefc330ceea40358924705a6990724b',
        'locale': 'en',
        'taximeter_version': '8.71',
        'uuid': '7d7a94a3fee84eda95de736b5e000001',
        'first_name': 'Bobby',
    }

    await db.drivers.update_one(query, update)
    result = await db.drivers.find_one(driver_1_id)
    expected['updated_ts'] = result['updated_ts']
    assert expected == result


async def test_update_many(db):
    driver_1_id = '100500_7d7a94a3fee84eda95de736b5e000001'
    query = {'_id': '100500_7d7a94a3fee84eda95de736b5e000001'}
    update = {
        '$set': {'first_name': 'Johny'},
        '$currentDate': {'updated_ts': {'$type': 'timestamp'}},
    }
    expected = {
        '_id': '100500_7d7a94a3fee84eda95de736b5e000001',
        'db_id': '6fefc330ceea40358924705a6990724b',
        'locale': 'en',
        'taximeter_version': '8.71',
        'uuid': '7d7a94a3fee84eda95de736b5e000001',
        'first_name': 'Johny',
    }

    await db.drivers.update_many(query, update)
    result = await db.drivers.find_one(driver_1_id)
    expected['updated_ts'] = result['updated_ts']
    assert expected == result


async def test_replace_one(db):
    driver_id = '100500_7d7a94a3fee84eda95de736b5e000000'

    await db.drivers.replace_one(
        {'_id': driver_id},
        {
            '_id': driver_id,
            'first_name': 'Oleg',
            'updated_ts': bson.timestamp.Timestamp(0, 0),
        },
    )
    expected = {
        '_id': '100500_7d7a94a3fee84eda95de736b5e000000',
        'first_name': 'Oleg',
    }
    result = await db.drivers.find_one(driver_id)
    expected['updated_ts'] = result['updated_ts']
    assert expected == result


async def test_find_one_and_update(db):
    driver_1_id = '100500_7d7a94a3fee84eda95de736b5e000001'
    query = {'_id': '100500_7d7a94a3fee84eda95de736b5e000001'}
    update = {
        '$set': {'first_name': 'Bobby'},
        '$currentDate': {'updated_ts': {'$type': 'timestamp'}},
    }
    expected = {
        '_id': '100500_7d7a94a3fee84eda95de736b5e000001',
        'db_id': '6fefc330ceea40358924705a6990724b',
        'locale': 'en',
        'taximeter_version': '8.71',
        'uuid': '7d7a94a3fee84eda95de736b5e000001',
        'first_name': 'Bobby',
    }

    await db.drivers.find_one_and_update(query, update)
    result = await db.drivers.find_one(driver_1_id)
    expected['updated_ts'] = result['updated_ts']
    assert expected == result


async def test_find_one_and_replace(db):
    driver_1_id = '100500_7d7a94a3fee84eda95de736b5e000001'
    query = {'_id': '100500_7d7a94a3fee84eda95de736b5e000001'}
    expected = {
        '_id': '100500_7d7a94a3fee84eda95de736b5e000001',
        'first_name': 'Oleg',
    }
    await db.drivers.find_one_and_replace(
        query,
        {'first_name': 'Oleg', 'updated_ts': bson.timestamp.Timestamp(0, 0)},
    )
    result = await db.drivers.find_one(driver_1_id)
    expected['updated_ts'] = result['updated_ts']
    assert expected == result


async def test_find_and_modify(db):
    driver_1_id = '100500_7d7a94a3fee84eda95de736b5e000001'
    query = {'_id': '100500_7d7a94a3fee84eda95de736b5e000001'}
    update = {
        '$set': {'first_name': 'Bobby'},
        '$currentDate': {'updated_ts': {'$type': 'timestamp'}},
    }
    expected = {
        '_id': '100500_7d7a94a3fee84eda95de736b5e000001',
        'db_id': '6fefc330ceea40358924705a6990724b',
        'locale': 'en',
        'taximeter_version': '8.71',
        'uuid': '7d7a94a3fee84eda95de736b5e000001',
        'first_name': 'Bobby',
    }

    await db.drivers.find_and_modify(query, update)
    result = await db.drivers.find_one(driver_1_id)
    expected['updated_ts'] = result['updated_ts']
    assert expected == result

    expected = {
        '_id': '100500_7d7a94a3fee84eda95de736b5e000001',
        'first_name': 'Oleg',
    }
    await db.drivers.find_and_modify(
        query,
        {'first_name': 'Oleg', 'updated_ts': bson.timestamp.Timestamp(0, 0)},
    )
    result = await db.drivers.find_one(driver_1_id)
    expected['updated_ts'] = result['updated_ts']
    assert expected == result


async def test_unordered_bulk_op(db):
    bulk = db.drivers.initialize_unordered_bulk_op()
    await _test_bulk(db, bulk)


async def test_ordered_bulk_op(db):
    bulk = db.drivers.initialize_ordered_bulk_op()
    await _test_bulk(db, bulk)


async def _test_bulk(db, bulk):
    driver_1_id = '100500_7d7a94a3fee84eda95de736b5e000001'
    driver_2_id = '100500_7d7a94a3fee84eda95de736b5e000002'
    expectations = [
        {
            '_id': '100500_7d7a94a3fee84eda95de736b5e000001',
            'first_name': 'Oleg',
        },
        {
            '_id': '100500_7d7a94a3fee84eda95de736b5e000002',
            'first_name': 'Peter',
        },
    ]
    await db.drivers.remove()
    bulk.insert(
        {
            '_id': driver_1_id,
            'first_name': 'Oleg',
            'updated_ts': bson.timestamp.Timestamp(0, 0),
        },
    )
    bulk.insert(
        {
            '_id': driver_2_id,
            'first_name': 'Peter',
            'updated_ts': bson.timestamp.Timestamp(0, 0),
        },
    )
    await bulk.execute()
    results = [
        await db.drivers.find_one(driver_1_id),
        await db.drivers.find_one(driver_2_id),
    ]
    for result, expected in zip(results, expectations):
        expected['updated_ts'] = result['updated_ts']
        assert expected == result
