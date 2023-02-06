# pylint: disable=protected-access,redefined-outer-name,unused-variable

import copy
import operator

import pytest


@pytest.fixture
def mongodb_collections():
    return ['order_proc']


async def test_save(db):
    order_id = '46dcc06602b14fca8a438762681bf474'
    expected = {
        '_id': '46dcc06602b14fca8a438762681bf474',
        'foo': 'bar',
        '_shard_id': 0,
    }

    await db.order_proc.save({'_id': order_id, 'foo': 'bar'})
    result = await db.order_proc.find_one(order_id)

    assert result == expected


async def test_save_fail(db):
    with pytest.raises(ValueError):
        await db.order_proc.save({'foo': 'bar'})


async def test_order_proc_insert(db):
    order_id_1 = '46dcc06602b15fca8a438762681bf474'
    order_id_2 = '46dcc06602b16fca8a438762681bf474'
    expected = [
        {
            '_id': '46dcc06602b15fca8a438762681bf474',
            'foo': 'bar',
            '_shard_id': 1,
        },
        {
            '_id': '46dcc06602b16fca8a438762681bf474',
            'baz': 'quux',
            '_shard_id': 2,
        },
    ]

    await db.order_proc.remove()
    await db.order_proc.insert({'_id': order_id_1, 'foo': 'bar'})
    await db.order_proc.insert([{'_id': order_id_2, 'baz': 'quux'}])
    result = await db.order_proc.find().to_list(None)

    assert sorted(result, key=operator.itemgetter('_id')) == expected


async def test_order_proc_insert_fail(db):
    with pytest.raises(ValueError):
        await db.order_proc.insert({'foo': 'bar'})
    with pytest.raises(ValueError):
        await db.order_proc.insert([{'foo': 'bar'}])
    with pytest.raises(ValueError):
        await db.order_proc.insert(({'foo': 'bar'},))


@pytest.mark.parametrize(
    'query,expected_query',
    [
        (
            {'_id': '46dcc06602b17fca8a438762681bf474'},
            {'_id': '46dcc06602b17fca8a438762681bf474', '_shard_id': 3},
        ),
        (
            {'candidates.alias_id': '26d6408790eb7a279f15c564560584be'},
            {
                'candidates.alias_id': '26d6408790eb7a279f15c564560584be',
                '_shard_id': 3,
            },
        ),
        (
            {'aliases.id': '26d6408790eb7a279f15c564560584be'},
            {'aliases.id': '26d6408790eb7a279f15c564560584be', '_shard_id': 3},
        ),
        (
            {'performer.alias_id': '26d6408790eb7a279f15c564560584be'},
            {
                'performer.alias_id': '26d6408790eb7a279f15c564560584be',
                '_shard_id': 3,
            },
        ),
        (
            {'reorder.id': '4323a92bfd897146982999e25f2e720f'},
            {'reorder.id': '4323a92bfd897146982999e25f2e720f', '_shard_id': 3},
        ),
    ],
)
async def test_update(query, expected_query, db, patch):
    queries = []
    original_update = db.order_proc._collection.update

    @patch('motor.motor_asyncio.AsyncIOMotorCollection.update')
    def update(spec, *args, **kwargs):
        queries.append(spec)
        return original_update(spec, *args, **kwargs)

    await db.order_proc.update(query, {'$set': {'foo': 'bar'}})

    result = await db.order_proc.find_one('46dcc06602b17fca8a438762681bf474')
    expected_doc = {
        '_id': '46dcc06602b17fca8a438762681bf474',
        '_shard_id': 3,
        'aliases': [{'id': '26d6408790eb7a279f15c564560584be'}],
        'candidates': [{'alias_id': '26d6408790eb7a279f15c564560584be'}],
        'foo': 'bar',
        'performer': {'alias_id': '26d6408790eb7a279f15c564560584be'},
        'reorder': {'id': '4323a92bfd897146982999e25f2e720f'},
    }

    assert result == expected_doc
    assert queries == [expected_query]


@pytest.mark.parametrize(
    'query,expected_query',
    [
        (
            {'_id': '46dcc06602b17fca8a438762681bf474'},
            {'_id': '46dcc06602b17fca8a438762681bf474', '_shard_id': 3},
        ),
        (
            '46dcc06602b17fca8a438762681bf474',
            {'_id': '46dcc06602b17fca8a438762681bf474', '_shard_id': 3},
        ),
        (
            {'candidates.alias_id': '26d6408790eb7a279f15c564560584be'},
            {
                'candidates.alias_id': '26d6408790eb7a279f15c564560584be',
                '_shard_id': 3,
            },
        ),
        (
            {'aliases.id': '26d6408790eb7a279f15c564560584be'},
            {'aliases.id': '26d6408790eb7a279f15c564560584be', '_shard_id': 3},
        ),
        (
            {'performer.alias_id': '26d6408790eb7a279f15c564560584be'},
            {
                'performer.alias_id': '26d6408790eb7a279f15c564560584be',
                '_shard_id': 3,
            },
        ),
        (
            {'reorder.id': '4323a92bfd897146982999e25f2e720f'},
            {'reorder.id': '4323a92bfd897146982999e25f2e720f', '_shard_id': 3},
        ),
    ],
)
async def test_remove(db, query, expected_query, patch):
    queries = []
    original_remove = db.order_proc._collection.remove

    @patch('motor.motor_asyncio.AsyncIOMotorCollection.remove')
    def remove(spec_or_id, *args, **kwargs):
        queries.append(spec_or_id)
        return original_remove(spec_or_id, *args, **kwargs)

    await db.order_proc.remove(query)

    result = await db.order_proc.find_one('46dcc06602b10fca8a438762681bf474')

    assert result is None
    assert queries == [expected_query]


@pytest.mark.parametrize(
    'query,expected_query',
    [
        (
            {'_id': '46dcc06602b17fca8a438762681bf474'},
            {'_id': '46dcc06602b17fca8a438762681bf474', '_shard_id': 3},
        ),
        (
            '46dcc06602b17fca8a438762681bf474',
            {'_id': '46dcc06602b17fca8a438762681bf474', '_shard_id': 3},
        ),
        (
            {'candidates.alias_id': '26d6408790eb7a279f15c564560584be'},
            {
                'candidates.alias_id': '26d6408790eb7a279f15c564560584be',
                '_shard_id': 3,
            },
        ),
        (
            {'aliases.id': '26d6408790eb7a279f15c564560584be'},
            {'aliases.id': '26d6408790eb7a279f15c564560584be', '_shard_id': 3},
        ),
        (
            {'performer.alias_id': '26d6408790eb7a279f15c564560584be'},
            {
                'performer.alias_id': '26d6408790eb7a279f15c564560584be',
                '_shard_id': 3,
            },
        ),
        (
            {'reorder.id': '4323a92bfd897146982999e25f2e720f'},
            {'reorder.id': '4323a92bfd897146982999e25f2e720f', '_shard_id': 3},
        ),
        (
            {'_id': {'$in': ['46dcc06602b17fca8a438762681bf474']}},
            {'_id': {'$in': ['46dcc06602b17fca8a438762681bf474']}},
        ),
    ],
)
async def test_find_one(db, query, expected_query, patch):
    queries = []
    original_find_one = db.order_proc._collection.find_one

    @patch('motor.motor_asyncio.AsyncIOMotorCollection.find_one')
    def find_one(spec_or_id, *args, **kwargs):
        queries.append(spec_or_id)
        return original_find_one(spec_or_id, *args, **kwargs)

    result = await db.order_proc.find_one(query)
    expected_doc = {
        '_id': '46dcc06602b17fca8a438762681bf474',
        '_shard_id': 3,
        'aliases': [{'id': '26d6408790eb7a279f15c564560584be'}],
        'candidates': [{'alias_id': '26d6408790eb7a279f15c564560584be'}],
        'performer': {'alias_id': '26d6408790eb7a279f15c564560584be'},
        'reorder': {'id': '4323a92bfd897146982999e25f2e720f'},
    }

    assert result == expected_doc
    assert queries == [expected_query]


@pytest.mark.parametrize(
    'query,expected_query',
    [
        (
            {'_id': '46dcc06602b17fca8a438762681bf474'},
            {'_id': '46dcc06602b17fca8a438762681bf474', '_shard_id': 3},
        ),
        (
            {'candidates.alias_id': '26d6408790eb7a279f15c564560584be'},
            {
                'candidates.alias_id': '26d6408790eb7a279f15c564560584be',
                '_shard_id': 3,
            },
        ),
        (
            {'aliases.id': '26d6408790eb7a279f15c564560584be'},
            {'aliases.id': '26d6408790eb7a279f15c564560584be', '_shard_id': 3},
        ),
        (
            {'performer.alias_id': '26d6408790eb7a279f15c564560584be'},
            {
                'performer.alias_id': '26d6408790eb7a279f15c564560584be',
                '_shard_id': 3,
            },
        ),
        (
            {'reorder.id': '4323a92bfd897146982999e25f2e720f'},
            {'reorder.id': '4323a92bfd897146982999e25f2e720f', '_shard_id': 3},
        ),
    ],
)
async def test_find_one_and_update(query, expected_query, db, patch):
    queries = []
    original_find_one_and_update = (
        db.order_proc._collection.find_one_and_update
    )

    @patch('motor.motor_asyncio.AsyncIOMotorCollection.find_one_and_update')
    def find_one_and_update(spec_or_id, *args, **kwargs):
        queries.append(spec_or_id)
        return original_find_one_and_update(spec_or_id, *args, **kwargs)

    returned_doc = await db.order_proc.find_one_and_update(
        query, {'$set': {'foo': 'bar'}},
    )
    result_doc = await db.order_proc.find_one(
        '46dcc06602b17fca8a438762681bf474',
    )
    expected_returned_doc = {
        '_id': '46dcc06602b17fca8a438762681bf474',
        '_shard_id': 3,
        'aliases': [{'id': '26d6408790eb7a279f15c564560584be'}],
        'candidates': [{'alias_id': '26d6408790eb7a279f15c564560584be'}],
        'performer': {'alias_id': '26d6408790eb7a279f15c564560584be'},
        'reorder': {'id': '4323a92bfd897146982999e25f2e720f'},
    }
    expected_result_doc = copy.copy(expected_returned_doc)
    expected_result_doc['foo'] = 'bar'

    assert returned_doc == expected_returned_doc
    assert result_doc == expected_result_doc
    assert queries == [expected_query]


@pytest.mark.parametrize(
    'query,expected_query',
    [
        (
            {'_id': '46dcc06602b17fca8a438762681bf474'},
            {'_id': '46dcc06602b17fca8a438762681bf474', '_shard_id': 3},
        ),
        (
            {'candidates.alias_id': '26d6408790eb7a279f15c564560584be'},
            {
                'candidates.alias_id': '26d6408790eb7a279f15c564560584be',
                '_shard_id': 3,
            },
        ),
        (
            {'aliases.id': '26d6408790eb7a279f15c564560584be'},
            {'aliases.id': '26d6408790eb7a279f15c564560584be', '_shard_id': 3},
        ),
        (
            {'performer.alias_id': '26d6408790eb7a279f15c564560584be'},
            {
                'performer.alias_id': '26d6408790eb7a279f15c564560584be',
                '_shard_id': 3,
            },
        ),
        (
            {'reorder.id': '4323a92bfd897146982999e25f2e720f'},
            {'reorder.id': '4323a92bfd897146982999e25f2e720f', '_shard_id': 3},
        ),
    ],
)
async def test_find_and_modify(query, expected_query, db, patch):
    queries = []
    original_find_and_modify = db.order_proc._collection.find_and_modify

    @patch('motor.motor_asyncio.AsyncIOMotorCollection.find_and_modify')
    def find_and_modify(query, *args, **kwargs):
        queries.append(query)
        return original_find_and_modify(query, *args, **kwargs)

    returned_doc = await db.order_proc.find_and_modify(
        query, {'$set': {'foo': 'bar'}},
    )
    result_doc = await db.order_proc.find_one(
        '46dcc06602b17fca8a438762681bf474',
    )
    expected_returned_doc = {
        '_id': '46dcc06602b17fca8a438762681bf474',
        '_shard_id': 3,
        'aliases': [{'id': '26d6408790eb7a279f15c564560584be'}],
        'candidates': [{'alias_id': '26d6408790eb7a279f15c564560584be'}],
        'performer': {'alias_id': '26d6408790eb7a279f15c564560584be'},
        'reorder': {'id': '4323a92bfd897146982999e25f2e720f'},
    }
    expected_result_doc = copy.copy(expected_returned_doc)
    expected_result_doc['foo'] = 'bar'

    assert returned_doc == expected_returned_doc
    assert result_doc == expected_result_doc
    assert queries == [expected_query]


@pytest.mark.filldb(order_proc='test_bulk')
async def test_unordered_bulk_op(db):
    expected = [
        {'_id': '29f21754786f71d2a258710e3d494f71', '_shard_id': 3},
        {
            '_id': '41e720f9520d4fb8a75eb89258613997',
            '_shard_id': 0,
            'foo': 'bar',
        },
        {
            '_id': 'ed4dfbbb302c3ee28e90e8dc12a88086',
            '_shard_id': 7,
            'foo': 'bar',
        },
    ]
    bulk = db.order_proc.initialize_unordered_bulk_op()
    await _test_bulk(db, bulk, expected)


@pytest.mark.filldb(order_proc='test_bulk')
async def test_ordered_bulk_op(db):
    expected = [
        {'_id': '29f21754786f71d2a258710e3d494f71', '_shard_id': 3},
        {
            '_id': '41e720f9520d4fb8a75eb89258613997',
            '_shard_id': 0,
            'foo': 'bar',
        },
        {
            '_id': 'ed4dfbbb302c3ee28e90e8dc12a88086',
            '_shard_id': 7,
            'foo': 'bar',
        },
    ]
    bulk = db.order_proc.initialize_ordered_bulk_op()
    await _test_bulk(db, bulk, expected)


async def _test_bulk(db, proc_bulk, expected):
    proc_bulk.insert({'_id': '29f21754786f71d2a258710e3d494f71'})
    proc_bulk.find({'_id': 'ed4dfbbb302c3ee28e90e8dc12a88086'}).update(
        {'$set': {'foo': 'bar'}},
    )
    proc_bulk.find(
        {'_id': '41e720f9520d4fb8a75eb89258613997'},
    ).upsert().update({'$set': {'foo': 'bar'}})

    await proc_bulk.execute()

    docs = await db.order_proc.find().to_list(None)

    assert sorted(docs, key=operator.itemgetter('_id')) == expected
