# flake8: noqa
# pylint: disable=redefined-outer-name
import pytest

from test_pricing_modifications_validator.plugins.mock_pricing_admin import (
    mock_pricing_admin,
)


@pytest.mark.pgsql(
    'pricing_modifications_validator', files=['pg_test_validation.sql'],
)
async def test_unexistent_task(web_app_client, load_json):
    query = {'id': 42}
    response = await web_app_client.get('/v1/task_result', params=query)
    assert response.status == 404


@pytest.mark.pgsql(
    'pricing_modifications_validator', files=['pg_test_validation.sql'],
)
@pytest.mark.parametrize(
    'task_id, results, expected_state',
    [
        (1, [], 'in_progress'),
        (
            2,
            [
                {
                    'test_name': 'nan_test',
                    'test_result': 'error',
                    'point': {'Detected division by zero in variable 0': 0},
                },
            ],
            'finished',
        ),
        (
            3,
            [
                {
                    'test_name': 'nan_test',
                    'point': {
                        'Detected division by zero in '
                        'variable ride.price.distance': 0,
                    },
                    'test_result': 'error',
                },
            ],
            'in_progress',
        ),
    ],
)
async def test_validation(
        web_app_client, task_id, results, expected_state, load_json,
):
    query = {'id': task_id}
    response = await web_app_client.get('/v1/task_result', params=query)
    assert response.status == 200
    response_data = await response.json()
    assert response_data['results'] == results
    assert response_data['done'] == expected_state


@pytest.mark.pgsql(
    'pricing_modifications_validator', files=['pg_test_validation.sql'],
)
@pytest.mark.parametrize(
    'task_ids, expected_response',
    [
        (
            [1, 2, 3, 42],
            {
                'items': [
                    {'id': 1, 'done': 'in_progress'},
                    {
                        'id': 2,
                        'done': 'finished',
                        'details': {
                            'status': 'error',
                            'errors': [
                                'Detected division by zero in variable 0',
                            ],
                        },
                    },
                    {'id': 3, 'done': 'in_progress'},
                ],
            },
        ),
    ],
)
async def test_v1_bulk_task_result(
        web_app_client, task_ids, expected_response,
):
    body = {'ids': task_ids}
    response = await web_app_client.post('/v1/bulk_task_result', json=body)
    assert response.status == 200
    response_data = await response.json()
    assert response_data == expected_response
