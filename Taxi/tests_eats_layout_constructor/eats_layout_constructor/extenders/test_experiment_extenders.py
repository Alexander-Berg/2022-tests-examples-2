import pytest

from testsuite.utils import matching

from eats_layout_constructor import configs
from eats_layout_constructor import experiments

ACT_ID0 = 'experiment_extender_actions0'
ACT_ID1 = 'experiment_extender_actions1'
ACT_ID2 = 'experiment_extender_actions2'
ACT_ID3 = 'experiment_extender_actions3'
ACT_ID4 = 'experiment_extender_actions4'
ACT_ID5 = 'experiment_extender_actions5'
ACT_ID6 = 'experiment_extender_actions6'
ACT_ID7 = 'experiment_extender_actions7'

ACT_TYPE = 'my_cool_action_type'

META_ID0 = 'experiment_extender_meta0'
META_ID1 = 'experiment_extender_meta1'
META_ID2 = 'experiment_extender_meta2'
META_ID3 = 'experiment_extender_meta3'
META_ID4 = 'experiment_extender_meta4'
META_ID5 = 'experiment_extender_meta5'
META_ID6 = 'experiment_extender_meta6'
META_ID7 = 'experiment_extender_meta7'
META_ID8 = 'experiment_extender_meta8'

META_TYPE = 'my_cool_meta_type'


@pytest.mark.parametrize(
    'places, expected',
    [
        pytest.param(
            [
                {
                    'meta': {'place_id': 222, 'brand_id': 333},
                    'payload': {
                        'slug': 'first',
                        'data': {'actions': [], 'meta': []},
                        'layout': [],
                    },
                },
                {
                    'meta': {'place_id': 555, 'brand_id': 777},
                    'payload': {
                        'slug': 'first',
                        'data': {'actions': [], 'meta': []},
                        'layout': [],
                    },
                },
            ],
            {
                'data': {
                    'places_lists': [
                        {
                            'id': '1_places_list',
                            'template_name': 'Places List Template',
                            'payload': {
                                'places': [
                                    {
                                        'data': {
                                            'actions': [
                                                {
                                                    'id': ACT_ID0,
                                                    'payload': {
                                                        'title': (
                                                            'По вкусу вкусно'
                                                        ),
                                                    },
                                                    'type': ACT_TYPE,
                                                },
                                            ],
                                            'meta': [
                                                {
                                                    'id': META_ID0,
                                                    'payload': {
                                                        'title': 'Быстро',
                                                    },
                                                    'type': META_TYPE,
                                                },
                                            ],
                                        },
                                        'layout': [
                                            {
                                                'layout': [
                                                    {
                                                        'id': ACT_ID0,
                                                        'type': ACT_TYPE,
                                                    },
                                                ],
                                                'type': 'actions',
                                            },
                                            {
                                                'layout': [
                                                    {
                                                        'id': META_ID0,
                                                        'type': META_TYPE,
                                                    },
                                                ],
                                                'type': 'meta',
                                            },
                                        ],
                                        'slug': 'first',
                                        'context': matching.any_string,
                                    },
                                    {
                                        'data': {
                                            'actions': [
                                                {
                                                    'id': ACT_ID1,
                                                    'payload': {
                                                        'title': (
                                                            'По вкусу вкусно'
                                                        ),
                                                    },
                                                    'type': ACT_TYPE,
                                                },
                                            ],
                                            'meta': [
                                                {
                                                    'id': META_ID2,
                                                    'payload': {
                                                        'title': (
                                                            'Очень быстро'
                                                        ),
                                                    },
                                                    'type': META_TYPE,
                                                },
                                            ],
                                        },
                                        'layout': [
                                            {
                                                'layout': [
                                                    {
                                                        'id': ACT_ID1,
                                                        'type': ACT_TYPE,
                                                    },
                                                ],
                                                'type': 'actions',
                                            },
                                            {
                                                'layout': [
                                                    {
                                                        'id': META_ID2,
                                                        'type': META_TYPE,
                                                    },
                                                ],
                                                'type': 'meta',
                                            },
                                        ],
                                        'slug': 'first',
                                        'context': matching.any_string,
                                    },
                                ],
                            },
                        },
                    ],
                },
                'layout': [
                    {
                        'id': '1_places_list',
                        'payload': {},
                        'type': 'places_list',
                    },
                ],
            },
            id='Test with two places, two meta and two actions',
        ),
        pytest.param(
            [
                {
                    'meta': {'place_id': 8888, 'brand_id': 333},
                    'payload': {
                        'slug': 'first',
                        'data': {'actions': [], 'meta': []},
                        'layout': [],
                    },
                },
                {
                    'meta': {'place_id': 7777, 'brand_id': 777},
                    'payload': {
                        'slug': 'first',
                        'data': {'actions': [], 'meta': []},
                        'layout': [],
                    },
                },
            ],
            {
                'data': {
                    'places_lists': [
                        {
                            'id': '1_places_list',
                            'template_name': 'Places List Template',
                            'payload': {
                                'places': [
                                    {
                                        'data': {
                                            'actions': [
                                                {
                                                    'id': ACT_ID4,
                                                    'payload': {
                                                        'title': (
                                                            'По сути вкусно'
                                                        ),
                                                    },
                                                    'type': ACT_TYPE,
                                                },
                                            ],
                                            'meta': [],
                                        },
                                        'layout': [
                                            {
                                                'layout': [
                                                    {
                                                        'id': ACT_ID4,
                                                        'type': ACT_TYPE,
                                                    },
                                                ],
                                                'type': 'actions',
                                            },
                                            {'layout': [], 'type': 'meta'},
                                        ],
                                        'slug': 'first',
                                        'context': matching.any_string,
                                    },
                                    {
                                        'data': {
                                            'actions': [],
                                            'meta': [
                                                {
                                                    'id': META_ID4,
                                                    'payload': {
                                                        'title': 'Быстро',
                                                    },
                                                    'type': META_TYPE,
                                                },
                                            ],
                                        },
                                        'layout': [
                                            {'layout': [], 'type': 'actions'},
                                            {
                                                'layout': [
                                                    {
                                                        'id': META_ID4,
                                                        'type': META_TYPE,
                                                    },
                                                ],
                                                'type': 'meta',
                                            },
                                        ],
                                        'slug': 'first',
                                        'context': matching.any_string,
                                    },
                                ],
                            },
                        },
                    ],
                },
                'layout': [
                    {
                        'id': '1_places_list',
                        'payload': {},
                        'type': 'places_list',
                    },
                ],
            },
            id='Test with two places, one meta and one action',
        ),
        pytest.param(
            [
                {
                    'meta': {'place_id': 8888, 'brand_id': 333},
                    'payload': {
                        'slug': 'first',
                        'data': {'actions': [], 'meta': []},
                        'layout': [],
                    },
                },
            ],
            {
                'data': {
                    'places_lists': [
                        {
                            'id': '1_places_list',
                            'template_name': 'Places List Template',
                            'payload': {
                                'places': [
                                    {
                                        'data': {
                                            'actions': [
                                                {
                                                    'id': ACT_ID7,
                                                    'payload': {
                                                        'title': (
                                                            'По сути вкусно'
                                                        ),
                                                    },
                                                    'type': ACT_TYPE,
                                                },
                                            ],
                                            'meta': [],
                                        },
                                        'layout': [
                                            {
                                                'layout': [
                                                    {
                                                        'id': ACT_ID7,
                                                        'type': ACT_TYPE,
                                                    },
                                                ],
                                                'type': 'actions',
                                            },
                                            {'layout': [], 'type': 'meta'},
                                        ],
                                        'slug': 'first',
                                        'context': matching.any_string,
                                    },
                                ],
                            },
                        },
                    ],
                },
                'layout': [
                    {
                        'id': '1_places_list',
                        'payload': {},
                        'type': 'places_list',
                    },
                ],
            },
            id='Test with one place, one action and without meta',
        ),
        pytest.param(
            [
                {
                    'meta': {'place_id': 7777, 'brand_id': 777},
                    'payload': {
                        'slug': 'first',
                        'data': {'actions': [], 'meta': []},
                        'layout': [],
                    },
                },
            ],
            {
                'data': {
                    'places_lists': [
                        {
                            'id': '1_places_list',
                            'template_name': 'Places List Template',
                            'payload': {
                                'places': [
                                    {
                                        'data': {
                                            'actions': [],
                                            'meta': [
                                                {
                                                    'id': META_ID8,
                                                    'payload': {
                                                        'title': 'Быстро',
                                                    },
                                                    'type': META_TYPE,
                                                },
                                            ],
                                        },
                                        'layout': [
                                            {'layout': [], 'type': 'actions'},
                                            {
                                                'layout': [
                                                    {
                                                        'id': META_ID8,
                                                        'type': META_TYPE,
                                                    },
                                                ],
                                                'type': 'meta',
                                            },
                                        ],
                                        'slug': 'first',
                                        'context': matching.any_string,
                                    },
                                ],
                            },
                        },
                    ],
                },
                'layout': [
                    {
                        'id': '1_places_list',
                        'payload': {},
                        'type': 'places_list',
                    },
                ],
            },
            id='Test with one places, one meta and without action',
        ),
        pytest.param(
            [
                {
                    'meta': {'place_id': 2222, 'brand_id': 777},
                    'payload': {
                        'slug': 'first',
                        'data': {'actions': [], 'meta': []},
                        'layout': [],
                    },
                },
            ],
            {
                'data': {
                    'places_lists': [
                        {
                            'id': '1_places_list',
                            'template_name': 'Places List Template',
                            'payload': {
                                'places': [
                                    {
                                        'data': {'actions': [], 'meta': []},
                                        'layout': [
                                            {'layout': [], 'type': 'actions'},
                                            {'layout': [], 'type': 'meta'},
                                        ],
                                        'slug': 'first',
                                        'context': matching.any_string,
                                    },
                                ],
                            },
                        },
                    ],
                },
                'layout': [
                    {
                        'id': '1_places_list',
                        'payload': {},
                        'type': 'places_list',
                    },
                ],
            },
            id='Test with one places, without action and meta',
        ),
    ],
)
@configs.layout_experiment_name('eats_layout_template')
@experiments.layout(
    layout_slug='test_place_layout', experiment_name='eats_layout_template',
)
@pytest.mark.experiments3(
    name='eats_layout_constructor_extenders_experimental_my_cool_action',
    consumers=['layout-constructor/extenders/experimental'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'extender',
            'predicate': {'type': 'true'},
            'value': {
                'extenders': [
                    {
                        'kind': 'actions',
                        'payload': {'title': 'По вкусу вкусно'},
                        'place_ids': [222, 555, 9999],
                        'type': 'my_cool_action_type',
                    },
                    {
                        'kind': 'actions',
                        'payload': {'title': 'По сути вкусно'},
                        'place_ids': [666, 8888],
                        'type': 'my_cool_action_type',
                    },
                ],
            },
        },
    ],
)
@pytest.mark.experiments3(
    name='eats_layout_constructor_extenders_experimental_my_cool_meta',
    consumers=['layout-constructor/extenders/experimental'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'extender',
            'predicate': {'type': 'true'},
            'value': {
                'extenders': [
                    {
                        'kind': 'meta',
                        'payload': {'title': 'Быстро'},
                        'place_ids': [222, 7777],
                        'type': 'my_cool_meta_type',
                    },
                    {
                        'kind': 'meta',
                        'payload': {'title': 'Очень быстро'},
                        'place_ids': [666, 555, 6666, 7777],
                        'type': 'my_cool_meta_type',
                    },
                    {
                        'kind': 'meta',
                        'payload': {'title': 'Очень быстро но без поля тип'},
                        'place_ids': [666, 555, 6666, 7777],
                    },
                    {
                        'kind': 'meta',
                        'payload': {
                            'title': 'Очень быстро но поле тип не строка',
                        },
                        'place_ids': [666, 555, 6666, 7777],
                        'type': {},
                    },
                    {
                        'kind': 'meta',
                        'place_ids': [666, 555, 6666, 7777],
                        'type': 'my_cool_meta_type',
                    },
                    {
                        'kind': 'meta',
                        'payload': 'строка это не объект',
                        'place_ids': [666, 555, 6666, 7777],
                        'type': 'my_cool_meta_type',
                    },
                    {
                        'kind': {},
                        'payload': {'title': 'тут kind не строка'},
                        'place_ids': [666, 555, 6666, 7777],
                        'type': 'my_cool_meta_type',
                    },
                    {
                        'payload': {'title': 'тут kind отсутствует'},
                        'place_ids': [666, 555, 6666, 7777],
                        'type': 'my_cool_meta_type',
                    },
                ],
            },
        },
    ],
)
@pytest.mark.config(
    EATS_LAYOUT_CONSTRUCTOR_EXPERIMENT_SETTINGS={
        'check_experiment': True,
        'refresh_period_ms': 1000,
        'experiment_name': 'eats_layout_template',
    },
)
async def test_experiment_extender(
        taxi_eats_layout_constructor, mockserver, places, expected,
):
    @mockserver.json_handler('/eats-catalog/internal/v1/catalog-for-layout')
    def _catalog(request):
        assert request.json == {
            'location': {'latitude': 0.0, 'longitude': 0.0},
            'blocks': [
                {
                    'id': 'open',
                    'type': 'open',
                    'disable_filters': False,
                    'round_eta_to_hours': False,
                },
            ],
        }
        return {
            'places': [],
            'blocks': [{'id': 'open', 'list': places}],
            'filters': {},
            'sort': {},
            'timepicker': [],
        }

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
    assert response.json() == expected
