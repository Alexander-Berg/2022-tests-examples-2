import http

import psycopg2.extras
import pytest


NOT_FOUND_RESPONSE = {'code': 'not_found', 'message': 'manager not found'}


@pytest.mark.parametrize(
    ('params', 'expected_code', 'expected_response'),
    (
        pytest.param(
            {'manager_uuid': 'manager_uuid_1'},
            http.HTTPStatus.OK,
            {},
            id='OK',
        ),
        pytest.param(
            {'manager_uuid': 'manager_uuid_2'},
            http.HTTPStatus.NOT_FOUND,
            NOT_FOUND_RESPONSE,
            id='already-deleted',
        ),
        pytest.param(
            {'manager_uuid': 'not-existing-manager'},
            http.HTTPStatus.NOT_FOUND,
            NOT_FOUND_RESPONSE,
            id='not-found-place',
        ),
    ),
)
@pytest.mark.pgsql(
    'eats_integration_offline_orders',
    files=['restaurants.sql', 'telegram_managers.sql'],
)
async def test_admin_notifications_tg_managers_delete(
        web_app_client, pgsql, params, expected_code, expected_response,
):
    response = await web_app_client.delete(
        '/admin/v1/notifications/tg/managers', params=params,
    )
    body = await response.json()
    assert response.status == expected_code
    assert body == expected_response
    cursor = pgsql['eats_integration_offline_orders'].cursor(
        cursor_factory=psycopg2.extras.RealDictCursor,
    )
    cursor.execute(
        f"""
SELECT uuid, deleted_at
FROM telegram_managers
WHERE uuid='{params['manager_uuid']}'
;
        """,
    )
    row = cursor.fetchone()
    assert row is None or row['deleted_at'] is not None
