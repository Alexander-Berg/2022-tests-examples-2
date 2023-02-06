import http

import pytest

from test_eats_integration_offline_orders import conftest


@pytest.mark.parametrize(
    ('params', 'expected_code', 'expected_response'),
    (
        pytest.param(
            {'visibility': 'global'},
            http.HTTPStatus.OK,
            {
                'templates': [
                    conftest.ADMIN_POSM_TEMPLATE_2,
                    conftest.ADMIN_POSM_TEMPLATE_1,
                ],
            },
            id='global',
        ),
        pytest.param(
            {'place_id': 'place_id__4', 'visibility': 'restaurant,global'},
            http.HTTPStatus.OK,
            {
                'templates': [
                    conftest.ADMIN_POSM_TEMPLATE_4,
                    conftest.ADMIN_POSM_TEMPLATE_2,
                    conftest.ADMIN_POSM_TEMPLATE_1,
                ],
            },
            id='place-filter',
        ),
        pytest.param(
            {'place_id': 'place_id__4', 'visibility': 'restaurant'},
            http.HTTPStatus.OK,
            {'templates': [conftest.ADMIN_POSM_TEMPLATE_4]},
            id='place-filter-exclude-global',
        ),
        pytest.param(
            {'place_id': 'place_id__1', 'visibility': 'restaurant,global'},
            http.HTTPStatus.OK,
            {
                'templates': [
                    conftest.ADMIN_POSM_TEMPLATE_2,
                    conftest.ADMIN_POSM_TEMPLATE_1,
                ],
            },
            id='place-without-templates',
        ),
        pytest.param(
            {'place_id': 'place_id__1', 'visibility': 'restaurant'},
            http.HTTPStatus.OK,
            {'templates': []},
            id='place-without-templates-exclude-global',
        ),
        pytest.param(
            {'place_id': 'not-found-place'},
            http.HTTPStatus.OK,
            {'templates': []},
            id='not-found-place',
        ),
        pytest.param(
            {},
            http.HTTPStatus.BAD_REQUEST,
            {
                'code': 'bad_request',
                'message': (
                    'at least one of place_id and visibility must be specified'
                ),
            },
            id='no-params',
        ),
        pytest.param(
            {'visibility': 'restaurant'},
            http.HTTPStatus.BAD_REQUEST,
            {
                'code': 'bad_request',
                'message': 'visibility can\'t be specified without place_id',
            },
            id='restaurant-without-place-id',
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
async def test_admin_posm_template_list(
        taxi_eats_integration_offline_orders_web,
        params,
        expected_code,
        expected_response,
):
    response = await taxi_eats_integration_offline_orders_web.get(
        '/admin/v1/posm/template/list', params=params,
    )
    body = await response.json()
    assert response.status == expected_code
    assert body == expected_response
