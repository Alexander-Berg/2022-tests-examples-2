import pytest

from test_eats_tips_payments import conftest


@pytest.mark.parametrize(
    ('params', 'expected_status', 'expected_result'),
    [
        (
            {
                'recipient_ids': conftest.PARTNER_ID_1,
                'date_from': '2021-10-10',
                'date_to': '2021-10-11',
                'tz': '+03:00',
            },
            200,
            {
                'aggregate': [
                    {
                        'date_from': '2021-10-10',
                        'date_to': '2021-10-10',
                        'total_count': 6,
                        'reviews_count': 3,
                        'payments_count': 5,
                        'payments_sum': 500.0,
                    },
                ],
            },
        ),
        (
            {'recipient_ids': conftest.NOT_FOUND_ID, 'tz': '+03:00'},
            200,
            {'aggregate': []},
        ),
        (
            {
                'recipient_ids': conftest.PARTNER_ID_1,
                'date_from': '2021-10-10',
                'date_to': '2021-10-11',
                'rating_from': 3,
                'tz': '+03:00',
            },
            200,
            {
                'aggregate': [
                    {
                        'date_from': '2021-10-10',
                        'date_to': '2021-10-10',
                        'total_count': 3,
                        'reviews_count': 3,
                        'payments_count': 2,
                        'payments_sum': 200.0,
                    },
                ],
            },
        ),
        (
            {
                'recipient_ids': conftest.PARTNER_ID_1,
                'date_from': '2021-10-10',
                'date_to': '2021-10-10',
                'places': 'eef266b2-09b3-4218-8da9-c90928608d97',
                'tz': '+03:00',
            },
            200,
            {
                'aggregate': [
                    {
                        'date_from': '2021-10-10',
                        'date_to': '2021-10-10',
                        'total_count': 6,
                        'reviews_count': 3,
                        'payments_count': 5,
                        'payments_sum': 500.0,
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
        '/internal/v1/payments-and-reviews/total/by-dates', params=params,
    )
    assert response.status == expected_status
    content = await response.json()
    assert content == expected_result
