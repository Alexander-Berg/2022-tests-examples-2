import dataclasses
import datetime
from typing import Any
from typing import Dict
from typing import List

import pytest

from tests_driver_priority import constants
from tests_driver_priority import db_tools
from tests_driver_priority import priority_items
from tests_driver_priority import utils


URL = 'admin/v1/priorities/list'

NOW = datetime.datetime.now(datetime.timezone.utc)
HOUR = datetime.timedelta(hours=1)
DAY = datetime.timedelta(days=1)
WEEK = datetime.timedelta(days=7)

RULES: List[Dict[str, Any]] = [
    {
        'single_rule': {
            'tag_name': 'gold',
            'priority_value': {'backend': 5, 'display': 6},
        },
    },
    {
        'single_rule': {
            'tag_name': 'gold',
            'priority_value': {'backend': 0, 'display': 1},
        },
    },
    {
        'ranked_rule': [
            {
                'tag_name': 'silver',
                'priority_value': {'backend': 1, 'display': 1},
            },
            {
                'tag_name': 'gold',
                'priority_value': {'backend': 3, 'display': 3},
            },
            {
                'tag_name': 'platinum',
                'priority_value': {'backend': 5, 'display': 5},
            },
        ],
    },
]

_BRANDING_PRIORITY_ITEM = priority_items.Item(
    priority_items.Priority('branding', 'description', 'branding', 'active'),
    priority_items.MatchedPreset(
        'actual_preset', 'description', constants.MSK,
    ),
    priority_items.Version(0, NOW, NOW, NOW + HOUR),
    db_tools.DEFAULT_RULE,
    db_tools.DEFAULT_PAYLOADS,
    priority_items.Conditions(None, None, None),
    max_value=1,
)

_DISABLED_PRIORITY_ITEM = priority_items.Item(
    priority_items.Priority('disabled', 'description', 'disabled', 'disabled'),
    priority_items.Preset('default', 'description'),
    priority_items.Version(2, NOW, NOW, None),
    db_tools.DEFAULT_RULE,
    db_tools.DEFAULT_PAYLOADS,
    priority_items.Conditions(None, None, None),
    max_value=1,
)

PRIORITY_ITEMS = [
    priority_items.Item(
        priority_items.Priority(
            'branding_local', 'description', 'branding', 'active',
        ),
        priority_items.Preset('default', 'description'),  # constants.MSK,
        priority_items.Version(0, NOW, NOW, None),
        RULES[0],
        db_tools.DEFAULT_PAYLOADS,
        priority_items.Conditions(None, None, None),
        6,
    ),
    priority_items.Item(
        priority_items.Priority(
            'loyalty_local', 'description', 'loyalty', 'active',
        ),
        priority_items.Preset('default', 'description'),
        priority_items.Version(7, NOW, NOW, None),
        RULES[1],
        db_tools.DEFAULT_PAYLOADS,
        priority_items.Conditions(None, None, None),
        1,
    ),
    priority_items.Item(
        priority_items.Priority(
            'version_disabled', 'description', 'disabled', 'disabled',
        ),
        priority_items.Preset('default', 'description'),
        priority_items.Version(4, NOW, NOW, None),
        db_tools.DEFAULT_RULE,
        db_tools.DEFAULT_PAYLOADS,
        priority_items.Conditions(None, {'value': True}, None),
        max_value=1,
    ),
    priority_items.Item(
        priority_items.Priority(
            'second_loyalty', 'description', 'loyalty', 'active',
        ),
        priority_items.Preset('default', 'description'),
        priority_items.Version(11, NOW, NOW, None),
        RULES[2],
        db_tools.DEFAULT_PAYLOADS,
        priority_items.Conditions(None, None, None),
        5,
    ),
]

CUSTOM_DB_QUERIES = [
    # branding
    db_tools.insert_priority(5, 'branding_local', True, 'branding'),
    db_tools.insert_priority_relation(constants.MSK, 5, False),
    db_tools.insert_preset(9, 5, 'default', NOW, is_default=True),
    db_tools.insert_version(
        13, 9, 0, RULES[0], db_tools.DEFAULT_ACHIEVED_PAYLOAD, NOW, NOW,
    ),
    # loyalty
    db_tools.insert_priority(6, 'loyalty_local', True, 'loyalty'),
    db_tools.insert_priority_relation(constants.MSK, 6, False),
    db_tools.insert_preset(10, 6, 'default', NOW, is_default=True),
    db_tools.insert_version(
        14, 10, 7, RULES[1], db_tools.DEFAULT_ACHIEVED_PAYLOAD, NOW, NOW,
    ),
    # disabled
    db_tools.insert_priority(7, 'version_disabled', False, 'disabled'),
    db_tools.insert_priority_relation(constants.MSK, 7, False),
    db_tools.insert_preset(11, 7, 'default', NOW, is_default=True),
    db_tools.insert_version(
        15,
        11,
        4,
        db_tools.DEFAULT_RULE,
        db_tools.DEFAULT_ACHIEVED_PAYLOAD,
        NOW,
        NOW,
        disabled_condition={'value': True},
    ),
    # second loyalty
    db_tools.insert_priority(8, 'second_loyalty', True, 'loyalty'),
    db_tools.insert_priority_relation(constants.MSK, 8, False),
    db_tools.insert_preset(12, 8, 'default', NOW, is_default=True),
    db_tools.insert_version(
        16, 12, 11, RULES[2], db_tools.DEFAULT_ACHIEVED_PAYLOAD, NOW, NOW,
    ),
]
QUERIES = (
    db_tools.get_pg_default_data(NOW)
    + db_tools.join_queries(CUSTOM_DB_QUERIES),
)


def _time_to_str(time: datetime.datetime):
    timestamp = time.strftime('%Y-%m-%dT%H:%M:%S')
    microseconds = time.strftime('%f').rstrip('0')
    if microseconds:
        return timestamp + '.' + microseconds + '+0000'
    return timestamp + '+0000'


@pytest.mark.geo_nodes(
    [
        {
            'name': 'br_root',
            'name_en': 'Basic Hierarchy',
            'name_ru': 'Базовая иерархия',
            'node_type': 'root',
            'tariff_zones': ['tula'],
        },
        {
            'name': 'br_moscow',
            'name_en': 'Moscow',
            'name_ru': 'Москва',
            'node_type': 'node',
            'parent_name': 'br_root',
        },
        {
            'name': 'br_moscow_adm',
            'name_en': 'Moscow (adm)',
            'name_ru': 'Москва (адм)',
            'node_type': 'node',
            'parent_name': 'br_moscow',
            'tariff_zones': ['moscow'],
            'region_id': '213',
        },
        {
            'name': 'br_spb',
            'name_en': 'St. Petersburg',
            'name_ru': 'Cанкт-Петербург',
            'node_type': 'node',
            'parent_name': 'br_root',
            'tariff_zones': ['spb'],
            'region_id': '2',
        },
    ],
)
@pytest.mark.now(NOW.isoformat())
@pytest.mark.pgsql('driver_priority', queries=QUERIES)
@pytest.mark.parametrize(
    'request_body, expected_items, expected_code',
    [
        pytest.param(
            {
                'tariff_zone': constants.TULA,
                'show': 'only_active',
                'active_at': _time_to_str(NOW + WEEK),
            },
            [],
            200,
            id='no priorities',
        ),
        pytest.param(
            {'tariff_zone': constants.MSK, 'show': 'only_active'},
            [
                _BRANDING_PRIORITY_ITEM,
                PRIORITY_ITEMS[0],
                PRIORITY_ITEMS[1],
                PRIORITY_ITEMS[3],
            ],
            200,
            id='active_at is now',
        ),
        pytest.param(
            {
                'tariff_zone': constants.MSK,
                'show': 'only_active',
                'active_at': _time_to_str(NOW - DAY),
            },
            [],
            200,
            id='active_at is past',
        ),
        pytest.param(
            {'tariff_zone': constants.SPB, 'show': 'only_active'},
            [
                priority_items.Item(
                    priority_items.Priority(
                        'loyalty', 'description', 'loyalty', 'active',
                    ),
                    priority_items.Preset('default', 'description'),
                    priority_items.Version(1, NOW - DAY, NOW - DAY, None),
                    db_tools.DEFAULT_RULE,
                    db_tools.DEFAULT_PAYLOADS,
                    priority_items.Conditions(
                        {'value': True}, None, {'value': False},
                    ),
                    max_value=1,
                ),
            ],
            200,
            id='another tariff_zone',
        ),
        pytest.param(
            {
                'tariff_zone': constants.MSK,
                'show': 'all',
                'active_at': _time_to_str(NOW),
            },
            [
                _BRANDING_PRIORITY_ITEM,
                PRIORITY_ITEMS[0],
                priority_items.Item(
                    priority_items.Priority(
                        'disabled', 'description', 'disabled', 'disabled',
                    ),
                    priority_items.Preset('default', 'description'),
                    priority_items.Version(2, NOW, NOW, None),
                    db_tools.DEFAULT_RULE,
                    db_tools.DEFAULT_PAYLOADS,
                    priority_items.Conditions(None, None, None),
                    max_value=1,
                ),
                PRIORITY_ITEMS[2],
                PRIORITY_ITEMS[1],
                PRIORITY_ITEMS[3],
            ],
            200,
            id='show all',
        ),
        pytest.param(
            {
                'tariff_zone': constants.MSK,
                'show': 'all',
                'limit': 1,
                'offset': 2,
            },
            [_DISABLED_PRIORITY_ITEM],
            200,
            id='limit & offset are defined',
        ),
        pytest.param(
            {'tariff_zone': constants.MSK, 'show': 'all', 'offset': 2},
            [
                _DISABLED_PRIORITY_ITEM,
                PRIORITY_ITEMS[2],
                PRIORITY_ITEMS[1],
                PRIORITY_ITEMS[3],
            ],
            200,
            id='offset is defined only',
        ),
        pytest.param(
            {'tariff_zone': constants.MSK, 'show': 'all', 'offset': 6},
            [],
            200,
            id='out of range large',
        ),
        pytest.param(
            {'tariff_zone': 'not_exist', 'show': 'only_active'},
            [],
            404,
            id='not existing tariff_zone',
        ),
        pytest.param(
            {
                'tariff_zone': constants.MSK,
                'show': 'all',
                'active_at': _time_to_str(NOW),
                'list_sort': {'entity': 'sort_order', 'direction': 'ASC'},
            },
            [
                _BRANDING_PRIORITY_ITEM,
                PRIORITY_ITEMS[0],
                _DISABLED_PRIORITY_ITEM,
                PRIORITY_ITEMS[2],
                PRIORITY_ITEMS[1],
                PRIORITY_ITEMS[3],
            ],
            200,
            id='asc sort by sort_order',
        ),
        pytest.param(
            {
                'tariff_zone': constants.MSK,
                'show': 'all',
                'active_at': _time_to_str(NOW),
                'list_sort': {'entity': 'sort_order', 'direction': 'DESC'},
            },
            [
                PRIORITY_ITEMS[3],
                PRIORITY_ITEMS[1],
                PRIORITY_ITEMS[2],
                _DISABLED_PRIORITY_ITEM,
                PRIORITY_ITEMS[0],
                _BRANDING_PRIORITY_ITEM,
            ],
            200,
            id='desc sort by sort_order',
        ),
        pytest.param(
            {
                'tariff_zone': constants.MSK,
                'show': 'all',
                'active_at': _time_to_str(NOW),
                'list_sort': {'entity': 'max_value', 'direction': 'ASC'},
            },
            [
                _BRANDING_PRIORITY_ITEM,
                _DISABLED_PRIORITY_ITEM,
                PRIORITY_ITEMS[1],
                PRIORITY_ITEMS[2],
                PRIORITY_ITEMS[3],
                PRIORITY_ITEMS[0],
            ],
            200,
            id='asc sort by max_value',
        ),
        pytest.param(
            {
                'tariff_zone': constants.MSK,
                'show': 'all',
                'active_at': _time_to_str(NOW),
                'list_sort': {'entity': 'max_value', 'direction': 'DESC'},
            },
            [
                PRIORITY_ITEMS[0],
                PRIORITY_ITEMS[3],
                PRIORITY_ITEMS[2],
                PRIORITY_ITEMS[1],
                _DISABLED_PRIORITY_ITEM,
                _BRANDING_PRIORITY_ITEM,
            ],
            200,
            id='desc sort by max_value',
        ),
    ],
)
async def test_handler(
        taxi_driver_priority,
        request_body: Dict[str, Any],
        expected_items: List[priority_items.Item],
        expected_code: int,
):
    response = await taxi_driver_priority.post(URL, request_body)
    assert response.status_code == expected_code
    if expected_code != 200:
        return

    expected_priorities = []
    for item in expected_items:
        expected_item = dataclasses.asdict(item)
        expected_item['version'] = db_tools.remove_nullable_keys(
            expected_item['version'],
        )
        expected_item['conditions'] = db_tools.remove_nullable_keys(
            expected_item['conditions'],
        )
        expected_priorities.append(expected_item)

    items = response.json()['items']
    for priority_item in items:
        for key in ['created_at', 'starts_at', 'stops_at']:
            if key in priority_item['version']:
                priority_item['version'][key] = utils.parse_datetime(
                    priority_item['version'][key],
                )
    assert items == expected_priorities
