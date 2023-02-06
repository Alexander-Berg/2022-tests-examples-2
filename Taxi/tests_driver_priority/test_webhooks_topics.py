import datetime
from typing import Any
from typing import Dict
from typing import List

import pytest
import pytz

from tests_driver_priority import db_tools


_HANDLER_URL = 'internal/v1/webhooks/topic'

_NOW = datetime.datetime(2021, 9, 9, 12, 0, 0, tzinfo=pytz.timezone('UTC'))
_DAY = datetime.timedelta(hours=24)
_HOUR = datetime.timedelta(hours=1)

_DEFAULT_PRIORITY_VALUE = {'backend': 0, 'display': 0}
_CONDITIONS: List[Dict[str, Any]] = [
    {'all_of': ['tag1', 'tag2']},
    {'and': [{'any_of': ['tag3']}]},
    {'or': [{'or': [{'none_of': ['tag4', 'tag5']}]}]},
    {'any_of': ['tag6']},
    {'none_of': ['tag7', 'tag8']},
    {'all_of': ['tag9', 'tag10']},
]
_RULES: List[Dict[str, Any]] = [
    {
        'single_rule': {
            'tag_name': 'unused_tags',
            'priority_value': _DEFAULT_PRIORITY_VALUE,
            'override': _CONDITIONS[0],
        },
    },
    {
        'single_rule': {
            'tag_name': '',
            'priority_value': _DEFAULT_PRIORITY_VALUE,
            'override': _CONDITIONS[3],
        },
    },
    {
        'ranked_rule': [
            {
                'tag_name': 'tag_with_override',
                'priority_value': _DEFAULT_PRIORITY_VALUE,
                'override': _CONDITIONS[4],
            },
            {
                'tag_name': 'ranked_tag1',
                'priority_value': _DEFAULT_PRIORITY_VALUE,
            },
        ],
    },
    {
        'excluding_rule': [
            {
                'tag_name': 'excluding_tag0',
                'priority_value': _DEFAULT_PRIORITY_VALUE,
            },
            {
                'rating': {'higher_than': 1},
                'priority_value': _DEFAULT_PRIORITY_VALUE,
                'tanker_key_part': 'tk',
                'override': _CONDITIONS[5],
            },
        ],
    },
]

_APPEND_ALLOW = 'Append action is allowed'
_REMOVE_ALLOW = 'Remove action is allowed'
_REMOVE_PROHIBITED = (
    'Remove action is prohibited: tags are used by driver-priority service'
)


@pytest.mark.now(_NOW.isoformat())
@pytest.mark.pgsql(
    'driver_priority',
    queries=db_tools.join_queries(
        [
            db_tools.insert_priority(0, 'branding', True, 'tk0'),
            db_tools.insert_priority(1, 'loyalty', False, 'tk2'),
            db_tools.insert_preset(0, 0, 'default', _NOW, is_default=True),
            db_tools.insert_preset(1, 0, 'custom0', _NOW),
            db_tools.insert_preset(2, 1, 'default', _NOW, is_default=True),
            # outdated
            db_tools.insert_version(
                0,
                0,
                10,
                _RULES[0],
                db_tools.DEFAULT_ACHIEVED_PAYLOAD,
                _NOW - _DAY,
                _NOW - _DAY,
                stops_at=_NOW - _HOUR,
                temporary_condition=_CONDITIONS[0],
            ),
            # active branding default
            db_tools.insert_version(
                1,
                0,
                20,
                _RULES[1],
                db_tools.DEFAULT_ACHIEVED_PAYLOAD,
                _NOW - _HOUR,
                _NOW - _HOUR,
                disabled_condition={'value': True},
                achievable_condition=_CONDITIONS[2],
            ),
            # active branding custom0
            db_tools.insert_version(
                2,
                1,
                30,
                _RULES[2],
                db_tools.DEFAULT_ACHIEVED_PAYLOAD,
                _NOW,
                _NOW,
                temporary_condition=_CONDITIONS[2],
                disabled_condition=None,
                achievable_condition=None,
            ),
            # active loyalty default
            db_tools.insert_version(
                3,
                2,
                40,
                _RULES[3],
                db_tools.DEFAULT_ACHIEVED_PAYLOAD,
                _NOW,
                _NOW,
            ),
        ],
    ),
)
@pytest.mark.parametrize(
    'data, expected_response',
    [
        pytest.param(
            {'action': 'append', 'tags': ['tag1', 'tag2', 'tag3', 'tag4']},
            {'permission': 'allowed', 'message': _APPEND_ALLOW, 'details': {}},
            id='append action',
        ),
        pytest.param(
            {'action': 'remove', 'tags': ['tag1', 'tag2', 'unused_tags']},
            {'permission': 'allowed', 'message': _REMOVE_ALLOW, 'details': {}},
            id='remove action for outdated',
        ),
        pytest.param(
            {'action': 'remove', 'tags': ['tag3', 'tag5']},
            {
                'permission': 'prohibited',
                'message': _REMOVE_PROHIBITED,
                'details': {
                    'errors': [
                        'tag "tag5" is used by '
                        'priority "branding" (presets: custom0, default)',
                    ],
                },
            },
            id='remove action, tags from conditions',
        ),
        pytest.param(
            {'action': 'remove', 'tags': ['tag6']},
            {
                'permission': 'prohibited',
                'message': _REMOVE_PROHIBITED,
                'details': {
                    'errors': [
                        'tag "tag6" is used by '
                        'priority "branding" (presets: default)',
                    ],
                },
            },
            id='remove action, tag from override (single rule)',
        ),
        pytest.param(
            {'action': 'remove', 'tags': ['tag7']},
            {
                'permission': 'prohibited',
                'message': _REMOVE_PROHIBITED,
                'details': {
                    'errors': [
                        'tag "tag7" is used by '
                        'priority "branding" (presets: custom0)',
                    ],
                },
            },
            id='remove action, tag from override (ranked rule)',
        ),
        pytest.param(
            {'action': 'remove', 'tags': ['tag9', 'tag10']},
            {
                'permission': 'prohibited',
                'message': _REMOVE_PROHIBITED,
                'details': {
                    'errors': [
                        'tag "tag10" is used by '
                        'priority "loyalty" (presets: default)',
                        'tag "tag9" is used by '
                        'priority "loyalty" (presets: default)',
                    ],
                },
            },
            id='remove action, tag from override (excluding rule)',
        ),
        pytest.param(
            {'action': 'remove', 'tags': ['tag_with_override']},
            {'permission': 'allowed', 'message': _REMOVE_ALLOW, 'details': {}},
            id='tag from ranked rule, but rule has override condition',
        ),
        pytest.param(
            {'action': 'remove', 'tags': ['ranked_tag1']},
            {
                'permission': 'prohibited',
                'message': _REMOVE_PROHIBITED,
                'details': {
                    'errors': [
                        'tag "ranked_tag1" is used by '
                        'priority "branding" (presets: custom0)',
                    ],
                },
            },
            id='remove action, tag from ranked rule',
        ),
        pytest.param(
            {'action': 'remove', 'tags': ['excluding_tag0']},
            {
                'permission': 'prohibited',
                'message': _REMOVE_PROHIBITED,
                'details': {
                    'errors': [
                        'tag "excluding_tag0" is used by '
                        'priority "loyalty" (presets: default)',
                    ],
                },
            },
            id='remove action, tag from excluding rule',
        ),
        pytest.param(
            {'action': 'remove', 'tags': ['higher_than']},
            {'permission': 'allowed', 'message': _REMOVE_ALLOW, 'details': {}},
            id='allow remove action for tag from excluding rule with override '
            'condition',
        ),
    ],
)
async def test_webhooks_topics(taxi_driver_priority, data, expected_response):
    response = await taxi_driver_priority.post(_HANDLER_URL, data)
    assert response.status_code == 200
    assert response.json() == expected_response
