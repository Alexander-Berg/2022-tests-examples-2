import pytest


@pytest.mark.parametrize(
    'params, expected_status, expected_result',
    [
        (
            {'users': '6,4', 'tz': '+5:00'},
            200,
            {
                'aggregate': [
                    {'date': '2021-09-16', 'count': 3, 'money_total': 3000.0},
                    {'date': '1969-12-31', 'count': 1, 'money_total': 4000.0},
                ],
            },
        ),
    ],
)
@pytest.mark.mysql('chaevieprosto', files=['mysql_chaevieprosto.sql'])
async def test_get_payments(
        taxi_eats_tips_payments_web, params, expected_status, expected_result,
):
    response = await taxi_eats_tips_payments_web.get(
        '/internal/v1/payments/total/by-dates', params=params,
    )
    assert response.status == expected_status
    content = await response.json()
    assert content == expected_result
