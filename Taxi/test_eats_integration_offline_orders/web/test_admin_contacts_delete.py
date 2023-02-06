import http

import psycopg2.extras
import pytest


@pytest.mark.parametrize(
    ('params', 'expected_code', 'expected_response'),
    (
        pytest.param(
            {'contact_uuid': 'contact_uuid_1'},
            http.HTTPStatus.OK,
            {},
            id='OK',
        ),
        pytest.param(
            {'contact_uuid': 'contact_uuid_2'},
            http.HTTPStatus.NOT_FOUND,
            {'code': 'not_found', 'message': 'contact not found'},
            id='already-deleted',
        ),
        pytest.param(
            {'contact_uuid': 'not-existing-contact'},
            http.HTTPStatus.NOT_FOUND,
            {'code': 'not_found', 'message': 'contact not found'},
            id='not-found-place',
        ),
    ),
)
@pytest.mark.pgsql(
    'eats_integration_offline_orders',
    files=['restaurants.sql', 'restaurants_contacts.sql'],
)
async def test_admin_place_contacts_delete(
        web_app_client, pgsql, params, expected_code, expected_response,
):
    response = await web_app_client.delete('/admin/v1/contacts', params=params)
    body = await response.json()
    assert response.status == expected_code
    assert body == expected_response
    cursor = pgsql['eats_integration_offline_orders'].cursor(
        cursor_factory=psycopg2.extras.RealDictCursor,
    )
    cursor.execute(
        f"""
SELECT uuid, deleted_at
FROM restaurants_contacts
WHERE uuid='{params['contact_uuid']}'
;
        """,
    )
    row = cursor.fetchone()
    assert row is None or row['deleted_at'] is not None
