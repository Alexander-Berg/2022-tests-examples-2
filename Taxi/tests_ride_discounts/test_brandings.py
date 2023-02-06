import datetime

import pytest

from tests_ride_discounts import common


@pytest.mark.now('2019-01-01T00:00:00+00:00')
@pytest.mark.pgsql('ride_discounts', files=['init.sql'])
async def test_v1_brandings(client, load_json, mocked_time):
    response = await client.post(
        '/v1/admin/prioritized-entity',
        headers=common.get_draft_headers(),
        json={
            'name': 'bin_set\'_name',
            'data': {
                'active_period': {
                    'start': '2019-01-01T00:00:01',
                    'end': '2023-01-01T00:00:03',
                },
                'prioritized_entity_type': 'bin_set',
                'bins': ['222100'],
            },
        },
    )
    assert response.status == 200, response.json()
    await client.invalidate_caches()

    response = await client.post(
        'v1/admin/match-discounts/add-rules',
        headers=common.get_draft_headers(),
        json=load_json('add_rules_data.json'),
    )

    mocked_time.set(
        datetime.datetime.fromisoformat('2021-06-26T18:00:00+00:00'),
    )
    assert response.status == 200, response.json()
    await client.invalidate_caches()

    response = await client.post(
        'v1/brandings',
        headers=common.get_headers(),
        json={'tariff_zone': 'moscow', 'tariffs': ['econom']},
    )
    assert response.status == 200
    assert response.json() == {
        'items': [
            {
                'branding_keys': {
                    'combined_branding_keys': {
                        'card_subtitle': 'test_combined_card_subtitle',
                        'card_title': 'test_combined_card_title',
                        'payment_method_subtitle': (
                            'test_combined_payment_method_subtitle'
                        ),
                    },
                    'default_branding_keys': {
                        'card_subtitle': 'test_card_subtitle',
                        'card_title': 'test_card_title',
                        'payment_method_subtitle': (
                            'test_payment_method_subtitle'
                        ),
                    },
                },
                'payment_system': 'Mastercard',
                'tariff': 'econom',
            },
        ],
    }
