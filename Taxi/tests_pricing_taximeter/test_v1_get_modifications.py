# pylint: disable=too-many-lines, redefined-outer-name, import-only-modules
# flake8: noqa F401
import copy

import bson
import pytest

from tests_plugins import json_util

from tests_pricing_taximeter.plugins.mock_order_core import mock_order_core
from tests_pricing_taximeter.plugins.mock_order_core import order_core
from tests_pricing_taximeter.plugins.mock_order_core import OrderIdRequestType

AUTH = {
    'park_id': 'park_id_000',
    'session': 'session_000',
    'uuid': 'driverid000',
}

USER_AGENT = 'Taximeter-DEV 9.21 (2147483647)'

DEFAULT_HEADERS = {
    'X-Driver-Session': AUTH['session'],
    'User-Agent': USER_AGENT,
    'Accept-Language': 'en-EN',
}


@pytest.fixture(name='contractor_orders_multioffer', autouse=True)
def _mock_multioffer(mockserver):
    @mockserver.json_handler(
        '/contractor-orders-multioffer/'
        'internal/v1/multioffer/state_for_pricing',
    )
    def state_for_pricing(request):
        if (
                request.json['multioffer_id']
                == '01234567-89ab-cdef-0123-456789abcdef'
        ):
            return {
                'order_id': '9b0ef3c5398b3e07b59f03110563479d',
                'paid_supply': False,
            }
        return mockserver.make_response(status=404, json={})

    return state_for_pricing


@pytest.mark.parametrize(
    'params, expected_code, expected_error, expected_bv_opt_parse',
    [
        ({'order_id': 'non-exist-order'}, 404, 'ORDER_NOT_FOUND', False),
        (
            {'order_id': 'cf0ae5ed549457a081fe9dd0c4bb6fcb'},
            404,
            'PRICING_DATA_NOT_FOUND',
            False,
        ),
        ({'order_id': 'd78fdfe188ee39cbbdeb74235430fb40'}, 200, None, False),
        ({'order_id': 'good_but_no_surge_value_in_bv'}, 200, None, True),
        ({'order_id': 'good_but_empty_bv_for_driver'}, 200, None, True),
        (
            {'multioffer_id': '01234567-89ab-cdef-0123-456789abcdef'},
            200,
            None,
            False,
        ),
        (
            {'multioffer_id': '88888888-89ab-cdef-0123-456789abcdef'},
            404,
            'ORDER_NOT_FOUND',
            False,
        ),
    ],
    ids=[
        'no_order',
        'no_pricing_data',
        'good',
        'good_but_no_surge_value_in_bv',
        'good_but_empty_bv_for_driver',
        'multioffer_good',
        'multioffer_404',
    ],
)
@pytest.mark.pgsql('pricing_data_preparer', files=['rules.sql'])
@pytest.mark.config(
    PRICING_DATA_PREPARER_METADATA_MAPPING={
        'dummy': {'taximeter': True, 'backend': True},
    },
)
async def test_v1_get_modifications_found_order(
        taxi_pricing_taximeter,
        driver_authorizer,
        contractor_orders_multioffer,
        params,
        expected_code,
        expected_error,
        expected_bv_opt_parse,
        order_core,
        mock_order_core,
        testpoint,
):
    driver_authorizer.set_session(
        AUTH['park_id'], AUTH['session'], AUTH['uuid'],
    )

    @testpoint('backend_variables_optional_parse')
    def bv_optional_parse(data):
        assert data == expected_bv_opt_parse

    response = await taxi_pricing_taximeter.post(
        'v1/get_modifications',
        json=params,
        headers=DEFAULT_HEADERS,
        params={'park_id': AUTH['park_id']},
    )
    assert response.status_code == expected_code

    resp = response.json()
    if expected_code == 200:
        assert 'driver' in resp
        assert 'user' in resp
        assert 'metadata_mapping' in resp
        assert 'taximeter_metadata' in resp
        assert bv_optional_parse.times_called == 1
    else:
        assert 'code' in resp and resp['code'] == expected_error
        assert bv_optional_parse.times_called == 0


@pytest.mark.pgsql('pricing_data_preparer', files=['rules.sql'])
@pytest.mark.now('2019-02-01T14:00:00Z')
@pytest.mark.config(FIXED_PRICE_ADDITIONAL_DISTANCE_FOR_AIRPORT=42)
@pytest.mark.parametrize(
    'order_id, experiment_fixed_price_discard_enabled, experiment_max_distance_from_b,'
    ' expected_max_distance_from_b, alternative_type',
    [
        ('d78fdfe188ee39cbbdeb74235430fb40', True, False, 123, None),
        pytest.param(
            'd78fdfe188ee39cbbdeb74235430fb40',
            False,
            False,
            500,
            None,
            marks=pytest.mark.filldb(tariff_settings='other'),
        ),
        ('order_to_airport', True, False, 123 + 42, None),
        ('d78fdfe188ee39cbbdeb74235430fb40', True, False, None, 'combo_inner'),
        ('d78fdfe188ee39cbbdeb74235430fb40', True, False, None, 'combo_outer'),
        (
            'd78fdfe188ee39cbbdeb74235430fb40',
            True,
            False,
            123,
            'explicit_antisurge',
        ),
        ('d78fdfe188ee39cbbdeb74235430fb40', True, True, 500, None),
        ('order_to_airport', True, True, 500 + 50, None),
    ],
    ids=[
        'price_from_exp_distance_from_tariff',
        'no_price, distance_from_config',
        'airport_order',
        'combo_inner',
        'combo_outer',
        'explicit_antisurge',
        'exp_max_distance_from_b',
        'exp_max_distance_from_b_airport',
    ],
)
async def test_v1_get_modifications_discard_fix_params(
        taxi_pricing_taximeter,
        driver_authorizer,
        experiments3,
        experiment_fixed_price_discard_enabled,
        experiment_max_distance_from_b,
        expected_max_distance_from_b,
        order_id,
        alternative_type,
        load_json,
        mongodb,
        order_core,
        mock_order_core,
):
    if alternative_type:
        mongodb.order_proc.update_one(
            {'_id': '9b0ef3c5398b3e07b59f03110563479d'},
            {'$set': {'order.calc.alternative_type': alternative_type}},
        )

    driver_authorizer.set_session(
        AUTH['park_id'], AUTH['session'], AUTH['uuid'],
    )
    if experiment_fixed_price_discard_enabled:
        experiments3.add_experiments_json(
            load_json('exp3_discard_fixed_price.json'),
        )

    if experiment_max_distance_from_b:
        experiments3.add_experiments_json(
            load_json('exp3_max_distance_fom_b.json'),
        )

    response = await taxi_pricing_taximeter.post(
        'v1/get_modifications',
        json={'order_id': order_id},
        headers=DEFAULT_HEADERS,
        params={'park_id': AUTH['park_id']},
    )
    assert response.status_code == 200

    resp = response.json()
    taximeter_metadata = resp['taximeter_metadata']

    assert 'fixed_price_discard_parameters' in taximeter_metadata
    fix_discard_params = taximeter_metadata['fixed_price_discard_parameters']

    if experiment_fixed_price_discard_enabled:
        assert fix_discard_params['taximeter_price_diff_config'] == {
            'max_calc_price_for_discard': 100.0,
            'min_percentage_difference_for_discard': 25.0,
        }
    else:
        assert 'taximeter_price_diff_config' not in fix_discard_params

    if expected_max_distance_from_b:
        assert (
            fix_discard_params['max_distance_from_point_b']
            == expected_max_distance_from_b
        )
    else:
        assert 'max_distance_from_point_b' not in fix_discard_params


class LoggerMessage:
    def __init__(self):
        self.message = ''

    def set_message(self, message):
        self.message = message


@pytest.fixture(name='logger_message')
def fixture_logger_message():
    return LoggerMessage()


@pytest.mark.parametrize(
    'alias_order_id, expected_driver, expected_user, log, order_id',
    [
        (
            'd78fdfe188ee39cbbdeb74235430fb40',
            {
                'for_taximeter': (
                    'EUBFAAAAAAAAgwAAEgETIxQAIhIBEy'
                    'MUASISARMjFAIiEgETIxQDIhIBEyMU'
                    'BCISARMjFAUiEgETIxQGIoE='
                ),
            },
            {
                'for_taximeter': (
                    'EUBFAAAAAAAAgwAAEgETIxQAIhIBEy'
                    'MUASISARMjFAIiEgETIxQDIhIBEyMU'
                    'BCISARMjFAUiEgETIxQGIoE='
                ),
            },
            {
                'driver': {'for_taximeter': '84b'},
                'user': {'for_taximeter': '84b'},
                'taximeter_metadata': {
                    'details': [],
                    'fixed_price_discard_parameters': {
                        'max_distance_from_point_b': 123,
                    },
                    'currency': {
                        'symbol': '₽',
                        'fraction_digits': 0,
                        'rounding': 1.0,
                    },
                    'charter_contract': False,
                    'services': {
                        'waiting': {
                            'taximeter': {'free_time': 180},
                            'fixed': {'free_time': 180},
                        },
                        'waiting_in_transit': {},
                    },
                },
                'metadata_mapping': {'dummy': 0},
            },
            '9b0ef3c5398b3e07b59f03110563479d',
        ),
        (
            'd78fdfe188ee39cbbdeb74235430fb41',
            {
                'for_taximeter': 'FAAUARQCFAMUBBQFFAaB',
                'for_fixed': {'modifications': 'FAAUARQCFAMUBBQFFAaB'},
            },
            {
                'for_taximeter': 'FAAUARQCFAMUBBQFFAaB',
                'for_fixed': {'modifications': 'FAAUARQCFAMUBBQFFAaB'},
            },
            {
                'driver': {
                    'for_taximeter': '20b',
                    'for_fixed': {'modifications': '20b'},
                },
                'user': {
                    'for_taximeter': '20b',
                    'for_fixed': {'modifications': '20b'},
                },
                'taximeter_metadata': {
                    'details': [],
                    'fixed_price_discard_parameters': {
                        'max_distance_from_point_b': 123,
                    },
                    'currency': {
                        'symbol': '₽',
                        'fraction_digits': 0,
                        'rounding': 1.0,
                    },
                    'charter_contract': True,
                    'services': {
                        'waiting': {
                            'taximeter': {'free_time': 180},
                            'fixed': {'free_time': 180},
                        },
                        'waiting_in_transit': {},
                    },
                },
                'metadata_mapping': {'dummy': 0},
            },
            '9b0ef3c5398b3e07b59f031105634799',
        ),
        (
            'd78fdfe188ee39cbbdeb74235430f777',
            {
                'for_taximeter': 'FAAUARQCFAMUBBQFFAaB',
                'for_fixed': {'modifications': 'FAAUARQCFAMUBBQFFAaB'},
            },
            {
                'for_taximeter': 'FAAUARQCFAMUBBQFFAaB',
                'for_fixed': {'modifications': 'FAAUARQCFAMUBBQFFAaB'},
            },
            {
                'driver': {
                    'for_taximeter': '20b',
                    'for_fixed': {'modifications': '20b'},
                },
                'user': {
                    'for_taximeter': '20b',
                    'for_fixed': {'modifications': '20b'},
                },
                'taximeter_metadata': {
                    'details': [],
                    'fixed_price_discard_parameters': {
                        'max_distance_from_point_b': 123,
                    },
                    'currency': {
                        'symbol': '₽',
                        'fraction_digits': 0,
                        'rounding': 1.0,
                    },
                    'charter_contract': True,
                    'services': {
                        'waiting': {
                            'taximeter': {'free_time': 180},
                            'fixed': {'free_time': 180},
                        },
                        'waiting_in_transit': {},
                    },
                },
                'metadata_mapping': {'dummy': 0},
            },
            '9b0ef3c5398b3e07b59f031105634777',
        ),
        (
            'd78fdfe188ee39cbbdeb74235430f666',
            {
                'for_taximeter': (
                    'FAAUARQCFAMUBBQFFAaBEUBFAAAAAAAAgwAAEg'
                    'ETIxQAIhIBEyMUASISARMjFAIiEgETIxQDIhIB'
                    'EyMUBCISARMjFAUiEgETIxQGIoE='
                ),
                'for_fixed': {
                    'modifications': (
                        'FAAUARQCFAMUBBQFFAaBFAAUARQCFAMUBBQFFAaB'
                    ),
                },
            },
            {
                'for_taximeter': (
                    'FAAUARQCFAMUBBQFFAaBEUBFAAAAAAAAgwAAE'
                    'gETIxQAIhIBEyMUASISARMjFAIiEgETIxQDIh'
                    'IBEyMUBCISARMjFAUiEgETIxQGIoE='
                ),
                'for_fixed': {
                    'modifications': (
                        'FAAUARQCFAMUBBQFFAaBFAAUARQCFAMUBBQFFAaB'
                    ),
                },
            },
            {
                'driver': {
                    'for_taximeter': '104b',
                    'for_fixed': {'modifications': '40b'},
                },
                'user': {
                    'for_taximeter': '104b',
                    'for_fixed': {'modifications': '40b'},
                },
                'taximeter_metadata': {
                    'details': [],
                    'fixed_price_discard_parameters': {
                        'max_distance_from_point_b': 123,
                    },
                    'currency': {
                        'symbol': '₽',
                        'fraction_digits': 0,
                        'rounding': 1.0,
                    },
                    'charter_contract': True,
                    'services': {
                        'waiting': {
                            'taximeter': {'free_time': 180},
                            'fixed': {'free_time': 180},
                        },
                        'waiting_in_transit': {},
                    },
                },
                'metadata_mapping': {'dummy': 0},
            },
            '9b0ef3c5398b3e07b59f031105634766',
        ),
    ],
    ids=['no_fixed', 'fixed', 'no_paid_supply', 'paid_supply'],
)
@pytest.mark.pgsql('pricing_data_preparer', files=['rules.sql'])
@pytest.mark.config(
    PRICING_DATA_PREPARER_METADATA_MAPPING={
        'dummy': {'taximeter': True, 'backend': True},
    },
)
async def test_v1_get_modifications(
        taxi_pricing_taximeter,
        driver_authorizer,
        load_json,
        order_id,
        expected_driver,
        expected_user,
        alias_order_id,
        testpoint,
        log,
        logger_message,
        taxi_config,
        order_core,
        mock_order_core,
):
    if alias_order_id == 'd78fdfe188ee39cbbdeb74235430fb40':
        taxi_config.set_values(
            {'EULAS_FREIGHTAGE_DRIVER_TAGS': ['non-lightbox']},
        )
    else:
        taxi_config.set_values({'EULAS_FREIGHTAGE_DRIVER_TAGS': ['lightbox']})
    driver_authorizer.set_session(
        AUTH['park_id'], AUTH['session'], AUTH['uuid'],
    )

    @testpoint('v1_get_modifications_response_log')
    def v1_get_modifications_resp_log(data):
        assert data == log

    @testpoint('yt_logger_message')
    def set_logger_message(data):
        logger_message.set_message(data)

    response = await taxi_pricing_taximeter.post(
        'v1/get_modifications',
        json={'order_id': alias_order_id},
        headers=DEFAULT_HEADERS,
        params={'park_id': AUTH['park_id']},
    )
    assert response.status_code == 200

    variables = {
        'driver': expected_driver,
        'user': expected_user,
        'meta': {'dummy': 0},
    }
    expected_response = load_json(
        'response.json', object_hook=json_util.VarHook(variables),
    )
    expected_response['taximeter_metadata']['charter_contract'] = bool(
        alias_order_id != 'd78fdfe188ee39cbbdeb74235430fb40',
    )
    resp = response.json()
    assert resp == expected_response
    assert v1_get_modifications_resp_log.times_called == 1

    # checking yt-logger message
    assert set_logger_message.times_called == 1
    message = logger_message.message
    assert 'order_id' in message
    assert message['order_id'] == order_id
    assert 'driver_uuid' in message
    assert 'price_calc_version' in message
    assert message['price_calc_version'] == ''
    if 'for_fixed' in resp['driver']:
        assert 'driver_modifications_fixed' in message
        assert (
            message['driver_modifications_fixed']
            == resp['driver']['for_fixed']['modifications']
        )
    else:
        assert 'driver_modifications_fixed' not in message
    assert 'driver_modifications_taximeter' in message
    assert (
        message['driver_modifications_taximeter']
        == resp['driver']['for_taximeter']
    )
    if 'for_fixed' in resp['user']:
        assert 'user_modifications_fixed' in message
        assert (
            message['user_modifications_fixed']
            == resp['user']['for_fixed']['modifications']
        )
    else:
        assert 'user_modifications_fixed' not in message
    assert 'user_modifications_taximeter' in message
    assert (
        message['user_modifications_taximeter']
        == resp['user']['for_taximeter']
    )
    assert 'metadata_mapping' in message
    assert message['metadata_mapping'] == resp['metadata_mapping']
    assert 'taximeter_metadata' in message
    assert message['taximeter_metadata'] == resp['taximeter_metadata']


@pytest.mark.parametrize(
    'driver_park_id, expected_driver, expected_user',
    [
        (
            'park_id_000',
            {'for_taximeter': 'FAAUARQCFAMUBBQFFAaB'},
            {'for_taximeter': 'FAAUARQCFAMUBBQFFAaB'},
        ),
        (
            'park_id_777',
            {
                'for_taximeter': (
                    'FAARP+AAAAAAAAAiFAERP+mZmZmZmZoi'
                    'FAIRP/AAAAAAAAAiFAMUBBQFFAaB'
                ),
            },
            {
                'for_taximeter': (
                    'FAARP+AAAAAAAAAiFAERP+mZmZmZmZoi'
                    'FAIRP/AAAAAAAAAiFAMUBBQFFAaB'
                ),
            },
        ),
    ],
    ids=['park_id_not_matches_exp', 'park_id_matches_exp'],
)
@pytest.mark.pgsql('pricing_data_preparer', files=['rules.sql'])
@pytest.mark.experiments3(filename='exp3_base_price_discount.json')
@pytest.mark.config(
    PRICING_DATA_PREPARER_METADATA_MAPPING={
        'dummy': {'taximeter': True, 'backend': True},
    },
)
async def test_v1_get_modifications_base_price_discount(
        taxi_pricing_taximeter,
        driver_authorizer,
        load_json,
        driver_park_id,
        expected_driver,
        expected_user,
        order_core,
        mock_order_core,
):
    driver_authorizer.set_session(
        driver_park_id, AUTH['session'], AUTH['uuid'],
    )

    response = await taxi_pricing_taximeter.post(
        'v1/get_modifications',
        json={'order_id': '00000fe188ee39cbbdeb74235400000'},
        headers=DEFAULT_HEADERS,
        params={'park_id': driver_park_id},
    )
    assert response.status_code == 200

    variables = {
        'driver': expected_driver,
        'user': expected_user,
        'meta': {'dummy': 0},
    }
    expected_response = load_json(
        'response.json', object_hook=json_util.VarHook(variables),
    )
    assert response.json() == expected_response


@pytest.mark.parametrize(
    'order_id, expected_manual_price',
    [
        ('alias_id_no_manual_price', None),
        (
            'alias_id_manual_price_input_keyboard',
            {'input': {'mode': 'keyboard'}},
        ),
        ('alias_id_disable_manual_price_input_buttons_not_enough_metas', None),
        (
            'alias_id_manual_price_input_buttons',
            {
                'input': {
                    'mode': 'buttons',
                    'calc': 'user',
                    'meta_ids_keys': {'start', 'min', 'max'},
                    'meta_names_keys': {'start', 'min', 'max'},
                    'step': 0.1,
                },
            },
        ),
        ('alias_id_disable_manual_price_prices_differ', None),
        ('alias_id_disable_manual_price_decoupling', None),
    ],
)
@pytest.mark.experiments3(filename='exp3_manual_price_settings.json')
async def test_v1_get_modifications_manual_price(
        taxi_pricing_taximeter,
        driver_authorizer,
        order_id,
        expected_manual_price,
        order_core,
        mock_order_core,
):
    driver_authorizer.set_session(
        AUTH['park_id'], AUTH['session'], AUTH['uuid'],
    )

    response = await taxi_pricing_taximeter.post(
        'v1/get_modifications',
        json={'order_id': order_id},
        headers=DEFAULT_HEADERS,
        params={'park_id': AUTH['park_id']},
    )
    assert response.status_code == 200

    data = response.json()
    if expected_manual_price is not None:
        assert 'manual_price' in data['taximeter_metadata']
        manual_price = data['taximeter_metadata']['manual_price']

        # metas are unordered, removing ids to compare only keys
        if (
                'input' in manual_price
                and 'meta_ids' in manual_price['input']
                and 'meta_names' in manual_price['input']
        ):
            manual_price['input']['meta_ids_keys'] = manual_price['input'][
                'meta_ids'
            ].keys()
            del manual_price['input']['meta_ids']
            manual_price['input']['meta_names_keys'] = manual_price['input'][
                'meta_names'
            ].keys()
            del manual_price['input']['meta_names']

        assert manual_price == expected_manual_price
    else:
        assert 'manual_price' not in data['taximeter_metadata']


@pytest.mark.filldb(order_proc='expired_tariff')
@pytest.mark.pgsql('pricing_data_preparer', files=['rules.sql'])
@pytest.mark.config(
    PRICING_DATA_PREPARER_METADATA_MAPPING={
        'dummy': {'taximeter': True, 'backend': True},
    },
)
async def test_v1_get_modifications_expired_tariff(
        taxi_pricing_taximeter, driver_authorizer, order_core, mock_order_core,
):
    driver_authorizer.set_session(
        AUTH['park_id'], AUTH['session'], AUTH['uuid'],
    )

    response = await taxi_pricing_taximeter.post(
        'v1/get_modifications',
        json={'order_id': 'd78fdfe188ee39cbbdeb74235430fb40'},
        headers=DEFAULT_HEADERS,
        params={'park_id': AUTH['park_id']},
    )
    assert response.status_code == 200


@pytest.mark.parametrize(
    'override_l10n_config, localize_additional',
    [
        (None, False),
        (
            {
                'additional_foo': {
                    'keyset': 'taximeter_driver_messages',
                    'tanker_key': 'from_driver_messages',
                },
            },
            True,
        ),
    ],
    ids=['no-overrides', 'additional_from_driver_messages'],
)
@pytest.mark.parametrize('locale', ['en', 'ru'], ids=['en', 'ru'])
@pytest.mark.parametrize(
    'use_handler_consumer',
    [False, True],
    ids=['__default__', 'v1/get_modification'],
)
@pytest.mark.pgsql('pricing_data_preparer', files=['rules.sql'])
@pytest.mark.config(
    PRICING_DATA_PREPARER_METADATA_MAPPING={
        '__default__': {'taximeter': False, 'backend': True},
        'dummy': {'taximeter': True, 'backend': True},
    },
)
async def test_taximeter_metadata_details(
        taxi_pricing_taximeter,
        driver_authorizer,
        taxi_config,
        load_json,
        override_l10n_config,
        localize_additional,
        locale,
        use_handler_consumer,
        order_core,
        mock_order_core,
):
    driver_authorizer.set_session(
        AUTH['park_id'], AUTH['session'], AUTH['uuid'],
    )

    if override_l10n_config:
        taxi_config.set(
            PRICING_DATA_PREPARER_OVERRIDE_L10N=override_l10n_config,
        )

    details_config = {
        'requirements': {
            'patterns': [r'req:(\w+):(count|included|per_unit|price)'],
            'tanker': {'keyset': 'tariff', 'key_prefix': 'service_name.'},
        },
        'services': {
            'patterns': ['additional_foo'],
            'tanker': {'keyset': 'tariff'},
        },
    }

    if use_handler_consumer:
        taxi_config.set(
            PRICING_DATA_PREPARER_DETAILING_BY_CONSUMERS={
                '__default__': {},
                'v1/get_modifications': details_config,
            },
        )
    else:
        taxi_config.set(
            PRICING_DATA_PREPARER_DETAILING_BY_CONSUMERS={
                '__default__': details_config,
            },
        )

    headers = copy.deepcopy(DEFAULT_HEADERS)
    headers['Accept-Language'] = locale

    response = await taxi_pricing_taximeter.post(
        'v1/get_modifications',
        json={'order_id': 'd78fdfe188ee39cbbdeb74235430fb40'},
        headers=headers,
        params={'park_id': AUTH['park_id']},
    )
    assert response.status_code == 200

    response_json = response.json()

    assert 'metadata_mapping' in response_json
    actual_metadata_mapping = response_json['metadata_mapping']

    expected_metadata_mapping = {
        # only set by config PRICING_DATA_PREPARER_METADATA_MAPPING
        'dummy': True,
    }

    def normalize_metadata_mapping(metadata):
        for key, _ in metadata.items():
            metadata[key] = True
        return sorted(metadata)

    assert normalize_metadata_mapping(
        actual_metadata_mapping,
    ) == normalize_metadata_mapping(expected_metadata_mapping)

    assert 'taximeter_metadata' in response_json
    assert 'details' in response_json['taximeter_metadata']
    actual_details = response_json['taximeter_metadata']['details']

    def make_details_item(name, text, price, count=None, included=None):
        meta_ids = {'price': True}
        if count:
            meta_ids['count'] = True
        if included:
            meta_ids['included'] = True
        return {
            'name': name,
            'text': text,
            'meta_ids': meta_ids,
            'meta_names': meta_ids,
        }

    def make_l10n(name, locale):
        return 'text for `{}` {}'.format(name, locale.upper())

    # emitted requirements (from order_proc)
    expected_details = [
        make_details_item(
            'foo',
            make_l10n('foo', locale),
            price=True,
            count=True,
            included=True,
        ),
        make_details_item(
            'foo_bar', make_l10n('foo_bar', locale), price=True, count=True,
        ),
        make_details_item(
            'foo_bar_baz', make_l10n('foo_bar_baz', locale), price=True,
        ),
    ]
    # additional requires override localization
    if localize_additional:
        expected_details.append(
            make_details_item(
                'additional_foo',
                make_l10n('from_driver_messages', locale),
                price=True,
            ),
        )

    def normalize_details(details):
        for item in details:
            item['meta_ids'] = normalize_metadata_mapping(item['meta_ids'])
            item['meta_names'] = normalize_metadata_mapping(item['meta_names'])
        return sorted(details, key=lambda item: item['name'])

    assert normalize_details(actual_details) == normalize_details(
        expected_details,
    )


@pytest.mark.pgsql('pricing_data_preparer', files=['rules.sql'])
@pytest.mark.now('2019-02-01T14:00:00Z')
@pytest.mark.config(
    UNLOADING_CONFIG_BY_ZONE_AND_CATEGORY={
        'moscow': {
            'econom': {
                'free_time': 300.0,
                'max_distance_to_destination': 500.0,
            },
        },
    },
)
@pytest.mark.parametrize(
    'service_response_file, category_id, tariff_category_update',
    [
        (  # simple
            'simple_service_response.json',
            'ed3b2fe5c51f4a4da7bee86349259dda',
            lambda cat: None,
        ),
        (  # no_waiting_in_transit
            'no_waiting_in_transit_service_response.json',
            'ed3b2fe5c51f4a4da7bee86349259dda',
            lambda cat: cat.remove_requirement_price('waiting_in_transit'),
        ),
        (  # zero_waiting_in_transit
            'no_waiting_in_transit_service_response.json',
            'ed3b2fe5c51f4a4da7bee86349259dda',
            lambda cat: cat.set_requirement_price('waiting_in_transit', 0),
        ),
        (  # with_unloading
            'service_response_with_unloading.json',
            'ed3b2fe5c51f4a4da7bee86349259dda',
            lambda cat: cat.add_requirement_price('unloading', 1),
        ),
        (  # zero_unloading
            'no_unloading_service_response.json',
            'ed3b2fe5c51f4a4da7bee86349259dda',
            lambda cat: cat.add_requirement_price('unloading', 0),
        ),
    ],
    ids=[
        'simple',
        'no_waiting_in_transit',
        'zero_waiting_in_transit',
        'with_unloading',
        'zero_unloading',
    ],
)
async def test_taximeter_services(
        taxi_pricing_taximeter,
        driver_authorizer,
        load_json,
        mongodb,
        service_response_file,
        tariff_category_update,
        category_id,
        order_core,
        mock_order_core,
        mock_individual_tariffs,
):
    expected_services = load_json(service_response_file)
    driver_authorizer.set_session(
        AUTH['park_id'], AUTH['session'], AUTH['uuid'],
    )

    category = mock_individual_tariffs.get_tariff_category(
        '5d1f30c70c69ffa8ba0170c7', category_id,
    )
    tariff_category_update(category)

    response = await taxi_pricing_taximeter.post(
        'v1/get_modifications',
        json={'order_id': 'd78fdfe188ee39cbbdeb74235430fb40'},
        headers=DEFAULT_HEADERS,
        params={'park_id': AUTH['park_id']},
    )
    assert response.status_code == 200

    resp = response.json()
    services = resp['taximeter_metadata']['services']
    assert services == expected_services


@pytest.mark.pgsql('pricing_data_preparer', files=['rules.sql'])
@pytest.mark.now('2019-02-01T14:00:00Z')
@pytest.mark.config(
    PRICING_DATA_PREPARER_FREE_WAITING_TIME_OVERRIDES_BY_REQUIREMENTS={
        '__default__': {'__default__': {}},
        'moscow': {
            '__default__': {},
            'econom': {'test_req': 1440, 'smaller_req': 1439},
        },
    },
)
@pytest.mark.parametrize(
    'order_id, expected_waiting_services',
    [
        (
            '00000000000000000000000000000001',
            {'fixed': {'free_time': 180}, 'taximeter': {'free_time': 180}},
        ),
        (
            '00000000000000000000000000000002',
            {'fixed': {'free_time': 180}, 'taximeter': {'free_time': 180}},
        ),
        (
            '00000000000000000000000000000003',
            {'fixed': {'free_time': 1440}, 'taximeter': {'free_time': 1440}},
        ),
    ],
    ids=['simple', 'other_req', 'target_req'],
)
async def test_taximeter_waiting_service_override(
        taxi_pricing_taximeter,
        driver_authorizer,
        order_id,
        expected_waiting_services,
        order_core,
        mock_order_core,
):
    driver_authorizer.set_session(
        AUTH['park_id'], AUTH['session'], AUTH['uuid'],
    )

    response = await taxi_pricing_taximeter.post(
        'v1/get_modifications',
        json={'order_id': order_id},
        headers=DEFAULT_HEADERS,
        params={'park_id': AUTH['park_id']},
    )
    assert response.status_code == 200

    resp = response.json()
    waiting_services = resp['taximeter_metadata']['services']['waiting']
    assert waiting_services == expected_waiting_services


@pytest.mark.pgsql('pricing_data_preparer', files=['rules.sql'])
@pytest.mark.parametrize(
    'corp_tariff_home_zone, expected_max_distance_from_point_b,'
    'corp_tariffs_timeout, corp_tariffs_response_code',
    [
        ('invalid', None, False, 200),
        ('moscow', 123, False, 200),
        ('minsk', 321, False, 200),
        (None, None, False, 404),
        (None, None, True, 500),
    ],
    ids=[
        'invalid_home_zone',
        'tariff_settings_for_moscow',
        'tariff_settings_for_minsk',
        'corp_tariffs_404',
        'corp_tariffs_timeout',
    ],
)
async def test_v1_get_modifications_decoupling(
        taxi_pricing_taximeter,
        driver_authorizer,
        corp_tariff_home_zone,
        expected_max_distance_from_point_b,
        corp_tariffs_timeout,
        corp_tariffs_response_code,
        mockserver,
        load_json,
        order_core,
        mock_order_core,
):
    def _corp_tariffs_helper(response_filename, mockserver):
        if corp_tariffs_timeout:
            raise mockserver.TimeoutError()

        if corp_tariffs_response_code == 200:
            return load_json(
                response_filename,
                object_hook=json_util.VarHook(
                    {'home_zone': corp_tariff_home_zone},
                ),
            )
        if corp_tariffs_response_code == 404:
            return mockserver.make_response(
                json={
                    'code': 'not_found',
                    'message': 'not_found message',
                    'details': {'reason': 'not_found details'},
                },
                status=404,
            )
        return mockserver.make_response('Internal Error', status=500)

    @mockserver.json_handler('/corp-tariffs/v1/tariff')
    def _mock_corp_tariffs(request):
        return _corp_tariffs_helper('corp_tariffs_response.json', mockserver)

    driver_authorizer.set_session(
        AUTH['park_id'], AUTH['session'], AUTH['uuid'],
    )

    response = await taxi_pricing_taximeter.post(
        'v1/get_modifications',
        json={'order_id': 'd78fdfe188ee39cbbdeb74235430fb40'},
        headers=DEFAULT_HEADERS,
        params={'park_id': AUTH['park_id']},
    )
    expected_code = (
        200
        if (
            not corp_tariffs_timeout
            and corp_tariffs_response_code == 200
            and expected_max_distance_from_point_b
        )
        else 500
    )
    assert response.status_code == expected_code
    assert _mock_corp_tariffs.has_calls

    if expected_code == 200:
        resp = response.json()
        assert 'taximeter_metadata' in resp
        taximeter_metadata = resp['taximeter_metadata']
        assert 'fixed_price_discard_parameters' in taximeter_metadata
        fixed_price_discard_parameters = taximeter_metadata[
            'fixed_price_discard_parameters'
        ]
        assert 'max_distance_from_point_b' in fixed_price_discard_parameters
        assert (
            fixed_price_discard_parameters['max_distance_from_point_b']
            == expected_max_distance_from_point_b
        )


@pytest.mark.pgsql('pricing_data_preparer', files=['rules.sql'])
@pytest.mark.experiments3(
    consumers=['pricing-data-preparer/caches'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[],
    name='enable_drafts_prestable_evaluation',
    default_value={'enabled': True},
    is_config=True,
)
async def test_prestable_drafts_compilation(
        taxi_pricing_taximeter,
        testpoint,
        driver_authorizer,
        order_core,
        mock_order_core,
):
    @testpoint('compile_prestable_drafts')
    def compile_prestable_drafts_tp(data):
        assert data == ['run_on_pre_draft']

    driver_authorizer.set_session(
        AUTH['park_id'], AUTH['session'], AUTH['uuid'],
    )

    response = await taxi_pricing_taximeter.post(
        'v1/get_modifications',
        json={'order_id': 'd78fdfe188ee39cbbdeb74235430fb40'},
        headers=DEFAULT_HEADERS,
        params={'park_id': AUTH['park_id']},
    )
    assert response.status_code == 200
    assert compile_prestable_drafts_tp.times_called == 1


@pytest.mark.pgsql('pricing_data_preparer', files=['rules.sql'])
async def test_read_from_order_core(
        taxi_pricing_taximeter,
        experiments3,
        driver_authorizer,
        mock_order_core,
        order_core,
):
    experiments3.add_config(
        consumers=['pricing-data-preparer/pricing_components'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[],
        name='read_order_proc_from_order_core',
        default_value={
            '__default__': 'mongo',
            'get_modifications': 'order_core',
        },
    )

    driver_authorizer.set_session(
        AUTH['park_id'], AUTH['session'], AUTH['uuid'],
    )

    order_core.set_expected_key(
        'd78fdfe188ee39cbbdeb74235430fb40',
        OrderIdRequestType.alias_id,
        require_latest=True,
    )

    response = await taxi_pricing_taximeter.post(
        'v1/get_modifications',
        json={'order_id': 'd78fdfe188ee39cbbdeb74235430fb40'},
        headers=DEFAULT_HEADERS,
        params={'park_id': AUTH['park_id']},
    )

    assert response.status_code == 200

    assert mock_order_core.times_called == 1


@pytest.mark.pgsql('pricing_data_preparer', files=['rules_testing.sql'])
@pytest.mark.experiments3(filename='exp3_base_price_discount.json')
@pytest.mark.config(
    PRICING_DATA_PREPARER_METADATA_MAPPING={
        'dummy': {'taximeter': True, 'backend': True},
    },
    PRICING_DATA_PREPARER_COMPILATION_TIMEOUT=120000,
)
async def test_v1_get_modifications_testing_rules(
        taxi_pricing_taximeter,
        driver_authorizer,
        load_json,
        order_core,
        mock_order_core,
):
    driver_authorizer.set_session(
        '7ad36bc7560449998acbe2c57a75c293',
        AUTH['session'],
        '7a6d8a4b776a10116206637a41720961',
    )

    response = await taxi_pricing_taximeter.post(
        'v1/get_modifications',
        json={'order_id': '90ee28385d65cfefb3ea2c730fe15830'},
        headers=DEFAULT_HEADERS,
        params={'park_id': '7ad36bc7560449998acbe2c57a75c293'},
    )
    assert response.status_code == 200

    variables = {
        'driver': {
            'for_taximeter': 'EgASASMRQAzMzMzMzM0iggAAFAAUARIBEQAAAAAAAAAAUREAAAAAAAAAABIBEUEidQAAAAAAUBEAAAAAAAAAABIBEUDlGAAAAAAAUBUAEUAkAAAAAAAAUREAAAAAAAAAABQCABQCAAAAFAMUBBQFFAaBEgASASMRQAzMzMzMzM0iggAAFAASABFBUxLQAAAAAFARAAAAAAAAAAASABFBHoSAAAAAAFASARE/Gjbi6xxDLVAVABFAaQAAAAAAAFARAAAAAAAAAAAUAQARAAAAAAAAAAAAFAEAABQCFAMUBBQFFAaBFAAUARQCFAMUBBQFFAaBFAAUARQCFAMUBBQFFAaBEgIRQILAAAAAAABREgIRQILAAAAAAAAAggAAFQARQCgAAAAAAAAiEUBOAAAAAAAAI4IAARFAaOAAAAAAABUBIIIAAhQAFAEUAhQDFAQUBRQGgRICEUAoAAAAAAAAIhFATgAAAAAAACOCAAAUABQBFAISAhFA1RgAAAAAAFAUAxICEQAAAAAAAAAAUBUAFAMAABQEFAUUBoEUBRIDEQAAAAAAAAAAIiCCAAAUABQBFAIUAxQEEgMRQOUYAAAAAABQFAUSAxEAAAAAAAAAAFAVABQFAAAUBoEUBhIEEQAAAAAAAAAAIiCCAAAUABQBFAIUAxQEFAUSBBFA1RgAAAAAAFAUBhIEEQAAAAAAAAAAUBUAFAYAAIEUABQBFAIUAxQEFAUUBoEUABQBFAIUAxQEFAUUBoEUABQBFAIUAxQEEQAAAAAAAAAAIBEAAAAAAAAAACAUBRQGgRE/8AAAAAAAABQDIoIAABE/8AAAAAAAABQFIoIAARE/8AAAAAAAABQGIoIAAhE/8AAAAAAAABQAIhEAAAAAAAAAACCCAAMRP/AAAAAAAAAUASKCAAQRP/AAAAAAAAAUAiKCAAURP/AAAAAAAAAUBCKCAAYVAxUEIBUFIBUGIBQDIBQFIBQGIIIABxUHEyGCAAgTET8aNuLrHEMtUBUHEyMRP/AAAAAAAAAAggAJFQkRP6mZmZmZmZohET+5mZmZmZmaJYIAChUIET/wAAAAAAAAJYIACxUDFQQgFQUgFQYgFQAgFQEgFQIgEyGCAAwVAxUEFQUVABUGFQEVAoEUABQBFAIUAxQEFAUUBoESAhFAgsAAAAAAAFAUAxFAgsAAAAAAACISAiMUAwCCAAARAAAAAAAAAAARP/AAAAAAAAAUACIgggABFAAUARQCFAMUBBQFFAaBFAAUARQCFAMUBBQFFAaBFAAUARQCFAMUBBQFFAaBFAAUARQCFAMUBBQFFAaBET/wAAAAAAAAFAAiET/wAAAAAAAAFAEiET/wAAAAAAAAFAIiET/wAAAAAAAAFAMiET/wAAAAAAAAFAQiET/wAAAAAAAAFAUiET/wAAAAAAAAFAYigRQAFAEUAhQDFAQUBRQGgRQAFAEUAhQDFAQUBRQGgRQAFAEUAhQDFAQUBRQGgRQAFAEgFAIgEUBo4AAAAAAAURFAaOAAAAAAABQAFAEgFAIgIREAAAAAAAAAAACCAAAUABUAIBQBFAIUAxQEFAUUBoEUABQEIBEAAAAAAAAAAFAUABQEIBEAAAAAAAAAAACCAAAUABQBFAIUAxQEFAUUBoEUABQBFAIUAxQEFAUUBoE=',
        },
        'user': {
            'for_taximeter': 'EgASASMRQAzMzMzMzM0iggAAFAAUARIBEQAAAAAAAAAAUREAAAAAAAAAABIBEUEidQAAAAAAUBEAAAAAAAAAABIBEUDlGAAAAAAAUBUAEUAkAAAAAAAAUREAAAAAAAAAABQCABQCAAAAFAMUBBQFFAaBEgASASMRQAzMzMzMzM0iggAAFAASABFBUxLQAAAAAFARAAAAAAAAAAASABFBHoSAAAAAAFASARE/Gjbi6xxDLVAVABFAaQAAAAAAAFARAAAAAAAAAAAUAQARAAAAAAAAAAAAFAEAABQCFAMUBBQFFAaBFAAUARQCFAMUBBQFFAaBFAAUARQCFAMUBBQFFAaBEgIRQILAAAAAAABREgIRQILAAAAAAAAAggAAFQARQCgAAAAAAAAiEUBOAAAAAAAAI4IAARFAaOAAAAAAABUBIIIAAhQAFAEUAhQDFAQUBRQGgRICEUAoAAAAAAAAIhFATgAAAAAAACOCAAAUABQBFAISAhFA1RgAAAAAAFAUAxICEQAAAAAAAAAAUBUAFAMAABQEFAUUBoEUBRIDEQAAAAAAAAAAIiCCAAAUABQBFAIUAxQEEgMRQOUYAAAAAABQFAUSAxEAAAAAAAAAAFAVABQFAAAUBoEUBhIEEQAAAAAAAAAAIiCCAAAUABQBFAIUAxQEFAUSBBFA1RgAAAAAAFAUBhIEEQAAAAAAAAAAUBUAFAYAAIEUABQBFAIUAxQEFAUUBoEUABQBFAIUAxQEFAUUBoEUABQBFAIUAxQEEQAAAAAAAAAAIBEAAAAAAAAAACAUBRQGgRQAFAEUAhQDFAQUBRQGgRE/8AAAAAAAABQDIoIAABE/8AAAAAAAABQFIoIAARE/8AAAAAAAABQGIoIAAhE/8AAAAAAAABQAIhEAAAAAAAAAACCCAAMRP/AAAAAAAAAUASKCAAQRP/AAAAAAAAAUAiKCAAURP/AAAAAAAAAUBCKCAAYVAxUEIBUFIBUGIBQDIBQFIBQGIIIABxUHEyGCAAgTET8aNuLrHEMtUBUHEyMRP/AAAAAAAAAAggAJFQkRP6mZmZmZmZohET+5mZmZmZmaJYIAChUIET/wAAAAAAAAJYIACxUDFQQgFQUgFQYgFQAgFQEgFQIgEyGCAAwVAxUEFQUVABUGFQEVAoEUABQBFAIUAxQEFAUUBoESAhFAgsAAAAAAAFAUAxFAgsAAAAAAACISAiMUAwCCAAARAAAAAAAAAAARP/AAAAAAAAAUACIgggABFAAUARQCFAMUBBQFFAaBFAAUARQCFAMUBBQFFAaBFAAUARQCFAMUBBQFFAaBFAAUARQCFAMUBBQFFAaBFAAUARQCFAMUBBQFFAaBET/wAAAAAAAAFAAiET/wAAAAAAAAFAEiET/wAAAAAAAAFAIiET/wAAAAAAAAFAMiET/wAAAAAAAAFAQiET/wAAAAAAAAFAUiET/wAAAAAAAAFAYigRQAFAEUAhQDFAQUBRQGgRQAFAQgEQAAAAAAAAAAUBQAFAQgEQAAAAAAAAAAAIIAABQAFAEUAhQDFAQUBRQGgRQAFAEUAhQDFAQUBRQGgRQAFAEUAhQDFAQUBRQGgRQAFAEUAhQDFAQUBRQGgRQAFAEUAhQDFAQUBRQGgRQAFAEUAhQDFAQUBRQGgRQAFAEUAhQDFAQUBRQGgQ==',
        },
        'meta': {'dummy': 19},
    }
    expected_response = load_json(
        'response.json', object_hook=json_util.VarHook(variables),
    )
    assert response.json() == expected_response
