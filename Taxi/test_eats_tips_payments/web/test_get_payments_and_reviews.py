import pytest

from test_eats_tips_payments import conftest


@pytest.mark.parametrize(
    ('params', 'expected_status', 'expected_result'),
    [
        (
            {
                'recipient_ids': conftest.PARTNER_ID_1,
                'date_from': '2021-10-10 00:00:00Z',
                'date_to': '2021-10-11 00:00:00Z',
            },
            200,
            {
                'transactions': [
                    {
                        'recipient_id': 'f907a11d-e1aa-4b2e-8253-069c58801727',
                        'recipient_type': 'partner',
                        'datetime': '2021-10-10T09:00:00+03:00',
                        'place_id': 'eef266b2-09b3-4218-8da9-c90928608d97',
                        'amount': 100.0,
                        'rating': 5,
                        'review': 'Text review 46',
                        'quick_choices': [],
                    },
                    {
                        'recipient_id': 'f907a11d-e1aa-4b2e-8253-069c58801727',
                        'recipient_type': 'partner',
                        'datetime': '2021-10-10T08:00:00+03:00',
                        'place_id': 'eef266b2-09b3-4218-8da9-c90928608d97',
                        'amount': 100.0,
                        'rating': 4,
                        'review': 'Text review 45',
                        'quick_choices': [],
                    },
                    {
                        'recipient_id': 'f907a11d-e1aa-4b2e-8253-069c58801727',
                        'recipient_type': 'partner',
                        'datetime': '2021-10-10T07:30:00+03:00',
                        'place_id': 'eef266b2-09b3-4218-8da9-c90928608d97',
                        'rating': 4,
                        'review': 'Text review 44',
                        'quick_choices': ['Сервис'],
                    },
                    {
                        'recipient_id': 'f907a11d-e1aa-4b2e-8253-069c58801727',
                        'recipient_type': 'partner',
                        'datetime': '2021-10-10T07:00:00+03:00',
                        'place_id': 'eef266b2-09b3-4218-8da9-c90928608d97',
                        'amount': 100.0,
                    },
                    {
                        'recipient_id': 'f907a11d-e1aa-4b2e-8253-069c58801727',
                        'recipient_type': 'partner',
                        'datetime': '2021-10-10T06:00:00+03:00',
                        'place_id': 'eef266b2-09b3-4218-8da9-c90928608d97',
                        'amount': 100.0,
                    },
                    {
                        'recipient_id': 'f907a11d-e1aa-4b2e-8253-069c58801727',
                        'recipient_type': 'partner',
                        'datetime': '2021-10-10T05:00:00+03:00',
                        'place_id': 'eef266b2-09b3-4218-8da9-c90928608d97',
                        'amount': 100.0,
                    },
                ],
            },
        ),
        ({'recipient_ids': conftest.NOT_FOUND_ID}, 200, {'transactions': []}),
        (
            {
                'recipient_ids': conftest.PARTNER_ID_1,
                'date_from': '2021-10-10 00:00:00Z',
                'date_to': '2021-10-11 00:00:00Z',
                'rating_from': 3,
            },
            200,
            {
                'transactions': [
                    {
                        'recipient_id': 'f907a11d-e1aa-4b2e-8253-069c58801727',
                        'recipient_type': 'partner',
                        'datetime': '2021-10-10T09:00:00+03:00',
                        'place_id': 'eef266b2-09b3-4218-8da9-c90928608d97',
                        'amount': 100.0,
                        'rating': 5,
                        'review': 'Text review 46',
                        'quick_choices': [],
                    },
                    {
                        'recipient_id': 'f907a11d-e1aa-4b2e-8253-069c58801727',
                        'recipient_type': 'partner',
                        'datetime': '2021-10-10T08:00:00+03:00',
                        'place_id': 'eef266b2-09b3-4218-8da9-c90928608d97',
                        'amount': 100.0,
                        'rating': 4,
                        'review': 'Text review 45',
                        'quick_choices': [],
                    },
                    {
                        'recipient_id': 'f907a11d-e1aa-4b2e-8253-069c58801727',
                        'recipient_type': 'partner',
                        'datetime': '2021-10-10T07:30:00+03:00',
                        'place_id': 'eef266b2-09b3-4218-8da9-c90928608d97',
                        'rating': 4,
                        'review': 'Text review 44',
                        'quick_choices': ['Сервис'],
                    },
                ],
            },
        ),
        (
            {
                'recipient_ids': conftest.PARTNER_ID_1,
                'date_from': '2021-10-10 04:30:00Z',
                'date_to': '2021-10-11 00:00:00Z',
            },
            200,
            {
                'transactions': [
                    {
                        'recipient_id': 'f907a11d-e1aa-4b2e-8253-069c58801727',
                        'recipient_type': 'partner',
                        'datetime': '2021-10-10T09:00:00+03:00',
                        'place_id': 'eef266b2-09b3-4218-8da9-c90928608d97',
                        'amount': 100.0,
                        'rating': 5,
                        'review': 'Text review 46',
                        'quick_choices': [],
                    },
                    {
                        'recipient_id': 'f907a11d-e1aa-4b2e-8253-069c58801727',
                        'recipient_type': 'partner',
                        'datetime': '2021-10-10T08:00:00+03:00',
                        'place_id': 'eef266b2-09b3-4218-8da9-c90928608d97',
                        'amount': 100.0,
                        'rating': 4,
                        'review': 'Text review 45',
                        'quick_choices': [],
                    },
                    {
                        'recipient_id': 'f907a11d-e1aa-4b2e-8253-069c58801727',
                        'recipient_type': 'partner',
                        'datetime': '2021-10-10T07:30:00+03:00',
                        'place_id': 'eef266b2-09b3-4218-8da9-c90928608d97',
                        'rating': 4,
                        'review': 'Text review 44',
                        'quick_choices': ['Сервис'],
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
        '/internal/v1/payments-and-reviews', params=params,
    )
    assert response.status == expected_status
    content = await response.json()
    assert content == expected_result
