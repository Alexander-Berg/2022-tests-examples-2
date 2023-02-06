import http

import psycopg2.extras
import pytest

from test_eats_integration_offline_orders import conftest

SETTINGS = {
    'qr': {'rotate': 2.0, 'size': 10, 'x': 20, 'y': 25},
    'text': {
        'alpha': 0.5,
        'color': '#000000',
        'font_name': 'YandexSansText-Bold',
        'font_size': 12.0,
        'rotate': 2.0,
        'x': 150,
        'y': 100,
    },
}


def _create_request(visibility, place_ids=None):
    result = {
        'description': 'awesome-description',
        'name': 'new-name',
        'settings': SETTINGS,
        'visibility': visibility,
    }
    if place_ids is not None:
        result['place_ids'] = place_ids
    return result


def _create_response(template_id, visibility, place_ids=None):
    return conftest.create_admin_posm_template(
        description='awesome-description',
        name='new-name',
        settings=SETTINGS,
        template_id=template_id,
        visibility=visibility,
        place_ids=place_ids,
    )


@pytest.mark.parametrize(
    ('params', 'request_body', 'expected_code', 'expected_response'),
    (
        pytest.param(
            {'template_id': 1},
            _create_request(visibility='global'),
            http.HTTPStatus.OK,
            _create_response(template_id=1, visibility='global'),
            id='OK-global',
        ),
        pytest.param(
            {'template_id': 4},
            _create_request(
                visibility='restaurant',
                place_ids=['place_id__4', 'place_id__5'],
            ),
            http.HTTPStatus.OK,
            _create_response(
                template_id=4,
                visibility='restaurant',
                place_ids=['place_id__4', 'place_id__5'],
            ),
            id='OK-restaurant',
        ),
        pytest.param(
            {'template_id': 1},
            _create_request(
                visibility='restaurant',
                place_ids=['place_id__1', 'place_id__2'],
            ),
            http.HTTPStatus.OK,
            _create_response(
                template_id=1,
                visibility='restaurant',
                place_ids=['place_id__1', 'place_id__2'],
            ),
            id='global-to-restaurant',
        ),
        pytest.param(
            {'template_id': 4},
            _create_request(visibility='global'),
            http.HTTPStatus.OK,
            _create_response(template_id=4, visibility='global'),
            id='restaurant-to-global',
        ),
        pytest.param(
            {'template_id': 1},
            _create_request(visibility='global', place_ids=['place_id__1']),
            http.HTTPStatus.BAD_REQUEST,
            {
                'code': 'bad_request',
                'message': (
                    'global visibility must be passed without place_ids'
                ),
            },
            id='global-with-place-id',
        ),
        pytest.param(
            {'template_id': 1},
            _create_request(visibility='restaurant'),
            http.HTTPStatus.BAD_REQUEST,
            {
                'code': 'bad_request',
                'message': (
                    'restaurant visibility must be passed with place_ids'
                ),
            },
            id='restaurant-without-place-id',
        ),
        pytest.param(
            {'template_id': 100500},
            _create_request(visibility='global'),
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
async def test_admin_posm_template_edit(
        taxi_eats_integration_offline_orders_web,
        pgsql,
        params,
        request_body,
        expected_code,
        expected_response,
):
    response = await taxi_eats_integration_offline_orders_web.put(
        '/admin/v1/posm/template', params=params, json=request_body,
    )
    body = await response.json()
    assert response.status == expected_code
    assert body == expected_response
    if expected_code is not http.HTTPStatus.OK:
        return
    cursor = pgsql['eats_integration_offline_orders'].cursor(
        cursor_factory=psycopg2.extras.RealDictCursor,
    )
    cursor.execute(
        f"""
        SELECT * FROM posm_templates
        WHERE id = {params["template_id"]};
        """,
    )
    row = cursor.fetchone()
    assert row['name'] == request_body['name']
    assert row['description'] == request_body['description']
    assert row['settings'] == request_body['settings']
    assert row['visibility'] == request_body['visibility']

    cursor.execute(
        f"""
        SELECT * FROM restaurants_posm_templates
        WHERE
            template_id = {params["template_id"]}
            AND deleted_at IS NULL
        ;
        """,
    )
    rows = cursor.fetchall()
    assert sorted(row['place_id'] for row in rows) == sorted(
        request_body.get('place_ids', []),
    )
