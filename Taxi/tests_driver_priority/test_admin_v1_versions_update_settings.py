import copy
import datetime
from typing import Any
from typing import Dict
from typing import Optional
import uuid

import pytest

from tests_driver_priority import db_tools
from tests_driver_priority import utils


URL = 'admin/v1/versions/update-settings'
CHECK_URL = 'admin/v1/versions/check-update-settings'
NOW = datetime.datetime.now(datetime.timezone.utc)
HOUR = datetime.timedelta(hours=1)
SORT_ORDER = 123


@pytest.mark.pgsql(
    'driver_priority',
    queries=db_tools.get_pg_default_data(NOW)
    + db_tools.join_queries(
        [
            db_tools.insert_priority(
                4,
                'activity',
                True,
                'activity',
                can_contain_activity_rule=True,
            ),
            db_tools.insert_preset(
                9, 4, 'default_for_activity', NOW, is_default=True,
            ),
            db_tools.insert_version(
                14,
                9,
                4,
                db_tools.ACTIVITY_RULE,
                db_tools.DEFAULT_ACHIEVED_PAYLOAD,
                NOW,
                NOW + db_tools.HOUR,
            ),
        ],
    ),
)
@pytest.mark.parametrize(
    'priority_name, preset_name, version_id, rule, expected_code, '
    'error_message',
    [
        pytest.param(
            'branding',
            'actual_preset',
            3,
            db_tools.DEFAULT_RULE,
            200,
            None,
            id='success request',
        ),
        pytest.param(
            'branding',
            'without_versions',
            0,
            db_tools.DEFAULT_RULE,
            404,
            (
                'Could not find preset for priority_name="branding" '
                'and preset_name="without_versions"'
            ),
            id='priority or preset was not found',
        ),
        pytest.param(
            'branding',
            'default',
            2,
            db_tools.DEFAULT_RULE,
            404,
            (
                'Preset "default" has id=0, but updated version with id=2 has '
                'relation with preset_id=1'
            ),
            id='version was not found',
        ),
        pytest.param(
            'empty_relations',
            'default',
            8,
            db_tools.DEFAULT_RULE,
            404,
            (
                'Some tanker keys were not found: priority rule keys are '
                '"priority_view.priorities.empty_relations.car_year_text, '
                'priority_view.priorities.empty_relations.platinum_text, '
                'priority_view.priorities.empty_relations.rating_text, '
                'priority_view.priorities.empty_relations.silver_text"'
            ),
            id='tanker key is not found',
        ),
        pytest.param(
            'branding',
            'default',
            0,
            db_tools.DEFAULT_RULE,
            409,
            (
                'Could not update version settings for priority_name='
                '"branding", preset_name="default" and version_id=0 because '
                'version is archived or active. It\'s possible to modify '
                'versions with starting time in the future'
            ),
            id='version is archived or active',
        ),
        pytest.param(
            'branding',
            'actual_preset',
            3,
            db_tools.ACTIVITY_RULE,
            409,
            'Existing priority "branding" cannot contain activity rule',
            id='activity rule for non-activity preset',
        ),
        pytest.param(
            'branding',
            'actual_preset',
            3,
            {
                'ranked_rule': [
                    {
                        'tag_name': 'silver',
                        'priority_value': {'backend': 1, 'display': 1},
                        'override': {'none_of': ['activity', 'car_year']},
                    },
                    {
                        'tag_name': 'gold',
                        'priority_value': {'backend': 5, 'display': 5},
                    },
                    {
                        'tag_name': 'rating',
                        'priority_value': {'backend': 10, 'display': 10},
                    },
                ],
            },
            400,
            'Priority rule contains tags [activity, car_year, gold, rating] '
            'which do not have relation with \"priority\" topic. Add '
            'necessary relations in tags service',
            id='passed tags do not have relation with priority topic',
        ),
        pytest.param(
            'activity',
            'default_for_activity',
            14,
            db_tools.ACTIVITY_RULE,
            200,
            None,
            id='activity rule for activity preset',
        ),
        pytest.param(
            'branding',
            'actual_preset',
            3,
            db_tools.WRONG_VALUES_RANKED_RULE,
            400,
            'Found incorrect priority rule values: visible value 3 for item '
            'on position 3 and next visible value 1 has descending ordering, '
            'but previous values already have ascending ordering',
            id='incorrect ranked rule',
        ),
        pytest.param(
            'branding',
            'actual_preset',
            3,
            db_tools.WRONG_VALUES_EXCLUDING_RULE,
            400,
            'Found incorrect priority rule values: visible value -2 for item '
            'on position 2 and next visible value -1 has ascending ordering, '
            'but previous values already have descending ordering',
            id='incorrect excluding rule',
        ),
    ],
)
async def test_handler(
        taxi_driver_priority,
        priority_name: str,
        preset_name: str,
        version_id: int,
        rule: Dict[str, Any],
        expected_code: int,
        error_message: Optional[str],
        pgsql,
):

    db = pgsql['driver_priority']
    current_settings = db_tools.get_preset_version(version_id, db)
    assert current_settings is not None
    current_diff = {
        'version': {
            'id': version_id,
            'sort_order': current_settings['sort_order'],
        },
        'rule': current_settings['rule'],
        'payloads': {'achieved': current_settings['achieved_payload']},
        'conditions': {},
    }

    request_body = {
        'priority_name': priority_name,
        'preset_name': preset_name,
        'version': {'id': version_id, 'sort_order': SORT_ORDER},
        'rule': rule,
        'payloads': {'achieved': db_tools.DEFAULT_ACHIEVED_PAYLOAD},
        'conditions': {
            'temporary': {'value': True},
            'disabled': {'value': False},
            'achievable': {'and': [{'value': True}, {'value': False}]},
        },
    }
    headers = {'X-Idempotency-Token': str(uuid.uuid4())}

    check_response = await taxi_driver_priority.post(
        CHECK_URL, request_body, headers=headers,
    )
    assert check_response.status_code == expected_code

    response = await taxi_driver_priority.post(
        URL, request_body, headers=headers,
    )
    assert response.status_code == expected_code
    assert (error_message is None) == (expected_code == 200)

    if expected_code != 200:
        return

    assert response.json()['status'] == 'succeeded'
    settings = db_tools.get_preset_version(version_id, db)
    preset_id = db_tools.get_preset_id(version_id, db)

    assert settings == {
        'preset_id': preset_id,
        'sort_order': SORT_ORDER,
        'rule': rule,
        'achieved_payload': db_tools.DEFAULT_ACHIEVED_PAYLOAD,
        'achievable_payload': {},
        'temporary_condition': {'value': True},
        'achievable_condition': {'and': [{'value': True}, {'value': False}]},
        'disabled_condition': {'value': False},
        'created_at': NOW,
        'starts_at': NOW + HOUR,
    }

    new_state = copy.deepcopy(request_body)
    new_state.pop('priority_name')
    new_state.pop('preset_name')
    utils.validate_check_version_response(
        check_response.json(),
        request_body,
        preset_name,
        expected_diff={'new': new_state, 'current': current_diff},
    )
