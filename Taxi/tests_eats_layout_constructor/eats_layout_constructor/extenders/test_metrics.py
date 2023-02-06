import pytest

from eats_layout_constructor import configs
from eats_layout_constructor import experiments
from eats_layout_constructor import utils

CATALOG_RESPONSE = {
    'blocks': [
        {
            'id': 'open',
            'list': [
                {
                    'meta': {'place_id': 1, 'brand_id': 1},
                    'payload': {
                        'data': {
                            'actions': [
                                {
                                    'id': '1',
                                    'type': 'info',
                                    'payload': {'some': 'data'},
                                },
                            ],
                            'meta': [
                                {
                                    'id': '3',
                                    'type': 'info',
                                    'payload': {'some': 'data'},
                                },
                                {
                                    'id': '4',
                                    'type': 'rating',
                                    'payload': {'some': 'data'},
                                },
                            ],
                        },
                        'layout': [],
                    },
                },
            ],
        },
        {
            'id': 'promo',
            'list': [
                {
                    'meta': {'place_id': 2, 'brand_id': 2},
                    'payload': {
                        'data': {
                            'actions': [
                                {
                                    'id': '1',
                                    'type': 'info',
                                    'payload': {'some': 'data'},
                                },
                            ],
                            'meta': [
                                {
                                    'id': '3',
                                    'type': 'info',
                                    'payload': {'some': 'data'},
                                },
                                {
                                    'id': '4',
                                    'type': 'rating',
                                    'payload': {'some': 'data'},
                                },
                            ],
                        },
                        'layout': [],
                    },
                },
            ],
        },
    ],
    'filters': {},
    'sort': {},
    'timepicker': [],
}
METRICS_NAME = 'place_extenders_statistics'

META_WIDGET = utils.MetaWidget(
    type='place_layout',
    name='meta_widget',
    slug='meta_widget',
    settings={
        'order': ['actions', 'meta'],
        'action_extenders': [
            'actions_repeat_order',
            'actions_zen',
            'actions_info',
        ],
        'meta_extenders': ['meta_info', 'meta_rating', 'meta_price_category'],
        'max_actions_count': 1,
        'max_meta_count': 1,
    },
)


@experiments.layout('test_place_layout')
@configs.layout_experiment_name()
@pytest.mark.layout(
    slug='test_place_layout',
    widgets=[
        utils.Widget(
            name='list_1',
            type='places_collection',
            meta={'place_filter_type': 'open', 'output_type': 'list'},
            payload={},
            payload_schema={},
            meta_widget=META_WIDGET,
        ),
        utils.Widget(
            name='carousel',
            type='places_collection',
            meta={'place_filter_type': 'promo', 'output_type': 'carousel'},
            payload={},
            payload_schema={},
            meta_widget=META_WIDGET,
        ),
        utils.Widget(
            name='list_2',
            type='places_collection',
            meta={'place_filter_type': 'open', 'output_type': 'list'},
            payload={},
            payload_schema={},
            meta_widget=META_WIDGET,
        ),
    ],
)
async def test_metrics(
        taxi_eats_layout_constructor,
        mockserver,
        taxi_eats_layout_constructor_monitor,
):
    @mockserver.json_handler('/eats-catalog/internal/v1/catalog-for-layout')
    def _catalog(request):
        return CATALOG_RESPONSE

    @mockserver.handler('/eats-repeat-order/v1/get-orders')
    def _mock_eats_repeat_order(request):
        return mockserver.make_response(status=500)

    metrics_before = await taxi_eats_layout_constructor_monitor.get_metric(
        METRICS_NAME,
    )

    response = await taxi_eats_layout_constructor.post(
        'eats/v1/layout-constructor/v1/layout',
        headers={
            'x-device-id': 'dev_id',
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
    assert response.status_code == 200

    metrics_after = await taxi_eats_layout_constructor_monitor.get_metric(
        METRICS_NAME,
    )
    assert metrics_after is not None

    def check_metrics_diff(extender_name, key, diff):
        def _get_metric_value(metrics, default=0):
            if metrics is None:
                return default
            return metrics.get(extender_name, dict()).get(key, default)

        assert (
            _get_metric_value(metrics_after)
            == _get_metric_value(metrics_before) + diff
        )

    # Это первый экстендер в очереди.
    # Лимит еще не превышен, но экстендер не найден,
    # т.к. из каталога не приехало.
    check_metrics_diff('actions_repeat_order', 'shown', 0)
    check_metrics_diff('actions_repeat_order', 'limit_exceeded', 0)
    check_metrics_diff('actions_repeat_order', 'not_found', 3)

    # Второй экстендер в очереди.
    # Лимит еще не превышен.
    # 2 раза показан для place_id=1
    # 1 раз не найден для place_id=2, т.к. zen не знает про place_id=2.
    check_metrics_diff('actions_zen', 'shown', 2)
    check_metrics_diff('actions_zen', 'limit_exceeded', 0)
    check_metrics_diff('actions_zen', 'not_found', 1)

    # Третий экстендер в очереди.
    # 1 раз показан для place_id=2
    # 2 раза лимит превышен для place_id=1,
    # т.к. предыдущий 'actions_zen' уже занял место.
    check_metrics_diff('actions_info', 'shown', 1)
    check_metrics_diff('actions_info', 'limit_exceeded', 2)
    check_metrics_diff('actions_info', 'not_found', 0)

    # Это первый экстендер в очереди.
    # Лимит еще не превышен.
    # 3 раза показан для всех.
    check_metrics_diff('meta_info', 'shown', 3)
    check_metrics_diff('meta_info', 'limit_exceeded', 0)
    check_metrics_diff('meta_info', 'not_found', 0)

    # Второй экстендер в очереди.
    # 3 раза лимит превышен, т.к. 'meta_info' уже везде занял место.
    check_metrics_diff('meta_rating', 'shown', 0)
    check_metrics_diff('meta_rating', 'limit_exceeded', 3)
    check_metrics_diff('meta_rating', 'not_found', 0)

    # Третий экстендер в очереди.
    # 3 раза лимит превышен, т.к. 'meta_info' уже везде занял место.
    # (Несмотря на то, что экстеншн не был бы найден.)
    check_metrics_diff('meta_price_category', 'shown', 0)
    check_metrics_diff('meta_price_category', 'limit_exceeded', 3)
    check_metrics_diff('meta_price_category', 'not_found', 0)
