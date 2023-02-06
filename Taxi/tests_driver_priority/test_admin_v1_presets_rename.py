import copy
import datetime
from typing import Any
from typing import Dict
import uuid

import psycopg2
import pytest

from tests_driver_priority import constants
from tests_driver_priority import db_tools
from tests_driver_priority import utils


RENAME_URL = 'admin/v1/presets/rename'
CHECK_RENAME_URL = 'admin/v1/presets/check-rename'
NOW = datetime.datetime.now(datetime.timezone.utc)
NOW_TZ = (NOW + datetime.timedelta(hours=3)).replace(
    tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=180),
)

PRIORITY_NAME = 'branding'
DEFAULT_PRESET_NAME = 'default'
CUSTOM_PRESET_NAME = 'custom'
NEW_PRESET_NAME = 'new_preset'

DB_DATA = {
    PRIORITY_NAME: {
        'is_enabled': True,
        'tanker_keys_prefix': 'tk0',
        'description': 'description',
        'presets': {
            DEFAULT_PRESET_NAME: {
                'is_default': True,
                'description': 'description',
                'versions': [
                    {
                        'sort_order': 0,
                        'rule': {},
                        'temporary_condition': {},
                        'disabled_condition': {},
                        'achievable_condition': {},
                        'achieved_payload': {},
                        'achievable_payload': {},
                        'created_at': NOW_TZ,
                        'starts_at': NOW_TZ,
                    },
                ],
            },
            CUSTOM_PRESET_NAME: {
                'is_default': False,
                'description': 'description',
                'agglomerations': [constants.TULA],
            },
        },
    },
}


def _rename_preset(
        data: Dict[str, Any],
        priority_name: str,
        preset_name: str,
        new_preset_name: str,
):
    result = copy.deepcopy(data)
    preset_data = result[priority_name]['presets'][preset_name]
    del result[priority_name]['presets'][preset_name]
    result[priority_name]['presets'][new_preset_name] = preset_data
    return result


@pytest.mark.pgsql(
    'driver_priority',
    queries=db_tools.join_queries(
        [
            db_tools.insert_priority(0, PRIORITY_NAME, True, 'tk0'),
            db_tools.insert_preset(
                0, 0, DEFAULT_PRESET_NAME, NOW, is_default=True,
            ),
            db_tools.insert_preset(1, 0, CUSTOM_PRESET_NAME, NOW),
            db_tools.insert_version(0, 0, 0, dict(), dict(), NOW, NOW),
            db_tools.insert_preset_relation(constants.TULA, 1),
        ],
    ),
)
@pytest.mark.parametrize(
    'priority_name, preset_name, new_preset_name, '
    'expected_code, error_message',
    [
        pytest.param(
            PRIORITY_NAME,
            CUSTOM_PRESET_NAME,
            NEW_PRESET_NAME,
            200,
            None,
            id='success custom rename',
        ),
        pytest.param(
            PRIORITY_NAME,
            DEFAULT_PRESET_NAME,
            NEW_PRESET_NAME,
            200,
            None,
            id='success default rename',
        ),
        pytest.param(
            PRIORITY_NAME,
            CUSTOM_PRESET_NAME,
            CUSTOM_PRESET_NAME,
            400,
            'New preset name does not have any change',
            id='no rename',
        ),
        pytest.param(
            'non-existed',
            CUSTOM_PRESET_NAME,
            NEW_PRESET_NAME,
            404,
            'Priority \"non-existed\" does not exist',
            id='priority is not found',
        ),
        pytest.param(
            PRIORITY_NAME,
            'non-existed',
            NEW_PRESET_NAME,
            404,
            'Preset \"non-existed\" for priority \"'
            + PRIORITY_NAME
            + '\" does not exist',
            id='preset is not found',
        ),
        pytest.param(
            PRIORITY_NAME,
            CUSTOM_PRESET_NAME,
            DEFAULT_PRESET_NAME,
            409,
            'Preset \"'
            + DEFAULT_PRESET_NAME
            + '\" for priority \"'
            + PRIORITY_NAME
            + '\" is already presented',
            id='preset name conflict',
        ),
    ],
)
async def test_handler(
        taxi_driver_priority,
        priority_name,
        preset_name,
        new_preset_name,
        expected_code,
        error_message,
        pgsql,
):
    headers = {'X-Idempotency-Token': str(uuid.uuid4())}
    request_body = {
        'priority_name': priority_name,
        'preset': {'current_name': preset_name, 'new_name': new_preset_name},
    }

    check_response = await taxi_driver_priority.post(
        CHECK_RENAME_URL, request_body, headers=headers,
    )
    assert check_response.status_code == expected_code

    response = await taxi_driver_priority.post(
        RENAME_URL, request_body, headers=headers,
    )
    assert response.status_code == expected_code

    expected_data = DB_DATA
    if expected_code == 200:
        assert response.json()['status'] == 'succeeded'

        utils.validate_check_response(
            check_response.json(),
            request_body,
            expected_diff={
                'current': {'name': preset_name},
                'new': {'name': new_preset_name},
            },
        )

        expected_data = _rename_preset(
            expected_data, priority_name, preset_name, new_preset_name,
        )

    assert expected_data == db_tools.select_priorities_info(
        pgsql['driver_priority'],
    )

    if error_message is not None:
        assert response.json()['message'] == error_message
