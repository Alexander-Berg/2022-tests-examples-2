import copy

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

TEXT_ONLY_RESPONSE = {
    'data': {
        'informers': [
            {
                'id': '1_informer',
                'payload': {
                    'text': {
                        'color': [
                            {'theme': 'dark', 'value': '#ffffff'},
                            {'theme': 'light', 'value': '#000000'},
                        ],
                        'text': 'text',
                    },
                },
                'template_name': 'Informer',
            },
        ],
    },
    'layout': [{'id': '1_informer', 'payload': {}, 'type': 'informer'}],
}

ALL_DATA_RESPONSE = {
    'data': {
        'informers': [
            {
                'id': '1_informer',
                'payload': {
                    'text': {
                        'color': [
                            {'theme': 'dark', 'value': '#ffffff'},
                            {'theme': 'light', 'value': '#000000'},
                        ],
                        'text': 'text',
                    },
                    'background_color': [
                        {'theme': 'dark', 'value': '#000000'},
                        {'theme': 'light', 'value': '#ffffff'},
                    ],
                    'icon': [
                        {'theme': 'light', 'icon': 'l'},
                        {'theme': 'dark', 'icon': 'd'},
                    ],
                    'link': 'link',
                },
                'template_name': 'Informer',
            },
        ],
    },
    'layout': [{'id': '1_informer', 'payload': {}, 'type': 'informer'}],
}


def create_widget(
        id_=1, background_color=None, link=None, icon=None, max_orders=None,
):
    return utils.WidgetTemplate(
        widget_template_id=id_,
        type='informer',
        name='Informer',
        meta={
            'text': {
                'text': 'text',
                'color': [
                    {'theme': 'dark', 'color': '#ffffff'},
                    {'theme': 'light', 'color': '#000000'},
                ],
            },
            'background_color': background_color,
            'link': link,
            'icon': icon,
            'max_orders': max_orders,
        },
        payload={},
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
async def test_eats_layout_informer_text(
        taxi_eats_layout_constructor, single_widget_layout,
):
    # Тест проверяет, что если опциональные поля не заданны, они не приходят
    # с виджетом
    widget = create_widget()
    single_widget_layout('layout_1', widget)

    response = await taxi_eats_layout_constructor.post(
        'eats/v1/layout-constructor/v1/layout',
        headers=HEADERS,
        json={'location': {'latitude': 0.0, 'longitude': 0.0}},
    )

    assert response.status_code == 200
    assert response.json() == TEXT_ONLY_RESPONSE


@configs.keep_empty_layout()
@experiments.layout('layout_1')
@configs.layout_experiment_name()
@pytest.mark.parametrize('max_orders', [None, 4, 3, 2])
@pytest.mark.parametrize('has_orders', [True, False])
async def test_eats_layout_informer_all_data(
        taxi_eats_layout_constructor,
        mockserver,
        single_widget_layout,
        max_orders,
        has_orders,
):
    # Тест проверяет работу ограничения по max_orders и,
    # что все поля приходят корректно
    @mockserver.json_handler(
        '/eats-order-stats/internal/eats-order-stats/v1/orders',
    )
    def _moc_order_stats(request):
        return utils.order_stats_response(3 if has_orders else 0)

    widget = create_widget(
        background_color=[
            {'theme': 'dark', 'color': '#000000'},
            {'theme': 'light', 'color': '#ffffff'},
        ],
        icon=[{'theme': 'light', 'icon': 'l'}, {'theme': 'dark', 'icon': 'd'}],
        link='link',
        max_orders=max_orders,
    )
    single_widget_layout('layout_1', widget)

    response = await taxi_eats_layout_constructor.post(
        'eats/v1/layout-constructor/v1/layout',
        headers=HEADERS,
        json={'location': {'latitude': 0.0, 'longitude': 0.0}},
    )

    assert response.status_code == 200
    result = response.json()

    if has_orders and max_orders is not None and max_orders <= 3:
        assert not result['data']
        return

    assert result == ALL_DATA_RESPONSE


@configs.keep_empty_layout()
@experiments.layout('layout_1')
@configs.layout_experiment_name()
@pytest.mark.parametrize('max_orders', [None, 1])
async def test_eats_layout_informer_empty_user_id(
        taxi_eats_layout_constructor,
        mockserver,
        single_widget_layout,
        max_orders,
):
    """
        Проверка на выдачу информера для незалогиненного пользователя
    """
    widget = create_widget(
        background_color=[
            {'theme': 'dark', 'color': '#000000'},
            {'theme': 'light', 'color': '#ffffff'},
        ],
        icon=[{'theme': 'light', 'icon': 'l'}, {'theme': 'dark', 'icon': 'd'}],
        link='link',
        max_orders=max_orders,
    )
    single_widget_layout('layout_1', widget)

    request_headers = copy.deepcopy(HEADERS)
    request_headers['X-Eats-User'] = ''

    response = await taxi_eats_layout_constructor.post(
        'eats/v1/layout-constructor/v1/layout',
        headers=request_headers,
        json={'location': {'latitude': 0.0, 'longitude': 0.0}},
    )
    result = response.json()
    assert response.status_code == 200
    assert result == ALL_DATA_RESPONSE


@configs.keep_empty_layout()
@experiments.layout('layout_1')
@configs.layout_experiment_name()
@pytest.mark.parametrize('first_max_orders', [None, 4, 3, 2])
@pytest.mark.parametrize('second_max_orders', [None, 4, 3, 2])
async def test_eats_layout_informers_max_orders(
        taxi_eats_layout_constructor,
        mockserver,
        widget_templates,
        layout_widgets,
        layouts,
        first_max_orders,
        second_max_orders,
):
    # Тест проверяет работу ограничения по max_orders в случае с layout'ом
    # который содержит несколько informer widget

    layout = utils.Layout(layout_id=1, name='layout_1', slug='layout_1')
    layouts.add_layout(layout)
    widget_1 = create_widget(id_=1, max_orders=first_max_orders)
    widget_2 = create_widget(id_=2, max_orders=second_max_orders)
    widget_templates.add_widget_template(widget_1)
    widget_templates.add_widget_template(widget_2)
    add_layout_widget(layout_widgets, widget_1, layout.layout_id)
    add_layout_widget(layout_widgets, widget_2, layout.layout_id)

    @mockserver.json_handler(
        '/eats-order-stats/internal/eats-order-stats/v1/orders',
    )
    def _moc_order_stats(request):
        return utils.order_stats_response(3)

    response = await taxi_eats_layout_constructor.post(
        'eats/v1/layout-constructor/v1/layout',
        headers=HEADERS,
        json={'location': {'latitude': 0.0, 'longitude': 0.0}},
    )

    assert response.status_code == 200
    result = response.json()

    if (
            first_max_orders is not None
            and second_max_orders is not None
            and first_max_orders <= 3
            and second_max_orders <= 3
    ):
        assert not result['data']
        return

    informers = {informer['id'] for informer in result['data']['informers']}

    if first_max_orders is None or first_max_orders > 3:
        assert '1_informer' in informers

    if second_max_orders is None or second_max_orders > 3:
        assert '2_informer' in informers


@configs.keep_empty_layout()
@experiments.layout('layout_1')
@configs.layout_experiment_name()
@pytest.mark.parametrize('network_code', [200, 400, 500, None])
async def test_eats_layout_informer_wrong_data(
        taxi_eats_layout_constructor,
        mockserver,
        single_widget_layout,
        network_code,
):
    # Тест проверяет работу виджета при некорректном ответе eats-order-stats
    @mockserver.json_handler(
        '/eats-order-stats/internal/eats-order-stats/v1/orders',
    )
    def _moc_order_stats(request):
        if not network_code:
            raise mockserver.NetworkError()
        if network_code == 200:
            return {
                'data': [
                    {
                        'identity': {
                            'type': 'eater_id',
                            'value': utils.EATER_ID,
                        },
                        'counters': [
                            {
                                'properties': [
                                    {
                                        'name': 'business_type',
                                        'value': 'retail',
                                    },
                                ],
                                'value': -3,
                                'first_order_at': '2021-08-19T13:04:05+0000',
                                'last_order_at': '2021-09-19T13:04:05+0000',
                            },
                        ],
                    },
                ],
            }
        return mockserver.make_response(status=network_code)

    widget = create_widget(max_orders=10)
    single_widget_layout('layout_1', widget)

    response = await taxi_eats_layout_constructor.post(
        'eats/v1/layout-constructor/v1/layout',
        headers=HEADERS,
        json={'location': {'latitude': 0.0, 'longitude': 0.0}},
    )

    assert response.status_code == 200
    assert not response.json()['data']
