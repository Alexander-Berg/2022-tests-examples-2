import pytest

from testsuite.utils import matching

CATALOG_RESPONSE = {
    'blocks': [
        {
            'id': 'open_history_order',
            'type': 'open',
            'list': [
                {
                    'payload': {
                        'name': 'First',
                        'slug': 'first',
                        'availability': {'is_available': True},
                        'layout': [
                            {
                                'type': 'meta',
                                'layout': [
                                    {'id': 'rating_1', 'type': 'rating'},
                                    {
                                        'id': 'price_category_1',
                                        'type': 'price_category',
                                    },
                                ],
                            },
                            {
                                'type': 'actions',
                                'layout': [{'id': 'promo_1', 'type': 'promo'}],
                            },
                        ],
                        'data': {
                            'meta': [
                                {
                                    'id': 'rating_1',
                                    'type': 'rating',
                                    'payload': {
                                        'icon': {
                                            'color': [],
                                            'uri': 'asset://rating_star',
                                        },
                                        'description': {
                                            'color': [],
                                            'text': '4.8 Хорошо',
                                        },
                                        'additional_text': {
                                            'color': [],
                                            'text': '(105)',
                                        },
                                    },
                                },
                                {
                                    'id': 'price_category_1',
                                    'type': 'price_category',
                                    'payload': {
                                        'icon_url': 'asset://price_category',
                                        'currency_sign': '₽',
                                        'total_symbols': 3,
                                        'highlighted_symbols': 2,
                                    },
                                },
                            ],
                            'actions': [
                                {
                                    'id': 'promo_1',
                                    'type': 'promo',
                                    'payload': {
                                        'icon_url': '/images/13828446e3.png',
                                        'accent_color': [
                                            {
                                                'theme': 'dark',
                                                'value': '#5AC31A',
                                            },
                                            {
                                                'theme': 'light',
                                                'value': '#5AC31A',
                                            },
                                        ],
                                        'title': 'Скидка 20%',
                                        'description': (
                                            'На Пицца Такино, Пицца Дьявола '
                                            'и Крем-суп из шампиньонов'
                                        ),
                                    },
                                },
                            ],
                        },
                    },
                    'meta': {'place_id': 1, 'brand_id': 1},
                },
            ],
        },
        {
            'id': 'any_history_order',
            'type': 'any',
            'list': [
                {
                    'payload': {
                        'name': 'First',
                        'slug': 'first',
                        'availability': {'is_available': True},
                        'layout': [
                            {
                                'type': 'meta',
                                'layout': [
                                    {'id': 'rating_1', 'type': 'rating'},
                                    {
                                        'id': 'price_category_1',
                                        'type': 'price_category',
                                    },
                                ],
                            },
                            {
                                'type': 'actions',
                                'layout': [{'id': 'promo_1', 'type': 'promo'}],
                            },
                        ],
                        'data': {
                            'meta': [
                                {
                                    'id': 'rating_1',
                                    'type': 'rating',
                                    'payload': {
                                        'icon': {
                                            'color': [],
                                            'uri': 'asset://rating_star',
                                        },
                                        'description': {
                                            'color': [],
                                            'text': '4.8 Хорошо',
                                        },
                                        'additional_text': {
                                            'color': [],
                                            'text': '(105)',
                                        },
                                    },
                                },
                                {
                                    'id': 'price_category_1',
                                    'type': 'price_category',
                                    'payload': {
                                        'icon_url': 'asset://price_category',
                                        'currency_sign': '₽',
                                        'total_symbols': 3,
                                        'highlighted_symbols': 2,
                                    },
                                },
                            ],
                            'actions': [
                                {
                                    'id': 'promo_1',
                                    'type': 'promo',
                                    'payload': {
                                        'icon_url': '/images/13828446e3.png',
                                        'accent_color': [
                                            {
                                                'theme': 'dark',
                                                'value': '#5AC31A',
                                            },
                                            {
                                                'theme': 'light',
                                                'value': '#5AC31A',
                                            },
                                        ],
                                        'title': 'Скидка 20%',
                                        'description': (
                                            'На Пицца Такино, Пицца Дьявола '
                                            'и Крем-суп из шампиньонов'
                                        ),
                                    },
                                },
                            ],
                        },
                    },
                    'meta': {'place_id': 1, 'brand_id': 1},
                },
                {
                    'payload': {
                        'name': 'Second',
                        'slug': 'second',
                        'availability': {'is_available': False},
                        'data': {'meta': [], 'actions': []},
                        'layout': [],
                    },
                    'meta': {'place_id': 2, 'brand_id': 2},
                },
            ],
        },
    ],
    'filters': {},
    'sort': {},
    'timepicker': [],
}


@pytest.mark.config(
    EATS_LAYOUT_CONSTRUCTOR_EXPERIMENT_SETTINGS={
        'check_experiment': True,
        'refresh_period_ms': 1000,
        'experiment_name': 'places_selection_template',
    },
)
@pytest.mark.experiments3(
    name='places_selection_template',
    consumers=['layout-constructor/layout'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Always enabled',
            'predicate': {'type': 'true'},
            'value': {'layout_slug': 'places_selection'},
        },
    ],
    default_value=True,
)
async def test_places_selection(taxi_eats_layout_constructor, mockserver):
    """
    Тестирует работу виджета places_selection
    EDACAT-347
    """

    def assert_request_block(data: dict, block_id: str, expected: dict):
        for block in data['blocks']:
            if block['id'] == block_id:
                assert block == expected
                return

        assert False, 'missing block with id {}'.format(block_id)

    @mockserver.json_handler('/eats-catalog/internal/v1/catalog-for-layout')
    def catalog(request):
        assert_request_block(
            request.json,
            'open_history_order',
            {
                'id': 'open_history_order',
                'type': 'open',
                'compilation_type': 'history_order',
                'disable_filters': False,
                'round_eta_to_hours': False,
            },
        )
        assert_request_block(
            request.json,
            'any_history_order',
            {
                'id': 'any_history_order',
                'type': 'any',
                'compilation_type': 'history_order',
                'disable_filters': False,
                'round_eta_to_hours': False,
            },
        )

        return CATALOG_RESPONSE

    response = await taxi_eats_layout_constructor.post(
        'eats/v1/layout-constructor/v1/layout',
        headers={
            'x-device-id': 'device-id',
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
    assert catalog.times_called == 1
    assert response.json() == {
        'data': {
            'places_lists': [
                {
                    'id': '1_places_collection',
                    'template_name': 'Selection',
                    'payload': {
                        'places': [
                            {
                                'name': 'First',
                                'slug': 'first',
                                'context': matching.any_string,
                                'analytics': matching.any_string,
                                'availability': {'is_available': True},
                                'data': {
                                    'meta': [
                                        {
                                            'id': 'price_category_1',
                                            'type': 'price_category',
                                            'payload': {
                                                'icon_url': (
                                                    'asset://price_category'
                                                ),
                                                'currency_sign': '₽',
                                                'total_symbols': 3,
                                                'highlighted_symbols': 2,
                                            },
                                        },
                                    ],
                                },
                                'layout': [
                                    {
                                        'type': 'meta',
                                        'layout': [
                                            {
                                                'id': 'price_category_1',
                                                'type': 'price_category',
                                            },
                                        ],
                                    },
                                ],
                            },
                        ],
                    },
                },
                {
                    'id': '3_places_collection',
                    'template_name': 'Selection',
                    'payload': {
                        'places': [
                            {
                                'name': 'First',
                                'slug': 'first',
                                'context': matching.any_string,
                                'analytics': matching.any_string,
                                'availability': {'is_available': True},
                                'data': {
                                    'meta': [
                                        {
                                            'id': 'price_category_1',
                                            'type': 'price_category',
                                            'payload': {
                                                'icon_url': (
                                                    'asset://price_category'
                                                ),
                                                'currency_sign': '₽',
                                                'total_symbols': 3,
                                                'highlighted_symbols': 2,
                                            },
                                        },
                                    ],
                                },
                                'layout': [
                                    {
                                        'type': 'meta',
                                        'layout': [
                                            {
                                                'id': 'price_category_1',
                                                'type': 'price_category',
                                            },
                                        ],
                                    },
                                ],
                            },
                            {
                                'name': 'Second',
                                'slug': 'second',
                                'context': matching.any_string,
                                'analytics': matching.any_string,
                                'availability': {'is_available': False},
                                'data': {'meta': []},
                                'layout': [{'layout': [], 'type': 'meta'}],
                            },
                        ],
                    },
                },
            ],
            'places_carousels': [
                {
                    'id': '2_places_collection',
                    'template_name': 'Selection',
                    'payload': {
                        'places': [
                            {
                                'name': 'First',
                                'slug': 'first',
                                'context': matching.any_string,
                                'analytics': matching.any_string,
                                'availability': {'is_available': True},
                                'layout': [
                                    {
                                        'type': 'meta',
                                        'layout': [
                                            {
                                                'id': 'price_category_1',
                                                'type': 'price_category',
                                            },
                                            {
                                                'id': 'rating_1',
                                                'type': 'rating',
                                            },
                                        ],
                                    },
                                    {
                                        'type': 'actions',
                                        'layout': [
                                            {'id': 'promo_1', 'type': 'promo'},
                                        ],
                                    },
                                ],
                                'data': {
                                    'meta': [
                                        {
                                            'id': 'price_category_1',
                                            'type': 'price_category',
                                            'payload': {
                                                'icon_url': (
                                                    'asset://price_category'
                                                ),
                                                'currency_sign': '₽',
                                                'total_symbols': 3,
                                                'highlighted_symbols': 2,
                                            },
                                        },
                                        {
                                            'id': 'rating_1',
                                            'type': 'rating',
                                            'payload': {
                                                'icon': {
                                                    'color': [],
                                                    'uri': (
                                                        'asset://rating_star'
                                                    ),
                                                },
                                                'description': {
                                                    'color': [],
                                                    'text': '4.8 Хорошо',
                                                },
                                                'additional_text': {
                                                    'color': [],
                                                    'text': '(105)',
                                                },
                                            },
                                        },
                                    ],
                                    'actions': [
                                        {
                                            'id': 'promo_1',
                                            'type': 'promo',
                                            'payload': {
                                                'icon_url': (
                                                    '/images/13828446e3.png'
                                                ),
                                                'accent_color': [
                                                    {
                                                        'theme': 'dark',
                                                        'value': '#5AC31A',
                                                    },
                                                    {
                                                        'theme': 'light',
                                                        'value': '#5AC31A',
                                                    },
                                                ],
                                                'title': 'Скидка 20%',
                                                'description': (
                                                    'На Пицца Такино, Пицца '
                                                    'Дьявола и Крем-суп из '
                                                    'шампиньонов'
                                                ),
                                            },
                                        },
                                    ],
                                },
                            },
                            {
                                'name': 'Second',
                                'slug': 'second',
                                'context': matching.any_string,
                                'analytics': matching.any_string,
                                'availability': {'is_available': False},
                                'data': {'meta': [], 'actions': []},
                                'layout': [
                                    {'type': 'meta', 'layout': []},
                                    {'type': 'actions', 'layout': []},
                                ],
                            },
                        ],
                    },
                },
            ],
        },
        'layout': [
            {
                'id': '1_places_collection',
                'payload': {},
                'type': 'places_list',
            },
            {
                'id': '2_places_collection',
                'payload': {},
                'type': 'places_carousel',
            },
            {
                'id': '3_places_collection',
                'payload': {},
                'type': 'places_list',
            },
        ],
    }
