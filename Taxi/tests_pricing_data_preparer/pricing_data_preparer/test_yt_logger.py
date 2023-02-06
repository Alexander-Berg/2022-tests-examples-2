# pylint: disable=redefined-outer-name, import-only-modules
# pylint: disable=too-many-lines
# flake8: noqa F401
import pytest

from testsuite.utils import matching

from .plugins import test_utils
from .plugins import utils_request
from .round_values import round_values

from .plugins.mock_user_api import user_api
from .plugins.mock_user_api import mock_user_api_get_phones
from .plugins.mock_user_api import mock_user_api_get_users
from .plugins.mock_surge import surger
from .plugins.mock_surge import mock_surger
from .plugins.mock_ride_discounts import ride_discounts
from .plugins.mock_ride_discounts import mock_ride_discounts
from .plugins.mock_tags import tags
from .plugins.mock_tags import mock_tags
from .plugins.mock_coupons import coupons
from .plugins.mock_coupons import mock_coupons
from .plugins.mock_decoupling import decoupling
from .plugins.mock_decoupling import mock_decoupling_corp_tariffs
from .plugins.utils_response import econom_category
from .plugins.utils_response import econom_response
from .plugins.utils_response import business_category
from .plugins.utils_response import business_response
from .plugins.utils_response import econom_with_additional_prices
from .plugins.utils_response import decoupling_response
from .plugins.utils_response import category_list
from .plugins.utils_response import calc_price
from .plugins.mock_order_core import mock_order_core
from .plugins.mock_order_core import OrderIdRequestType
from .plugins.mock_order_core import order_core


class ExtendUuidString(matching.UuidString):
    """Matches lower-case hexadecimal uuid string included character '-'."""

    def __eq__(self, other):
        return super().__eq__(other.replace('-', ''))


extend_uuid_string = ExtendUuidString()  # pylint: disable=invalid-name

ECONOM_COMMON = {
    'disable_surge': False,
    'caller_link': 'parent_link',
    'disable_fixed_price': False,
    'is_corp_decoupling': False,
    'is_decoupling': False,
    'stat': {
        'corp_tariffs': 'not_used',
        'coupons': 'not_used',
        'discounts': 'success',
        'phone': 'success',
        'route_with_jams': 'success',
        'route_without_jams': 'not_used',
        'surge': 'success',
        'tags': 'success',
        'user': 'success',
    },
    'tariff_name': 'moscow',
    'timestamp': '2019-02-01T17:00:00+03:00',
    'uuid': matching.uuid_string,
    'waypoints': [[37.683, 55.774], [37.656, 55.764]],
    'link': matching.uuid_string,
    'extra': {
        'surge_calculation_id': '012345678901234567890123',
        'uuids': {
            'driver_category': {'econom': matching.uuid_string},
            'user_category': {'econom': matching.uuid_string},
            'driver_routes': {},
            'user_routes': {'econom': extend_uuid_string},
        },
    },
    'due': '2019-02-01T17:00:00+03:00',
}
DECOUPLING_COMMON = {
    'caller_link': 'parent_link',
    'disable_fixed_price': False,
    'disable_paid_supply': False,
    'disable_surge': False,
    'is_corp_decoupling': True,
    'is_decoupling': True,
    'stat': {
        'corp_tariffs': 'success',
        'coupons': 'not_used',
        'discounts': 'success',
        'phone': 'success',
        'route_with_jams': 'success',
        'route_without_jams': 'not_used',
        'surge': 'success',
        'tags': 'success',
        'user': 'success',
    },
    'tariff_name': 'moscow',
    'timestamp': '2019-02-01T17:00:00+03:00',
    'uuid': matching.uuid_string,
    'waypoints': [[37.683, 55.774], [37.656, 55.764]],
    'link': matching.uuid_string,
    'extra': {
        'surge_calculation_id': '012345678901234567890123',
        'uuids': {
            'driver_category': {'econom': matching.uuid_string},
            'user_category': {'econom': matching.uuid_string},
            'driver_routes': {'econom': extend_uuid_string},
            'user_routes': {'econom': extend_uuid_string},
        },
    },
    'due': '2019-02-01T17:00:00+03:00',
}

BUSINESS_COMMON = {
    'disable_surge': False,
    'caller_link': 'parent_link',
    'disable_fixed_price': False,
    'is_corp_decoupling': False,
    'is_decoupling': False,
    'stat': {
        'corp_tariffs': 'not_used',
        'coupons': 'not_used',
        'discounts': 'success',
        'phone': 'success',
        'route_with_jams': 'success',
        'route_without_jams': 'not_used',
        'surge': 'success',
        'tags': 'success',
        'user': 'success',
    },
    'tariff_name': 'moscow',
    'timestamp': '2019-02-01T17:00:00+03:00',
    'uuid': matching.uuid_string,
    'waypoints': [[37.683, 55.774], [37.656, 55.764]],
    'link': matching.uuid_string,
    'extra': {
        'surge_calculation_id': '012345678901234567890123',
        'uuids': {
            'driver_category': {
                'econom': matching.uuid_string,
                'business': matching.uuid_string,
            },
            'user_category': {
                'econom': matching.uuid_string,
                'business': matching.uuid_string,
            },
            'driver_routes': {},
            'user_routes': {
                'econom': extend_uuid_string,
                'business': extend_uuid_string,
            },
        },
    },
    'due': '2019-02-01T17:00:00+03:00',
}

ADDITIONAL_PRICES_COMMON = {
    'disable_surge': False,
    'caller_link': 'parent_link',
    'disable_fixed_price': False,
    'is_corp_decoupling': False,
    'is_decoupling': False,
    'stat': {
        'corp_tariffs': 'not_used',
        'coupons': 'not_used',
        'discounts': 'success',
        'phone': 'success',
        'route_with_jams': 'success',
        'route_without_jams': 'not_used',
        'surge': 'success',
        'tags': 'success',
        'user': 'success',
    },
    'tariff_name': 'moscow',
    'timestamp': '2019-02-01T17:00:00+03:00',
    'uuid': matching.uuid_string,
    'waypoints': [[37.683, 55.774], [37.656, 55.764]],
    'link': matching.uuid_string,
    'extra': {
        'surge_calculation_id': '012345678901234567890123',
        'uuids': {
            'driver_category': {'econom': matching.uuid_string},
            'user_category': {'econom': matching.uuid_string},
            'driver_routes': {},
            'user_routes': {'econom': extend_uuid_string},
        },
    },
    'due': '2019-02-01T17:00:00+03:00',
}

ECONOM_ROUTE_JAMS = {
    'blocked': False,
    'caller_link': 'parent_link',
    'points': [
        [37.683, 55.774, 0.0, 0.0],
        [37.674, 55.772, 605.0, 90.0],
        [37.662, 55.766, 1610.0, 241.0],
        [37.656, 55.764, 2046.0, 307.0],
    ],
    'router_settings': {
        'intent': 'ROUTESTATS',
        'jams': True,
        'mode': 'approx',
        'request_id': matching.uuid_string,
        'tolls': False,
        'user_id': 'some_user_id',
    },
    'timestamp': '2019-02-01T17:00:00+03:00',
    'uuid': extend_uuid_string,
    'distance': 2046,
    'jams': True,
    'time': 307,
    'tolls': False,
}

DECOUIPLING_ROUTE_JAMS = {
    'blocked': False,
    'caller_link': 'parent_link',
    'points': [
        [37.683, 55.774, 0.0, 0.0],
        [37.674, 55.772, 605.0, 90.0],
        [37.662, 55.766, 1610.0, 241.0],
        [37.656, 55.764, 2046.0, 307.0],
    ],
    'router_settings': {
        'intent': 'ROUTESTATS',
        'jams': True,
        'mode': 'approx',
        'request_id': matching.uuid_string,
        'tolls': False,
        'user_id': 'some_user_id',
    },
    'timestamp': '2019-02-01T17:00:00+03:00',
    'uuid': extend_uuid_string,
    'distance': 2046,
    'jams': True,
    'time': 307,
    'tolls': False,
}

BUSINESS_ROUTE_JAMS = {
    'blocked': False,
    'caller_link': 'parent_link',
    'points': [
        [37.683, 55.774, 0.0, 0.0],
        [37.674, 55.772, 605.0, 90.0],
        [37.662, 55.766, 1610.0, 241.0],
        [37.656, 55.764, 2046.0, 307.0],
    ],
    'router_settings': {
        'intent': 'ROUTESTATS',
        'jams': True,
        'mode': 'approx',
        'request_id': matching.uuid_string,
        'tolls': False,
        'user_id': 'some_user_id',
    },
    'timestamp': '2019-02-01T17:00:00+03:00',
    'uuid': extend_uuid_string,
    'distance': 2046,
    'jams': True,
    'time': 307,
    'tolls': False,
}

ADDITIONAL_PRICES_ROUTE_JAMS = {
    'blocked': False,
    'caller_link': 'parent_link',
    'points': [
        [37.683, 55.774, 0.0, 0.0],
        [37.674, 55.772, 605.0, 90.0],
        [37.662, 55.766, 1610.0, 241.0],
        [37.656, 55.764, 2046.0, 307.0],
    ],
    'router_settings': {
        'intent': 'ROUTESTATS',
        'jams': True,
        'mode': 'approx',
        'request_id': matching.uuid_string,
        'tolls': False,
        'user_id': 'some_user_id',
    },
    'timestamp': '2019-02-01T17:00:00+03:00',
    'uuid': extend_uuid_string,
    'distance': 2046,
    'jams': True,
    'time': 307,
    'tolls': False,
}

ECONOM_CATEGORY_USER = {
    'alternative_prices_delta_list': {},
    'alternative_prices_meta': {},
    'base_price': [129.0, 0.0, 1.05, 0.0, 0.0, 0.0, 0.0],
    'caller_link': 'parent_link',
    'category_name': 'econom',
    'category_prices_id': 'c/ed3b2fe5c51f4a4da7bee86349259dda',
    'geoarea_ids': ['g/1f121111472a45e9bcbb7c72200c6340'],
    'is_transfer': False,
    'is_user': True,
    'price_delta_list': [],
    'price_meta': {},
    'routepart_list': [['moscow', 2046.0, 307.0, 0.0, 1.05, 0]],
    'timestamp': '2019-02-01T17:00:00+03:00',
    'use_fixed_price': True,
    'use_jams': True,
    'uuid': matching.uuid_string,
    'extra': {},
}

DECOUPLING_CATEGORY_USER = {
    'alternative_prices_delta_list': {},
    'alternative_prices_meta': {},
    'base_price': [
        49.0,
        4.0920000000000005,
        2.558333333333333,
        0.0,
        0.0,
        0.0,
        0.0,
    ],
    'caller_link': 'parent_link',
    'category_name': 'econom',
    'category_prices_id': 'd/corp_tariff_id/decoupling_category_id',
    'geoarea_ids': ['g/1f121111472a45e9bcbb7c72200c6340'],
    'is_transfer': False,
    'is_user': True,
    'price_delta_list': [],
    'price_meta': {},
    'routepart_list': [
        ['moscow', 2046.0, 307.0, 4.0920000000000005, 2.558333333333333, 0],
    ],
    'timestamp': '2019-02-01T17:00:00+03:00',
    'use_fixed_price': True,
    'use_jams': True,
    'uuid': matching.uuid_string,
    'extra': {'disable_surge': False},
}

BUSINESS_CATEGORY_USER = {
    'alternative_prices_delta_list': {},
    'alternative_prices_meta': {},
    'base_price': [199.0, 0.552, 0.0, 0.0, 0.0, 0.0, 0.0],
    'caller_link': 'parent_link',
    'category_name': 'business',
    'category_prices_id': 'c/465adfd1acb34724b7825bf6a2e663d4',
    'geoarea_ids': ['g/1f121111472a45e9bcbb7c72200c6340'],
    'is_transfer': False,
    'is_user': True,
    'price_delta_list': [],
    'price_meta': {},
    'routepart_list': [['moscow', 2046.0, 307.0, 0.552, 0.0, 0]],
    'timestamp': '2019-02-01T17:00:00+03:00',
    'use_fixed_price': False,
    'use_jams': True,
    'uuid': matching.uuid_string,
    'extra': {},
    'fixed_price_discard_reason': 'DISABLED_FOR_CATEGORY',
}

ADDITIONAL_PRICES_CATEGORY_USER = {
    'alternative_prices_delta_list': {'antisurge': []},
    'alternative_prices_meta': {'antisurge': {}},
    'antisurge_price_delta_list': [],
    'antisurge_price_meta': {},
    'base_price': [129.0, 0.0, 1.05, 0.0, 0.0, 0.0, 0.0],
    'caller_link': 'parent_link',
    'category_name': 'econom',
    'category_prices_id': 'c/ed3b2fe5c51f4a4da7bee86349259dda',
    'geoarea_ids': ['g/1f121111472a45e9bcbb7c72200c6340'],
    'is_transfer': False,
    'is_user': True,
    'price_delta_list': [],
    'price_meta': {},
    'routepart_list': [['moscow', 2046.0, 307.0, 0.0, 1.05, 0]],
    'timestamp': '2019-02-01T17:00:00+03:00',
    'use_fixed_price': True,
    'use_jams': True,
    'uuid': matching.uuid_string,
    'extra': {},
}

ECONOM_CATEGORY_DRIVER = {
    'alternative_prices_delta_list': {},
    'alternative_prices_meta': {},
    'base_price': [129.0, 0.0, 1.05, 0.0, 0.0, 0.0, 0.0],
    'caller_link': 'parent_link',
    'category_name': 'econom',
    'category_prices_id': 'c/ed3b2fe5c51f4a4da7bee86349259dda',
    'geoarea_ids': ['g/1f121111472a45e9bcbb7c72200c6340'],
    'is_transfer': False,
    'is_user': False,
    'price_delta_list': [],
    'price_meta': {},
    'routepart_list': [['moscow', 2046.0, 307.0, 0.0, 1.05, 0]],
    'timestamp': '2019-02-01T17:00:00+03:00',
    'use_fixed_price': True,
    'use_jams': True,
    'uuid': matching.uuid_string,
    'extra': {},
}

DECOUPLING_CATEGORY_DRIVER = {
    'alternative_prices_delta_list': {},
    'alternative_prices_meta': {},
    'base_price': [129.0, 0.0, 1.05, 0.0, 0.0, 0.0, 0.0],
    'caller_link': 'parent_link',
    'category_name': 'econom',
    'category_prices_id': 'c/ed3b2fe5c51f4a4da7bee86349259dda',
    'geoarea_ids': ['g/1f121111472a45e9bcbb7c72200c6340'],
    'is_transfer': False,
    'is_user': False,
    'price_delta_list': [],
    'price_meta': {},
    'routepart_list': [['moscow', 2046.0, 307.0, 0.0, 1.05, 0]],
    'timestamp': '2019-02-01T17:00:00+03:00',
    'use_fixed_price': True,
    'use_jams': True,
    'uuid': matching.uuid_string,
    'extra': {'disable_surge': False},
}

BUSINESS_CATEGORY_DRIVER = {
    'alternative_prices_delta_list': {},
    'alternative_prices_meta': {},
    'base_price': [199.0, 0.552, 0.0, 0.0, 0.0, 0.0, 0.0],
    'caller_link': 'parent_link',
    'category_name': 'business',
    'category_prices_id': 'c/465adfd1acb34724b7825bf6a2e663d4',
    'geoarea_ids': ['g/1f121111472a45e9bcbb7c72200c6340'],
    'is_transfer': False,
    'is_user': False,
    'price_delta_list': [],
    'price_meta': {},
    'routepart_list': [['moscow', 2046.0, 307.0, 0.552, 0.0, 0]],
    'timestamp': '2019-02-01T17:00:00+03:00',
    'use_fixed_price': False,
    'use_jams': True,
    'uuid': matching.uuid_string,
    'extra': {},
    'fixed_price_discard_reason': 'DISABLED_FOR_CATEGORY',
}

ADDITIONAL_PRICES_CATEGORY_DRIVER = {
    'alternative_prices_delta_list': {'antisurge': []},
    'alternative_prices_meta': {'antisurge': {}},
    'antisurge_price_delta_list': [],
    'antisurge_price_meta': {},
    'base_price': [129.0, 0.0, 1.05, 0.0, 0.0, 0.0, 0.0],
    'caller_link': 'parent_link',
    'category_name': 'econom',
    'category_prices_id': 'c/ed3b2fe5c51f4a4da7bee86349259dda',
    'geoarea_ids': ['g/1f121111472a45e9bcbb7c72200c6340'],
    'is_transfer': False,
    'is_user': False,
    'price_delta_list': [],
    'price_meta': {},
    'routepart_list': [['moscow', 2046.0, 307.0, 0.0, 1.05, 0]],
    'timestamp': '2019-02-01T17:00:00+03:00',
    'use_fixed_price': True,
    'use_jams': True,
    'uuid': matching.uuid_string,
    'extra': {},
}

BACKEND_VARIABLES_LOG_TEMPLATE = {
    'uuid': matching.uuid_string,
    'caller_link': 'parent_link',
    'prepare_link': matching.uuid_string,
    'user_id': 'some_user_id',
    'source': 'v2/prepare',
    'version': 0,
    'timestamp': '2019-02-01T17:00:00+03:00',
}

ECONOM_BACKEND_VARIABLES = {
    'category': 'econom',
    'category_data': {
        'corp_decoupling': False,
        'decoupling': False,
        'fixed_price': True,
        'min_paid_supply_price_for_paid_cancel': 0.0,
        'paid_cancel_waiting_time_limit': 600.0,
    },
    'country_code2': 'RU',
    'exps': {},
    'payment_type': 'SOME_PAYMENT_TYPE',
    'requirements': {'select': {}, 'simple': []},
    'rounding_factor': 1.0,
    'surge_params': {
        'free_drivers': 6,
        'free_drivers_chain': 0,
        'pins': 0,
        'radius': 3000.0,
        'total_drivers': 6,
        'value': 1.0,
        'value_b': 1.0,
        'value_raw': 1.0,
        'value_smooth': 1.0,
    },
    'tariff': {
        'boarding_price': 129.0,
        'minimum_price': 0.0,
        'paid_cancel_options': {
            'add_minimal_to_paid_cancel': True,
            'paid_cancel_fix': 0.0,
        },
        'requirement_prices': {
            'animaltransport': 150.0,
            'bicycle': 150.0,
            'check': 0.0,
            'childchair_moscow': 100.0,
            'conditioner': 0.0,
            'nosmoking': 0.0,
            'waiting_in_transit': 9.0,
            'yellowcarnumber': 0.0,
        },
        'requirements_included_one_of': ['some_fake_requirement'],
        'waiting_price': {'free_waiting_time': 180, 'price_per_minute': 9.0},
    },
    'user_data': {'has_cashback_plus': False, 'has_yaplus': False},
    'user_tags': [],
    'waypoints_count': 2,
    'zone': 'moscow',
}

ECONOM_BACKEND_VARIABLES_USER_DECOUPLING = {
    'category': 'econom',
    'category_data': {
        'corp_decoupling': True,
        'decoupling': True,
        'disable_paid_supply': False,
        'disable_surge': False,
        'fixed_price': True,
        'min_paid_supply_price_for_paid_cancel': 0.0,
        'paid_cancel_waiting_time_limit': 600.0,
    },
    'country_code2': 'RU',
    'exps': {},
    'payment_type': 'corp',
    'requirements': {'select': {}, 'simple': []},
    'rounding_factor': 1.0,
    'surge_params': {
        'free_drivers': 6,
        'free_drivers_chain': 0,
        'pins': 0,
        'radius': 3000.0,
        'total_drivers': 6,
        'value': 1.0,
        'value_b': 1.0,
        'value_raw': 1.0,
        'value_smooth': 1.0,
    },
    'tariff': {
        'boarding_price': 49.0,
        'minimum_price': 49.0,
        'paid_cancel_options': {
            'add_minimal_to_paid_cancel': True,
            'paid_cancel_fix': 100.0,
        },
        'requirement_multipliers': {'cargo_loaders': 1.5},
        'requirement_prices': {
            'cargo_loaders': 0.0,
            'waiting_in_transit': 12.0,
        },
        'requirements_included_one_of': ['some_fake_decoupling_requirement'],
        'waiting_price': {'free_waiting_time': 180, 'price_per_minute': 10.8},
    },
    'user_data': {'has_cashback_plus': False, 'has_yaplus': False},
    'user_tags': [],
    'waypoints_count': 2,
    'zone': 'moscow',
}

ECONOM_BACKEND_VARIABLES_DRIVER_DECOUPLING = {
    'category': 'econom',
    'category_data': {
        'corp_decoupling': True,
        'decoupling': False,
        'fixed_price': True,
        'min_paid_supply_price_for_paid_cancel': 0.0,
        'paid_cancel_waiting_time_limit': 600.0,
    },
    'country_code2': 'RU',
    'exps': {},
    'payment_type': 'corp',
    'requirements': {'select': {}, 'simple': []},
    'rounding_factor': 1.0,
    'surge_params': {
        'free_drivers': 6,
        'free_drivers_chain': 0,
        'pins': 0,
        'radius': 3000.0,
        'total_drivers': 6,
        'value': 1.0,
        'value_b': 1.0,
        'value_raw': 1.0,
        'value_smooth': 1.0,
    },
    'tariff': {
        'boarding_price': 129.0,
        'minimum_price': 0.0,
        'paid_cancel_options': {
            'add_minimal_to_paid_cancel': True,
            'paid_cancel_fix': 0.0,
        },
        'requirement_prices': {
            'animaltransport': 150.0,
            'bicycle': 150.0,
            'check': 0.0,
            'childchair_moscow': 100.0,
            'conditioner': 0.0,
            'nosmoking': 0.0,
            'waiting_in_transit': 9.0,
            'yellowcarnumber': 0.0,
        },
        'requirements_included_one_of': ['some_fake_requirement'],
        'waiting_price': {'free_waiting_time': 180, 'price_per_minute': 9.0},
    },
    'user_data': {'has_cashback_plus': False, 'has_yaplus': False},
    'user_tags': [],
    'waypoints_count': 2,
    'zone': 'moscow',
}

BUSINESS_BACKEND_VARIABLES = {
    'category': 'business',
    'category_data': {
        'corp_decoupling': False,
        'decoupling': False,
        'fixed_price': False,
        'min_paid_supply_price_for_paid_cancel': 0.0,
        'paid_cancel_waiting_time_limit': 600.0,
        'yaplus_coeff': 0.9,
    },
    'country_code2': 'RU',
    'exps': {},
    'payment_type': 'SOME_PAYMENT_TYPE',
    'requirements': {'select': {}, 'simple': []},
    'rounding_factor': 1.0,
    'surge_params': {
        'free_drivers': 6,
        'free_drivers_chain': 0,
        'pins': 0,
        'radius': 3000.0,
        'total_drivers': 6,
        'value': 1.0,
        'value_b': 1.0,
        'value_raw': 1.0,
        'value_smooth': 1.0,
    },
    'tariff': {
        'boarding_price': 199.0,
        'minimum_price': 0.0,
        'paid_cancel_options': {
            'add_minimal_to_paid_cancel': True,
            'paid_cancel_fix': 0.0,
        },
        'requirement_prices': {
            'animaltransport': 150.0,
            'bicycle': 100.0,
            'check': 0.0,
            'childchair_moscow': 100.0,
            'nosmoking': 0.0,
            'waiting_in_transit': 13.0,
            'yellowcarnumber': 0.0,
        },
        'waiting_price': {'free_waiting_time': 180, 'price_per_minute': 13.0},
    },
    'user_data': {'has_cashback_plus': False, 'has_yaplus': False},
    'user_tags': [],
    'waypoints_count': 2,
    'zone': 'moscow',
}

ECONOM_BACKEND_VARIABLES_ADDITIONAL_PRICES = {
    'category': 'econom',
    'category_data': {
        'corp_decoupling': False,
        'decoupling': False,
        'fixed_price': True,
        'min_paid_supply_price_for_paid_cancel': 0.0,
        'paid_cancel_waiting_time_limit': 600.0,
    },
    'country_code2': 'RU',
    'exps': {},
    'payment_type': 'SOME_PAYMENT_TYPE',
    'requirements': {'select': {}, 'simple': []},
    'rounding_factor': 1.0,
    'surge_params': {
        'explicit_antisurge': {'value': 0.5},
        'free_drivers': 6,
        'free_drivers_chain': 0,
        'pins': 0,
        'radius': 3000.0,
        'total_drivers': 6,
        'value': 1.0,
        'value_b': 1.0,
        'value_raw': 1.0,
        'value_smooth': 1.0,
    },
    'tariff': {
        'boarding_price': 129.0,
        'minimum_price': 0.0,
        'paid_cancel_options': {
            'add_minimal_to_paid_cancel': True,
            'paid_cancel_fix': 0.0,
        },
        'requirement_prices': {
            'animaltransport': 150.0,
            'bicycle': 150.0,
            'check': 0.0,
            'childchair_moscow': 100.0,
            'conditioner': 0.0,
            'nosmoking': 0.0,
            'waiting_in_transit': 9.0,
            'yellowcarnumber': 0.0,
        },
        'requirements_included_one_of': ['some_fake_requirement'],
        'waiting_price': {'free_waiting_time': 180, 'price_per_minute': 9.0},
    },
    'user_data': {'has_cashback_plus': False, 'has_yaplus': False},
    'user_tags': [],
    'waypoints_count': 2,
    'zone': 'moscow',
}

RESPONSE_CASES = test_utils.BooleanFlagCases(
    ['econom', 'with_decoupling', 'business', 'all_additional_prices'],
)


class BackendVariablesUuids:
    def __init__(self):
        self.uuids = {}

    def add_uuid(self, category, is_user, uuid):
        if category not in self.uuids:
            self.uuids.update({category: {}})
        if is_user:
            self.uuids[category]['user'] = uuid
        else:
            self.uuids[category]['driver'] = uuid


@pytest.fixture(name='backend_variables_uuids')
def fixture_backend_variables_uuids():
    return BackendVariablesUuids()


@pytest.mark.config(
    ROUTER_MAPS_ENABLED=True,
    PRICING_DATA_PREPARER_ROUTER_ENABLED={'__default__': True},
    PRICING_DATA_PREPARER_SURGER_ENABLED={
        '__default__': {'__default__': True},
    },
    PRICING_DATA_PREPARER_COUPONS_ENABLED=True,
    PRICING_DATA_PREPARER_DISCOUNTS_ENABLED=True,
    PRICING_PASSENGER_TAGS_ENABLED=True,
)
@pytest.mark.experiments3(filename='exp3_config.json')
@pytest.mark.now('2019-02-01T14:00:00Z')
@pytest.mark.parametrize(
    argnames=RESPONSE_CASES.get_names(),
    argvalues=RESPONSE_CASES.get_args(),
    ids=RESPONSE_CASES.get_ids(),
)
async def test_v2_prepare_yt_logger(
        taxi_pricing_data_preparer,
        mock_yamaps_router,
        mock_user_api_get_users,
        mock_user_api_get_phones,
        surger,
        mock_surger,
        mock_ride_discounts,
        mock_tags,
        mock_coupons,
        mock_decoupling_corp_tariffs,
        econom_response,
        business_response,
        decoupling_response,
        econom_with_additional_prices,
        econom,
        with_decoupling,
        business,
        all_additional_prices,
        testpoint,
        backend_variables_uuids,
):
    pre_request = utils_request.Request()

    if econom:
        common_log = ECONOM_COMMON
        route_jams_log = ECONOM_ROUTE_JAMS
        category_user_econom_log = ECONOM_CATEGORY_USER
        category_driver_econom_log = ECONOM_CATEGORY_DRIVER
        econom_backend_variables_user = ECONOM_BACKEND_VARIABLES
        econom_backend_variables_driver = ECONOM_BACKEND_VARIABLES
    elif with_decoupling:
        common_log = DECOUPLING_COMMON
        route_jams_log = DECOUIPLING_ROUTE_JAMS
        pre_request.add_decoupling_method()
        category_user_econom_log = DECOUPLING_CATEGORY_USER
        category_driver_econom_log = DECOUPLING_CATEGORY_DRIVER
        econom_backend_variables_user = (
            ECONOM_BACKEND_VARIABLES_USER_DECOUPLING
        )
        econom_backend_variables_driver = (
            ECONOM_BACKEND_VARIABLES_DRIVER_DECOUPLING
        )
    elif business:
        common_log = BUSINESS_COMMON
        route_jams_log = BUSINESS_ROUTE_JAMS
        pre_request.set_categories(['econom', 'business'])
        category_user_econom_log = ECONOM_CATEGORY_USER
        category_driver_econom_log = ECONOM_CATEGORY_DRIVER
        category_user_business_log = BUSINESS_CATEGORY_USER
        category_driver_business_log = BUSINESS_CATEGORY_DRIVER
        econom_backend_variables_user = ECONOM_BACKEND_VARIABLES
        econom_backend_variables_driver = ECONOM_BACKEND_VARIABLES
    elif all_additional_prices:
        route_jams_log = ADDITIONAL_PRICES_ROUTE_JAMS
        common_log = ADDITIONAL_PRICES_COMMON
        category_user_econom_log = ADDITIONAL_PRICES_CATEGORY_USER
        category_driver_econom_log = ADDITIONAL_PRICES_CATEGORY_DRIVER
        pre_request.set_additional_prices(
            antisurge=True,
            strikeout=True,
            combo_order=False,
            combo_inner=False,
            combo_outer=False,
        )
        surger.set_explicit_antisurge()
        econom_backend_variables_user = (
            ECONOM_BACKEND_VARIABLES_ADDITIONAL_PRICES
        )
        econom_backend_variables_driver = ECONOM_BACKEND_VARIABLES

    @testpoint('v2_prepare_common')
    def tp_v2_prepare_common(data):
        assert round_values(data) == round_values(common_log)

    @testpoint('v2_prepare_route_jams')
    def tp_v2_preparer_route_jams(data):
        assert round_values(data) == round_values(route_jams_log)

    @testpoint('v2_prepare_route_no_jams')
    def tp_v2_preparer_route_no_jams(data):
        pass

    @testpoint('v2_prepare_category_user_econom')
    def tp_v2_prepare_user_econom(data):
        assert round_values(data) == round_values(category_user_econom_log)

    @testpoint('v2_prepare_category_driver_econom')
    def tp_v2_prepare_driver_econom(data):
        assert round_values(data) == round_values(category_driver_econom_log)

    @testpoint('v2_prepare_category_user_business')
    def tp_v2_prepare_user_business(data):
        assert round_values(data) == round_values(category_user_business_log)

    @testpoint('v2_prepare_category_driver_business')
    def tp_v2_prepare_driver_business(data):
        assert round_values(data) == round_values(category_driver_business_log)

    @testpoint('backend_variables_both_econom')
    def tp_bv_both_econom(data):
        BACKEND_VARIABLES_LOG_TEMPLATE['category_name'] = 'econom'
        BACKEND_VARIABLES_LOG_TEMPLATE['subject'] = 'both'
        BACKEND_VARIABLES_LOG_TEMPLATE['data'] = econom_backend_variables_user
        assert data == BACKEND_VARIABLES_LOG_TEMPLATE
        backend_variables_uuids.add_uuid('econom', True, data['uuid'])

    @testpoint('backend_variables_user_econom')
    def tp_bv_user_econom(data):
        BACKEND_VARIABLES_LOG_TEMPLATE['category_name'] = 'econom'
        BACKEND_VARIABLES_LOG_TEMPLATE['subject'] = 'user'
        BACKEND_VARIABLES_LOG_TEMPLATE['data'] = econom_backend_variables_user
        assert data == BACKEND_VARIABLES_LOG_TEMPLATE
        backend_variables_uuids.add_uuid('econom', True, data['uuid'])

    @testpoint('backend_variables_driver_econom')
    def tp_bv_driver_econom(data):
        BACKEND_VARIABLES_LOG_TEMPLATE['category_name'] = 'econom'
        BACKEND_VARIABLES_LOG_TEMPLATE['subject'] = 'driver'
        BACKEND_VARIABLES_LOG_TEMPLATE[
            'data'
        ] = econom_backend_variables_driver
        assert data == BACKEND_VARIABLES_LOG_TEMPLATE
        backend_variables_uuids.add_uuid('econom', False, data['uuid'])

    @testpoint('backend_variables_both_business')
    def tp_bv_both_business(data):
        BACKEND_VARIABLES_LOG_TEMPLATE['category_name'] = 'business'
        BACKEND_VARIABLES_LOG_TEMPLATE['subject'] = 'both'
        BACKEND_VARIABLES_LOG_TEMPLATE['data'] = BUSINESS_BACKEND_VARIABLES
        assert data == BACKEND_VARIABLES_LOG_TEMPLATE
        backend_variables_uuids.add_uuid('business', True, data['uuid'])

    @testpoint('backend_variables_user_business')
    def tp_bv_user_business(data):
        BACKEND_VARIABLES_LOG_TEMPLATE['category_name'] = 'business'
        BACKEND_VARIABLES_LOG_TEMPLATE['subject'] = 'user'
        BACKEND_VARIABLES_LOG_TEMPLATE['data'] = BUSINESS_BACKEND_VARIABLES
        assert data == BACKEND_VARIABLES_LOG_TEMPLATE
        backend_variables_uuids.add_uuid('business', True, data['uuid'])

    @testpoint('backend_variables_driver_business')
    def tp_bv_driver_business(data):
        BACKEND_VARIABLES_LOG_TEMPLATE['category_name'] = 'business'
        BACKEND_VARIABLES_LOG_TEMPLATE['subject'] = 'driver'
        BACKEND_VARIABLES_LOG_TEMPLATE['data'] = BUSINESS_BACKEND_VARIABLES
        assert data == BACKEND_VARIABLES_LOG_TEMPLATE
        backend_variables_uuids.add_uuid('business', False, data['uuid'])

    request = pre_request.get()
    response = await taxi_pricing_data_preparer.post(
        'v2/prepare', json=request, headers={'X-YaRequestId': 'parent_link'},
    )
    assert response.status_code == 200
    resp = response.json()

    assert tp_v2_prepare_common.times_called == 1
    assert tp_v2_preparer_route_jams.times_called == 1
    assert tp_v2_preparer_route_no_jams.times_called == 0
    assert tp_v2_prepare_user_econom.times_called == 1
    assert tp_v2_prepare_driver_econom.times_called == 1
    assert tp_v2_prepare_user_business.times_called == (1 if business else 0)
    assert tp_v2_prepare_driver_business.times_called == (1 if business else 0)
    if econom:
        assert tp_bv_user_econom.times_called == 0
        assert tp_bv_driver_econom.times_called == 0
        assert tp_bv_both_econom.times_called == 1

        assert (
            'econom' in backend_variables_uuids.uuids
            and 'business' not in backend_variables_uuids.uuids
        )
        assert (
            backend_variables_uuids.uuids['econom']
            == resp['categories']['econom']['backend_variables_uuids']
        )
    elif with_decoupling:
        assert tp_bv_user_econom.times_called == 1
        assert tp_bv_driver_econom.times_called == 1
        assert tp_bv_both_econom.times_called == 0
        assert (
            'econom' in backend_variables_uuids.uuids
            and 'business' not in backend_variables_uuids.uuids
        )
        assert (
            backend_variables_uuids.uuids['econom']
            == resp['categories']['econom']['backend_variables_uuids']
        )
    elif business:
        assert tp_bv_user_econom.times_called == 0
        assert tp_bv_driver_econom.times_called == 0
        assert tp_bv_both_econom.times_called == 1
        assert tp_bv_user_business.times_called == 0
        assert tp_bv_driver_business.times_called == 0
        assert tp_bv_both_business.times_called == 1
        assert (
            'econom' in backend_variables_uuids.uuids
            and 'business' in backend_variables_uuids.uuids
        )
        assert (
            backend_variables_uuids.uuids['econom']
            == resp['categories']['econom']['backend_variables_uuids']
        )
        assert (
            backend_variables_uuids.uuids['business']
            == resp['categories']['business']['backend_variables_uuids']
        )
    elif all_additional_prices:
        assert tp_bv_user_econom.times_called == 0
        assert tp_bv_driver_econom.times_called == 0
        assert tp_bv_both_econom.times_called == 1
        assert (
            'econom' in backend_variables_uuids.uuids
            and 'business' not in backend_variables_uuids.uuids
        )
        assert (
            backend_variables_uuids.uuids['econom']
            == resp['categories']['econom']['backend_variables_uuids']
        )


PAID_SUPPLY_USER = {
    'caller_link': 'parent_link',
    'category_name': 'econom',
    'category_prices_id': 'c/00000000000000000000000000000001',
    'is_user': True,
    'price_delta_list': [],
    'price_meta': {},
    'timestamp': '2019-02-01T17:00:00+03:00',
    'uuid': '',
}

PAID_SUPPLY_DRIVER = {
    'caller_link': 'parent_link',
    'category_name': 'econom',
    'category_prices_id': 'c/00000000000000000000000000000001',
    'is_user': False,
    'price_delta_list': [],
    'price_meta': {},
    'timestamp': '2019-02-01T17:00:00+03:00',
    'uuid': '',
}


@pytest.mark.now('2019-02-01T14:00:00Z')
@pytest.mark.experiments3(filename='exp3_config_paid_supply_min_price.json')
async def test_v2_calc_paid_supply_yt_logger(
        taxi_pricing_data_preparer, taxi_config, testpoint,
):
    point_a = [37.683, 55.774]
    driver_route_info = {'distance': 5000.0, 'time': 1000.0}
    cfg_paid_supply_free_route = {'DISTANCE': 15000.0, 'TIME': 1200.0}

    taxi_config.set(
        PAID_SUPPLY_FREE_DISTANCE_TIME={
            '__default__': {'__default__': cfg_paid_supply_free_route},
        },
    )

    @testpoint('v2_paid_supply_user')
    def tp_v2_paid_supply_user(data):
        data['uuid'] = ''
        assert data == PAID_SUPPLY_USER

    @testpoint('v2_paid_supply_driver')
    def tp_v2_paid_supply_driver(data):
        data['uuid'] = ''
        assert data == PAID_SUPPLY_DRIVER

    response = await taxi_pricing_data_preparer.post(
        'v2/calc_paid_supply',
        headers={'X-YaRequestId': 'parent_link'},
        json={
            'modifications_scope': 'taxi',
            'point': point_a,
            'zone': 'moscow',
            'categories': {
                'econom': {
                    'driver_route_info': driver_route_info,
                    'prepared': {
                        'tariff_info': {
                            'time': {
                                'included_minutes': 1,
                                'price_per_minute': 2,
                            },
                            'distance': {
                                'included_kilometers': 3,
                                'price_per_kilometer': 4,
                            },
                            'point_a_free_waiting_time': 5,
                            'max_free_waiting_time': 6,
                        },
                        'corp_decoupling': False,
                        'fixed_price': True,
                        'geoarea_ids': ['g/1f121111472a45e9bcbb7c72200c6340'],
                        'currency': {
                            'fraction_digits': 0,
                            'name': 'RUB',
                            'symbol': '₽',
                        },
                        'driver': {
                            'modifications': {
                                'for_fixed': [77, 88, 99],
                                'for_taximeter': [77, 88],
                            },
                            'price': {'total': 1060.0},
                            'meta': {},
                            'trip_information': {
                                'distance': 100500,
                                'has_toll_roads': False,
                                'jams': True,
                                'time': 307.0,
                            },
                            'tariff_id': 'aaaaaaaaaaaaaaaaaaaaaaaa',
                            'category_id': '00000000000000000000000000000001',
                            'base_price': {
                                'boarding': 100.0,
                                'distance': 400.0,
                                'time': 500.0,
                                'waiting': 10.0,
                                'requirements': 0.0,
                                'transit_waiting': 50.0,
                                'destination_waiting': 0.0,
                            },
                            'category_prices_id': (
                                'c/00000000000000000000000000000001'
                            ),
                            'additional_prices': {},
                        },
                        'user': {
                            'modifications': {
                                'for_fixed': [55, 44, 33],
                                'for_taximeter': [55, 33],
                            },
                            'price': {'total': 830.0, 'strikeout': 830.0},
                            'meta': {},
                            'trip_information': {
                                'distance': 100500,
                                'has_toll_roads': False,
                                'jams': True,
                                'time': 307.0,
                            },
                            'tariff_id': 'aaaaaaaaaaaaaaaaaaaaaaaa',
                            'category_id': '00000000000000000000000000000001',
                            'base_price': {
                                'boarding': 70.0,
                                'distance': 300.0,
                                'time': 400.0,
                                'waiting': 10.0,
                                'requirements': 0.0,
                                'transit_waiting': 50.0,
                                'destination_waiting': 0.0,
                            },
                            'category_prices_id': (
                                'c/00000000000000000000000000000001'
                            ),
                            'additional_prices': {},
                            'data': {
                                'country_code2': 'RU',
                                'zone': 'moscow',
                                'category': 'econom',
                                'rounding_factor': 1.0,
                                'user_tags': [],
                                'surge_params': {
                                    'value': 1.0,
                                    'value_smooth': 1.0,
                                    'value_raw': 1.0,
                                },
                                'requirements': {'simple': [], 'select': {}},
                                'tariff': {
                                    'boarding_price': 0.0,
                                    'minimum_price': 0.0,
                                    'waiting_price': {
                                        'free_waiting_time': 0,
                                        'price_per_minute': 0.0,
                                    },
                                    'requirement_prices': {},
                                },
                                'user_data': {
                                    'has_yaplus': False,
                                    'has_cashback_plus': False,
                                },
                                'category_data': {
                                    'fixed_price': False,
                                    'decoupling': False,
                                    'paid_cancel_waiting_time_limit': 600.0,
                                    'min_paid_supply_price_for_paid_cancel': (
                                        0.0
                                    ),
                                },
                                'exps': {},
                            },
                        },
                    },
                },
            },
        },
    )

    assert response.status_code == 200

    assert tp_v2_paid_supply_user.times_called == 1
    assert tp_v2_paid_supply_driver.times_called == 1


BV_PATCH_REQUEST = {
    'order_id': 'fix_price_order_decoupling',
    'reason': 'user_increase_price',
    'new_value': {'variable_id': 'extra_price', 'extra_price_value': 42.42},
}


@pytest.mark.now('2022-03-18T15:00:00Z')
@pytest.mark.pgsql('pricing_data_preparer', files=['rules.sql'])
async def test_v1_backend_variables_patch_logger(
        taxi_pricing_data_preparer, testpoint, order_core, mock_order_core,
):
    previous_uuids = {'user': None, 'driver': None}

    def common_asserts(data, subject):
        assert data['subject'] == subject
        assert data['category_name'] == 'econom'
        assert data['uuid'] == matching.uuid_string
        assert data['previous_uuid'] == matching.uuid_string

        previous_uuids[subject] = data['previous_uuid']

    @testpoint('backend_variables_user_econom')
    def tp_bv_user_econom(data):
        common_asserts(data, 'user')

    @testpoint('backend_variables_driver_econom')
    def tp_bv_driver_econom(data):
        common_asserts(data, 'driver')

    order_core.set_expected_update_fields(
        {'order.pricing_data.user.data.extra_price': 42.42},
    )

    result = await taxi_pricing_data_preparer.patch(
        '/internal/v1/backend_variables/', json=BV_PATCH_REQUEST,
    )

    assert result.status_code == 200
    assert mock_order_core.get_fields.times_called == 1

    assert tp_bv_user_econom.times_called == 1
    assert tp_bv_driver_econom.times_called == 1

    result = await taxi_pricing_data_preparer.patch(
        '/internal/v1/backend_variables/', json=BV_PATCH_REQUEST,
    )
    assert result.status_code == 200
    assert mock_order_core.get_fields.times_called == 2

    assert tp_bv_user_econom.times_called == 2
    assert tp_bv_driver_econom.times_called == 2
