import copy

import pytest

from eats_layout_constructor import configs
from eats_layout_constructor import experiments

CATALOG_HANDLER = '/eats-catalog/internal/v1/catalog-for-layout'
REPEAT_ORDER_HANDLER = '/eats-repeat-order/v1/get-orders'
LAYOUT_CONSTRUCTOR_HANDLER = {
    'path': '/eats/v1/layout-constructor/v1/layout',
    'headers': {
        'x-device-id': 'dev_id',
        'x-platform': 'android_app',
        'x-app-version': '12.11.12',
        'cookie': '{}',
        'X-Eats-User': 'user_id=12345',
        'x-request-application': 'application=1.1.0',
        'x-request-language': 'enUS',
        'Content-Type': 'application/json',
    },
    'json': {'location': {'latitude': 0.0, 'longitude': 0.0}},
}
ACTION_SETTINGS = {
    'icon_url': 'asset://repeat_order',
    'title_prefix': 'Повторим?',
    'accent_color': [{'theme': 'light', 'value': '#169CDC'}],
    'experiment_name': 'eats_layout_constructor_actions_repeat_order',
}


def check_layouts(layouts, expected_layouts):
    has_layout = False
    for layout in layouts:
        if layout['type'] == 'actions':
            for layout_data in layout['layout']:
                has_layout = True
                assert layout_data in expected_layouts
    return has_layout


@configs.layout_experiment_name()
@experiments.layout('test_place_layout')
async def test_has_only_repeat_order_actions(
        taxi_eats_layout_constructor, mockserver, load_json,
):
    # тест проверяет, что рестораны содержат только акции
    # с типом `repeat_order`
    @mockserver.json_handler(CATALOG_HANDLER)
    def _catalog(request):
        return load_json('catalog-1.json')

    @mockserver.json_handler(REPEAT_ORDER_HANDLER)
    def _mock_eats_repeat_order(request):
        assert request.json['user_id'] == 12345
        return load_json('repeat-order-1.json')

    response = await taxi_eats_layout_constructor.post(
        LAYOUT_CONSTRUCTOR_HANDLER['path'],
        headers=LAYOUT_CONSTRUCTOR_HANDLER['headers'],
        json=LAYOUT_CONSTRUCTOR_HANDLER['json'],
    )

    assert response.status_code == 200
    has_actions = False
    has_layout = False
    expected_layouts_data = []
    for place_list in response.json()['data']['places_lists']:
        for place in place_list['payload']['places']:
            if 'actions' in place['data']:
                for action in place['data']['actions']:
                    has_actions = True
                    assert action['type'] == 'repeat_order'
                    expected_layouts_data.append(
                        {'id': action['id'], 'type': action['type']},
                    )
                has_layout = check_layouts(
                    place['layout'], expected_layouts_data,
                )
    assert has_actions
    assert has_layout


@configs.layout_experiment_name()
@experiments.layout('test_place_layout')
async def test_empty_eats_user_id(
        taxi_eats_layout_constructor, mockserver, load_json,
):
    # тест проверяет, что фетчер `repeat_order_fetcher`
    # не отрабатывает в случае отсутсвия идентификатора пользователя я.еда
    # (`eats_user_id`)
    @mockserver.json_handler(CATALOG_HANDLER)
    def _catalog(request):
        return load_json('catalog-1.json')

    @mockserver.json_handler(REPEAT_ORDER_HANDLER)
    def _mock_eats_repeat_order(request):
        assert request.json['user_id'] == 12345
        assert False, 'this call should not be made'
        return {}

    headers = copy.deepcopy(LAYOUT_CONSTRUCTOR_HANDLER['headers'])
    headers['X-Eats-User'] = ''
    response = await taxi_eats_layout_constructor.post(
        LAYOUT_CONSTRUCTOR_HANDLER['path'],
        headers=headers,
        json=LAYOUT_CONSTRUCTOR_HANDLER['json'],
    )

    assert response.status_code == 200
    for place_list in response.json()['data']['places_lists']:
        for place in place_list['payload']['places']:
            if 'actions' in place['data']:
                for action in place['data']['actions']:
                    assert action['type'] != 'repeat_order'
            for layout in place['layout']:
                if layout['type'] == 'actions':
                    for layout_action in layout['layout']:
                        assert layout_action['type'] != 'repeat_order'


@configs.layout_experiment_name()
@experiments.layout('test_place_layout')
async def test_empty_repeat_orders_response(
        taxi_eats_layout_constructor, mockserver, load_json,
):
    # тест проверяет, что в ответе отсутсвуют акции `repeat_order`
    # если сервис `eats-repeat-order` не нашёл запрашиваемых
    # ресторанов
    @mockserver.json_handler(CATALOG_HANDLER)
    def _catalog(request):
        return load_json('catalog-1.json')

    @mockserver.json_handler(REPEAT_ORDER_HANDLER)
    def _mock_eats_repeat_order(request):
        assert request.json['user_id'] == 12345
        return {'orders': []}

    response = await taxi_eats_layout_constructor.post(
        LAYOUT_CONSTRUCTOR_HANDLER['path'],
        headers=LAYOUT_CONSTRUCTOR_HANDLER['headers'],
        json=LAYOUT_CONSTRUCTOR_HANDLER['json'],
    )

    assert response.status_code == 200
    for place_list in response.json()['data']['places_lists']:
        for place in place_list['payload']['places']:
            if 'actions' in place['data']:
                for action in place['data']['actions']:
                    assert action['type'] != 'repeat_order'
            for layout in place['layout']:
                if layout['type'] == 'actions':
                    for layout_action in layout['layout']:
                        assert layout_action['type'] != 'repeat_order'


@configs.layout_experiment_name()
@experiments.layout('test_place_layout')
@pytest.mark.config(
    EATS_LAYOUT_CONSTRUCTOR_ACTION_REPEAT_ORDER_SETTINGS=ACTION_SETTINGS,
)
async def test_actions_content(
        taxi_eats_layout_constructor, mockserver, load_json,
):
    # тест проверяет содержимое (контент) добавляемых
    # объектов акций `repeat_order`
    @mockserver.json_handler(CATALOG_HANDLER)
    def _catalog(request):
        return load_json('catalog-1.json')

    @mockserver.json_handler(REPEAT_ORDER_HANDLER)
    def _mock_eats_repeat_order(request):
        assert request.json['user_id'] == 12345
        return load_json('repeat-order-1.json')

    response = await taxi_eats_layout_constructor.post(
        LAYOUT_CONSTRUCTOR_HANDLER['path'],
        headers=LAYOUT_CONSTRUCTOR_HANDLER['headers'],
        json=LAYOUT_CONSTRUCTOR_HANDLER['json'],
    )

    assert response.status_code == 200
    expected_actions = {
        'first': {
            'id': 'repeat_order_repeat-order-1',
            'type': 'repeat_order',
            'payload': {
                'icon_url': 'asset://repeat_order',
                'title': 'Повторим? description for order 1',
                'description': '',
                'order_id': 'repeat-order-1',
                'accent_color': [{'theme': 'light', 'value': '#169CDC'}],
            },
        },
        'second': {
            'id': 'repeat_order_repeat-order-2',
            'type': 'repeat_order',
            'payload': {
                'icon_url': 'asset://repeat_order',
                'title': 'Повторим? description for order 2',
                'description': '',
                'order_id': 'repeat-order-2',
                'accent_color': [{'theme': 'light', 'value': '#169CDC'}],
            },
        },
        'third': {
            'id': 'repeat_order_repeat-order-3',
            'type': 'repeat_order',
            'payload': {
                'icon_url': 'asset://repeat_order',
                'title': 'Повторим? description for order 3',
                'description': '',
                'order_id': 'repeat-order-3',
                'accent_color': [{'theme': 'light', 'value': '#169CDC'}],
            },
        },
    }

    expected_layouts_data = []
    has_actions = False
    has_layout = False
    for place_list in response.json()['data']['places_lists']:
        for place in place_list['payload']['places']:
            if 'actions' in place['data']:
                for action in place['data']['actions']:
                    has_actions = True
                    assert action == expected_actions[place['slug']]
                    expected_layouts_data.append(
                        {'id': action['id'], 'type': action['type']},
                    )
                has_layout = check_layouts(
                    place['layout'], expected_layouts_data,
                )
    assert has_actions
    assert has_layout


@pytest.mark.parametrize(
    'expected_icon_url', ['http://ololo', 'http://trololo'],
)
@configs.layout_experiment_name()
@experiments.layout('test_place_layout')
@pytest.mark.config(
    EATS_LAYOUT_CONSTRUCTOR_ACTION_REPEAT_ORDER_SETTINGS=ACTION_SETTINGS,
)
async def test_icon_url(
        taxi_eats_layout_constructor,
        mockserver,
        load_json,
        taxi_config,
        expected_icon_url,
):
    # тест проверяет, корректность работы параметра конфигурации `icon_url`
    @mockserver.json_handler(CATALOG_HANDLER)
    def _catalog(request):
        return load_json('catalog-1.json')

    @mockserver.json_handler(REPEAT_ORDER_HANDLER)
    def _mock_eats_repeat_order(request):
        assert request.json['user_id'] == 12345
        return load_json('repeat-order-1.json')

    settings = copy.deepcopy(ACTION_SETTINGS)
    settings['icon_url'] = expected_icon_url
    taxi_config.set(
        EATS_LAYOUT_CONSTRUCTOR_ACTION_REPEAT_ORDER_SETTINGS=settings,
    )

    response = await taxi_eats_layout_constructor.post(
        LAYOUT_CONSTRUCTOR_HANDLER['path'],
        headers=LAYOUT_CONSTRUCTOR_HANDLER['headers'],
        json=LAYOUT_CONSTRUCTOR_HANDLER['json'],
    )

    assert response.status_code == 200
    has_actions = False
    for place_list in response.json()['data']['places_lists']:
        for place in place_list['payload']['places']:
            if 'actions' in place['data']:
                for action in place['data']['actions']:
                    has_actions = True
                    if action['type'] == 'repeat_order':
                        assert (
                            action['payload']['icon_url'] == expected_icon_url
                        )
    assert has_actions


@pytest.mark.parametrize(
    'title_prefix,expected_titles',
    [
        (
            'Повторим?',
            {
                'first': 'Повторим? description for order 1',
                'second': 'Повторим? description for order 2',
                'third': 'Повторим? description for order 3',
            },
        ),
        (
            'Ещё раз?',
            {
                'first': 'Ещё раз? description for order 1',
                'second': 'Ещё раз? description for order 2',
                'third': 'Ещё раз? description for order 3',
            },
        ),
    ],
)
@configs.layout_experiment_name()
@experiments.layout('test_place_layout')
@pytest.mark.config(
    EATS_LAYOUT_CONSTRUCTOR_ACTION_REPEAT_ORDER_SETTINGS=ACTION_SETTINGS,
)
async def test_title(
        taxi_eats_layout_constructor,
        mockserver,
        load_json,
        taxi_config,
        title_prefix,
        expected_titles,
):
    # тест проверяет, корректность работы параметра конфигурации `title_prefix`
    @mockserver.json_handler(CATALOG_HANDLER)
    def _catalog(request):
        return load_json('catalog-1.json')

    @mockserver.json_handler(REPEAT_ORDER_HANDLER)
    def _mock_eats_repeat_order(request):
        assert request.json['user_id'] == 12345
        return load_json('repeat-order-1.json')

    settings = copy.deepcopy(ACTION_SETTINGS)
    settings['title_prefix'] = title_prefix
    taxi_config.set(
        EATS_LAYOUT_CONSTRUCTOR_ACTION_REPEAT_ORDER_SETTINGS=settings,
    )

    response = await taxi_eats_layout_constructor.post(
        LAYOUT_CONSTRUCTOR_HANDLER['path'],
        headers=LAYOUT_CONSTRUCTOR_HANDLER['headers'],
        json=LAYOUT_CONSTRUCTOR_HANDLER['json'],
    )

    assert response.status_code == 200
    has_actions = False
    for place_list in response.json()['data']['places_lists']:
        for place in place_list['payload']['places']:
            if 'actions' in place['data']:
                for action in place['data']['actions']:
                    has_actions = True
                    if action['type'] == 'repeat_order':
                        assert (
                            action['payload']['title']
                            == expected_titles[place['slug']]
                        )
    assert has_actions


@pytest.mark.parametrize(
    'accent_color',
    [
        [{'theme': 'light', 'value': '#169CDC'}],
        [
            {'theme': 'light', 'value': '#fffff'},
            {'theme': 'dark', 'value': '#eeeee'},
        ],
        [
            {'theme': 'dark', 'value': '#18282'},
            {'theme': 'light', 'value': '#fcdc2'},
        ],
    ],
)
@configs.layout_experiment_name()
@experiments.layout('test_place_layout')
@pytest.mark.config(
    EATS_LAYOUT_CONSTRUCTOR_ACTION_REPEAT_ORDER_SETTINGS=ACTION_SETTINGS,
)
async def test_accent_color(
        taxi_eats_layout_constructor,
        mockserver,
        load_json,
        taxi_config,
        accent_color,
):
    # тест проверяет, корректность работы параметра конфигурации `accent_color`
    @mockserver.json_handler(CATALOG_HANDLER)
    def _catalog(request):
        return load_json('catalog-1.json')

    @mockserver.json_handler(REPEAT_ORDER_HANDLER)
    def _mock_eats_repeat_order(request):
        assert request.json['user_id'] == 12345
        return load_json('repeat-order-1.json')

    settings = copy.deepcopy(ACTION_SETTINGS)
    settings['accent_color'] = accent_color
    taxi_config.set(
        EATS_LAYOUT_CONSTRUCTOR_ACTION_REPEAT_ORDER_SETTINGS=settings,
    )

    response = await taxi_eats_layout_constructor.post(
        LAYOUT_CONSTRUCTOR_HANDLER['path'],
        headers=LAYOUT_CONSTRUCTOR_HANDLER['headers'],
        json=LAYOUT_CONSTRUCTOR_HANDLER['json'],
    )

    assert response.status_code == 200
    has_actions = False
    for place_list in response.json()['data']['places_lists']:
        for place in place_list['payload']['places']:
            if 'actions' in place['data']:
                for action in place['data']['actions']:
                    has_actions = True
                    if action['type'] == 'repeat_order':
                        assert (
                            action['payload']['accent_color'] == accent_color
                        )
    assert has_actions
