# pylint: disable=C0302
import pytest

from testsuite.utils import matching

from . import configs
from . import experiments
from . import utils

NO_SQL = pytest.mark.pgsql(
    'eats_layout_constructor', files=[], directories=[], queries=[],
)

CATALOG_LAYOUT = pytest.mark.layout(
    slug='with_catalog_request',
    widgets=[
        utils.Widget(
            name='open',
            type='places_collection',
            meta={'place_filter_type': 'open', 'output_type': 'list'},
        ),
    ],
)


def get_places(
        count, with_context: bool = False, with_context_string: bool = False,
):
    places = []
    for i in range(count):
        place: dict = {
            'meta': {'place_id': i, 'brand_id': i},
            'payload': {'id': f'id_{i}', 'name': f'name{i}'},
        }
        if with_context:
            place['payload']['context'] = {}
        if with_context_string:
            place['payload']['context'] = matching.any_string

        places.append(place)

    return places


def get_places_list_widget(
        all_places, widget_id, widget_template_name, slice_from, slice_to=0,
):
    if len(all_places) < slice_from:
        return {}
    if slice_to == 0 or slice_to > len(all_places):
        slice_to = len(all_places)
    return {
        'id': widget_id,
        'template_name': widget_template_name,
        'payload': {
            'places': [
                place['payload'] for place in all_places[slice_from:slice_to]
            ],
        },
    }


@pytest.mark.now('2020-10-02T11:50:00+0300')
@pytest.mark.experiments3(filename='eats_layout_advertisements_carousel.json')
@pytest.mark.parametrize(
    'place_count,layout',
    [
        (
            3,
            {
                'layout': [
                    {
                        'id': '10_places_carousel',
                        'payload': {'title': 'Реклама'},
                        'type': 'places_carousel',
                    },
                ],
                'data': {
                    'places_carousels': [
                        {
                            'id': '10_places_carousel',
                            'template_name': 'Widget template 3',
                            'payload': {
                                'places': [
                                    {
                                        'id': 'id_0',
                                        'name': 'name0',
                                        'context': matching.any_string,
                                    },
                                    {
                                        'id': 'id_1',
                                        'name': 'name1',
                                        'context': matching.any_string,
                                    },
                                    {
                                        'id': 'id_2',
                                        'name': 'name2',
                                        'context': matching.any_string,
                                    },
                                ],
                            },
                        },
                    ],
                },
            },
        ),
    ],
)
@pytest.mark.config(
    EATS_LAYOUT_CONSTRUCTOR_EXPERIMENT_SETTINGS={
        'check_experiment': True,
        'refresh_period_ms': 1000,
        'experiment_name': 'eats_layout_advertisements',
    },
)
async def test_layout_advertisements_carousel(
        taxi_eats_layout_constructor, mockserver, place_count, layout,
):
    @mockserver.json_handler('/eats-catalog/internal/v1/catalog-for-layout')
    def catalog(request):
        assert request.json == {
            'location': {'latitude': 55.750028, 'longitude': 37.534397},
            'blocks': [
                {
                    'id': 'advertisements',
                    'type': 'advertisements',
                    'round_eta_to_hours': False,
                    'disable_filters': False,
                },
            ],
        }

        response = {
            'filters': {},
            'sort': {},
            'timepicker': [],
            'blocks': [
                {
                    'id': 'advertisements',
                    'type': 'advertisements',
                    'list': get_places(place_count),
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
    assert catalog.times_called == 1
    assert response.json() == layout


@pytest.mark.config(
    EATS_LAYOUT_CONSTRUCTOR_EXPERIMENT_SETTINGS={
        'check_experiment': True,
        'refresh_period_ms': 1000,
        'experiment_name': 'eats_layout_pickup',
    },
)
@pytest.mark.experiments3(
    name='eats_layout_pickup',
    consumers=['layout-constructor/layout'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Always true',
            'predicate': {'type': 'true'},
            'value': {'layout_slug': 'with_pickup_carousel'},
        },
    ],
)
@pytest.mark.parametrize(
    'place_count,layout',
    [
        (
            3,
            {
                'layout': [
                    {
                        'id': '11_places_carousel',
                        'payload': {'title': 'Самовывоз'},
                        'type': 'places_carousel',
                    },
                ],
                'data': {
                    'places_carousels': [
                        {
                            'id': '11_places_carousel',
                            'template_name': 'Widget template 4',
                            'payload': {
                                'places': [
                                    {
                                        'id': 'id_0',
                                        'name': 'name0',
                                        'context': matching.any_string,
                                    },
                                    {
                                        'id': 'id_1',
                                        'name': 'name1',
                                        'context': matching.any_string,
                                    },
                                    {
                                        'id': 'id_2',
                                        'name': 'name2',
                                        'context': matching.any_string,
                                    },
                                ],
                            },
                        },
                    ],
                },
            },
        ),
    ],
)
async def test_layout_pickup_carousel(
        taxi_eats_layout_constructor, mockserver, place_count, layout,
):
    """EDACAT-22: проверят корректность работы карусели самовывоза"""

    @mockserver.json_handler('/eats-catalog/internal/v1/catalog-for-layout')
    def catalog(request):
        assert request.json == {
            'location': {'latitude': 55.750028, 'longitude': 37.534397},
            'blocks': [
                {
                    'id': 'pickup',
                    'type': 'pickup',
                    'disable_filters': False,
                    'round_eta_to_hours': False,
                },
            ],
        }

        response = {
            'filters': {},
            'sort': {},
            'timepicker': [],
            'blocks': [
                {
                    'id': 'pickup',
                    'type': 'pickup',
                    'list': get_places(place_count),
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
    assert catalog.times_called == 1
    assert response.json() == layout


@pytest.mark.parametrize(
    'platform,expected,code', [('ios_app', {'data': {}, 'layout': []}, 200)],
)
@pytest.mark.config(
    EATS_LAYOUT_CONSTRUCTOR_EXPERIMENT_SETTINGS={
        'check_experiment': True,
        'refresh_period_ms': 1000,
        'experiment_name': 'eats_layout_template',
    },
)
@NO_SQL
@configs.layout_experiment_name()
@experiments.layout('with_catalog_request')
@CATALOG_LAYOUT
async def test_catalog_not_available(
        taxi_eats_layout_constructor, mockserver, platform, expected, code,
):
    @mockserver.handler('/eats-catalog/internal/v1/catalog-for-layout')
    def catalog(request):
        return mockserver.make_response('{}', status=500)

    response = await taxi_eats_layout_constructor.post(
        'eats/v1/layout-constructor/v1/layout',
        headers={
            'x-device-id': 'dev_id',
            'x-platform': platform,
            'x-app-version': '12.11.12',
            'cookie': '{}',
            'X-Eats-User': 'user_id=12345',
            'x-request-application': 'application=1.1.0',
            'x-request-language': 'enUS',
            'Content-Type': 'application/json',
        },
        json={'location': {'latitude': 0.0, 'longitude': 0.0}},
    )

    assert response.status_code == code
    assert response.json() == expected
    assert catalog.times_called == 1


@pytest.mark.parametrize(
    'layout_request,catalog_request',
    [
        (
            {
                'location': {'latitude': 0.0, 'longitude': 0.0},
                'filter': 'some_slug',
            },
            {
                'blocks': [
                    {
                        'id': 'open',
                        'type': 'open',
                        'disable_filters': False,
                        'round_eta_to_hours': False,
                    },
                ],
                'quick_filter_slug': 'some_slug',
                'location': {'latitude': 0.0, 'longitude': 0.0},
            },
        ),
        (
            {
                'location': {'latitude': 0.0, 'longitude': 0.0},
                'filters': [{'type': 'test_type', 'slug': 'some_slug'}],
            },
            {
                'blocks': [
                    {
                        'id': 'open',
                        'type': 'open',
                        'disable_filters': False,
                        'round_eta_to_hours': False,
                    },
                ],
                'filters': [{'type': 'test_type', 'slug': 'some_slug'}],
                'location': {'latitude': 0.0, 'longitude': 0.0},
            },
        ),
    ],
)
@NO_SQL
@configs.layout_experiment_name()
@experiments.layout('with_catalog_request')
@CATALOG_LAYOUT
async def test_catalog_filters_param(
        taxi_eats_layout_constructor,
        mockserver,
        layout_request,
        catalog_request,
):
    @mockserver.handler('/eats-catalog/internal/v1/catalog-for-layout')
    def catalog(request):
        assert request.json == catalog_request
        return mockserver.make_response('{}', status=500)

    response = await taxi_eats_layout_constructor.post(
        'eats/v1/layout-constructor/v1/layout',
        headers={
            'x-device-id': 'dev_id',
            'x-platform': 'ios_app',
            'x-app-version': '12.11.12',
            'cookie': '{}',
            'X-Eats-User': 'user_id=12345',
            'x-request-application': 'application=1.1.1',
            'x-request-language': 'enUS',
            'Content-Type': 'application/json',
        },
        json=layout_request,
    )

    assert response.status_code == 200
    assert catalog.times_called == 1


@pytest.mark.config(
    EATS_LAYOUT_CONSTRUCTOR_EXPERIMENT_SETTINGS={
        'check_experiment': True,
        'refresh_period_ms': 1000,
        'experiment_name': 'eats_layout_template',
    },
    EATS_LAYOUT_CONSTRUCTOR_ANALYTICS_LOGS_SETTINGS={
        'logging_enabled': True,
        'sampling': 100,
    },
)
@NO_SQL
@configs.layout_experiment_name()
@experiments.layout('with_catalog_request')
@CATALOG_LAYOUT
async def test_catalog_request_id(
        taxi_eats_layout_constructor, mockserver, testpoint,
):
    request_id = None

    @mockserver.handler('/eats-catalog/internal/v1/catalog-for-layout')
    def catalog(request):
        nonlocal request_id
        request_id = request.headers['x-request-id'].strip(' \n')
        assert request_id, 'missing request_id in catalog request'
        return mockserver.make_response('{}', status=200)

    @testpoint('LayoutComponent::LogLayout')
    def log_testpoint(data):
        assert data['request_id'], 'missing request id'
        assert data['request_id'] == request_id

    response = await taxi_eats_layout_constructor.post(
        'eats/v1/layout-constructor/v1/layout',
        headers={
            'x-device-id': 'dev_id',
            'x-platform': 'ios_app',
            'x-app-version': '12.11.12',
            'cookie': '{}',
            'X-Eats-User': 'user_id=12345',
            'x-request-application': 'application=1.1.1',
            'x-request-language': 'enUS',
            'Content-Type': 'application/json',
        },
        json={'location': {'latitude': 0.0, 'longitude': 0.0}},
    )

    assert response.status_code == 200
    assert request_id == response.headers['x-request-id']
    assert log_testpoint.times_called == 1
    assert catalog.times_called == 1


@pytest.mark.config(
    EATS_LAYOUT_CONSTRUCTOR_ANALYTICS_LOGS_SETTINGS={
        'logging_enabled': True,
        'sampling': 100,
    },
)
@NO_SQL
@configs.layout_experiment_name()
@experiments.layout('with_catalog_request')
@CATALOG_LAYOUT
async def test_catalog_request_id_from_request(
        taxi_eats_layout_constructor, mockserver, testpoint,
):
    request_id = 'test-id'

    @mockserver.handler('/eats-catalog/internal/v1/catalog-for-layout')
    def catalog(request):
        assert request.headers['x-request-id'].strip(' \n') == request_id
        return mockserver.make_response('{}', status=200)

    @testpoint('LayoutComponent::LogLayout')
    def log_testpoint(data):
        assert data['request_id'] == request_id

    response = await taxi_eats_layout_constructor.post(
        'eats/v1/layout-constructor/v1/layout',
        headers={
            'x-device-id': 'dev_id',
            'x-platform': 'ios_app',
            'x-app-version': '12.11.12',
            'cookie': '{}',
            'X-Eats-User': 'user_id=12345',
            'x-request-application': 'application=1.1.1',
            'x-request-language': 'enUS',
            'Content-Type': 'application/json',
            'x-request-id': request_id,
        },
        json={'location': {'latitude': 0.0, 'longitude': 0.0}},
    )

    assert response.status_code == 200
    assert request_id == response.headers['x-request-id']
    assert log_testpoint.times_called == 1
    assert catalog.times_called == 1


@NO_SQL
@configs.layout_experiment_name()
@experiments.layout('with_catalog_request')
@CATALOG_LAYOUT
@pytest.mark.parametrize(
    'headers',
    [
        pytest.param({}, id='No advert headers'),
        pytest.param(
            {'x-mobile-ifa': 'test-mobile-ifa'}, id='Only mobile-ifa',
        ),
        pytest.param(
            {
                'x-mobile-ifa': 'test-mobile-ifa',
                'x-appmetrica-uuid': 'test-appmetrica-uuid',
            },
            id='MobileIFA and AppMetrica UUID',
        ),
        pytest.param(
            {
                'x-mobile-ifa': 'test-mobile-ifa',
                'x-appmetrica-uuid': 'test-appmetrica-uuid',
                'X-Forwarded-For': 'localhost/testsuite',
                'X-Real-Ip': '117.224.3.10',
            },
            id='All advert headers',
        ),
        pytest.param({'User-Agent': 'ios(5.4.0)'}, id='User-Agent header'),
    ],
)
async def test_catalog_has_advert_headers(
        taxi_eats_layout_constructor, mockserver, headers,
):
    def assert_headers(headers: dict, request_headers: dict):
        for k in headers:
            assert headers[k] == request_headers[k]

    @mockserver.json_handler('/eats-catalog/internal/v1/catalog-for-layout')
    def catalog(request):
        assert_headers(headers, request.headers)
        return {}

    req_headers = {
        'x-device-id': 'dev_id',
        'x-platform': 'ios_app',
        'x-app-version': '12.11.12',
        'cookie': '{}',
        'X-Eats-User': 'user_id=12345',
        'x-request-application': 'application=1.1.1',
        'x-request-language': 'enUS',
        'Content-Type': 'application/json',
        'x-request-id': '1',
    }

    for k in headers:
        req_headers[k] = headers[k]

    response = await taxi_eats_layout_constructor.post(
        'eats/v1/layout-constructor/v1/layout',
        headers=req_headers,
        json={'location': {'latitude': 0.0, 'longitude': 0.0}},
    )

    assert response.status_code == 200
    assert catalog.times_called == 1


@configs.layout_experiment_name('eats_layout_template')
@experiments.layout('source_required', 'eats_layout_template')
async def test_catalog_source_empty_sort(
        taxi_eats_layout_constructor, mockserver,
):
    """
    EDACAT-854: тест проверяет, что пустая стратегия сортировки не будет
    отправлена в каталог.
    """

    @mockserver.json_handler('/eats-catalog/internal/v1/catalog-for-layout')
    def eats_catalog(request):
        assert (
            'sort' not in request.json
        ), 'eats-layout-constructor expected to ignore empty sort param'
        return {'filters': {}, 'sort': {}, 'timepicker': [], 'blocks': []}

    response = await taxi_eats_layout_constructor.post(
        'eats/v1/layout-constructor/v1/layout',
        headers={
            'x-device-id': 'test_device_id',
            'x-platform': 'ios_app',
            'x-app-version': '10.0.0',
            'cookie': '{}',
            'X-Eats-User': 'user_id=12345',
            'X-Eats-Session': 'blabla',
            'x-request-application': 'application=1.1.0',
            'x-request-language': 'enUS',
            'Content-Type': 'application/json',
        },
        json={
            'location': {'latitude': 55.750028, 'longitude': 37.534397},
            'sort': '',
        },
    )

    assert response.status_code == 200
    assert eats_catalog.times_called == 1


@pytest.mark.parametrize(
    'places_count,expected_layout,expected_widgets',
    [
        (
            1,
            [
                {
                    'id': '12_places_list',
                    'payload': {'title': 'Реклама'},
                    'type': 'places_list',
                },
            ],
            [('12_places_list', 'Widget template 5', 0, 1)],
        ),
        (
            2,
            [
                {
                    'id': '12_places_list',
                    'payload': {'title': 'Реклама'},
                    'type': 'places_list',
                },
                {
                    'id': '13_places_list',
                    'payload': {'title': 'Реклама'},
                    'type': 'places_list',
                },
            ],
            [
                ('12_places_list', 'Widget template 5', 0, 1),
                ('13_places_list', 'Widget template 5', 1, 2),
            ],
        ),
    ],
)
@configs.layout_experiment_name('eats_layout_template')
@experiments.layout('with_place_list_ads', 'eats_layout_template')
async def test_layout_places_list_with_ads(
        taxi_eats_layout_constructor,
        mockserver,
        places_count,
        expected_layout,
        expected_widgets,
):

    filter_type = 'advertisements'
    block_id = 'advertisements'
    all_places = [
        {
            'id': block_id,
            'type': filter_type,
            'round_eta_to_hours': False,
            'list': get_places(places_count),
        },
    ]

    @mockserver.json_handler('/eats-catalog/internal/v1/catalog-for-layout')
    def catalog(request):
        blocks_expected_data = [
            {
                'id': block_id,
                'type': filter_type,
                'disable_filters': False,
                'round_eta_to_hours': False,
            },
        ]
        assert request.json['blocks'] == blocks_expected_data

        return {
            'blocks': all_places,
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
            'Content-Type': 'application/json',
        },
        json={'location': {'latitude': 0.0, 'longitude': 0.0}},
    )

    assert response.status_code == 200
    assert catalog.times_called == 1

    response_json = response.json()
    expected_response = {'places_lists': []}
    for widget in expected_widgets:
        expected_response['places_lists'].append(
            get_places_list_widget(
                get_places(places_count, False, True), *widget,
            ),
        )
    assert response_json == {
        'layout': expected_layout,
        'data': expected_response,
    }


@configs.layout_experiment_name('eats_layout_template')
@experiments.layout('delivery_time_and_delivery_type', 'eats_layout_template')
async def test_request_delivery_time_and_delivery_type(
        taxi_eats_layout_constructor, mockserver,
):
    """
    Тест проверяет, что ограничение на время доставки и тип доставки
    корректно транфсормируются в блоки и отправляюится в каталог.
    """

    @mockserver.json_handler('/eats-catalog/internal/v1/catalog-for-layout')
    def eats_catalog(request):
        expected_condition = {
            'type': 'all_of',
            'predicates': [
                {
                    'type': 'lte',
                    'init': {
                        'arg_name': 'delivery_time_max',
                        'arg_type': 'int',
                        'value': 30,
                    },
                },
                {
                    'type': 'eq',
                    'init': {
                        'arg_name': 'delivery_type',
                        'arg_type': 'string',
                        'value': 'native',
                    },
                },
            ],
        }

        blocks = request.json['blocks']

        assert len(blocks) == 1
        block = blocks[0]
        assert block['condition'] == expected_condition
        assert block['sort_type'] == 'fast_delivery'

        return {'filters': {}, 'sort': {}, 'timepicker': [], 'blocks': []}

    response = await taxi_eats_layout_constructor.post(
        'eats/v1/layout-constructor/v1/layout',
        headers={
            'x-device-id': 'test_device_id',
            'x-platform': 'ios_app',
            'x-app-version': '10.0.0',
            'cookie': '{}',
            'X-Eats-User': 'user_id=12345',
            'X-Eats-Session': 'blabla',
            'x-request-application': 'application=1.1.0',
            'x-request-language': 'enUS',
            'Content-Type': 'application/json',
        },
        json={'location': {'latitude': 55.750028, 'longitude': 37.534397}},
    )

    assert response.status_code == 200
    assert eats_catalog.times_called == 1


@configs.layout_experiment_name()
@experiments.layout('filter_by_categories')
@pytest.mark.layout(
    slug='filter_by_categories',
    widgets=[
        utils.Widget(
            name='Place categories',
            type='places_collection',
            meta={
                'place_categories': [3, 10],
                'place_filter_type': 'open',
                'output_type': 'list',
            },
            payload={'title': 'Заведения с категорией 3 или 10'},
            payload_schema={},
        ),
    ],
)
@pytest.mark.pgsql(
    # Не загружаем 'pg_eats_layout_constructor.sql'
    'eats_layout_constructor',
    files=[],
    directories=[],
    queries=[],
)
async def test_request_filter_by_categories(
        taxi_eats_layout_constructor,
        mockserver,
        layouts,
        widget_templates,
        layout_widgets,
):
    """
    Тест проверяет, что фильтрация по категориям
    корректно трансформируется в блоки и отправляется в каталог.
    """

    @mockserver.json_handler('/eats-catalog/internal/v1/catalog-for-layout')
    def eats_catalog(request):
        expected_condition = {
            'type': 'intersects',
            'init': {
                'arg_name': 'category_id',
                'set_elem_type': 'int',
                'set': [3, 10],
            },
        }

        blocks = request.json['blocks']

        assert len(blocks) == 1
        block = blocks[0]
        assert block['condition'] == expected_condition

        return {'filters': {}, 'sort': {}, 'timepicker': [], 'blocks': []}

    response = await taxi_eats_layout_constructor.post(
        'eats/v1/layout-constructor/v1/layout',
        headers={
            'x-device-id': 'test_device_id',
            'x-platform': 'ios_app',
            'x-app-version': '10.0.0',
            'cookie': '{}',
            'X-Eats-User': 'user_id=12345',
            'X-Eats-Session': 'blabla',
            'x-request-application': 'application=1.1.0',
            'x-request-language': 'enUS',
            'Content-Type': 'application/json',
        },
        json={'location': {'latitude': 55.750028, 'longitude': 37.534397}},
    )

    assert response.status_code == 200
    assert eats_catalog.times_called == 1


@configs.layout_experiment_name('eats_layout_template')
@experiments.layout('place_menu_category_layout', 'eats_layout_template')
async def test_request_place_menu_category(
        taxi_eats_layout_constructor, mockserver,
):
    """
    Проверяем, что параметры для блока типа
    place-menu-category передаются в запросе в каталог
    """

    @mockserver.json_handler('/eats-catalog/internal/v1/catalog-for-layout')
    def eats_catalog(request):

        blocks = request.json['blocks']

        assert len(blocks) == 1
        block = blocks[0]
        assert block['type'] == 'place-menu-category'
        assert block['place_menu_category_tag'] == 'my_category_tag'

        return {'filters': {}, 'sort': {}, 'timepicker': [], 'blocks': []}

    response = await taxi_eats_layout_constructor.post(
        'eats/v1/layout-constructor/v1/layout',
        headers={
            'x-device-id': 'test_device_id',
            'x-platform': 'ios_app',
            'x-app-version': '10.0.0',
            'cookie': '{}',
            'X-Eats-User': 'user_id=12345',
            'X-Eats-Session': 'blabla',
            'x-request-application': 'application=1.1.0',
            'x-request-language': 'enUS',
            'Content-Type': 'application/json',
        },
        json={'location': {'latitude': 55.750028, 'longitude': 37.534397}},
    )

    assert response.status_code == 200
    assert eats_catalog.times_called == 1


@configs.layout_experiment_name('eats_layout_template')
@experiments.layout('layout_advert', 'eats_layout_template')
@pytest.mark.pgsql(
    'eats_layout_constructor', files=[], directories=[], queries=[],
)
@pytest.mark.parametrize(
    'advert_settings',
    [
        pytest.param(None, id='no block advert settings'),
        pytest.param(
            {'ads_only': True, 'indexes': []}, id='ads only settings',
        ),
        pytest.param(
            {'ads_only': False, 'indexes': [1, 2, 3]}, id='indexes settings',
        ),
    ],
)
async def test_block_advert_settings(
        taxi_eats_layout_constructor,
        mockserver,
        layouts,
        widget_templates,
        layout_widgets,
        advert_settings,
):
    """
    EDACAT-1300: тест проверяет, что при наличии рекламных настроек блока, они
    передаются в каталог.
    """

    layout = utils.Layout(
        layout_id=1, name='layout with adverts', slug='layout_advert',
    )
    layouts.add_layout(layout)

    widget_template = utils.WidgetTemplate(
        widget_template_id=1,
        type='places_collection',
        name='places list',
        meta={'place_filter_type': 'open', 'output_type': 'list'},
        payload={},
        payload_schema={},
    )
    widget_templates.add_widget_template(widget_template)

    layout_widget = utils.LayoutWidget(
        name='places list widget',
        widget_template_id=widget_template.widget_template_id,
        layout_id=layout.layout_id,
        meta={},
        payload={},
    )
    if advert_settings:
        layout_widget.meta['advert_settings'] = advert_settings

    layout_widgets.add_layout_widget(layout_widget)

    @mockserver.json_handler('/eats-catalog/internal/v1/catalog-for-layout')
    def eats_catalog(request):
        blocks = request.json['blocks']

        assert len(blocks) == 1
        block = blocks[0]

        assert block['type'] == 'open'
        if not advert_settings:
            assert 'advert_settings' not in block
        else:
            assert 'advert_settings' in block
            assert block['advert_settings'] == advert_settings

        return {'filters': {}, 'sort': {}, 'timepicker': [], 'blocks': []}

    response = await taxi_eats_layout_constructor.post(
        'eats/v1/layout-constructor/v1/layout',
        headers={
            'x-device-id': 'test_device_id',
            'x-platform': 'ios_app',
            'x-app-version': '10.0.0',
            'cookie': '{}',
            'X-Eats-User': 'user_id=12345',
            'X-Eats-Session': 'blabla',
            'x-request-application': 'application=1.1.0',
            'x-request-language': 'enUS',
            'Content-Type': 'application/json',
        },
        json={'location': {'latitude': 55.750028, 'longitude': 37.534397}},
    )

    assert response.status_code == 200
    assert eats_catalog.times_called == 1


@configs.layout_experiment_name('eats_layout_template')
@experiments.layout('layout', 'eats_layout_template')
@pytest.mark.pgsql(
    'eats_layout_constructor', files=[], directories=[], queries=[],
)
async def test_block_places_context(
        taxi_eats_layout_constructor,
        mockserver,
        layouts,
        widget_templates,
        layout_widgets,
):
    """
    EDACAT-1594: проверяет, что контекст ресторана обновляется типом и
    идентификатором виджета.
    """

    # setup
    # layout
    layout = utils.Layout(layout_id=1, name='default layout', slug='layout')
    layouts.add_layout(layout)

    # widget templates
    list_widget_template = utils.WidgetTemplate(
        widget_template_id=1,
        type='places_list',
        name='list',
        meta={'place_filter_type': 'open'},
        payload={},
        payload_schema={},
    )
    widget_templates.add_widget_template(list_widget_template)

    carousel_widget_template = utils.WidgetTemplate(
        widget_template_id=2,
        type='places_carousel',
        name='carousel',
        meta={'carousel': 'open'},
        payload={},
        payload_schema={},
    )
    widget_templates.add_widget_template(carousel_widget_template)

    collection_list_widget_template = utils.WidgetTemplate(
        widget_template_id=3,
        type='places_collection',
        name='collection_list',
        meta={'place_filter_type': 'open', 'output_type': 'list'},
        payload={},
        payload_schema={},
    )
    widget_templates.add_widget_template(collection_list_widget_template)

    collection_car_widget_template = utils.WidgetTemplate(
        widget_template_id=4,
        type='places_collection',
        name='collection_carousel',
        meta={'place_filter_type': 'open', 'output_type': 'carousel'},
        payload={},
        payload_schema={},
    )
    widget_templates.add_widget_template(collection_car_widget_template)

    # layout widgets
    list_widget = utils.LayoutWidget(
        name=list_widget_template.name,
        widget_template_id=list_widget_template.widget_template_id,
        layout_id=layout.layout_id,
        meta={},
        payload={},
    )
    layout_widgets.add_layout_widget(list_widget)

    carousel_widget = utils.LayoutWidget(
        name=carousel_widget_template.name,
        widget_template_id=carousel_widget_template.widget_template_id,
        layout_id=layout.layout_id,
        meta={},
        payload={},
    )
    layout_widgets.add_layout_widget(carousel_widget)

    collection_list_widget = utils.LayoutWidget(
        name=collection_list_widget_template.name,
        widget_template_id=collection_list_widget_template.widget_template_id,
        layout_id=layout.layout_id,
        meta={},
        payload={},
    )
    layout_widgets.add_layout_widget(collection_list_widget)

    collection_carousel_widget = utils.LayoutWidget(
        name=collection_car_widget_template.name,
        widget_template_id=collection_car_widget_template.widget_template_id,
        layout_id=layout.layout_id,
        meta={},
        payload={},
    )
    layout_widgets.add_layout_widget(collection_carousel_widget)

    # setup end

    places_count: int = 5

    @mockserver.json_handler('/eats-catalog/internal/v1/catalog-for-layout')
    def eats_catalog(request):
        blocks = request.json['blocks']

        assert len(blocks) == 1
        return {
            'filters': {},
            'sort': {},
            'timepicker': [],
            'blocks': [
                {
                    'id': blocks[0]['id'],
                    'type': 'open',
                    'list': get_places(places_count, with_context=True),
                },
            ],
        }

    response = await taxi_eats_layout_constructor.post(
        'eats/v1/layout-constructor/v1/layout',
        headers={
            'x-device-id': 'test_device_id',
            'x-platform': 'ios_app',
            'x-app-version': '10.0.0',
            'cookie': '{}',
            'X-Eats-User': 'user_id=12345',
            'X-Eats-Session': 'blabla',
            'x-request-application': 'application=1.1.0',
            'x-request-language': 'enUS',
            'Content-Type': 'application/json',
        },
        json={'location': {'latitude': 55.750028, 'longitude': 37.534397}},
    )

    assert response.status_code == 200
    assert eats_catalog.times_called == 1

    response_widgets = response.json()['layout']
    assert len(response_widgets) == 4, response.json()['layout']

    response_data = response.json()['data']
    places_lists = response_data['places_lists']
    places_carousels = response_data['places_carousels']

    for widget in response_widgets:
        widget_id: str = widget['id']
        widget_type: str = widget['type']

        payload: dict = {}
        if widget_type == 'places_list':
            payload = utils.find_widget_payload(widget_id, places_lists)
        elif widget_type == 'places_carousel':
            payload = utils.find_widget_payload(widget_id, places_carousels)
        else:
            assert False, 'unexpected widget type={}'.format(widget_type)

        places: list = payload['places']
        assert len(places) == places_count
        for place in places:
            assert 'context' in place


@configs.layout_experiment_name('eats_layout_template')
@experiments.layout('layout', 'eats_layout_template')
@pytest.mark.pgsql(
    'eats_layout_constructor', files=[], directories=[], queries=[],
)
async def test_block_places_context_encoded(
        taxi_eats_layout_constructor,
        mockserver,
        layouts,
        widget_templates,
        layout_widgets,
):
    # setup
    layout = utils.Layout(layout_id=1, name='default layout', slug='layout')
    layouts.add_layout(layout)

    collection_list_widget_template = utils.WidgetTemplate(
        widget_template_id=3,
        type='places_collection',
        name='collection_list',
        meta={'place_filter_type': 'open', 'output_type': 'list'},
        payload={},
        payload_schema={},
    )
    widget_templates.add_widget_template(collection_list_widget_template)

    collection_list_widget = utils.LayoutWidget(
        name=collection_list_widget_template.name,
        widget_template_id=collection_list_widget_template.widget_template_id,
        layout_id=layout.layout_id,
        meta={},
        payload={},
    )
    layout_widgets.add_layout_widget(collection_list_widget)
    # setup end

    places_count: int = 5

    @mockserver.json_handler('/eats-catalog/internal/v1/catalog-for-layout')
    def eats_catalog(request):
        blocks = request.json['blocks']

        assert len(blocks) == 1
        return {
            'filters': {},
            'sort': {},
            'timepicker': [],
            'blocks': [
                {
                    'id': blocks[0]['id'],
                    'type': 'open',
                    'list': get_places(places_count, with_context=True),
                },
            ],
        }

    response = await taxi_eats_layout_constructor.post(
        'eats/v1/layout-constructor/v1/layout',
        headers={
            'x-device-id': 'test_device_id',
            'x-platform': 'ios_app',
            'x-app-version': '10.0.0',
            'cookie': '{}',
            'X-Eats-User': 'user_id=12345',
            'X-Eats-Session': 'blabla',
            'x-request-application': 'application=1.1.0',
            'x-request-language': 'enUS',
            'Content-Type': 'application/json',
        },
        json={'location': {'latitude': 55.750028, 'longitude': 37.534397}},
    )

    assert response.status_code == 200
    assert eats_catalog.times_called == 1

    response_data = response.json()['data']
    places_lists = response_data['places_lists']

    response_widgets: list = response.json()['layout']
    for widget in response_widgets:
        widget_id: str = widget['id']

        payload: dict = utils.find_widget_payload(widget_id, places_lists)

        places: list = payload['places']
        assert len(places) == places_count
        for place in places:
            assert 'context' in place
