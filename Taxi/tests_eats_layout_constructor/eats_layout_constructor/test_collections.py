# pylint: disable=C0302
import copy
import typing

import pytest

from testsuite.utils import matching

from . import collections
from . import configs
from . import experiments
from . import utils

ANY_SHIPPING = {
    'predicates': [
        {
            'init': {
                'arg_name': 'shipping_types',
                'arg_type': 'string',
                'value': 'pickup',
            },
            'type': 'contains',
        },
        {
            'init': {
                'arg_name': 'shipping_types',
                'arg_type': 'string',
                'value': 'delivery',
            },
            'type': 'contains',
        },
    ],
    'type': 'any_of',
}


def create_collection_predicate(
        predicate, shipping_type: typing.Optional[str] = None,
):
    if shipping_type is None:
        return {'type': 'all_of', 'predicates': [ANY_SHIPPING, predicate]}

    return {
        'type': 'all_of',
        'predicates': [
            {
                'type': 'contains',
                'init': {
                    'arg_name': 'shipping_types',
                    'arg_type': 'string',
                    'value': shipping_type,
                },
            },
            predicate,
        ],
    }


CATALOG_PLACE = {
    'meta': {'place_id': 1, 'brand_id': 737},
    'payload': {
        'brand': {'slug': 'pita__suvlaki'},
        'layout': [{'layout': [], 'type': 'meta'}],
        'data': {'features': {}, 'meta': []},
    },
}

COLLECTION_EXPERIMENT = {
    'name': 'eats_layout_collection',
    'consumers': ['layout-constructor/layout'],
    'match': {'predicate': {'type': 'true'}, 'enabled': True},
    'clauses': [
        {
            'title': 'Always true',
            'predicate': {'type': 'true'},
            'value': {'layout_slug': 'default_collection_layout'},
        },
    ],
}


def add_review(place):
    place_copy = copy.deepcopy(place)
    place_copy['payload']['context'] = matching.any_string
    place_copy['payload']['analytics'] = matching.any_string
    place_copy['payload']['data']['features'] = {
        'review': {
            'description': (
                'Таверна с традиционным греческим меню и образом жизни.'
            ),
            'informationBlocks': [],
        },
    }
    return place_copy['payload']


def add_ads(place):
    place_copy = copy.deepcopy(place)

    place_copy['layout'] = [
        {'type': 'meta', 'layout': [{'id': '_', 'type': 'advertisements'}]},
    ]
    place_copy['data']['meta'] = [
        {
            'id': '_',
            'type': 'advertisements',
            'payload': {
                'text': {
                    'text': 'реклама',
                    'color': [
                        {'theme': 'light', 'value': '#000000'},
                        {'theme': 'dark', 'value': '#FFFFFF'},
                    ],
                },
                'background': [
                    {'theme': 'light', 'value': '#FAE3AA'},
                    {'theme': 'dark', 'value': '#674718'},
                ],
            },
        },
    ]
    return place_copy


RESULT_PLACE = add_review(CATALOG_PLACE)

RESULT_ADS_PLACE = add_ads(RESULT_PLACE)


def get_result_view_header(collection_slug: str) -> dict:
    return {
        'id': f'view_header_{collection_slug}',
        'template_name': 'view_header',
        'meta': {
            'slug': collection_slug,
            'url': f'https://eda.yandex.ru/collections/{collection_slug}',
        },
        'payload': {
            'title': 'Сочные шашлыки на выходные',
            'description': 'Приготовить хороший шашлык в духовке невозможно.',
        },
    }


async def request_layout_constructor(taxi_eats_layout_constructor, json):
    response = await taxi_eats_layout_constructor.post(
        'eats/v1/layout-constructor/v1/layout',
        headers={
            'x-device-id': 'dev_id',
            'x-platform': 'android_app',
            'x-app-version': '12.11.12',
            'cookie': '{}',
            'X-Eats-User': 'user_id=12345',
            'x-request-application': 'application=1.1.0',
            'x-request-language': 'ru',
            'Content-Type': 'application/json',
        },
        json=json,
    )
    return response


async def get_fallbacks_layout_count(taxi_eats_layout_constructor_monitor):
    metric = await taxi_eats_layout_constructor_monitor.get_metric(
        'layout-component',
    )
    return metric['fallbacks_layout_count']


@pytest.mark.now('2020-05-07T11:30:00+0300')
@pytest.mark.experiments3(filename='eats_layout_collections.json')
@pytest.mark.parametrize(
    'collection_name,layout',
    [
        pytest.param(
            'shahliki_collection_without_layout_slug',
            {
                'layout': [
                    {
                        'id': '1_places_collection',
                        'payload': {'title': 'Default List'},
                        'type': 'places_list',
                    },
                ],
                'data': {
                    'view_header': get_result_view_header(
                        'shahliki_collection_without_layout_slug',
                    ),
                    'places_lists': [
                        {
                            'id': '1_places_collection',
                            'template_name': 'Default List',
                            'payload': {'places': [RESULT_ADS_PLACE]},
                        },
                    ],
                },
            },
            id='default layout',
        ),
        pytest.param(
            'shahliki_collection_with_layout_slug',
            {
                'layout': [
                    {
                        'id': '2_places_collection',
                        'payload': {'title': 'Custom List'},
                        'type': 'places_list',
                    },
                ],
                'data': {
                    'view_header': get_result_view_header(
                        'shahliki_collection_with_layout_slug',
                    ),
                    'places_lists': [
                        {
                            'id': '2_places_collection',
                            'template_name': 'Custom List',
                            'payload': {'places': [RESULT_PLACE]},
                        },
                    ],
                },
            },
            id='custom layout',
        ),
    ],
)
@configs.layout_experiment_name(collection='eats_layout_collection')
async def test_collection(
        taxi_eats_layout_constructor, mockserver, collection_name, layout,
):
    """
    Проверяем, что коллекция рисуется с явно указанным в эксперименте
    layout_slug и с дефолтным.

    Для коллекции 'shahliki_collection_without_layout_slug'
    layout_slug не указан, ожидаем, что возьмется
    default_collection_layout из эксперимента с условием collection not null
    Виджет places_list с Title: Default List

    Для коллекции 'shahliki_collection_with_layout_slug'
    layout_slug: custom_collection_layout
    Виджет places_collection с Title: Custom List
    """

    @mockserver.json_handler('/eats-catalog/internal/v1/catalog-for-layout')
    def _catalog(request):
        request_data = request.json
        block_id = f'open_{collection_name}'
        # 737 from testsute/static/default/eats_layout_collections.json
        expected_custom_type = {
            'id': f'open_{collection_name}',
            'type': 'open',
            'disable_filters': False,
            'round_eta_to_hours': False,
            'condition': create_collection_predicate(
                {
                    'init': {
                        'arg_name': 'brand_id',
                        'set': [737],
                        'set_elem_type': 'int',
                    },
                    'type': 'in_set',
                },
            ),
        }

        assert request_data['blocks'] == [expected_custom_type]

        catalog_response = {
            'filters': {},
            'sort': {},
            'timepicker': [],
            'blocks': [{'id': block_id, 'list': [CATALOG_PLACE]}],
        }
        return catalog_response

    response = await request_layout_constructor(
        taxi_eats_layout_constructor,
        {
            'view': {'type': 'collection', 'slug': collection_name},
            'location': {'latitude': 0.0, 'longitude': 0.0},
        },
    )

    assert response.status_code == 200

    response_json = response.json()
    # убираем id меты с рекламой, чтобы тест не флапал
    try:
        place = response_json['data']['places_lists'][0]['payload']['places'][
            0
        ]
        place['layout'][0]['layout'][0]['id'] = '_'
        place['data']['meta'][0]['id'] = '_'
    except:  # noqa
        pass

    assert response_json == layout


@pytest.mark.experiments3(filename='eats_layout_collections.json')
@pytest.mark.config(
    EATS_LAYOUT_CONSTRUCTOR_FALLBACK_LAYOUT={
        'fallback_enabled': True,
        'layout_slug': 'unknown',
        'collection_layout_slug': 'default_collection_layout',
    },
)
@configs.layout_experiment_name(
    name='invalid_experiment_name', collection='invalid_experiment_name',
)
async def test_collection_layout_fallback(
        taxi_eats_layout_constructor,
        mockserver,
        taxi_eats_layout_constructor_monitor,
):
    """
    Проверяем работу fallback layout.
    Ожидаем, что shahliki_collection_with_layout_slug
    соберется в дефолтном лейауте, несмотря на наличие явного значения
    в эксперименте layout
    """
    collection_slug = 'shahliki_collection_with_layout_slug'
    layout = {
        'layout': [
            {
                'id': '1_places_collection',
                'payload': {'title': 'Default List'},
                'type': 'places_list',
            },
        ],
        'data': {
            'view_header': get_result_view_header(
                'shahliki_collection_with_layout_slug',
            ),
            'places_lists': [
                {
                    'id': '1_places_collection',
                    'template_name': 'Default List',
                    'payload': {'places': [RESULT_PLACE]},
                },
            ],
        },
    }

    @mockserver.json_handler('/eats-catalog/internal/v1/catalog-for-layout')
    def _catalog(request):
        request_data = request.json
        block_id = f'open_{collection_slug}'
        # 737 from testsute/static/default/eats_layout_collections.json
        expected_custom_type = {
            'id': f'open_{collection_slug}',
            'type': 'open',
            'disable_filters': False,
            'round_eta_to_hours': False,
            'condition': create_collection_predicate(
                {
                    'init': {
                        'arg_name': 'brand_id',
                        'set': [737],
                        'set_elem_type': 'int',
                    },
                    'type': 'in_set',
                },
            ),
        }

        assert request_data['blocks'] == [expected_custom_type]

        catalog_response = {
            'filters': {},
            'sort': {},
            'timepicker': [],
            'blocks': [{'id': block_id, 'list': [CATALOG_PLACE]}],
        }
        return catalog_response

    fallbacks_layout_count_old = await get_fallbacks_layout_count(
        taxi_eats_layout_constructor_monitor,
    )

    response = await request_layout_constructor(
        taxi_eats_layout_constructor,
        {
            'view': {'type': 'collection', 'slug': collection_slug},
            'location': {'latitude': 0.0, 'longitude': 0.0},
        },
    )

    fallbacks_layout_count = await get_fallbacks_layout_count(
        taxi_eats_layout_constructor_monitor,
    )
    assert fallbacks_layout_count - fallbacks_layout_count_old == 1

    assert response.status_code == 200
    assert response.json() == layout


@pytest.mark.now('2021-04-05T13:30:00+0300')
@configs.layout_experiment_name(collection='eats_layout_collection')
@pytest.mark.experiments3(**COLLECTION_EXPERIMENT)
@pytest.mark.parametrize(
    'collection_args',
    [
        pytest.param(
            create_collection_predicate(
                {
                    'type': 'in_set',
                    'init': {
                        'arg_name': 'brand_id',
                        'set_elem_type': 'int',
                        'set': [737],
                    },
                },
            ),
            marks=collections.experiment(
                slug='testsuite',
                title='testsuite collection',
                strategy=collections.Strategy.by_brand_id,
                args=collections.BrandArgs(brand_ids=[737]),
            ),
            id='by_brand_id',
        ),
        pytest.param(
            create_collection_predicate(
                {
                    'type': 'in_set',
                    'init': {
                        'arg_name': 'place_id',
                        'set_elem_type': 'int',
                        'set': [123],
                    },
                },
            ),
            marks=collections.experiment(
                slug='testsuite',
                title='testsuite collection',
                strategy=collections.Strategy.by_place_id,
                args=collections.PlaceArgs(place_ids=[123]),
            ),
            id='by_place_id',
        ),
        pytest.param(
            create_collection_predicate(
                {
                    'type': 'in_set',
                    'init': {
                        'arg_name': 'business',
                        'set_elem_type': 'string',
                        'set': utils.MatchingSet(['shop', 'store']),
                    },
                },
            ),
            marks=collections.experiment(
                slug='testsuite',
                title='testsuite collection',
                strategy=collections.Strategy.by_business,
                args=collections.BusinessArgs(businesses=['shop', 'store']),
            ),
            id='by_business with set',
        ),
        pytest.param(
            create_collection_predicate(
                {
                    'type': 'in_set',
                    'init': {
                        'arg_name': 'business',
                        'set_elem_type': 'string',
                        'set': ['shop'],
                    },
                },
            ),
            marks=(
                pytest.mark.experiments3(
                    name='eats_collections_testsuite',
                    consumers=['eats-collections/collections'],
                    match={'predicate': {'type': 'true'}, 'enabled': True},
                    clauses=[
                        {
                            'title': 'Always true',
                            'predicate': {'type': 'true'},
                            'value': {
                                'title': 'testsuite collection',
                                'searchConditions': {
                                    'strategy': 'by_business',
                                    'arguments': {'business': 'shop'},
                                },
                            },
                        },
                    ],
                )
            ),
            id='by_business deprecated',
        ),
        pytest.param(
            create_collection_predicate(
                {
                    'type': 'in_set',
                    'init': {
                        'arg_name': 'business',
                        'set_elem_type': 'string',
                        'set': utils.MatchingSet(['restaurant', 'shop']),
                    },
                },
            ),
            marks=(
                pytest.mark.experiments3(
                    name='eats_collections_testsuite',
                    consumers=['eats-collections/collections'],
                    match={'predicate': {'type': 'true'}, 'enabled': True},
                    clauses=[
                        {
                            'title': 'Always true',
                            'predicate': {'type': 'true'},
                            'value': {
                                'title': 'testsuite collection',
                                'searchConditions': {
                                    'strategy': 'by_business',
                                    'arguments': {
                                        'business': 'shop',
                                        'businesses': ['restaurant'],
                                    },
                                },
                            },
                        },
                    ],
                )
            ),
            id='by_business combined',
        ),
        pytest.param(
            create_collection_predicate(
                {
                    'type': 'in_set',
                    'init': {
                        'arg_name': 'courier_type',
                        'set_elem_type': 'string',
                        'set': utils.MatchingSet(['pedestrian', 'rover']),
                    },
                },
            ),
            marks=(
                pytest.mark.experiments3(
                    name='eats_collections_testsuite',
                    consumers=['eats-collections/collections'],
                    match={'predicate': {'type': 'true'}, 'enabled': True},
                    clauses=[
                        {
                            'title': 'Always true',
                            'predicate': {'type': 'true'},
                            'value': {
                                'title': 'testsuite collection',
                                'searchConditions': {
                                    'strategy': 'by_courier_type',
                                    'arguments': {
                                        'type': 'rover',
                                        'types': ['rover', 'pedestrian'],
                                    },
                                },
                            },
                        },
                    ],
                )
            ),
            id='by courier type combined',
        ),
        pytest.param(
            create_collection_predicate(
                {
                    'type': 'in_set',
                    'init': {
                        'arg_name': 'courier_type',
                        'set_elem_type': 'string',
                        'set': ['rover'],
                    },
                },
            ),
            marks=(
                pytest.mark.experiments3(
                    name='eats_collections_testsuite',
                    consumers=['eats-collections/collections'],
                    match={'predicate': {'type': 'true'}, 'enabled': True},
                    clauses=[
                        {
                            'title': 'Always true',
                            'predicate': {'type': 'true'},
                            'value': {
                                'title': 'testsuite collection',
                                'searchConditions': {
                                    'strategy': 'by_courier_type',
                                    'arguments': {'type': 'rover'},
                                },
                            },
                        },
                    ],
                )
            ),
            id='by courier type single',
        ),
        pytest.param(
            create_collection_predicate(
                {
                    'type': 'in_set',
                    'init': {
                        'arg_name': 'courier_type',
                        'set_elem_type': 'string',
                        'set': utils.MatchingSet(['rover', 'taxi']),
                    },
                },
            ),
            marks=collections.experiment(
                slug='testsuite',
                title='testsuite collection',
                strategy=collections.Strategy.by_courier_type,
                args=collections.CourierArgs(types=['rover', 'rover', 'taxi']),
            ),
            id='by courier type many',
        ),
        pytest.param(
            create_collection_predicate(
                {
                    'type': 'intersects',
                    'init': {
                        'arg_name': 'promo_type',
                        'set_elem_type': 'int',
                        'set': [1],
                    },
                },
            ),
            marks=(
                pytest.mark.experiments3(
                    name='eats_collections_testsuite',
                    consumers=['eats-collections/collections'],
                    match={'predicate': {'type': 'true'}, 'enabled': True},
                    clauses=[
                        {
                            'title': 'Always true',
                            'predicate': {'type': 'true'},
                            'value': {
                                'title': 'testsuite collection',
                                'searchConditions': {
                                    'strategy': 'by_promo_type',
                                    'arguments': {'id': 1},
                                },
                            },
                        },
                    ],
                )
            ),
            id='by promo type single',
        ),
        pytest.param(
            create_collection_predicate(
                {
                    'type': 'intersects',
                    'init': {
                        'arg_name': 'promo_type',
                        'set_elem_type': 'int',
                        'set': utils.MatchingSet([1, 2]),
                    },
                },
            ),
            marks=collections.experiment(
                slug='testsuite',
                title='testsuite collection',
                strategy=collections.Strategy.by_promo_type,
                args=collections.PromoArgs(promo_type_ids=[1, 1, 2]),
            ),
            id='by promo type many',
        ),
        pytest.param(
            create_collection_predicate(
                {
                    'type': 'intersects',
                    'init': {
                        'arg_name': 'promo_type',
                        'set_elem_type': 'int',
                        'set': utils.MatchingSet([1, 2, 3]),
                    },
                },
            ),
            marks=(
                pytest.mark.experiments3(
                    name='eats_collections_testsuite',
                    consumers=['eats-collections/collections'],
                    match={'predicate': {'type': 'true'}, 'enabled': True},
                    clauses=[
                        {
                            'title': 'Always true',
                            'predicate': {'type': 'true'},
                            'value': {
                                'title': 'testsuite collection',
                                'searchConditions': {
                                    'strategy': 'by_promo_type',
                                    'arguments': {
                                        'promo_ids': [1, 1, 2],
                                        'id': 3,
                                    },
                                },
                            },
                        },
                    ],
                )
            ),
            id='by promo type combined',
        ),
    ],
)
async def test_collections_args(
        taxi_eats_layout_constructor, mockserver, collection_args,
):
    """EDACAT-676: тест проверяет, что в каталог отправляются правильно
    сформированные предикаты."""

    @mockserver.json_handler('/eats-catalog/internal/v1/catalog-for-layout')
    def catalog(request):
        blocks: list = [
            {
                'id': 'open_testsuite',
                'type': 'open',
                'disable_filters': False,
                'round_eta_to_hours': False,
                'condition': collection_args,
            },
        ]
        assert request.json['blocks'] == blocks

        return {
            'filters': {},
            'sort': {},
            'timepicker': [],
            'blocks': [{'id': 'open_testsuite', 'list': []}],
        }

    response = await taxi_eats_layout_constructor.post(
        '/eats/v1/layout-constructor/v1/layout',
        headers={
            'x-device-id': 'testsuite',
            'x-platform': 'ios_app',
            'x-app-version': '5.10.0',
            'cookie': '{}',
            'X-Eats-User': 'user_id=12345',
            'content-type': 'application/json',
        },
        json={
            'view': {'type': 'collection', 'slug': 'testsuite'},
            'location': {'latitude': 0.0, 'longitude': 0.0},
        },
    )
    assert response.status_code == 200
    assert catalog.times_called == 1


@pytest.mark.now('2021-04-05T13:30:00+0300')
@configs.layout_experiment_name(collection='eats_layout_collection')
@pytest.mark.experiments3(**COLLECTION_EXPERIMENT)
@pytest.mark.parametrize(
    'collection_args, catalog_filters_v2',
    [
        pytest.param(
            create_collection_predicate(
                {
                    'type': 'in_set',
                    'init': {
                        'arg_name': 'brand_id',
                        'set_elem_type': 'int',
                        'set': [737],
                    },
                },
                'pickup',
            ),
            {
                'groups': [
                    {
                        'filters': [{'slug': 'pickup', 'type': 'pickup'}],
                        'type': 'and',
                    },
                ],
            },
            marks=collections.experiment(
                slug='testsuite',
                title='testsuite collection',
                strategy=collections.Strategy.by_brand_id,
                shipping_type='pickup',
                args=collections.BrandArgs(brand_ids=[737]),
            ),
            id='by_brand_id',
        ),
        pytest.param(
            create_collection_predicate(
                {
                    'type': 'in_set',
                    'init': {
                        'arg_name': 'place_id',
                        'set_elem_type': 'int',
                        'set': [123],
                    },
                },
                'delivery',
            ),
            None,
            marks=collections.experiment(
                slug='testsuite',
                title='testsuite collection',
                strategy=collections.Strategy.by_place_id,
                shipping_type='delivery',
                args=collections.PlaceArgs(place_ids=[123]),
            ),
            id='by_place_id',
        ),
    ],
)
async def test_collections_args_pickup(
        taxi_eats_layout_constructor,
        mockserver,
        collection_args,
        catalog_filters_v2,
):
    """Тест проверяет, что в каталог отправляются правильно
    сформированные предикаты и фильтр самовывоза."""

    @mockserver.json_handler('/eats-catalog/internal/v1/catalog-for-layout')
    def catalog(request):
        blocks: list = [
            {
                'id': 'open_testsuite',
                'type': 'open',
                'disable_filters': False,
                'round_eta_to_hours': False,
                'condition': collection_args,
            },
        ]

        assert request.json['blocks'] == blocks
        if catalog_filters_v2 is not None:
            assert request.json['filters_v2'] == catalog_filters_v2
        else:
            assert request.json.get('filters_v2') is None

        return {
            'filters': {},
            'sort': {},
            'timepicker': [],
            'blocks': [{'id': 'open_testsuite', 'list': []}],
            'filters_v2': {'groups': []},
        }

    response = await taxi_eats_layout_constructor.post(
        '/eats/v1/layout-constructor/v1/layout',
        headers={
            'x-device-id': 'testsuite',
            'x-platform': 'ios_app',
            'x-app-version': '5.10.0',
            'cookie': '{}',
            'X-Eats-User': 'user_id=12345',
            'content-type': 'application/json',
        },
        json={
            'view': {'type': 'collection', 'slug': 'testsuite'},
            'location': {'latitude': 0.0, 'longitude': 0.0},
        },
    )
    assert response.status_code == 200
    assert catalog.times_called == 1


@configs.layout_experiment_name(collection='eats_layout_collection')
@experiments.layout('layout_1', 'eats_layout_collection')
@pytest.mark.pgsql(
    'eats_layout_constructor', files=[], directories=[], queries=[],
)
@pytest.mark.experiments3(
    name='eats_collections_testsuite',
    consumers=['eats-collections/collections'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Always true',
            'predicate': {'type': 'true'},
            'value': {
                'title': 'testsuite collection',
                'searchConditions': {
                    'strategy': 'by_brand_id',
                    'arguments': {'brand_ids': [737]},
                },
            },
        },
    ],
)
async def test_collections_widget_and_collection_params(
        taxi_eats_layout_constructor,
        mockserver,
        layouts,
        widget_templates,
        layout_widgets,
):
    """
    Проверяет, что условия выборки заведений с виджета
    объединяются с условиями коллекции
    """

    layout = utils.Layout(layout_id=1, name='layout', slug='layout_1')
    layouts.add_layout(layout)

    widget_template = utils.WidgetTemplate(
        widget_template_id=1,
        type='places_collection',
        name='places list',
        meta={
            'place_filter_type': 'open',
            'output_type': 'list',
            'exclude_businesses': ['shop'],
        },
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

    layout_widgets.add_layout_widget(layout_widget)

    @mockserver.json_handler('/eats-catalog/internal/v1/catalog-for-layout')
    def catalog(request):
        collection_predicate = create_collection_predicate(
            {
                'type': 'in_set',
                'init': {
                    'arg_name': 'brand_id',
                    'set_elem_type': 'int',
                    'set': [737],
                },
            },
        )

        widget_predicate = {
            'type': 'not',
            'predicates': [
                {
                    'init': {
                        'arg_name': 'business',
                        'set_elem_type': 'string',
                        'set': ['shop'],
                    },
                    'type': 'in_set',
                },
            ],
        }

        blocks: list = [
            {
                'id': 'open_testsuite_no_shop',
                'type': 'open',
                'disable_filters': False,
                'round_eta_to_hours': False,
                'condition': {
                    'type': 'all_of',
                    'predicates': [collection_predicate, widget_predicate],
                },
            },
        ]
        assert request.json['blocks'] == blocks

        return {
            'filters': {},
            'sort': {},
            'timepicker': [],
            'blocks': [{'id': 'open_testsuite_no_shop', 'list': []}],
        }

    response = await taxi_eats_layout_constructor.post(
        '/eats/v1/layout-constructor/v1/layout',
        headers={
            'x-device-id': 'testsuite',
            'x-platform': 'ios_app',
            'x-app-version': '5.10.0',
            'cookie': '{}',
            'X-Eats-User': 'user_id=12345',
            'content-type': 'application/json',
        },
        json={
            'view': {'type': 'collection', 'slug': 'testsuite'},
            'location': {'latitude': 0.0, 'longitude': 0.0},
        },
    )
    assert response.status_code == 200
    assert catalog.times_called == 1


@configs.layout_experiment_name(collection='eats_layout_collection')
@experiments.layout('layout_1', 'eats_layout_collection')
@pytest.mark.pgsql(
    'eats_layout_constructor', files=[], directories=[], queries=[],
)
async def test_not_found_collection(
        taxi_eats_layout_constructor, single_widget_layout,
):
    """
    Проверяем, что для неизвестной коллекции
    возвраащается 404
    """

    widget_template = utils.WidgetTemplate(
        widget_template_id=1,
        type='places_collection',
        name='places list',
        meta={
            'place_filter_type': 'open',
            'output_type': 'list',
            'exclude_businesses': ['shop'],
        },
        payload={},
        payload_schema={},
    )
    single_widget_layout('layout_1', widget_template)

    response = await taxi_eats_layout_constructor.post(
        '/eats/v1/layout-constructor/v1/layout',
        headers={
            'x-device-id': 'testsuite',
            'x-platform': 'ios_app',
            'x-app-version': '5.10.0',
            'cookie': '{}',
            'X-Eats-User': 'user_id=12345',
            'content-type': 'application/json',
        },
        json={
            'view': {'type': 'collection', 'slug': 'invalid_slug'},
            'location': {'latitude': 0.0, 'longitude': 0.0},
        },
    )
    assert response.status_code == 404


@pytest.mark.layout(
    autouse=True,
    slug='ultima_collection',
    widgets=[
        utils.Widget(
            name='open',
            type='ultima_places_list',
            meta={'place_filter_type': 'open'},
            payload={},
            payload_schema={},
        ),
    ],
)
@pytest.mark.pgsql(
    'eats_layout_constructor', files=[], directories=[], queries=[],
)
@collections.experiment(
    slug='ultima',
    title='ULTIMA',
    description='ultima ultima ultima aaaand ultima',
    image=collections.Image(
        light='https://ultima-light.png', dark='https://ultima-dark.png',
    ),
    strategy=collections.Strategy.ultima,
)
@configs.ultima_places(
    {
        'place0': {
            'image': 'http://place_slug_0',
            'carousel_settings': {'items': []},
            'review': {'text': 'Review text', 'subtext': 'Review subtext'},
        },
        'place2': {
            'image': 'http://place_slug_2',
            'carousel_settings': {'items': []},
            'review': {'text': 'Review text'},
        },
    },
)
async def test_ultima_collection(taxi_eats_layout_constructor, mockserver):
    """
    Проверяем, работу коллекции Ультма
    """

    def build_places(places_count, is_available: bool):
        places = []
        for i in range(places_count):
            place_data = {
                'payload': {
                    'name': f'place{i}',
                    'slug': f'place{i}',
                    'availability': {'is_available': is_available},
                    'brand': {
                        'name': f'brand_name_{i}',
                        'slug': f'brand_slug_{i}',
                        'business': 'restaurant',
                    },
                    'data': {
                        'features': {'delivery': {'text': '1000 мин'}},
                        'meta': [],
                    },
                },
                'meta': {
                    'place_id': i,
                    'brand_id': i,
                    'is_ultima': True,
                    'categories': ['пиво', 'Some Штуки', 'Сигареты'],
                },
            }
            places.append(place_data)

        return places

    def ultima_collection_block(filter_type: str) -> dict:
        return {
            'condition': {
                'predicates': [
                    {'init': {'arg_name': 'is_ultima'}, 'type': 'bool'},
                    # NOTE(nk2ge5k): тут получается 2 раза одно условие
                    # потому что я не знаю как их дедуплицировать:
                    # одно приходит из виджета, другое из коллекции.
                    create_collection_predicate(
                        {'init': {'arg_name': 'is_ultima'}, 'type': 'bool'},
                    ),
                ],
                'type': 'all_of',
            },
            'disable_filters': False,
            'id': f'ultima_{filter_type}_ultima',
            'round_eta_to_hours': False,
            'type': filter_type,
        }

    def response_place(subtext: str, index: int, is_available: bool):
        return {
            'analytics': matching.any_string,
            'availability': {'is_available': is_available},
            'brand': {
                'business': 'restaurant',
                'name': f'brand_name_{index}',
                'slug': f'brand_slug_{index}',
            },
            'data': {
                'features': {
                    'delivery': {
                        'background_color': {
                            'dark': '#DEBACK',
                            'light': '#DEBACK',
                        },
                        'text': {
                            'color': {'dark': '#DETEXT', 'light': '#DETEXT'},
                            'value': '1000 МИН',
                        },
                    },
                    'ultimatum': {
                        'subtext': {
                            'color': {'dark': '#RSUBTE', 'light': '#RSUBTE'},
                            'value': subtext,
                        },
                        'text': {
                            'color': {'dark': '#RETEXT', 'light': '#RETEXT'},
                            'value': 'Review text',
                        },
                    },
                },
            },
            'media': {'image': f'http://place_slug_{index}'},
            'name': {
                'color': {'dark': '#TTITLE', 'light': '#TTITLE'},
                'value': f'PLACE{index}',
            },
            'slug': f'place{index}',
        }

    @mockserver.json_handler('/eats-catalog/internal/v1/catalog-for-layout')
    def catalog(request):
        blocks = request.json['blocks']
        assert set(['ultima_open_ultima']) == {block['id'] for block in blocks}

        for block in blocks:
            if block['id'] == 'ultima_open_ultima':
                assert block == ultima_collection_block('open')

        return {
            'filters': {},
            'sort': {},
            'timepicker': [],
            'blocks': [
                {'id': 'ultima_open_ultima', 'list': build_places(3, True)},
            ],
        }

    response = await taxi_eats_layout_constructor.post(
        '/eats/v1/layout-constructor/v1/layout',
        headers={
            'x-device-id': 'testsuite',
            'x-platform': 'ios_app',
            'x-app-version': '5.10.0',
            'cookie': '{}',
            'X-Eats-User': 'user_id=12345',
            'content-type': 'application/json',
        },
        json={
            'view': {'type': 'collection', 'slug': 'ultima'},
            'location': {'latitude': 0.0, 'longitude': 0.0},
        },
    )

    assert response.status_code == 200
    assert catalog.times_called == 1

    data = response.json()['data']
    assert data == {
        'ultima_places_list': [
            {
                'id': '1_ultima_places_list',
                'payload': {
                    'places': [
                        response_place('Review subtext', 0, True),
                        response_place(
                            'ПИВО \u2022\u00A0SOME ШТУКИ \u2022\u00A0СИГАРЕТЫ',
                            2,
                            True,
                        ),
                    ],
                },
                'template_name': 'open_template',
            },
        ],
        'view_header': {
            'id': 'view_header_ultima',
            'meta': {
                'slug': 'ultima',
                'url': 'https://eda.yandex.ru/collections/ultima',
            },
            'payload': {
                'description': 'ultima ultima ultima aaaand ultima',
                'image': {
                    'dark': 'https://ultima-dark.png',
                    'light': 'https://ultima-light.png',
                },
                'title': 'ULTIMA',
            },
            'template_name': 'view_header',
        },
    }


@pytest.mark.layout(
    autouse=True,
    slug='locale_collection',
    widgets=[
        utils.Widget(
            name='open',
            type='places_collection',
            meta={'place_filter_type': 'open', 'output_type': 'list'},
            payload={},
            payload_schema={},
        ),
    ],
)
@pytest.mark.pgsql(
    'eats_layout_constructor', files=[], directories=[], queries=[],
)
@collections.experiment(
    slug='locale_collection',
    title='Collection with locale',
    description='Must show only if request_locale = en',
    locale='en',
    strategy=collections.Strategy.by_brand_id,
    args=collections.BrandArgs(brand_ids=[737]),
)
@pytest.mark.parametrize(
    'locale',
    (
        pytest.param('ru', id='mismatch_locale'),
        pytest.param('en', id='match_locale'),
    ),
)
async def test_locale_collection(
        taxi_eats_layout_constructor, mockserver, locale,
):
    """
    Проверяем что если запрошенный язык не совпадает
    с локалью коллекции, коллекция не будет
    показана
    """

    def build_places(places_count, is_available: bool):
        places = []
        for i in range(places_count):
            place_data = {
                'payload': {
                    'name': f'place{i}',
                    'slug': f'place{i}',
                    'availability': {'is_available': is_available},
                    'brand': {
                        'name': f'brand_name_{i}',
                        'slug': f'brand_slug_{i}',
                        'business': 'restaurant',
                    },
                    'data': {'features': {'delivery': {'text': '1000 мин'}}},
                },
                'meta': {
                    'place_id': i,
                    'brand_id': i,
                    'is_ultima': False,
                    'categories': ['пиво', 'Some Штуки', 'Сигареты'],
                },
            }
            places.append(place_data)

        return places

    @mockserver.json_handler('/eats-catalog/internal/v1/catalog-for-layout')
    def catalog(_):
        return {
            'filters': {},
            'sort': {},
            'timepicker': [],
            'blocks': [
                {
                    'id': 'open_locale_collection',
                    'list': build_places(1, True),
                },
            ],
        }

    response = await taxi_eats_layout_constructor.post(
        '/eats/v1/layout-constructor/v1/layout',
        headers={
            'x-device-id': 'testsuite',
            'x-platform': 'ios_app',
            'x-app-version': '5.10.0',
            'cookie': '{}',
            'X-Eats-User': 'user_id=12345',
            'content-type': 'application/json',
            'x-request-language': locale,
        },
        json={
            'view': {'type': 'collection', 'slug': 'locale_collection'},
            'location': {'latitude': 0.0, 'longitude': 0.0},
        },
    )

    if locale == 'ru':
        assert response.status_code == 404
        return

    assert catalog.times_called == 1
    assert response.status_code == 200

    data = response.json()['data']
    assert data['places_lists']
    assert data['view_header']
