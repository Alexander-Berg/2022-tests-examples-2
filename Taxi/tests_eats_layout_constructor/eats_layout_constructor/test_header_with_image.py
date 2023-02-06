import pytest

from . import configs
from . import experiments
from . import utils

HEADERS = {
    'x-device-id': 'id',
    'x-platform': 'android_app',
    'x-app-version': '12.11.12',
    'cookie': '{}',
    'X-Eats-User': 'user_id=' + utils.EATER_ID,
    'x-request-application': 'application=1.1.0',
    'x-request-language': 'enUS',
    'Content-Type': 'application/json',
}


def get_single_data(
        id_=1,
        right_button_image=None,
        right_button_deeplink=None,
        image_url='',
):
    payload = {
        'image_url': {'light': image_url['light'], 'dark': image_url['dark']},
    }
    if right_button_image is not None:
        payload['right_button_image'] = {
            'light': right_button_image['light'],
            'dark': right_button_image['dark'],
        }
    if right_button_deeplink is not None:
        payload['right_button_deeplink'] = {
            'app': right_button_deeplink['app'],
            'web': right_button_deeplink['web'],
        }
    return {
        'payload': payload,
        'id': f'{id_}_header_with_image',
        'template_name': 'Header_with_image',
    }


def get_single_layout(
        id_=1,
        background_color_dark='#ffffff',
        background_color_light='#000000',
):
    return {
        'id': f'{id_}_header_with_image',
        'payload': {
            'background_color_dark': background_color_dark,
            'background_color_light': background_color_light,
        },
        'type': 'header_with_image',
    }


def create_widget(
        image_url,
        id_=1,
        background_color_dark='#ffffff',
        background_color_light='#000000',
        right_button_image=None,
        right_button_deeplink=None,
        depends_on_any=tuple(),
):
    return utils.WidgetTemplate(
        widget_template_id=id_,
        type='header_with_image',
        name='Header_with_image',
        meta={
            'right_button_image': right_button_image,
            'right_button_deeplink': right_button_deeplink,
            'image_url': image_url,
            'depends_on_any': depends_on_any,
        },
        payload={
            'background_color_dark': background_color_dark,
            'background_color_light': background_color_light,
        },
        payload_schema={},
    )


def add_layout_widget(layout_widgets, widget_template, layout_id):
    widget = utils.LayoutWidget(
        name=widget_template.name,
        widget_template_id=widget_template.widget_template_id,
        layout_id=layout_id,
        meta={},
        payload={},
    )

    layout_widgets.add_layout_widget(widget)


@configs.keep_empty_layout()
@experiments.layout('layout_1')
@configs.layout_experiment_name()
async def test_eats_layout_header_with_image_basic(
        taxi_eats_layout_constructor, single_widget_layout,
):
    """
        Тест проверяет, корректное заполнение полей виджета
    """
    widget = create_widget(
        right_button_image={
            'light': 'right_button_image_light',
            'dark': 'right_button_image_dark',
        },
        right_button_deeplink={
            'app': 'right_button_deeplink_app',
            'web': 'right_button_deeplink_web',
        },
        image_url={'light': 'image_url_light', 'dark': 'image_url_dark'},
    )
    single_widget_layout('layout_1', widget)

    response = await taxi_eats_layout_constructor.post(
        'eats/v1/layout-constructor/v1/layout',
        headers=HEADERS,
        json={'location': {'latitude': 0.0, 'longitude': 0.0}},
    )
    expected_response = {
        'data': {
            'headers_with_image': [
                get_single_data(
                    right_button_image={
                        'light': 'right_button_image_light',
                        'dark': 'right_button_image_dark',
                    },
                    right_button_deeplink={
                        'app': 'right_button_deeplink_app',
                        'web': 'right_button_deeplink_web',
                    },
                    image_url={
                        'light': 'image_url_light',
                        'dark': 'image_url_dark',
                    },
                ),
            ],
        },
        'layout': [get_single_layout()],
    }

    assert response.status_code == 200
    assert response.json() == expected_response


@configs.keep_empty_layout()
@experiments.layout('layout_1')
@configs.layout_experiment_name()
async def test_eats_layout_header_with_image_empty(
        taxi_eats_layout_constructor, single_widget_layout,
):
    """
        Если не заданы необязательные поля в meta, их не будет в ответе
    """
    widget = create_widget(
        image_url={'light': 'image_url_light', 'dark': 'image_url_dark'},
    )
    single_widget_layout('layout_1', widget)

    response = await taxi_eats_layout_constructor.post(
        'eats/v1/layout-constructor/v1/layout',
        headers=HEADERS,
        json={'location': {'latitude': 0.0, 'longitude': 0.0}},
    )
    expected_response = {
        'data': {
            'headers_with_image': [
                get_single_data(
                    image_url={
                        'light': 'image_url_light',
                        'dark': 'image_url_dark',
                    },
                ),
            ],
        },
        'layout': [get_single_layout()],
    }

    assert response.status_code == 200
    assert response.json() == expected_response


@configs.keep_empty_layout()
@experiments.layout('layout_1')
@configs.layout_experiment_name()
@pytest.mark.parametrize('first_dep_widget', [True, False])
@pytest.mark.parametrize('second_dep_widget', [True, False])
async def test_eats_layout_header_with_image_dependence(
        taxi_eats_layout_constructor,
        layouts,
        widget_templates,
        layout_widgets,
        first_dep_widget,
        second_dep_widget,
):
    """
        Если в depends_on_any проставлены существующие в выдаче виджеты,
        виджет выдаётся иначе нет
    """
    layout = utils.Layout(layout_id=1, name='layout_1', slug='layout_1')
    layouts.add_layout(layout)
    widget_count = 0
    if first_dep_widget:
        widget_1 = create_widget(
            id_=1,
            image_url={'light': 'image_url_light', 'dark': 'image_url_dark'},
        )
        widget_templates.add_widget_template(widget_1)
        add_layout_widget(layout_widgets, widget_1, layout.layout_id)
        widget_count += 1

    if second_dep_widget:
        widget_2 = create_widget(
            id_=2,
            image_url={'light': 'image_url_light', 'dark': 'image_url_dark'},
        )
        widget_templates.add_widget_template(widget_2)
        add_layout_widget(layout_widgets, widget_2, layout.layout_id)
        widget_count += 1

    widget = create_widget(
        id_=3,
        right_button_image={
            'light': 'right_button_image_light',
            'dark': 'right_button_image_dark',
        },
        right_button_deeplink={
            'app': 'right_button_deeplink_app',
            'web': 'right_button_deeplink_web',
        },
        image_url={'light': 'image_url_light', 'dark': 'image_url_dark'},
        depends_on_any=['1_header_with_image', '2_header_with_image'],
    )

    widget_templates.add_widget_template(widget)
    add_layout_widget(layout_widgets, widget, layout.layout_id)
    if first_dep_widget or second_dep_widget:
        widget_count += 1

    response = await taxi_eats_layout_constructor.post(
        'eats/v1/layout-constructor/v1/layout',
        headers=HEADERS,
        json={'location': {'latitude': 0.0, 'longitude': 0.0}},
    )

    assert response.status_code == 200
    assert len(response.json()['layout']) == widget_count
    if widget_count == 0:
        assert 'header_with_image' not in response.json()['data']
    else:
        assert (
            len(response.json()['data']['headers_with_image']) == widget_count
        )
