import datetime
from typing import Optional

import pytest

from chatterbox import constants
from test_chatterbox import plugins as conftest


@pytest.mark.config(
    CHATTERBOX_SEARCH_QUEUES_BY_PROFILE={'support-taxi': ['TEST_QUEUE']},
    STARTRACK_CUSTOM_FIELDS_MAP_FOR_SEARCH={
        'support-taxi': {'line': 'line', 'chatterbox_id': 'Chatterbox ID'},
    },
)
@pytest.mark.parametrize(
    'data, expected_query',
    (
        ({}, 'Queue: "TEST_QUEUE" AND "Chatterbox ID": notEmpty()'),
        ({'status': 'in_progress'}, None),
        (
            {'status': 'archived'},
            'Queue: "TEST_QUEUE" AND "Chatterbox ID": notEmpty()',
        ),
        (
            {'status': 'exported'},
            'Queue: "TEST_QUEUE" AND "Chatterbox ID": notEmpty()',
        ),
        (
            {'dummy': 'first'},
            'Queue: "TEST_QUEUE" AND "Chatterbox ID": notEmpty()',
        ),
        (
            {'line': 'first'},
            'Queue: "TEST_QUEUE" AND '
            '"Chatterbox ID": notEmpty() AND '
            '"line": "first"',
        ),
        (
            {'line': ['first', 'second']},
            'Queue: "TEST_QUEUE" AND '
            '"Chatterbox ID": notEmpty() AND '
            '"line": "first", "second"',
        ),
        (
            {'tags': ['first', 'second']},
            'Queue: "TEST_QUEUE" AND '
            '"Chatterbox ID": notEmpty() AND '
            'tags: "first" AND tags: "second"',
        ),
        (
            {'created': datetime.datetime(2019, 1, 1)},
            'Queue: "TEST_QUEUE" AND '
            '"Chatterbox ID": notEmpty() AND '
            'created: "2019-01-01".."2019-01-01"',
        ),
        (
            {'created_from': datetime.datetime(2019, 1, 1)},
            'Queue: "TEST_QUEUE" AND '
            '"Chatterbox ID": notEmpty() AND '
            'created: >= "2019-01-01 03:00"',
        ),
        (
            {'created_to': datetime.datetime(2019, 2, 1)},
            'Queue: "TEST_QUEUE" AND '
            '"Chatterbox ID": notEmpty() AND '
            'created: <= "2019-02-01 03:00"',
        ),
        (
            {'text': 'Text'},
            'Queue: "TEST_QUEUE" AND '
            '"Chatterbox ID": notEmpty() AND '
            '(Description: "Text" OR Comment: "Text")',
        ),
        (
            {
                'status': 'archived',
                'invalid_field': 'first',
                'line': 'second',
                'text': 'New',
                'tags': ['first', 'second'],
                'created': datetime.datetime(2019, 1, 1),
            },
            'Queue: "TEST_QUEUE" AND '
            '"Chatterbox ID": notEmpty() AND '
            '"line": "second" AND '
            'created: "2019-01-01".."2019-01-01" AND '
            'tags: "first" AND '
            'tags: "second" AND '
            '(Description: "New" OR Comment: "New")',
        ),
    ),
)
async def test_get_startrack_query(
        cbox: conftest.CboxWrap, data: dict, expected_query: Optional[str],
):
    manager = cbox.app.startrack_manager

    query = manager.get_startrack_query(
        profile=constants.DEFAULT_STARTRACK_PROFILE, **data,
    )
    assert query == expected_query
