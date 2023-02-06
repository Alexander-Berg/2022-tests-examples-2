import pytest


@pytest.mark.parametrize(
    'data, expected_response',
    [
        (
            {
                'start_date': '2022-01-01',
                'stop_date': '2022-01-10',
                'logins': ['ivanov', 'petrov', 'smirnov'],
            },
            {'logins': [], 'bo_rate': 1.0},
        ),
        (
            {
                'start_date': '2022-01-01',
                'stop_date': '2022-01-31',
                'logins': ['ivanov', 'petrov', 'smirnov'],
            },
            {'logins': [], 'bo_rate': 1.0},
        ),
        (
            {
                'start_date': '2022-02-01',
                'stop_date': '2022-02-10',
                'logins': ['ivanov', 'petrov', 'smirnov'],
            },
            {
                'logins': [
                    {
                        'login': 'ivanov',
                        'loans': [
                            {
                                'date_time': '2022-02-05T18:00:00+03:00',
                                'amount': 500.0,
                            },
                        ],
                    },
                    {
                        'login': 'petrov',
                        'loans': [
                            {
                                'date_time': '2022-02-01T03:00:00+03:00',
                                'amount': 300.0,
                            },
                        ],
                    },
                ],
                'bo_rate': 1.0,
            },
        ),
        (
            {
                'start_date': '2022-02-01',
                'stop_date': '2022-02-10',
                'logins': ['petrov', 'smirnov'],
            },
            {
                'logins': [
                    {
                        'login': 'petrov',
                        'loans': [
                            {
                                'date_time': '2022-02-01T03:00:00+03:00',
                                'amount': 300.0,
                            },
                        ],
                    },
                ],
                'bo_rate': 1.0,
            },
        ),
    ],
)
async def test_fetch_payday_loans(
        web_context, web_app_client, data, expected_response,
):
    response = await web_app_client.post('/v1/payday/loans/load', json=data)
    assert response.status == 200
    response_body = await response.json()
    assert response_body == expected_response
