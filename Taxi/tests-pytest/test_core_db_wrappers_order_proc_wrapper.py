import copy

import pytest

from taxi.conf import settings
from taxi.core import db
from taxi.core.db.wrappers import base_order_wrapper


@pytest.fixture(scope='function')
def order_proc_wrapper_env(monkeypatch):
    def env_setter(shards_queries_enabled):
        monkeypatch.setattr(
            settings,
            'ORDER_PROC_SHARDS_QUERIES_ENABLED',
            shards_queries_enabled,
        )

    return env_setter


@pytest.mark.parametrize('shards_queries_enabled,expected', [
    (False, {'_id': '46dcc06602b14fca8a438762681bf474', 'foo': 'bar'}),
    (
        True,
        {
            '_id': '46dcc06602b14fca8a438762681bf474',
            'foo': 'bar',
            '_shard_id': 0,
        },
    ),
])
@pytest.inline_callbacks
def test_order_proc_collection_wrapper_save(shards_queries_enabled, expected,
                                            order_proc_wrapper_env):
    order_id = '46dcc06602b14fca8a438762681bf474'
    order_proc_wrapper_env(shards_queries_enabled)

    yield db.order_proc.save(
        {
            '_id': order_id,
            'foo': 'bar',
        }
    )
    result = yield db.order_proc.find_one(order_id)

    assert result == expected


@pytest.inline_callbacks
def test_order_proc_collection_wrapper_save_fail(order_proc_wrapper_env):
    order_proc_wrapper_env(True)
    with pytest.raises(ValueError):
        yield db.order_proc.save({'foo': 'bar'})


@pytest.mark.parametrize('shards_queries_enabled,expected', [
    (
        False,
        [
            {'_id': '46dcc06602b15fca8a438762681bf474', 'foo': 'bar'},
            {'_id': '46dcc06602b16fca8a438762681bf474', 'baz': 'quux'},
        ],
    ),
    (
        True,
        [
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
        ],
    ),
])
@pytest.inline_callbacks
def test_order_proc_collection_wrapper_insert(shards_queries_enabled,
                                              expected,
                                              order_proc_wrapper_env):
    order_id_1 = '46dcc06602b15fca8a438762681bf474'
    order_id_2 = '46dcc06602b16fca8a438762681bf474'
    order_proc_wrapper_env(shards_queries_enabled)

    yield db.order_proc.remove()
    yield db.order_proc.insert({'_id': order_id_1, 'foo': 'bar'})
    yield db.order_proc.insert([{'_id': order_id_2, 'baz': 'quux'}])
    result = yield db.order_proc.find().run()

    assert sorted(result) == expected


@pytest.inline_callbacks
def test_order_proc_collection_wrapper_insert_fail(order_proc_wrapper_env):
    order_proc_wrapper_env(True)
    with pytest.raises(ValueError):
        yield db.order_proc.insert({'foo': 'bar'})
    with pytest.raises(ValueError):
        yield db.order_proc.insert([{'foo': 'bar'}])
    with pytest.raises(ValueError):
        yield db.order_proc.insert(({'foo': 'bar'},))


@pytest.mark.parametrize('shards_queries_enabled,query,expected_query', [
    (
        False,
        {'_id': '46dcc06602b17fca8a438762681bf474'},
        {'_id': '46dcc06602b17fca8a438762681bf474'},
    ),
    (
        True,
        {'_id': '46dcc06602b17fca8a438762681bf474'},
        {'_id': '46dcc06602b17fca8a438762681bf474', '_shard_id': 3},
    ),
    (
        True,
        {'candidates.alias_id': '26d6408790eb7a279f15c564560584be'},
        {
            'candidates.alias_id': '26d6408790eb7a279f15c564560584be',
            '_shard_id': 3,
        },
    ),
    (
        True,
        {'aliases.id': '26d6408790eb7a279f15c564560584be'},
        {
            'aliases.id': '26d6408790eb7a279f15c564560584be',
            '_shard_id': 3,
        },
    ),
    (
        True,
        {'performer.alias_id': '26d6408790eb7a279f15c564560584be'},
        {
            'performer.alias_id': '26d6408790eb7a279f15c564560584be',
            '_shard_id': 3,
        },
    ),
])
@pytest.inline_callbacks
def test_order_proc_collection_wrapper_update(shards_queries_enabled,
                                              query, expected_query,
                                              order_proc_wrapper_env, patch):
    queries = []
    original_update = (
        super(base_order_wrapper.BaseOrderCollectionWrapper,
              db.order_proc).update
    )

    @patch('taxi.core.db.classes.BaseCollectionWrapper.update')
    def update(spec, *args, **kwargs):
        queries.append(spec)
        return original_update(spec, *args, **kwargs)

    order_proc_wrapper_env(shards_queries_enabled)

    yield db.order_proc.update(query, {'$set': {'foo': 'bar'}})

    result = yield db.order_proc.find_one('46dcc06602b17fca8a438762681bf474')
    expected_doc = {
        '_id': '46dcc06602b17fca8a438762681bf474',
        '_shard_id': 3,
        'aliases': [
            {'id': '26d6408790eb7a279f15c564560584be'}
        ],
        'candidates': [
            {
                'alias_id': '26d6408790eb7a279f15c564560584be'
            }
        ],
        'foo': 'bar',
        'performer': {
            'alias_id': '26d6408790eb7a279f15c564560584be'
        },
        'reorder': {
            'id': '4323a92bfd897146982999e25f2e720f'
        }
    }

    assert result == expected_doc
    assert queries == [expected_query]


@pytest.mark.parametrize('shards_queries_enabled,query,expected_query', [
    (
        False,
        {'_id': '46dcc06602b17fca8a438762681bf474'},
        {'_id': '46dcc06602b17fca8a438762681bf474'},
    ),
    (
        True,
        {'_id': '46dcc06602b17fca8a438762681bf474'},
        {'_id': '46dcc06602b17fca8a438762681bf474', '_shard_id': 3},
    ),
    (
        False,
        '46dcc06602b17fca8a438762681bf474',
        '46dcc06602b17fca8a438762681bf474',
    ),
    (
        True,
        '46dcc06602b17fca8a438762681bf474',
        {'_id': '46dcc06602b17fca8a438762681bf474', '_shard_id': 3},
    ),
    (
        True,
        {'candidates.alias_id': '26d6408790eb7a279f15c564560584be'},
        {
            'candidates.alias_id': '26d6408790eb7a279f15c564560584be',
            '_shard_id': 3,
        },
    ),
    (
        True,
        {'aliases.id': '26d6408790eb7a279f15c564560584be'},
        {
            'aliases.id': '26d6408790eb7a279f15c564560584be',
            '_shard_id': 3,
        },
    ),
    (
        True,
        {'performer.alias_id': '26d6408790eb7a279f15c564560584be'},
        {
            'performer.alias_id': '26d6408790eb7a279f15c564560584be',
            '_shard_id': 3,
        },
    ),
])
@pytest.inline_callbacks
def test_order_proc_collection_wrapper_remove(shards_queries_enabled,
                                              query, expected_query,
                                              order_proc_wrapper_env, patch):
    queries = []
    original_remove = (
        super(base_order_wrapper.BaseOrderCollectionWrapper,
              db.order_proc).remove
    )

    @patch('taxi.core.db.classes.BaseCollectionWrapper.remove')
    def remove(spec_or_id, *args, **kwargs):
        queries.append(spec_or_id)
        return original_remove(spec_or_id, *args, **kwargs)

    order_proc_wrapper_env(shards_queries_enabled)

    yield db.order_proc.remove(query)

    result = yield db.order_proc.find_one('46dcc06602b10fca8a438762681bf474')

    assert result is None
    assert queries == [expected_query]


@pytest.mark.parametrize('shards_queries_enabled,query,expected_query', [
    (
        False,
        {'_id': '46dcc06602b17fca8a438762681bf474'},
        {'_id': '46dcc06602b17fca8a438762681bf474'},
    ),
    (
        True,
        {'_id': '46dcc06602b17fca8a438762681bf474'},
        {'_id': '46dcc06602b17fca8a438762681bf474', '_shard_id': 3},
    ),
    (
        False,
        '46dcc06602b17fca8a438762681bf474',
        '46dcc06602b17fca8a438762681bf474',
    ),
    (
        True,
        '46dcc06602b17fca8a438762681bf474',
        {'_id': '46dcc06602b17fca8a438762681bf474', '_shard_id': 3},
    ),
    (
        True,
        {'candidates.alias_id': '26d6408790eb7a279f15c564560584be'},
        {
            'candidates.alias_id': '26d6408790eb7a279f15c564560584be',
            '_shard_id': 3,
        },
    ),
    (
        True,
        {'aliases.id': '26d6408790eb7a279f15c564560584be'},
        {
            'aliases.id': '26d6408790eb7a279f15c564560584be',
            '_shard_id': 3,
        },
    ),
    (
        True,
        {'performer.alias_id': '26d6408790eb7a279f15c564560584be'},
        {
            'performer.alias_id': '26d6408790eb7a279f15c564560584be',
            '_shard_id': 3,
        },
    ),
    (
        True,
        {'_id': {'$in': ['46dcc06602b17fca8a438762681bf474']}},
        {'_id': {'$in': ['46dcc06602b17fca8a438762681bf474']}},
    ),
])
@pytest.inline_callbacks
def test_order_proc_collection_wrapper_find_one(shards_queries_enabled,
                                                query, expected_query,
                                                order_proc_wrapper_env, patch):
    queries = []
    original_find_one = (
        super(base_order_wrapper.BaseOrderCollectionWrapper,
              db.order_proc).find_one
    )

    @patch('taxi.core.db.classes.BaseCollectionWrapper.find_one')
    def find_one(spec_or_id, *args, **kwargs):
        queries.append(spec_or_id)
        return original_find_one(spec_or_id, *args, **kwargs)

    order_proc_wrapper_env(shards_queries_enabled)

    result = yield db.order_proc.find_one(query)
    expected_doc = {
        '_id': '46dcc06602b17fca8a438762681bf474',
        '_shard_id': 3,
        'aliases': [
            {'id': '26d6408790eb7a279f15c564560584be'},
        ],
        'candidates': [
            {
                'alias_id': '26d6408790eb7a279f15c564560584be',
            },
        ],
        'performer': {
            'alias_id': '26d6408790eb7a279f15c564560584be',
        },
        'reorder': {
            'id': '4323a92bfd897146982999e25f2e720f',
        },
    }

    assert result == expected_doc
    assert queries == [expected_query]

    result = yield db.order_proc.find_one(query, ['aliases'])
    expected_doc = {
        '_id': '46dcc06602b17fca8a438762681bf474',
        'aliases': [
            {'id': '26d6408790eb7a279f15c564560584be'},
        ],
    }

    assert result == expected_doc


@pytest.mark.parametrize('shards_queries_enabled,query,expected_query', [
    (
        False,
        {'_id': '46dcc06602b17fca8a438762681bf474'},
        {'_id': '46dcc06602b17fca8a438762681bf474'},
    ),
    (
        True,
        {'_id': '46dcc06602b17fca8a438762681bf474'},
        {'_id': '46dcc06602b17fca8a438762681bf474', '_shard_id': 3},
    ),
    (
        True,
        {'candidates.alias_id': '26d6408790eb7a279f15c564560584be'},
        {
            'candidates.alias_id': '26d6408790eb7a279f15c564560584be',
            '_shard_id': 3,
        },
    ),
    (
        True,
        {'aliases.id': '26d6408790eb7a279f15c564560584be'},
        {
            'aliases.id': '26d6408790eb7a279f15c564560584be',
            '_shard_id': 3,
        },
    ),
    (
        True,
        {'performer.alias_id': '26d6408790eb7a279f15c564560584be'},
        {
            'performer.alias_id': '26d6408790eb7a279f15c564560584be',
            '_shard_id': 3,
        },
    ),
])
@pytest.inline_callbacks
def test_order_proc_collection_wrapper_find_one_and_update(
        shards_queries_enabled, query, expected_query, order_proc_wrapper_env,
        patch):
    queries = []
    original_find_one_and_update = (
        super(base_order_wrapper.BaseOrderCollectionWrapper,
              db.order_proc).find_one_and_update
    )

    @patch('taxi.core.db.classes.BaseCollectionWrapper.find_one_and_update')
    def find_one_and_update(spec_or_id, *args, **kwargs):
        queries.append(spec_or_id)
        return original_find_one_and_update(spec_or_id, *args, **kwargs)

    order_proc_wrapper_env(shards_queries_enabled)

    returned_doc = yield db.order_proc.find_one_and_update(
        query, {'$set': {'foo': 'bar'}}
    )
    result_doc = yield db.order_proc.find_one(
        '46dcc06602b17fca8a438762681bf474'
    )
    expected_returned_doc = {
        '_id': '46dcc06602b17fca8a438762681bf474',
        '_shard_id': 3,
        'aliases': [
            {'id': '26d6408790eb7a279f15c564560584be'}
        ],
        'candidates': [
            {
                'alias_id': '26d6408790eb7a279f15c564560584be'
            }
        ],
        'performer': {
            'alias_id': '26d6408790eb7a279f15c564560584be'
        },
        'reorder': {
            'id': '4323a92bfd897146982999e25f2e720f'
        }
    }
    expected_result_doc = copy.copy(expected_returned_doc)
    expected_result_doc['foo'] = 'bar'

    assert returned_doc == expected_returned_doc
    assert result_doc == expected_result_doc
    assert queries == [expected_query]


@pytest.mark.parametrize('shards_queries_enabled,query,expected_query', [
    (
        False,
        {'_id': '46dcc06602b17fca8a438762681bf474'},
        {'_id': '46dcc06602b17fca8a438762681bf474'},
    ),
    (
        True,
        {'_id': '46dcc06602b17fca8a438762681bf474'},
        {'_id': '46dcc06602b17fca8a438762681bf474', '_shard_id': 3},
    ),
    (
        True,
        {'candidates.alias_id': '26d6408790eb7a279f15c564560584be'},
        {
            'candidates.alias_id': '26d6408790eb7a279f15c564560584be',
            '_shard_id': 3,
        },
    ),
    (
        True,
        {'aliases.id': '26d6408790eb7a279f15c564560584be'},
        {
            'aliases.id': '26d6408790eb7a279f15c564560584be',
            '_shard_id': 3,
        },
    ),
    (
        True,
        {'performer.alias_id': '26d6408790eb7a279f15c564560584be'},
        {
            'performer.alias_id': '26d6408790eb7a279f15c564560584be',
            '_shard_id': 3,
        },
    ),
])
@pytest.inline_callbacks
def test_order_proc_collection_wrapper_find_and_modify(
        shards_queries_enabled, query, expected_query, order_proc_wrapper_env,
        patch):
    queries = []
    original_find_and_modify = (
        super(base_order_wrapper.BaseOrderCollectionWrapper,
              db.order_proc).find_and_modify
    )

    @patch('taxi.core.db.classes.BaseCollectionWrapper.find_and_modify')
    def find_and_modify(query, *args, **kwargs):
        queries.append(query)
        return original_find_and_modify(query, *args, **kwargs)

    order_proc_wrapper_env(shards_queries_enabled)

    returned_doc = yield db.order_proc.find_and_modify(
        query, {'$set': {'foo': 'bar'}}
    )
    result_doc = yield db.order_proc.find_one(
        '46dcc06602b17fca8a438762681bf474'
    )
    expected_returned_doc = {
        '_id': '46dcc06602b17fca8a438762681bf474',
        '_shard_id': 3,
        'aliases': [
            {'id': '26d6408790eb7a279f15c564560584be'}
        ],
        'candidates': [
            {
                'alias_id': '26d6408790eb7a279f15c564560584be'
            }
        ],
        'performer': {
            'alias_id': '26d6408790eb7a279f15c564560584be'
        },
        'reorder': {
            'id': '4323a92bfd897146982999e25f2e720f'
        }
    }
    expected_result_doc = copy.copy(expected_returned_doc)
    expected_result_doc['foo'] = 'bar'

    assert returned_doc == expected_returned_doc
    assert result_doc == expected_result_doc
    assert queries == [expected_query]


@pytest.mark.parametrize('shards_queries_enabled,expected', [
    (False, [
        {'_id': '29f21754786f71d2a258710e3d494f71'},
        {
            '_id': '41e720f9520d4fb8a75eb89258613997',
            'foo': 'bar',
        },
        {
            '_id': 'ed4dfbbb302c3ee28e90e8dc12a88086',
            '_shard_id': 7,
            'foo': 'bar',
        },
    ]),
    (True, [
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
    ]),
])
@pytest.mark.filldb(order_proc='test_bulk')
@pytest.inline_callbacks
def test_order_proc_collection_wrapper_initialize_unordered_bulk_op(
        shards_queries_enabled, expected, order_proc_wrapper_env):
    order_proc_wrapper_env(shards_queries_enabled)
    bulk = db.order_proc.initialize_unordered_bulk_op()
    yield _test_bulk(bulk, expected)


@pytest.mark.parametrize('shards_queries_enabled,expected', [
    (False, [
        {'_id': '29f21754786f71d2a258710e3d494f71'},
        {
            '_id': '41e720f9520d4fb8a75eb89258613997',
            'foo': 'bar',
        },
        {
            '_id': 'ed4dfbbb302c3ee28e90e8dc12a88086',
            '_shard_id': 7,
            'foo': 'bar',
        },
    ]),
    (True, [
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
    ]),
])
@pytest.mark.filldb(order_proc='test_bulk')
@pytest.inline_callbacks
def test_order_proc_collection_wrapper_initialize_ordered_bulk_op(
        shards_queries_enabled, expected, order_proc_wrapper_env):
    order_proc_wrapper_env(shards_queries_enabled)
    bulk = db.order_proc.initialize_ordered_bulk_op()
    yield _test_bulk(bulk, expected)


@pytest.inline_callbacks
def _test_bulk(proc_bulk, expected):
    proc_bulk.insert({'_id': '29f21754786f71d2a258710e3d494f71'})
    proc_bulk.find(
        {'_id': '41e720f9520d4fb8a75eb89258613997'}
    ).upsert().update({'$set': {'foo': 'bar'}})
    proc_bulk.update(
        {'_id': 'ed4dfbbb302c3ee28e90e8dc12a88086'}, {'$set': {'foo': 'bar'}}
    )

    yield proc_bulk.execute()

    docs = yield db.order_proc.find().run()

    assert sorted(docs) == expected
