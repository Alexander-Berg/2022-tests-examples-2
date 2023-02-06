import datetime
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

import pytest

from tests_driver_priority import db_tools
from tests_driver_priority import utils


URL = 'admin/v1/presets/versions-list'

NOW = datetime.datetime.now(datetime.timezone.utc)
HOUR = datetime.timedelta(hours=1)
DAY = datetime.timedelta(days=1)
WEEK = datetime.timedelta(days=7)


def _get_preset_version_item(
        id_: int,
        starts_at: datetime.datetime,
        stops_at: Optional[datetime.datetime] = None,
        created_at: datetime.datetime = NOW,
) -> Dict[str, Any]:
    result = {'id': id_, 'created_at': created_at, 'starts_at': starts_at}
    if stops_at is not None:
        result['stops_at'] = stops_at
    return result


@pytest.mark.now(NOW.isoformat())
@pytest.mark.pgsql(
    'driver_priority', queries=db_tools.get_pg_default_data(NOW),
)
@pytest.mark.parametrize(
    'query_params, expected_versions, expected_code',
    [
        pytest.param(
            {'preset_name': 'default', 'type': 'all'},
            [],
            400,
            id='missed priority_name in query',
        ),
        pytest.param(
            {'priority_name': 'no_preset_name', 'type': 'all'},
            [],
            400,
            id='missed preset_name in query',
        ),
        pytest.param(
            {'priority_name': 'branding', 'preset_name': 'default'},
            [],
            400,
            id='missed type in query',
        ),
        pytest.param(
            {
                'priority_name': 'branding',
                'preset_name': 'not_exists',
                'type': 'all',
            },
            [],
            404,
            id='preset not exists',
        ),
        pytest.param(
            {
                'priority_name': 'not_exists',
                'preset_name': 'default',
                'type': 'all',
            },
            [],
            404,
            id='priority not exists',
        ),
        (
            {
                'priority_name': 'branding',
                'preset_name': 'default',
                'type': 'all',
            },
            [
                _get_preset_version_item(0, NOW, stops_at=NOW + DAY),
                _get_preset_version_item(1, NOW + DAY),
            ],
            200,
        ),
        (
            {
                'priority_name': 'branding',
                'preset_name': 'default',
                'type': 'active',
            },
            [_get_preset_version_item(0, NOW, stops_at=NOW + DAY)],
            200,
        ),
        (
            {
                'priority_name': 'branding',
                'preset_name': 'default',
                'type': 'future',
            },
            [_get_preset_version_item(1, NOW + DAY)],
            200,
        ),
        (
            {
                'priority_name': 'loyalty',
                'preset_name': 'without_versions',
                'type': 'all',
            },
            [],
            200,
        ),
    ],
)
async def test_handler(
        taxi_driver_priority,
        query_params: Dict[str, str],
        expected_versions: List[Dict[str, Any]],
        expected_code: int,
):
    query = '&'.join(f'{k}={v}' for k, v in query_params.items())
    response = await taxi_driver_priority.get(f'{URL}?{query}')
    assert response.status_code == expected_code
    if expected_code != 200:
        return

    versions = response.json()['versions']
    for version in versions:
        for key in ['created_at', 'starts_at', 'stops_at']:
            if key in version:
                version[key] = utils.parse_datetime(version[key])
    assert versions == expected_versions
