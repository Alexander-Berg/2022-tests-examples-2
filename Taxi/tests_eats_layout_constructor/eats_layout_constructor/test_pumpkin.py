from testsuite.utils import matching

from . import configs
from . import experiments

BANNERS_PUMPKIN_RESPONSE = {
    'payload': {
        'blocks': [],
        'banners': [
            {
                'id': 1,
                'kind': 'info',
                'formats': ['classic', 'shortcut'],
                'payload': {
                    'id': 1,
                    'kind': 'info',
                    'url': 'https://eda.yandex/lavka',
                    'appLink': 'null',
                    'payload': {'badge': {'counter': 10}},
                    'images': [
                        {
                            'url': 'http://goolge.com',
                            'theme': 'light',
                            'platform': 'web',
                        },
                    ],
                    'shortcuts': [
                        {
                            'url': 'http://goolge.com',
                            'theme': 'light',
                            'platform': 'web',
                        },
                    ],
                },
            },
        ],
        'header_notes': [],
    },
}

CATALOG_PUMPKIN_RESPONSE = {
    'blocks': [
        {
            'id': 'open',
            'type': 'open',
            'list': [
                {
                    'meta': {'place_id': 1, 'brand_id': 1},
                    'payload': {'id': 'id1', 'name': 'name1'},
                },
                {
                    'meta': {'place_id': 2, 'brand_id': 2},
                    'payload': {'id': 'id2', 'name': 'name2'},
                },
                {
                    'meta': {'place_id': 3, 'brand_id': 3},
                    'payload': {'id': 'id3', 'name': 'name3'},
                },
                {
                    'meta': {'place_id': 4, 'brand_id': 4},
                    'payload': {'id': 'id4', 'name': 'name4'},
                },
                {
                    'meta': {'place_id': 5, 'brand_id': 5},
                    'payload': {'id': 'id5', 'name': 'name5'},
                },
                {
                    'meta': {'place_id': 6, 'brand_id': 6},
                    'payload': {'id': 'id6', 'name': 'name6'},
                },
                {
                    'meta': {'place_id': 7, 'brand_id': 7},
                    'payload': {'id': 'id7', 'name': 'name7'},
                },
                {
                    'meta': {'place_id': 8, 'brand_id': 8},
                    'payload': {'id': 'id8', 'name': 'name8'},
                },
                {
                    'meta': {'place_id': 9, 'brand_id': 9},
                    'payload': {'id': 'id9', 'name': 'name9'},
                },
                {
                    'meta': {'place_id': 10, 'brand_id': 10},
                    'payload': {'id': 'id10', 'name': 'name10'},
                },
                {
                    'meta': {'place_id': 11, 'brand_id': 11},
                    'payload': {'id': 'id11', 'name': 'name11'},
                },
                {
                    'meta': {'place_id': 12, 'brand_id': 12},
                    'payload': {'id': 'id12', 'name': 'name12'},
                },
            ],
        },
        {
            'id': 'closed',
            'type': 'closed',
            'list': [
                {
                    'meta': {'place_id': 13, 'brand_id': 13},
                    'payload': {'id': 'id13', 'name': 'name13'},
                },
                {
                    'meta': {'place_id': 14, 'brand_id': 14},
                    'payload': {'id': 'id14', 'name': 'name14'},
                },
            ],
        },
        {
            'id': 'new',
            'type': 'new',
            'list': [
                {
                    'meta': {'place_id': 1, 'brand_id': 1},
                    'payload': {'id': 'id1', 'name': 'name1'},
                },
                {
                    'meta': {'place_id': 2, 'brand_id': 2},
                    'payload': {'id': 'id2', 'name': 'name2'},
                },
                {
                    'meta': {'place_id': 3, 'brand_id': 3},
                    'payload': {'id': 'id3', 'name': 'name3'},
                },
                {
                    'meta': {'place_id': 4, 'brand_id': 4},
                    'payload': {'id': 'id4', 'name': 'name4'},
                },
            ],
        },
        {
            'id': 'promo',
            'type': 'promo',
            'list': [
                {
                    'meta': {'place_id': 1, 'brand_id': 1},
                    'payload': {'id': 'id1', 'name': 'name1'},
                },
                {
                    'meta': {'place_id': 2, 'brand_id': 2},
                    'payload': {'id': 'id2', 'name': 'name2'},
                },
                {
                    'meta': {'place_id': 3, 'brand_id': 3},
                    'payload': {'id': 'id3', 'name': 'name3'},
                },
                {
                    'meta': {'place_id': 4, 'brand_id': 4},
                    'payload': {'id': 'id4', 'name': 'name4'},
                },
            ],
        },
    ],
    'filters': {
        'current': 'genitive',
        'list': [
            {
                'genitive': 'шавермы',
                'name': 'Шаверма',
                'photo_uri': (
                    '/images/1368744/aafb68cebeb3e'
                    '0edf6eb5aa73d80faf6-{w}x{h}.jpg'
                ),
                'picture_uri': (
                    '/images/1368744/7eb79169054839e801225ebcdcc22c13.png'
                ),
                'promo_photo_uri': (
                    '/images/1387779/ebc4de93763e64d'
                    '978f2012706fd9b2f-{w}x{h}.png'
                ),
                'slug': 'shaverma',
            },
            {
                'genitive': 'шашлыка',
                'name': 'Шашлык',
                'photo_uri': (
                    '/images/1380157/f82530e5ed9ede'
                    '1aa310e830eca7cbc8-{w}x{h}.jpg'
                ),
                'picture_uri': (
                    '/images/1368744/318909aa345cabca778fded1d309c8de.png'
                ),
                'promo_photo_uri': (
                    '/images/1387779/3578a3519e07f6e'
                    '4f85a1b66d48cce71-{w}x{h}.png'
                ),
                'slug': 'shashlyk',
            },
            {
                'genitive': 'блюд грузинской кухни',
                'name': 'Грузинская',
                'photo_uri': (
                    '/images/1380157/7261a46c7ee50'
                    'edb6208bb58d07a47a9-{w}x{h}.jpg'
                ),
                'picture_uri': (
                    '/images/1387779/d592dc20250aa916ce89d1162941d2c3.png'
                ),
                'promo_photo_uri': (
                    '/images/1387779/9c1ca1a6878'
                    'c6aedf6a01bb5b7c90c5a-{w}x{h}.png'
                ),
                'slug': 'gruzinskaya',
            },
        ],
    },
    'sort': {
        'current': 'default',
        'default': 'default',
        'list': [
            {'description': 'Доверюсь вам', 'slug': 'default'},
            {'description': 'c', 'slug': 'high_rating'},
            {'description': 'Быстрые', 'slug': 'fast_delivery'},
            {'description': 'Недорогие', 'slug': 'cheap_first'},
            {'description': 'Дорогие', 'slug': 'expensive_first'},
        ],
    },
    'timepicker': [
        [
            '2020-05-15T18:30:00+05:00',
            '2020-05-15T19:00:00+05:00',
            '2020-05-15T19:30:00+05:00',
            '2020-05-15T20:00:00+05:00',
            '2020-05-15T20:30:00+05:00',
            '2020-05-15T21:00:00+05:00',
            '2020-05-15T21:30:00+05:00',
            '2020-05-15T22:00:00+05:00',
            '2020-05-15T22:30:00+05:00',
            '2020-05-15T23:00:00+05:00',
            '2020-05-15T23:30:00+05:00',
        ],
        [
            '2020-05-16T09:30:00+05:00',
            '2020-05-16T10:00:00+05:00',
            '2020-05-16T10:30:00+05:00',
            '2020-05-16T11:00:00+05:00',
            '2020-05-16T11:30:00+05:00',
            '2020-05-16T12:00:00+05:00',
            '2020-05-16T12:30:00+05:00',
            '2020-05-16T13:00:00+05:00',
        ],
    ],
}


@configs.layout_experiment_name()
@experiments.layout('layout_1')
async def test_layout_pumpkin_request(
        taxi_eats_layout_constructor, mockserver,
):
    @mockserver.json_handler('/eats-catalog/internal/v1/catalog-for-layout')
    def _catalog(request):
        return CATALOG_PUMPKIN_RESPONSE

    @mockserver.json_handler(
        '/eats-communications/eats-communications/v1/layout/banners',
    )
    def _banners(request):
        return BANNERS_PUMPKIN_RESPONSE

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
    assert response.json() == {
        'data': {
            'places_carousels': [
                {
                    'id': '1_places_carousel',
                    'template_name': 'Widget template 1',
                    'payload': {
                        'places': [
                            {
                                'id': 'id1',
                                'name': 'name1',
                                'context': matching.any_string,
                            },
                            {
                                'id': 'id2',
                                'name': 'name2',
                                'context': matching.any_string,
                            },
                            {
                                'id': 'id3',
                                'name': 'name3',
                                'context': matching.any_string,
                            },
                            {
                                'id': 'id4',
                                'name': 'name4',
                                'context': matching.any_string,
                            },
                        ],
                    },
                },
                {
                    'id': '4_places_carousel',
                    'template_name': 'Widget template 1',
                    'payload': {
                        'places': [
                            {
                                'id': 'id1',
                                'name': 'name1',
                                'context': matching.any_string,
                            },
                            {
                                'id': 'id2',
                                'name': 'name2',
                                'context': matching.any_string,
                            },
                            {
                                'id': 'id3',
                                'name': 'name3',
                                'context': matching.any_string,
                            },
                            {
                                'id': 'id4',
                                'name': 'name4',
                                'context': matching.any_string,
                            },
                        ],
                    },
                },
            ],
            'places_lists': [
                {
                    'id': '2_places_list',
                    'template_name': 'Widget template 2',
                    'payload': {
                        'places': [
                            {
                                'id': 'id1',
                                'name': 'name1',
                                'context': matching.any_string,
                            },
                            {
                                'id': 'id2',
                                'name': 'name2',
                                'context': matching.any_string,
                            },
                            {
                                'id': 'id3',
                                'name': 'name3',
                                'context': matching.any_string,
                            },
                        ],
                    },
                },
                {
                    'id': '5_places_list',
                    'template_name': 'Widget template 2',
                    'payload': {
                        'places': [
                            {
                                'id': 'id4',
                                'name': 'name4',
                                'context': matching.any_string,
                            },
                            {
                                'id': 'id5',
                                'name': 'name5',
                                'context': matching.any_string,
                            },
                            {
                                'id': 'id6',
                                'name': 'name6',
                                'context': matching.any_string,
                            },
                            {
                                'id': 'id7',
                                'name': 'name7',
                                'context': matching.any_string,
                            },
                            {
                                'id': 'id8',
                                'name': 'name8',
                                'context': matching.any_string,
                            },
                            {
                                'id': 'id9',
                                'name': 'name9',
                                'context': matching.any_string,
                            },
                            {
                                'id': 'id10',
                                'name': 'name10',
                                'context': matching.any_string,
                            },
                            {
                                'id': 'id11',
                                'name': 'name11',
                                'context': matching.any_string,
                            },
                            {
                                'id': 'id12',
                                'name': 'name12',
                                'context': matching.any_string,
                            },
                        ],
                    },
                },
                {
                    'id': '6_places_list',
                    'template_name': 'Widget template 2',
                    'payload': {
                        'places': [
                            {
                                'id': 'id13',
                                'name': 'name13',
                                'context': matching.any_string,
                            },
                            {
                                'id': 'id14',
                                'name': 'name14',
                                'context': matching.any_string,
                            },
                        ],
                    },
                },
            ],
            'sorts': [
                {
                    'id': '7_sorts',
                    'template_name': 'Widget template 4',
                    'payload': {
                        'sort': {
                            'current': 'default',
                            'default': 'default',
                            'list': [
                                {
                                    'description': 'Доверюсь вам',
                                    'slug': 'default',
                                },
                                {'description': 'c', 'slug': 'high_rating'},
                                {
                                    'description': 'Быстрые',
                                    'slug': 'fast_delivery',
                                },
                                {
                                    'description': 'Недорогие',
                                    'slug': 'cheap_first',
                                },
                                {
                                    'description': 'Дорогие',
                                    'slug': 'expensive_first',
                                },
                            ],
                        },
                    },
                },
            ],
            'filters': [
                {
                    'id': '8_filters',
                    'template_name': 'Widget template 5',
                    'payload': {
                        'current': 'genitive',
                        'list': [
                            {
                                'genitive': 'шавермы',
                                'name': 'Шаверма',
                                'photo_uri': (
                                    '/images/1368744/'
                                    'aafb68cebeb3e0edf6eb5aa73d80faf6'
                                    '-{w}x{h}.jpg'
                                ),
                                'picture_uri': (
                                    '/images/1368744/'
                                    '7eb79169054839e801225'
                                    'ebcdcc22c13.png'
                                ),
                                'promo_photo_uri': (
                                    '/images/1387779/'
                                    'ebc4de93763e64d9'
                                    '78f2012706fd9b2f-{w}x{h}'
                                    '.png'
                                ),
                                'slug': 'shaverma',
                            },
                            {
                                'genitive': 'шашлыка',
                                'name': 'Шашлык',
                                'photo_uri': (
                                    '/images/1380157/'
                                    'f82530e5ed9ede1aa310e830eca7cbc8'
                                    '-{w}x{h}.jpg'
                                ),
                                'picture_uri': (
                                    '/images/1368744/'
                                    '318909aa345cabca7'
                                    '78fded1d309c8de.png'
                                ),
                                'promo_photo_uri': (
                                    '/images/1387779/'
                                    '3578a3519e07f6e4f8'
                                    '5a1b66d48cce71'
                                    '-{w}x{h}.png'
                                ),
                                'slug': 'shashlyk',
                            },
                            {
                                'genitive': 'блюд грузинской кухни',
                                'name': 'Грузинская',
                                'photo_uri': (
                                    '/images/1380157/'
                                    '7261a46c7ee50edb6208bb58'
                                    'd07a47a9-{w}x{h}.jpg'
                                ),
                                'picture_uri': (
                                    '/images/1387779/'
                                    'd592dc20250aa916ce89'
                                    'd1162941d2c3.png'
                                ),
                                'promo_photo_uri': (
                                    '/images/1387779/'
                                    '9c1ca1a6878c6aedf6a0'
                                    '1bb5b7c90c5a'
                                    '-{w}x{h}.png'
                                ),
                                'slug': 'gruzinskaya',
                            },
                        ],
                    },
                },
            ],
            'timepickers': [
                {
                    'id': '9_timepickers',
                    'template_name': 'Widget template 6',
                    'payload': {
                        'timepicker': [
                            [
                                '2020-05-15T18:30:00+05:00',
                                '2020-05-15T19:00:00+05:00',
                                '2020-05-15T19:30:00+05:00',
                                '2020-05-15T20:00:00+05:00',
                                '2020-05-15T20:30:00+05:00',
                                '2020-05-15T21:00:00+05:00',
                                '2020-05-15T21:30:00+05:00',
                                '2020-05-15T22:00:00+05:00',
                                '2020-05-15T22:30:00+05:00',
                                '2020-05-15T23:00:00+05:00',
                                '2020-05-15T23:30:00+05:00',
                            ],
                            [
                                '2020-05-16T09:30:00+05:00',
                                '2020-05-16T10:00:00+05:00',
                                '2020-05-16T10:30:00+05:00',
                                '2020-05-16T11:00:00+05:00',
                                '2020-05-16T11:30:00+05:00',
                                '2020-05-16T12:00:00+05:00',
                                '2020-05-16T12:30:00+05:00',
                                '2020-05-16T13:00:00+05:00',
                            ],
                        ],
                    },
                },
            ],
            'banners': [
                {
                    'id': '3_banners',
                    'template_name': 'Widget template 3',
                    'payload': {
                        'design': {'type': 'shortcut'},
                        'banners': [
                            {
                                'id': 1,
                                'kind': 'info',
                                'url': 'https://eda.yandex/lavka',
                                'appLink': 'null',
                                'payload': {'badge': {'counter': 10}},
                                'images': [
                                    {
                                        'url': 'http://goolge.com',
                                        'theme': 'light',
                                        'platform': 'web',
                                    },
                                ],
                                'shortcuts': [
                                    {
                                        'url': 'http://goolge.com',
                                        'theme': 'light',
                                        'platform': 'web',
                                    },
                                ],
                                'meta': {'analytics': matching.any_string},
                            },
                        ],
                    },
                },
            ],
        },
        'layout': [
            {
                'id': '1_places_carousel',
                'payload': {'title': 'Бла бла бла'},
                'type': 'places_carousel',
            },
            {
                'id': '2_places_list',
                'payload': {'title': 'Три первых ресторана'},
                'type': 'places_list',
            },
            {
                'id': '3_banners',
                'payload': {'title': 'Что-то еще'},
                'type': 'banners',
            },
            {
                'id': '4_places_carousel',
                'payload': {'title': 'Акции и новинки'},
                'type': 'places_carousel',
            },
            {
                'id': '5_places_list',
                'payload': {'title': 'Остальные места'},
                'type': 'places_list',
            },
            {
                'id': '6_places_list',
                'payload': {'title': 'Закрытые места'},
                'type': 'places_list',
            },
            {'id': '7_sorts', 'payload': {'title': ''}, 'type': 'sorts'},
            {'id': '8_filters', 'payload': {'title': ''}, 'type': 'filters'},
            {
                'id': '9_timepickers',
                'payload': {'title': ''},
                'type': 'timepickers',
            },
        ],
    }
