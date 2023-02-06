import pytest


@pytest.mark.parametrize(
    'meta_widget_id,expected_status,expected_data',
    [
        (
            1,
            400,
            {
                'code': 'deletion_error',
                'message': (
                    'Can\'t delete meta_widget which '
                    'currently in use. Layout slugs: [layout_1].'
                ),
            },
        ),
        (2, 200, {}),
        (100500, 200, {}),
    ],
)
async def test_delete_meta_widgets(
        taxi_eats_layout_constructor,
        mockserver,
        meta_widget_id,
        expected_status,
        expected_data,
):
    response = await taxi_eats_layout_constructor.delete(
        'layout-constructor/v1/constructor/meta-widgets/',
        params={'meta_widget_id': meta_widget_id},
    )
    assert response.status == expected_status
    assert response.json() == expected_data
