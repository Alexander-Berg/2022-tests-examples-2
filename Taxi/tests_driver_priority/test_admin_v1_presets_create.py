import copy
import datetime
from typing import Any
from typing import Dict
from typing import Optional
import uuid

import psycopg2
import pytest

from tests_driver_priority import constants
from tests_driver_priority import db_tools
from tests_driver_priority import utils


CREATE_URL = 'admin/v1/presets/create'
CHECK_CREATE_URL = 'admin/v1/presets/check-create'

NOW = datetime.datetime.now(datetime.timezone.utc)
NOW_TZ = (NOW + datetime.timedelta(hours=3)).replace(
    tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=180),
)

PRIORITY_NAME = 'branding'
DEFAULT_PRESET_NAME = 'default'
CUSTOM_PRESET_NAME = 'custom'
NEW_PRESET_NAME = 'new_preset'
AGGLOMERATIONS = [constants.MSK, constants.SPB]

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


def _upsert_preset(
        data: Dict[str, Any],
        priority_name: str,
        preset_name: str,
        preset_description: Optional[str] = None,
):
    result = copy.deepcopy(data)
    result[priority_name]['presets'].setdefault(
        preset_name, {'is_default': False},
    )
    result[priority_name]['presets'][preset_name].pop('description', None)
    if preset_description:
        result[priority_name]['presets'][preset_name][
            'description'
        ] = preset_description
    return result


def _upsert_agglomerations(
        data: Dict[str, Any],
        priority_name: str,
        preset_name: str,
        agglomerations: Optional[str] = None,
):
    result = copy.deepcopy(data)
    result[priority_name]['presets'][preset_name].pop('agglomerations', None)
    if agglomerations:
        geo_nodes = sorted(list(set(agglomerations)))
        result[priority_name]['presets'][preset_name][
            'agglomerations'
        ] = geo_nodes
    return result


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
        ],
    ),
)
@pytest.mark.parametrize(
    'priority_name, preset_name, description, agglomerations, '
    'expected_code, error_message',
    [
        # create request
        pytest.param(
            PRIORITY_NAME,
            NEW_PRESET_NAME,
            'new description',
            None,
            200,
            None,
            id='create new preset (no agglomerations)',
        ),
        pytest.param(
            PRIORITY_NAME,
            NEW_PRESET_NAME,
            None,
            [constants.MSK, constants.SPB],
            200,
            None,
            id='create new preset with agglomerations',
        ),
        pytest.param(
            PRIORITY_NAME,
            NEW_PRESET_NAME,
            None,
            [constants.MSK, constants.SPB, constants.MSK],
            200,
            None,
            id='create new preset with dup agglomerations',
        ),
        pytest.param(
            'non-existed',
            NEW_PRESET_NAME,
            None,
            None,
            404,
            'Priority "non-existed" does not exist',
            id='no priority exists',
        ),
        pytest.param(
            PRIORITY_NAME,
            DEFAULT_PRESET_NAME,
            None,
            None,
            409,
            'Preset "default" for priority "branding" is already exist',
            id='preset is already existed',
        ),
        pytest.param(
            PRIORITY_NAME,
            NEW_PRESET_NAME,
            None,
            [constants.TULA],
            409,
            'Preset agglomerations [tula] for priority "branding" '
            'is already related',
            id='agglomeration is already related',
        ),
    ],
)
async def test_handler(
        taxi_driver_priority,
        priority_name,
        preset_name,
        description,
        agglomerations,
        expected_code,
        error_message,
        pgsql,
):
    headers = {'X-Idempotency-Token': str(uuid.uuid4())}
    request_body = {
        'priority_name': priority_name,
        'preset': {'name': preset_name},
    }
    if description:
        request_body['preset']['description'] = description
    if agglomerations:
        request_body['preset']['agglomerations'] = agglomerations

    check_response = await taxi_driver_priority.post(
        CHECK_CREATE_URL, request_body, headers=headers,
    )
    assert check_response.status_code == expected_code

    response = await taxi_driver_priority.post(
        CREATE_URL, request_body, headers=headers,
    )
    assert response.status_code == expected_code

    expected_data = DB_DATA
    db = pgsql['driver_priority']
    if expected_code == 200:
        assert response.json()['status'] == 'succeeded'
        utils.validate_check_response(check_response.json(), request_body)
        expected_data = _upsert_preset(
            expected_data, priority_name, preset_name, description,
        )
        expected_data = _upsert_agglomerations(
            expected_data, priority_name, preset_name, agglomerations,
        )
        db_tools.check_recalculation_task(
            db,
            expected_data[priority_name]['presets'][preset_name].get(
                'agglomerations',
            ),
        )
    else:
        db_tools.check_recalculation_task(db, None)
    assert expected_data == db_tools.select_priorities_info(db)

    if error_message is not None:
        assert response.json()['message'] == error_message
