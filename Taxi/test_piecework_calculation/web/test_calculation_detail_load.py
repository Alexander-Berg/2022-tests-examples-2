import pytest


@pytest.mark.parametrize(
    'data, expected_status, expected_response',
    [
        (
            {
                'start_date': '2020-01-05',
                'stop_date': '2020-01-10',
                'tariff_type': 'support-taxi',
                'login': 'first',
                'country': 'rus',
            },
            200,
            {
                'login': 'first',
                'start_date': '2020-01-05',
                'stop_date': '2020-01-10',
                'details': [
                    {
                        'line': '2_line',
                        'actions': [
                            {
                                'cost_condition_key': 'test_action_key_2',
                                'cost': 3.0,
                                'count': 8,
                            },
                        ],
                    },
                ],
            },
        ),
        (
            {
                'start_date': '2020-02-05',
                'stop_date': '2020-02-10',
                'tariff_type': 'support-taxi',
                'login': 'first',
                'country': 'rus',
            },
            200,
            {
                'login': 'first',
                'start_date': '2020-02-05',
                'stop_date': '2020-02-10',
                'details': [
                    {
                        'line': 'calltaxi_common',
                        'actions': [
                            {
                                'cost_condition_key': 'test_action_key_2',
                                'cost': 2.0,
                                'count': 2,
                            },
                        ],
                    },
                ],
            },
        ),
        (
            {
                'start_date': '2020-02-25',
                'stop_date': '2020-03-01',
                'tariff_type': 'support-taxi',
                'login': 'first',
                'country': 'rus',
            },
            200,
            {
                'login': 'first',
                'start_date': '2020-02-25',
                'stop_date': '2020-03-01',
                'details': [],
            },
        ),
        (
            {
                'start_date': '2020-02-05',
                'stop_date': '2020-02-20',
                'tariff_type': 'support-taxi',
                'login': 'first',
                'country': 'rus',
            },
            200,
            {
                'login': 'first',
                'start_date': '2020-02-05',
                'stop_date': '2020-02-20',
                'details': [
                    {
                        'line': 'calltaxi_common',
                        'actions': [
                            {
                                'cost_condition_key': 'test_action_key_2',
                                'cost': 2.0,
                                'count': 4,
                            },
                        ],
                    },
                ],
            },
        ),
        (
            {
                'start_date': '2020-01-01',
                'stop_date': '2020-01-05',
                'tariff_type': 'support-taxi',
                'login': 'not_in_db',
                'country': 'rus',
            },
            200,
            {
                'login': 'not_in_db',
                'start_date': '2020-01-01',
                'stop_date': '2020-01-05',
                'details': [],
            },
        ),
        (
            {
                'start_date': '2021-01-01',
                'stop_date': '2022-01-05',
                'tariff_type': 'support-taxi',
                'login': 'first',
                'country': 'rus',
            },
            200,
            {
                'login': 'first',
                'start_date': '2021-01-01',
                'stop_date': '2022-01-05',
                'details': [],
            },
        ),
        (
            {
                'start_date': '2020-01-01',
                'stop_date': '2020-01-05',
                'tariff_type': 'support-taxi',
                'login': 'first',
                'country': 'rus',
            },
            200,
            {
                'login': 'first',
                'start_date': '2020-01-01',
                'stop_date': '2020-01-05',
                'details': [
                    {
                        'line': '1_line',
                        'actions': [
                            {
                                'cost_condition_key': 'test_action_key',
                                'cost': 1.0,
                                'count': 32,
                            },
                            {
                                'cost_condition_key': 'test_action_key_1',
                                'cost': 0.2,
                                'count': 12,
                            },
                            {
                                'cost_condition_key': 'test_action_key_2',
                                'cost': 0.01,
                                'count': 10,
                            },
                        ],
                    },
                    {
                        'line': '2_line',
                        'actions': [
                            {
                                'cost_condition_key': 'test_action_key_2',
                                'cost': 3.0,
                                'count': 8,
                            },
                        ],
                    },
                    {
                        'line': 'calltaxi_common',
                        'actions': [
                            {
                                'cost_condition_key': 'test_action_key_1',
                                'cost': 3.0,
                                'count': 3,
                            },
                            {
                                'cost_condition_key': 'test_action_key_2',
                                'cost': 2.0,
                                'count': 2,
                            },
                        ],
                    },
                ],
            },
        ),
        (
            {
                'start_date': '2020-01-01',
                'stop_date': '2020-01-05',
                'tariff_type': 'support-taxi',
                'login': 'second',
                'country': 'rus',
            },
            200,
            {
                'login': 'second',
                'start_date': '2020-01-01',
                'stop_date': '2020-01-05',
                'details': [
                    {
                        'line': 'calltaxi_common',
                        'actions': [
                            {
                                'cost_condition_key': 'test_action_key_2',
                                'cost': 2.0,
                                'count': 6,
                            },
                        ],
                    },
                ],
            },
        ),
    ],
)
async def test_calculation_detail_load(
        web_app_client, data, expected_status, expected_response,
):
    response = await web_app_client.post(
        '/v1/calculation/detail/load', json=data,
    )
    assert response.status == expected_status
    resp = await response.json()
    for line in resp['details']:
        line['actions'] = sorted(
            line['actions'], key=lambda x: x['count'], reverse=True,
        )
    assert resp == expected_response
