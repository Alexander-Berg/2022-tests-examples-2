import pytest

from eats_layout_constructor import configs
import eats_layout_constructor.utils as utils


def make_layout_widget(url_id, widget_template_id=1, meta=None, payload=None):
    if not payload:
        payload = {'field_4': 'value_5'}
    return {
        'url_id': url_id,
        'meta': (
            meta
            if meta is not None
            else {'field_3': 'value_4', 'format': 'classic'}
        ),
        'meta_schema': {},
        'name': 'Widget',
        'payload': payload,
        'template_meta': {'field_1': 'value_1'},
        'template_payload': {'field_2': 'value_2'},
        'widget_template_id': widget_template_id,
    }


def make_input_data(*widgets):
    return {'name': 'Layout (updated)', 'widgets': list(widgets)}


@pytest.mark.parametrize(
    'layout_id,input_data,expected_status,expected_data',
    [
        (
            1,
            make_input_data(
                make_layout_widget(
                    1,
                    payload={
                        'field_4': 'value_5',
                        'background_color_dark': '#ffffff',
                    },
                ),
                make_layout_widget(None),
            ),
            200,
            {
                'id': 1,
                'name': 'Layout (updated)',
                'slug': 'layout_1',
                'published': False,
                'author': 'nevladov',
                'widgets': [
                    {
                        'id': '1_banners',
                        'url_id': 1,
                        'widget_template_id': 1,
                        'type': 'banners',
                        'name': 'Widget',
                        'template_meta': {'field_1': 'value_1'},
                        'meta': {'field_3': 'value_4', 'format': 'classic'},
                        'payload_schema': {'type': 'object'},
                        'template_payload': {'field_2': 'value_2'},
                        'payload': {
                            'field_4': 'value_5',
                            'background_color_dark': '#ffffff',
                        },
                    },
                    {
                        'id': '3_banners',
                        'url_id': 3,
                        'widget_template_id': 1,
                        'type': 'banners',
                        'name': 'Widget',
                        'template_meta': {'field_1': 'value_1'},
                        'meta': {'field_3': 'value_4', 'format': 'classic'},
                        'payload_schema': {'type': 'object'},
                        'template_payload': {'field_2': 'value_2'},
                        'payload': {'field_4': 'value_5'},
                    },
                ],
            },
        ),
        (
            2,
            make_input_data(make_layout_widget(None)),
            200,
            {
                'id': 2,
                'name': 'Layout (updated)',
                'slug': 'layout_2',
                'published': False,
                'author': 'nevladov',
                'widgets': [
                    {
                        'id': '3_banners',
                        'url_id': 3,
                        'widget_template_id': 1,
                        'type': 'banners',
                        'name': 'Widget',
                        'template_meta': {'field_1': 'value_1'},
                        'meta': {'field_3': 'value_4', 'format': 'classic'},
                        'payload_schema': {'type': 'object'},
                        'template_payload': {'field_2': 'value_2'},
                        'payload': {'field_4': 'value_5'},
                    },
                ],
            },
        ),
        (
            3,
            make_input_data(make_layout_widget(None)),
            404,
            {
                'code': 'LAYOUT_IS_NOT_FOUND',
                'message': 'Layout with id \'3\' is not found',
            },
        ),
        (
            1,
            make_input_data(
                make_layout_widget(
                    None, payload={'background_color_dark': '#fffff'},
                ),
            ),
            400,
            {
                'code': 'WidgetValidationError',
                'message': (
                    'Widget with type \'banners\' is not valid: '
                    '\'#fffff\' is not valid hex color for key '
                    '\'background_color_dark\''
                ),
            },
        ),
    ],
)
async def test_put_layout(
        taxi_eats_layout_constructor,
        mockserver,
        layout_id,
        input_data,
        expected_status,
        expected_data,
):
    response = await taxi_eats_layout_constructor.put(
        'layout-constructor/v1/constructor/layouts/',
        params={'layout_id': layout_id},
        json=input_data,
    )
    assert response.status == expected_status
    data = response.json()
    if expected_status == 200:
        data.pop('created')
        for widget in data['widgets']:
            widget.pop('meta_schema')
    assert data == expected_data


@pytest.mark.config(
    EATS_LAYOUT_CONSTRUCTOR_EXPERIMENT_SETTINGS={
        'check_experiment': True,
        'refresh_period_ms': 1,
        'experiment_name': 'experiment_1',
    },
)
@pytest.mark.parametrize(
    'layout_id,input_data,expected_status,expected_data',
    [
        (
            1,
            make_input_data(make_layout_widget(1), make_layout_widget(None)),
            200,
            None,
        ),
        (
            100,
            make_input_data(make_layout_widget(1), make_layout_widget(None)),
            400,
            {
                'code': 'LAYOUT_IS_ALREADY_PUBLISHED',
                'message': (
                    'Layout with slug \'layout_100\' is not editable cause it '
                    'is already published'
                ),
            },
        ),
        (
            101,
            make_input_data(make_layout_widget(1), make_layout_widget(None)),
            400,
            {
                'code': 'LAYOUT_IS_ALREADY_PUBLISHED',
                'message': (
                    'Layout with slug \'layout_101\' is not editable cause it '
                    'is already published'
                ),
            },
        ),
        (
            1,
            make_input_data(
                make_layout_widget(1, meta={'format': 'shortshortcut'}),
            ),
            400,
            {
                'code': 'WidgetValidationError',
                'message': (
                    'Widget with type \'banners\' is not valid: '
                    'Value of \'format\' '
                    '(shortshortcut) is not parseable into enum'
                ),
            },
        ),
    ],
)
async def test_put_published_layout(
        taxi_eats_layout_constructor,
        mockserver,
        layout_id,
        input_data,
        expected_status,
        expected_data,
):
    await taxi_eats_layout_constructor.run_periodic_task('layout-status')
    response = await taxi_eats_layout_constructor.put(
        'layout-constructor/v1/constructor/layouts/',
        params={'layout_id': layout_id},
        json=input_data,
    )
    assert response.status == expected_status
    data = response.json()
    if expected_data is not None:
        assert data == expected_data


@configs.fallback_layout('layout_100', collection_slug='layout_101')
@pytest.mark.parametrize(
    'layout_id,input_data,expected_status,expected_data',
    [
        (
            1,
            make_input_data(make_layout_widget(1), make_layout_widget(None)),
            200,
            None,
        ),
        (
            100,
            make_input_data(make_layout_widget(1), make_layout_widget(None)),
            400,
            {
                'code': 'LAYOUT_IS_FALLBACK',
                'message': (
                    'Layout with slug \'layout_100\' is not editable '
                    'because it is used as fallback.'
                ),
            },
        ),
        (
            101,
            make_input_data(make_layout_widget(1), make_layout_widget(None)),
            400,
            {
                'code': 'LAYOUT_IS_FALLBACK',
                'message': (
                    'Layout with slug \'layout_101\' is not editable '
                    'because it is used as fallback.'
                ),
            },
        ),
    ],
)
async def test_put_fallback_layout(
        taxi_eats_layout_constructor,
        layout_id,
        input_data,
        expected_status,
        expected_data,
):
    await taxi_eats_layout_constructor.run_periodic_task('layout-status')
    response = await taxi_eats_layout_constructor.put(
        'layout-constructor/v1/constructor/layouts/',
        params={'layout_id': layout_id},
        json=input_data,
    )
    assert response.status == expected_status
    data = response.json()
    if expected_data is not None:
        assert data == expected_data


async def test_put_published_layout_add_deprecated_widget(
        taxi_eats_layout_constructor, mockserver,
):
    """
    Проверяем что нельзя добавить в существующий лэйаут
    виджеты устаревшего типа
    """

    layout_data = make_input_data(make_layout_widget(1, widget_template_id=2))

    await taxi_eats_layout_constructor.run_periodic_task('layout-status')
    response = await taxi_eats_layout_constructor.put(
        'layout-constructor/v1/constructor/layouts/',
        params={'layout_id': 1},
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


async def test_put_published_layout_with_deprecated_widget(
        taxi_eats_layout_constructor,
        layouts,
        widget_templates,
        layout_widgets,
):
    """
    Проверяем что если в лэйауте уже содержится устаревший виджет,
    то обновление лэйаута не приводит к ошибке
    """

    layout_id = 10
    widget_template_id = 11
    widget_id = 12

    layouts.add_layout(
        utils.Layout(layout_id=layout_id, name='layout1', slug='layout1'),
    )
    widget_templates.add_widget_template(
        utils.WidgetTemplate(
            widget_template_id=widget_template_id,
            type='places_list',
            name='list',
            meta={},
            payload={},
            payload_schema={},
        ),
    )
    layout_widgets.add_layout_widget(
        utils.LayoutWidget(
            name='widget1',
            url_id=widget_id,
            widget_template_id=widget_template_id,
            layout_id=layout_id,
            meta={},
            payload={},
        ),
    )

    layout_data = make_input_data(
        make_layout_widget(
            url_id=widget_id,
            widget_template_id=widget_template_id,
            meta={'place_filter_type': 'open'},
        ),
    )

    response = await taxi_eats_layout_constructor.put(
        'layout-constructor/v1/constructor/layouts/',
        params={'layout_id': layout_id},
        json=layout_data,
    )

    assert response.status == 200
