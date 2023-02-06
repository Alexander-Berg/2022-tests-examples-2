async def test_get_widget_templates_list(
        taxi_eats_layout_constructor, mockserver,
):
    response = await taxi_eats_layout_constructor.get(
        'layout-constructor/v1/constructor/widget-templates/list/',
    )
    assert response.json() == {
        'widget_templates': [
            {'id': 3, 'name': 'Popup banner'},
            {'id': 2, 'name': 'Widget template 2'},
            {'id': 1, 'name': 'Widget template 1'},
        ],
    }
