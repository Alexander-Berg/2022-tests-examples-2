import pytest

from test_eats_tips_payments import conftest


@pytest.mark.parametrize(
    ('params', 'expected_status', 'expected_result'),
    [
        (
            {
                'recipient_ids': conftest.PARTNER_ID_1,
                'places': conftest.PLACE_ID_1,
                'tz': '+05:00',
                'chunking': 'day',
                'date_from': '2021-10-10 00:00:00+05:00',
                'date_to': '2021-10-11 00:00:00+05:00',
            },
            200,
            {
                'aggregate': [
                    {
                        'count': 5,
                        'date_from': '2021-10-10',
                        'date_to': '2021-10-10',
                        'money_total': 500.0,
                        'place_id': conftest.PLACE_ID_1,
                    },
                ],
            },
        ),
        (
            {
                'recipient_ids': conftest.PARTNER_ID_1,
                'places': conftest.PLACE_ID_1,
                'tz': '+05:00',
                'chunking': 'week',
                'date_from': '2021-10-10 00:00:00+5:00',
                'date_to': '2021-10-11 00:00:00+5:00',
            },
            200,
            {
                'aggregate': [
                    {
                        'count': 5,
                        'date_from': '2021-10-04',  # monday
                        'date_to': '2021-10-10',  # sunday
                        'money_total': 500.0,
                        'place_id': conftest.PLACE_ID_1,
                    },
                ],
            },
        ),
        (
            {
                'recipient_ids': conftest.PARTNER_ID_1,
                'places': conftest.PLACE_ID_1,
                'tz': '+5:00',
                'chunking': 'month',
                'date_from': '2021-10-10 00:00:00+05:00',
                'date_to': '2021-10-11 00:00:00+05:00',
            },
            200,
            {
                'aggregate': [
                    {
                        'count': 5,
                        'date_from': '2021-10-01',
                        'date_to': '2021-10-31',
                        'money_total': 500.0,
                        'place_id': conftest.PLACE_ID_1,
                    },
                ],
            },
        ),
        (
            {
                'recipient_ids': conftest.PARTNER_ID_1,
                'places': conftest.PLACE_ID_1,
                'tz': '+5:00',
                'chunking': 'year',
                'date_from': '2021-10-10 00:00:00+05:00',
                'date_to': '2021-10-11 00:00:00+05:00',
            },
            200,
            {
                'aggregate': [
                    {
                        'count': 5,
                        'date_from': '2021-01-01',
                        'date_to': '2021-12-31',
                        'money_total': 500.0,
                        'place_id': conftest.PLACE_ID_1,
                    },
                ],
            },
        ),
    ],
)
@pytest.mark.pgsql('eats_tips_payments', files=['pg_eats_tips.sql'])
async def test_get_payments(
        taxi_eats_tips_payments_web, params, expected_status, expected_result,
):
    response = await taxi_eats_tips_payments_web.get(
        '/internal/v1/payments/total/by-dates-and-place', params=params,
    )
    assert response.status == expected_status
    content = await response.json()
    assert content == expected_result
