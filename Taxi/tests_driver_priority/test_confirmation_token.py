import datetime

import pytest

from tests_driver_priority import constants
from tests_driver_priority import db_tools


CREATE_URL = 'admin/v1/presets/create'

NOW = datetime.datetime.now(datetime.timezone.utc)

PRIORITY_NAME = 'branding'
DEFAULT_PRESET_NAME = 'default'
CUSTOM_PRESET_NAME = 'custom'
NEW_PRESET_NAME = 'new_preset'
TOKEN = 'aaabbbccc'
AGGLOMERATIONS = [constants.MSK, constants.SPB]


def _token_insert_query(token: str) -> str:
    return (
        f'INSERT INTO service.request_results (confirmation_token, '
        f'response_code, valid_until) VALUES (\'{token}\', 200, '
        f'\'{NOW.isoformat()}\'::timestamp)'
    )


@pytest.mark.now(NOW.isoformat())
@pytest.mark.pgsql(
    'driver_priority',
    queries=db_tools.join_queries(
        [
            db_tools.insert_priority(0, PRIORITY_NAME, True, 'tk0'),
            db_tools.insert_preset(
                0, 0, DEFAULT_PRESET_NAME, NOW, is_default=True,
            ),
            # There is no id=1 to avoid duplicate key value by insert
            db_tools.insert_preset(2, 0, CUSTOM_PRESET_NAME, NOW),
            db_tools.insert_version(0, 0, 0, dict(), dict(), NOW, NOW),
            db_tools.insert_preset_relation(constants.TULA, 2),
            _token_insert_query(TOKEN),
        ],
    ),
)
async def test_handler(taxi_driver_priority, pgsql):
    data_before = db_tools.select_priorities_info(pgsql['driver_priority'])

    headers = {'X-Idempotency-Token': TOKEN}
    request_body = {
        'priority_name': PRIORITY_NAME,
        'preset': {'name': NEW_PRESET_NAME, 'agglomerations': [constants.MSK]},
    }
    response = await taxi_driver_priority.post(
        CREATE_URL, request_body, headers=headers,
    )
    assert response.status_code == 200

    data_after = db_tools.select_priorities_info(pgsql['driver_priority'])

    assert data_before == data_after
