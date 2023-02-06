import pytest

from . import configs
from . import experiments
from . import translations
from . import utils


LAYOUT = pytest.mark.layout(
    slug='layout_1',
    widgets=[
        utils.Widget(
            name='open',
            type='places_collection',
            meta={'place_filter_type': 'open', 'output_type': 'list'},
            payload={},
            payload_schema={},
        ),
    ],
)

TRANSLATIONS = {
    'main': 'Главная',
    'rest': 'Рестораны',
    'shops': 'Магазины',
    'lavka': 'Лавка',
    'cart': 'Корзина',
}


@LAYOUT
@configs.keep_empty_layout()
@experiments.layout('layout_1')
@configs.layout_experiment_name()
@translations.eats_layout_constructor_ru(TRANSLATIONS)
@pytest.mark.parametrize(
    'selected_tab',
    [
        pytest.param('main', marks=experiments.TAB_BAR, id='default tab'),
        pytest.param(
            'rest',
            marks=experiments.tab_bar(default_tab='main', forced_tab='rest'),
            id='forced tab',
        ),
    ],
)
async def test_tab_bar(taxi_eats_layout_constructor, mockserver, selected_tab):
    """
    Проверяем отображение таббара
    """

    @mockserver.json_handler('/eats-catalog/internal/v1/catalog-for-layout')
    def _catalog(_):
        return {'blocks': [], 'filters': {}, 'sort': {}, 'timepicker': []}

    response = await taxi_eats_layout_constructor.post(
        'eats/v1/layout-constructor/v1/layout',
        headers={
            'x-device-id': 'id',
            'x-platform': 'android_app',
            'x-app-version': '12.11.12',
            'cookie': '{}',
            'X-Eats-User': 'user_id=12345',
            'x-request-application': 'application=1.1.0',
            'x-request-language': 'enUS',
            'Content-Type': 'application/json',
        },
        json={'location': {'latitude': 0.0, 'longitude': 0.0}},
    )

    data = response.json()
    widget = data['data']['tab_bar']['payload']

    assert widget == {
        'current_id': selected_tab,
        'list': [
            {
                'id': 'main',
                'name': 'Главная',
                'action_type': 'view',
                'action_payload': {},
            },
            {
                'id': 'rest',
                'name': 'Рестораны',
                'action_type': 'view',
                'action_payload': {'view': {'type': 'tab', 'slug': 'rests'}},
            },
            {
                'id': 'shops',
                'name': 'Магазины',
                'action_type': 'view',
                'action_payload': {'view': {'type': 'tab', 'slug': 'shops'}},
            },
            {
                'id': 'lavka',
                'name': 'Лавка',
                'action_type': 'deeplink',
                'action_payload': {'deeplink': 'lavka://catalog'},
            },
            {
                'id': 'cart',
                'name': 'Корзина',
                'action_type': 'screen',
                'action_payload': {'screen': 'cart'},
            },
        ],
    }


@LAYOUT
@configs.keep_empty_layout()
@experiments.layout('layout_1')
@configs.layout_experiment_name()
@experiments.tab_bar(default_tab='main', with_shop_notification=True)
@pytest.mark.parametrize(
    'orders_count',
    [
        pytest.param(0, id='user without orders'),
        pytest.param(1, id='new user'),
        pytest.param(3, id='old user'),
    ],
)
@experiments.tab_bar_notification_experiment()
async def test_tab_notification(layout_constructor, mockserver, orders_count):
    """
        Для новых пользователей должна возвращаться нотификация
    """

    @mockserver.json_handler('/eats-catalog/internal/v1/catalog-for-layout')
    def _catalog(_):
        return {'blocks': [], 'filters': {}, 'sort': {}, 'timepicker': []}

    @mockserver.json_handler(
        '/eats-order-stats/internal/eats-order-stats/v1/orders',
    )
    def _mock_order_stats(request):
        return utils.order_stats_response(orders_count)

    response = await layout_constructor.post()

    data = response.json()
    widget = data['data']['tab_bar']['payload']
    expected_data = {
        'current_id': 'main',
        'list': [
            {
                'id': 'main',
                'name': 'main',
                'action_type': 'view',
                'action_payload': {},
            },
            {
                'id': 'rest',
                'name': 'rest',
                'action_type': 'view',
                'action_payload': {'view': {'type': 'tab', 'slug': 'rests'}},
            },
            {
                'id': 'shops',
                'name': 'shops',
                'action_type': 'view',
                'action_payload': {'view': {'type': 'tab', 'slug': 'shops'}},
            },
            {
                'id': 'lavka',
                'name': 'lavka',
                'action_type': 'deeplink',
                'action_payload': {'deeplink': 'lavka://catalog'},
            },
            {
                'id': 'cart',
                'name': 'cart',
                'action_type': 'screen',
                'action_payload': {'screen': 'cart'},
            },
        ],
    }
    if orders_count < experiments.ORDERS_COUNT_THRESHOLD:
        shop_data = next(
            filter(lambda tab: tab['id'] == 'shops', expected_data['list']),
        )
        shop_data['notifications'] = {
            'red_notification_dot': {'id': 'red_dot'},
        }
    assert widget == expected_data


@LAYOUT
@configs.keep_empty_layout()
@experiments.layout('layout_1')
@configs.layout_experiment_name()
@experiments.tab_bar(default_tab='main', with_shop_notification=True)
@experiments.tab_bar_notification_experiment()
async def test_tab_notification_empty_user_id(layout_constructor, mockserver):
    """
        Для незалогиненных пользователей должна возвращаться нотификация
    """

    @mockserver.json_handler('/eats-catalog/internal/v1/catalog-for-layout')
    def _catalog(_):
        return {'blocks': [], 'filters': {}, 'sort': {}, 'timepicker': []}

    request_headers = {'X-Eats-User': ''}
    response = await layout_constructor.post(headers=request_headers)

    data = response.json()
    widget = data['data']['tab_bar']['payload']
    shop_data = next(filter(lambda tab: tab['id'] == 'shops', widget['list']))
    assert shop_data['notifications'] == {
        'red_notification_dot': {'id': 'red_dot'},
    }


@LAYOUT
@configs.keep_empty_layout()
@experiments.layout('layout_1')
@configs.layout_experiment_name()
@experiments.tab_bar(default_tab='main', with_shop_notification=True)
@experiments.tab_bar_notification_experiment()
@pytest.mark.parametrize(
    'response_code', [400, 404, 429, 500, 'timeout_error', 'network_error'],
)
async def test_tab_notification_orders_stats_bad_respose(
        layout_constructor, mockserver, response_code,
):
    """
        При плохих ответах от eats-order-stats нотификация не возвращается
    """

    @mockserver.json_handler('/eats-catalog/internal/v1/catalog-for-layout')
    def _catalog(_):
        return {'blocks': [], 'filters': {}, 'sort': {}, 'timepicker': []}

    @mockserver.json_handler(
        '/eats-order-stats/internal/eats-order-stats/v1/orders',
    )
    def _mock_order_stats(request):
        if response_code == 'timeout_error':
            raise mockserver.TimeoutError()
        if response_code == 'network_error':
            raise mockserver.NetworkError()
        return mockserver.make_response(status=response_code)

    response = await layout_constructor.post()
    widget = response.json()['data']['tab_bar']['payload']
    shop_data = next(filter(lambda tab: tab['id'] == 'shops', widget['list']))
    assert 'notifications' not in shop_data
    assert response.status_code == 200
