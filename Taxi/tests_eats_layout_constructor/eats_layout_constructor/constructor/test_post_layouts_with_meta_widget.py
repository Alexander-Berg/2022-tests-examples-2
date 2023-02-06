import pytest


@pytest.mark.parametrize(
    'input_data,expected_status,expected_data',
    [
        pytest.param(
            {
                'name': 'Layout 1',
                'slug': 'layout_1',
                'widgets': [
                    {
                        'meta': {
                            'place_filter_type': 'open',
                            'output_type': 'list',
                        },
                        'name': 'Widget 1',
                        'slug': 'layout_1',
                        'payload': {'field_1': 'value_3'},
                        'template_meta': {'field_1': 'value_1'},
                        'template_payload': {'field_2': 'value_2'},
                        'widget_template_id': 1,
                        'meta_widget': 1,
                        'meta_widget_experiment_name': (
                            'meta_widget_experiment'
                        ),
                    },
                ],
            },
            200,
            {
                'id': 1,
                'name': 'Layout 1',
                'slug': 'layout_1',
                'published': False,
                'author': 'nk2ge5k',
                'widgets': [
                    {
                        'id': '1_places_collection',
                        'url_id': 1,
                        'type': 'places_collection',
                        'name': 'Widget 1',
                        'meta': {
                            'place_filter_type': 'open',
                            'output_type': 'list',
                        },
                        'payload': {'field_1': 'value_3'},
                        'payload_schema': {'type': 'object'},
                        'template_meta': {'field_1': 'value_1'},
                        'template_payload': {'field_2': 'value_2'},
                        'widget_template_id': 1,
                        'meta_widget': 1,
                        'meta_widget_experiment_name': (
                            'meta_widget_experiment'
                        ),
                    },
                ],
            },
            id='ok',
        ),
        pytest.param(
            {
                'name': 'Layout 1',
                'slug': 'layout_1',
                'widgets': [
                    {
                        'meta': {'place_filter_type': 'open'},
                        'name': 'Widget 1',
                        'slug': 'layout_1',
                        'payload': {'field_1': 'value_3'},
                        'template_meta': {'field_1': 'value_1'},
                        'template_payload': {'field_2': 'value_2'},
                        'widget_template_id': 1,
                        'meta_widget': 1,
                        'meta_widget_experiment_name': '',
                    },
                ],
            },
            400,
            {
                'code': '400',
                'message': (
                    'Parse error at pos 329, path '
                    '\'widgets.[0].meta_widget_experiment_name\': '
                    'incorrect size, must be 5 (limit) <= 0 (value), '
                    'the latest token was : ""'
                ),
            },
            id='empty meta_widget experiment name',
        ),
        pytest.param(
            {
                'name': 'Layout 4',
                'slug': 'layout_4',
                'widgets': [
                    {
                        'meta': {'place_filter_type': 'open'},
                        'name': 'Widget 1',
                        'slug': 'layout_1',
                        'payload': {'field_1': 'value_3'},
                        'template_meta': {'field_1': 'value_1'},
                        'template_payload': {'field_2': 'value_2'},
                        'widget_template_id': 1,
                        'meta_widget_experiment_name': (
                            'meta_widget_experiment'
                        ),
                    },
                ],
            },
            400,
            {
                'code': 'WidgetValidationError',
                'message': (
                    'Widget with type \'places_collection\' is not valid: '
                    'meta_widget cannot be empty if '
                    'meta_widget_experiment_name is set'
                ),
            },
            id='meta_widget experment without meta_widget',
        ),
        pytest.param(
            {
                'name': 'Layout 1',
                'slug': 'layout_1',
                'widgets': [
                    {
                        'meta': {
                            'place_filter_type': 'open',
                            'output_type': 'list',
                            'limit': 2147483648,
                        },
                        'name': 'Widget 1',
                        'slug': 'layout_1',
                        'payload': {'field_1': 'value_3'},
                        'template_meta': {'field_1': 'value_1'},
                        'template_payload': {'field_2': 'value_2'},
                        'widget_template_id': 1,
                        'meta_widget': 1,
                        'meta_widget_experiment_name': (
                            'meta_widget_experiment'
                        ),
                    },
                ],
            },
            400,
            {
                'code': 'WidgetValidationError',
                'message': (
                    'Widget with type \'places_collection\' is not valid: '
                    'Value of \'limit\' is out of bounds '
                    '(-2147483648 <= 2147483648 <= 2147483647)'
                ),
            },
            id='integer overflow',
        ),
    ],
)
async def test_post_layout_with_meta_widget(
        taxi_eats_layout_constructor,
        input_data,
        expected_status,
        expected_data,
):
    response = await taxi_eats_layout_constructor.post(
        'layout-constructor/v1/constructor/layouts/',
        headers={'X-Yandex-Login': 'nk2ge5k'},
        json=input_data,
    )
    assert response.status == expected_status
    data = response.json()
    if expected_status == 200:
        data.pop('created')
        for widget in data['widgets']:
            widget.pop('meta_schema')
    assert data == expected_data
