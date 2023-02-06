import http

import psycopg2.extras
import pytest


def _create_request(chat_id, chat_type='group', enabled=True):
    return {'chat_id': chat_id, 'chat_type': chat_type, 'enabled': enabled}


@pytest.mark.parametrize(
    ('params', 'request_body', 'expected_code', 'expected_response'),
    (
        pytest.param(
            {'place_id': 'place_id__2'},
            _create_request(777777777, enabled=False),
            http.HTTPStatus.OK,
            {},
            id='OK-new',
        ),
        pytest.param(
            {'place_id': 'place_id__1'},
            _create_request(100500),
            http.HTTPStatus.OK,
            {},
            id='OK-update',
        ),
        pytest.param(
            {'place_id': 'place_id__2'},
            _create_request(987654321),
            http.HTTPStatus.OK,
            {},
            id='OK-unset-deleted',
        ),
        pytest.param(
            {'place_id': 'not-found'},
            _create_request(100500),
            http.HTTPStatus.NOT_FOUND,
            {'code': 'not_found', 'message': 'place not found'},
            id='not-found-place',
        ),
    ),
)
@pytest.mark.pgsql(
    'eats_integration_offline_orders',
    files=['restaurants.sql', 'telegram_chats.sql'],
)
async def test_admin_notifications_tg_add(
        web_app_client,
        pgsql,
        params,
        request_body,
        expected_code,
        expected_response,
):
    response = await web_app_client.post(
        '/admin/v1/notifications/tg', params=params, json=request_body,
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
        SELECT *
        FROM telegram_chats
        WHERE
            place_id = '{params["place_id"]}'
            AND chat_id = {request_body['chat_id']}
        """,
    )
    row = cursor.fetchone()
    assert row
    assert row['deleted_at'] is None
    assert row['disabled'] is not request_body['enabled']
    assert row['chat_type'] == request_body['chat_type']
