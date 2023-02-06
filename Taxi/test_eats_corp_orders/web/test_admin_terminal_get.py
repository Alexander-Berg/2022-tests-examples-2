import pytest


@pytest.mark.pgsql('eats_corp_orders', files=['pg_eats_corp_orders.sql'])
@pytest.mark.parametrize(
    ('params', 'expected_status', 'expected_json'),
    [
        (
            {'terminal_id': 'terminal_id'},
            200,
            {
                'place_id': '146',
                'terminal_id': 'terminal_id',
                'slug': 'terminal_id',
                'enabled': True,
                'orders': {'count': 0},
            },
        ),
        ({'terminal_id': 'not_found'}, 404, {}),
    ],
)
async def test_admin_terminal_get(
        taxi_eats_corp_orders_web, params, expected_status, expected_json,
):
    response = await taxi_eats_corp_orders_web.get(
        '/v1/admin/terminal', params=params,
    )
    assert response.status == expected_status
    content = await response.json()
    assert content == expected_json
