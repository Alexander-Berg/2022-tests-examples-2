async def test_stub__remove_me(taxi_grocery_menu):
    response = await taxi_grocery_menu.post(
        '/internal/v1/menu/v1/available',
        json={'depot_id': 'depot-id', 'layout_id': 'layout-id'},
    )
    assert response.status_code == 200


async def test_returns_404_when_depot_is_not_found__fix_me(taxi_grocery_menu):
    response = await taxi_grocery_menu.post(
        '/internal/v1/menu/v1/available',
        json={'depot_id': '', 'layout_id': 'layout-id'},
    )
    assert response.status_code == 404
