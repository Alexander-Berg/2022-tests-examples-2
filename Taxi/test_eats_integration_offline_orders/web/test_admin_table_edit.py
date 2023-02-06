import http
import typing

import psycopg2.extras
import pytest


def _create_request(
        table_pos_id: str = 'table_pos_id',
        uuid: str = 'new_uuid',
        table_pos_name: typing.Optional[str] = None,
        table_ya_id: typing.Optional[str] = None,
):
    result = {'table_pos_id': table_pos_id, 'uuid': uuid}
    if table_pos_name is not None:
        result['table_pos_name'] = table_pos_name
    if table_ya_id is not None:
        result['table_ya_id'] = table_ya_id
    return result


@pytest.mark.parametrize(
    ('params', 'request_body', 'expected_code'),
    (
        pytest.param(
            {'table_id': 1}, _create_request(), http.HTTPStatus.OK, id='OK',
        ),
        pytest.param(
            {'table_id': 1},
            _create_request(
                table_pos_name='table_pos_name', table_ya_id='table_ya_id',
            ),
            http.HTTPStatus.OK,
            id='OK-table_pos_name',
        ),
        pytest.param(
            {'table_id': 2},
            _create_request(uuid='uuid__1'),
            http.HTTPStatus.CONFLICT,
            id='conflict',
        ),
        pytest.param(
            {'table_id': 100500},
            _create_request('table_id__1', 'new_uuid'),
            http.HTTPStatus.NOT_FOUND,
            id='no-place',
        ),
    ),
)
@pytest.mark.pgsql(
    'eats_integration_offline_orders', files=['restaurants.sql', 'tables.sql'],
)
async def test_admin_table_edit(
        web_app_client, pgsql, params, request_body, expected_code,
):
    response = await web_app_client.patch(
        '/admin/v1/tables', params=params, json=request_body,
    )
    assert response.status == expected_code
    if expected_code != http.HTTPStatus.OK:
        return

    cursor = pgsql['eats_integration_offline_orders'].cursor(
        cursor_factory=psycopg2.extras.RealDictCursor,
    )
    cursor.execute(
        f"""
        SELECT
            place_id,
            uuid,
            table_pos_id,
            table_pos_name,
            table_ya_id
        FROM tables
        WHERE
            uuid = '{request_body['uuid']}'
        ORDER BY id
        ;
        """,
    )
    row = cursor.fetchone()

    assert row
    assert row['uuid'] == request_body['uuid']
    assert row['table_pos_id'] == request_body['table_pos_id']
    assert row['table_pos_name'] == request_body.get('table_pos_name')
    assert row['table_ya_id'] == request_body.get('table_ya_id')
