import pytest

from tests_merchant_profiles import utils


@pytest.mark.config(
    MERCHANT_PROFILES_MERCHANTS=utils.MERCHANT_PROFILES_MERCHANTS,
)
async def test_merchants_post(taxi_merchant_profiles):
    merchant_ids = [
        'merchant-id-1',
        'merchant-id-2',
        'merchant-id-3',
        'merchant-id-4',
    ]

    response = await taxi_merchant_profiles.post(
        '/internal/merchant-profiles/v1/merchants/bulk-retrieve',
        json={'merchant_ids': merchant_ids},
    )

    assert response.status == 200
    assert response.json() == {
        'merchants': [
            {
                'merchant_id': 'merchant-id-1',
                'merchant': {
                    'merchant_name': 'Vkusvill',
                    'park_id': 'park-id-1',
                    'enable_balance_check_on_pay': False,
                    'enable_requisites_check_on_draft': True,
                    'payment_ttl_sec': 300,
                    'payment_scheme': 'yandex_withhold',
                },
            },
            {
                'merchant_id': 'merchant-id-2',
                'merchant': {
                    'merchant_name': 'Pyaterochka',
                    'enable_balance_check_on_pay': True,
                    'enable_requisites_check_on_draft': False,
                    'payment_scheme': 'remittance',
                },
            },
            {'merchant_id': 'merchant-id-3'},
            {'merchant_id': 'merchant-id-4'},
        ],
    }


@pytest.mark.config(
    MERCHANT_PROFILES_MERCHANTS=utils.MERCHANT_PROFILES_MERCHANTS,
)
async def test_duplicate_merchant_ids(taxi_merchant_profiles):
    merchant_ids = [
        'merchant-id-1',
        'merchant-id-2',
        'merchant-id-2',
        'merchant-id-4',
    ]

    response = await taxi_merchant_profiles.post(
        '/internal/merchant-profiles/v1/merchants/bulk-retrieve',
        json={'merchant_ids': merchant_ids},
    )

    assert response.status == 400
    assert response.json() == {
        'code': 'duplicate_merchant_ids',
        'message': 'duplicate_merchant_ids',
    }
