import pytest


@pytest.mark.pgsql('eats_corp_orders', files=['pg_eats_corp_orders.sql'])
@pytest.mark.parametrize(
    ('params', 'expected_status', 'expected_json'),
    [
        (
            {'terminal_ids': 'not_found'},
            200,
            {'terminals': [], 'has_more': False},
        ),
        (
            {'terminal_ids': 'terminal_id'},
            200,
            {
                'terminals': [
                    {
                        'place_id': '146',
                        'terminal_id': 'terminal_id',
                        'slug': 'terminal_id',
                        'enabled': True,
                        'orders': {'count': 0},
                    },
                ],
                'has_more': False,
            },
        ),
        (
            {'place_ids': '146'},
            200,
            {
                'terminals': [
                    {
                        'place_id': '146',
                        'terminal_id': 'terminal_id',
                        'slug': 'terminal_id',
                        'enabled': True,
                        'orders': {'count': 0},
                    },
                ],
                'has_more': False,
            },
        ),
    ],
)
async def test_admin_terminals_get(
        taxi_eats_corp_orders_web, params, expected_status, expected_json,
):
    response = await taxi_eats_corp_orders_web.get(
        '/v1/admin/terminals', params=params,
    )
    assert response.status == expected_status
    content = await response.json()
    assert content == expected_json
