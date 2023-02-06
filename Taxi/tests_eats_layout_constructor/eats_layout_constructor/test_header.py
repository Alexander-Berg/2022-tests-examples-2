from testsuite.utils import matching

from . import configs
from . import experiments
from . import translations


TRANSLATIONS = {
    'rest.1': 'рестораны 1',
    'rest.2': 'рестораны 2',
    'rest.3': 'рестораны 3',
    'rest.4': 'рестораны 4',
    'rest.5': 'рестораны 5',
    'all': 'все',
}

CATALOG_RESPONSE = {
    'blocks': [
        {
            'id': 'open',
            'type': 'open',
            'list': [
                {
                    'meta': {'place_id': 1, 'brand_id': 1},
                    'payload': {'id': 'id-snedi', 'name': 'Снеди Феди'},
                },
                {
                    'meta': {'place_id': 2, 'brand_id': 2},
                    'payload': {'id': 'id-paul', 'name': 'Paul'},
                },
                {
                    'meta': {'place_id': 3, 'brand_id': 3},
                    'payload': {'id': 'id-ramen-club', 'name': 'Рамен Club'},
                },
            ],
        },
    ],
    'filters': {
        'current': 'shaverma',
        'list': [
            {
                'genitive': 'шаверма',
                'name': 'Шаверма',
                'photo_uri': '/images/шаверма/{w}x{h}.jpg',
                'picture_uri': '/images/шаверма/100x200.png',
                'promo_photo_uri': '/images/шаверма/promo-{w}x{h}.png',
                'slug': 'shaverma',
            },
            {
                'genitive': 'шашлыка',
                'name': 'Шашлык',
                'photo_uri': '/images/шашлык/{w}x{h}.jpg',
                'picture_uri': '/images/шашлык/100x200.png',
                'promo_photo_uri': '/images/шашлык/promo-{w}x{h}.png',
                'slug': 'shashlyk',
            },
            {
                'genitive': 'блюд грузинской кухни',
                'name': 'Грузинская',
                'photo_uri': '/images/грузинская/{w}x{h}.jpg',
                'picture_uri': '/images/грузинская/100x200.png',
                'promo_photo_uri': '/images/грузинская/promo-{w}x{h}.png',
                'slug': 'gruzinskaya',
            },
        ],
    },
    'sort': {
        'current': 'default',
        'default': 'default',
        'list': [
            {'description': 'Доверюсь вам', 'slug': 'default'},
            {'description': 'Быстрые', 'slug': 'fast_delivery'},
            {'description': 'Недорогие', 'slug': 'cheap_first'},
        ],
    },
    'timepicker': [
        [
            '2020-05-15T22:00:00+03:00',
            '2020-05-15T22:30:00+03:00',
            '2020-05-15T23:00:00+03:00',
            '2020-05-15T23:30:00+03:00',
        ],
        [
            '2020-05-16T09:30:00+03:00',
            '2020-05-16T10:00:00+03:00',
            '2020-05-16T10:30:00+03:00',
            '2020-05-16T11:00:00+03:00',
        ],
    ],
}


@configs.layout_experiment_name(name='eats_layout_template')
@experiments.layout('basic_header_1')
@translations.eats_layout_constructor_ru(TRANSLATIONS)
async def test_eats_layout_header_basic(
        taxi_eats_layout_constructor, mockserver,
):
    """
    Test checks basic behaviour of Header widget.
    """

    @mockserver.json_handler(
        '/eats-communications/eats-communications/v1/layout/banners',
    )
    def _banners(request):
        return {'payload': {'blocks': [], 'banners': [], 'header_notes': []}}

    @mockserver.json_handler('/eats-catalog/internal/v1/catalog-for-layout')
    def _catalog(request):
        return CATALOG_RESPONSE

    response = await taxi_eats_layout_constructor.post(
        'eats/v1/layout-constructor/v1/layout',
        headers={
            'x-device-id': 'basic',
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
            'headers': [
                {
                    'id': '1_header',
                    'template_name': 'Basic header widget',
                    'payload': {'text': 'рестораны 1', 'styles': {}},
                },
            ],
            'places_lists': [
                {
                    'id': '2_places_list',
                    'template_name': 'Open places',
                    'payload': {
                        'places': [
                            {
                                'id': 'id-snedi',
                                'name': 'Снеди Феди',
                                'context': matching.any_string,
                            },
                            {
                                'id': 'id-paul',
                                'name': 'Paul',
                                'context': matching.any_string,
                            },
                            {
                                'id': 'id-ramen-club',
                                'name': 'Рамен Club',
                                'context': matching.any_string,
                            },
                        ],
                    },
                },
            ],
        },
        'layout': [
            {'id': '1_header', 'payload': {}, 'type': 'header'},
            {'id': '2_places_list', 'payload': {}, 'type': 'places_list'},
        ],
    }


@configs.layout_experiment_name(name='eats_layout_template')
@experiments.layout('header_with_button_and_styles_1')
@translations.eats_layout_constructor_ru(TRANSLATIONS)
async def test_eats_layout_header_with_button_and_styles(
        taxi_eats_layout_constructor, mockserver,
):
    """
    Test checks a Header with button and styles.
    """

    @mockserver.json_handler('/eats-catalog/internal/v1/catalog-for-layout')
    def _catalog(request):
        return CATALOG_RESPONSE

    response = await taxi_eats_layout_constructor.post(
        'eats/v1/layout-constructor/v1/layout',
        headers={
            'x-device-id': 'with_button_and_styles',
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
            'headers': [
                {
                    'id': '3_header',
                    'template_name': 'Header widget with button and styles',
                    'payload': {
                        'text': 'рестораны 2',
                        'styles': {'bold': True},
                        'button': {
                            'text': 'все',
                            'deeplink': 'eda.yandex://collections/places',
                        },
                    },
                },
            ],
            'places_lists': [
                {
                    'id': '4_places_list',
                    'template_name': 'Open places',
                    'payload': {
                        'places': [
                            {
                                'id': 'id-snedi',
                                'name': 'Снеди Феди',
                                'context': matching.any_string,
                            },
                            {
                                'id': 'id-paul',
                                'name': 'Paul',
                                'context': matching.any_string,
                            },
                            {
                                'id': 'id-ramen-club',
                                'name': 'Рамен Club',
                                'context': matching.any_string,
                            },
                        ],
                    },
                },
            ],
        },
        'layout': [
            {'id': '3_header', 'payload': {}, 'type': 'header'},
            {'id': '4_places_list', 'payload': {}, 'type': 'places_list'},
        ],
    }


@configs.layout_experiment_name(name='eats_layout_template')
@experiments.layout('header_depends_on_one_1')
@translations.eats_layout_constructor_ru(TRANSLATIONS)
async def test_eats_layout_header_depends_on_one(
        taxi_eats_layout_constructor, mockserver,
):
    """
    Test checks a Header which depends on one another widget.
    """

    @mockserver.json_handler('/eats-catalog/internal/v1/catalog-for-layout')
    def _catalog(request):
        return CATALOG_RESPONSE

    response = await taxi_eats_layout_constructor.post(
        'eats/v1/layout-constructor/v1/layout',
        headers={
            'x-device-id': 'header_depends_on_one',
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
            'headers': [
                {
                    'id': '5_header',
                    'template_name': 'Header widget depends on one',
                    'payload': {'text': 'рестораны 3', 'styles': {}},
                },
            ],
            'places_lists': [
                {
                    'id': '6_places_list',
                    'template_name': 'Open places',
                    'payload': {
                        'places': [
                            {
                                'id': 'id-snedi',
                                'name': 'Снеди Феди',
                                'context': matching.any_string,
                            },
                            {
                                'id': 'id-paul',
                                'name': 'Paul',
                                'context': matching.any_string,
                            },
                            {
                                'id': 'id-ramen-club',
                                'name': 'Рамен Club',
                                'context': matching.any_string,
                            },
                        ],
                    },
                },
            ],
        },
        'layout': [
            {'id': '5_header', 'payload': {}, 'type': 'header'},
            {'id': '6_places_list', 'payload': {}, 'type': 'places_list'},
        ],
    }


@configs.layout_experiment_name(name='eats_layout_template')
@experiments.layout('header_depends_on_two_1')
@translations.eats_layout_constructor_ru(TRANSLATIONS)
async def test_eats_layout_header_depends_on_two(
        taxi_eats_layout_constructor, mockserver,
):
    """
    Test checks a Header which depends on one non-existed and one existed.
    """

    @mockserver.json_handler('/eats-catalog/internal/v1/catalog-for-layout')
    def _catalog(request):
        return CATALOG_RESPONSE

    response = await taxi_eats_layout_constructor.post(
        'eats/v1/layout-constructor/v1/layout',
        headers={
            'x-device-id': 'header_depends_on_two',
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
            'headers': [
                {
                    'id': '7_header',
                    'template_name': 'Header widget depends on two',
                    'payload': {'text': 'рестораны 4', 'styles': {}},
                },
            ],
            'places_lists': [
                {
                    'id': '8_places_list',
                    'template_name': 'Open places',
                    'payload': {
                        'places': [
                            {
                                'id': 'id-snedi',
                                'name': 'Снеди Феди',
                                'context': matching.any_string,
                            },
                            {
                                'id': 'id-paul',
                                'name': 'Paul',
                                'context': matching.any_string,
                            },
                            {
                                'id': 'id-ramen-club',
                                'name': 'Рамен Club',
                                'context': matching.any_string,
                            },
                        ],
                    },
                },
            ],
        },
        'layout': [
            {'id': '7_header', 'payload': {}, 'type': 'header'},
            {'id': '8_places_list', 'payload': {}, 'type': 'places_list'},
        ],
    }


@configs.layout_experiment_name(name='eats_layout_template')
@experiments.layout('header_depends_on_unknown_1')
@translations.eats_layout_constructor_ru(TRANSLATIONS)
async def test_eats_layout_header_depends_on_unknown(
        taxi_eats_layout_constructor, mockserver,
):
    """
    Test checks a Header which depends on unknown widget.
    """

    @mockserver.json_handler('/eats-catalog/internal/v1/catalog-for-layout')
    def _catalog(request):
        return CATALOG_RESPONSE

    response = await taxi_eats_layout_constructor.post(
        'eats/v1/layout-constructor/v1/layout',
        headers={
            'x-device-id': 'header_depends_on_unknown',
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
            'places_lists': [
                {
                    'id': '10_places_list',
                    'template_name': 'Open places',
                    'payload': {
                        'places': [
                            {
                                'id': 'id-snedi',
                                'name': 'Снеди Феди',
                                'context': matching.any_string,
                            },
                            {
                                'id': 'id-paul',
                                'name': 'Paul',
                                'context': matching.any_string,
                            },
                            {
                                'id': 'id-ramen-club',
                                'name': 'Рамен Club',
                                'context': matching.any_string,
                            },
                        ],
                    },
                },
            ],
        },
        'layout': [
            {'id': '10_places_list', 'payload': {}, 'type': 'places_list'},
        ],
    }


@configs.layout_experiment_name(name='eats_layout_template')
@experiments.layout('header_depends_on_empty_string_1')
async def test_eats_layout_header_depends_on_empty_string(
        taxi_eats_layout_constructor, mockserver,
):
    """
    Test checks a Header which depends on empty ID strings
    """

    @mockserver.json_handler('/eats-catalog/internal/v1/catalog-for-layout')
    def _catalog(request):
        return CATALOG_RESPONSE

    response = await taxi_eats_layout_constructor.post(
        'eats/v1/layout-constructor/v1/layout',
        headers={
            'x-device-id': 'header_depends_on_empty_string',
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
            'places_lists': [
                {
                    'id': '12_places_list',
                    'template_name': 'Open places',
                    'payload': {
                        'places': [
                            {
                                'id': 'id-snedi',
                                'name': 'Снеди Феди',
                                'context': matching.any_string,
                            },
                            {
                                'id': 'id-paul',
                                'name': 'Paul',
                                'context': matching.any_string,
                            },
                            {
                                'id': 'id-ramen-club',
                                'name': 'Рамен Club',
                                'context': matching.any_string,
                            },
                        ],
                    },
                },
            ],
        },
        'layout': [
            {'id': '12_places_list', 'payload': {}, 'type': 'places_list'},
        ],
    }


@configs.layout_experiment_name(name='eats_layout_template')
@experiments.layout('basic_header_1')
@translations.eats_layout_constructor_ru(TRANSLATIONS)
async def test_header_notes(taxi_eats_layout_constructor, mockserver):
    @mockserver.json_handler(
        '/eats-communications/eats-communications/v1/layout/banners',
    )
    def _banners(request):
        return {
            'payload': {
                'blocks': [],
                'banners': [],
                'header_notes': [
                    {
                        'type': 'eats_free_delivery',
                        'payload': {
                            'icon': {
                                'color': [
                                    {'theme': 'dark', 'value': '#000000'},
                                ],
                                'uri': 'http://icon',
                            },
                            'text': {
                                'color': [
                                    {'theme': 'light', 'value': '#111111'},
                                ],
                                'text': 'Header note',
                            },
                        },
                    },
                ],
            },
        }

    @mockserver.json_handler('/eats-catalog/internal/v1/catalog-for-layout')
    def _catalog(request):
        return CATALOG_RESPONSE

    response = await taxi_eats_layout_constructor.post(
        'eats/v1/layout-constructor/v1/layout',
        headers={
            'x-device-id': 'basic',
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

    data = response.json()

    assert data['data']['headers'] == [
        {
            'id': '1_header',
            'template_name': 'Basic header widget',
            'payload': {
                'text': 'рестораны 1',
                'styles': {},
                'note': {
                    'icon': {
                        'color': [{'theme': 'dark', 'value': '#000000'}],
                        'uri': 'http://icon',
                    },
                    'text': {
                        'color': [{'theme': 'light', 'value': '#111111'}],
                        'text': 'Header note',
                    },
                },
            },
        },
    ]
