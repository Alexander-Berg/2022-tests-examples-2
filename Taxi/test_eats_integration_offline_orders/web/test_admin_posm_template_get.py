import http

import pytest

from test_eats_integration_offline_orders import conftest


@pytest.mark.parametrize(
    ('params', 'expected_code', 'expected_response'),
    (
        pytest.param(
            {'template_id': 1},
            http.HTTPStatus.OK,
            conftest.ADMIN_POSM_TEMPLATE_1,
            id='OK',
        ),
        pytest.param(
            {'template_id': 2},
            http.HTTPStatus.OK,
            conftest.ADMIN_POSM_TEMPLATE_2,
            id='OK-with-settings',
        ),
        pytest.param(
            {'template_id': 3},
            http.HTTPStatus.NOT_FOUND,
            {'code': 'not_found', 'message': 'template not found'},
            id='deleted',
        ),
        pytest.param(
            {'template_id': 4},
            http.HTTPStatus.OK,
            conftest.ADMIN_POSM_TEMPLATE_4,
            id='OK-restaurant',
        ),
        pytest.param(
            {'template_id': 100500},
            http.HTTPStatus.NOT_FOUND,
            {'code': 'not_found', 'message': 'template not found'},
            id='not-found',
        ),
    ),
)
@pytest.mark.pgsql(
    'eats_integration_offline_orders',
    files=[
        'restaurants.sql',
        'posm_templates.sql',
        'restaurants_posm_templates.sql',
    ],
)
async def test_admin_posm_template_get(
        taxi_eats_integration_offline_orders_web,
        params,
        expected_code,
        expected_response,
):
    response = await taxi_eats_integration_offline_orders_web.get(
        '/admin/v1/posm/template', params=params,
    )
    body = await response.json()
    assert response.status == expected_code
    assert body == expected_response
