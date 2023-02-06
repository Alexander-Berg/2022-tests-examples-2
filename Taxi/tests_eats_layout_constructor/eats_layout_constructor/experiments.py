import typing

import pytest

ALWAYS = {'predicate': {'type': 'true'}, 'enabled': True}


def always_match(
        name: str, consumer: str, value: dict, is_config: bool = False,
):
    return pytest.mark.experiments3(
        is_config=is_config,
        match=ALWAYS,
        name=name,
        consumers=[consumer],
        clauses=[
            {
                'title': 'Always match',
                'value': value,
                'predicate': {'type': 'true'},
            },
        ],
    )


def layout(layout_slug: str, experiment_name: str = 'eats_layout_template'):
    return always_match(
        name=experiment_name,
        consumer='layout-constructor/layout',
        value={'layout_slug': layout_slug},
    )


RESIZE_IN_CATALOG = always_match(
    name='eats_layout_constructor_resize_in_catalog',
    consumer='layout-constructor/widget',
    value={'enabled': True},
)

NATIVE_ORDER_HISTORY = always_match(
    name='eats_layout_constructor_native_order_history',
    consumer='layout-constructor/widget',
    value={'enabled': True},
)


DISABLE_OFFERS = always_match(
    name='eats_layout_constructor_disable_offers',
    consumer='layout-constructor/v1/layout',
    value={'enabled': True},
)

DISABLE_ZEN = always_match(
    name='eats_layout_constructor_disable_zen',
    consumer='layout-constructor/extenders/zen',
    value={'enabled': True},
)

ENABLE_BRANDS_COUNT = always_match(
    name='eats_layout_constructor_brands_precount',
    consumer='layout-constructor/v1/layout',
    value={'enabled': True},
)


def tab_bar(
        default_tab: typing.Optional[str] = None,
        forced_tab: typing.Optional[str] = None,
        with_shop_notification: bool = False,
):

    return always_match(
        name='eats_layout_constructor_tab_bar',
        consumer='layout-constructor/tab-bar',
        is_config=True,
        value={
            'enabled': True,
            'red_notification_dot_enabled': with_shop_notification,
            'default_tab': default_tab,
            'force_tab': forced_tab,
            'tabs': [
                {
                    'id': 'main',
                    'name': 'main',
                    'action': {'type': 'view'},
                    'business': [],
                },
                {
                    'id': 'rest',
                    'name': 'rest',
                    'action': {
                        'type': 'view',
                        'view': {'type': 'tab', 'slug': 'rests'},
                    },
                    'business': [],
                },
                {
                    'id': 'shops',
                    'name': 'shops',
                    'action': {
                        'type': 'view',
                        'view': {'type': 'tab', 'slug': 'shops'},
                    },
                    'business': [],
                },
                {
                    'id': 'lavka',
                    'name': 'lavka',
                    'action': {
                        'type': 'deeplink',
                        'deeplink': 'lavka://catalog',
                    },
                    'business': [],
                },
                {
                    'id': 'cart',
                    'name': 'cart',
                    'action': {'type': 'screen', 'screen': 'cart'},
                    'business': [],
                },
            ],
        },
    )


TAB_BAR = tab_bar(default_tab='main')

RECOMMENDATIONS_CONFIG_NAME: str = (
    'eats_layout_constructor_recommendations_settings'
)


def recommendation_settings(
        enabled: bool = True,
        divisor: int = 1,
        remainder: int = 0,
        recommendations_limit: typing.Optional[int] = None,
        ignore_recommended_places: typing.Optional[int] = None,
):
    """
    Устанавливает эксперимент eats_layout_constructor_recommendations_settings.
    """
    assert divisor > 0, 'divisor must be greate than 0'

    value: dict = {
        'enabled': enabled,
        'divisor': divisor,
        'remainder': remainder,
    }

    if recommendations_limit:
        value['recommendations_limit'] = recommendations_limit

    if ignore_recommended_places:
        value['ignore_recommended_places'] = ignore_recommended_places

    return always_match(
        name=RECOMMENDATIONS_CONFIG_NAME,
        consumer='layout-constructor/v1/recommendations',
        value=value,
        is_config=True,
    )


def filter_source_response(
        place_ids: typing.Optional[typing.List[int]] = None,
        brand_ids: typing.Optional[typing.List[int]] = None,
        banner_ids: typing.Optional[typing.List[int]] = None,
):

    if place_ids is None:
        place_ids = []

    if brand_ids is None:
        brand_ids = []

    if banner_ids is None:
        banner_ids = []

    return always_match(
        name='filter_source_response',
        consumer='layout-constructor/filter-source-response',
        value={
            'brand_ids': brand_ids,
            'place_ids': place_ids,
            'banner_ids': banner_ids,
        },
    )


def brand_photo_tag(tag: str):
    return always_match(
        name='eats_layout_constructor_photo_tag',
        consumer='layout-constructor/extenders/hero_photo',
        value={'tag': tag},
    )


def meta_widget(meta_widget_slug: str):
    return always_match(
        name='meta_widget_experiment',
        consumer='layout-constructor/meta-widget',
        value={'meta_widget_slug': meta_widget_slug},
    )


ORDERS_COUNT_THRESHOLD = 2


def tab_bar_notification_experiment():
    experiment_value = {
        'tab_notifications': {
            'tab_id': 'shops',
            'notifications': {'red_notification_dot': {'id': 'red_dot'}},
        },
    }
    return pytest.mark.experiments3(
        name='eats_layout_constructor_tab_bar_notifications',
        consumers=['layout-constructor/tab-bar-notification'],
        clauses=[
            {
                'title': 'Retail order stats checking',
                'value': experiment_value,
                'predicate': {
                    'type': 'lte',
                    'init': {
                        'arg_name': 'retail_orders_count',
                        'arg_type': 'int',
                        'value': ORDERS_COUNT_THRESHOLD,
                    },
                },
            },
        ],
    )
