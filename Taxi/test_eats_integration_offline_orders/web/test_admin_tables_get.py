import http
import typing

import pytest


def _create_table(
        table_id: int,
        place_id,
        is_deleted: bool = False,
        table_pos_name: typing.Optional[str] = None,
):
    result = {
        'id': table_id,
        'table_pos_id': f'table_id__{table_id}',
        'table_ya_id': f'{table_id}',
        'uuid': f'uuid__{table_id}',
        'is_deleted': is_deleted,
        'place_id': place_id,
    }
    if table_pos_name is not None:
        result['table_pos_name'] = table_pos_name
    return result


@pytest.mark.parametrize(
    ('params', 'expected_code', 'expected_response'),
    (
        pytest.param(
            {'place_id': 'place_id__1'},
            http.HTTPStatus.OK,
            {
                'tables': [
                    _create_table(
                        1, 'place_id__1', table_pos_name='table_id__1',
                    ),
                ],
            },
            id='OK',
        ),
        pytest.param(
            {'place_id': 'place_id__3'},
            http.HTTPStatus.OK,
            {
                'tables': [
                    _create_table(
                        3, 'place_id__3', table_pos_name='table_id__3',
                    ),
                    _create_table(4, 'place_id__3', table_pos_name=''),
                    _create_table(5, 'place_id__3'),
                ],
            },
            id='OK-few',
        ),
        pytest.param(
            {'place_id': 'place_id__3', 'include_deleted': 'true'},
            http.HTTPStatus.OK,
            {
                'tables': [
                    _create_table(
                        3, 'place_id__3', table_pos_name='table_id__3',
                    ),
                    _create_table(4, 'place_id__3', table_pos_name=''),
                    _create_table(5, 'place_id__3'),
                    _create_table(6, 'place_id__3', is_deleted=True),
                ],
            },
            id='include-deleted',
        ),
        pytest.param(
            {'place_id': 'not_found'},
            http.HTTPStatus.OK,
            {'tables': []},
            id='not-found',
        ),
    ),
)
@pytest.mark.pgsql(
    'eats_integration_offline_orders', files=['restaurants.sql', 'tables.sql'],
)
async def test_admin_tables_get(
        web_app_client, params, expected_code, expected_response,
):
    response = await web_app_client.get('/admin/v1/tables', params=params)
    body = await response.json()
    assert response.status == expected_code
    assert body == expected_response
