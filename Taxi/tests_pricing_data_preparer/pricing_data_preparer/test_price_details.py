# pylint: disable=redefined-outer-name, import-only-modules
# flake8: noqa F401
import copy
import datetime

import pytest

from tests_plugins import json_util

from .plugins import utils_request

from .plugins.mock_order_core import mock_order_core
from .plugins.mock_order_core import order_core


from .plugins.mock_surge import mock_surger, surger
from .plugins.mock_user_api import (
    mock_user_api_get_phones,
    mock_user_api_get_users,
    user_api,
)


CONFIG_REQUIREMENTS_SECTION = {
    'patterns': [r'req:(\w+)(?:[:](price|per_unit|included|count))?'],
    'tanker': {'keyset': 'requirements_keyset', 'key_prefix': 'prefix.'},
}

CONFIG_SERVICES_SECTION = {
    'patterns': [r'srv:(\w+)(?:[:](price))?'],
    'tanker': {'keyset': 'services_keyset', 'key_suffix': '.suffix'},
}

CONFIG_INVALID_PATTERN = {
    'patterns': [r'missed_bracket_(?:[:](\w+)?'],
    'tanker': {'keyset': 'requirements_keyset'},
}

EXPECTED_METADATA = {
    'req:something_important:count': 4.0,
    'req:something_important:per_unit': 25.0,
    'req:something_important:price': 100.0,
    'srv:anything_unusual:price': 34.21,
    'srv:something_unusual': 12.34,
}

EXPECTED_REQUIREMENTS = [
    {
        'name': 'something_important',
        'text': {
            'keyset': 'requirements_keyset',
            'tanker_key': 'prefix.something_important',
        },
        'price': {'total': 100.0, 'per_unit': 25.0},
        'count': 4,
        'included': 0,
    },
]

EXPECTED_SERVICES = [
    {
        'name': 'anything_unusual',
        'text': {
            'keyset': 'services_keyset',
            'tanker_key': 'anything_unusual.suffix',
        },
        'price': 34.21,
    },
    {
        'name': 'something_unusual',
        'text': {
            'keyset': 'services_keyset',
            'tanker_key': 'something_unusual.suffix',
        },
        'price': 12.34,
    },
]


@pytest.fixture(name='new_pricing_flow_dry_run', autouse=False)
def new_pricing_flow_dry_run(testpoint, experiments3):
    experiments3.add_experiment(
        clauses=[
            {
                'predicate': {'type': 'true'},
                'enabled': True,
                'title': '',
                'value': {'work_mode': 'dry_run', 'skip_source_load': True},
            },
        ],
        name='new_pricing_data_generator_settings',
        consumers=['pricing-data-preparer/prepare'],
        match={'enabled': True, 'predicate': {'type': 'true'}},
    )

    @testpoint('new_pricing_flow_dry_run')
    def _new_pricing_flow_dry_run(data):
        data['new'].pop('backend_variables_uuids', None)
        data['old'].pop('backend_variables_uuids', None)
        assert data['new'] == data['old']

    return _new_pricing_flow_dry_run


@pytest.mark.parametrize(
    'requirements, is_requirements_valid',
    [
        (None, True),
        (CONFIG_REQUIREMENTS_SECTION, True),
        (CONFIG_INVALID_PATTERN, False),
    ],
    ids=['no_requirements', 'has_requirements', 'invalid_requirements'],
)
@pytest.mark.parametrize(
    'services, is_services_valid',
    [
        (None, True),
        (CONFIG_SERVICES_SECTION, True),
        (CONFIG_INVALID_PATTERN, False),
    ],
    ids=['no_services', 'has_services', 'invalid_services'],
)
@pytest.mark.pgsql(
    'pricing_data_preparer', files=['rules.sql', 'workabilities.sql'],
)
async def test_v2_prepare_price_details(
        taxi_pricing_data_preparer,
        taxi_config,
        requirements,
        is_requirements_valid,
        services,
        is_services_valid,
        mock_yamaps_router,
        mock_user_api_get_users,
        mock_user_api_get_phones,
        mock_surger,
        new_pricing_flow_dry_run,
):
    details_config = {'__default__': {}}

    if requirements:
        details_config['__default__']['requirements'] = requirements
    if services:
        details_config['__default__']['services'] = services

    taxi_config.set(
        PRICING_DATA_PREPARER_DETAILING_BY_CONSUMERS=details_config,
    )

    pre_request = utils_request.Request()
    pre_request.set_details_enabled('consumer001')

    request = pre_request.get()
    response = await taxi_pricing_data_preparer.post(
        'v2/prepare', json=request,
    )
    assert response.status_code == 200

    data = response.json()
    for category in data['categories'].values():
        for subject in ('driver', 'user'):
            assert 'meta' in category[subject]
            assert category[subject]['meta'] == EXPECTED_METADATA

            if (requirements and is_requirements_valid) or (
                    services and is_services_valid
            ):
                assert 'additional_payloads' in category[subject]
                additional_payloads = category[subject]['additional_payloads']
                assert 'details' in additional_payloads
                details = additional_payloads['details']
                if requirements and is_requirements_valid:
                    assert 'requirements' in details
                    requirements = details['requirements']
                    assert (
                        sorted(requirements, key=lambda x: x['name'])
                        == EXPECTED_REQUIREMENTS
                    )
                else:
                    assert 'requirements' not in details
                if services and is_services_valid:
                    assert 'services' in details
                    services = details['services']
                    assert (
                        sorted(services, key=lambda x: x['name'])
                        == EXPECTED_SERVICES
                    )
                else:
                    assert 'services' not in details
                continue
            assert 'additional_payloads' not in category[subject] or (
                category[subject]['additional_payloads']
                and 'details' not in category[subject]['additional_payloads']
            )
    assert new_pricing_flow_dry_run.times_called > 0


@pytest.mark.parametrize(
    'requirements, is_requirements_valid',
    [
        (None, True),
        (CONFIG_REQUIREMENTS_SECTION, True),
        (CONFIG_INVALID_PATTERN, False),
    ],
    ids=['no_requirements', 'has_requirements', 'invalid_requirements'],
)
@pytest.mark.parametrize(
    'services, is_services_valid',
    [
        (None, True),
        (CONFIG_SERVICES_SECTION, True),
        (CONFIG_INVALID_PATTERN, False),
    ],
    ids=['no_services', 'has_services', 'invalid_services'],
)
@pytest.mark.pgsql(
    'pricing_data_preparer', files=['rules.sql', 'workabilities.sql'],
)
async def test_v2_recalc_price_details(
        taxi_pricing_data_preparer,
        taxi_config,
        load_json,
        requirements,
        is_requirements_valid,
        services,
        is_services_valid,
):
    details_config = {'__default__': {}}

    if requirements:
        details_config['__default__']['requirements'] = requirements
    if services:
        details_config['__default__']['services'] = services

    taxi_config.set(
        PRICING_DATA_PREPARER_DETAILING_BY_CONSUMERS=details_config,
    )

    response = await taxi_pricing_data_preparer.post(
        'v2/recalc', json=load_json('v2_recalc.json'),
    )
    assert response.status_code == 200

    data = response.json()['price']
    for subject in ('driver', 'user'):
        assert 'meta' in data[subject]
        assert data[subject]['meta'] == EXPECTED_METADATA

        assert 'additional_payloads' in data[subject]
        additional_payloads = data[subject]['additional_payloads']
        assert 'details' in additional_payloads
        details = additional_payloads['details']

        if requirements and is_requirements_valid:
            assert 'requirements' in details
            requirements = details['requirements']
            assert (
                sorted(requirements, key=lambda x: x['name'])
                == EXPECTED_REQUIREMENTS
            )
        else:
            assert 'requirements' not in details

        if services and is_services_valid:
            assert 'services' in details
            services = details['services']
            assert (
                sorted(services, key=lambda x: x['name']) == EXPECTED_SERVICES
            )
        else:
            assert 'services' not in details


@pytest.mark.parametrize(
    'details_consumer, expected_details',
    [(None, None), ('INVALID', '__default__'), ('foo-bar', 'foo-bar')],
    ids=['no_details', 'fallback_to_default', 'custom_consumer'],
)
@pytest.mark.parametrize(
    'handler_name',
    ['v2/calc_paid_supply', 'v2/prepare', 'v2/recalc', 'v2/recalc_order'],
)
@pytest.mark.pgsql(
    'pricing_data_preparer', files=['rules.sql', 'workabilities.sql'],
)
@pytest.mark.usefixtures(
    'mock_user_api_get_users',
    'mock_user_api_get_phones',
    'mock_surger',
    'mock_yamaps_router',
)
@pytest.mark.experiments3(filename='exp3_config_paid_supply_min_price.json')
async def test_details_consumer(
        taxi_pricing_data_preparer,
        taxi_config,
        load_json,
        details_consumer,
        expected_details,
        handler_name,
        new_pricing_flow_dry_run,
        order_core,
        mock_order_core,
):
    def _replace_config_section(config_section, key_prefix, key_suffix=None):
        result = copy.deepcopy(config_section)
        result['tanker']['key_prefix'] = key_prefix
        if key_suffix:
            result['tanker']['key_suffix'] = key_suffix
        elif 'key_suffix' in result['tanker']:
            result['tanker'].pop('key_suffix')
        return result

    def _replace_config_tankers(details_config):
        for key, value in details_config.items():
            value['requirements'] = _replace_config_section(
                value['requirements'], key + '.req.',
            )
            value['services'] = _replace_config_section(
                value['services'], key + '.srv.',
            )

    def _replace_expected_tankers(details_section, key_prefix, key_suffix=''):
        result = copy.deepcopy(details_section)
        for each in result:
            each['text']['tanker_key'] = each['text']['tanker_key'].replace(
                '.suffix', key_suffix,
            )
            tanker_key = each['text']['tanker_key']
            if tanker_key.startswith('prefix.'):
                each['text']['tanker_key'] = tanker_key.replace(
                    'prefix.', key_prefix,
                )
            else:
                each['text']['tanker_key'] = key_prefix + tanker_key
        return result

    details_config = {}
    details_config['__default__'] = {
        'requirements': CONFIG_REQUIREMENTS_SECTION,
        'services': CONFIG_SERVICES_SECTION,
    }
    details_config['foo-bar'] = {
        'requirements': CONFIG_REQUIREMENTS_SECTION,
        'services': CONFIG_SERVICES_SECTION,
    }
    _replace_config_tankers(details_config)

    taxi_config.set(
        PRICING_DATA_PREPARER_DETAILING_BY_CONSUMERS=details_config,
    )

    request_body = load_json(
        '{}.json'.format(handler_name.replace('/', '_')),
        object_hook=json_util.VarHook({'details_consumer': details_consumer}),
    )

    response = await taxi_pricing_data_preparer.post(
        handler_name,
        json=request_body,
        headers={'Accept-Language': 'en-EN'},
        params={'order_id': 'order_id'},
    )
    assert response.status_code == 200

    data = response.json()
    for subject in ('driver', 'user'):
        if handler_name in {'v2/recalc', 'v2/recalc_order'}:
            actual = data['price'][subject]
        elif handler_name in {'v2/calc_paid_supply'}:
            actual = data['categories']['econom'][subject][
                'additional_prices'
            ]['paid_supply']
        elif handler_name in {'v2/prepare'}:
            actual = data['categories']['econom'][subject]

        if details_consumer:
            expected_requirements = _replace_expected_tankers(
                EXPECTED_REQUIREMENTS, expected_details + '.req.',
            )
            expected_services = _replace_expected_tankers(
                EXPECTED_SERVICES, expected_details + '.srv.',
            )

            assert (
                'additional_payloads' in actual
                and 'details' in actual['additional_payloads']
            )
            requirements = actual['additional_payloads']['details'][
                'requirements'
            ]
            assert (
                sorted(requirements, key=lambda x: x['name'])
                == expected_requirements
            )
            services = actual['additional_payloads']['details']['services']
            assert (
                sorted(services, key=lambda x: x['name']) == expected_services
            )
        else:
            assert (
                not 'additional_payloads' in actual
                or not 'details' in actual['additional_payloads']
            )
    if handler_name == 'v2/prepare':
        assert new_pricing_flow_dry_run.times_called == 1
