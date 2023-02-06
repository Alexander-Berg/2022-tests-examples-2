import http

import pytest


@pytest.mark.parametrize(
    ('params', 'expected_code', 'expected_response'),
    (
        pytest.param(
            {'table_id': 1},
            http.HTTPStatus.OK,
            {
                'id': 1,
                'is_deleted': False,
                'place_id': 'place_id__1',
                'table_pos_id': 'table_id__1',
                'table_pos_name': 'table_id__1',
                'table_ya_id': '1',
                'uuid': 'uuid__1',
            },
            id='OK',
        ),
        pytest.param(
            {'table_id': 100500},
            http.HTTPStatus.NOT_FOUND,
            {'message': 'table not found', 'code': 'not_found'},
            id='not-found',
        ),
    ),
)
@pytest.mark.pgsql('eats_integration_offline_orders', files=['tables.sql'])
async def test_admin_table_get(
        taxi_eats_integration_offline_orders_web,
        pgsql,
        params,
        expected_code,
        expected_response,
):
    response = await taxi_eats_integration_offline_orders_web.get(
        '/admin/v1/table', params=params,
    )
    body = await response.json()
    assert response.status == expected_code
    assert body == expected_response
