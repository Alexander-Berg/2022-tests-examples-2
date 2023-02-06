import pytest

from testsuite.utils import matching

from . import configs
from . import experiments

CATALOG_RESPONSE = {
    'blocks': [
        {
            'id': 'open',
            'type': 'open',
            'list': [
                {
                    'payload': {
                        'layout': [
                            {
                                'type': 'meta',
                                'layout': [
                                    {'id': '2', 'type': 'price_category'},
                                ],
                            },
                            {
                                'type': 'actions',
                                'layout': [{'id': '1', 'type': 'promo'}],
                            },
                        ],
                        'data': {
                            'meta': [
                                {
                                    'id': '2',
                                    'type': 'price_category',
                                    'payload': {
                                        'icon_url': 'asset://price_category',
                                    },
                                },
                            ],
                            'actions': [
                                {
                                    'id': '1',
                                    'type': 'promo',
                                    'payload': {
                                        'title': 'Promo title',
                                        'description': 'Promo description',
                                    },
                                },
                            ],
                        },
                    },
                    'meta': {'place_id': 1, 'brand_id': 1},
                },
            ],
        },
    ],
    'places': [],
    'filters': {
        'list': [
            {
                'name': 'Самовывоз',
                'slug': 'pickup',
                'type': 'pickup',
                'group': 'shipping',
                'active': False,
            },
        ],
    },
    'sort': {
        'current': 'default',
        'default': 'default',
        'list': [{'slug': 'default', 'description': 'Доверюсь вам'}],
    },
    'timepicker': [
        ['2020-10-02T17:30:00+03:00', '2020-10-02T18:00:00+03:00'],
        [],
    ],
}


@configs.layout_experiment_name()
@pytest.mark.parametrize(
    'expected_place',
    [
        pytest.param(
            {
                'layout': [
                    {
                        'type': 'actions',
                        'layout': [{'id': '1', 'type': 'promo'}],
                    },
                ],
                'data': {
                    'actions': [
                        {
                            'id': '1',
                            'type': 'promo',
                            'payload': {
                                'title': 'Promo title',
                                'description': 'Promo description',
                            },
                        },
                    ],
                },
                'context': matching.any_string,
            },
            marks=experiments.layout('layout_1'),
            id='Layout with meta widget from field',
        ),
        pytest.param(
            {
                'layout': [
                    {
                        'type': 'meta',
                        'layout': [{'id': '2', 'type': 'price_category'}],
                    },
                ],
                'data': {
                    'meta': [
                        {
                            'id': '2',
                            'type': 'price_category',
                            'payload': {'icon_url': 'asset://price_category'},
                        },
                    ],
                },
                'context': matching.any_string,
            },
            marks=(
                experiments.layout('layout_2'),
                experiments.meta_widget('second'),
            ),
            id='Layout with meta widget from experiment',
        ),
        pytest.param(
            {
                'layout': [
                    {
                        'type': 'actions',
                        'layout': [{'id': '1', 'type': 'promo'}],
                    },
                ],
                'data': {
                    'actions': [
                        {
                            'id': '1',
                            'type': 'promo',
                            'payload': {
                                'title': 'Promo title',
                                'description': 'Promo description',
                            },
                        },
                    ],
                },
                'context': matching.any_string,
            },
            marks=(
                experiments.layout('layout_3'),
                experiments.always_match(
                    name='invalid_meta_widget_experiment',
                    consumer='layout-constructor/meta-widget',
                    value={'meta_widget_slug': {'hello': 'world'}},
                ),
            ),
            id='Layout with invalid meta widget experiment',
        ),
        pytest.param(
            {
                'layout': [
                    {
                        'type': 'actions',
                        'layout': [{'id': '1', 'type': 'promo'}],
                    },
                ],
                'data': {
                    'actions': [
                        {
                            'id': '1',
                            'type': 'promo',
                            'payload': {
                                'title': 'Promo title',
                                'description': 'Promo description',
                            },
                        },
                    ],
                },
                'context': matching.any_string,
            },
            marks=experiments.layout('layout_4'),
            id='Layout with unknown meta widget experiment',
        ),
    ],
)
async def test_meta_widget(
        taxi_eats_layout_constructor, mockserver, expected_place,
):
    @mockserver.json_handler('/eats-catalog/internal/v1/catalog-for-layout')
    def catalog(_):
        return CATALOG_RESPONSE

    response = await taxi_eats_layout_constructor.post(
        'eats/v1/layout-constructor/v1/layout',
        headers={
            'x-device-id': 'some',
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

    places_lists = response.json()['data']['places_lists']
    assert len(places_lists) == 1

    places = places_lists[0]['payload']['places']
    assert len(places) == 1

    assert places[0] == expected_place


@pytest.mark.now('2020-10-06T13:30:00+0300')
@configs.layout_experiment_name()
@experiments.layout('layout_5')
async def test_meta_widget_advertisements(
        taxi_eats_layout_constructor, mockserver,
):
    expected_places = [
        {
            'id': 'id_1',
            'name': 'name_1',
            'context': matching.any_string,
            'layout': [
                {
                    'type': 'meta',
                    'layout': [
                        {'id': '3', 'type': 'advertisements'},
                        {'id': '2', 'type': 'price_category'},
                    ],
                },
            ],
            'data': {
                'meta': [
                    {
                        'id': '3',
                        'type': 'advertisements',
                        'payload': {
                            'text': {
                                'color': [
                                    {'theme': 'light', 'value': '#000000'},
                                    {'theme': 'dark', 'value': '#FFFFFF'},
                                ],
                                'text': 'реклама',
                            },
                            'background': [
                                {'theme': 'light', 'value': '#FAE3AA'},
                                {'theme': 'dark', 'value': '#674718'},
                            ],
                        },
                    },
                    {
                        'id': '2',
                        'type': 'price_category',
                        'payload': {'icon_url': 'asset://price_category'},
                    },
                ],
            },
        },
        {
            'id': 'id_2',
            'name': 'name_2',
            'context': matching.any_string,
            'layout': [
                {
                    'type': 'meta',
                    'layout': [
                        {'id': '3', 'type': 'advertisements'},
                        {'id': '2', 'type': 'price_category'},
                    ],
                },
            ],
            'data': {
                'meta': [
                    {
                        'id': '3',
                        'type': 'advertisements',
                        'payload': {
                            'text': {
                                'color': [
                                    {'theme': 'light', 'value': '#000000'},
                                    {'theme': 'dark', 'value': '#FFFFFF'},
                                ],
                                'text': 'реклама',
                            },
                            'background': [
                                {'theme': 'light', 'value': '#FAE3AA'},
                                {'theme': 'dark', 'value': '#674718'},
                            ],
                        },
                    },
                    {
                        'id': '2',
                        'type': 'price_category',
                        'payload': {'icon_url': 'asset://price_category'},
                    },
                ],
            },
        },
        {
            'id': 'id_3',
            'name': 'name_3',
            'context': matching.any_string,
            'layout': [{'type': 'meta', 'layout': []}],
            'data': {'meta': []},
        },
    ]

    @mockserver.json_handler('/eats-catalog/internal/v1/catalog-for-layout')
    def _catalog(request):
        response = {
            'filters': {},
            'sort': {},
            'timepicker': [],
            'places': [],
            'blocks': [
                {
                    'id': 'advertisements',
                    'type': 'advertisements',
                    'list': [
                        {
                            'meta': {'place_id': 1, 'brand_id': 1},
                            'payload': {
                                'id': 'id_1',
                                'name': 'name_1',
                                'layout': [
                                    {
                                        'type': 'meta',
                                        'layout': [
                                            {
                                                'id': '2',
                                                'type': 'price_category',
                                            },
                                            {
                                                'id': '3',
                                                'type': 'advertisements',
                                            },
                                        ],
                                    },
                                ],
                                'data': {
                                    'meta': [
                                        {
                                            'id': '2',
                                            'type': 'price_category',
                                            'payload': {
                                                'icon_url': (
                                                    'asset://price_category'
                                                ),
                                            },
                                        },
                                        {
                                            'id': '3',
                                            'type': 'advertisements',
                                            'payload': {
                                                'text': {
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
                                                    'text': 'реклама',
                                                },
                                                'background': [
                                                    {
                                                        'theme': 'light',
                                                        'value': '#FAE3AA',
                                                    },
                                                    {
                                                        'theme': 'dark',
                                                        'value': '#674718',
                                                    },
                                                ],
                                            },
                                        },
                                    ],
                                },
                            },
                        },
                        {
                            'meta': {'place_id': 2, 'brand_id': 2},
                            'payload': {
                                'id': 'id_2',
                                'name': 'name_2',
                                'layout': [
                                    {
                                        'type': 'meta',
                                        'layout': [
                                            {
                                                'id': '3',
                                                'type': 'advertisements',
                                            },
                                            {
                                                'id': '2',
                                                'type': 'price_category',
                                            },
                                        ],
                                    },
                                ],
                                'data': {
                                    'meta': [
                                        {
                                            'id': '3',
                                            'type': 'advertisements',
                                            'payload': {
                                                'text': {
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
                                                    'text': 'реклама',
                                                },
                                                'background': [
                                                    {
                                                        'theme': 'light',
                                                        'value': '#FAE3AA',
                                                    },
                                                    {
                                                        'theme': 'dark',
                                                        'value': '#674718',
                                                    },
                                                ],
                                            },
                                        },
                                        {
                                            'id': '2',
                                            'type': 'price_category',
                                            'payload': {
                                                'icon_url': (
                                                    'asset://price_category'
                                                ),
                                            },
                                        },
                                    ],
                                },
                            },
                        },
                        {
                            'meta': {'place_id': 3, 'brand_id': 3},
                            'payload': {
                                'id': 'id_3',
                                'name': 'name_3',
                                'layout': [],
                                'data': {'meta': []},
                            },
                        },
                    ],
                },
            ],
        }
        return response

    response = await taxi_eats_layout_constructor.post(
        'eats/v1/layout-constructor/v1/layout',
        headers={
            'x-device-id': 'test_device_id',
            'x-platform': 'ios_app',
            'x-app-version': '10.0.0',
            'cookie': '{}',
            'X-Eats-User': 'user_id=12345',
            'x-request-application': 'application=1.1.0',
            'x-request-language': 'enUS',
            'Content-Type': 'application/json',
        },
        json={'location': {'latitude': 55.750028, 'longitude': 37.534397}},
    )

    assert response.status_code == 200
    assert _catalog.times_called == 1

    places_lists = response.json()['data']['places_carousels']
    assert len(places_lists) == 1

    places = places_lists[0]['payload']['places']
    assert len(places) == 3

    assert expected_places == places
