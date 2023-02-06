import copy
import datetime
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
import uuid

import pytest

from tests_driver_priority import db_tools
from tests_driver_priority import utils


HANDLER_URL = 'admin/v1/versions/update-time'
CHECK_URL = 'admin/v1/versions/check-update-time'
NOW = datetime.datetime.now(datetime.timezone.utc)


def _use_utc_tz(timestamp: datetime.datetime) -> datetime.datetime:
    return (timestamp - datetime.timedelta(hours=3)).replace(
        tzinfo=datetime.timezone.utc,
    )


@pytest.mark.now(NOW.isoformat())
@pytest.mark.pgsql(
    'driver_priority',
    queries=db_tools.get_pg_default_data(NOW)
    + [
        db_tools.insert_preset(9, 0, 'future_preset', NOW),
        db_tools.insert_version(
            13,
            9,
            0,
            db_tools.DEFAULT_RULE,
            db_tools.DEFAULT_ACHIEVED_PAYLOAD,
            NOW,
            NOW + db_tools.DAY,
            stops_at=None,
        ),
        db_tools.insert_version(
            14,
            4,
            1,
            db_tools.DEFAULT_RULE,
            db_tools.DEFAULT_ACHIEVED_PAYLOAD,
            NOW,
            NOW + db_tools.DAY,
            stops_at=None,
        ),
    ]
    + db_tools.get_sequence_ids_update_queries(),
)
@pytest.mark.parametrize(
    'priority_name, preset_name, version_id, starts_at, stops_at, '
    'expected_updates, expected_code',
    [
        pytest.param(
            'not_found',
            'default',
            0,
            NOW,
            None,
            [],
            404,
            id='priority not found',
        ),
        pytest.param(
            'branding',
            'not_found',
            0,
            NOW,
            None,
            [],
            404,
            id='preset not found',
        ),
        pytest.param(
            'branding',
            'default',
            2,
            NOW,
            None,
            [],
            404,
            id='version with id not found',
        ),
        pytest.param(
            'branding',
            'future_preset',
            13,
            NOW - db_tools.MINUTE,
            None,
            [],
            409,
            id='try set starts_at in past',
        ),
        pytest.param(
            'branding',
            'future_preset',
            13,
            NOW + db_tools.HOUR,
            NOW + db_tools.MINUTE,
            [],
            400,
            id='try set starts_at after stops_at',
        ),
        pytest.param(
            'disabled',
            'default',
            7,
            NOW + db_tools.MINUTE,
            None,
            [],
            409,
            id='try change starts_at time for started at NOW version',
        ),
        pytest.param(
            'disabled',
            'default',
            7,
            NOW,
            NOW + db_tools.MINUTE,
            [],
            409,
            id='try set stops_at time for singe version of default preset',
        ),
        pytest.param(
            'branding',
            'default',
            1,
            NOW + db_tools.DAY,
            NOW + db_tools.WEEK,
            [],
            409,
            id='try set stops_at time for last version of default preset',
        ),
        pytest.param(
            'branding',
            'default',
            1,
            NOW + db_tools.DAY,
            None,
            [],
            409,
            id='do not update version without any change',
        ),
        pytest.param(
            'loyalty',
            'outdated_preset',
            6,
            NOW - db_tools.DAY,
            NOW + db_tools.DAY,
            [],
            409,
            id='try enable archived version with stops_at time in past',
        ),
        pytest.param(
            'loyalty',
            'actual_preset',
            11,
            NOW - db_tools.DAY,
            NOW - db_tools.MINUTE,
            [],
            400,
            id='try to move stops_at before current time for version, started '
            'before current time',
        ),
        pytest.param(
            'branding',
            'default',
            1,
            NOW + db_tools.WEEK,
            None,
            [
                {
                    'id': 0,
                    'created_at': NOW,
                    'starts_at': NOW,
                    'stops_at': NOW + db_tools.WEEK,
                },
                {'id': 1, 'created_at': NOW, 'starts_at': NOW + db_tools.WEEK},
            ],
            200,
            id='increase starts_at time for future version of default preset',
        ),
        pytest.param(
            'empty_relations',
            'default',
            8,
            NOW + (db_tools.HOUR * 2),
            NOW + db_tools.DAY,
            [
                {
                    'id': 8,
                    'created_at': NOW,
                    'starts_at': NOW + (db_tools.HOUR * 2),
                    'stops_at': NOW + db_tools.DAY,
                },
            ],
            200,
            id='increase starts_at time for first future version of default '
            'preset',
        ),
        pytest.param(
            'empty_relations',
            'default',
            8,
            NOW + db_tools.MINUTE,
            NOW + db_tools.DAY,
            [
                {
                    'id': 8,
                    'created_at': NOW,
                    'starts_at': NOW + db_tools.MINUTE,
                    'stops_at': NOW + db_tools.DAY,
                },
            ],
            200,
            id='decrease starts_at time for first future version of default '
            'preset',
        ),
        pytest.param(
            'branding',
            'default',
            0,
            NOW,
            NOW + db_tools.WEEK,
            [
                {
                    'id': 0,
                    'created_at': NOW,
                    'starts_at': NOW,
                    'stops_at': NOW + db_tools.WEEK,
                },
                {'id': 1, 'created_at': NOW, 'starts_at': NOW + db_tools.WEEK},
            ],
            200,
            id='increase stops_at time for current version of default preset',
        ),
        pytest.param(
            'branding',
            'default',
            1,
            NOW + db_tools.HOUR,
            None,
            [
                {
                    'id': 0,
                    'created_at': NOW,
                    'starts_at': NOW,
                    'stops_at': NOW + db_tools.HOUR,
                },
                {'id': 1, 'created_at': NOW, 'starts_at': NOW + db_tools.HOUR},
            ],
            200,
            id='decrease starts_at time for future version of default preset',
        ),
        pytest.param(
            'branding',
            'default',
            0,
            NOW,
            NOW + db_tools.HOUR,
            [
                {
                    'id': 0,
                    'created_at': NOW,
                    'starts_at': NOW,
                    'stops_at': NOW + db_tools.HOUR,
                },
                {'id': 1, 'created_at': NOW, 'starts_at': NOW + db_tools.HOUR},
            ],
            200,
            id='decrease stops_at time for current version of default preset',
        ),
        pytest.param(
            'empty_relations',
            'default',
            9,
            NOW + db_tools.TWO_DAYS,
            NOW + db_tools.SIX_DAYS,
            [
                {
                    'id': 8,
                    'created_at': NOW,
                    'starts_at': NOW + db_tools.HOUR,
                    'stops_at': NOW + db_tools.TWO_DAYS,
                },
                {
                    'id': 9,
                    'created_at': NOW,
                    'starts_at': NOW + db_tools.TWO_DAYS,
                    'stops_at': NOW + db_tools.SIX_DAYS,
                },
                {
                    'id': 10,
                    'created_at': NOW,
                    'starts_at': NOW + db_tools.SIX_DAYS,
                },
            ],
            200,
            id='shorten time for future finite version of default preset and '
            'cause nearest versions to shift',
        ),
        pytest.param(
            'empty_relations',
            'default',
            9,
            NOW + db_tools.DAY - db_tools.MINUTE,
            NOW + db_tools.WEEK + db_tools.MINUTE,
            [],
            409,
            id='forbid more than one version intersection on both ends of '
            'current version',
        ),
        pytest.param(
            'empty_relations',
            'default',
            8,
            NOW + db_tools.MINUTE,
            NOW + db_tools.SIX_DAYS,
            [
                {
                    'id': 8,
                    'created_at': NOW,
                    'starts_at': NOW + db_tools.MINUTE,
                    'stops_at': NOW + db_tools.SIX_DAYS,
                },
                {
                    'id': 9,
                    'created_at': NOW,
                    'starts_at': NOW + db_tools.SIX_DAYS,
                    'stops_at': NOW + db_tools.WEEK,
                },
            ],
            200,
            id='move time for first future finite version of default preset',
        ),
        pytest.param(
            'empty_relations',
            'default',
            8,
            NOW + db_tools.MINUTE,
            NOW + db_tools.WEEK,
            [],
            409,
            id='full version inclusion',
        ),
        pytest.param(
            'branding',
            'actual_preset',
            2,
            NOW,
            NOW + db_tools.MINUTE,
            [
                {
                    'id': 2,
                    'created_at': NOW,
                    'starts_at': NOW,
                    'stops_at': NOW + db_tools.MINUTE,
                },
            ],
            200,
            id='move stops_at earlier for active version, next not affected',
        ),
        pytest.param(
            'branding',
            'actual_preset',
            2,
            NOW,
            NOW + db_tools.WEEK,
            [
                {
                    'id': 2,
                    'created_at': NOW,
                    'starts_at': NOW,
                    'stops_at': NOW + db_tools.WEEK,
                },
                {'id': 3, 'created_at': NOW, 'starts_at': NOW + db_tools.WEEK},
            ],
            200,
            id='move stops_at later for active version',
        ),
        pytest.param(
            'branding',
            'actual_preset',
            3,
            NOW + db_tools.MINUTE,
            None,
            [
                {
                    'id': 2,
                    'created_at': NOW,
                    'starts_at': NOW,
                    'stops_at': NOW + db_tools.MINUTE,
                },
                {
                    'id': 3,
                    'created_at': NOW,
                    'starts_at': NOW + db_tools.MINUTE,
                },
            ],
            200,
            id='move starts_at earlier for last version after active',
        ),
        pytest.param(
            'branding',
            'actual_preset',
            3,
            NOW + db_tools.DAY,
            NOW + db_tools.WEEK,
            [
                {
                    'id': 3,
                    'created_at': NOW,
                    'starts_at': NOW + db_tools.DAY,
                    'stops_at': NOW + db_tools.WEEK,
                },
            ],
            200,
            id='set both times later for last version with creating a gap',
        ),
        pytest.param(
            'branding',
            'actual_preset',
            3,
            NOW + db_tools.HOUR,
            NOW + db_tools.DAY,
            [
                {
                    'id': 3,
                    'created_at': NOW,
                    'starts_at': NOW + db_tools.HOUR,
                    'stops_at': NOW + db_tools.DAY,
                },
            ],
            200,
            id='set stops_at for infinite version',
        ),
        pytest.param(
            'empty_relations',
            'default',
            8,
            NOW + db_tools.HOUR,
            NOW + db_tools.WEEK,
            [],
            409,
            id='full intersection with existing version',
        ),
        pytest.param(
            'empty_relations',
            'default',
            9,
            NOW + db_tools.HOUR,
            NOW + db_tools.WEEK,
            [],
            409,
            id='full intersection with existing version',
        ),
        pytest.param(
            'branding',
            'preset2',
            4,
            NOW + db_tools.MINUTE,
            None,
            [{'id': 4, 'created_at': NOW, 'starts_at': NOW + db_tools.MINUTE}],
            200,
            id='remote stops_at time for last finite version',
        ),
        pytest.param(
            'loyalty',
            'default',
            5,
            NOW + db_tools.MINUTE,
            None,
            [],
            409,
            id='try to move starts_at from past',
        ),
        pytest.param(
            'empty_relations',
            'default',
            9,
            NOW + db_tools.MINUTE,
            NOW + db_tools.HOUR,
            [],
            409,
            id='move finite version for default preset to another place with '
            'creating a gap',
        ),
    ],
)
async def test_handler(
        taxi_driver_priority,
        priority_name: str,
        preset_name: str,
        version_id: int,
        starts_at: datetime.datetime,
        stops_at: Optional[datetime.datetime],
        expected_updates: List[Dict[str, Any]],
        expected_code,
        pgsql,
):
    db = pgsql['driver_priority']

    versions_query = (
        f'SELECT id,created_at,starts_at,stops_at FROM state.preset_versions'
        f' WHERE preset_id IN (SELECT presets.id FROM state.presets JOIN '
        f'state.priorities ON priorities.id = presets.priority_id WHERE '
        f'presets.name=\'{preset_name}\' AND priorities.name=\'{priority_name}'
        f'\') ORDER BY preset_versions.id'
    )
    versions_before = db_tools.select_named(versions_query, db)

    headers = {'X-Idempotency-Token': str(uuid.uuid4())}
    body: Dict[str, Any] = {
        'priority_name': priority_name,
        'preset_name': preset_name,
        'version': {'id': version_id, 'starts_at': starts_at.isoformat()},
    }
    if stops_at is not None:
        body['version']['stops_at'] = stops_at.isoformat()

    check_response = await taxi_driver_priority.post(
        CHECK_URL, body, headers=headers,
    )
    assert check_response.status_code == expected_code

    response = await taxi_driver_priority.post(
        HANDLER_URL, body, headers=headers,
    )
    assert response.status_code == expected_code

    if response.status_code != 200:
        assert response.json()['message']
        assert check_response.json()['message']
        return

    # make expected updates in previous versions
    version_before_update = None
    for update in expected_updates:
        has_update = False
        for pos, version in enumerate(versions_before):
            if version['id'] == update['id']:
                if version['id'] == version_id:
                    version_before_update = copy.deepcopy(versions_before[pos])

                versions_before[pos] = {
                    'id': update['id'],
                    'created_at': utils.add_local_tz(update['created_at']),
                    'starts_at': utils.add_local_tz(update['starts_at']),
                    'stops_at': (
                        None
                        if update.get('stops_at') is None
                        else utils.add_local_tz(update['stops_at'])
                    ),
                }
                has_update = True

        assert has_update
    assert version_before_update is not None

    # compare previous state with actual
    versions_after = db_tools.select_named(versions_query, db)
    assert versions_before == versions_after

    current_state = {
        'id': version_before_update['id'],
        'starts_at': _use_utc_tz(version_before_update['starts_at']),
    }
    if version_before_update['stops_at'] is not None:
        current_state['stops_at'] = _use_utc_tz(
            version_before_update['stops_at'],
        )
    utils.validate_check_version_response(
        check_response.json(),
        body,
        preset_name,
        expected_diff={'new': body['version'], 'current': current_state},
    )

    assert response.json()['status'] == 'succeeded'
