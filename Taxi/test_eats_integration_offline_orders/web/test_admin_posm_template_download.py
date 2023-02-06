import http

import pytest


@pytest.mark.parametrize(
    ('params', 'expected_code'),
    (
        pytest.param({'template_id': 1}, http.HTTPStatus.OK, id='OK'),
        pytest.param(
            {'template_id': 100500}, http.HTTPStatus.NOT_FOUND, id='not-found',
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
async def test_admin_posm_template_download(
        taxi_eats_integration_offline_orders_web, params, expected_code,
):
    response = await taxi_eats_integration_offline_orders_web.get(
        '/admin/v1/posm/template/download', params=params,
    )
    assert response.status == expected_code
    if expected_code is not http.HTTPStatus.OK:
        return
    assert 'X-Accel-Redirect' in response.headers
