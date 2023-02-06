import pytest


@pytest.mark.pgsql(
    'eats_corp_orders', files=['pg_eats_corp_orders.sql', 'menu.sql'],
)
@pytest.mark.parametrize(
    ('params', 'expected_status', 'expected_json'),
    [
        (
            {'terminal_id': 'terminal_id'},
            200,
            {
                'categories': [
                    {
                        'category_name': 'category_name',
                        'items': [{'title': 'title', 'price': '10'}],
                    },
                ],
            },
        ),
        ({'terminal_id': 'not found'}, 404, {}),
    ],
)
async def test_menu_get(
        taxi_eats_corp_orders_web, params, expected_status, expected_json,
):
    response = await taxi_eats_corp_orders_web.get(
        '/v1/user/menu', params=params,
    )
    assert response.status == expected_status
    content = await response.json()
    assert content == expected_json
