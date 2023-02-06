import datetime
from typing import Any
from typing import Dict
from typing import Optional

import pytest

from tests_driver_priority import db_tools


URL = 'admin/v1/suggest-names'

NOW = datetime.datetime.now(datetime.timezone.utc)


@pytest.mark.pgsql(
    'driver_priority',
    queries=db_tools.join_queries(
        [
            db_tools.insert_priority(0, 'branding', True, 'tk0'),
            db_tools.insert_priority(1, 'loyalty', True, 'tk1'),
            db_tools.insert_priority(2, 'disabled', False, 'tk2'),
            db_tools.insert_priority(3, 'empty_relations', False, 'tk3'),
            # presets 0, 3, 5 and 6 are default => cannot have relations
            db_tools.insert_preset(0, 0, 'default', NOW, is_default=True),
            db_tools.insert_preset(1, 0, 'actual_preset', NOW),
            db_tools.insert_preset(2, 0, 'preset2', NOW),
            db_tools.insert_preset(3, 1, 'default', NOW, is_default=True),
            db_tools.insert_preset(4, 1, 'outdated_preset', NOW),
            db_tools.insert_preset(5, 2, 'default', NOW, is_default=True),
            db_tools.insert_preset(6, 3, 'default', NOW, is_default=True),
            # presets 0, 3, 5 and 6 should have active infinity version
            db_tools.insert_version(0, 0, 0, dict(), dict(), NOW, NOW),
            db_tools.insert_version(1, 3, 0, dict(), dict(), NOW, NOW),
            db_tools.insert_version(2, 5, 0, dict(), dict(), NOW, NOW),
            db_tools.insert_version(3, 6, 0, dict(), dict(), NOW, NOW),
        ],
    ),
)
@pytest.mark.parametrize(
    'name_part, expected_suggested_names',
    [
        pytest.param(
            None,
            [
                {
                    'priority': 'branding',
                    'presets': ['actual_preset', 'default', 'preset2'],
                },
                {'priority': 'disabled', 'presets': ['default']},
                {'priority': 'empty_relations', 'presets': ['default']},
                {
                    'priority': 'loyalty',
                    'presets': ['default', 'outdated_preset'],
                },
            ],
            id='name-part is not defined',
        ),
        pytest.param(
            '',
            [
                {
                    'priority': 'branding',
                    'presets': ['actual_preset', 'default', 'preset2'],
                },
                {'priority': 'disabled', 'presets': ['default']},
                {'priority': 'empty_relations', 'presets': ['default']},
                {
                    'priority': 'loyalty',
                    'presets': ['default', 'outdated_preset'],
                },
            ],
            id='name-part is empty',
        ),
        pytest.param('123', [], id='no matched'),
        pytest.param(
            'branding',
            [
                {
                    'priority': 'branding',
                    'presets': ['actual_preset', 'default', 'preset2'],
                },
            ],
            id='matched by priority name only',
        ),
        pytest.param(
            'brAnDinG',
            [
                {
                    'priority': 'branding',
                    'presets': ['actual_preset', 'default', 'preset2'],
                },
            ],
            id='case-insensitive matched',
        ),
        pytest.param(
            'default',
            [
                {'priority': 'branding', 'presets': ['default']},
                {'priority': 'disabled', 'presets': ['default']},
                {'priority': 'empty_relations', 'presets': ['default']},
                {'priority': 'loyalty', 'presets': ['default']},
            ],
            id='matched by preset names only',
        ),
        pytest.param(
            'al',
            [
                {'priority': 'branding', 'presets': ['actual_preset']},
                {
                    'priority': 'loyalty',
                    'presets': ['default', 'outdated_preset'],
                },
            ],
            id='matched by priority and preset names',
        ),
        pytest.param(
            'AL',
            [
                {'priority': 'branding', 'presets': ['actual_preset']},
                {
                    'priority': 'loyalty',
                    'presets': ['default', 'outdated_preset'],
                },
            ],
            id='case-insensitive matched by priority and preset names',
        ),
    ],
)
async def test_handler(
        taxi_driver_priority,
        name_part: Optional[str],
        expected_suggested_names: Dict[str, Any],
):
    params = {} if name_part is None else {'part': name_part}
    response = await taxi_driver_priority.get(URL, params=params)

    assert response.status_code == 200
    assert response.json()['suggested_names'] == expected_suggested_names
