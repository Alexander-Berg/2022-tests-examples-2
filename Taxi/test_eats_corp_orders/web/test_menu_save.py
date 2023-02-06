REQUEST = [
    {
        'category_name': 'category_name',
        'items': [{'title': 'title', 'price': '10'}],
    },
]


async def test_menu_save_401(taxi_eats_corp_orders_web):
    response = await taxi_eats_corp_orders_web.post(
        '/v1/menu/save',
        headers={'X-Authorization': f'incorrect token'},
        json=REQUEST,
    )
    assert response.status == 401


async def test_menu_save(
        taxi_eats_corp_orders_web, terminal_id, terminal_token,
):
    response = await taxi_eats_corp_orders_web.post(
        '/v1/menu/save',
        headers={'X-Authorization': f'{terminal_id}:{terminal_token}'},
        json=REQUEST,
    )
    assert response.status == 200
