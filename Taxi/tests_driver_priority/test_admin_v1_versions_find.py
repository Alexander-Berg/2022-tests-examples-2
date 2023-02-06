import datetime
from typing import Any
from typing import Dict

import pytest

from tests_driver_priority import db_tools
from tests_driver_priority import utils


URL = 'admin/v1/versions/find'
NOW = datetime.datetime.now(datetime.timezone.utc)
TIME_FORMAT = '%Y-%m-%dT%H:%M:%S.%f+00:00'
VERSION_INFO = {
    'version': {
        'sort_order': 0,
        'created_at': NOW,
        'starts_at': NOW,
        'stops_at': NOW + db_tools.DAY,
    },
    'rule': db_tools.DEFAULT_RULE,
    'payloads': db_tools.DEFAULT_PAYLOADS,
    'conditions': {},
}


@pytest.mark.pgsql(
    'driver_priority', queries=db_tools.get_pg_default_data(NOW),
)
@pytest.mark.parametrize(
    'priority_name, preset_name, version_id,expected_code, expected_data',
    [
        pytest.param(
            'branding', 'default', 0, 200, VERSION_INFO, id='success request',
        ),
        pytest.param(
            'branding',
            'without_versions',
            0,
            404,
            {
                'message': (
                    'Could not find preset_id for '
                    'priority_name="branding" and '
                    'preset_name="without_versions"'
                ),
            },
            id='priority or preset was not found',
        ),
        pytest.param(
            'branding',
            'default',
            2,
            404,
            {
                'message': (
                    'Could not find version for '
                    'priority_name="branding", preset_name="default" '
                    'and version_id=2'
                ),
            },
            id='version was not found',
        ),
    ],
)
async def test_handler(
        taxi_driver_priority,
        priority_name: str,
        preset_name: str,
        version_id: int,
        expected_code: int,
        expected_data: Dict[str, Any],
):
    query = (
        f'{URL}?priority_name={priority_name}&preset_name={preset_name}&'
        f'version_id={version_id}'
    )
    response = await taxi_driver_priority.get(query)
    assert response.status_code == expected_code

    data = response.json()
    if expected_code == 200:
        for time_field in ['created_at', 'starts_at', 'stops_at']:
            data['version'][time_field] = utils.parse_datetime(
                data['version'][time_field],
            )
    assert data == expected_data
