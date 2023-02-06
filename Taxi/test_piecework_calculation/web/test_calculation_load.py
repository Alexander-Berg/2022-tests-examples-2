import datetime

import pytest

NOW = datetime.datetime(2020, 1, 1, 0, 0)


@pytest.mark.now(NOW.isoformat())
@pytest.mark.parametrize(
    'data,expected_status,expected_response',
    [
        (
            {
                'start_date': '2020-01-01',
                'stop_date': '2020-01-05',
                'tariff_type': 'support-taxi',
                'logins': ['first'],
                'country': 'rus',
            },
            200,
            {
                'calculation': {'commited': False},
                'logins': [
                    {
                        'login': 'first',
                        'date': '2020-01-03',
                        'bo': {
                            'daytime_cost': 10.0,
                            'night_cost': 5.0,
                            'holidays_daytime_cost': 8.0,
                            'holidays_night_cost': 1.0,
                        },
                    },
                ],
            },
        ),
        (
            {
                'start_date': '2020-01-01',
                'stop_date': '2020-01-05',
                'tariff_type': 'support-taxi',
                'logins': ['first', 'second', 'third', 'fourth'],
                'country': 'rus',
            },
            200,
            {
                'calculation': {'commited': False},
                'logins': [
                    {
                        'login': 'first',
                        'date': '2020-01-03',
                        'bo': {
                            'daytime_cost': 10.0,
                            'night_cost': 5.0,
                            'holidays_daytime_cost': 8.0,
                            'holidays_night_cost': 1.0,
                        },
                    },
                    {
                        'bo': {
                            'daytime_cost': 120.0,
                            'holidays_daytime_cost': 100.0,
                            'holidays_night_cost': 30.0,
                            'night_cost': 70.0,
                        },
                        'date': '2020-01-01',
                        'login': 'fourth',
                    },
                    {
                        'bo': {
                            'daytime_cost': 24.0,
                            'holidays_daytime_cost': 20.0,
                            'holidays_night_cost': 6.0,
                            'night_cost': 14.0,
                        },
                        'date': '2020-01-02',
                        'login': 'fourth',
                    },
                    {
                        'bo': {
                            'daytime_cost': 12.0,
                            'holidays_daytime_cost': 10.0,
                            'holidays_night_cost': 3.0,
                            'night_cost': 7.0,
                        },
                        'date': '2020-01-04',
                        'login': 'second',
                    },
                    {
                        'bo': {
                            'daytime_cost': 120.0,
                            'holidays_daytime_cost': 100.0,
                            'holidays_night_cost': 30.0,
                            'night_cost': 70.0,
                        },
                        'date': '2020-01-01',
                        'login': 'third',
                    },
                    {
                        'bo': {
                            'daytime_cost': 24.0,
                            'holidays_daytime_cost': 20.0,
                            'holidays_night_cost': 6.0,
                            'night_cost': 14.0,
                        },
                        'date': '2020-01-02',
                        'login': 'third',
                    },
                ],
            },
        ),
        (
            {
                'start_date': '2020-01-01',
                'stop_date': '2020-01-05',
                'tariff_type': 'support-taxi',
                'logins': ['fourth'],
                'country': 'rus',
            },
            200,
            {
                'calculation': {'commited': False},
                'logins': [
                    {
                        'bo': {
                            'daytime_cost': 120.0,
                            'holidays_daytime_cost': 100.0,
                            'holidays_night_cost': 30.0,
                            'night_cost': 70.0,
                        },
                        'date': '2020-01-01',
                        'login': 'fourth',
                    },
                    {
                        'bo': {
                            'daytime_cost': 24.0,
                            'holidays_daytime_cost': 20.0,
                            'holidays_night_cost': 6.0,
                            'night_cost': 14.0,
                        },
                        'date': '2020-01-02',
                        'login': 'fourth',
                    },
                ],
            },
        ),
        (
            {
                'start_date': '2020-01-01',
                'stop_date': '2020-01-05',
                'tariff_type': 'support-taxi',
                'logins': ['fifth'],
                'country': 'rus',
            },
            200,
            {
                'calculation': {'commited': False},
                'logins': [
                    {
                        'bo': {
                            'daytime_cost': 120.0,
                            'holidays_daytime_cost': 100.0,
                            'holidays_night_cost': 30.0,
                            'night_cost': 70.0,
                        },
                        'date': '2020-01-01',
                        'login': 'fifth',
                    },
                    {
                        'bo': {
                            'daytime_cost': 12.0,
                            'holidays_daytime_cost': 10.0,
                            'holidays_night_cost': 3.0,
                            'night_cost': 7.0,
                        },
                        'date': '2020-01-02',
                        'login': 'fifth',
                    },
                ],
            },
        ),
    ],
)
async def test_load_calculation_daily(
        web_app_client, data, expected_status, expected_response,
):
    response = await web_app_client.post(
        '/v1/calculation/daily/load', json=data,
    )
    assert response.status == expected_status
    if expected_status != 200:
        return

    content = await response.json()
    sorted(content['logins'], key=lambda x: x['login'])
    assert content == expected_response


@pytest.mark.now(NOW.isoformat())
@pytest.mark.parametrize(
    'data,expected_status,expected_response',
    [
        (
            {
                'start_date': '2020-01-01',
                'stop_date': '2020-01-05',
                'tariff_type': 'support-taxi',
                'logins': ['first'],
                'country': 'rus',
            },
            200,
            {
                'calculation': {'commited': False},
                'logins': [
                    {
                        'login': 'first',
                        'bo': {
                            'daytime_cost': 15.0,
                            'night_cost': 7.0,
                            'holidays_daytime_cost': 10.0,
                            'holidays_night_cost': 1.0,
                        },
                        'benefits': 16.0,
                        'benefit_details': {
                            'benefits_per_bo': 0.5,
                            'discipline_ratio': 0.7,
                            'extra_custom_field': 'value',
                            'hour_cost': 14.0,
                            'hour_cost_ratio': 0.875,
                            'min_hour_cost': 10.0,
                            'plan_workshifts_duration_sec': 7200,
                            'rating': 0.7975,
                            'rating_pos': 2,
                            'rating_prcnt': 66.66666666666666,
                            'unified_qa_ratio': 0.8,
                            'workshifts_duration_sec': 3600,
                        },
                    },
                ],
            },
        ),
        (
            {
                'start_date': '2020-01-01',
                'stop_date': '2020-01-05',
                'tariff_type': 'support-taxi',
                'logins': ['first', 'second', 'third', 'fourth'],
                'country': 'rus',
            },
            200,
            {
                'calculation': {'commited': False},
                'logins': [
                    {
                        'benefit_details': {
                            'benefits_per_bo': 0.5,
                            'discipline_ratio': 0.7,
                            'extra_custom_field': 'value',
                            'hour_cost': 14.0,
                            'hour_cost_ratio': 0.875,
                            'min_hour_cost': 10.0,
                            'plan_workshifts_duration_sec': 7200,
                            'rating': 0.7975,
                            'rating_pos': 2,
                            'rating_prcnt': 66.66666666666666,
                            'unified_qa_ratio': 0.8,
                            'workshifts_duration_sec': 3600,
                        },
                        'benefits': 16.0,
                        'bo': {
                            'daytime_cost': 15.0,
                            'holidays_daytime_cost': 10.0,
                            'holidays_night_cost': 1.0,
                            'night_cost': 7.0,
                        },
                        'login': 'first',
                    },
                    {
                        'benefit_details': {},
                        'benefits': 0.0,
                        'bo': {
                            'daytime_cost': 55.0,
                            'holidays_daytime_cost': 1.0,
                            'holidays_night_cost': 111.0,
                            'night_cost': 177.0,
                        },
                        'login': 'fourth',
                    },
                    {
                        'benefit_details': {},
                        'benefits': 17.0,
                        'bo': {
                            'daytime_cost': 16.0,
                            'holidays_daytime_cost': 11.0,
                            'holidays_night_cost': 2.0,
                            'night_cost': 8.0,
                        },
                        'login': 'second',
                    },
                    {
                        'benefit_details': {},
                        'benefits': 0.0,
                        'bo': {
                            'daytime_cost': 5.0,
                            'holidays_daytime_cost': 0.0,
                            'holidays_night_cost': 11.0,
                            'night_cost': 17.0,
                        },
                        'login': 'third',
                    },
                ],
            },
        ),
        (
            {
                'start_date': '2020-01-01',
                'stop_date': '2020-01-05',
                'tariff_type': 'support-taxi',
                'logins': ['fourth'],
                'country': 'rus',
            },
            200,
            {
                'calculation': {'commited': False},
                'logins': [
                    {
                        'benefit_details': {},
                        'benefits': 0.0,
                        'bo': {
                            'daytime_cost': 55.0,
                            'holidays_daytime_cost': 1.0,
                            'holidays_night_cost': 111.0,
                            'night_cost': 177.0,
                        },
                        'login': 'fourth',
                    },
                ],
            },
        ),
        (
            {
                'start_date': '2020-01-01',
                'stop_date': '2020-01-05',
                'tariff_type': 'support-taxi',
                'logins': ['fifth'],
                'country': 'rus',
            },
            200,
            {
                'calculation': {'commited': False},
                'logins': [
                    {
                        'benefit_details': {},
                        'benefits': 0.0,
                        'bo': {
                            'daytime_cost': 55.0,
                            'holidays_daytime_cost': 1.0,
                            'holidays_night_cost': 111.0,
                            'night_cost': 177.0,
                        },
                        'login': 'fifth',
                    },
                ],
            },
        ),
    ],
)
async def test_load_calculation(
        web_app_client, data, expected_status, expected_response,
):
    response = await web_app_client.post('/v1/calculation/load', json=data)
    assert response.status == expected_status
    if expected_status != 200:
        return

    content = await response.json()
    assert content == expected_response
