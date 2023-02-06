async def test_get_points_ui_items(taxi_driver_orders_builder):
    response = await taxi_driver_orders_builder.post(
        '/v1/cargo/build-update-offer-screen',
        json={
            'route_points': [
                {'title': 'Первая новая точка', 'subtitle': 'Получение'},
                {'title': 'Вторая новая точка', 'subtitle': 'Вручение'},
            ],
        },
    )
    assert response.status_code == 200, response.text
    assert response.json() == {
        'constructor_items': [
            {
                'horizontal_divider_type': 'bottom_gap',
                'reverse': True,
                'subtitle': 'Получение',
                'title': 'Первая новая точка',
                'type': 'default',
            },
            {
                'horizontal_divider_type': 'bottom_gap',
                'reverse': True,
                'subtitle': 'Вручение',
                'title': 'Вторая новая точка',
                'type': 'default',
            },
        ],
    }
