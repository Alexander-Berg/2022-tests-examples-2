import http

import psycopg2.extras
import pytest


@pytest.mark.parametrize(
    ('params', 'expected_code', 'expected_response'),
    (
        pytest.param({'chat_id': 100500}, http.HTTPStatus.OK, {}, id='OK'),
        pytest.param(
            {'chat_id': 987654321},
            http.HTTPStatus.NOT_FOUND,
            {'code': 'not_found', 'message': 'chat not found'},
            id='deleted',
        ),
        pytest.param(
            {'chat_id': 123321123321},
            http.HTTPStatus.NOT_FOUND,
            {'code': 'not_found', 'message': 'chat not found'},
            id='not-found',
        ),
    ),
)
@pytest.mark.pgsql(
    'eats_integration_offline_orders', files=['telegram_chats.sql'],
)
async def test_admin_notifications_tg_delete(
        web_app_client, pgsql, params, expected_code, expected_response,
):
    response = await web_app_client.delete(
        '/admin/v1/notifications/tg', params=params,
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
        SELECT deleted_at
        FROM telegram_chats
        WHERE chat_id = {params['chat_id']}
        """,
    )
    row = cursor.fetchone()
    assert row['deleted_at'] is not None
