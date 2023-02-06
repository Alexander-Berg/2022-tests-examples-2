import pytest

from testsuite.utils import yaml_util


def get_meta_widget_settings_schema(source_dir, meta_widget_type):
    data = yaml_util.load_file(
        source_dir / 'src/meta_widgets' / meta_widget_type / 'meta.yaml',
    )
    return data['settings']


@pytest.mark.parametrize(
    'meta_widget_type,meta_widget_id,expected_status,expected_data',
    [
        (
            'place_layout',
            1,
            200,
            {
                'id': 1,
                'type': 'place_layout',
                'slug': 'order_existing',
                'name': 'Order Actions and Meta',
                'settings': {
                    'order': ['actions', 'meta'],
                    'action_extenders': ['actions_info'],
                    'meta_extenders': ['meta_info'],
                },
            },
        ),
        (
            '',
            100500,
            404,
            {
                'code': 'META_WIDGET_NOT_FOUND',
                'message': 'Meta widget with id \'100500\' is not found',
            },
        ),
    ],
)
async def test_get_meta_widgets(
        taxi_eats_layout_constructor,
        mockserver,
        service_source_dir,
        meta_widget_type,
        meta_widget_id,
        expected_status,
        expected_data,
):
    response = await taxi_eats_layout_constructor.get(
        'layout-constructor/v1/constructor/meta-widgets/',
        params={'meta_widget_id': meta_widget_id},
    )
    if meta_widget_type:
        expected_data['settings_schema'] = get_meta_widget_settings_schema(
            service_source_dir, meta_widget_type,
        )

    assert response.status == expected_status
    assert response.json() == expected_data
