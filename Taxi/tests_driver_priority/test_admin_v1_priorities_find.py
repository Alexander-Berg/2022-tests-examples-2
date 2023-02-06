import datetime
from typing import Any
from typing import Dict

import pytest

from tests_driver_priority import constants
from tests_driver_priority import db_tools
from tests_driver_priority import utils


URL = 'admin/v1/priorities/find'

NOW = datetime.datetime.now(datetime.timezone.utc)


@pytest.mark.pgsql(
    'driver_priority', queries=db_tools.get_pg_default_data(NOW),
)
@pytest.mark.now(NOW.isoformat())
@pytest.mark.config(
    DRIVER_PRIORITY_PROFESSIONS_BY_PRIORITY_NAMES={
        '__default__': ['taxi'],
        'disabled': ['taxi', 'eats_courier'],
    },
)
@pytest.mark.parametrize(
    'priority_name, expected_response, expected_code',
    [
        (
            'branding',
            {
                'priority': {
                    'name': 'branding',
                    'status': 'active',
                    'tanker_keys_prefix': 'branding',
                    'description': 'description',
                    'agglomerations': {
                        'disabled_in': [constants.SPB, constants.TULA],
                        'enabled_in': [constants.MSK],
                    },
                    'contractor_professions': ['taxi'],
                },
                'presets': [
                    {
                        'name': 'default',
                        'description': 'description',
                        'created_at': NOW,
                        'agglomerations': [],
                        'type': 'default',
                    },
                    {
                        'name': 'actual_preset',
                        'description': 'description',
                        'created_at': NOW,
                        'agglomerations': [constants.MSK],
                        'type': 'custom',
                    },
                    {
                        'name': 'preset2',
                        'description': 'description',
                        'created_at': NOW,
                        'agglomerations': [],
                        'type': 'custom',
                    },
                ],
                'experiments': [
                    {
                        'name': 'exp0',
                        'created_at': NOW,
                        'agglomerations': ['br_moscow', 'br_root'],
                    },
                    {
                        'name': 'exp1',
                        'description': 'spb exp',
                        'created_at': NOW,
                        'agglomerations': ['br_spb'],
                    },
                ],
            },
            200,
        ),
        (
            'loyalty',
            {
                'priority': {
                    'name': 'loyalty',
                    'status': 'active',
                    'tanker_keys_prefix': 'loyalty',
                    'description': 'description',
                    'agglomerations': {
                        'disabled_in': [],
                        'enabled_in': [constants.SPB],
                    },
                    'contractor_professions': ['taxi'],
                },
                'presets': [
                    {
                        'name': 'default',
                        'description': 'description',
                        'created_at': NOW,
                        'agglomerations': [],
                        'type': 'default',
                    },
                    {
                        'name': 'actual_preset',
                        'description': 'description',
                        'created_at': NOW - db_tools.DAY,
                        'agglomerations': [],
                        'type': 'custom',
                    },
                    {
                        'name': 'outdated_preset',
                        'description': 'description',
                        'created_at': NOW,
                        'agglomerations': [constants.SPB],
                        'type': 'custom',
                    },
                    {
                        'name': 'without_versions',
                        'description': 'description',
                        'created_at': NOW,
                        'agglomerations': [],
                        'type': 'custom',
                    },
                ],
                'experiments': [
                    {
                        'name': 'exp2',
                        'description': 'loyalty_exp',
                        'created_at': NOW,
                        'agglomerations': ['spb'],
                    },
                ],
            },
            200,
        ),
        (
            'disabled',
            {
                'priority': {
                    'name': 'disabled',
                    'status': 'disabled',
                    'tanker_keys_prefix': 'disabled',
                    'description': 'description',
                    'agglomerations': {
                        'disabled_in': [constants.SPB],
                        'enabled_in': [constants.BR_ROOT],
                    },
                    'contractor_professions': ['eats_courier', 'taxi'],
                },
                'presets': [
                    {
                        'name': 'default',
                        'description': 'description',
                        'created_at': NOW,
                        'agglomerations': [],
                        'type': 'default',
                    },
                ],
                'experiments': [],
            },
            200,
        ),
        (
            'empty_relations',
            {
                'priority': {
                    'name': 'empty_relations',
                    'status': 'disabled',
                    'tanker_keys_prefix': 'empty_relations',
                    'description': 'description',
                    'agglomerations': {'disabled_in': [], 'enabled_in': []},
                    'contractor_professions': ['taxi'],
                },
                'presets': [
                    {
                        'name': 'default',
                        'description': 'description',
                        'created_at': NOW,
                        'agglomerations': [],
                        'type': 'default',
                    },
                ],
                'experiments': [],
            },
            200,
        ),
        ('not_found', {}, 404),
    ],
)
async def test_handler(
        taxi_driver_priority,
        priority_name: str,
        expected_response: Dict[str, Any],
        expected_code: int,
):
    query = f'{URL}?name={priority_name}'
    response = await taxi_driver_priority.get(query)
    assert response.status_code == expected_code
    if expected_code != 200:
        return

    data = response.json()
    for preset in data['presets']:
        preset['created_at'] = utils.parse_datetime(preset['created_at'])
    for experiment in data['experiments']:
        experiment['created_at'] = utils.parse_datetime(
            experiment['created_at'],
        )
    assert data == expected_response
