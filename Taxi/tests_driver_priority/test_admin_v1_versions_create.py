import copy
import datetime
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
import uuid

import pytest

from tests_driver_priority import constants
from tests_driver_priority import db_tools
from tests_driver_priority import utils


HANDLER_URL = 'admin/v1/versions/create'
CHECK_URL = 'admin/v1/versions/check-create'
NOW = datetime.datetime.now(datetime.timezone.utc)

PG_QUERIES = (
    db_tools.get_pg_default_data(NOW)
    + db_tools.join_queries(
        [
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
            db_tools.insert_priority(
                4,
                'activity',
                True,
                'activity',
                can_contain_activity_rule=True,
            ),
            db_tools.insert_preset(
                10, 4, 'default_for_activity', NOW, is_default=True,
            ),
            db_tools.insert_version(
                14,
                10,
                10,
                db_tools.ACTIVITY_RULE,
                db_tools.DEFAULT_ACHIEVED_PAYLOAD,
                NOW,
                NOW,
            ),
        ],
    )
    + db_tools.get_sequence_ids_update_queries()
)
_NEW_PRESET = {
    'name': 'new_preset',
    'description': 'some info',
    'agglomerations': [constants.SPB, constants.TULA],
}


def _get_preset_id(db, priority_name: str, preset_name: str) -> Optional[int]:
    query = (
        f'SELECT presets.id FROM state.presets'
        f' JOIN state.priorities ON priorities.id = presets.priority_id'
        f' WHERE presets.name=\'{preset_name}\''
        f' AND priorities.name=\'{priority_name}\''
    )
    rows = db_tools.select_named(query, db)
    assert 0 <= len(rows) <= 1
    return rows[0]['id'] if rows else None


def _get_priority_preset_versions(db, preset_id: int):
    versions_query = (
        f'SELECT id,created_at,starts_at,stops_at, rule, temporary_condition,'
        f'disabled_condition, achievable_condition, achieved_payload, '
        f'achievable_payload FROM state.preset_versions'
        f' WHERE preset_id={preset_id} ORDER BY preset_versions.id'
    )
    return db_tools.select_named(versions_query, db)


def _make_last_created_version(db, rule, starts_at, stops_at):
    new_version_id = db_tools.select_named(
        'SELECT max(id) AS id FROM state.preset_versions', db,
    )[0]['id']
    return {
        'id': new_version_id,
        'created_at': utils.add_local_tz(NOW),
        'starts_at': utils.add_local_tz(starts_at),
        'stops_at': None if stops_at is None else utils.add_local_tz(stops_at),
        'rule': rule,
        'achieved_payload': db_tools.DEFAULT_ACHIEVED_PAYLOAD,
        'achievable_payload': {},
        'temporary_condition': {},
        'disabled_condition': {},
        'achievable_condition': {},
    }


def _check_created_preset(
        db, priority_name: str, preset_name: str, expected_preset_data,
):
    presets: List[Any] = db_tools.select_named(
        f'SELECT presets.id, presets.name, presets.description FROM '
        f'state.presets JOIN state.priorities ON priorities.id = '
        f'presets.priority_id WHERE priorities.name =\'{priority_name}\' AND '
        f'presets.name = \'{preset_name}\'',
        db,
    )

    if not presets:
        assert expected_preset_data is None
        return

    preset_id = db_tools.select_named(
        'SELECT max(id) AS id FROM state.presets', db,
    )[0]['id']
    assert len(presets) == 1
    preset = presets[0]
    assert preset_id == preset['id']
    preset_agglomerations = db_tools.select_named(
        f'SELECT presets_relations.agglomeration FROM state.presets_relations '
        f'JOIN state.presets ON presets_relations.preset_id = presets.id '
        f'WHERE preset_id={preset_id}',
        db,
    )

    preset_data = {'name': preset['name']}
    if preset['description']:
        preset_data['description'] = preset['description']
    if preset_agglomerations:
        preset_data['agglomerations'] = sorted(
            [row['agglomeration'] for row in preset_agglomerations],
        )

    assert preset_data == expected_preset_data


def _make_original_version_diff(db, version_id: Optional[int]):
    if version_id is None:
        return {}

    query = (
        f'SELECT preset_versions.starts_at, rule, preset_versions.stops_at, '
        f'sort_order, temporary_condition as temporary, '
        f'disabled_condition as disabled, achievable_condition as achievable, '
        f'achieved_payload, achievable_payload FROM state.preset_versions '
        f'WHERE preset_versions.id = {version_id}'
    )
    rows = db_tools.select_named(query, db)
    if not rows:
        return {}
    version = rows[0]
    result = {
        'version': {
            'sort_order': version['sort_order'],
            'starts_at': version['starts_at'],
        },
        'rule': version['rule'],
        'payloads': {'achieved': version['achieved_payload']},
        'conditions': {},
    }
    if version['stops_at']:
        result['version']['stops_at'] = version['stops_at']
    for condition_key in ['temporary', 'disabled', 'achievable']:
        if version[condition_key]:
            result['conditions'][condition_key] = version[condition_key]
    if version['achievable_payload']:
        result['payloads']['achievable_payload'] = version[
            'achievable_payload'
        ]
    return result


def _make_new_version_diff(data, starts_at, stops_at):
    result = {
        'version': copy.deepcopy(data['version']),
        'rule': copy.deepcopy(data['rule']),
        'payloads': copy.deepcopy(data['payloads']),
        'conditions': copy.deepcopy(data['conditions']),
    }
    result['version']['starts_at'] = starts_at
    if stops_at is not None:
        result['version']['stops_at'] = stops_at
    return result


@pytest.mark.now(NOW.isoformat())
@pytest.mark.pgsql('driver_priority', queries=PG_QUERIES)
@pytest.mark.parametrize(
    'priority_name,preset_name,rule,starts_at,stops_at,original_version_id,'
    'expected_update,expected_code',
    [
        # three cases with both infinite versions
        pytest.param(
            'branding',
            'default',
            db_tools.DEFAULT_RULE,
            NOW + db_tools.WEEK,
            None,
            1,
            {
                'id': 1,
                'created_at': NOW,
                'starts_at': NOW + db_tools.DAY,
                'stops_at': NOW + db_tools.WEEK,
            },
            200,
            id='new version continues existing, both infinite',
        ),
        pytest.param(
            'branding',
            'default',
            db_tools.DEFAULT_RULE,
            NOW + db_tools.DAY,
            None,
            None,
            None,
            400,
            id='new version has the same starts/stops time, both infinite',
        ),
        pytest.param(
            'branding',
            'future_preset',
            db_tools.DEFAULT_RULE,
            NOW + db_tools.HOUR,
            None,
            None,
            None,
            400,
            id='new infinite version starts before existing infinite',
        ),
        # next cases have infinite existing version and finite new one
        pytest.param(
            'branding',
            'future_preset',
            db_tools.DEFAULT_RULE,
            NOW + db_tools.HOUR,
            NOW + db_tools.DAY,
            1,
            None,
            200,
            id='new finite version starts and stops before existing infinite, '
            'no change',
        ),
        pytest.param(
            'branding',
            'future_preset',
            db_tools.DEFAULT_RULE,
            NOW + db_tools.HOUR,
            NOW + db_tools.WEEK,
            13,
            {
                'id': 13,
                'created_at': NOW,
                'starts_at': NOW + db_tools.WEEK,
                'stops_at': None,
            },
            200,
            id='new finite version starts before and shifts start of existing '
            'infinite',
        ),
        pytest.param(
            'branding',
            'future_preset',
            db_tools.DEFAULT_RULE,
            NOW + db_tools.DAY,
            NOW + db_tools.WEEK,
            13,
            {
                'id': 13,
                'created_at': NOW,
                'starts_at': NOW + db_tools.WEEK,
                'stops_at': None,
            },
            200,
            id='new finite version starts at the same time as existing '
            'infinite',
        ),
        pytest.param(
            'branding',
            'actual_preset',
            db_tools.DEFAULT_RULE,
            NOW + db_tools.DAY,
            NOW + db_tools.WEEK,
            None,
            None,
            400,
            id='new finite version starts after existing infinite version',
        ),
        # next cases have finite existing version and infinite new
        pytest.param(
            'branding',
            'future_preset',
            db_tools.DEFAULT_RULE,
            NOW + db_tools.HOUR,
            None,
            None,
            None,
            400,
            id='new infinite version starts before existing finite',
        ),
        pytest.param(
            'branding',
            'future_preset',
            db_tools.DEFAULT_RULE,
            NOW + db_tools.DAY,
            None,
            None,
            None,
            400,
            id='new infinite version starts exactly with existing finite',
        ),
        pytest.param(
            'branding',
            'actual_preset',
            db_tools.DEFAULT_RULE,
            NOW + db_tools.DAY,
            None,
            3,
            {
                'id': 3,
                'created_at': NOW,
                'starts_at': NOW + db_tools.HOUR,
                'stops_at': NOW + db_tools.DAY,
            },
            200,
            id='new infinite version has partial intersection with existing '
            'infinite, shift stops_at',
        ),
        pytest.param(
            'branding',
            'preset2',
            db_tools.DEFAULT_RULE,
            NOW + db_tools.WEEK,
            None,
            None,
            None,
            200,
            id='new infinite version after existing finite, without updates',
        ),
        # next cases have both finite versions
        pytest.param(
            'branding',
            'preset2',
            db_tools.DEFAULT_RULE,
            NOW + db_tools.MINUTE * 30,
            NOW + db_tools.MINUTE * 40,
            None,
            None,
            200,
            id='new version stops before existing',
        ),
        pytest.param(
            'branding',
            'preset2',
            db_tools.DEFAULT_RULE,
            NOW + db_tools.MINUTE * 30,
            NOW + db_tools.HOUR + db_tools.MINUTE * 30,
            4,
            {
                'id': 4,
                'created_at': NOW,
                'starts_at': NOW + db_tools.HOUR + db_tools.MINUTE * 30,
                'stops_at': NOW + db_tools.DAY,
            },
            200,
            id='new version starts before existing but stops when its active',
        ),
        pytest.param(
            'branding',
            'preset2',
            db_tools.DEFAULT_RULE,
            NOW + db_tools.MINUTE * 30,
            NOW + db_tools.DAY,
            None,
            None,
            400,
            id='new version starts before existing and stops exactly as it',
        ),
        pytest.param(
            'branding',
            'preset2',
            db_tools.DEFAULT_RULE,
            NOW + db_tools.MINUTE * 30,
            NOW + db_tools.WEEK,
            None,
            None,
            400,
            id='new version fully include existing, stops after it',
        ),
        pytest.param(
            'branding',
            'preset2',
            db_tools.DEFAULT_RULE,
            NOW + db_tools.HOUR,
            NOW + db_tools.DAY,
            None,
            None,
            400,
            id='new version has the same duration as existing, with stop time',
        ),
        pytest.param(
            'branding',
            'preset2',
            db_tools.DEFAULT_RULE,
            NOW + db_tools.HOUR,
            NOW + db_tools.HOUR + db_tools.MINUTE * 30,
            4,
            {
                'id': 4,
                'created_at': NOW,
                'starts_at': NOW + db_tools.HOUR + db_tools.MINUTE * 30,
                'stops_at': NOW + db_tools.DAY,
            },
            200,
            id='existing version include new with the same start time',
        ),
        pytest.param(
            'branding',
            'preset2',
            db_tools.DEFAULT_RULE,
            NOW + db_tools.HOUR + db_tools.MINUTE,
            NOW + db_tools.HOUR + db_tools.MINUTE * 30,
            None,
            None,
            400,
            id='existing version fully include new',
        ),
        pytest.param(
            'branding',
            'preset2',
            db_tools.DEFAULT_RULE,
            NOW + db_tools.DAY - db_tools.MINUTE * 30,
            NOW + db_tools.DAY,
            4,
            {
                'id': 4,
                'created_at': NOW,
                'starts_at': NOW + db_tools.HOUR,
                'stops_at': NOW + db_tools.DAY - db_tools.MINUTE * 30,
            },
            200,
            id='existing version include new with the same stops time',
        ),
        pytest.param(
            'branding',
            'preset2',
            db_tools.DEFAULT_RULE,
            NOW + db_tools.DAY - db_tools.MINUTE * 30,
            NOW + db_tools.DAY + db_tools.MINUTE * 30,
            1,
            {
                'id': 4,
                'created_at': NOW,
                'starts_at': NOW + db_tools.HOUR,
                'stops_at': NOW + db_tools.DAY - db_tools.MINUTE * 30,
            },
            200,
            id='new version stops after existing but starts when its active',
        ),
        pytest.param(
            'branding',
            'preset2',
            db_tools.DEFAULT_RULE,
            NOW + (db_tools.HOUR * 12),
            NOW + db_tools.DAY,
            4,
            {
                'id': 4,
                'created_at': NOW,
                'starts_at': NOW + db_tools.HOUR,
                'stops_at': NOW + (db_tools.HOUR * 12),
            },
            200,
            id='new version starts after existing',
        ),
        pytest.param(
            'branding',
            'preset2',
            db_tools.DEFAULT_RULE,
            NOW + db_tools.DAY,
            NOW + db_tools.WEEK,
            None,
            None,
            200,
            id='new version starts exactly after existing, no gap',
        ),
        pytest.param(
            'branding',
            'preset2',
            db_tools.DEFAULT_RULE,
            NOW + db_tools.DAY + db_tools.HOUR,
            NOW + db_tools.WEEK,
            None,
            None,
            200,
            id='new version starts after existing, with a gap',
        ),
        # check special restrictions for handler
        pytest.param(
            'branding',
            'actual_preset',
            db_tools.DEFAULT_RULE,
            NOW + db_tools.HOUR,
            None,
            None,
            None,
            400,
            id='new version has the same duration as existing, without stop '
            'time',
        ),
        pytest.param(
            'branding',
            'default',
            db_tools.DEFAULT_RULE,
            NOW + db_tools.WEEK,
            NOW + db_tools.WEEK + db_tools.HOUR,
            None,
            None,
            400,
            id='try to add finite version for default preset',
        ),
        pytest.param(
            'branding',
            'default',
            db_tools.DEFAULT_RULE,
            NOW + db_tools.HOUR,
            NOW + db_tools.DAY,
            None,
            None,
            400,
            id='attempt to add correct version for default preset, without '
            'invariant violation, but currently forbidden',
        ),
        pytest.param(
            'branding',
            'actual_preset',
            db_tools.DEFAULT_RULE,
            NOW + db_tools.MINUTE,
            NOW + db_tools.DAY,
            None,
            None,
            400,
            id='new version intersect more than one existing versions',
        ),
        pytest.param(
            'branding',
            'preset2',
            db_tools.DEFAULT_RULE,
            NOW + db_tools.MINUTE * 10,
            NOW + db_tools.WEEK,
            None,
            None,
            400,
            id='new finite version includes existing finite version',
        ),
        pytest.param(
            'empty_relations',
            'default',
            db_tools.DEFAULT_RULE,
            NOW + db_tools.WEEK,
            None,
            None,
            None,
            404,
            id='tanker key is not found',
        ),
        pytest.param(
            'branding',
            'future_preset',
            db_tools.ACTIVITY_RULE,
            NOW + db_tools.WEEK,
            None,
            None,
            None,
            409,
            id='activity version created for non-activity priority',
        ),
        pytest.param(
            'activity',
            'default_for_activity',
            db_tools.ACTIVITY_RULE,
            NOW + db_tools.HOUR,
            None,
            13,
            {
                'id': 14,
                'created_at': NOW,
                'starts_at': NOW,
                'stops_at': NOW + db_tools.HOUR,
            },
            200,
            id='activity version created for activity priority',
        ),
        pytest.param(
            'loyalty',
            'default',
            db_tools.WRONG_TOPIC_RULE,
            NOW + db_tools.WEEK,
            None,
            None,
            None,
            400,
            id='tag has no relation with priority topic',
        ),
        pytest.param(
            'branding',
            'actual_preset',
            db_tools.WRONG_VALUES_RANKED_RULE,
            NOW + db_tools.DAY,
            None,
            None,
            None,
            400,
            id='incorrect ranked rule',
        ),
        pytest.param(
            'branding',
            'actual_preset',
            db_tools.WRONG_VALUES_RANKED_RULE,
            NOW + db_tools.DAY,
            None,
            None,
            None,
            400,
            id='incorrect excluding rule',
        ),
    ],
)
async def test_handler(
        taxi_driver_priority,
        priority_name: str,
        preset_name: str,
        rule: Dict[str, Any],
        starts_at: datetime.datetime,
        stops_at: Optional[datetime.datetime],
        original_version_id: Optional[int],
        expected_update: Optional[Dict[str, Any]],
        expected_code,
        pgsql,
):
    db = pgsql['driver_priority']

    preset_id = _get_preset_id(db, priority_name, preset_name)
    versions_before = (
        _get_priority_preset_versions(db, preset_id)
        if preset_id is not None
        else []
    )

    headers = {'X-Idempotency-Token': str(uuid.uuid4())}
    body: Dict[str, Any] = {
        'priority_name': priority_name,
        'preset_name': preset_name,
        'version': {'sort_order': 123, 'starts_at': starts_at.isoformat()},
        'rule': rule,
        'payloads': db_tools.DEFAULT_PAYLOADS,
        'conditions': {},
    }
    if stops_at is not None:
        body['version']['stops_at'] = stops_at.isoformat()
    if original_version_id is not None:
        body['version']['original_version_id'] = original_version_id

    new_diff = _make_new_version_diff(body, starts_at, stops_at)
    current_diff = _make_original_version_diff(db, original_version_id)

    check_response = await taxi_driver_priority.post(
        CHECK_URL, body, headers=headers,
    )
    assert check_response.status_code == expected_code

    response = await taxi_driver_priority.post(
        HANDLER_URL, body, headers=headers,
    )
    assert response.status_code == expected_code

    # update single version, if necessary
    if expected_update is not None:
        has_update = False
        for pos, version in enumerate(versions_before):
            if version['id'] == expected_update['id']:
                for key in expected_update.keys():
                    versions_before[pos][key] = expected_update[key]
                has_update = True
        assert has_update

    if response.status_code != 200:
        # check error message existence
        assert response.json()['message']
        assert check_response.json()['message']
    else:
        versions_before.append(
            _make_last_created_version(db, rule, starts_at, stops_at),
        )
        utils.validate_check_version_response(
            check_response.json(),
            body,
            preset_name if preset_id is not None else None,
            expected_diff={'current': current_diff, 'new': new_diff},
        )

    # compare previous state with actual
    versions_after = (
        _get_priority_preset_versions(db, preset_id)
        if preset_id is not None
        else []
    )
    assert versions_before == versions_after
    # TODO: create existing priority with activity rule
    # and try to add version for another priority


@pytest.mark.now(NOW.isoformat())
@pytest.mark.pgsql('driver_priority', queries=PG_QUERIES)
@pytest.mark.parametrize(
    'priority_name, request_preset_name, new_preset, expected_version_update, '
    'expected_preset, expected_code',
    [
        pytest.param(
            'branding',
            None,
            None,
            None,
            None,
            400,
            id='missing existing and new preset',
        ),
        pytest.param(
            'branding',
            'preset2',
            _NEW_PRESET,
            None,
            None,
            400,
            id='existing and new preset passed together',
        ),
        pytest.param(
            'branding',
            'preset2',
            None,
            None,
            None,
            200,
            id='new version creating',
        ),
        pytest.param(
            'branding',
            None,
            _NEW_PRESET,
            None,
            _NEW_PRESET,
            200,
            id='new version and preset creating',
        ),
        pytest.param(
            'branding',
            None,
            {'name': 'new_preset', 'agglomerations': [constants.MSK]},
            None,
            None,
            409,
            id='new preset has agglomerations intersection',
        ),
        pytest.param(
            'branding',
            None,
            {'name': 'preset2'},
            None,
            None,
            409,
            id='new preset has the same name with existing one',
        ),
        pytest.param(
            'branding',
            None,
            {'name': 'simple_preset'},
            None,
            {'name': 'simple_preset'},
            200,
            id='new version and preset without agglomerations',
        ),
        pytest.param(
            'branding',
            None,
            {'name': 'new_preset', 'agglomerations': [constants.TULA]},
            None,
            {'name': 'new_preset', 'agglomerations': [constants.TULA]},
            200,
            id='new version and preset without description',
        ),
    ],
)
async def test_version_create_with_preset(
        priority_name: str,
        request_preset_name: Optional[str],
        new_preset: Optional[Dict[str, Any]],
        expected_version_update: Optional[Dict[str, Any]],
        expected_preset: Optional[Dict[str, Any]],
        expected_code: int,
        pgsql,
        taxi_driver_priority,
):
    version_preset_name = None
    if request_preset_name:
        version_preset_name = request_preset_name
    elif new_preset:
        version_preset_name = new_preset['name']

    db = pgsql['driver_priority']
    preset_id = None
    if version_preset_name is not None:
        preset_id = _get_preset_id(db, priority_name, version_preset_name)
    versions_before = (
        _get_priority_preset_versions(db, preset_id)
        if preset_id is not None
        else []
    )

    version_start = NOW + db_tools.DAY
    body: Dict[str, Any] = {
        'priority_name': priority_name,
        'version': {'sort_order': 123, 'starts_at': version_start.isoformat()},
        'rule': db_tools.DEFAULT_RULE,
        'payloads': db_tools.DEFAULT_PAYLOADS,
        'conditions': {},
    }
    if request_preset_name is not None:
        body['preset_name'] = request_preset_name
    if new_preset is not None:
        body['new_preset'] = new_preset
    headers = {'X-Idempotency-Token': str(uuid.uuid4())}

    check_response = await taxi_driver_priority.post(
        CHECK_URL, body, headers=headers,
    )
    assert check_response.status_code == expected_code

    response = await taxi_driver_priority.post(
        HANDLER_URL, body, headers=headers,
    )
    assert response.status_code == expected_code

    if expected_code != 200:
        assert response.json()['message']
        assert check_response.json()['message']
        db_tools.check_recalculation_task(db, None)
    else:
        assert response.json()['status'] == 'succeeded'
        versions_before.append(
            _make_last_created_version(
                db, db_tools.DEFAULT_RULE, version_start, None,
            ),
        )

        new_diff = _make_new_version_diff(body, version_start, None)
        utils.validate_check_version_response(
            check_response.json(),
            body,
            version_preset_name if preset_id is not None else None,
            expected_diff={'current': {}, 'new': new_diff},
        )
        if new_preset is not None:
            _check_created_preset(
                db, priority_name, new_preset['name'], expected_preset,
            )
            db_tools.check_recalculation_task(
                db, new_preset.get('agglomerations'),
            )
        else:
            db_tools.check_recalculation_task(db, None)

    # compare previous state with actual
    if preset_id is None and version_preset_name is not None:
        preset_id = _get_preset_id(db, priority_name, version_preset_name)
    versions_after = (
        _get_priority_preset_versions(db, preset_id)
        if preset_id is not None
        else []
    )
    assert versions_before == versions_after
