import http

import psycopg2.extras
import pytest


@pytest.mark.parametrize(
    'request_body, expected_code, expected_response',
    (
        pytest.param(
            {
                'address': 'Улица Пушкина',
                'name': 'хороший ресторан',
                'place_id': 'another_place_id',
                'pos_type': 'iiko',
                'pos_api_version': '1.0',
                'description': 'прекрасное описание',
            },
            http.HTTPStatus.OK,
            {
                'id': 5,
                'slug': 'horoshij_restoran_0',
                'place_id': 'another_place_id',
            },
            id='OK',
        ),
        pytest.param(
            {
                'address': '',
                'name': 'новый ресторан',
                'place_id': 'another_place_id',
                'pos_type': 'iiko',
            },
            http.HTTPStatus.OK,
            {
                'id': 5,
                'slug': 'novij_restoran_101',
                'place_id': 'another_place_id',
            },
            id='OK-slug-exists',
        ),
        pytest.param(
            {
                'address': '',
                'name': 'нОвыЙ ресТораН',
                'place_id': 'another_place_id',
                'pos_type': 'iiko',
            },
            http.HTTPStatus.OK,
            {
                'id': 5,
                'slug': 'novij_restoran_101',
                'place_id': 'another_place_id',
            },
            id='OK-camel-case',
        ),
        pytest.param(
            {
                'address': '',
                'name': 'noVij rEstOran',
                'place_id': 'another_place_id',
                'pos_type': 'iiko',
            },
            http.HTTPStatus.OK,
            {
                'id': 5,
                'slug': 'novij_restoran_101',
                'place_id': 'another_place_id',
            },
            id='OK-camel-case-2',
        ),
        pytest.param(
            {
                'address': '',
                'name': '"ресторан"',
                'place_id': 'another_place_id',
                'pos_type': 'iiko',
            },
            http.HTTPStatus.OK,
            {'id': 5, 'slug': 'restoran_6', 'place_id': 'another_place_id'},
            id='OK-leading-zero',
        ),
        pytest.param(
            {
                'address': '',
                'name': '"%"',
                'place_id': 'another_place_id',
                'pos_type': 'iiko',
            },
            http.HTTPStatus.BAD_REQUEST,
            {'message': 'invalid name', 'code': 'bad_request'},
            id='non-alphanumeric-name',
        ),
        pytest.param(
            {
                'address': '',
                'name': '           ресторан',
                'place_id': 'another_place_id',
                'pos_type': 'iiko',
            },
            http.HTTPStatus.BAD_REQUEST,
            {'message': 'invalid name', 'code': 'bad_request'},
            id='name-starts-with-whitespace',
        ),
        pytest.param(
            {
                'address': '',
                'name': 'новый ресторан',
                'place_id': 'place_id__1',
                'pos_type': 'iiko',
            },
            http.HTTPStatus.CONFLICT,
            {'message': 'place already exists', 'code': 'conflict'},
            id='conflict',
        ),
    ),
)
@pytest.mark.pgsql(
    'eats_integration_offline_orders', files=['restaurants.sql'],
)
async def test_admin_place_create(
        web_app_client, pgsql, request_body, expected_code, expected_response,
):
    response = await web_app_client.post('/admin/v1/place', json=request_body)
    body = await response.json()
    assert response.status == expected_code
    assert body == expected_response

    if expected_code != http.HTTPStatus.OK:
        return
    cursor = pgsql['eats_integration_offline_orders'].cursor(
        cursor_factory=psycopg2.extras.RealDictCursor,
    )
    cursor.execute(
        f"""
        select
            slug,
            name,
            address,
            pos_type,
            pos_api_version,
            description
        from restaurants
        where id = {expected_response['id']}
        ;
        """,
    )
    row = cursor.fetchone()
    assert row
    assert row['slug'] == expected_response['slug']
    assert row['name'] == request_body['name']
    assert row['address'] == request_body['address']
    assert row['pos_type'] == request_body['pos_type']
    assert row['pos_api_version'] == request_body.get('pos_api_version', '1.0')
    assert row['description'] == request_body.get('description')
