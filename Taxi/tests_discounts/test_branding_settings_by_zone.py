# noqa: F841 E501,  pylint: disable=C0301
import json

import pytest

from tests_discounts import common


@pytest.mark.pgsql(
    'discounts',
    files=[
        'zonal_lists.sql',
        'discounts_entities.sql',
        'discounts_lists.sql',
        'user_discounts.sql',
    ],
)
async def test_branding_settings_empty(taxi_discounts):
    request = {'zone': 'moscow'}
    response = await taxi_discounts.post(
        'v1/branding-settings-by-zone',
        headers=common.DEFAULT_DISCOUNTS_HEADER,
        data=json.dumps(request),
    )
    assert response.status_code == 200
    assert response.json() == {'branding_items': []}


@pytest.mark.pgsql(
    'discounts',
    files=[
        'zonal_lists.sql',
        'discounts_entities.sql',
        'discounts_lists.sql',
        'user_discounts.sql',
    ],
)
@pytest.mark.now('2019-03-08T00:00:00Z')
async def test_branding_settings_by_zone(taxi_discounts):
    request = {'zone': 'moscow'}
    response = await taxi_discounts.post(
        'v1/branding-settings-by-zone',
        headers=common.DEFAULT_DISCOUNTS_HEADER,
        data=json.dumps(request),
    )
    assert response.status_code == 200
    assert response.json() == {
        'branding_items': [
            {
                'bin_filter': ['123456'],
                'branding_keys': {
                    'card_title': 'key_card_title',
                    'card_subtitle': 'key_card_subtitle',
                    'payment_method_subtitle': 'key_payment_method_subtitle',
                },
                'classes': ['econom'],
                'combined_branding_keys': {
                    'card_title': 'combined_key_card_title',
                    'card_subtitle': 'combined_key_card_subtitle',
                    'payment_method_subtitle': 'combined_key_payment_method_subtitle',  # noqa: F841 E501,  pylint: disable=C0301
                },
            },
            {
                'bin_filter': ['654321'],
                'branding_keys': {},
                'classes': ['business'],
                'combined_branding_keys': {},
            },
        ],
    }


@pytest.mark.pgsql(
    'discounts',
    files=[
        'zonal_lists.sql',
        'discounts_entities.sql',
        'discounts_lists.sql',
        'user_discounts.sql',
    ],
)
async def test_branding_settings_empty_branding_keys(taxi_discounts):
    request = {'zone': 'moscow'}
    response = await taxi_discounts.post(
        'v1/branding-settings-by-zone',
        headers=common.DEFAULT_DISCOUNTS_HEADER,
        data=json.dumps(request),
    )
    assert response.status_code == 200
    assert response.json() == {
        'branding_items': [
            {
                'bin_filter': ['123456'],
                'branding_keys': {},
                'classes': ['econom'],
                'combined_branding_keys': {},
            },
        ],
    }


@pytest.mark.config(USE_AGGLOMERATIONS_CACHE=True)
@pytest.mark.pgsql(
    'discounts',
    files=[
        'zonal_lists.sql',
        'discounts_entities.sql',
        'discounts_lists.sql',
        'user_discounts.sql',
    ],
)
async def test_branding_settings_by_agglomeration(taxi_discounts):
    await taxi_discounts.invalidate_caches()
    await taxi_discounts.invalidate_caches()
    request = {'zone': 'moscow'}
    response = await taxi_discounts.post(
        'v1/branding-settings-by-zone',
        headers=common.DEFAULT_DISCOUNTS_HEADER,
        data=json.dumps(request),
    )
    assert response.status_code == 200
    assert response.json() == {
        'branding_items': [
            {
                'bin_filter': ['123456'],
                'branding_keys': {
                    'card_subtitle': 'key_card_subtitle',
                    'card_title': 'key_card_title',
                    'payment_method_subtitle': 'key_payment_method_subtitle',
                },
                'classes': ['econom'],
                'combined_branding_keys': {
                    'card_subtitle': 'combined_key_card_subtitle',
                    'card_title': 'combined_key_card_title',
                    'payment_method_subtitle': 'combined_key_payment_method_subtitle',  # noqa: F841 E501,  pylint: disable=C0301
                },
            },
            {
                'bin_filter': ['654321'],
                'branding_keys': {},
                'classes': ['business'],
                'combined_branding_keys': {},
            },
        ],
    }
