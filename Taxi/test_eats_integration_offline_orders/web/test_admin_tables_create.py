import http
import typing

import psycopg2.extras
import pytest


def _create_request(
        table_pos_id: str = 'table_pos_id',
        uuid: str = 'new_uuid',
        table_pos_name: typing.Optional[str] = None,
):
    result = {
        'table_pos_id': table_pos_id,
        'table_ya_id': table_pos_id,
        'uuid': uuid,
    }
    if table_pos_name is not None:
        result['table_pos_name'] = table_pos_name
    return result


@pytest.mark.parametrize(
    ('params', 'request_body', 'expected_code', 'expected_response'),
    (
        pytest.param(
            {'place_id': 'place_id__1'},
            {'tables': [_create_request()]},
            http.HTTPStatus.OK,
            {
                'tables': [
                    {
                        'id': 8,
                        'is_deleted': False,
                        'table_pos_id': 'table_pos_id',
                        'table_pos_name': 'table_pos_id',
                        'table_ya_id': 'table_pos_id',
                        'uuid': 'new_uuid',
                        'place_id': 'place_id__1',
                    },
                ],
            },
            id='OK',
        ),
        pytest.param(
            {'place_id': 'place_id__1'},
            {'tables': [_create_request(table_pos_name='table_pos_name')]},
            http.HTTPStatus.OK,
            {
                'tables': [
                    {
                        'id': 8,
                        'is_deleted': False,
                        'table_pos_id': 'table_pos_id',
                        'table_pos_name': 'table_pos_name',
                        'table_ya_id': 'table_pos_id',
                        'uuid': 'new_uuid',
                        'place_id': 'place_id__1',
                    },
                ],
            },
            id='OK-table_pos_name',
        ),
        pytest.param(
            {'place_id': 'place_id__1'},
            {
                'tables': [
                    _create_request(
                        uuid='test-uuid-1', table_pos_id='pos-id-1',
                    ),
                    _create_request(
                        uuid='test-uuid-2', table_pos_id='pos-id-2',
                    ),
                ],
            },
            http.HTTPStatus.OK,
            {
                'tables': [
                    {
                        'id': 8,
                        'is_deleted': False,
                        'table_pos_id': 'pos-id-1',
                        'table_pos_name': 'pos-id-1',
                        'table_ya_id': 'pos-id-1',
                        'uuid': 'test-uuid-1',
                        'place_id': 'place_id__1',
                    },
                    {
                        'id': 9,
                        'is_deleted': False,
                        'table_pos_id': 'pos-id-2',
                        'table_pos_name': 'pos-id-2',
                        'table_ya_id': 'pos-id-2',
                        'uuid': 'test-uuid-2',
                        'place_id': 'place_id__1',
                    },
                ],
            },
            id='OK-few',
        ),
        pytest.param(
            {'place_id': 'place_id__1'},
            {'tables': [_create_request(), _create_request()]},
            http.HTTPStatus.CONFLICT,
            None,
            id='conflict-duplicate-request',
        ),
        pytest.param(
            {'place_id': 'place_id__1'},
            {'tables': [_create_request()]},
            http.HTTPStatus.OK,
            {
                'tables': [
                    {
                        'id': 8,
                        'is_deleted': False,
                        'table_pos_id': 'table_pos_id',
                        'table_pos_name': 'table_pos_id',
                        'table_ya_id': 'table_pos_id',
                        'uuid': 'new_uuid',
                        'place_id': 'place_id__1',
                    },
                ],
            },
            id='OK-with-tips',
        ),
        pytest.param(
            {'place_id': 'place_id__1'},
            {
                'tables': [
                    _create_request(uuid='new_uuid'),
                    _create_request(uuid='uuid__1'),
                ],
            },
            http.HTTPStatus.CONFLICT,
            None,
            id='conflict',
        ),
        pytest.param(
            {'place_id': 'not_found'},
            {'tables': [{'table_pos_id': 'table_id__1', 'uuid': 'new_uuid'}]},
            http.HTTPStatus.NOT_FOUND,
            {'code': 'not_found', 'message': 'place not found'},
            id='no-place',
        ),
    ),
)
@pytest.mark.pgsql(
    'eats_integration_offline_orders', files=['restaurants.sql', 'tables.sql'],
)
async def test_admin_tables_create(
        web_app_client,
        pgsql,
        params,
        request_body,
        expected_code,
        expected_response,
):
    response = await web_app_client.post(
        '/admin/v1/tables', params=params, json=request_body,
    )
    body = await response.json()
    assert response.status == expected_code
    if expected_code != http.HTTPStatus.OK:
        return
    assert body == expected_response

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
            uuid = '{request_body['tables'][0]['uuid']}'
        ORDER BY id
        ;
        """,
    )
    rows = cursor.fetchall()

    assert rows
    request_tables = request_body['tables']
    for index, row in enumerate(rows):
        assert row['place_id'] == params['place_id']
        assert row['uuid'] == request_body['tables'][index]['uuid']
        assert row['table_pos_id'] == request_tables[index]['table_pos_id']
        assert row['table_pos_name'] == request_tables[index].get(
            'table_pos_name', request_tables[index]['table_pos_id'],
        )
        assert row['table_ya_id'] == request_tables[index]['table_pos_id']
