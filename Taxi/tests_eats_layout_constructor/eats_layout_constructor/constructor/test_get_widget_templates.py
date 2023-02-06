import pytest

from testsuite.utils import yaml_util


def get_widget_meta(source_dir, widget_type):
    data = yaml_util.load_file(
        source_dir / 'src/widgets' / widget_type / 'meta.yaml',
    )

    return data['meta']


@pytest.mark.parametrize(
    'widget_type,widget_template_id,expected_status,expected_data',
    [
        (
            'banners',
            1,
            200,
            {
                'id': 1,
                'type': 'banners',
                'name': 'Widget template 1',
                'meta': {'field_1': 'value_1'},
                'payload_schema': {'type': 'object'},
                'payload': {'field_2': 'value_2'},
            },
        ),
        (
            'places_carousel',
            2,
            200,
            {
                'id': 2,
                'type': 'places_carousel',
                'name': 'Widget template 2',
                'meta': {'field_1': 'value_1'},
                'payload_schema': {'type': 'object'},
                'payload': {'field_2': 'value_2'},
            },
        ),
        (
            '',
            100,
            404,
            {
                'code': 'WIDGET_TEMPLATE_IS_NOT_FOUND',
                'message': 'Widget template with id \'100\' is not found',
            },
        ),
    ],
)
async def test_get_widget_templates(
        taxi_eats_layout_constructor,
        mockserver,
        service_source_dir,
        widget_type,
        widget_template_id,
        expected_status,
        expected_data,
):

    response = await taxi_eats_layout_constructor.get(
        'layout-constructor/v1/constructor/widget-templates/',
        params={'widget_template_id': widget_template_id},
    )
    if widget_type:
        expected_data['meta_schema'] = get_widget_meta(
            service_source_dir, widget_type,
        )

    assert response.status == expected_status
    assert response.json() == expected_data
