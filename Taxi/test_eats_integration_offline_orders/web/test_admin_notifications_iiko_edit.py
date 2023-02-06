import http

import psycopg2.extras
import pytest


BODY = {'department_id': 'department_new', 'enabled': True}


@pytest.mark.parametrize(
    ('params', 'expected_code', 'expected_response'),
    (
        pytest.param(
            {'place_id': 'place_id__2'}, http.HTTPStatus.OK, {}, id='OK-new',
        ),
        pytest.param(
            {'place_id': 'place_id__1'},
            http.HTTPStatus.OK,
            {},
            id='OK-update',
        ),
        pytest.param(
            {'place_id': '100000'},
            http.HTTPStatus.NOT_FOUND,
            {'code': 'not_found', 'message': 'place not found'},
            id='not-found',
        ),
        pytest.param(
            {'place_id': 'place_id__4'},
            http.HTTPStatus.BAD_REQUEST,
            {'code': 'bad_request', 'message': 'non-iiko place'},
            id='non-iiko',
        ),
    ),
)
@pytest.mark.pgsql(
    'eats_integration_offline_orders',
    files=['restaurants.sql', 'iiko_waiter_data.sql'],
)
async def test_admin_notifications_iiko_edit(
        web_app_client, pgsql, params, expected_code, expected_response,
):
    response = await web_app_client.post(
        '/admin/v1/notifications/iiko_waiter', params=params, json=BODY,
    )
    body = await response.json()
    assert response.status == expected_code
    assert body == expected_response
    if response.status != http.HTTPStatus.OK:
        return
    cursor = pgsql['eats_integration_offline_orders'].cursor(
        cursor_factory=psycopg2.extras.RealDictCursor,
    )
    cursor.execute(
        f"""
        SELECT
            department_id,
            available AS enabled
        FROM iiko_waiter_data
        WHERE place_id = '{params["place_id"]}'
        """,
    )
    row = cursor.fetchone()
    assert row == BODY
