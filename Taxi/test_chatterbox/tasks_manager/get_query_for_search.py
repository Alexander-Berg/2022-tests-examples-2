import datetime
from typing import Optional

import pytest

from chatterbox.internal.tasks_manager import _private
from test_chatterbox import plugins as conftest


@pytest.mark.config(
    CHATTERBOX_META_INFO_FIELDS_FOR_EXACT_MATCH_SEARCH=[
        'order_id',
        'some_field',
    ],
)
@pytest.mark.parametrize(
    'data, expected_query',
    (
        ({}, {'status': {'$nin': ['archived', 'exported']}}),
        (
            {'dummy_field': 'invalid'},
            {'status': {'$nin': ['archived', 'exported']}},
        ),
        (
            {'status': 'in_progress'},
            {
                'status': {
                    '$eq': 'in_progress',
                    '$nin': ['archived', 'exported'],
                },
            },
        ),
        (
            {'created': datetime.datetime(2019, 1, 1)},
            {
                'created': {
                    '$gte': datetime.datetime(2019, 1, 1),
                    '$lte': datetime.datetime(2019, 1, 2),
                },
                'status': {'$nin': ['archived', 'exported']},
            },
        ),
        (
            {'created_from': datetime.datetime(2019, 1, 1)},
            {
                'created': {'$gte': datetime.datetime(2019, 1, 1)},
                'status': {'$nin': ['archived', 'exported']},
            },
        ),
        (
            {'created_to': datetime.datetime(2019, 2, 1)},
            {
                'created': {'$lte': datetime.datetime(2019, 2, 1)},
                'status': {'$nin': ['archived', 'exported']},
            },
        ),
        (
            {'line': 'first'},
            {
                'line': {'$in': ['first']},
                'status': {'$nin': ['archived', 'exported']},
            },
        ),
        (
            {'line': ['first']},
            {
                'line': {'$in': ['first']},
                'status': {'$nin': ['archived', 'exported']},
            },
        ),
        (
            {'login': 'superuser'},
            {
                'support_admin': 'superuser',
                'status': {'$nin': ['archived', 'exported']},
            },
        ),
        (
            {'tags': ['tag1', 'tag2']},
            {
                'tags': {'$all': ['tag1', 'tag2']},
                'status': {'$nin': ['archived', 'exported']},
            },
        ),
        (
            {'order_id': '089d368248001cbe652cadf8c93558dc'},
            {
                'meta_info.order_id': '089d368248001cbe652cadf8c93558dc',
                'status': {'$ne': 'dummy_status'},
            },
        ),
        (
            {'some_field': 'some_value'},
            {
                'meta_info.some_field': 'some_value',
                'status': {'$nin': ['archived', 'exported']},
            },
        ),
    ),
)
async def test_get_mongo_search_query(
        cbox: conftest.CboxWrap, data: dict, expected_query: Optional[str],
):

    query = _private.get_query_for_search(cbox.app.config, **data)

    assert query == expected_query
