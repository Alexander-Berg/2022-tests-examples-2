from testsuite.utils import yaml_util


def get_meta_widget_settings_schema(source_dir, meta_widget_type):
    data = yaml_util.load_file(
        source_dir / 'src/meta_widgets' / meta_widget_type / 'meta.yaml',
    )
    return data['settings']


async def test_get_meta_widgets_types(
        taxi_eats_layout_constructor,
        mockserver,
        service_source_dir,
        load_json,
):
    response = await taxi_eats_layout_constructor.get(
        'layout-constructor/v1/constructor/meta-widgets/types/',
    )
    assert response.json() == {
        'types': [
            {
                'settings_schema': load_json('filters_layout_settings.json'),
                'type': 'filters_layout',
            },
            {
                'settings_schema': get_meta_widget_settings_schema(
                    service_source_dir, 'place_layout',
                ),
                'type': 'place_layout',
            },
            {
                'settings_schema': get_meta_widget_settings_schema(
                    service_source_dir, 'banners_custom',
                ),
                'type': 'banners_custom',
            },
        ],
    }
