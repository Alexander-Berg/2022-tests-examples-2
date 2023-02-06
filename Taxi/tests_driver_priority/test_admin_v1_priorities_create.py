import datetime
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
import uuid

import psycopg2
import pytest

from tests_driver_priority import constants
from tests_driver_priority import db_tools
from tests_driver_priority import utils


URL = 'admin/v1/priorities/create'
CHECK_URL = 'admin/v1/priorities/check-create'
NOW = datetime.datetime.now(datetime.timezone.utc)
NOW_TZ = (NOW + datetime.timedelta(hours=3)).replace(
    tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=180),
)

PRIORITY_DATA = {
    'name': 'loyalty',
    'description': 'new priority description',
    'tanker_keys_prefix': 'loyalty',
}
DEFAULT_PRESET = {'name': 'default', 'description': 'preset description'}

BRANDING_CONDITIONS: Dict[str, Dict[str, Any]] = {
    'temporary': {'all_of': ['tag1']},
    'disabled': {'and': [{'any_of': ['tag3']}]},
    'achievable': {'or': [{'or': [{'none_of': ['tag5']}]}]},
}
BRANDING_PRIORITY = {
    'is_enabled': True,
    'tanker_keys_prefix': 'tk0',
    'description': 'description',
    'agglomerations': {'moscow': False, 'tula': True},
    'presets': {
        'default': {
            'is_default': True,
            'description': 'description',
            'versions': [
                {
                    'sort_order': 0,
                    'rule': db_tools.DEFAULT_RULE,
                    'temporary_condition': BRANDING_CONDITIONS['temporary'],
                    'disabled_condition': BRANDING_CONDITIONS['disabled'],
                    'achievable_condition': BRANDING_CONDITIONS['achievable'],
                    'achieved_payload': db_tools.DEFAULT_ACHIEVED_PAYLOAD,
                    'achievable_payload': {},
                    'created_at': NOW_TZ,
                    'starts_at': NOW_TZ,
                },
            ],
        },
    },
}

ACTIVITY_PRIORITY = {
    'is_enabled': True,
    'tanker_keys_prefix': 'activity',
    'description': 'description',
    'agglomerations': {'br_root': False},
    'presets': {
        'default': {
            'is_default': True,
            'description': 'description',
            'versions': [
                {
                    'sort_order': 1,
                    'rule': db_tools.ACTIVITY_RULE,
                    'temporary_condition': {},
                    'disabled_condition': {},
                    'achievable_condition': {},
                    'achieved_payload': db_tools.DEFAULT_ACHIEVED_PAYLOAD,
                    'achievable_payload': {},
                    'created_at': NOW_TZ,
                    'starts_at': NOW_TZ,
                },
            ],
        },
    },
}

LOYALTY_PRIORITY = {
    'is_enabled': False,
    'tanker_keys_prefix': 'loyalty',
    'description': 'new priority description',
    'presets': {
        'default': {
            'is_default': True,
            'description': 'preset description',
            'versions': [
                {
                    'sort_order': 123,
                    'rule': db_tools.DEFAULT_RULE,
                    'temporary_condition': BRANDING_CONDITIONS['temporary'],
                    'disabled_condition': BRANDING_CONDITIONS['disabled'],
                    'achievable_condition': BRANDING_CONDITIONS['achievable'],
                    'achieved_payload': db_tools.DEFAULT_ACHIEVED_PAYLOAD,
                    'achievable_payload': {},
                    'created_at': NOW_TZ,
                    'starts_at': NOW_TZ,
                },
            ],
        },
    },
}


@pytest.mark.now(NOW.isoformat())
@pytest.mark.pgsql(
    'driver_priority',
    queries=db_tools.join_queries(
        [
            # branding priority
            db_tools.insert_priority(0, 'branding', True, 'tk0'),
            db_tools.insert_priority_relation(constants.MSK, 0, False),
            db_tools.insert_priority_relation(constants.TULA, 0, True),
            db_tools.insert_preset(0, 0, 'default', NOW, is_default=True),
            db_tools.insert_version(
                0,
                0,
                0,
                db_tools.DEFAULT_RULE,
                db_tools.DEFAULT_ACHIEVED_PAYLOAD,
                NOW,
                NOW,
                temporary_condition=BRANDING_CONDITIONS['temporary'],
                disabled_condition=BRANDING_CONDITIONS['disabled'],
                achievable_condition=BRANDING_CONDITIONS['achievable'],
            ),
            # activity priority
            db_tools.insert_priority(
                1,
                'activity',
                True,
                'activity',
                can_contain_activity_rule=True,
            ),
            db_tools.insert_priority_relation(constants.BR_ROOT, 1, False),
            db_tools.insert_preset(1, 1, 'default', NOW, is_default=True),
            db_tools.insert_version(
                1,
                1,
                1,
                db_tools.ACTIVITY_RULE,
                db_tools.DEFAULT_ACHIEVED_PAYLOAD,
                NOW,
                NOW,
            ),
        ],
    )
    + db_tools.get_sequence_ids_update_queries(),
)
@pytest.mark.parametrize(
    'request_body, expected_code, expected_message, expected_data',
    [
        pytest.param(
            {
                'priority': PRIORITY_DATA,
                'preset': DEFAULT_PRESET,
                'version': {'sort_order': 123},
                'rule': db_tools.DEFAULT_RULE,
                'payloads': db_tools.DEFAULT_PAYLOADS,
                'conditions': BRANDING_CONDITIONS,
            },
            200,
            None,
            {
                'activity': ACTIVITY_PRIORITY,
                'branding': BRANDING_PRIORITY,
                'loyalty': LOYALTY_PRIORITY,
            },
            id='create new priority',
        ),
        pytest.param(
            {
                'priority': PRIORITY_DATA,
                'preset': DEFAULT_PRESET,
                'version': {'sort_order': 123},
                'rule': db_tools.WRONG_TOPIC_RULE,
                'payloads': db_tools.DEFAULT_PAYLOADS,
                'conditions': BRANDING_CONDITIONS,
            },
            400,
            'Priority rule contains tags [gold] which do not have relation '
            'with "priority" topic. Add necessary relations in tags service',
            {'activity': ACTIVITY_PRIORITY, 'branding': BRANDING_PRIORITY},
            id='rule contains topic without priority topic relation',
        ),
        pytest.param(
            {
                'priority': PRIORITY_DATA,
                'preset': DEFAULT_PRESET,
                'version': {'sort_order': 123},
                'rule': db_tools.WRONG_VALUES_RANKED_RULE,
                'payloads': db_tools.DEFAULT_PAYLOADS,
                'conditions': BRANDING_CONDITIONS,
            },
            400,
            'Found incorrect priority rule values: visible value 3 for item '
            'on position 3 and next visible value 1 has descending ordering, '
            'but previous values already have ascending ordering',
            {'activity': ACTIVITY_PRIORITY, 'branding': BRANDING_PRIORITY},
            id='ranked rule with incorrect visible values order',
        ),
        pytest.param(
            {
                'priority': PRIORITY_DATA,
                'preset': DEFAULT_PRESET,
                'version': {'sort_order': 123},
                'rule': db_tools.WRONG_VALUES_EXCLUDING_RULE,
                'payloads': db_tools.DEFAULT_PAYLOADS,
                'conditions': BRANDING_CONDITIONS,
            },
            400,
            'Found incorrect priority rule values: visible value -2 for item '
            'on position 2 and next visible value -1 has ascending ordering, '
            'but previous values already have descending ordering',
            {'activity': ACTIVITY_PRIORITY, 'branding': BRANDING_PRIORITY},
            id='ranked rule with incorrect visible values order',
        ),
        pytest.param(
            {
                'priority': {
                    'name': 'branding',
                    'description': 'new priority description',
                    'tanker_keys_prefix': 'new_priority_tanker',
                },
                'preset': DEFAULT_PRESET,
                'version': {'sort_order': 123},
                'rule': db_tools.DEFAULT_RULE,
                'payloads': db_tools.DEFAULT_PAYLOADS,
                'conditions': {},
            },
            409,
            'Priority "branding" already exists',
            {'activity': ACTIVITY_PRIORITY, 'branding': BRANDING_PRIORITY},
            id='same priority name',
        ),
        pytest.param(
            {
                'priority': PRIORITY_DATA,
                'preset': DEFAULT_PRESET,
                'version': {'sort_order': 123},
                'rule': {'invalid': 'data'},
                'payloads': db_tools.DEFAULT_PAYLOADS,
                'conditions': {},
            },
            400,
            None,  # do not check userver parse error
            {'activity': ACTIVITY_PRIORITY, 'branding': BRANDING_PRIORITY},
            id='invalid rule',
        ),
        pytest.param(
            {
                'priority': PRIORITY_DATA,
                'preset': DEFAULT_PRESET,
                'version': {'sort_order': 123},
                'rule': db_tools.DEFAULT_RULE,
                'payloads': db_tools.DEFAULT_PAYLOADS,
                'conditions': {'temporary': {'invalid': 'data'}},
            },
            400,
            None,  # do not check userver parse error
            {'activity': ACTIVITY_PRIORITY, 'branding': BRANDING_PRIORITY},
            id='invalid conditions',
        ),
        pytest.param(
            {
                'priority': {
                    'name': 'loyalty',
                    'description': 'new priority description',
                    'tanker_keys_prefix': 'loAYlty',
                },
                'preset': DEFAULT_PRESET,
                'version': {'sort_order': 123},
                'rule': db_tools.DEFAULT_RULE,
                'payloads': db_tools.DEFAULT_PAYLOADS,
                'conditions': {},
            },
            404,
            'Some tanker keys were not found: priority rule keys are "'
            'priority_view.priorities.loAYlty.car_year_text, '
            'priority_view.priorities.loAYlty.platinum_text, '
            'priority_view.priorities.loAYlty.rating_text, '
            'priority_view.priorities.loAYlty.silver_text"',
            {'activity': ACTIVITY_PRIORITY, 'branding': BRANDING_PRIORITY},
            id='tanker keys were not found',
        ),
        pytest.param(
            {
                'priority': PRIORITY_DATA,
                'preset': DEFAULT_PRESET,
                'version': {'sort_order': 123},
                'rule': db_tools.DEFAULT_RULE,
                'payloads': {
                    'achieved': {
                        'main_title': 'missed_tanker_key',
                        'constructor': [
                            {'numbered_list': [{'title': 'some_title'}]},
                        ],
                    },
                },
                'conditions': {},
            },
            404,
            'Some tanker keys were not found: payload keys are '
            '"priority_view.priority_payload.missed_tanker_key"',
            {'activity': ACTIVITY_PRIORITY, 'branding': BRANDING_PRIORITY},
            id='tanker keys were not found',
        ),
        pytest.param(
            {
                'priority': PRIORITY_DATA,
                'preset': DEFAULT_PRESET,
                'version': {'sort_order': 123},
                'rule': db_tools.ACTIVITY_RULE,
                'payloads': db_tools.DEFAULT_PAYLOADS,
                'conditions': BRANDING_CONDITIONS,
            },
            409,
            'New priority contains activity rule, but only existing priority '
            '"activity" can contain it',
            {'activity': ACTIVITY_PRIORITY, 'branding': BRANDING_PRIORITY},
            id='cannot create another priority with activity rule',
        ),
    ],
)
async def test_handler(
        taxi_driver_priority,
        request_body: Dict[str, Any],
        expected_code: int,
        expected_message: Optional[str],
        expected_data: Dict[str, Any],
        pgsql,
):
    headers = {'X-Idempotency-Token': str(uuid.uuid4())}
    check_response = await taxi_driver_priority.post(
        CHECK_URL, request_body, headers=headers,
    )
    assert check_response.status_code == expected_code

    response = await taxi_driver_priority.post(
        URL, request_body, headers=headers,
    )
    assert response.status_code == expected_code

    check_response_json = check_response.json()
    if expected_code == 200:
        utils.validate_check_response(check_response_json, request_body)
        assert response.json()['status'] == 'succeeded'
    elif expected_message is not None:
        assert check_response_json['message'] == expected_message
    saved_data = db_tools.select_priorities_info(pgsql['driver_priority'])
    assert expected_data == saved_data


@pytest.mark.now(NOW.isoformat())
@pytest.mark.parametrize(
    'request_body, missed_keys',
    [
        (
            {
                'priority': PRIORITY_DATA,
                'preset': DEFAULT_PRESET,
                'version': {'sort_order': 123},
                'rule': db_tools.DEFAULT_RULE,
                'payloads': {
                    'achieved': {
                        'main_title': 'loyal',
                        'constructor': [
                            {
                                'numbered_list': [
                                    {
                                        'title': 'some_title',
                                        'subtitle': 'missed_subtitle',
                                    },
                                ],
                            },
                        ],
                    },
                    'achievable': {
                        'main_title': 'missed_main_title',
                        'constructor': [
                            {
                                'text': 'missed_paragraph_text',
                                'title': 'missed_paragraph_title',
                            },
                        ],
                        'button': {
                            'action': {
                                'url': 'url',
                                'title': 'missed_action_title',
                            },
                            'text': 'missed_button_text',
                        },
                    },
                },
                'conditions': {},
            },
            [
                'priority_payload.missed_subtitle',
                'priority_payload.missed_main_title',
                'priority_payload.missed_paragraph_title',
                'priority_payload.missed_paragraph_text',
                'priority_payload.missed_button_text',
                'priority_payload.missed_action_title',
            ],
        ),
    ],
)
async def test_missed_tanker_keys(
        taxi_driver_priority,
        request_body: Dict[str, Any],
        missed_keys: List[str],
):
    headers = {'X-Idempotency-Token': str(uuid.uuid4())}

    check_response = await taxi_driver_priority.post(
        CHECK_URL, request_body, headers=headers,
    )
    assert check_response.status_code == 404

    response = await taxi_driver_priority.post(
        URL, request_body, headers=headers,
    )
    assert response.status_code == 404
    error_message = response.json()['message']
    for key in missed_keys:
        assert error_message.find(key) != -1
