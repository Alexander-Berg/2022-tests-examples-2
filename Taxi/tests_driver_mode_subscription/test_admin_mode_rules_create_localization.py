from typing import Optional

import pytest

from tests_driver_mode_subscription import mode_rules
from tests_driver_mode_subscription import mode_rules_create
from tests_driver_mode_subscription import offer_templates


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
    DRIVER_MODE_RULES_VALIDATION_SETTINGS={
        'rule_draft_starts_min_threshold_m': 120,
        'is_template_validation_enabled': True,
    },
)
@pytest.mark.parametrize(
    'rule_data, expected_error_msg',
    [
        pytest.param(
            mode_rules_create.RuleData(),
            'Missing translation for key: Failed to localize keyset=driver_fix'
            ' key=missing_key locale=ru',
            marks=[
                pytest.mark.config(
                    DRIVER_MODE_SUBSCRIPTION_OFFER_TEMPLATES={
                        'templates': {
                            'orders_template': {
                                'model': {'title': 'offer_card.orders_title'},
                                'schema': {
                                    'card_items': [
                                        {
                                            'type': 'card_header',
                                            'data': {
                                                'icon_type': 'passenger',
                                                'description': 'missing_key',
                                                'subtitle': 'missing_key',
                                            },
                                        },
                                    ],
                                    'screen_items': [
                                        {
                                            'type': 'header',
                                            'data': {'text': 'missing_key'},
                                        },
                                        {
                                            'type': 'multi_paragraph_text',
                                            'data': {'text': 'missing_key'},
                                        },
                                    ],
                                    'memo_items': [
                                        {
                                            'type': 'header',
                                            'data': {'text': 'missing_key'},
                                        },
                                        {
                                            'type': 'multi_paragraph_text',
                                            'data': {'text': 'missing_key'},
                                        },
                                    ],
                                },
                            },
                        },
                    },
                ),
            ],
            id='no_key_in_tanker_from_template',
        ),
        pytest.param(
            mode_rules_create.RuleData(),
            'Missing template \'orders_template\' in '
            'DRIVER_MODE_SUBSCRIPTION_OFFER_TEMPLATES',
            marks=[
                pytest.mark.config(
                    DRIVER_MODE_SUBSCRIPTION_OFFER_TEMPLATES={'templates': {}},
                ),
            ],
            id='no_template',
        ),
        pytest.param(
            mode_rules_create.RuleData(),
            'Missing translation for key: Failed to localize keyset=driver_fix'
            ' key=missing_key locale=ru',
            marks=[
                pytest.mark.config(
                    DRIVER_MODE_SUBSCRIPTION_OFFER_TEMPLATES={
                        'templates': {
                            'orders_template': {
                                **offer_templates.DEFAULT_ORDERS_TEMPLATE,
                                **{'model': {'title': 'missing_key'}},
                            },
                        },
                    },
                ),
            ],
            id='no_key_in_tanker_from_model',
        ),
        pytest.param(
            mode_rules_create.RuleData(),
            None,
            marks=[
                pytest.mark.config(
                    DRIVER_MODE_SUBSCRIPTION_OFFER_TEMPLATES={
                        'templates': {
                            'orders_template': {
                                **offer_templates.DEFAULT_ORDERS_TEMPLATE,
                                **{'model': {'title': 'missing_key'}},
                            },
                        },
                    },
                    DRIVER_MODE_RULES_VALIDATION_SETTINGS={
                        'rule_draft_starts_min_threshold_m': 120,
                        'is_template_validation_enabled': False,
                    },
                ),
            ],
            id='template_check_disabled',
        ),
        pytest.param(
            mode_rules_create.RuleData('uberdriver', offers_group=None),
            'Missing template name for work mode \'uberdriver\' in '
            'DRIVER_MODE_SUBSCRIPTION_MODE_TEMPLATE_RELATIONS',
            id='check_template_for_no_offers',
        ),
        pytest.param(
            mode_rules_create.RuleData(
                'driver_fix',
                billing_mode='driver_fix',
                features=[{'name': 'driver_fix', 'settings': {}}],
            ),
            'Missing template name for work mode \'driver_fix\' in '
            'DRIVER_MODE_SUBSCRIPTION_MODE_TEMPLATE_RELATIONS',
            id='check_template_for_driver_fix',
        ),
        pytest.param(
            mode_rules_create.RuleData(
                'geobooking',
                features=[{'name': 'geobooking', 'settings': {}}],
            ),
            'Missing template name for work mode \'geobooking\' in '
            'DRIVER_MODE_SUBSCRIPTION_MODE_TEMPLATE_RELATIONS',
            id='check_template_for_geobooking',
        ),
        pytest.param(
            mode_rules_create.RuleData(
                'driver_fix',
                billing_mode='driver_fix',
                features=[{'name': 'driver_fix', 'settings': {}}],
            ),
            None,
            marks=[
                pytest.mark.config(
                    DRIVER_MODE_SUBSCRIPTION_MODE_TEMPLATE_RELATIONS={
                        'by_mode_class': {},
                        'by_work_mode': {'driver_fix': 'orders_template'},
                    },
                    DRIVER_MODE_SUBSCRIPTION_OFFER_TEMPLATES={
                        'templates': {
                            'orders_template': {
                                'model': {'title': 'offer_card.orders_title'},
                                'schema': {
                                    'card_items': [
                                        {
                                            'type': 'driver_fix_card_header',
                                            'data': {'icon_type': 'time'},
                                        },
                                    ],
                                    'screen_items': [
                                        {
                                            'type': 'header',
                                            'data': {
                                                'text': (
                                                    'offer_card.orders_title'
                                                ),
                                            },
                                        },
                                    ],
                                    'memo_items': [
                                        {
                                            'type': 'header',
                                            'data': {
                                                'text': (
                                                    'offer_card.orders_title'
                                                ),
                                            },
                                        },
                                    ],
                                },
                            },
                        },
                    },
                ),
            ],
            id='ok_driver_fix_card_header',
        ),
        pytest.param(
            mode_rules_create.RuleData(
                'geobooking',
                features=[{'name': 'geobooking', 'settings': {}}],
            ),
            None,
            marks=[
                pytest.mark.config(
                    DRIVER_MODE_SUBSCRIPTION_MODE_TEMPLATE_RELATIONS={
                        'by_mode_class': {},
                        'by_work_mode': {'geobooking': 'orders_template'},
                    },
                    DRIVER_MODE_SUBSCRIPTION_OFFER_TEMPLATES={
                        'templates': {
                            'orders_template': {
                                'model': {'title': 'offer_card.orders_title'},
                                'schema': {
                                    'card_items': [
                                        {
                                            'type': 'geobooking_card_header',
                                            'data': {'icon_type': 'time'},
                                        },
                                    ],
                                    'screen_items': [
                                        {
                                            'type': 'header',
                                            'data': {
                                                'text': (
                                                    'offer_card.orders_title'
                                                ),
                                            },
                                        },
                                    ],
                                    'memo_items': [
                                        {
                                            'type': 'header',
                                            'data': {
                                                'text': (
                                                    'offer_card.orders_title'
                                                ),
                                            },
                                        },
                                    ],
                                },
                            },
                        },
                    },
                ),
            ],
            id='ok_geobooking_card_header',
        ),
        pytest.param(
            mode_rules_create.RuleData(),
            'Template orders_template is invalid: Offer card template must not'
            ' be empty',
            marks=[
                pytest.mark.config(
                    DRIVER_MODE_SUBSCRIPTION_OFFER_TEMPLATES={
                        'templates': {
                            'orders_template': {
                                'model': {'title': 'offer_card.orders_title'},
                                'schema': {
                                    'card_items': [],
                                    'screen_items': [
                                        {
                                            'type': 'header',
                                            'data': {
                                                'text': (
                                                    'offer_card.orders_title'
                                                ),
                                            },
                                        },
                                    ],
                                    'memo_items': [
                                        {
                                            'type': 'header',
                                            'data': {
                                                'text': (
                                                    'offer_card.orders_title'
                                                ),
                                            },
                                        },
                                    ],
                                },
                            },
                        },
                    },
                ),
            ],
            id='fail_empty_card',
        ),
        pytest.param(
            mode_rules_create.RuleData(),
            'Template orders_template is invalid: card_header must be the '
            'first item of card template',
            marks=[
                pytest.mark.config(
                    DRIVER_MODE_SUBSCRIPTION_OFFER_TEMPLATES={
                        'templates': {
                            'orders_template': {
                                'model': {'title': 'offer_card.orders_title'},
                                'schema': {
                                    'card_items': [
                                        {'type': 'booking_info'},
                                        {
                                            'type': 'geobooking_card_header',
                                            'data': {'icon_type': 'time'},
                                        },
                                    ],
                                    'screen_items': [
                                        {
                                            'type': 'header',
                                            'data': {
                                                'text': (
                                                    'offer_card.orders_title'
                                                ),
                                            },
                                        },
                                    ],
                                    'memo_items': [
                                        {
                                            'type': 'header',
                                            'data': {
                                                'text': (
                                                    'offer_card.orders_title'
                                                ),
                                            },
                                        },
                                    ],
                                },
                            },
                        },
                    },
                ),
            ],
            id='fail_card_header_order',
        ),
        pytest.param(
            mode_rules_create.RuleData('uberdriver', offers_group=None),
            None,
            marks=[
                pytest.mark.config(
                    DRIVER_MODE_SUBSCRIPTION_MODE_TEMPLATE_RELATIONS={
                        'by_mode_class': {},
                        'by_work_mode': {'uberdriver': 'orders_template'},
                    },
                    DRIVER_MODE_SUBSCRIPTION_OFFER_TEMPLATES={
                        'templates': {
                            'orders_template': {
                                'model': {'title': 'offer_card.orders_title'},
                                'schema': {
                                    'card_items': [],
                                    'screen_items': [],
                                    'memo_items': [],
                                },
                            },
                        },
                    },
                ),
            ],
            id='ok_card_header_no_offers',
        ),
        pytest.param(
            mode_rules_create.RuleData(),
            'Template orders_template is invalid: Offer screen template must '
            'not be empty',
            marks=[
                pytest.mark.config(
                    DRIVER_MODE_SUBSCRIPTION_OFFER_TEMPLATES={
                        'templates': {
                            'orders_template': {
                                'model': {'title': 'offer_card.orders_title'},
                                'schema': {
                                    'card_items': [
                                        {
                                            'type': 'card_header',
                                            'data': {
                                                'icon_type': 'passenger',
                                                'description': 'missing_key',
                                                'subtitle': 'missing_key',
                                            },
                                        },
                                    ],
                                    'screen_items': [],
                                    'memo_items': [
                                        {
                                            'type': 'header',
                                            'data': {
                                                'text': (
                                                    'offer_card.orders_title'
                                                ),
                                            },
                                        },
                                    ],
                                },
                            },
                        },
                    },
                ),
            ],
            id='fail_empty_screen',
        ),
        pytest.param(
            mode_rules_create.RuleData(),
            'Template orders_template is invalid: Offer memo screen template '
            'must not be empty',
            marks=[
                pytest.mark.config(
                    DRIVER_MODE_SUBSCRIPTION_OFFER_TEMPLATES={
                        'templates': {
                            'orders_template': {
                                'model': {'title': 'offer_card.orders_title'},
                                'schema': {
                                    'card_items': [
                                        {
                                            'type': 'card_header',
                                            'data': {
                                                'icon_type': 'passenger',
                                                'description': 'missing_key',
                                                'subtitle': 'missing_key',
                                            },
                                        },
                                    ],
                                    'screen_items': [
                                        {
                                            'type': 'header',
                                            'data': {
                                                'text': (
                                                    'offer_card.orders_title'
                                                ),
                                            },
                                        },
                                    ],
                                    'memo_items': [],
                                },
                            },
                        },
                    },
                ),
            ],
            id='fail_empty_memo',
        ),
    ],
)
async def test_admin_mode_rules_check_create_localization(
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
