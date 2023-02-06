import http

import pytest


@pytest.mark.parametrize(
    ('params', 'expected_code', 'expected_response'),
    (
        pytest.param(
            {'generation_id': 1},
            http.HTTPStatus.BAD_REQUEST,
            {
                'code': 'bad_request',
                'message': (
                    'generation is not ready for download, actual status: '
                    'in_progress'
                ),
            },
            id='not-ready',
        ),
        pytest.param(
            {'generation_id': 2},
            http.HTTPStatus.OK,
            {
                'errors': [
                    'following tables were deleted: 2 (table_uuid__2)',
                    'uuid of following tables were changed: 1 '
                    '(table_uuid__1 -> uuid__1)',
                    'pos_name of following tables were changed: 1 '
                    '(1 -> table_id__1)',
                ],
            },
            id='errors',
        ),
        pytest.param(
            {'generation_id': 4},
            http.HTTPStatus.BAD_REQUEST,
            {'code': 'bad_request', 'message': 'generation already cleaned'},
            id='deleted',
        ),
        pytest.param(
            {'generation_id': 5}, http.HTTPStatus.OK, {'errors': []}, id='OK',
        ),
        pytest.param(
            {'generation_id': 100500},
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
async def test_admin_posm_generation_check(
        taxi_eats_integration_offline_orders_web,
        params,
        expected_code,
        expected_response,
):
    response = await taxi_eats_integration_offline_orders_web.get(
        '/admin/v1/posm/generation/check', params=params,
    )
    body = await response.json()
    assert response.status == expected_code
    assert body == expected_response
