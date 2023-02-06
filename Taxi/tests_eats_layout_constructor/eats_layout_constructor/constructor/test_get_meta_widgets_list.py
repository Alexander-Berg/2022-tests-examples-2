async def test_get_meta_widgets_list(taxi_eats_layout_constructor):
    response = await taxi_eats_layout_constructor.get(
        'layout-constructor/v1/constructor/meta-widgets/list/',
    )
    assert response.json() == {
        'meta_widgets': [
            {
                'id': 1,
                'name': 'Order Actions and Meta',
                'slug': 'order_existing',
                'type': 'place_layout',
            },
            {
                'id': 2,
                'name': 'Drop some meta and actions',
                'slug': 'drop_some',
                'type': 'place_layout',
            },
        ],
    }
