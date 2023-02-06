import http

import pytest


@pytest.mark.config(
    PIECEWORK_CALCULATION_QUALITY_CALCULATION_PARAMETERS={
        'marks_weight': 0.4,
        'claim_count_limit': 10,
    },
)
@pytest.mark.parametrize(
    'request_data, expected_data',
    [
        (
            {
                'operator_login': 'random_support',
                'start_date': '2022-02-01',
                'stop_date': '2022-02-10',
            },
            {'csat': 85.0, 'quality': 81.0},
        ),
        (
            {
                'operator_login': 'random_support',
                'start_date': '2022-02-05',
                'stop_date': '2022-02-06',
            },
            {'csat': 90.0, 'quality': 80.0},
        ),
        (
            {
                'operator_login': 'support_without_quality',
                'start_date': '2022-02-05',
                'stop_date': '2022-02-06',
            },
            {'csat': 85.0, 'quality': 0},
        ),
        (
            {
                'operator_login': 'support_without_csat',
                'start_date': '2022-02-05',
                'stop_date': '2022-02-06',
            },
            {'csat': 0, 'quality': 35.0},
        ),
        (
            {
                'operator_login': 'support_with_zero_cnt',
                'start_date': '2022-02-05',
                'stop_date': '2022-02-06',
            },
            {'csat': 0, 'quality': 0},
        ),
        (
            {
                'operator_login': 'non_existent_login',
                'start_date': '2022-02-05',
                'stop_date': '2022-02-06',
            },
            {'csat': 0, 'quality': 0},
        ),
        (
            {
                'operator_login': 'random_support',
                'start_date': '2022-02-05',
                'stop_date': '2022-02-05',
            },
            {'csat': 0, 'quality': 0},
        ),
        (
            {
                'operator_login': 'random_support',
                'start_date': '2022-03-01',
                'stop_date': '2022-03-31',
            },
            {'csat': 0, 'quality': 0},
        ),
    ],
)
async def test_get_green(web_app_client, request_data, expected_data):
    response = await web_app_client.get(
        '/v1/eats-support-metrics', params=request_data,
    )
    assert response.status == http.HTTPStatus.OK
    response_data = await response.json()
    assert response_data == expected_data
