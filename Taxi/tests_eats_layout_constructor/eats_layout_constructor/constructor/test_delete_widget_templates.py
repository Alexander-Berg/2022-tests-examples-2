import pytest


@pytest.mark.parametrize(
    'widget_template_id,expected_status,expected_data',
    [
        (
            1,
            400,
            {
                'code': 'deletion_error',
                'message': (
                    'Can\'t delete widget template which '
                    'currently in use. Layout slugs: [layout_2].'
                ),
            },
        ),
        (2, 200, {}),
        (100500, 200, {}),
    ],
)
async def test_delete_widget_templates(
        taxi_eats_layout_constructor,
        mockserver,
        widget_template_id,
        expected_status,
        expected_data,
):
    response = await taxi_eats_layout_constructor.delete(
        'layout-constructor/v1/constructor/widget-templates/',
        params={'widget_template_id': widget_template_id},
    )
    assert response.status == expected_status
    assert response.json() == expected_data
