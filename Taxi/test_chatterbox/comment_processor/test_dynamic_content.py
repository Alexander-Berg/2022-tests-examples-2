from typing import List
from typing import Set

import pytest

from chatterbox import constants
from test_chatterbox import plugins as conftest


@pytest.mark.parametrize(
    (
        'comment',
        'task_data',
        'expected_comment',
        'succeed_operations',
        'log_messages',
    ),
    (
        (
            'Hello! Sorry {{dynamic_content:test_field}}',
            {},
            'Hello! Sorry {{dynamic_content:test_field}}',
            set(),
            ['Cant apply macro: content id test_field missing in config'],
        ),
        (
            'Hello! Sorry {{dynamic_content:sign}}',
            {'field': 'value_3'},
            'Hello! Sorry {{dynamic_content:sign}}',
            set(),
            ['There is not satisfying conditions for sign content_id'],
        ),
        (
            'Hello! Sorry {{dynamic_content:sign}}',
            {'field': 'value_2'},
            'Hello! Sorry support_2',
            {'insert_dynamic_content'},
            ['Insert dynamic content sign processed'],
        ),
        (
            'Hello! Sorry {{dynamic_content:sign}} {{dynamic_content:brand}}',
            {'field': 'value_1', 'country': 'eng'},
            'Hello! Sorry support_1 yango',
            {'insert_dynamic_content'},
            [
                'Insert dynamic content sign processed',
                'Insert dynamic content brand processed',
            ],
        ),
        (
            'Hello! Sorry {{dynamic_content:brand}} {{dynamic_content:sign}}',
            {'field': 'value_3', 'country': 'eng'},
            'Hello! Sorry {{dynamic_content:brand}} {{dynamic_content:sign}}',
            {'insert_dynamic_content'},
            [
                'Insert dynamic content brand processed',
                'There is not satisfying conditions for sign content_id',
            ],
        ),
        (
            'Hello! Sorry {{dynamic_content:test_tag}}',
            {'field': 'value_1', 'country': 'eng', 'tags': ['test_tag_2']},
            'Hello! Sorry value_2',
            {'insert_dynamic_content'},
            ['Insert dynamic content test_tag processed'],
        ),
    ),
)
@pytest.mark.config(
    CHATTERBOX_MACRO_DYNAMIC_CONTENT={
        'brand': [
            {'value': 'yandex', 'apply_condition': {'country': 'rus'}},
            {'value': 'yango', 'apply_condition': {'country': {'#ne': 'rus'}}},
        ],
        'sign': [
            {'value': 'support_1', 'apply_condition': {'field': 'value_1'}},
            {'value': 'support_2', 'apply_condition': {'field': 'value_2'}},
            {'value': 'support_3', 'apply_condition': {'field': 'value_1'}},
        ],
        'test_tag': [
            {
                'value': 'value_1',
                'apply_condition': {'tags': {'#in': ['test_tag_1']}},
            },
            {
                'value': 'value_2',
                'apply_condition': {
                    'tags': {'#in': ['test_tag_2', 'test_tag_3']},
                },
            },
        ],
    },
)
async def test_dynamic_content(
        cbox: conftest.CboxWrap,
        comment: str,
        task_data: dict,
        expected_comment: str,
        succeed_operations: Set[str],
        log_messages: List[str],
):

    comment_processor = cbox.app.comment_processor

    new_comment, processing_info = await comment_processor.process(
        comment, task_data, {}, constants.DEFAULT_STARTRACK_PROFILE,
    )
    assert new_comment == expected_comment
    assert processing_info.succeed_operations == succeed_operations
    assert processing_info.operations_log == log_messages
