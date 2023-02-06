import json
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

import jsonschema
import pytest

from tests_driver_mode_subscription import common
from tests_driver_mode_subscription import mode_rules

REQUEST_HEADER = {'X-Ya-Service-Ticket': common.MOCK_TICKET}

VALIDATION_SETTINGS = {
    'available_billing_modes': ['orders', 'driver_fix', 'my'],
    'available_display_modes': ['orders', 'orders_type', 'shuttle'],
    'available_display_profiles': ['orders', 'all_features', 'driver_fix'],
}

BILLING_SETTINGS: Dict[str, Any] = {
    'orders': [],
    'driver_fix': [],
    'mode_rule_1': [],
    'mode_rule_3': [],
    'mode_rule_2': [],
}

_PLACEHOLDER_SCHEME_1 = '{"placeholder":"test1"}'
_PLACEHOLDER_SCHEME_2 = '{"placeholder":"test2"}'


def _make_insert_admin_schema(
        name: str,
        placeholder: str,
        hash_str: str,
        min_compatible_version: int,
        max_compatible_version: Optional[int],
):
    max_compatible_version_str = (
        'Null'
        if max_compatible_version is None
        else str(max_compatible_version)
    )

    # placeholder = placeholder.replace("'", "\\'")

    return f"""
        INSERT INTO config.admin_schemas
        (name, schema, hash, compatible_version)
        VALUES ('{name}', '{placeholder}'::JSONB, '{hash_str}',
        INT4RANGE({min_compatible_version}, {max_compatible_version_str},'[)'))
        """


@pytest.mark.pgsql(
    'driver_mode_subscription',
    queries=[
        mode_rules.patched_db(
            patches=[mode_rules.Patch(rule_name='mode1')],
            mode_classes=[mode_rules.ModeClass('my_class', ['mode1'])],
        ),
    ],
)
@pytest.mark.now('2019-05-01T12:00:00+0300')
async def test_admin_work_modes_suggest(taxi_driver_mode_subscription):
    response = await taxi_driver_mode_subscription.get(
        '/v1/admin/modes', json={}, headers=REQUEST_HEADER,
    )
    assert response.status_code == 200

    response_data = response.json()
    assert response_data == {
        'work_modes': [
            {'name': 'custom_orders'},
            {'name': 'driver_fix'},
            {'name': 'mode1', 'class_name': 'my_class'},
            {'name': 'orders'},
            {'name': 'uberdriver'},
        ],
    }


@pytest.mark.pgsql(
    'driver_mode_subscription',
    queries=[
        mode_rules.make_insert_offers_groups_sql(
            {'taxi', 'eda', 'lavka', 'custom_group'},
        ),
    ],
)
@pytest.mark.now('2019-05-01T12:00:00+0300')
async def test_admin_offers_groups_suggest(taxi_driver_mode_subscription):
    response = await taxi_driver_mode_subscription.get(
        '/v1/admin/mode/groups', json={}, headers=REQUEST_HEADER,
    )
    assert response.status_code == 200

    response_data = response.json()
    assert response_data == {
        'offers_groups': [
            {'name': 'custom_group'},
            {'name': 'eda'},
            {'name': 'lavka'},
            {'name': 'taxi'},
        ],
    }


@pytest.mark.pgsql(
    'driver_mode_subscription',
    queries=[
        mode_rules.make_insert_mode_classes_sql(
            {'driver_fix', 'flexible', 'highsubs'},
        ),
    ],
)
@pytest.mark.now('2019-05-01T12:00:00+0300')
async def test_admin_mode_classes_suggest(taxi_driver_mode_subscription):
    response = await taxi_driver_mode_subscription.get(
        '/v1/admin/mode/classes', json={}, headers=REQUEST_HEADER,
    )
    assert response.status_code == 200

    response_data = response.json()
    assert response_data == {
        'mode_classes': [
            {'name': 'driver_fix'},
            {'name': 'flexible'},
            {'name': 'highsubs'},
        ],
    }


@pytest.mark.parametrize(
    'expected_suggests',
    [
        pytest.param(
            [{'name': 'driver_fix'}, {'name': 'my'}, {'name': 'orders'}],
            marks=[
                pytest.mark.config(
                    DRIVER_MODE_RULES_VALIDATION_SETTINGS=VALIDATION_SETTINGS,
                ),
            ],
            id='not empty',
        ),
        pytest.param([], id='empty'),
    ],
)
@pytest.mark.now('2019-05-01T12:00:00+0300')
async def test_admin_billing_modes_suggest(
        taxi_driver_mode_subscription, expected_suggests: List[Dict[str, str]],
):
    response = await taxi_driver_mode_subscription.get(
        '/v1/admin/billing/modes', json={}, headers=REQUEST_HEADER,
    )
    assert response.status_code == 200

    response_data = response.json()
    assert response_data == {'billing_modes': expected_suggests}


@pytest.mark.parametrize(
    'expected_suggests',
    [
        pytest.param(
            [
                {'name': 'driver_fix'},
                {'name': 'mode_rule_1'},
                {'name': 'mode_rule_2'},
                {'name': 'mode_rule_3'},
                {'name': 'orders'},
            ],
            marks=[
                pytest.mark.config(
                    BILLING_DRIVER_MODE_SETTINGS=BILLING_SETTINGS,
                ),
            ],
            id='not empty',
        ),
        pytest.param([], id='empty'),
    ],
)
@pytest.mark.now('2019-05-01T12:00:00+0300')
async def test_admin_billing_mode_rules_suggest(
        taxi_driver_mode_subscription, expected_suggests: List[Dict[str, str]],
):
    response = await taxi_driver_mode_subscription.get(
        '/v1/admin/billing/mode_rules', json={}, headers=REQUEST_HEADER,
    )
    assert response.status_code == 200

    response_data = response.json()
    assert response_data == {'billing_mode_rules': expected_suggests}


@pytest.mark.parametrize(
    'expected_suggests',
    [
        pytest.param(
            [{'name': 'orders'}, {'name': 'orders_type'}, {'name': 'shuttle'}],
            marks=[
                pytest.mark.config(
                    DRIVER_MODE_RULES_VALIDATION_SETTINGS=VALIDATION_SETTINGS,
                ),
            ],
            id='not empty',
        ),
        pytest.param([], id='empty'),
    ],
)
@pytest.mark.now('2019-05-01T12:00:00+0300')
async def test_admin_display_modes_suggest(
        taxi_driver_mode_subscription, expected_suggests: List[Dict[str, str]],
):
    response = await taxi_driver_mode_subscription.get(
        '/v1/admin/display/modes', json={}, headers=REQUEST_HEADER,
    )
    assert response.status_code == 200

    response_data = response.json()
    assert response_data == {'display_modes': expected_suggests}


@pytest.mark.parametrize(
    'expected_suggests',
    [
        pytest.param(
            [
                {'name': 'all_features'},
                {'name': 'driver_fix'},
                {'name': 'orders'},
            ],
            marks=[
                pytest.mark.config(
                    DRIVER_MODE_RULES_VALIDATION_SETTINGS=VALIDATION_SETTINGS,
                ),
            ],
            id='not empty',
        ),
        pytest.param([], id='empty'),
    ],
)
@pytest.mark.now('2019-05-01T12:00:00+0300')
async def test_admin_display_profiles_suggest(
        taxi_driver_mode_subscription, expected_suggests: List[Dict[str, str]],
):
    response = await taxi_driver_mode_subscription.get(
        '/v1/admin/display/profiles', json={}, headers=REQUEST_HEADER,
    )
    assert response.status_code == 200

    response_data = response.json()
    assert response_data == {'display_profiles': expected_suggests}


@pytest.mark.pgsql(
    'driver_mode_subscription',
    queries=[
        mode_rules.patched_db(
            patches=[
                mode_rules.Patch(
                    rule_name='all_features',
                    features={
                        'driver_fix': {'roles': [{'name': 'role1'}]},
                        'tags': {'assign': ['driver_fix']},
                        'reposition': {'profile': 'reposition_profile'},
                        'active_transport': {'type': 'bicycle'},
                        'geobooking': {'roles': [{'name': 'role1'}]},
                        'booking': {'slot_policy': 'key_params'},
                    },
                ),
            ],
        ),
        mode_rules.init_admin_schema_version(),
    ],
)
@pytest.mark.now('2019-05-01T12:00:00+0300')
async def test_admin_mode_features_suggest(taxi_driver_mode_subscription):

    # Run updater once to load schemas to database
    await taxi_driver_mode_subscription.run_task('admin-schemas-updater')

    response = await taxi_driver_mode_subscription.get(
        '/v1/admin/mode/features', json={}, headers=REQUEST_HEADER,
    )
    assert response.status_code == 200

    response_data = response.json()

    assert 'features' in response_data

    feature_names = []
    feature_schemas = {}

    for feature in response_data['features']:
        assert 'name' in feature and 'settings_schema' in feature

        jsonschema.Draft4Validator.check_schema(feature['settings_schema'])

        feature_names.append(feature['name'])
        feature_schemas[feature['name']] = feature['settings_schema']

    assert feature_names == [
        'active_transport',
        'booking',
        'driver_fix',
        'geobooking',
        'logistic_workshifts',
        'reposition',
        'tags',
    ]

    # check that features pass validation with given schemas

    response = await taxi_driver_mode_subscription.post(
        'v1/admin/mode_rules/list',
        json={'filters': {'work_modes': ['all_features']}},
        headers=REQUEST_HEADER,
    )
    assert response.status_code == 200

    response_data = response.json()
    for feature in response_data['rules'][0]['rule_data']['features']:
        jsonschema.validate(
            feature['settings'], feature_schemas[feature['name']],
        )


@pytest.mark.parametrize(
    'requested_version, expected_code, expected_version, expected_placeholder',
    [
        pytest.param(1, 200, 1, _PLACEHOLDER_SCHEME_1, id='old_version'),
        pytest.param(2, 200, 2, _PLACEHOLDER_SCHEME_2, id='new_version'),
        pytest.param(
            None,
            200,
            2,
            _PLACEHOLDER_SCHEME_2,
            id='missed_version_in_request',
        ),
        pytest.param(10, 404, 1, None, id='future_version'),
    ],
)
@pytest.mark.pgsql(
    'driver_mode_subscription',
    queries=[
        mode_rules.init_admin_schema_version(2),
        _make_insert_admin_schema(
            'active_transport', _PLACEHOLDER_SCHEME_1, 'some_hash_1', 1, 2,
        ),
        _make_insert_admin_schema(
            'active_transport', _PLACEHOLDER_SCHEME_2, 'some_hash_2', 2, None,
        ),
    ],
)
async def test_admin_mode_features_suggest_version_param(
        taxi_driver_mode_subscription,
        requested_version: Optional[int],
        expected_code: int,
        expected_version: int,
        expected_placeholder: Optional[str],
):

    request_params = {}
    if requested_version is not None:
        request_params['version'] = requested_version

    response = await taxi_driver_mode_subscription.get(
        '/v1/admin/mode/features',
        params=request_params,
        json={},
        headers=REQUEST_HEADER,
    )

    assert response.status_code == expected_code

    if expected_code != 200:
        return

    response_data = response.json()

    assert response_data['version'] == expected_version
    assert 'features' in response_data

    feature_names = []
    feature_schemas = {}

    for feature in response_data['features']:
        assert 'name' in feature and 'settings_schema' in feature

        feature_names.append(feature['name'])
        feature_schemas[feature['name']] = feature['settings_schema']

    assert 'active_transport' in feature_names

    if expected_placeholder is not None:
        assert feature_schemas['active_transport'] == json.loads(
            expected_placeholder,
        )
