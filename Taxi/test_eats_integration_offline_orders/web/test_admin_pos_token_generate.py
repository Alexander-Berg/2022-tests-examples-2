import http

import bcrypt
import pytest


@pytest.mark.parametrize(
    ('params', 'expected_code'),
    (
        pytest.param(
            {'place_id': 'place_id__1'},
            http.HTTPStatus.OK,
            id='OK-update-token',
        ),
        pytest.param(
            {'place_id': 'place_id__2'}, http.HTTPStatus.OK, id='OK-new-token',
        ),
        pytest.param(
            {'place_id': 'place_id__5'},
            http.HTTPStatus.OK,
            id='OK-new-quick_resto',
        ),
        pytest.param(
            {'place_id': 'place_id__4'},
            http.HTTPStatus.BAD_REQUEST,
            id='rkeeper',
        ),
    ),
)
@pytest.mark.pgsql(
    'eats_integration_offline_orders', files=['restaurants.sql', 'tables.sql'],
)
async def test_admin_pos_token_generate(
        web_app_client, pgsql, params, expected_code,
):
    response = await web_app_client.post('/admin/v1/pos_token', params=params)
    body = await response.json()
    assert response.status == expected_code
    if response.status != http.HTTPStatus.OK:
        return
    assert body.get('token')
    cursor = pgsql['eats_integration_offline_orders'].cursor()
    cursor.execute(
        f"""
        SELECT token
        FROM pos_tokens
        WHERE place_id = '{params['place_id']}'
        ;
        """,
    )
    row = cursor.fetchone()
    assert bcrypt.checkpw(body['token'].encode(), row[0].encode())
