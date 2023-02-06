import pytest


@pytest.mark.parametrize(
    ('params', 'expected_status', 'expected_result'),
    [
        pytest.param(
            {
                'box_id': '00000000-0000-0000-0000-000000000001',
                'date_from': '1970-01-01 0:01',
                'date_to': '2970-01-01 0:01',
            },
            200,
            {
                'transactions': [
                    {
                        'datetime': '2021-01-27T16:45:00+03:00',
                        'amount': '100',
                        'direction': 'outgoing',
                        'partner': '00000000-0000-0000-1000-000000000001',
                        'status': 'success',
                    },
                    {
                        'datetime': '2021-01-27T16:35:00+03:00',
                        'amount': '150',
                        'direction': 'incoming',
                        'status': 'success',
                    },
                    {
                        'datetime': '2021-01-27T16:30:00+03:00',
                        'amount': '100',
                        'direction': 'outgoing',
                        'partner': '00000000-0000-0000-1000-000000000001',
                        'status': 'in-progress',
                    },
                ],
            },
            id='success',
        ),
    ],
)
@pytest.mark.pgsql('eats_tips_payments', files=['pg_eats_tips.sql'])
async def test_money_box_transactions(
        taxi_eats_tips_payments_web, params, expected_status, expected_result,
):
    response = await taxi_eats_tips_payments_web.get(
        '/internal/v1/money-box/transactions', params=params,
    )
    assert response.status == expected_status
    content = await response.json()
    assert content == expected_result
