# pylint: disable=import-error
import copy

import pytest

from eats_analytics import eats_analytics

from . import configs
from . import experiments
from . import utils


CATALOG_RESPONSE = {
    'blocks': [
        {
            'id': 'open_no_filters_shop_sort_default',
            'list': [
                {
                    'meta': {'place_id': 42, 'brand_id': 1},
                    'payload': {
                        'context': {},
                        'analytics': eats_analytics.encode(
                            eats_analytics.AnalyticsContext(item_id='42'),
                        ),
                        'name': 'Out of order',
                        'slug': 'out_of_order',
                        'brand': {
                            'name': 'Out of order',
                            'slug': 'out_of_order',
                            'business': 'restaurant',
                        },
                        'availability': {'is_available': True},
                        'media': {
                            'photos': [
                                {
                                    'uri': (
                                        '/images/1370147/'
                                        '7691446c316478b7'
                                        '13d54ca6e40a330b-{w}x{h}.jpg'
                                    ),
                                },
                            ],
                        },
                        'layout': [
                            {
                                'type': 'meta',
                                'layout': [
                                    {'id': 'fake_c48a1c13', 'type': 'rating'},
                                    {
                                        'id': 'fake_333ec296',
                                        'type': 'price_category',
                                    },
                                ],
                            },
                            {'type': 'actions', 'layout': []},
                        ],
                        'data': {
                            'features': {'delivery': {'text': '~45 мин'}},
                            'meta': [
                                {
                                    'id': 'fake_c48a1c13',
                                    'type': 'rating',
                                    'payload': {
                                        'icon_url': 'asset://flame',
                                        'color': [
                                            {
                                                'theme': 'dark',
                                                'value': '#C4C2BE',
                                            },
                                            {
                                                'theme': 'light',
                                                'value': '#C4C2BE',
                                            },
                                        ],
                                        'title': '4.7 Входит в Топ',
                                    },
                                },
                                {
                                    'id': 'fake_333ec296',
                                    'type': 'price_category',
                                    'payload': {
                                        'icon_url': 'asset://price_category',
                                        'currency_sign': '₽',
                                        'total_symbols': 3,
                                        'highlighted_symbols': 3,
                                    },
                                },
                            ],
                            'actions': [],
                        },
                    },
                },
                {
                    'meta': {'place_id': 1, 'brand_id': 10},
                    'payload': {
                        'context': {},
                        'name': 'Осетинские пироги от Миры',
                        'slug': 'osetinskie_pirogi_ot_miry_holodilnyj',
                        'brand': {
                            'name': 'Осетинские пироги от Миры',
                            'slug': 'osetinskie_pirogi_ot_miry',
                            'business': 'shop',
                        },
                        'availability': {'is_available': True},
                        'media': {
                            'photos': [
                                {
                                    'uri': (
                                        '/images/1370147/'
                                        '7691446c316478b7'
                                        '13d54ca6e40a330b-{w}x{h}.jpg'
                                    ),
                                },
                            ],
                        },
                        'layout': [
                            {
                                'type': 'meta',
                                'layout': [
                                    {'id': 'fake_c48a1c13', 'type': 'rating'},
                                    {
                                        'id': 'fake_333ec296',
                                        'type': 'price_category',
                                    },
                                ],
                            },
                            {'type': 'actions', 'layout': []},
                        ],
                        'data': {
                            'features': {'delivery': {'text': '~45 мин'}},
                            'meta': [
                                {
                                    'id': 'fake_c48a1c13',
                                    'type': 'rating',
                                    'payload': {
                                        'icon_url': 'asset://flame',
                                        'color': [
                                            {
                                                'theme': 'dark',
                                                'value': '#C4C2BE',
                                            },
                                            {
                                                'theme': 'light',
                                                'value': '#C4C2BE',
                                            },
                                        ],
                                        'title': '4.7 Входит в Топ',
                                    },
                                },
                                {
                                    'id': 'fake_333ec296',
                                    'type': 'price_category',
                                    'payload': {
                                        'icon_url': 'asset://price_category',
                                        'currency_sign': '₽',
                                        'total_symbols': 3,
                                        'highlighted_symbols': 3,
                                    },
                                },
                            ],
                            'actions': [],
                        },
                    },
                },
                {
                    'meta': {'place_id': 2, 'brand_id': 20},
                    'payload': {
                        'context': {},
                        'name': 'Kombinat Deli',
                        'slug': 'KombinatDeli',
                        'brand': {
                            'name': 'Kombinat Deli',
                            'slug': 'kombinat_deli',
                            'business': 'shop',
                        },
                        'availability': {'is_available': True},
                        'media': {
                            'photos': [
                                {
                                    'uri': (
                                        '/images/1380157/'
                                        '629efca1465723f4'
                                        '7ae6a5b419577b46-{w}x{h}.jpeg'
                                    ),
                                },
                            ],
                        },
                        'layout': [
                            {
                                'type': 'meta',
                                'layout': [
                                    {'id': 'fake_c3f98c33', 'type': 'rating'},
                                    {
                                        'id': 'fake_b6f5a73a',
                                        'type': 'price_category',
                                    },
                                ],
                            },
                            {'type': 'actions', 'layout': []},
                        ],
                        'data': {
                            'features': {
                                'delivery': {
                                    'icons': ['asset://native_delivery'],
                                    'text': '30 – 40 мин',
                                },
                                'favorite': {'active': True},
                            },
                            'meta': [
                                {
                                    'id': 'fake_c3f98c33',
                                    'type': 'rating',
                                    'payload': {
                                        'icon_url': 'asset://flame',
                                        'color': [
                                            {
                                                'theme': 'dark',
                                                'value': '#C4C2BE',
                                            },
                                            {
                                                'theme': 'light',
                                                'value': '#C4C2BE',
                                            },
                                        ],
                                        'title': '4.9 Входит в Топ',
                                    },
                                },
                                {
                                    'id': 'fake_b6f5a73a',
                                    'type': 'price_category',
                                    'payload': {
                                        'icon_url': 'asset://price_category',
                                        'currency_sign': '₽',
                                        'total_symbols': 3,
                                        'highlighted_symbols': 1,
                                    },
                                },
                            ],
                            'actions': [],
                        },
                    },
                },
                {
                    'meta': {'place_id': 3, 'brand_id': 30},
                    'payload': {
                        'context': {},
                        'name': 'IL Патио',
                        'slug': 'il_patio_paveleskaya',
                        'brand': {
                            'name': 'IL Патио',
                            'slug': 'il_ukmbh',
                            'business': 'shop',
                        },
                        'availability': {'is_available': False},
                        'media': {
                            'photos': [
                                {
                                    'uri': (
                                        '/images/1368744/'
                                        '009132b0a17ea8f1'
                                        '1c37d54897d27e09-{w}x{h}.jpg'
                                    ),
                                },
                            ],
                        },
                        'layout': [
                            {
                                'type': 'meta',
                                'layout': [
                                    {'id': 'fake_14abeb96', 'type': 'rating'},
                                    {
                                        'id': 'fake_ebce35aa',
                                        'type': 'price_category',
                                    },
                                ],
                            },
                            {'type': 'actions', 'layout': []},
                        ],
                        'data': {
                            'features': {
                                'delivery': {'text': 'Завтра в 22:00'},
                            },
                            'meta': [
                                {
                                    'id': (
                                        '947deaab-f192-4298-ad5a-8fcc3baf94ca'
                                    ),
                                    'payload': {
                                        'icon_url': 'asset://yandex_plus',
                                        'styles': {
                                            'border': True,
                                            'rainbow': True,
                                        },
                                        'text': '10%',
                                    },
                                    'type': 'yandex_plus',
                                },
                                {
                                    'id': 'fake_14abeb96',
                                    'type': 'rating',
                                    'payload': {
                                        'icon_url': 'asset://rating_star',
                                        'color': [
                                            {
                                                'theme': 'dark',
                                                'value': '#C4C2BE',
                                            },
                                            {
                                                'theme': 'light',
                                                'value': '#C4C2BE',
                                            },
                                        ],
                                        'title': 'Мало оценок',
                                    },
                                },
                                {
                                    'id': 'fake_ebce35aa',
                                    'type': 'price_category',
                                    'payload': {
                                        'icon_url': 'asset://price_category',
                                        'currency_sign': '₽',
                                        'total_symbols': 3,
                                        'highlighted_symbols': 2,
                                    },
                                },
                            ],
                            'actions': [],
                        },
                    },
                },
            ],
        },
    ],
    'filters': {},
    'sort': {},
    'timepicker': [],
}


@configs.layout_experiment_name()
@experiments.layout('layout_1')
async def test_eats_layout_mini_places_carousel(
        taxi_eats_layout_constructor, mockserver,
):
    @mockserver.json_handler('/eats-catalog/internal/v1/catalog-for-layout')
    def _catalog(request):
        return CATALOG_RESPONSE

    response = await taxi_eats_layout_constructor.post(
        'eats/v1/layout-constructor/v1/layout',
        headers={
            'x-device-id': 'pumpkin',
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
    body = response.json()

    assert body['layout'] == [
        {
            'id': '1_mini_places_carousel',
            'payload': {},
            'type': 'mini_places_carousel',
        },
    ]

    mini_places_carousel = body['data']['mini_places_carousels'][0]

    assert mini_places_carousel['id'] == '1_mini_places_carousel'
    assert mini_places_carousel['template_name'] == 'Mini shops carouseel'

    payload = utils.decode_widget_payload(mini_places_carousel['payload'])
    assert payload == {
        'places': [
            {
                'name': 'IL Патио',
                'slug': 'il_patio_paveleskaya',
                'brand': {
                    'name': 'IL Патио',
                    'slug': 'il_ukmbh',
                    'business': 'shop',
                },
                'availability': {'is_available': False},
                'media': {
                    'photos': [
                        {
                            'uri': (
                                '/images/1368744/'
                                '009132b0a17ea8f1'
                                '1c37d54897d27e09-{w}x{h}.jpg'
                            ),
                        },
                    ],
                },
                'data': {
                    'features': {
                        'delivery': {'text': 'Завтра в 22:00'},
                        'yandex_plus': {
                            'icon_url': 'asset://yandex_plus',
                            'styles': {'border': True, 'rainbow': True},
                            'text': '10%',
                        },
                    },
                },
                'meta': {'image_source': 'logo'},
                'context': {
                    'place_id': 3,
                    'widget': {
                        'id': '1_mini_places_carousel',
                        'type': 'mini_places_carousel',
                    },
                },
                'analytics': eats_analytics.AnalyticsContext(
                    widget_id='1_mini_places_carousel',
                    widget_template_id='Mini shops carouseel',
                    item_position=eats_analytics.Position(column=0, row=0),
                ),
            },
            {
                'name': 'Kombinat Deli',
                'slug': 'KombinatDeli',
                'brand': {
                    'name': 'Kombinat Deli',
                    'slug': 'kombinat_deli',
                    'business': 'shop',
                },
                'availability': {'is_available': True},
                'media': {
                    'photos': [
                        {
                            'uri': (
                                '/images/1380157/'
                                '629efca1465723f4'
                                '7ae6a5b419577b46-{w}x{h}.jpeg'
                            ),
                        },
                    ],
                },
                'data': {
                    'features': {
                        'delivery': {
                            'icons': ['asset://native_delivery'],
                            'text': '30 – 40 мин',
                        },
                    },
                },
                'meta': {'image_source': 'logo'},
                'context': {
                    'place_id': 2,
                    'widget': {
                        'id': '1_mini_places_carousel',
                        'type': 'mini_places_carousel',
                    },
                },
                'analytics': eats_analytics.AnalyticsContext(
                    widget_id='1_mini_places_carousel',
                    widget_template_id='Mini shops carouseel',
                    item_position=eats_analytics.Position(column=1, row=0),
                ),
            },
            {
                'name': 'Осетинские пироги от Миры',
                'slug': 'osetinskie_pirogi_ot_miry_holodilnyj',
                'brand': {
                    'name': 'Осетинские пироги от Миры',
                    'slug': 'osetinskie_pirogi_ot_miry',
                    'business': 'shop',
                },
                'availability': {'is_available': True},
                'media': {
                    'photos': [
                        {
                            'uri': (
                                '/images/1370147/'
                                '7691446c316478b7'
                                '13d54ca6e40a330b-{w}x{h}.jpg'
                            ),
                        },
                    ],
                },
                'data': {'features': {'delivery': {'text': '~45 мин'}}},
                'meta': {'image_source': 'logo'},
                'context': {
                    'place_id': 1,
                    'widget': {
                        'id': '1_mini_places_carousel',
                        'type': 'mini_places_carousel',
                    },
                },
                'analytics': eats_analytics.AnalyticsContext(
                    widget_id='1_mini_places_carousel',
                    widget_template_id='Mini shops carouseel',
                    item_position=eats_analytics.Position(column=2, row=0),
                ),
            },
            {
                'name': 'Out of order',
                'slug': 'out_of_order',
                'brand': {
                    'name': 'Out of order',
                    'slug': 'out_of_order',
                    'business': 'restaurant',
                },
                'availability': {'is_available': True},
                'media': {
                    'photos': [
                        {
                            'uri': (
                                '/images/1370147/'
                                '7691446c316478b7'
                                '13d54ca6e40a330b-{w}x{h}.jpg'
                            ),
                        },
                    ],
                },
                'data': {'features': {'delivery': {'text': '~45 мин'}}},
                'meta': {'image_source': 'logo'},
                'context': {
                    'place_id': 42,
                    'widget': {
                        'id': '1_mini_places_carousel',
                        'type': 'mini_places_carousel',
                    },
                },
                'analytics': eats_analytics.AnalyticsContext(
                    item_id='42',
                    widget_id='1_mini_places_carousel',
                    widget_template_id='Mini shops carouseel',
                    item_position=eats_analytics.Position(column=3, row=0),
                ),
            },
        ],
    }


@configs.layout_experiment_name()
@experiments.layout('place_filter_type_layout')
@pytest.mark.layout(
    slug='place_filter_type_layout',
    widgets=[
        utils.Widget(
            name='Mini shops carouseel with default place_filter_type',
            type='mini_places_carousel',
            meta={},
            payload={},
        ),
        utils.Widget(
            name='Mini shops carouseel with open place_filter_type',
            type='mini_places_carousel',
            meta={'place_filter_type': 'open'},
            payload={},
        ),
        utils.Widget(
            name='Mini shops carouseel with any place_filter_type',
            type='mini_places_carousel',
            meta={'place_filter_type': 'any'},
            payload={},
        ),
        utils.Widget(
            name='Mini shops carouseel with shop or store',
            type='mini_places_carousel',
            meta={
                'place_filter_type': 'any',
                'include_businesses': ['shop', 'store'],
            },
            payload={},
        ),
        utils.Widget(
            name='Mini shops carouseel with open shop delivery or pickup',
            type='mini_places_carousel',
            meta={'place_filter_type': 'open-delivery-or-pickup'},
            payload={},
        ),
    ],
)
async def test_eats_layout_mini_places_carousel_request(
        taxi_eats_layout_constructor, mockserver,
):
    @mockserver.json_handler('/eats-catalog/internal/v1/catalog-for-layout')
    def catalog(request):
        blocks = copy.deepcopy(request.json['blocks'])
        # Данные в запросе имеют произвольный порядок.
        # сортируем по id блока для удобства валидации
        blocks.sort(key=lambda val: val['id'])
        assert blocks == [
            {
                'id': 'any_no_filters_shop_sort_default',
                'type': 'any',
                'disable_filters': True,
                'round_eta_to_hours': False,
                'sort_type': 'default',
                'compilation_type': 'retail',
                'condition': {
                    'type': 'eq',
                    'init': {
                        'arg_name': 'business',
                        'arg_type': 'string',
                        'value': 'shop',
                    },
                },
            },
            {
                'id': 'any_no_filters_shop_store_sort_default',
                'type': 'any',
                'disable_filters': True,
                'round_eta_to_hours': False,
                'sort_type': 'default',
                'compilation_type': 'retail',
                'condition': {
                    'type': 'any_of',
                    'predicates': [
                        {
                            'type': 'eq',
                            'init': {
                                'arg_name': 'business',
                                'arg_type': 'string',
                                'value': 'shop',
                            },
                        },
                        {
                            'type': 'eq',
                            'init': {
                                'arg_name': 'business',
                                'arg_type': 'string',
                                'value': 'store',
                            },
                        },
                    ],
                },
            },
            {
                'id': 'open-delivery-or-pickup_no_filters_shop_sort_default',
                'type': 'open-delivery-or-pickup',
                'disable_filters': True,
                'round_eta_to_hours': False,
                'sort_type': 'default',
                'compilation_type': 'retail',
                'condition': {
                    'type': 'eq',
                    'init': {
                        'arg_name': 'business',
                        'arg_type': 'string',
                        'value': 'shop',
                    },
                },
            },
            {
                'id': 'open_no_filters_shop_sort_default',
                'type': 'open',
                'disable_filters': True,
                'round_eta_to_hours': False,
                'sort_type': 'default',
                'compilation_type': 'retail',
                'condition': {
                    'type': 'eq',
                    'init': {
                        'arg_name': 'business',
                        'arg_type': 'string',
                        'value': 'shop',
                    },
                },
            },
        ]

    response = await taxi_eats_layout_constructor.post(
        'eats/v1/layout-constructor/v1/layout',
        headers={
            'x-device-id': 'test_request',
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

    assert response.status == 200
    assert catalog.times_called == 1
