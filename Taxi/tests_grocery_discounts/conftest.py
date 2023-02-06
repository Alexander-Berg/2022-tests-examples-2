# pylint: disable=wildcard-import, unused-wildcard-import, import-error
import copy
from typing import List

from grocery_discounts_plugins import *  # noqa: F403 F401
import pytest

from tests_grocery_discounts import common


@pytest.fixture(autouse=True)
def search_root_request(mockserver):
    @mockserver.json_handler(
        '/overlord-catalog/admin/categories/v1/search/root',
    )
    def _search_root(request):
        return {
            'result': [
                {
                    'category_id': (
                        '459ecd66305f43e68e72753338be759b000200010001'
                    ),
                    'title': '\u0424\u0420\u041e\u041d\u0422',
                    'depot_ids': [
                        'f2cf987af49f4644b82c593256a3053a000300010000',
                        '9e9303fefd204a45a41b467142d60e07000200010001',
                        '2e56710cfb0a4478be265f436e6baad9000200010001',
                        'da4463fdbaa340f7b830e66836f297fa000200010001',
                        '518fc4e6b04a46aa98c3257b4b60298e000300010000',
                        '38a168e1ffe44d609fa92caf8707a853000100010001',
                        'ddb8a6fbcee34b38b5281d8ea6ef749a000100010000',
                        'f98988de43a1440691250c0589b71f3b000200010000',
                        'f84a99a151ce4aa4a880ba4a596ae61f000100010001',
                        '20ecd9e20e34401c938b67980aec224e000300010000',
                        '509615719b324db4a60672833b00320f000200010001',
                        'a5c53daaf50f4efb9fc6f03bec682f21000300010000',
                        'fb33f182f7af4e43bb4035536af35814000200010001',
                        '6a7acf5a239f47aa93a8966a0df9dfdd000300010000',
                        '13493eb88b1b42c1a9a30a9bfdb4d39f000200010000',
                        'f95b8bec5307401ea4e0e821dded09cb000200010001',
                    ],
                    'status': 'active',
                    'store_ids': [
                        '120345',
                        '91456',
                        '72554',
                        '60287',
                        '103547',
                        '112360',
                        '71249',
                        '106383',
                        '125065',
                        '91168',
                        '139065',
                        '106355',
                        '108603',
                        '106375',
                        '92348',
                        '87254',
                    ],
                },
                {
                    'category_id': (
                        '2a62043aea5249c3ad8f7964bdef6b13000100010001'
                    ),
                    'title': (
                        '\u0424\u0420\u041e\u041d\u0422 '
                        '\u041c\u0410\u0413\u041d\u0418\u0422'
                    ),
                    'depot_ids': [],
                    'status': 'active',
                    'store_ids': [],
                },
                {
                    'category_id': (
                        '7ab2cec3d8a840ecb9f26ffd1afd0d86000300010000'
                    ),
                    'title': '\u041c\u0410\u0421\u0422\u0415\u0420',
                    'depot_ids': [],
                    'status': 'disabled',
                    'store_ids': [],
                },
                {
                    'category_id': 'root1',
                    'title': 'Root for tests 1',
                    'depot_ids': [
                        'b63a9024217448279784cd2f19dfc187000200010000',
                    ],
                    'status': 'active',
                    'store_ids': ['depot1', 'depot3'],
                },
                {
                    'category_id': 'root2',
                    'title': 'Root for tests 2',
                    'depot_ids': [
                        '75985fcda4ba4b2f9d5febc5cd74a974000200010000',
                        '597e92446a5648e8be81b148ff462643000200010000',
                    ],
                    'status': 'active',
                    'store_ids': ['depot2'],
                },
                {
                    'category_id': 'root3',
                    'title': 'Root for tests 3',
                    'depot_ids': [
                        '658747cc77f84685a8c633bfa3089d31000200010000',
                    ],
                    'status': 'active',
                    'store_ids': ['depot5'],
                },
            ],
        }


@pytest.fixture
def default_headers():
    return common.DEFAULT_DISCOUNTS_HEADERS


@pytest.fixture
def client(taxi_grocery_discounts):
    return taxi_grocery_discounts


@pytest.fixture
def headers():
    return common.DEFAULT_DISCOUNTS_HEADERS


@pytest.fixture
def add_rules_url():
    return common.ADD_RULES_URL


@pytest.fixture
def add_rules_check_url():
    return common.ADD_RULES_CHECK_URL


@pytest.fixture
def default_discount():
    return common.small_menu_discount()


@pytest.fixture
def service_name():
    return 'grocery_discounts'


@pytest.fixture
def condition_descriptions() -> List[dict]:
    condition_tag = {
        'condition_name': 'tag',
        'type': 'text',
        'default': {'value_type': 'Other'},
        'support_any': True,
        'support_other': True,
        'exclusions_for_any': True,
        'exclusions_for_other': True,
        'exclusions_for_type': False,
    }
    condition_class = {
        'condition_name': 'class',
        'type': 'text',
        'default': {'value': 'No class'},
        'support_any': False,
        'support_other': False,
        'exclusions_for_any': False,
        'exclusions_for_other': False,
        'exclusions_for_type': False,
    }
    condition_experiment = {
        'condition_name': 'experiment',
        'type': 'text',
        'default': {'value_type': 'Other'},
        'support_any': True,
        'support_other': True,
        'exclusions_for_any': True,
        'exclusions_for_other': True,
        'exclusions_for_type': False,
    }
    condition_has_yaplus = {
        'condition_name': 'has_yaplus',
        'default': {'value_type': 'Other'},
        'exclusions_for_any': False,
        'exclusions_for_other': False,
        'exclusions_for_type': False,
        'support_any': True,
        'support_other': True,
        'type': 'bool',
    }
    condition_active_with_surge = {
        'condition_name': 'active_with_surge',
        'default': {'value_type': 'Other'},
        'exclusions_for_any': False,
        'exclusions_for_other': False,
        'exclusions_for_type': False,
        'support_any': True,
        'support_other': True,
        'type': 'bool',
    }
    condition_application_name = {
        'condition_name': 'application_name',
        'type': 'text',
        'default': {'value_type': 'Other'},
        'support_any': True,
        'support_other': True,
        'exclusions_for_any': True,
        'exclusions_for_other': True,
        'exclusions_for_type': False,
    }
    condition_country = {
        'condition_name': 'country',
        'type': 'text',
        'default': {'value_type': 'Other'},
        'support_any': True,
        'support_other': True,
        'exclusions_for_any': True,
        'exclusions_for_other': True,
        'exclusions_for_type': False,
    }
    condition_city = {
        'condition_name': 'city',
        'type': 'text',
        'default': {'value_type': 'Other'},
        'support_any': True,
        'support_other': True,
        'exclusions_for_any': True,
        'exclusions_for_other': True,
        'exclusions_for_type': False,
    }
    condition_depot = {
        'condition_name': 'depot',
        'type': 'text',
        'default': {'value_type': 'Other'},
        'support_any': True,
        'support_other': True,
        'exclusions_for_any': True,
        'exclusions_for_other': True,
        'exclusions_for_type': False,
    }
    condition_product_set = {
        'condition_name': 'product_set',
        'type': 'array',
        'default': {'value': []},
        'support_any': False,
        'support_other': False,
        'exclusions_for_any': False,
        'exclusions_for_other': False,
        'exclusions_for_type': False,
    }
    condition_orders_restriction = {
        'condition_name': 'orders_restriction',
        'default': {'value_type': 'Other'},
        'exclusions_for_any': True,
        'exclusions_for_other': True,
        'exclusions_for_type': False,
        'support_any': True,
        'support_other': True,
        'type': 'orders_restriction',
    }
    condition_active_period = {
        'condition_name': 'active_period',
        'type': 'time_range',
        'default': {
            'value': {
                'start': '2000-01-01T00:00:00+00:00',
                'is_start_utc': False,
                'is_end_utc': False,
            },
        },
        'support_any': False,
        'support_other': False,
        'exclusions_for_any': False,
        'exclusions_for_other': False,
        'exclusions_for_type': False,
    }
    condition_master_group = {
        'condition_name': 'master_group',
        'type': 'text',
        'default': {'value_type': 'Other'},
        'support_any': True,
        'support_other': True,
        'exclusions_for_any': True,
        'exclusions_for_other': True,
        'exclusions_for_type': False,
    }
    condition_group = {
        'condition_name': 'group',
        'type': 'text',
        'default': {'value_type': 'Other'},
        'support_any': True,
        'support_other': True,
        'exclusions_for_any': True,
        'exclusions_for_other': True,
        'exclusions_for_type': False,
    }
    condition_payment_method = {
        'condition_name': 'payment_method',
        'type': 'text',
        'default': {'value_type': 'Other'},
        'support_any': True,
        'support_other': True,
        'exclusions_for_any': True,
        'exclusions_for_other': True,
        'exclusions_for_type': False,
    }
    condition_product = {
        'condition_name': 'product',
        'type': 'text',
        'default': {'value_type': 'Other'},
        'support_any': True,
        'support_other': True,
        'exclusions_for_any': True,
        'exclusions_for_other': True,
        'exclusions_for_type': False,
    }
    condition_label = {
        'condition_name': 'label',
        'type': 'text',
        'default': {'value': 'default'},
        'support_any': False,
        'support_other': False,
        'exclusions_for_any': False,
        'exclusions_for_other': False,
        'exclusions_for_type': False,
    }
    condition_bins = {
        'condition_name': 'bins',
        'type': 'text',
        'default': {'value_type': 'Other'},
        'support_any': True,
        'support_other': True,
        'exclusions_for_any': True,
        'exclusions_for_other': True,
        'exclusions_for_type': False,
    }
    return [
        {
            'name': 'cart_discounts',
            'conditions': [
                copy.deepcopy(condition_class),
                copy.deepcopy(condition_experiment),
                copy.deepcopy(condition_tag),
                copy.deepcopy(condition_has_yaplus),
                copy.deepcopy(condition_active_with_surge),
                copy.deepcopy(condition_application_name),
                copy.deepcopy(condition_country),
                copy.deepcopy(condition_city),
                copy.deepcopy(condition_depot),
                copy.deepcopy(condition_product_set),
                copy.deepcopy(condition_orders_restriction),
                copy.deepcopy(condition_active_period),
            ],
        },
        {
            'name': 'cart_cashback',
            'conditions': [
                copy.deepcopy(condition_class),
                copy.deepcopy(condition_experiment),
                copy.deepcopy(condition_tag),
                copy.deepcopy(condition_has_yaplus),
                copy.deepcopy(condition_active_with_surge),
                copy.deepcopy(condition_application_name),
                copy.deepcopy(condition_country),
                copy.deepcopy(condition_city),
                copy.deepcopy(condition_depot),
                copy.deepcopy(condition_product_set),
                copy.deepcopy(condition_orders_restriction),
                copy.deepcopy(condition_active_period),
            ],
        },
        {
            'name': 'dynamic_discounts',
            'conditions': [
                copy.deepcopy(condition_label),
                copy.deepcopy(condition_active_period),
            ],
        },
        {
            'name': 'markdown_discounts',
            'conditions': [
                copy.deepcopy(condition_tag),
                copy.deepcopy(condition_has_yaplus),
                copy.deepcopy(condition_country),
                copy.deepcopy(condition_city),
                copy.deepcopy(condition_depot),
                copy.deepcopy(condition_master_group),
                copy.deepcopy(condition_product),
                copy.deepcopy(condition_active_period),
            ],
        },
        {
            'name': 'suppliers_discounts',
            'conditions': [
                copy.deepcopy(condition_country),
                copy.deepcopy(condition_city),
                copy.deepcopy(condition_product),
                copy.deepcopy(condition_active_period),
            ],
        },
        {
            'name': 'suppliers_cashback',
            'conditions': [
                copy.deepcopy(condition_country),
                copy.deepcopy(condition_city),
                copy.deepcopy(condition_product),
                copy.deepcopy(condition_active_period),
            ],
        },
        {
            'name': 'menu_discounts',
            'conditions': [
                copy.deepcopy(condition_class),
                copy.deepcopy(condition_experiment),
                copy.deepcopy(condition_tag),
                copy.deepcopy(condition_has_yaplus),
                copy.deepcopy(condition_country),
                copy.deepcopy(condition_city),
                copy.deepcopy(condition_depot),
                copy.deepcopy(condition_master_group),
                copy.deepcopy(condition_group),
                copy.deepcopy(condition_product),
                copy.deepcopy(condition_orders_restriction),
                copy.deepcopy(condition_active_period),
            ],
        },
        {
            'name': 'menu_cashback',
            'conditions': [
                copy.deepcopy(condition_class),
                copy.deepcopy(condition_experiment),
                copy.deepcopy(condition_tag),
                copy.deepcopy(condition_has_yaplus),
                copy.deepcopy(condition_country),
                copy.deepcopy(condition_city),
                copy.deepcopy(condition_depot),
                copy.deepcopy(condition_master_group),
                copy.deepcopy(condition_group),
                copy.deepcopy(condition_product),
                copy.deepcopy(condition_orders_restriction),
                copy.deepcopy(condition_active_period),
            ],
        },
        {
            'name': 'bundle_discounts',
            'conditions': [
                copy.deepcopy(condition_class),
                copy.deepcopy(condition_experiment),
                copy.deepcopy(condition_tag),
                copy.deepcopy(condition_has_yaplus),
                copy.deepcopy(condition_country),
                copy.deepcopy(condition_city),
                copy.deepcopy(condition_depot),
                copy.deepcopy(condition_master_group),
                copy.deepcopy(condition_group),
                copy.deepcopy(condition_product),
                copy.deepcopy(condition_orders_restriction),
                copy.deepcopy(condition_active_period),
            ],
        },
        {
            'name': 'bundle_cashback',
            'conditions': [
                copy.deepcopy(condition_class),
                copy.deepcopy(condition_experiment),
                copy.deepcopy(condition_tag),
                copy.deepcopy(condition_has_yaplus),
                copy.deepcopy(condition_country),
                copy.deepcopy(condition_city),
                copy.deepcopy(condition_depot),
                copy.deepcopy(condition_master_group),
                copy.deepcopy(condition_group),
                copy.deepcopy(condition_product),
                copy.deepcopy(condition_orders_restriction),
                copy.deepcopy(condition_active_period),
            ],
        },
        {
            'name': 'payment_method_discounts',
            'conditions': [
                copy.deepcopy(condition_class),
                copy.deepcopy(condition_experiment),
                copy.deepcopy(condition_has_yaplus),
                copy.deepcopy(condition_application_name),
                copy.deepcopy(condition_country),
                copy.deepcopy(condition_city),
                copy.deepcopy(condition_depot),
                copy.deepcopy(condition_payment_method),
                copy.deepcopy(condition_bins),
                copy.deepcopy(condition_master_group),
                copy.deepcopy(condition_group),
                copy.deepcopy(condition_product),
                copy.deepcopy(condition_active_period),
            ],
        },
        {
            'name': 'payment_method_cashback',
            'conditions': [
                copy.deepcopy(condition_class),
                copy.deepcopy(condition_experiment),
                copy.deepcopy(condition_has_yaplus),
                copy.deepcopy(condition_application_name),
                copy.deepcopy(condition_country),
                copy.deepcopy(condition_city),
                copy.deepcopy(condition_depot),
                copy.deepcopy(condition_payment_method),
                copy.deepcopy(condition_bins),
                copy.deepcopy(condition_master_group),
                copy.deepcopy(condition_group),
                copy.deepcopy(condition_product),
                copy.deepcopy(condition_active_period),
            ],
        },
    ]


@pytest.fixture()
def hierarchy_descriptions_url():
    return '/v3/admin/match-discounts/hierarchy-descriptions'
