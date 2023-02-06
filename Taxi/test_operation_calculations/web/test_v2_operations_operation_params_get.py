import http

import pytest


@pytest.mark.parametrize(
    'operation_id, expected_status, expected_content',
    (
        pytest.param(
            '61711eb7b7e4790047d4fe50',
            http.HTTPStatus.OK,
            {
                'task': {
                    'tariffs': ['econom'],
                    'end_date': '2021-10-08',
                    'start_date': '2021-10-01',
                    'tariff_zone': 'moscow',
                    'sub_operations': [
                        {
                            'week_days': ['mon', 'tue', 'wed', 'thu', 'fri'],
                            'alg_params': {'sub_gmv': 0.05},
                            'branding_type': 'unspecified',
                            'sub_operation_id': 1,
                        },
                    ],
                    'common_alg_params': {
                        'm': 5,
                        'a1': 3,
                        'a2': 4,
                        'step': 5,
                        'alg_type': 'stepwise',
                        'maxtrips': 30,
                        'has_commission': False,
                        'price_increase': 1,
                    },
                    'subvention_end_date': '2022-11-01',
                    'subvention_start_date': '2021-11-01',
                },
                'task_id': '61711eb7b7e4790047d4fe50',
                'task_status': 'CREATED',
            },
        ),
        pytest.param(
            '61711eb7b7e4790047d4fe53', http.HTTPStatus.NOT_FOUND, {},
        ),
    ),
)
@pytest.mark.pgsql(
    'operation_calculations',
    files=['pg_operations_status.sql', 'pg_operations_params.sql'],
)
async def test_v2_operations_operation_params_get(
        web_app_client, operation_id, expected_status, expected_content,
):
    response = await web_app_client.get(
        f'/v2/operations/operation_params/', params={'task_id': operation_id},
    )
    assert response.status == expected_status
    if expected_status == http.HTTPStatus.OK:
        assert await response.json() == expected_content
