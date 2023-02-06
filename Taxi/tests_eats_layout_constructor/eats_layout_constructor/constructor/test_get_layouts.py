import pytest


@pytest.mark.parametrize(
    'layout_id,expected_status,expected_data',
    [
        (
            1,
            200,
            {
                'author': 'nevladov',
                'created': '2020-05-25T08:00:00+00:00',
                'id': 1,
                'name': 'Layout 1',
                'slug': 'layout_1',
                'published': False,
                'widgets': [],
            },
        ),
        (
            2,
            200,
            {
                'author': 'nevladov',
                'created': '2020-05-25T09:00:00+00:00',
                'id': 2,
                'name': 'Layout 2',
                'slug': 'layout_2',
                'published': False,
                'widgets': [
                    {
                        'meta': {'field_1': 'value_3'},
                        'name': 'Widget 1',
                        'payload': {'field_1': 'value_3'},
                        'payload_schema': {'type': 'object'},
                        'template_meta': {'field_1': 'value_1'},
                        'template_payload': {'field_2': 'value_2'},
                        'type': 'banners',
                        'url_id': 1,
                        'id': '1_banners',
                        'widget_template_id': 1,
                    },
                    {
                        'meta': {'field_1': 'value_3'},
                        'name': 'Widget 2',
                        'payload': {'field_1': 'value_3'},
                        'payload_schema': {'type': 'object'},
                        'template_meta': {'field_1': 'value_1'},
                        'template_payload': {'field_2': 'value_2'},
                        'type': 'banners',
                        'url_id': 2,
                        'id': '2_banners',
                        'widget_template_id': 1,
                    },
                ],
            },
        ),
        (
            3,
            404,
            {
                'code': 'LAYOUT_IS_NOT_FOUND',
                'message': 'Layout with id \'3\' is not found',
            },
        ),
    ],
)
async def test_get_layout(
        taxi_eats_layout_constructor,
        mockserver,
        layout_id,
        expected_status,
        expected_data,
):
    response = await taxi_eats_layout_constructor.get(
        'layout-constructor/v1/constructor/layouts/',
        params={'layout_id': layout_id},
    )

    assert response.status == expected_status
    data = response.json()
    if expected_status == 200:
        for widget in data['widgets']:
            widget.pop('meta_schema')
    assert data == expected_data
