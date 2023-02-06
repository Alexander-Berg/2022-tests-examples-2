import pytest


@pytest.mark.parametrize(
    'input_data,expected_status,expected_data,strict_match',
    [
        (
            {
                'name': 'Layout 2',
                'slug': 'layout_3',
                'widgets': [
                    {
                        'meta': {'field_1': 'value_3', 'format': 'shortcut'},
                        'name': 'Widget 1',
                        'slug': 'layout_1',
                        'payload': {
                            'field_1': 'value_3',
                            'background_color_dark': '#ffffff',
                        },
                        'template_meta': {'field_1': 'value_1'},
                        'template_payload': {'field_2': 'value_2'},
                        'widget_template_id': 1,
                    },
                    {
                        'meta': {'field_1': 'value_3', 'format': 'classic'},
                        'name': 'Widget 2',
                        'payload': {'field_1': [1, 2, 3], 'field_2': 1},
                        'template_meta': {'field_1': 'value_1'},
                        'template_payload': {'field_2': 'value_2'},
                        'widget_template_id': 1,
                    },
                ],
            },
            200,
            {
                'id': 3,
                'name': 'Layout 2',
                'slug': 'layout_3',
                'published': False,
                'author': 'nevladov',
                'widgets': [
                    {
                        'id': '3_banners',
                        'url_id': 3,
                        'widget_template_id': 1,
                        'type': 'banners',
                        'name': 'Widget 1',
                        'template_meta': {'field_1': 'value_1'},
                        'meta': {'field_1': 'value_3', 'format': 'shortcut'},
                        'payload_schema': {'type': 'object'},
                        'template_payload': {'field_2': 'value_2'},
                        'payload': {
                            'field_1': 'value_3',
                            'background_color_dark': '#ffffff',
                        },
                    },
                    {
                        'id': '4_banners',
                        'url_id': 4,
                        'widget_template_id': 1,
                        'type': 'banners',
                        'name': 'Widget 2',
                        'template_meta': {'field_1': 'value_1'},
                        'meta': {'field_1': 'value_3', 'format': 'classic'},
                        'payload_schema': {'type': 'object'},
                        'template_payload': {'field_2': 'value_2'},
                        'payload': {'field_1': [1, 2, 3], 'field_2': 1},
                    },
                ],
            },
            True,
        ),
        (
            {'name': 'Layout 2', 'slug': 'layout_2', 'widgets': []},
            409,
            {
                'code': 'SLUG_IS_ALREADY_EXIST',
                'message': 'Layout with slug \'layout_2\' is already exist',
            },
            True,
        ),
        (
            {'name': 'Layout 2', 'widgets': []},
            400,
            {'code': 'SLUG_IS_REQUIRED', 'message': 'slug is required'},
            True,
        ),
        (
            {
                'name': 'Layout 2',
                'slug': 'layout_3',
                'widgets': [
                    {
                        'meta': {'banners_id': '1'},
                        'name': 'Widget 1',
                        'slug': 'layout_1',
                        'payload': {'field_1': 'value_3'},
                        'template_meta': {'field_1': 'value_1'},
                        'template_payload': {'field_2': 'value_2'},
                        'widget_template_id': 1,
                    },
                ],
            },
            400,
            {'code': 'WidgetValidationError'},
            False,
        ),
        (
            {
                'name': 'Layout 2',
                'slug': 'layout_3',
                'widgets': [
                    {
                        'meta': {'banners_id': '1'},
                        'name': 'Widget 1',
                        'slug': 'layout_1',
                        'payload': {'field_1': 'value_3'},
                        'template_meta': {'field_1': 'value_1'},
                        'template_payload': {'field_2': 'value_2'},
                        'widget_template_id': 10,
                    },
                ],
            },
            400,
            {
                'code': 'UNKNOWN_WIDGET_TEMPLATE_ID',
                'message': 'Unknown widget template id \'10\'',
            },
            True,
        ),
        (
            {
                'name': 'Layout 2',
                'slug': 'layout_3',
                'widgets': [
                    {
                        'meta': {'field_1': 'value_3', 'format': 'shortcut'},
                        'name': 'Widget 1',
                        'slug': 'layout_1',
                        'payload': {
                            'field_1': 'value_3',
                            'background_color_dark': 'ffffff',
                            'background_color_light': '#000',
                        },
                        'template_meta': {'field_1': 'value_1'},
                        'template_payload': {'field_2': 'value_2'},
                        'widget_template_id': 1,
                    },
                ],
            },
            400,
            {
                'code': 'WidgetValidationError',
                'message': (
                    'Widget with type \'banners\' is not valid: '
                    '\'ffffff\' is not valid hex color for key '
                    '\'background_color_dark\''
                ),
            },
            True,
        ),
        (
            {
                'name': 'Layout with multiple popups',
                'slug': 'layout_with_popups',
                'widgets': [
                    {
                        'meta': {
                            'experiments': [],
                            'size': {'width': 0, 'height': 0},
                        },
                        'name': 'Popup 1',
                        'slug': 'popup_1',
                        'payload': {},
                        'template_meta': {},
                        'template_payload': {},
                        'widget_template_id': 3,
                    },
                    {
                        'meta': {
                            'experiments': [],
                            'size': {'width': 0, 'height': 0},
                        },
                        'name': 'Popup 2',
                        'slug': 'popup_2',
                        'payload': {},
                        'template_meta': {},
                        'template_payload': {},
                        'widget_template_id': 3,
                    },
                ],
            },
            400,
            {
                'code': 'MultiplePopups',
                'message': (
                    'Multiple widgets of type popup_banner '
                    'in same layout does not allowed'
                ),
            },
            True,
        ),
    ],
)
async def test_post_layout(
        taxi_eats_layout_constructor,
        mockserver,
        input_data,
        expected_status,
        expected_data,
        strict_match,
):
    response = await taxi_eats_layout_constructor.post(
        'layout-constructor/v1/constructor/layouts/',
        headers={'X-Yandex-Login': 'nevladov'},
        json=input_data,
    )
    assert response.status == expected_status
    data = response.json()
    if expected_status == 200:
        data.pop('created')
        for widget in data['widgets']:
            widget.pop('meta_schema')

    if strict_match:
        assert data == expected_data
    else:
        assert data['code'] == expected_data['code']


async def test_post_layout_with_deprecated_widgets(
        taxi_eats_layout_constructor,
):
    """
    Проверяем что нельзя создать новый лэйаут с устаревшим
    типом виджетов
    """

    layout_data = {
        'name': 'layout 1',
        'slug': 'layout_1',
        'widgets': [
            {
                'meta': {},
                'name': 'Widget 1',
                'slug': 'widget_1',
                'payload': {},
                'template_meta': {},
                'template_payload': {},
                'widget_template_id': 2,
            },
        ],
    }

    response = await taxi_eats_layout_constructor.post(
        'layout-constructor/v1/constructor/layouts/',
        headers={'X-Yandex-Login': 'egor-sorokin'},
        json=layout_data,
    )
    assert response.status == 400
    data = response.json()
    assert data == {
        'code': 'DeprecatedWidgetTemplateTypeError',
        'message': (
            'Widget template type \'places_carousel\' is deprecated. '
            'Consider to use \'places_collection\' instead.'
        ),
    }
