# pylint: disable=redefined-outer-name, import-only-modules
# flake8: noqa F401
import copy
import datetime

import pytest

from tests_plugins import json_util

from tests_pricing_taximeter.plugins import utils_request
from tests_pricing_taximeter.plugins.mock_order_core import mock_order_core
from tests_pricing_taximeter.plugins.mock_order_core import order_core


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
async def test_v1_save_order_details_price_details(
        taxi_pricing_taximeter,
        taxi_config,
        load_json,
        requirements,
        is_requirements_valid,
        services,
        is_services_valid,
        order_core,
        mock_order_core,
):
    details_config = {'__default__': {}}

    if requirements:
        details_config['__default__']['requirements'] = requirements
    if services:
        details_config['__default__']['services'] = services

    taxi_config.set(
        PRICING_DATA_PREPARER_DETAILING_BY_CONSUMERS=details_config,
    )

    response = await taxi_pricing_taximeter.post(
        'v1/save_order_details',
        json=load_json('v1_save_order_details.json'),
        params={'order_id': 'order_id', 'taximeter_app': 'Taximeter 9.8'},
    )
    assert response.status_code == 200

    data = response.json()
    for subject in ('driver', 'user'):
        assert 'meta' in data['price'][subject]
        assert data['price'][subject]['meta'] == EXPECTED_METADATA

        if (requirements and is_requirements_valid) or (
                services and is_services_valid
        ):
            assert 'additional_payloads' in data['price'][subject]
            additional_payloads = data['price'][subject]['additional_payloads']
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
        else:
            assert (
                not 'additional_payloads' in data['price'][subject]
                or not 'details'
                in data['price'][subject]['additional_payloads']
            )


@pytest.mark.filldb(order_proc='agent')
@pytest.mark.pgsql(
    'pricing_data_preparer', files=['rules.sql', 'workabilities.sql'],
)
@pytest.mark.now('2020-11-10T17:28:00+03:00')
@pytest.mark.config(
    PRICING_SAVE_AGENT_ORDERS_DETAILS=True,
    PRICING_DATA_PREPARER_DETAILING_BY_CONSUMERS={
        '__default__': {
            'requirements': CONFIG_REQUIREMENTS_SECTION,
            'services': CONFIG_SERVICES_SECTION,
        },
    },
)
async def test_save_agent_order_details(
        taxi_pricing_taximeter, load_json, stq, mock_order_core, order_core,
):
    response = await taxi_pricing_taximeter.post(
        'v1/save_order_details',
        json=load_json('v1_save_order_details.json'),
        params={
            'order_id': 'alias_agent_order_id',
            'taximeter_app': 'Taximeter 9.8',
        },
    )
    assert response.status_code == 200

    queue = stq.agent_orders_save_price_details
    assert queue.times_called == 1

    stq_calls = [
        stq.agent_orders_save_price_details.next_call()
        for _ in range(queue.times_called)
    ]
    for call_data in stq_calls:
        call_data.pop('id')  # some generated uuid
        kwargs = call_data['kwargs']
        kwargs.pop('log_extra')  # contains link
        kwargs['details']['services'].sort(key=lambda item: item['name'])

    assert stq_calls == [
        {
            'queue': 'agent_orders_save_price_details',
            'args': [],
            'eta': datetime.datetime(2020, 11, 10, 14, 28),
            'kwargs': {
                'details': {
                    'requirements': [
                        {
                            'count': 4,
                            'included': 0,
                            'name': 'something_important',
                            'price': {'per_unit': 25.0, 'total': 100.0},
                            'text': {
                                'keyset': 'requirements_keyset',
                                'tanker_key': 'prefix.something_important',
                            },
                        },
                    ],
                    'services': [
                        {
                            'name': 'anything_unusual',
                            'price': 34.21,
                            'text': {
                                'keyset': 'services_keyset',
                                'tanker_key': 'anything_unusual.suffix',
                            },
                        },
                        {
                            'name': 'something_unusual',
                            'price': 12.34,
                            'text': {
                                'keyset': 'services_keyset',
                                'tanker_key': 'something_unusual.suffix',
                            },
                        },
                    ],
                },
                'order_id': 'agent_order_id',
                'calculated_at': '2020-11-10T14:28:00+00:00',
            },
        },
    ]
