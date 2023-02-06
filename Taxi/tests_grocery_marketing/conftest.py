# pylint: disable=wildcard-import, unused-wildcard-import, import-error
import pytest

from grocery_marketing_plugins import *  # noqa: F403 F401

from tests_grocery_marketing import common


@pytest.fixture
def default_admin_rules_headers():
    return common.DEFAULT_ADMIN_RULES_HEADERS


@pytest.fixture
def default_user_headers():
    return common.DEFAULT_USER_HEADERS


@pytest.fixture
def client(taxi_grocery_marketing):
    return taxi_grocery_marketing


@pytest.fixture
def condition_descriptions():
    return [
        {
            'name': 'menu_tags',
            'conditions': [
                {
                    'condition_name': 'country',
                    'type': 'text',
                    'default': {'value_type': 'Other'},
                    'support_any': True,
                    'support_other': True,
                    'exclusions_for_any': True,
                    'exclusions_for_other': True,
                    'exclusions_for_type': False,
                },
                {
                    'condition_name': 'city',
                    'type': 'text',
                    'default': {'value_type': 'Other'},
                    'support_any': True,
                    'support_other': True,
                    'exclusions_for_any': True,
                    'exclusions_for_other': True,
                    'exclusions_for_type': False,
                },
                {
                    'condition_name': 'depot',
                    'type': 'text',
                    'default': {'value_type': 'Other'},
                    'support_any': True,
                    'support_other': True,
                    'exclusions_for_any': True,
                    'exclusions_for_other': True,
                    'exclusions_for_type': False,
                },
                {
                    'condition_name': 'group',
                    'type': 'text',
                    'default': {'value_type': 'Other'},
                    'support_any': True,
                    'support_other': True,
                    'exclusions_for_any': True,
                    'exclusions_for_other': True,
                    'exclusions_for_type': False,
                },
                {
                    'condition_name': 'product',
                    'type': 'text',
                    'default': {'value_type': 'Other'},
                    'support_any': True,
                    'support_other': True,
                    'exclusions_for_any': True,
                    'exclusions_for_other': True,
                    'exclusions_for_type': False,
                },
                {
                    'condition_name': 'active_period',
                    'type': 'time_range',
                    'default': {
                        'value': {
                            'start': '2000-01-01T00:00:00+00:00',
                            'is_start_utc': False,
                            'is_end_utc': False,
                            'end': '2262-04-11T23:47:16.854775807+00:00',
                        },
                    },
                    'support_any': False,
                    'support_other': False,
                    'exclusions_for_any': False,
                    'exclusions_for_other': False,
                    'exclusions_for_type': False,
                },
                {
                    'condition_name': 'rule_id',
                    'type': 'text',
                    'default': {'value_type': 'Other'},
                    'support_any': True,
                    'support_other': True,
                    'exclusions_for_any': True,
                    'exclusions_for_other': True,
                    'exclusions_for_type': False,
                },
            ],
        },
    ]


@pytest.fixture
def hierarchy_descriptions_url():
    return 'admin/v1/marketing/v1/match-tags/hierarchy-descriptions'


@pytest.fixture
def headers():
    return common.get_headers()


@pytest.fixture
def service_name():
    return 'grocery_marketing'
