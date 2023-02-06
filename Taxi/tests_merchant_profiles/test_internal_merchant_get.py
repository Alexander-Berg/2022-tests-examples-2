import pytest

from tests_merchant_profiles import utils


@pytest.mark.config(
    MERCHANT_PROFILES_MERCHANTS=utils.MERCHANT_PROFILES_MERCHANTS,
)
@pytest.mark.parametrize(
    'merchant_id, status, expected_response',
    [
        pytest.param(
            'merchant-id-1',
            200,
            {
                'merchant_name': 'Vkusvill',
                'park_id': 'park-id-1',
                'enable_balance_check_on_pay': False,
                'enable_requisites_check_on_draft': True,
                'payment_ttl_sec': 300,
                'payment_scheme': 'yandex_withhold',
            },
        ),
        pytest.param(
            'merchant-id-2',
            200,
            {
                'merchant_name': 'Pyaterochka',
                'enable_balance_check_on_pay': True,
                'enable_requisites_check_on_draft': False,
                'payment_scheme': 'remittance',
            },
        ),
        pytest.param(
            'merchant-id-3',
            404,
            {'code': 'merchant_not_found', 'message': 'Merchant not found'},
        ),
    ],
)
async def test_merchant_get(
        taxi_merchant_profiles, merchant_id, status, expected_response,
):
    response = await taxi_merchant_profiles.get(
        '/internal/merchant-profiles/v1/merchant',
        params={'merchant_id': merchant_id},
    )

    assert response.status == status
    assert response.json() == expected_response
