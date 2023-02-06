from typing import List
from typing import Set

import pytest

from chatterbox import constants
from test_chatterbox import plugins as conftest


@pytest.mark.parametrize(
    ('comment', 'expected_comment', 'succeed_operations', 'log_messages'),
    (
        (
            'Hello! Sorry {{meta:fixed_price}}',
            'Hello! Sorry 100.0',
            {'insert_meta'},
            ['Insert meta fixed_price processed'],
        ),
        (
            'Hello! Sorry {{meta:order_cost}}',
            'Hello! Sorry 100',
            {'insert_meta'},
            ['Insert meta order_cost processed'],
        ),
        (
            'Hello! Sorry {{meta:user_phone}}',
            'Hello! Sorry +79001211221',
            {'insert_meta'},
            ['Insert meta user_phone processed'],
        ),
        (
            'Hello! Sorry {{meta:dict_field}}',
            'Hello! Sorry {{meta:dict_field}}',
            set(),
            ['Cant apply macro: field dict_field insertion not allowed'],
        ),
        (
            'Hello! Sorry {{meta:list_field}}',
            'Hello! Sorry {{meta:list_field}}',
            set(),
            ['Cant apply macro: field list_field insertion not allowed'],
        ),
    ),
)
async def test_insert_meta(
        cbox: conftest.CboxWrap,
        comment: str,
        expected_comment: str,
        succeed_operations: Set[str],
        log_messages: List[str],
):

    comment_processor = cbox.app.comment_processor
    task_data = {
        'user_phone': '+79001211221',
        'fixed_price': 100.0,
        'order_cost': 100,
        'dict_field': {},
        'list_field': [],
    }

    new_comment, processing_info = await comment_processor.process(
        comment, task_data, {}, constants.DEFAULT_STARTRACK_PROFILE,
    )
    assert new_comment == expected_comment
    assert processing_info.succeed_operations == succeed_operations
    assert processing_info.operations_log == log_messages
