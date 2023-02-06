import http

import pytest


@pytest.mark.parametrize(
    'operation_id, expected_status, expected_content',
    (
        pytest.param(
            '5f9b08b19da21d52ed964473',
            http.HTTPStatus.OK,
            {
                'task_id': '5f9b08b19da21d52ed964473',
                'task': {
                    'rush_hours': {
                        'data': {},
                        'percentile': 0.65,
                        'surge_pwr': 2.2,
                        'distance_threshold': 0.3,
                    },
                    'polygons': {
                        'data': [],
                        'surge_weight_power': 1.3,
                        'cost_weight_power': 0,
                        'eps': 0.028,
                        'min_samples': 1,
                        'cluster_percent_of_sample': 0.03,
                        'alpha_param': 0.007,
                        'surge_threshold': 1.2,
                    },
                    'draft_rules': [],
                    'data_loader': {
                        'date_from': '2020-11-03 10:25:32',
                        'date_to': '2020-11-17 10:25:32',
                        'tariff_zones': ['moscow'],
                        'tariffs': ['econom'],
                    },
                    'budget': {'how_apply': 'driver', 'budget_scale': 1},
                    'tag_conf': {'main_tag': '', 'current_rules_tags': ['']},
                },
            },
        ),
        pytest.param(
            '5f9b08b19da21d53ed964474',
            http.HTTPStatus.NOT_FOUND,
            {
                'code': 'NotFound',
                'message': 'task for task 5f9b08b19da21d53ed964474 not found',
            },
        ),
    ),
)
@pytest.mark.pgsql(
    'operation_calculations', files=['pg_subvention_task_status.sql'],
)
async def test_v1_geosubventions_tasks_task_id_get(
        web_app_client,
        operation_id,
        expected_status,
        expected_content,
        caplog,
):
    response = await web_app_client.get(
        f'/v1/geosubventions/tasks/{operation_id}/',
    )
    assert response.status == expected_status, await response.text()
    assert await response.json() == expected_content
