import pytest

from testsuite.utils import matching

from eats_layout_constructor import configs
from eats_layout_constructor import experiments
from eats_layout_constructor import utils


def badge_action_experiment(
        use_details_form: bool, use_order_stats: bool = False,
):
    experiment_value = {
        'enabled': True,
        'promo_type_ids': ['100'],
        'dark': {'text_color': '#FFFFFF'},
        'light': {'text_color': '#000000'},
    }
    if use_details_form:
        experiment_value['details_form'] = {'text': 'Закрыть'}

    if use_order_stats:
        predicate = {
            'init': {
                'predicates': [
                    {
                        'init': {
                            'predicate': {
                                'init': {'arg_name': 'is_eda_new_user'},
                                'type': 'bool',
                            },
                        },
                        'type': 'not',
                    },
                    {
                        'init': {
                            'predicate': {
                                'init': {'arg_name': 'is_retail_new_user'},
                                'type': 'bool',
                            },
                        },
                        'type': 'not',
                    },
                ],
            },
            'type': 'all_of',
        }
    else:
        predicate = {'type': 'true'}

    return pytest.mark.experiments3(
        name='eats_layout_constructor_badge_action',
        consumers=['layout-constructor/extenders/badge_action'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[
            {
                'title': 'extender',
                'predicate': predicate,
                'value': experiment_value,
            },
        ],
    )


@pytest.mark.parametrize(
    'places,expected',
    [
        (
            [
                {
                    'id': 'open',
                    'type': 'open',
                    'list': [
                        {
                            'meta': {'place_id': 1, 'brand_id': 1},
                            'payload': {
                                'slug': 'first',
                                'data': {
                                    'actions': [
                                        {
                                            'id': 'aaabbb',
                                            'type': 'promo',
                                            'payload': {
                                                'promo_type_id': '100',
                                                'icon_url': 'a.png',
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
                                                'title': 'zagolobok',
                                                'description': 'podz',
                                                'extended': {
                                                    'title': 'zagolobok',
                                                    'content': 'podz',
                                                    'button': {
                                                        'title': 'a',
                                                        'url': '',
                                                    },
                                                },
                                            },
                                        },
                                        {
                                            'id': 'bbbccc',
                                            'type': 'promo',
                                            'payload': {
                                                'promo_type_id': '155',
                                                'icon_url': 'a.png',
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
                                                'title': 'adada',
                                                'description': 'ffff',
                                                'extended': {
                                                    'title': 'adad',
                                                    'content': 'ffff',
                                                    'button': {
                                                        'title': 'a',
                                                        'url': '',
                                                    },
                                                },
                                            },
                                        },
                                    ],
                                    'meta': [],
                                },
                                'layout': [
                                    {
                                        'type': 'actions',
                                        'layout': [
                                            {'id': 'aaabbb', 'type': 'promo'},
                                        ],
                                    },
                                ],
                            },
                        },
                        {
                            'meta': {'place_id': 2, 'brand_id': 1},
                            'payload': {
                                'slug': 'second',
                                'data': {'actions': [], 'meta': []},
                                'layout': [],
                            },
                        },
                    ],
                },
            ],
            {
                'data': {
                    'places_lists': [
                        {
                            'id': '1_places_collection',
                            'template_name': 'list_template',
                            'payload': {
                                'places': [
                                    {
                                        'data': {
                                            'actions': [
                                                {
                                                    'id': 'bbbccc',
                                                    'type': 'promo',
                                                    'payload': {
                                                        'icon_url': 'a.png',
                                                        'accent_color': [
                                                            {
                                                                'theme': (
                                                                    'dark'
                                                                ),
                                                                'value': (
                                                                    '#5AC31A'
                                                                ),
                                                            },
                                                            {
                                                                'theme': (
                                                                    'light'
                                                                ),
                                                                'value': (
                                                                    '#5AC31A'
                                                                ),
                                                            },
                                                        ],
                                                        'title': 'adada',
                                                        'description': 'ffff',
                                                        'extended': {
                                                            'title': 'adad',
                                                            'content': 'ffff',
                                                            'button': {
                                                                'title': 'a',
                                                                'url': '',
                                                            },
                                                        },
                                                    },
                                                },
                                            ],
                                            'features': {
                                                'badge': {
                                                    'color': [
                                                        {
                                                            'theme': 'light',
                                                            'value': '#000000',
                                                        },
                                                        {
                                                            'theme': 'dark',
                                                            'value': '#FFFFFF',
                                                        },
                                                    ],
                                                    'icon_url': 'a.png',
                                                    'styles': {
                                                        'rainbow': False,
                                                    },
                                                    'text': 'zagolobok',
                                                },
                                            },
                                        },
                                        'layout': [
                                            {
                                                'layout': [
                                                    {
                                                        'id': 'bbbccc',
                                                        'type': 'promo',
                                                    },
                                                ],
                                                'type': 'actions',
                                            },
                                        ],
                                        'slug': 'first',
                                        'context': matching.any_string,
                                        'analytics': matching.any_string,
                                    },
                                    {
                                        'data': {'actions': []},
                                        'layout': [
                                            {'layout': [], 'type': 'actions'},
                                        ],
                                        'slug': 'second',
                                        'context': matching.any_string,
                                        'analytics': matching.any_string,
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
                ],
            },
        ),
    ],
)
@configs.layout_experiment_name()
@experiments.layout('test_place_layout')
@pytest.mark.layout(
    slug='test_place_layout',
    widgets=[
        utils.Widget(
            name='list',
            type='places_collection',
            meta={'place_filter_type': 'open', 'output_type': 'list'},
            payload={},
            payload_schema={},
            meta_widget=utils.MetaWidget(
                type='place_layout',
                name='meta_widget',
                slug='meta_widget',
                settings={
                    'order': ['actions'],
                    'action_extenders': [
                        'actions_promo',
                        'actions_badge_extender',
                    ],
                    'meta_extenders': [],
                },
            ),
        ),
    ],
)
@pytest.mark.parametrize(
    'use_details_form',
    [
        pytest.param(
            False, marks=badge_action_experiment(use_details_form=False),
        ),
        pytest.param(
            True, marks=badge_action_experiment(use_details_form=True),
        ),
        pytest.param(
            True,
            marks=badge_action_experiment(
                use_details_form=True, use_order_stats=True,
            ),
        ),
    ],
)
async def test_actions_badge_extender(
        layout_constructor, mockserver, places, expected, use_details_form,
):
    @mockserver.json_handler('/eats-catalog/internal/v1/catalog-for-layout')
    def _catalog(request):
        return {'blocks': places, 'filters': {}, 'sort': {}, 'timepicker': []}

    response = await layout_constructor.post()

    assert response.status_code == 200
    response_json = response.json()

    if use_details_form:
        details_form = {
            'background': {'styles': {'rainbow': False}},
            'button': {'title': 'Закрыть'},
            'description': 'podz',
            'image_url': 'a.png',
            'title': 'zagolobok',
        }
        place = expected['data']['places_lists'][0]['payload']['places'][0]
        place['data']['features']['badge']['details_form'] = details_form

    assert response_json == expected


@pytest.mark.parametrize(
    'places,expected',
    [
        (
            [
                {
                    'id': 'open',
                    'type': 'open',
                    'list': [
                        {
                            'meta': {'place_id': 1, 'brand_id': 1},
                            'payload': {
                                'slug': 'first',
                                'data': {
                                    'actions': [
                                        {
                                            'id': 'aaabbb',
                                            'type': 'promo',
                                            'payload': {
                                                'promo_type_id': '100',
                                                'icon_url': 'a.png',
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
                                                'title': 'zagolobok',
                                                'description': 'podz',
                                                'extended': {
                                                    'title': 'zagolobok',
                                                    'content': 'podz',
                                                    'button': {
                                                        'title': 'a',
                                                        'url': '',
                                                    },
                                                },
                                            },
                                        },
                                        {
                                            'id': 'bbbccc',
                                            'type': 'promo',
                                            'payload': {
                                                'promo_type_id': '155',
                                                'icon_url': 'a.png',
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
                                                'title': 'adada',
                                                'description': 'ffff',
                                                'extended': {
                                                    'title': 'adad',
                                                    'content': 'ffff',
                                                    'button': {
                                                        'title': 'a',
                                                        'url': '',
                                                    },
                                                },
                                            },
                                        },
                                    ],
                                    'features': {
                                        'badge': {
                                            'color': [
                                                {
                                                    'theme': 'light',
                                                    'value': '#000000',
                                                },
                                                {
                                                    'theme': 'dark',
                                                    'value': '#FFFFFF',
                                                },
                                            ],
                                            'icon_url': 'a.png',
                                            'styles': {'rainbow': False},
                                            'text': 'asdasdasd',
                                        },
                                    },
                                    'meta': [],
                                },
                                'layout': [
                                    {
                                        'type': 'actions',
                                        'layout': [
                                            {'id': 'aaabbb', 'type': 'promo'},
                                        ],
                                    },
                                ],
                            },
                        },
                        {
                            'meta': {'place_id': 2, 'brand_id': 1},
                            'payload': {
                                'slug': 'second',
                                'data': {'actions': [], 'meta': []},
                                'layout': [],
                            },
                        },
                    ],
                },
            ],
            {
                'data': {
                    'places_lists': [
                        {
                            'id': '1_places_collection',
                            'template_name': 'list_template',
                            'payload': {
                                'places': [
                                    {
                                        'data': {
                                            'actions': [
                                                {
                                                    'id': 'aaabbb',
                                                    'type': 'promo',
                                                    'payload': {
                                                        'icon_url': 'a.png',
                                                        'accent_color': [
                                                            {
                                                                'theme': (
                                                                    'dark'
                                                                ),
                                                                'value': (
                                                                    '#5AC31A'
                                                                ),
                                                            },
                                                            {
                                                                'theme': (
                                                                    'light'
                                                                ),
                                                                'value': (
                                                                    '#5AC31A'
                                                                ),
                                                            },
                                                        ],
                                                        'title': 'zagolobok',
                                                        'description': 'podz',
                                                        'extended': {
                                                            'title': (
                                                                'zagolobok'
                                                            ),
                                                            'content': 'podz',
                                                            'button': {
                                                                'title': 'a',
                                                                'url': '',
                                                            },
                                                        },
                                                    },
                                                },
                                                {
                                                    'id': 'bbbccc',
                                                    'type': 'promo',
                                                    'payload': {
                                                        'icon_url': 'a.png',
                                                        'accent_color': [
                                                            {
                                                                'theme': (
                                                                    'dark'
                                                                ),
                                                                'value': (
                                                                    '#5AC31A'
                                                                ),
                                                            },
                                                            {
                                                                'theme': (
                                                                    'light'
                                                                ),
                                                                'value': (
                                                                    '#5AC31A'
                                                                ),
                                                            },
                                                        ],
                                                        'title': 'adada',
                                                        'description': 'ffff',
                                                        'extended': {
                                                            'title': 'adad',
                                                            'content': 'ffff',
                                                            'button': {
                                                                'title': 'a',
                                                                'url': '',
                                                            },
                                                        },
                                                    },
                                                },
                                            ],
                                            'features': {
                                                'badge': {
                                                    'color': [
                                                        {
                                                            'theme': 'light',
                                                            'value': '#000000',
                                                        },
                                                        {
                                                            'theme': 'dark',
                                                            'value': '#FFFFFF',
                                                        },
                                                    ],
                                                    'icon_url': 'a.png',
                                                    'styles': {
                                                        'rainbow': False,
                                                    },
                                                    'text': 'asdasdasd',
                                                },
                                            },
                                        },
                                        'layout': [
                                            {
                                                'layout': [
                                                    {
                                                        'id': 'aaabbb',
                                                        'type': 'promo',
                                                    },
                                                    {
                                                        'id': 'bbbccc',
                                                        'type': 'promo',
                                                    },
                                                ],
                                                'type': 'actions',
                                            },
                                        ],
                                        'slug': 'first',
                                        'context': matching.any_string,
                                        'analytics': matching.any_string,
                                    },
                                    {
                                        'data': {'actions': []},
                                        'layout': [
                                            {'layout': [], 'type': 'actions'},
                                        ],
                                        'slug': 'second',
                                        'context': matching.any_string,
                                        'analytics': matching.any_string,
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
                ],
            },
        ),
    ],
)
@configs.layout_experiment_name()
@experiments.layout('test_place_layout')
@pytest.mark.layout(
    slug='test_place_layout',
    widgets=[
        utils.Widget(
            name='list',
            type='places_collection',
            meta={'place_filter_type': 'open', 'output_type': 'list'},
            payload={},
            payload_schema={},
            meta_widget=utils.MetaWidget(
                type='place_layout',
                name='meta_widget',
                slug='meta_widget',
                settings={
                    'order': ['actions'],
                    'action_extenders': [
                        'actions_promo',
                        'actions_badge_extender',
                    ],
                    'meta_extenders': [],
                },
            ),
        ),
    ],
)
@badge_action_experiment(True)
async def test_actions_badge_extender_badge_exists(
        layout_constructor, mockserver, places, expected,
):
    @mockserver.json_handler('/eats-catalog/internal/v1/catalog-for-layout')
    def _catalog(request):
        return {'blocks': places, 'filters': {}, 'sort': {}, 'timepicker': []}

    response = await layout_constructor.post()

    assert response.status_code == 200
    response_json = response.json()

    assert response_json == expected
