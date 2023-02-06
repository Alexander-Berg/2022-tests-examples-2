import datetime
from typing import Optional

import pytest

from tests_driver_mode_subscription import common
from tests_driver_mode_subscription import mode_rules
from tests_driver_mode_subscription import mode_rules_create
from tests_driver_mode_subscription import offer_templates

_REQUEST_HEADER = {
    'X-Ya-Service-Ticket': common.MOCK_TICKET,
    'X-Yandex-Login': 'test_user',
    'X-YaTaxi-Draft-Id': '42',
}

_NOW = '2020-08-03T19:51:00+00:00'

_NON_CONFLICTING_FEATURES = [
    {'name': 'active_transport', 'settings': {'type': 'bicycle'}},
    {'name': 'reposition', 'settings': {'profile': 'reposition_profile'}},
    {'name': 'tags', 'settings': {'assign': ['driver_fix']}},
]

_ALL_FEATURES_WITH_GEOBOOKING = _NON_CONFLICTING_FEATURES + [
    {'name': 'geobooking', 'settings': {}},
]
_ALL_FEATURES_WITH_DRIVER_FIX = [
    {'name': 'driver_fix', 'settings': {'roles': [{'name': 'role1'}]}},
] + _NON_CONFLICTING_FEATURES

_VALIDATION_SETTINGS = {'rule_draft_starts_min_threshold_m': 120}


def _get_all_mode_rules_db(pgsql):
    cursor = pgsql['driver_mode_subscription'].cursor()
    cursor.execute(
        """
        SELECT
        config.modes.name,
        config.mode_classes.name,
        config.mode_rules.starts_at AT TIME ZONE 'UTC',
        config.mode_rules.stops_at AT TIME ZONE 'UTC',
        config.offers_groups.name,
        config.conditions.data,
        config.mode_rules.display_mode,
        config.mode_rules.display_profile,
        config.mode_rules.billing_mode,
        config.mode_rules.billing_mode_rule,
        config.mode_rules.features,
        config.mode_rules.drafts,
        config.mode_rules.admin_schemas_version
        FROM config.mode_rules
             INNER JOIN config.modes
                        ON config.modes.id = config.mode_rules.mode_id
             LEFT JOIN config.mode_classes
                       ON config.modes.class_id = config.mode_classes.id
             LEFT JOIN config.offers_groups
                       ON config.offers_groups.id =
                          config.mode_rules.offers_group_id
             LEFT JOIN config.conditions
                       ON config.conditions.id = config.mode_rules.condition_id
        """,
    )
    rows = list(row for row in cursor)
    return rows


@pytest.mark.pgsql(
    'driver_mode_subscription',
    queries=[
        mode_rules.make_insert_offers_groups_sql({'taxi'}),
        mode_rules.make_insert_mode_classes_sql(
            {'test_class', 'existing_class'},
        ),
        mode_rules.make_insert_modes_sql({'existing_mode'}, class_by_mode={}),
        mode_rules.init_admin_schema_version(),
    ],
)
@pytest.mark.now(_NOW)
@pytest.mark.config(
    BILLING_DRIVER_MODE_SETTINGS=(
        mode_rules_create.DEFAULT_BILLING_DRIVER_MODE_SETTINGS
    ),
    DRIVER_MODE_SUBSCRIPTION_OFFER_TEMPLATES=(
        offer_templates.DEFAULT_OFFER_TEMPLATES
    ),
    DRIVER_MODE_SUBSCRIPTION_MODE_TEMPLATE_RELATIONS={
        'by_mode_class': {},
        'by_work_mode': {
            'test_rule': 'orders_template',
            'existing_mode': 'orders_template',
        },
    },
)
@pytest.mark.parametrize(
    'rule_data',
    [
        pytest.param(
            mode_rules_create.RuleData(
                features=_ALL_FEATURES_WITH_DRIVER_FIX,
                billing_mode='driver_fix',
            ),
            id='all_features_driver_fix',
        ),
        pytest.param(
            mode_rules_create.RuleData(
                features=_ALL_FEATURES_WITH_GEOBOOKING, billing_mode='orders',
            ),
            id='all_features_geobooking',
        ),
        pytest.param(
            mode_rules_create.RuleData(offers_group=None),
            id='no offers_group',
        ),
        pytest.param(
            mode_rules_create.RuleData(
                offers_group=None,
                conditions={
                    'and': [{'none_of': ['tag1']}, {'all_of': ['tag2']}],
                },
            ),
            id='conditions',
        ),
        pytest.param(
            mode_rules_create.RuleData(work_mode_class='test_class'),
            id='assign work mode class to new mode',
        ),
        pytest.param(
            mode_rules_create.RuleData(
                work_mode_class='test_class',
                work_mode='existing_mode',
                features=_ALL_FEATURES_WITH_DRIVER_FIX,
                billing_mode='driver_fix',
            ),
            id='assign work mode class to existing mode',
        ),
        pytest.param(
            mode_rules_create.RuleData(
                work_mode_class='test_class',
                work_mode='existing_mode',
                features=_ALL_FEATURES_WITH_DRIVER_FIX,
                billing_mode='driver_fix',
                schema_version=777,
            ),
            id='schema version stored',
            marks=[
                pytest.mark.pgsql(
                    'driver_mode_subscription',
                    queries=[mode_rules.update_admin_schema_version(777)],
                ),
            ],
        ),
        pytest.param(
            mode_rules_create.RuleData(
                work_mode_class='test_class',
                work_mode='existing_mode',
                features=_ALL_FEATURES_WITH_DRIVER_FIX,
                billing_mode='driver_fix',
                schema_version=None,
            ),
            id='no schema version using fallback',
        ),
    ],
)
async def test_admin_mode_rules_create_fulldata(
        pgsql,
        taxi_driver_mode_subscription,
        rule_data: mode_rules_create.RuleData,
):
    response = await taxi_driver_mode_subscription.post(
        'v1/admin/mode_rules/create',
        json=rule_data.as_request(),
        headers=_REQUEST_HEADER,
    )
    assert response.status_code == 200

    assert response.json() == {}

    assert _get_all_mode_rules_db(pgsql) == [rule_data.as_db_row()]


@pytest.mark.pgsql(
    'driver_mode_subscription',
    queries=[
        mode_rules.make_insert_offers_groups_sql({'taxi'}),
        mode_rules.init_admin_schema_version(),
    ],
)
@pytest.mark.now(_NOW)
@pytest.mark.config(
    BILLING_DRIVER_MODE_SETTINGS=(
        mode_rules_create.DEFAULT_BILLING_DRIVER_MODE_SETTINGS
    ),
    DRIVER_MODE_SUBSCRIPTION_OFFER_TEMPLATES=(
        offer_templates.DEFAULT_OFFER_TEMPLATES
    ),
    DRIVER_MODE_SUBSCRIPTION_MODE_TEMPLATE_RELATIONS={
        'by_mode_class': {},
        'by_work_mode': {'test_rule': 'orders_template'},
    },
)
@pytest.mark.parametrize(
    'rule_data, expected_check_error_msg, expected_create_error_msg',
    [
        pytest.param(
            mode_rules_create.RuleData(
                starts_at='2020-08-03T21:51:00+00:00',
                stops_at='2020-07-03T21:51:00+00:00',
                features=_ALL_FEATURES_WITH_DRIVER_FIX,
                billing_mode='driver_fix',
            ),
            'stops_at must be greater than starts_at',
            'stops_at must be greater than starts_at',
            id='stops_at less than starts_at',
        ),
        pytest.param(
            mode_rules_create.RuleData(
                starts_at=_NOW,
                features=_ALL_FEATURES_WITH_DRIVER_FIX,
                billing_mode='driver_fix',
            ),
            None,
            None,
            id='starts_at at now without threshold',
        ),
        pytest.param(
            mode_rules_create.RuleData(
                starts_at=_NOW,
                features=_ALL_FEATURES_WITH_DRIVER_FIX,
                billing_mode='driver_fix',
            ),
            'starts_at must be at least now + 120 minutes',
            None,
            marks=[
                pytest.mark.config(
                    DRIVER_MODE_RULES_VALIDATION_SETTINGS=_VALIDATION_SETTINGS,
                ),
            ],
            id='starts_at at now with threshold bad',
        ),
        pytest.param(
            mode_rules_create.RuleData(
                starts_at='2020-08-03T21:51:00+00:00',
                features=_ALL_FEATURES_WITH_DRIVER_FIX,
                billing_mode='driver_fix',
            ),
            None,
            None,
            marks=[
                pytest.mark.config(
                    DRIVER_MODE_RULES_VALIDATION_SETTINGS=_VALIDATION_SETTINGS,
                ),
            ],
            id='starts_at at now with threshold good',
        ),
    ],
)
async def test_admin_mode_rules_check_create_interval_checks(
        taxi_driver_mode_subscription,
        rule_data: mode_rules_create.RuleData,
        expected_check_error_msg: Optional[str],
        expected_create_error_msg: Optional[str],
):
    await mode_rules_create.check_test_create_body_base(
        taxi_driver_mode_subscription,
        rule_data.as_request(),
        expected_check_error_msg,
        expected_create_error_msg,
    )


@pytest.mark.pgsql(
    'driver_mode_subscription',
    queries=[
        mode_rules.make_insert_offers_groups_sql({'taxi'}),
        mode_rules.make_insert_mode_classes_sql(
            {'test_class', 'existing_class'},
        ),
        mode_rules.make_insert_modes_sql(
            {'mode_with_class'},
            class_by_mode={'mode_with_class': 'existing_class'},
        ),
        mode_rules.init_admin_schema_version(),
    ],
)
@pytest.mark.now(_NOW)
@pytest.mark.config(
    BILLING_DRIVER_MODE_SETTINGS=(
        mode_rules_create.DEFAULT_BILLING_DRIVER_MODE_SETTINGS
    ),
    DRIVER_MODE_RULES_VALIDATION_SETTINGS={
        'available_billing_modes': ['driver_fix', 'some_billing_mode'],
        'available_display_modes': ['orders', 'orders_type'],
        'available_display_profiles': ['orders', 'all_features'],
        'read_only_modes': ['orders'],
    },
    DRIVER_MODE_SUBSCRIPTION_OFFER_TEMPLATES=(
        offer_templates.DEFAULT_OFFER_TEMPLATES
    ),
    DRIVER_MODE_SUBSCRIPTION_MODE_TEMPLATE_RELATIONS={
        'by_mode_class': {},
        'by_work_mode': {
            'test_rule': 'orders_template',
            'orders': 'orders_template',
            'driver_fix': 'driver_fix_template',
            'mode_with_class': 'orders_template',
        },
    },
)
@pytest.mark.parametrize(
    'rule_data, expected_error_msg',
    [
        pytest.param(mode_rules_create.RuleData(), None, id='all_valid'),
        pytest.param(
            mode_rules_create.RuleData(
                offers_group='wrong_group',
                features=_ALL_FEATURES_WITH_DRIVER_FIX,
                billing_mode='driver_fix',
            ),
            'invalid offers group: wrong_group',
            id='wrong offers_group',
        ),
        pytest.param(
            mode_rules_create.RuleData(billing_mode='bad_billing_mode'),
            'Unsupported billing mode: bad_billing_mode. Supported values: '
            'driver_fix, some_billing_mode',
            id='bad_billing_mode',
        ),
        pytest.param(
            mode_rules_create.RuleData(
                billing_mode_rule='bad_billing_mode_rule',
            ),
            'Unsupported billing mode rule: bad_billing_mode_rule not found in'
            ' BILLING_DRIVER_MODE_SETTINGS',
            id='bad_billing_mode_rule',
        ),
        pytest.param(
            mode_rules_create.RuleData(display_mode='bad_display_mode'),
            'Unsupported display mode: bad_display_mode. Supported values: '
            'orders, orders_type',
            id='bad_display_mode',
        ),
        pytest.param(
            mode_rules_create.RuleData(display_profile='bad_display_profile'),
            'Unsupported display profile: bad_display_profile. Supported '
            'values: all_features, orders',
            id='bad_display_profile',
        ),
        pytest.param(
            mode_rules_create.RuleData('orders'),
            'Editing of work mode orders is prohibited in '
            'DRIVER_MODE_RULES_VALIDATION_SETTINGS config',
            id='read_only_mode',
        ),
        pytest.param(
            mode_rules_create.RuleData(
                'driver_fix',
                billing_mode='driver_fix',
                features=[
                    {
                        'name': 'driver_fix',
                        'settings': {'roles': [{'name': 'role1'}]},
                    },
                    {'name': 'geobooking', 'settings': {}},
                ],
            ),
            'Multiple offer providers found: driver_fix, geobooking',
            id='conflicting_features_0',
        ),
        pytest.param(
            mode_rules_create.RuleData(
                'driver_fix',
                billing_mode='driver_fix',
                features=[
                    {
                        'name': 'driver_fix',
                        'settings': {'roles': [{'name': 'role1'}]},
                    },
                    {'name': 'logistic_workshifts', 'settings': {}},
                ],
            ),
            'Multiple offer providers found: driver_fix, logistic_workshifts',
            id='conflicting_features_1',
        ),
        pytest.param(
            mode_rules_create.RuleData(work_mode_class='wrong_class'),
            'invalid work mode class: wrong_class',
            id='wrong mode class',
        ),
        pytest.param(
            mode_rules_create.RuleData(
                work_mode='mode_with_class',
                work_mode_class='test_class',
                billing_mode='driver_fix',
                features=[
                    {
                        'name': 'unknown_feature',
                        'settings': {'roles': [{'name': 'role1'}]},
                    },
                ],
            ),
            'bad input on feature unknown_feature',
            id='wrong feature anme',
        ),
        pytest.param(
            mode_rules_create.RuleData(
                work_mode='custom_orders',
                billing_mode='orders',
                features=[],
                schema_version=0,
            ),
            'Wrong schemas version: 0, supported version: 1',
            id='wrong schema version',
        ),
    ],
)
async def test_admin_mode_rules_check_create_bad_input(
        taxi_driver_mode_subscription,
        rule_data: mode_rules_create.RuleData,
        expected_error_msg: Optional[str],
):
    await mode_rules_create.check_test_create_body_base(
        taxi_driver_mode_subscription,
        rule_data.as_request(),
        expected_error_msg,
        expected_error_msg,
    )


_INTERSECT_RULE_ID = '11111111111111111111111111111111'
_INTERSECT_RULE_ID2 = '22222222222222222222222222222222'


def _make_rule_patch(
        starts_at: str,
        stops_at: Optional[str] = None,
        rule_id: Optional[str] = None,
        is_canceled: Optional[bool] = None,
):
    _stops_at = datetime.datetime.fromisoformat(stops_at) if stops_at else None

    return mode_rules.Patch(
        rule_id=rule_id,
        rule_name='test_rule',
        starts_at=datetime.datetime.fromisoformat(starts_at),
        stops_at=_stops_at,
        is_canceled=is_canceled,
    )


def _make_intersection_error_message(
        starts_at: str,
        stops_at: str = 'null',
        rule_id: str = _INTERSECT_RULE_ID,
):
    return (
        f'intersect with rules: [{{id: {rule_id}, starts at: {starts_at}, '
        f'stops_at: {stops_at}}}]'
    )


@pytest.mark.pgsql(
    'driver_mode_subscription',
    queries=[mode_rules.init_admin_schema_version()],
)
@pytest.mark.now(_NOW)
@pytest.mark.config(
    BILLING_DRIVER_MODE_SETTINGS=(
        mode_rules_create.DEFAULT_BILLING_DRIVER_MODE_SETTINGS
    ),
    DRIVER_MODE_SUBSCRIPTION_OFFER_TEMPLATES=(
        offer_templates.DEFAULT_OFFER_TEMPLATES
    ),
    DRIVER_MODE_SUBSCRIPTION_MODE_TEMPLATE_RELATIONS={
        'by_mode_class': {},
        'by_work_mode': {'test_rule': 'orders_template'},
    },
)
@pytest.mark.parametrize(
    'rule_data, expected_error_msg',
    [
        pytest.param(
            mode_rules_create.RuleData(
                starts_at='2020-10-03T20:51:00+00:00',
                features=_ALL_FEATURES_WITH_DRIVER_FIX,
                billing_mode='driver_fix',
            ),
            None,
            marks=[
                pytest.mark.pgsql(
                    'driver_mode_subscription',
                    queries=[
                        mode_rules.patched_db(
                            patches=[
                                _make_rule_patch(
                                    '2020-08-10T20:51:00+00:00',
                                    '2020-08-12T20:51:00+00:00',
                                ),
                            ],
                        ),
                    ],
                ),
            ],
            id='no intersect, existing rule stops in past',
        ),
        pytest.param(
            mode_rules_create.RuleData(
                starts_at='2020-10-03T20:51:00+00:00',
                stops_at='2020-11-03T20:51:00+00:00',
                features=_ALL_FEATURES_WITH_DRIVER_FIX,
                billing_mode='driver_fix',
            ),
            None,
            marks=[
                pytest.mark.pgsql(
                    'driver_mode_subscription',
                    queries=[
                        mode_rules.patched_db(
                            patches=[
                                _make_rule_patch('2020-12-10T20:51:00+00:00'),
                            ],
                        ),
                    ],
                ),
            ],
            id='existing rule in future, new rule with stops_at',
        ),
        pytest.param(
            mode_rules_create.RuleData(
                starts_at='2020-08-03T20:51:00+00:00',
                features=_ALL_FEATURES_WITH_DRIVER_FIX,
                billing_mode='driver_fix',
            ),
            _make_intersection_error_message('2020-08-01T20:51:00+0000'),
            marks=[
                pytest.mark.pgsql(
                    'driver_mode_subscription',
                    queries=[
                        mode_rules.patched_db(
                            patches=[
                                _make_rule_patch(
                                    '2020-08-01T20:51:00+00:00',
                                    rule_id=_INTERSECT_RULE_ID,
                                ),
                            ],
                        ),
                    ],
                ),
            ],
            id='existing rule in past still active',
        ),
        pytest.param(
            mode_rules_create.RuleData(
                starts_at='2020-08-03T20:51:00+00:00',
                features=_ALL_FEATURES_WITH_DRIVER_FIX,
                billing_mode='driver_fix',
            ),
            'intersect with rules: [{id: 11111111111111111111111111111111, '
            'starts at: 2020-08-01T20:51:00+0000, '
            'stops_at: 2020-08-10T20:51:00+0000}, '
            '{id: 22222222222222222222222222222222, '
            'starts at: 2020-08-10T20:51:00+0000, '
            'stops_at: 2020-08-10T20:52:00+0000}]',
            marks=[
                pytest.mark.pgsql(
                    'driver_mode_subscription',
                    queries=[
                        mode_rules.patched_db(
                            patches=[
                                _make_rule_patch(
                                    '2020-08-01T20:51:00+00:00',
                                    '2020-08-10T20:51:00+00:00',
                                    rule_id=_INTERSECT_RULE_ID,
                                ),
                                _make_rule_patch(
                                    '2020-08-10T20:51:00+00:00',
                                    '2020-08-10T20:52:00+00:00',
                                    rule_id=_INTERSECT_RULE_ID2,
                                ),
                            ],
                        ),
                    ],
                ),
            ],
            id='intersect two rules',
        ),
        pytest.param(
            mode_rules_create.RuleData(
                starts_at='2020-08-03T20:51:00+00:00',
                features=_ALL_FEATURES_WITH_DRIVER_FIX,
                billing_mode='driver_fix',
            ),
            _make_intersection_error_message('2020-08-10T20:51:00+0000'),
            marks=[
                pytest.mark.pgsql(
                    'driver_mode_subscription',
                    queries=[
                        mode_rules.patched_db(
                            patches=[
                                _make_rule_patch(
                                    '2020-08-10T20:51:00+00:00',
                                    rule_id=_INTERSECT_RULE_ID,
                                ),
                            ],
                        ),
                    ],
                ),
            ],
            id='existing rule in future',
        ),
        pytest.param(
            mode_rules_create.RuleData(
                starts_at='2020-08-03T20:51:00+00:00',
                features=_ALL_FEATURES_WITH_DRIVER_FIX,
                billing_mode='driver_fix',
            ),
            _make_intersection_error_message(
                '2020-08-10T20:51:00+0000', '2020-08-11T20:51:00+0000',
            ),
            marks=[
                pytest.mark.pgsql(
                    'driver_mode_subscription',
                    queries=[
                        mode_rules.patched_db(
                            patches=[
                                _make_rule_patch(
                                    '2020-08-10T20:51:00+00:00',
                                    '2020-08-11T20:51:00+00:00',
                                    rule_id=_INTERSECT_RULE_ID,
                                ),
                            ],
                        ),
                    ],
                ),
            ],
            id='existing rule in future with stops_at',
        ),
        pytest.param(
            mode_rules_create.RuleData(
                starts_at='2020-08-03T20:51:00+00:00',
                features=_ALL_FEATURES_WITH_DRIVER_FIX,
                billing_mode='driver_fix',
            ),
            None,
            marks=[
                pytest.mark.pgsql(
                    'driver_mode_subscription',
                    queries=[
                        mode_rules.patched_db(
                            patches=[
                                _make_rule_patch(
                                    '2020-08-10T20:51:00+00:00',
                                    rule_id=_INTERSECT_RULE_ID,
                                    is_canceled=True,
                                ),
                            ],
                        ),
                    ],
                ),
            ],
            id='canceled rule in future',
        ),
        pytest.param(
            mode_rules_create.RuleData(
                starts_at='2020-08-03T20:51:00+00:00',
                features=_ALL_FEATURES_WITH_DRIVER_FIX,
                billing_mode='driver_fix',
            ),
            None,
            marks=[
                pytest.mark.pgsql(
                    'driver_mode_subscription',
                    queries=[
                        mode_rules.patched_db(
                            patches=[
                                _make_rule_patch(
                                    '2020-08-03T19:51:00+00:00',
                                    '2020-08-03T20:51:00+00:00',
                                    rule_id=_INTERSECT_RULE_ID,
                                ),
                            ],
                        ),
                    ],
                ),
            ],
            id='create_right_after_closed',
        ),
        pytest.param(
            mode_rules_create.RuleData(
                starts_at='2020-08-03T19:51:00+00:00',
                stops_at='2020-08-03T20:51:00+00:00',
                features=_ALL_FEATURES_WITH_DRIVER_FIX,
                billing_mode='driver_fix',
            ),
            None,
            marks=[
                pytest.mark.pgsql(
                    'driver_mode_subscription',
                    queries=[
                        mode_rules.patched_db(
                            patches=[
                                _make_rule_patch(
                                    '2020-08-03T20:51:00+00:00',
                                    '2020-08-03T21:51:00+00:00',
                                    rule_id=_INTERSECT_RULE_ID,
                                ),
                            ],
                        ),
                    ],
                ),
            ],
            id='create_right_before_next',
        ),
    ],
)
async def test_admin_mode_rules_check_create_intersection(
        taxi_driver_mode_subscription,
        rule_data: mode_rules_create.RuleData,
        expected_error_msg: Optional[str],
):
    await mode_rules_create.check_test_create_body_base(
        taxi_driver_mode_subscription,
        rule_data.as_request(),
        expected_error_msg,
        expected_error_msg,
    )


@pytest.mark.pgsql(
    'driver_mode_subscription',
    queries=[
        mode_rules.make_insert_offers_groups_sql({'taxi'}),
        mode_rules.init_admin_schema_version(),
    ],
)
@pytest.mark.now(_NOW)
@pytest.mark.config(
    BILLING_DRIVER_MODE_SETTINGS=(
        mode_rules_create.DEFAULT_BILLING_DRIVER_MODE_SETTINGS
    ),
    DRIVER_MODE_SUBSCRIPTION_OFFER_TEMPLATES=(
        offer_templates.DEFAULT_OFFER_TEMPLATES
    ),
    DRIVER_MODE_SUBSCRIPTION_MODE_TEMPLATE_RELATIONS={
        'by_mode_class': {},
        'by_work_mode': {'test_rule': 'orders_template'},
    },
)
@pytest.mark.parametrize(
    'rule_data, expected_error_msg',
    [
        pytest.param(
            mode_rules_create.RuleData(
                features=None, billing_mode='driver_fix',
            ),
            'Work mode "test_rule"\'s billing mode is "driver_fix", but there '
            'is no driver_fix feature',
            id='no driver_fix feature for billing_mode',
        ),
        pytest.param(
            mode_rules_create.RuleData(
                features=None,
                billing_mode='not_driver_fix',
                display_mode='driver_fix',
            ),
            'Work mode "test_rule"\'s display mode is "driver_fix", but there '
            'is no driver_fix feature',
            id='no driver_fix feature for billing_mode',
        ),
        pytest.param(
            mode_rules_create.RuleData(
                features=_ALL_FEATURES_WITH_DRIVER_FIX,
                billing_mode='not_driver_fix',
            ),
            'Work mode "test_rule"\'s feature driver_fix requires it\'s '
            'billing mode to be "driver_fix"',
            id='billing_mode required',
        ),
    ],
)
async def test_admin_mode_rules_check_create_driver_fix(
        taxi_driver_mode_subscription,
        rule_data: mode_rules_create.RuleData,
        expected_error_msg: Optional[str],
):
    await mode_rules_create.check_test_create_body_base(
        taxi_driver_mode_subscription,
        rule_data.as_request(),
        expected_error_msg,
        expected_error_msg,
    )


@pytest.mark.pgsql(
    'driver_mode_subscription',
    queries=[
        mode_rules.make_insert_offers_groups_sql({'taxi'}),
        mode_rules.init_admin_schema_version(),
    ],
)
@pytest.mark.now(_NOW)
@pytest.mark.config(
    BILLING_DRIVER_MODE_SETTINGS=(
        mode_rules_create.DEFAULT_BILLING_DRIVER_MODE_SETTINGS
    ),
    DRIVER_MODE_SUBSCRIPTION_OFFER_TEMPLATES=(
        offer_templates.DEFAULT_OFFER_TEMPLATES
    ),
    DRIVER_MODE_SUBSCRIPTION_MODE_TEMPLATE_RELATIONS={
        'by_mode_class': {},
        'by_work_mode': {'test_rule': 'orders_template'},
    },
)
@pytest.mark.parametrize(
    'rule_data, expected_error_msg',
    [
        pytest.param(
            mode_rules_create.RuleData(
                features=[
                    {
                        'name': 'booking',
                        'settings': {'slot_policy': 'mode_settings_rule_id'},
                    },
                ],
            ),
            (
                'Rule with booking slot_policy: "mode_settings_rule_id" '
                'must have one of following features: geobooking, driver_fix'
            ),
            id='no feature with mode_settings',
        ),
        pytest.param(
            mode_rules_create.RuleData(
                billing_mode='driver_fix',
                features=[
                    {
                        'name': 'driver_fix',
                        'settings': {'roles': [{'name': 'role1'}]},
                    },
                    {
                        'name': 'booking',
                        'settings': {'slot_policy': 'key_params'},
                    },
                ],
            ),
            (
                'Rule with booking slot policy: "key_params" '
                'must have geobooking feature'
            ),
            id='no feature with key_params',
        ),
    ],
)
async def test_admin_mode_rules_check_create_booking(
        taxi_driver_mode_subscription,
        rule_data: mode_rules_create.RuleData,
        expected_error_msg: Optional[str],
):
    await mode_rules_create.check_test_create_body_base(
        taxi_driver_mode_subscription,
        rule_data.as_request(),
        expected_error_msg,
        expected_error_msg,
    )
