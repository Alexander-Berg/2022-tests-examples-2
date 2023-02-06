import pytest

from taxi.core.db.wrappers import base_order_wrapper


ID_FIELDS = (
    ('_id', True),
    ('reorder.id', True),
    ('candidates.alias_id', False),
    ('aliases.id', False),
    ('performer.alias_id', False),
)


@pytest.mark.parametrize('query,expected', [
    (None, None),
    ({}, {}),
    (
        {'_id': '29f21754786f71d2a258710e3d494f71', '_shard_id': 4},
        {'_id': '29f21754786f71d2a258710e3d494f71', '_shard_id': 4},
    ),
    (
        {'_id': '29f21754786f71d2a258710e3d494f71'},
        {'_id': '29f21754786f71d2a258710e3d494f71', '_shard_id': 3},
    ),
    (
        {'candidates.alias_id': '29f21754786f71d2a258710e3d494f71'},
        {
            'candidates.alias_id': '29f21754786f71d2a258710e3d494f71',
            '_shard_id': 3,
        },
    ),
    (
        {'aliases.id': '29f21754786f71d2a258710e3d494f71'},
        {
            'aliases.id': '29f21754786f71d2a258710e3d494f71',
            '_shard_id': 3,
        },
    ),
    (
        {'performer.alias_id': '29f21754786f71d2a258710e3d494f71'},
        {
            'performer.alias_id': '29f21754786f71d2a258710e3d494f71',
            '_shard_id': 3,
        },
    ),
    (
        {'_id': '41e720f9520d4fb8a75eb89258613997'},
        {'_id': '41e720f9520d4fb8a75eb89258613997', '_shard_id': 0},
    ),
    (
        {'candidates.alias_id': '41e720f9520d4fb8a75eb89258613997'},
        {'candidates.alias_id': '41e720f9520d4fb8a75eb89258613997'},
    ),
    (
        {'aliases.id': '41e720f9520d4fb8a75eb89258613997'},
        {'aliases.id': '41e720f9520d4fb8a75eb89258613997'},
    ),
    (
        {'performer.alias_id': '41e720f9520d4fb8a75eb89258613997'},
        {'performer.alias_id': '41e720f9520d4fb8a75eb89258613997'},
    ),
    (
        # same shard in $or subqueries
        {
            '$or': [
                {'_id': '77378934fbec2347bdf1777378d4c8b7'},
                {'performer.alias_id': '8418b3392cc7297aaea5984ca1b7a6f3'},
            ],
        },
        {
            '$or': [
                {'_id': '77378934fbec2347bdf1777378d4c8b7'},
                {'performer.alias_id': '8418b3392cc7297aaea5984ca1b7a6f3'},
            ],
            '_shard_id': 6,
        },
    ),
    (
        # different shards in $or subqueries
        {
            '$or': [
                {'_id': 'bdaf0c3207cd7d5da3ada44f59e379b9'},
                {'performer.alias_id': 'c30a4388c3d90519a9b9d814903d1318'},
            ],
        },
        {
            '$or': [
                {'_id': 'bdaf0c3207cd7d5da3ada44f59e379b9'},
                {'performer.alias_id': 'c30a4388c3d90519a9b9d814903d1318'},
            ],
        },
    ),
    (
        # 0 shard in $or subqueries
        {
            '$or': [
                {'_id': '18f053fd7066466da7778ed011a0f52e'},
                {'candidates.alias_id': '41e720f9520d4fb8a75eb89258613997'},
            ],
        },
        {
            '$or': [
                {'_id': '18f053fd7066466da7778ed011a0f52e'},
                {'candidates.alias_id': '41e720f9520d4fb8a75eb89258613997'},
            ],
        },
    ),
    (
        # 1 subquery with id, another without any identifiers
        {
            '$or': [
                {'_id': '18f053fd7066466da7778ed011a0f52e'},
                {'foo': 'bar'},
            ],
        },
        {
            '$or': [
                {'_id': '18f053fd7066466da7778ed011a0f52e'},
                {'foo': 'bar'},
            ],
        },
    ),
    (
        # 2 subqueries without any identifiers in $or query
        {
            '$or': [
                {'foo': 'bar'},
                {'baz': 'quux'},
            ],
        },
        {
            '$or': [
                {'foo': 'bar'},
                {'baz': 'quux'},
            ],
        },
    ),
    (
        {
            '$and': [
                {'_id': '67deb8842f8a28608e60696314ce3940'},
                {'foo': 'bar'},
            ],
        },
        {
            '$and': [
                {'_id': '67deb8842f8a28608e60696314ce3940'},
                {'foo': 'bar'},
            ],
            '_shard_id': 6,
        },
    ),
    (
        # different shards in $and subqueries
        {
            '$and': [
                {'_id': 'bdaf0c3207cd7d5da3ada44f59e379b9'},
                {'performer.alias_id': 'c30a4388c3d90519a9b9d814903d1318'},
            ],
        },
        {
            '$and': [
                {'_id': 'bdaf0c3207cd7d5da3ada44f59e379b9'},
                {'performer.alias_id': 'c30a4388c3d90519a9b9d814903d1318'},
            ],
            '_shard_id': 3,
        },
    ),
    (
        # 0 shard in $and subqueries
        {
            '$and': [
                {'_id': '18f053fd7066466da7778ed011a0f52e'},
                {'candidates.alias_id': '41e720f9520d4fb8a75eb89258613997'},
            ],
        },
        {
            '$and': [
                {'_id': '18f053fd7066466da7778ed011a0f52e'},
                {'candidates.alias_id': '41e720f9520d4fb8a75eb89258613997'},
            ],
            '_shard_id': 0,
        },
    ),
    (
        # 2 subqueries without any identifiers in $and query
        {
            '$and': [
                {'foo': 'bar'},
                {'baz': 'quux'},
            ],
        },
        {
            '$and': [
                {'foo': 'bar'},
                {'baz': 'quux'},
            ],
        },
    ),
])
@pytest.mark.filldb(_fill=False)
@pytest.mark.asyncenv('blocking')
def test_extend_query(query, expected):
    query_wrapper = base_order_wrapper.QueryWrapper(id_fields=ID_FIELDS)
    result = query_wrapper.extend_query(query)
    assert result == expected


@pytest.mark.parametrize('spec_or_id,expected', [
    (None, None),
    ({}, {}),
    (
        '29f21754786f71d2a258710e3d494f71',
        {'_id': '29f21754786f71d2a258710e3d494f71', '_shard_id': 3},
    ),
    (
        {'_id': '29f21754786f71d2a258710e3d494f71'},
        {'_id': '29f21754786f71d2a258710e3d494f71', '_shard_id': 3},
    ),
    (
        {'aliases.id': '29f21754786f71d2a258710e3d494f71'},
        {'aliases.id': '29f21754786f71d2a258710e3d494f71', '_shard_id': 3},
    ),
    (
        {'_id': '29f21754786f71d2a258710e3d494f71', '_shard_id': 4},
        {'_id': '29f21754786f71d2a258710e3d494f71', '_shard_id': 4},
    ),
])
@pytest.mark.filldb(_fill=False)
@pytest.mark.asyncenv('blocking')
def test_extend_spec_or_id(spec_or_id, expected):
    query_wrapper = base_order_wrapper.QueryWrapper(id_fields=ID_FIELDS)
    result = query_wrapper.extend_spec_or_id(spec_or_id)
    assert result == expected


@pytest.mark.filldb(_fill=False)
@pytest.mark.asyncenv('blocking')
def test_check_doc_to_insert():
    with pytest.raises(ValueError):
        base_order_wrapper.QueryWrapper.check_doc_to_insert({'foo': 'bar'})
    result = base_order_wrapper.QueryWrapper.check_doc_to_insert(
        {'_id': 'foo'},
    )
    assert result
