import pytest

from test_eats_tips_payments import conftest


@pytest.mark.parametrize(
    'params, expected_result',
    [
        ({'recipient_id': conftest.PARTNER_ID_2}, {'count': 1}),
        ({'recipient_id': conftest.PARTNER_ID_1}, {'count': 0}),
    ],
)
@pytest.mark.pgsql('eats_tips_payments', files=['pg_eats_tips.sql'])
async def test_payments_from_blacklisted_cards(
        taxi_eats_tips_payments_web, params, expected_result,
):
    response = await taxi_eats_tips_payments_web.get(
        '/internal/v1/payments/from-blacklisted-cards', params=params,
    )
    assert response.status == 200
    content = await response.json()
    assert content == expected_result
