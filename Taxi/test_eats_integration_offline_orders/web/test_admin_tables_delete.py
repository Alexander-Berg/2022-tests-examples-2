import http

import psycopg2.extras
import pytest


@pytest.mark.parametrize(
    ('params', 'expected_code', 'expected_response'),
    (
        pytest.param(
            {'uuid': 'uuid__1'},
            http.HTTPStatus.OK,
            {'success': ['uuid__1'], 'error': []},
            id='OK',
        ),
        pytest.param(
            {'uuid': 'uuid__3,uuid__4'},
            http.HTTPStatus.OK,
            {'success': ['uuid__3', 'uuid__4'], 'error': []},
            id='OK-delete-few',
        ),
        pytest.param(
            {'uuid': 'uuid__6'},
            http.HTTPStatus.OK,
            {'success': [], 'error': ['uuid__6']},
            id='already-deleted',
        ),
        pytest.param(
            {'uuid': 'not_found'},
            http.HTTPStatus.OK,
            {'success': [], 'error': ['not_found']},
            id='not-found',
        ),
        pytest.param(
            {'uuid': 'uuid__1,not_found'},
            http.HTTPStatus.OK,
            {'success': ['uuid__1'], 'error': ['not_found']},
            id='OK-and-not-found',
        ),
    ),
)
@pytest.mark.pgsql(
    'eats_integration_offline_orders', files=['restaurants.sql', 'tables.sql'],
)
async def test_admin_tables_delete(
        web_app_client, pgsql, params, expected_code, expected_response,
):
    response = await web_app_client.delete('/admin/v1/tables', params=params)
    body = await response.json()
    assert response.status == expected_code
    assert body == expected_response
    if (
            response.status != http.HTTPStatus.OK
            or not expected_response['success']
    ):
        return
    cursor = pgsql['eats_integration_offline_orders'].cursor(
        cursor_factory=psycopg2.extras.RealDictCursor,
    )
    cursor.execute(
        f"""
        SELECT deleted_at
        FROM tables
        WHERE
            uuid IN (
                {','.join(f"'{x}'" for x in expected_response['success'])}
            )
        """,
    )
    rows = cursor.fetchall()
    assert rows
    assert all(row['deleted_at'] for row in rows)
