async def test_get_layouts_list(taxi_eats_layout_constructor, mockserver):
    response = await taxi_eats_layout_constructor.get(
        'layout-constructor/v1/constructor/layouts/list/',
    )
    assert response.json() == {
        'layouts': [
            {
                'id': 101,
                'name': 'Layout 101',
                'slug': 'layout_101',
                'published': False,
            },
            {
                'id': 100,
                'name': 'Layout 100',
                'slug': 'layout_100',
                'published': False,
            },
            {
                'id': 2,
                'name': 'Layout 2',
                'slug': 'layout_2',
                'published': False,
            },
            {
                'id': 1,
                'name': 'Layout 1',
                'slug': 'layout_1',
                'published': False,
            },
        ],
    }
