import pytest


@pytest.mark.parametrize(
    ('params', 'expected_status', 'expected_result'),
    [
        pytest.param(
            {'box_id': '00000000-0000-0000-0000-000000000001', 'tz': '+3:00'},
            200,
            {'aggregate': [{'date': '2021-01-27', 'money_total': '50'}]},
            id='success',
        ),
    ],
)
@pytest.mark.pgsql('eats_tips_payments', files=['pg_eats_tips.sql'])
async def test_money_box_transactions_total(
        taxi_eats_tips_payments_web, params, expected_status, expected_result,
):
    response = await taxi_eats_tips_payments_web.get(
        '/internal/v1/money-box/transactions/total', params=params,
    )
    assert response.status == expected_status
    content = await response.json()
    assert content == expected_result
