import pytest

from testsuite.utils import matching

from . import configs
from . import experiments
from . import utils


@configs.layout_experiment_name()
@experiments.layout('layout_filter')
@experiments.filter_source_response(brand_ids=[3, 1], place_ids=[3, 4])
@pytest.mark.layout(
    slug='layout_filter',
    widgets=[
        utils.Widget(
            name='carousel_1',
            type='places_collection',
            meta={'output_type': 'carousel', 'place_filter_type': 'new'},
            payload={'title': 'Карусель'},
            payload_schema={},
        ),
        utils.Widget(
            name='list_1',
            type='places_collection',
            meta={'output_type': 'list', 'place_filter_type': 'open'},
            payload={'title': 'Открытые места'},
            payload_schema={},
        ),
        utils.Widget(
            name='list_2',
            type='places_collection',
            meta={'output_type': 'list', 'place_filter_type': 'closed'},
            payload={'title': 'Закрытые места'},
            payload_schema={},
        ),
    ],
)
@pytest.mark.parametrize(
    'layout_request,layout_response',
    [
        pytest.param(
            {'location': {'latitude': 0.0, 'longitude': 0.0}},
            {
                'data': {
                    'places_lists': [
                        {
                            'id': '1_places_collection',
                            'template_name': 'carousel_1_template',
                            'payload': {
                                'places': [
                                    {
                                        'slug': 'someone',
                                        'context': matching.any_string,
                                        'analytics': matching.any_string,
                                        'data': {'actions': [], 'meta': []},
                                        'layout': [
                                            {'type': 'actions', 'layout': []},
                                            {'type': 'meta', 'layout': []},
                                        ],
                                    },
                                ],
                            },
                        },
                        {
                            'id': '2_places_collection',
                            'template_name': 'list_1_template',
                            'payload': {
                                'places': [
                                    {
                                        'slug': 'another_one',
                                        'context': matching.any_string,
                                        'analytics': matching.any_string,
                                        'data': {'actions': [], 'meta': []},
                                        'layout': [
                                            {'type': 'actions', 'layout': []},
                                            {'type': 'meta', 'layout': []},
                                        ],
                                    },
                                ],
                            },
                        },
                        {
                            'id': '3_places_collection',
                            'template_name': 'list_2_template',
                            'payload': {
                                'places': [
                                    {
                                        'slug': 'second',
                                        'context': matching.any_string,
                                        'analytics': matching.any_string,
                                        'data': {'actions': [], 'meta': []},
                                        'layout': [
                                            {'type': 'actions', 'layout': []},
                                            {'type': 'meta', 'layout': []},
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
                        'payload': {'title': 'Карусель'},
                        'type': 'places_list',
                    },
                    {
                        'id': '2_places_collection',
                        'payload': {'title': 'Открытые места'},
                        'type': 'places_list',
                    },
                    {
                        'id': '3_places_collection',
                        'payload': {'title': 'Закрытые места'},
                        'type': 'places_list',
                    },
                ],
            },
        ),
    ],
)
async def test_filter_catalog_response(
        taxi_eats_layout_constructor,
        mockserver,
        layout_request,
        layout_response,
):
    @mockserver.json_handler('/eats-catalog/internal/v1/catalog-for-layout')
    def _catalog(request):
        return {
            'blocks': [
                {
                    'id': 'new',
                    'type': 'new',
                    'list': [
                        {
                            'meta': {'place_id': 4, 'brand_id': 4},
                            'payload': {
                                'slug': 'fourth',
                                'data': {'actions': [], 'meta': []},
                                'layout': [
                                    {'type': 'actions', 'layout': []},
                                    {'type': 'meta', 'layout': []},
                                ],
                            },
                        },
                        {
                            'meta': {'place_id': 5, 'brand_id': 2},
                            'payload': {
                                'slug': 'someone',
                                'data': {'actions': [], 'meta': []},
                                'layout': [
                                    {'type': 'actions', 'layout': []},
                                    {'type': 'meta', 'layout': []},
                                ],
                            },
                        },
                    ],
                },
                {
                    'id': 'open',
                    'type': 'open',
                    'list': [
                        {
                            'meta': {'place_id': 1, 'brand_id': 1},
                            'payload': {
                                'slug': 'first',
                                'data': {'actions': [], 'meta': []},
                                'layout': [
                                    {'type': 'actions', 'layout': []},
                                    {'type': 'meta', 'layout': []},
                                ],
                            },
                        },
                        {
                            'meta': {'place_id': 1, 'brand_id': 5},
                            'payload': {
                                'slug': 'another_one',
                                'data': {'actions': [], 'meta': []},
                                'layout': [
                                    {'type': 'actions', 'layout': []},
                                    {'type': 'meta', 'layout': []},
                                ],
                            },
                        },
                    ],
                },
                {
                    'id': 'closed',
                    'type': 'closed',
                    'list': [
                        {
                            'meta': {'place_id': 2, 'brand_id': 2},
                            'payload': {
                                'slug': 'second',
                                'data': {'actions': [], 'meta': []},
                                'layout': [
                                    {'type': 'actions', 'layout': []},
                                    {'type': 'meta', 'layout': []},
                                ],
                            },
                        },
                        {
                            'meta': {'place_id': 3, 'brand_id': 3},
                            'payload': {
                                'slug': 'second',
                                'data': {'actions': [], 'meta': []},
                                'layout': [
                                    {'type': 'actions', 'layout': []},
                                    {'type': 'meta', 'layout': []},
                                ],
                            },
                        },
                    ],
                },
            ],
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
        json=layout_request,
    )

    assert response.status_code == 200
    response_json = response.json()
    assert response_json == layout_response


@configs.keep_empty_layout()
@configs.layout_experiment_name()
@experiments.layout('layout_2')
@experiments.filter_source_response(
    brand_ids=[3, 4], place_ids=[1, 2], banner_ids=[5, 6],
)
@pytest.mark.parametrize(
    'layout_request,layout_response',
    [
        (
            {'location': {'latitude': 0.0, 'longitude': 0.0}},
            {
                'data': {
                    'banners': [
                        {
                            'id': '1_banners',
                            'template_name': 'widget_1_template',
                            'payload': {
                                'banners': [
                                    {
                                        'data': 4,
                                        'meta': {
                                            'analytics': matching.AnyString(),
                                        },
                                    },
                                    {
                                        'data': 6,
                                        'meta': {
                                            'analytics': matching.AnyString(),
                                        },
                                    },
                                ],
                                'design': {'type': 'shortcut'},
                            },
                        },
                        {
                            'id': '2_banners',
                            'template_name': 'widget_2_template',
                            'payload': {
                                'banners': [
                                    {
                                        'data': 2,
                                        'meta': {
                                            'analytics': matching.AnyString(),
                                        },
                                    },
                                    {
                                        'data': 6,
                                        'meta': {
                                            'analytics': matching.AnyString(),
                                        },
                                    },
                                ],
                                'design': {'type': 'classic'},
                            },
                        },
                    ],
                },
                'layout': [
                    {
                        'id': '1_banners',
                        'payload': {'title': 'Шорткаты'},
                        'type': 'banners',
                    },
                    {
                        'id': '2_banners',
                        'payload': {'title': 'Классик'},
                        'type': 'banners',
                    },
                ],
            },
        ),
    ],
)
@pytest.mark.layout(
    slug='layout_2',
    widgets=[
        utils.Widget(
            name='widget_1',
            type='banners',
            meta={'format': 'shortcut'},
            payload={'title': 'Шорткаты'},
            payload_schema={},
        ),
        utils.Widget(
            name='widget_2',
            type='banners',
            meta={'format': 'classic'},
            payload={'title': 'Классик'},
            payload_schema={},
        ),
    ],
)
async def test_filter_banners_response(
        taxi_eats_layout_constructor,
        mockserver,
        layout_request,
        layout_response,
):
    @mockserver.json_handler(
        '/eats-communications/eats-communications/v1/layout/banners',
    )
    def _banners(request):
        return {
            'payload': {
                'blocks': [],
                'banners': [
                    {
                        'id': 1,
                        'place_id': 1,
                        'kind': 'info',
                        'formats': ['classic', 'shortcut'],
                        'payload': {'data': 1},
                    },
                    {
                        'id': 2,
                        'place_id': 3,
                        'kind': 'info',
                        'formats': ['classic'],
                        'payload': {'data': 2},
                    },
                    {
                        'id': 3,
                        'brand_id': 3,
                        'kind': 'info',
                        'formats': ['classic'],
                        'payload': {'data': 3},
                    },
                    {
                        'id': 4,
                        'brand_id': 5,
                        'kind': 'info',
                        'formats': ['shortcut'],
                        'payload': {'data': 4},
                    },
                    {
                        'id': 5,
                        'kind': 'info',
                        'formats': ['classic'],
                        'payload': {'data': 5},
                    },
                    {
                        'id': 7,
                        'kind': 'info',
                        'formats': ['classic', 'shortcut'],
                        'payload': {'data': 6},
                    },
                ],
                'header_notes': [],
            },
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
        json=layout_request,
    )

    assert response.status_code == 200
    response_json = response.json()
    assert response_json == layout_response
