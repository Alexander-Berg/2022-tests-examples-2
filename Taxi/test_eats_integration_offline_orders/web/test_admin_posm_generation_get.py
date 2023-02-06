import http

import pytest


@pytest.mark.parametrize(
    ('generation_id', 'expected_code', 'expected_response'),
    (
        pytest.param(
            1,
            http.HTTPStatus.OK,
            {
                'generation_id': 1,
                'author': 'username',
                'created_at': '2022-05-17 17:00:00',
                'place_id': 'place_id__1',
                'status': 'in_progress',
                'tables': [
                    {
                        'id': 1,
                        'table_pos_name': 'table_id__1',
                        'uuid': 'uuid__1',
                    },
                ],
                'templates': [{'id': 1}, {'id': 2}],
            },
            id='OK-few-templates',
        ),
        pytest.param(
            2,
            http.HTTPStatus.OK,
            {
                'generation_id': 2,
                'author': 'another_user',
                'created_at': '2022-05-17 18:00:00',
                'place_id': 'place_id__1',
                'status': 'done',
                'tables': [
                    {'id': 1, 'table_pos_name': '1', 'uuid': 'table_uuid__1'},
                    {'id': 2, 'table_pos_name': '2', 'uuid': 'table_uuid__2'},
                ],
                'templates': [{'id': 1}],
            },
            id='OK-one-template',
        ),
        pytest.param(
            3,
            http.HTTPStatus.OK,
            {
                'generation_id': 3,
                'author': 'username',
                'created_at': '2022-05-17 19:00:00',
                'place_id': 'place_id__1',
                'status': 'created',
                'tables': [
                    {
                        'id': 2,
                        'table_pos_name': 'table_id__2',
                        'uuid': 'uuid__2',
                    },
                ],
                'templates': [{'id': 2}],
            },
            id='OK-one-table',
        ),
        pytest.param(
            100500,
            http.HTTPStatus.NOT_FOUND,
            {'code': 'not_found', 'message': 'generation not found'},
            id='not-found',
        ),
    ),
)
@pytest.mark.pgsql(
    'eats_integration_offline_orders',
    files=[
        'restaurants.sql',
        'tables.sql',
        'posm_templates.sql',
        'restaurants_posm_templates.sql',
        'posm_generations.sql',
        'posm_generations_templates.sql',
    ],
)
async def test_admin_posm_generation_get(
        taxi_eats_integration_offline_orders_web,
        generation_id,
        expected_code,
        expected_response,
):
    response = await taxi_eats_integration_offline_orders_web.get(
        '/admin/v1/posm/generation', params={'generation_id': generation_id},
    )
    body = await response.json()
    assert response.status == expected_code
    assert body == expected_response
