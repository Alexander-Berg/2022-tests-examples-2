import http

import psycopg2.extras
import pytest


BODY_NO_LOGIN = {
    'organization_id': 'new-organization-id',
    'terminal_group_id': 'new-terminal-group-id',
}
BODY = BODY_NO_LOGIN.copy()
BODY['api_login'] = 'new-api-login'


@pytest.mark.parametrize(
    ('params', 'request_body', 'expected_code', 'expected_response'),
    (
        pytest.param(
            {'place_id': 'place_id__2'},
            BODY,
            http.HTTPStatus.OK,
            {
                'organization_id': 'new-organization-id',
                'place_id': 'place_id__2',
                'terminal_group_id': 'new-terminal-group-id',
            },
            id='OK-new',
        ),
        pytest.param(
            {'place_id': 'place_id__2'},
            BODY_NO_LOGIN,
            http.HTTPStatus.OK,
            {
                'organization_id': 'new-organization-id',
                'place_id': 'place_id__2',
                'terminal_group_id': 'new-terminal-group-id',
            },
            id='OK-new-no-login',
        ),
        pytest.param(
            {'place_id': 'place_id__1'},
            BODY,
            http.HTTPStatus.OK,
            {
                'organization_id': 'new-organization-id',
                'place_id': 'place_id__1',
                'terminal_group_id': 'new-terminal-group-id',
            },
            id='OK-update',
        ),
        pytest.param(
            {'place_id': 'place_id__1'},
            BODY_NO_LOGIN,
            http.HTTPStatus.OK,
            {
                'organization_id': 'new-organization-id',
                'place_id': 'place_id__1',
                'terminal_group_id': 'new-terminal-group-id',
            },
            id='OK-update-no-login',
        ),
        pytest.param(
            {'place_id': '100000'},
            BODY,
            http.HTTPStatus.NOT_FOUND,
            {'code': 'not_found', 'message': 'place not found'},
            id='not-found',
        ),
        pytest.param(
            {'place_id': 'place_id__4'},
            BODY,
            http.HTTPStatus.BAD_REQUEST,
            {'code': 'bad_request', 'message': 'place pos_type is not iiko'},
            id='non-iiko',
        ),
    ),
)
@pytest.mark.pgsql(
    'eats_integration_offline_orders',
    files=['restaurants.sql', 'iiko_transport_meta.sql'],
)
async def test_admin_iiko_transport_edit(
        taxi_eats_integration_offline_orders_web,
        pgsql,
        params,
        request_body,
        expected_code,
        expected_response,
):
    cursor = pgsql['eats_integration_offline_orders'].cursor(
        cursor_factory=psycopg2.extras.RealDictCursor,
    )
    cursor.execute(
        f"""
            SELECT
                api_login
            FROM iiko_transport_meta
            WHERE place_id = '{params["place_id"]}'
            """,
    )
    old_row = cursor.fetchone()
    old_login = old_row['api_login'] if old_row else ''

    response = await taxi_eats_integration_offline_orders_web.post(
        '/admin/v1/iiko_transport', params=params, json=request_body,
    )
    body = await response.json()
    assert response.status == expected_code
    for key, value in expected_response.items():
        assert value == body.get(key)
    if response.status != http.HTTPStatus.OK:
        return
    cursor.execute(
        f"""
        SELECT
            api_login,
            organization_id,
            terminal_group_id
        FROM iiko_transport_meta
        WHERE place_id = '{params["place_id"]}'
        """,
    )
    row = cursor.fetchone()
    if request_body.get('api_login'):
        assert row['api_login'] != old_login
        assert row['api_login'] != request_body['api_login']
    else:
        assert row['api_login'] == old_login
    assert row['organization_id'] == BODY['organization_id']
    assert row['terminal_group_id'] == BODY['terminal_group_id']
