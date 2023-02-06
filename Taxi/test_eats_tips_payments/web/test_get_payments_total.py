import pytest

from test_eats_tips_payments import conftest


@pytest.mark.parametrize(
    ('params', 'expected_status', 'expected_result'),
    [
        (
            {
                'recipient_ids': conftest.PARTNER_ID_1,
                'date_from': '2021-10-10 00:00:00Z',
                'to': '2021-10-11 00:00:00Z',
            },
            200,
            {'count': 5, 'money_total': 500.0},
        ),
        (
            {
                'recipient_ids': conftest.NOT_FOUND_ID,
                'date_from': '2021-10-10 00:00:00Z',
                'to': '2021-10-11 00:00:00Z',
            },
            200,
            {'count': 0, 'money_total': 0.0},
        ),
    ],
)
@pytest.mark.pgsql('eats_tips_payments', files=['pg_eats_tips.sql'])
async def test_get_payments(
        taxi_eats_tips_payments_web, params, expected_status, expected_result,
):
    response = await taxi_eats_tips_payments_web.get(
        '/internal/v1/payments/total', params=params,
    )
    assert response.status == expected_status
    content = await response.json()
    assert content == expected_result
