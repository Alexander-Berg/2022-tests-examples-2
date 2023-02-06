# pylint: disable=C0302
import enum
import typing

import pytest

from testsuite.utils import matching

from . import configs
from . import experiments
from . import utils

CATALOG_FOR_LC_PATH = '/eats-catalog/internal/v1/catalog-for-layout'

LC_LAYOUT_PATH = 'eats/v1/layout-constructor/v1/layout'
LC_LAYOUT_HEADERS = {
    'x-device-id': 'device-id',
    'x-platform': 'android_app',
    'x-app-version': '12.11.12',
    'cookie': '{}',
    'X-Eats-User': 'user_id=12345',
    'x-request-application': 'application=1.1.0',
    'x-request-language': 'enUS',
    'Content-Type': 'application/json',
}
LC_LAYOUT_REQUEST = {'location': {'latitude': 0.0, 'longitude': 0.0}}

LC_EMPTY_RESPONSE: dict = {'data': {}, 'layout': []}


class OutputType(enum.Enum):
    LIST = 'list'
    CAROUSEL = 'carousel'


def build_catalog_response(
        block_id, block_type, places_count, is_ultima: bool = False,
):
    places = []
    for i in range(places_count):
        availability_data = {'is_available': True}
        payload = {
            'name': 'place' + str(i),
            'slug': 'place' + str(i),
            'availability': availability_data,
        }
        place_data = {
            'payload': payload,
            'meta': {'place_id': i, 'brand_id': i, 'is_ultima': is_ultima},
        }
        places.append(place_data)

    return {
        'blocks': [{'id': block_id, 'type': block_type, 'list': places}],
        'filters': {},
        'sort': {},
        'timepicker': [],
    }


def build_expected_response(
        widget_id, template_name, output_type: OutputType, expected_place_ids,
):
    places = []
    for i in expected_place_ids:
        place = {
            'name': 'place' + str(i),
            'slug': 'place' + str(i),
            'context': matching.any_string,
            'analytics': matching.any_string,
            'availability': {'is_available': True},
        }
        places.append(place)
    widget_data = {
        'id': widget_id,
        'payload': {'places': places},
        'template_name': template_name,
    }
    data_section = (
        'places_lists'
        if output_type == OutputType.LIST
        else 'places_carousels'
    )
    return {
        'data': {data_section: [widget_data]},
        'layout': [
            {
                'id': widget_id,
                'payload': {'title': 'Рестораны'},
                'type': (
                    'places_list'
                    if output_type == OutputType.LIST
                    else 'places_carousel'
                ),
            },
        ],
    }


def assert_request_block(data: dict, block_id: str, expected: dict):
    blocks: typing.List[str] = []
    for block in data['blocks']:
        blocks.append(block['id'])
        if block['id'] == block_id:
            assert block == expected
            return
    assert False, f'missing block with id {block_id}, got {blocks}'


@configs.layout_experiment_name('places_collection')
@experiments.layout(
    layout_slug='places_collection_layout',
    experiment_name='places_collection',
)
@pytest.mark.parametrize('places_count', [1, 5])
async def test_places_collection(
        taxi_eats_layout_constructor, mockserver, places_count,
):
    # Тест проверяет работу places_collection в общем случае

    @mockserver.json_handler(CATALOG_FOR_LC_PATH)
    def catalog(request):
        assert_request_block(
            request.json,
            'open',
            {
                'id': 'open',
                'type': 'open',
                'disable_filters': False,
                'round_eta_to_hours': False,
            },
        )
        return build_catalog_response('open', 'open', places_count)

    response = await taxi_eats_layout_constructor.post(
        LC_LAYOUT_PATH, headers=LC_LAYOUT_HEADERS, json=LC_LAYOUT_REQUEST,
    )

    expected_response = build_expected_response(
        '1_places_collection',
        'places_collection_list_template',
        OutputType.LIST,
        range(places_count),
    )
    assert response.status_code == 200
    assert catalog.times_called == 1
    assert response.json() == expected_response


@configs.layout_experiment_name('places_collection')
@experiments.layout(
    layout_slug='places_collection_layout_2',
    experiment_name='places_collection',
)
@pytest.mark.parametrize(
    'places_count',
    [
        pytest.param(5, id='enough_places'),
        pytest.param(3, id='not enough_places'),
    ],
)
async def test_places_collection_slice(
        taxi_eats_layout_constructor, mockserver, places_count,
):
    # Тест проверяет контент виджета в случае указания параметров
    # low и limit. Краевые случаи покрыты юнит тестами

    @mockserver.json_handler(CATALOG_FOR_LC_PATH)
    def catalog(request):
        assert_request_block(
            request.json,
            'open',
            {
                'id': 'open',
                'type': 'open',
                'disable_filters': False,
                'round_eta_to_hours': False,
            },
        )
        return build_catalog_response('open', 'open', places_count)

    response = await taxi_eats_layout_constructor.post(
        LC_LAYOUT_PATH, headers=LC_LAYOUT_HEADERS, json=LC_LAYOUT_REQUEST,
    )

    low_place_id = 2  # low = 2
    high_place_id = min(places_count, 4)  # limit = 2
    expected_response = build_expected_response(
        '2_places_collection',
        'places_collection_list_template',
        OutputType.LIST,
        range(low_place_id, high_place_id),
    )
    assert response.status_code == 200
    assert catalog.times_called == 1
    assert response.json() == expected_response


@configs.layout_experiment_name('places_collection')
@experiments.layout(
    layout_slug='places_collection_layout_5',
    experiment_name='places_collection',
)
@pytest.mark.parametrize(
    'places_count',
    [
        pytest.param(5, id='enough_places'),
        pytest.param(3, id='not enough_places'),
    ],
)
async def test_places_collection_min_count(
        taxi_eats_layout_constructor, mockserver, places_count,
):
    # Тест проверяет контент виджета при указании параметра min_count

    @mockserver.json_handler(CATALOG_FOR_LC_PATH)
    def catalog(request):
        assert_request_block(
            request.json,
            'open',
            {
                'id': 'open',
                'type': 'open',
                'disable_filters': False,
                'round_eta_to_hours': False,
            },
        )
        return build_catalog_response('open', 'open', places_count)

    response = await taxi_eats_layout_constructor.post(
        LC_LAYOUT_PATH, headers=LC_LAYOUT_HEADERS, json=LC_LAYOUT_REQUEST,
    )

    # виджет не должен отображаться, если для него не набралось
    # достаточное количество заведений
    min_count = 4
    is_enough_places = places_count >= min_count
    if is_enough_places:
        expected_response = build_expected_response(
            '5_places_collection',
            'places_collection_list_template',
            OutputType.LIST,
            range(places_count),
        )
    else:
        expected_response = LC_EMPTY_RESPONSE

    assert response.status_code == 200
    assert catalog.times_called == 1
    assert response.json() == expected_response


@configs.layout_experiment_name('places_collection')
@experiments.layout(
    layout_slug='places_collection_layout',
    experiment_name='places_collection',
)
async def test_places_collection_empty(
        taxi_eats_layout_constructor, mockserver,
):
    # Тест проверяет содержимое виджета, если каталог не вернул
    # подходящих заведений

    @mockserver.json_handler(CATALOG_FOR_LC_PATH)
    def catalog(request):
        assert_request_block(
            request.json,
            'open',
            {
                'id': 'open',
                'type': 'open',
                'disable_filters': False,
                'round_eta_to_hours': False,
            },
        )
        return build_catalog_response('open', 'open', 0)

    response = await taxi_eats_layout_constructor.post(
        LC_LAYOUT_PATH, headers=LC_LAYOUT_HEADERS, json=LC_LAYOUT_REQUEST,
    )

    assert response.status_code == 200
    assert catalog.times_called == 1
    assert response.json() == LC_EMPTY_RESPONSE


@configs.layout_experiment_name('places_collection')
@experiments.layout(
    layout_slug='places_collection_layout_3',
    experiment_name='places_collection',
)
@pytest.mark.parametrize(
    'places_count',
    [
        pytest.param(5, id='draw as carousel'),
        pytest.param(1, id='draw as list'),
    ],
)
async def test_places_collection_carousel(
        taxi_eats_layout_constructor, mockserver, places_count,
):
    # Тест проверяет отрисовку виджета с типом отображения 'carousel'

    @mockserver.json_handler(CATALOG_FOR_LC_PATH)
    def catalog(request):
        assert_request_block(
            request.json,
            'open',
            {
                'id': 'open',
                'type': 'open',
                'disable_filters': False,
                'round_eta_to_hours': False,
            },
        )
        return build_catalog_response('open', 'open', places_count)

    response = await taxi_eats_layout_constructor.post(
        LC_LAYOUT_PATH, headers=LC_LAYOUT_HEADERS, json=LC_LAYOUT_REQUEST,
    )

    # если в виджет попало одно заведение - отдаем его как list
    expected_output_type = (
        OutputType.CAROUSEL if places_count > 1 else OutputType.LIST
    )
    expected_response = build_expected_response(
        '3_places_collection',
        'places_collection_carousel_template',
        expected_output_type,
        range(places_count),
    )
    assert response.status_code == 200
    assert catalog.times_called == 1
    assert response.json() == expected_response


@configs.layout_experiment_name('places_collection')
@experiments.layout(
    layout_slug='places_collection_layout_4',
    experiment_name='places_collection',
)
async def test_places_collection_exclude_brands(
        taxi_eats_layout_constructor, mockserver,
):
    # Тест проверяет что заведения с brand_id, указанным в 'exclude_brands',
    # не попадут в виджет

    places_count = 6

    @mockserver.json_handler(CATALOG_FOR_LC_PATH)
    def catalog(request):
        assert_request_block(
            request.json,
            'open',
            {
                'id': 'open',
                'type': 'open',
                'disable_filters': False,
                'round_eta_to_hours': False,
            },
        )
        return build_catalog_response('open', 'open', places_count)

    response = await taxi_eats_layout_constructor.post(
        LC_LAYOUT_PATH, headers=LC_LAYOUT_HEADERS, json=LC_LAYOUT_REQUEST,
    )

    # exclude_brands = [3, 4]
    expected_response = build_expected_response(
        '4_places_collection',
        'places_collection_list_template',
        OutputType.LIST,
        [0, 1, 2, 5],
    )
    assert response.status_code == 200
    assert catalog.times_called == 1
    assert response.json() == expected_response


@configs.layout_experiment_name('places_collection')
@experiments.layout(
    layout_slug='places_collection_layout_6',
    experiment_name='places_collection',
)
async def test_places_collection_promo_selection(
        taxi_eats_layout_constructor, mockserver,
):
    # Тест проверяет работу виджета с ML коллекцией promo
    # Ранее в запросе передавался compilation_type = promo,
    # но теперь достаточно указать type = promo, чтобы каталог
    # выдал нужную подборку

    places_count = 3

    @mockserver.json_handler(CATALOG_FOR_LC_PATH)
    def catalog(request):
        assert_request_block(
            request.json,
            'promo',
            {
                'id': 'promo',
                'type': 'promo',
                'disable_filters': False,
                'round_eta_to_hours': False,
            },
        )
        return build_catalog_response('promo', 'promo', places_count)

    response = await taxi_eats_layout_constructor.post(
        LC_LAYOUT_PATH, headers=LC_LAYOUT_HEADERS, json=LC_LAYOUT_REQUEST,
    )

    expected_response = build_expected_response(
        '6_places_collection',
        'places_collection_list_template',
        OutputType.LIST,
        range(places_count),
    )
    assert response.status_code == 200
    assert catalog.times_called == 1
    assert response.json() == expected_response


@configs.layout_experiment_name('places_collection')
@experiments.layout(
    layout_slug='places_collection_layout_7',
    experiment_name='places_collection',
)
async def test_places_collection_exclude_businesses(
        taxi_eats_layout_constructor, mockserver,
):
    # Тест проверяет что при указании параметра 'exclude_businesses'
    # формируется корректный запрос к каталогу

    places_count = 3

    @mockserver.json_handler(CATALOG_FOR_LC_PATH)
    def catalog(request):
        assert_request_block(
            request.json,
            'open_no_shop_no_store',
            {
                'id': 'open_no_shop_no_store',
                'type': 'open',
                'disable_filters': False,
                'round_eta_to_hours': False,
                'condition': {
                    'type': 'not',
                    'predicates': [
                        {
                            'init': {
                                'arg_name': 'business',
                                'set_elem_type': 'string',
                                'set': utils.MatchingSet(['store', 'shop']),
                            },
                            'type': 'in_set',
                        },
                    ],
                },
            },
        )
        return build_catalog_response(
            'open_no_shop_no_store', 'open', places_count,
        )

    response = await taxi_eats_layout_constructor.post(
        LC_LAYOUT_PATH, headers=LC_LAYOUT_HEADERS, json=LC_LAYOUT_REQUEST,
    )

    expected_response = build_expected_response(
        '7_places_collection',
        'places_collection_list_template',
        OutputType.LIST,
        range(places_count),
    )
    assert response.status_code == 200
    assert catalog.times_called == 1
    assert response.json() == expected_response


@configs.layout_experiment_name('places_collection')
@experiments.layout(
    layout_slug='places_collection_layout_8',
    experiment_name='places_collection',
)
async def test_places_collection_disable_filters(
        taxi_eats_layout_constructor, mockserver,
):
    # Тест проверяет что при указании параметра 'disable_filters'
    # формируется корректный запрос к каталогу

    places_count = 3

    @mockserver.json_handler(CATALOG_FOR_LC_PATH)
    def catalog(request):
        assert_request_block(
            request.json,
            'open_no_filters',
            {
                'id': 'open_no_filters',
                'type': 'open',
                'disable_filters': True,
                'round_eta_to_hours': False,
            },
        )
        return build_catalog_response('open_no_filters', 'open', places_count)

    response = await taxi_eats_layout_constructor.post(
        LC_LAYOUT_PATH, headers=LC_LAYOUT_HEADERS, json=LC_LAYOUT_REQUEST,
    )

    expected_response = build_expected_response(
        '8_places_collection',
        'places_collection_list_template',
        OutputType.LIST,
        range(places_count),
    )
    assert response.status_code == 200
    assert catalog.times_called == 1
    assert response.json() == expected_response


@configs.layout_experiment_name('places_collection')
@experiments.layout(
    layout_slug='places_collection_layout_9',
    experiment_name='places_collection',
)
@pytest.mark.parametrize(
    'block',
    [
        pytest.param(
            {
                'id': 'open_history_order',
                'type': 'open',
                'round_eta_to_hours': False,
                'compilation_type': 'history_order',
                'disable_filters': False,
            },
            id='comilation from umlaas',
        ),
        pytest.param(
            {
                'id': 'open_history_order',
                'type': 'open',
                'round_eta_to_hours': False,
                'disable_filters': False,
                'sort_type': 'default',
                'condition': {
                    'type': 'gt',
                    'init': {
                        'arg_name': 'orders_count',
                        'arg_type': 'int',
                        'value': 0,
                    },
                },
            },
            marks=experiments.NATIVE_ORDER_HISTORY,
            id='native compilation',
        ),
    ],
)
async def test_places_collection_history_order_selection(
        taxi_eats_layout_constructor, mockserver, block,
):
    # Тест проверяет работу виджета с ML коллекцией history_order

    places_count = 3

    @mockserver.json_handler(CATALOG_FOR_LC_PATH)
    def catalog(request):
        assert_request_block(request.json, 'open_history_order', block)
        return build_catalog_response(
            'open_history_order', 'open', places_count,
        )

    response = await taxi_eats_layout_constructor.post(
        LC_LAYOUT_PATH, headers=LC_LAYOUT_HEADERS, json=LC_LAYOUT_REQUEST,
    )

    expected_response = build_expected_response(
        '9_places_collection',
        'places_collection_list_template',
        OutputType.LIST,
        range(places_count),
    )
    assert response.status_code == 200
    assert catalog.times_called == 1
    assert response.json() == expected_response


@pytest.mark.pgsql(
    'eats_layout_constructor',
    files=['pg_eats_layout_constructor_advert_layouts.sql'],
    directories=[],
    queries=[],
)
@configs.layout_experiment_name('eats_layout_constructor')
@pytest.mark.parametrize(
    'expected_blocks',
    [
        pytest.param(
            [
                {
                    'id': 'open',
                    'type': 'open',
                    'disable_filters': False,
                    'round_eta_to_hours': False,
                    'advert_settings': {'ads_only': True, 'indexes': []},
                },
            ],
            marks=(
                experiments.layout(
                    experiment_name='eats_layout_constructor',
                    layout_slug='layout_no_yabs_settings',
                )
            ),
            id='no yabs params in advert settings',
        ),
        pytest.param(
            [
                {
                    'id': 'open',
                    'type': 'open',
                    'disable_filters': False,
                    'round_eta_to_hours': False,
                    'advert_settings': {
                        'ads_only': True,
                        'indexes': [],
                        'yabs_params': {
                            'page_id': 1,
                            'target_ref': 'testsuite',
                            'page_ref': 'testsuite',
                        },
                    },
                },
            ],
            marks=(
                experiments.layout(
                    experiment_name='eats_layout_constructor',
                    layout_slug='layout_yabs_settings',
                )
            ),
            id='yabs params in advert settings',
        ),
        pytest.param(
            [
                {
                    'id': 'open',
                    'type': 'open',
                    'disable_filters': False,
                    'round_eta_to_hours': False,
                    'advert_settings': {
                        'ads_only': True,
                        'indexes': [],
                        'yabs_params': {
                            'page_id': 1,
                            'target_ref': 'testsuite',
                            'page_ref': 'testsuite',
                            'coefficients': {
                                'yabs_ctr': 1,
                                'eats_ctr': 0,
                                'send_relevance': False,
                                'relevance_multiplier': 1,
                            },
                        },
                    },
                },
            ],
            marks=(
                experiments.layout(
                    experiment_name='eats_layout_constructor',
                    layout_slug='layout_yabs_settings_no_send_rel',
                )
            ),
            id='yabs params in advert settings with no sed rel in layout',
        ),
        pytest.param(
            [
                {
                    'id': 'open',
                    'type': 'open',
                    'disable_filters': False,
                    'round_eta_to_hours': False,
                    'advert_settings': {
                        'ads_only': True,
                        'indexes': [],
                        'yabs_params': {
                            'page_id': 1,
                            'target_ref': 'testsuite',
                            'page_ref': 'testsuite',
                            'coefficients': {
                                'yabs_ctr': 1,
                                'eats_ctr': 0,
                                'send_relevance': False,
                                'relevance_multiplier': 1,
                            },
                        },
                    },
                },
            ],
            marks=(
                experiments.layout(
                    experiment_name='eats_layout_constructor',
                    layout_slug='layout_yabs_settings_false_send_rel',
                )
            ),
            id='yabs params in advert settings with no send relevance',
        ),
        pytest.param(
            [
                {
                    'id': 'open',
                    'type': 'open',
                    'disable_filters': False,
                    'round_eta_to_hours': False,
                    'advert_settings': {
                        'ads_only': True,
                        'indexes': [],
                        'yabs_params': {
                            'page_id': 1,
                            'target_ref': 'testsuite',
                            'page_ref': 'testsuite',
                            'coefficients': {
                                'yabs_ctr': 1,
                                'eats_ctr': 0,
                                'send_relevance': True,
                                'relevance_multiplier': 1,
                            },
                        },
                    },
                },
            ],
            marks=(
                experiments.layout(
                    experiment_name='eats_layout_constructor',
                    layout_slug='layout_yabs_settings_true_send_rel',
                )
            ),
            id='yabs params in advert settings with send relevance',
        ),
    ],
)
async def test_places_collection_advert_setting(
        taxi_eats_layout_constructor, mockserver, expected_blocks,
):
    """
    EDACAT-1409: Проверяет, что в каталог передаются корректные рекламные
    настройки блока.
    """

    @mockserver.json_handler(CATALOG_FOR_LC_PATH)
    def catalog(request):
        assert 'blocks' in request.json
        blocks = request.json['blocks']

        assert blocks == expected_blocks

        return {'blocks': [], 'filters': {}, 'sort': {}, 'timepicker': []}

    response = await taxi_eats_layout_constructor.post(
        LC_LAYOUT_PATH, headers=LC_LAYOUT_HEADERS, json=LC_LAYOUT_REQUEST,
    )
    assert response.status_code == 200
    assert catalog.times_called == 1


@configs.layout_experiment_name()
@experiments.layout('prioritized_brands')
@pytest.mark.layout(
    slug='prioritized_brands',
    widgets=[
        utils.Widget(
            name='Prioritized brands',
            type='places_collection',
            meta={
                'prioritized_brands': [5, 1, 3],
                'place_filter_type': 'open',
                'output_type': 'list',
            },
            payload={'title': 'Рестораны'},
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
async def test_places_collection_prioritized_brands(
        taxi_eats_layout_constructor, mockserver,
):
    # Тест проверяет, что приоритизация брендов работает корректно, т.е.
    # что заведения с brand_id, указанным в 'prioritized_brands',
    # располагаются на первых позициях

    places_count = 6

    @mockserver.json_handler(CATALOG_FOR_LC_PATH)
    def catalog(request):
        assert_request_block(
            request.json,
            'open',
            {
                'id': 'open',
                'type': 'open',
                'disable_filters': False,
                'round_eta_to_hours': False,
            },
        )
        return build_catalog_response('open', 'open', places_count)

    response = await taxi_eats_layout_constructor.post(
        LC_LAYOUT_PATH, headers=LC_LAYOUT_HEADERS, json=LC_LAYOUT_REQUEST,
    )

    # exclude_brands = [3, 4]
    expected_response = build_expected_response(
        '1_places_collection',
        'Prioritized brands_template',
        OutputType.LIST,
        [5, 1, 3, 0, 2, 4],
    )
    assert response.status_code == 200
    assert catalog.times_called == 1
    assert response.json() == expected_response


@configs.layout_experiment_name()
@experiments.RESIZE_IN_CATALOG
@experiments.layout('limit_places_in_catalog')
@pytest.mark.layout(
    slug='limit_places_in_catalog',
    widgets=[
        utils.Widget(
            name='limited_in_catalog',
            type='places_collection',
            meta={
                'place_filter_type': 'open',
                'output_type': 'list',
                'limit': 10,
                'min_count': 5,
                'low': 2,
            },
            payload={'title': 'Рестораны'},
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
async def test_places_collection_resize_in_catalog(
        taxi_eats_layout_constructor, mockserver,
):
    """
    Тест проверяет, что экспериментом eats_layout_constructor_resize_in_catalog
    в запросе каталога передается ограничения на размер и минимальное
    количество плейсов в блоке и при этом обрезка рестов не просиходит в
    eats-layout-constructor.
    """

    @mockserver.json_handler(CATALOG_FOR_LC_PATH)
    def catalog(request):
        assert_request_block(
            request.json,
            'open_min-count_5_low_2_limit_10',
            {
                'id': 'open_min-count_5_low_2_limit_10',
                'type': 'open',
                'disable_filters': False,
                'round_eta_to_hours': False,
                'limit': 10,
                'min_count': 5,
                'low': 2,
            },
        )
        return build_catalog_response(
            # NOTE(nk2ge5k): тут 30 плейсов в ответе каталога чтобы проверить
            # что LC не будет делать своих манипуляций
            'open_min-count_5_low_2_limit_10',
            'open',
            30,
        )

    response = await taxi_eats_layout_constructor.post(
        LC_LAYOUT_PATH, headers=LC_LAYOUT_HEADERS, json=LC_LAYOUT_REQUEST,
    )

    assert response.status_code == 200
    assert catalog.times_called == 1

    expected_response = build_expected_response(
        '1_places_collection',
        'limited_in_catalog_template',
        OutputType.LIST,
        # Проверяем, что LC вернул плейсы в том же виде,
        # что и каталог - не обрезая по настройкам виджета.
        [i for i in range(0, 30)],
    )

    assert response.json() == expected_response


@configs.layout_experiment_name()
@experiments.layout('test_round_eta')
@pytest.mark.layout(
    slug='test_round_eta',
    widgets=[
        utils.Widget(
            name='limited_in_catalog',
            type='places_collection',
            meta={
                'place_filter_type': 'open',
                'output_type': 'list',
                'round_eta_to_hours': True,
            },
            payload={'title': 'Рестораны'},
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
async def test_places_collection_round_eta(
        taxi_eats_layout_constructor, mockserver,
):
    """
    Тест проверяет, что экспериментом из настроке виджета корректно
    передается флаг round_eta_to_hours
    """

    @mockserver.json_handler(CATALOG_FOR_LC_PATH)
    def catalog(request):
        assert_request_block(
            request.json,
            'open_eta_in_hours',
            {
                'id': 'open_eta_in_hours',
                'type': 'open',
                'disable_filters': False,
                'round_eta_to_hours': True,
            },
        )
        return build_catalog_response('open_eta_in_hours', 'open', 1)

    response = await taxi_eats_layout_constructor.post(
        LC_LAYOUT_PATH, headers=LC_LAYOUT_HEADERS, json=LC_LAYOUT_REQUEST,
    )

    assert response.status_code == 200
    assert catalog.times_called == 1


def build_places(places_count, is_ultima: bool = False):
    places = []
    for i in range(places_count):
        place_data = {
            'payload': {
                'name': f'place{i}',
                'slug': f'place{i}',
                'availability': {'is_available': True},
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
            'meta': {'place_id': i, 'brand_id': i, 'is_ultima': is_ultima},
        }
        places.append(place_data)

    return places


def ultima_layout(enabled: bool, output_type: str = 'list'):
    return pytest.mark.layout(
        slug='test_ultima_widget_group',
        widgets=[
            utils.Widget(
                name='multiple_in_one',
                type='places_collection',
                meta={
                    'place_filter_type': 'open',
                    'output_type': output_type,
                    'enable_ultima': enabled,
                },
                payload={'title': 'Рестораны'},
                payload_schema={},
            ),
        ],
    )


@configs.layout_experiment_name()
@experiments.layout('test_ultima_widget_group')
@pytest.mark.pgsql(
    # Не загружаем 'pg_eats_layout_constructor.sql'
    'eats_layout_constructor',
    files=[],
    directories=[],
    queries=[],
)
@pytest.mark.parametrize(
    'expected',
    [
        pytest.param(
            [
                {
                    'id': '1_places_collection_0',
                    'payload': {'title': 'Рестораны'},
                    'type': 'places_list',
                    'size': 1,
                },
                {
                    'id': '1_places_collection_separator_1',
                    'payload': {},
                    'type': 'separator',
                },
                {
                    'id': '1_places_collection_1',
                    'payload': {},
                    'type': 'ultima_places_list',
                    'size': 2,
                },
                {
                    'id': '1_places_collection_separator_2',
                    'payload': {},
                    'type': 'separator',
                },
                {
                    'id': '1_places_collection_2',
                    'payload': {},
                    'type': 'places_list',
                    'size': 3,
                },
                {
                    'id': '1_places_collection_separator_3',
                    'payload': {},
                    'type': 'separator',
                },
                {
                    'id': '1_places_collection_3',
                    'payload': {},
                    'type': 'ultima_places_list',
                    'size': 1,
                },
            ],
            marks=(
                ultima_layout(True),
                configs.ultima_places(
                    {
                        'place0': {
                            'image': 'http://place_slug_0',
                            'carousel_settings': {'items': []},
                        },
                        'place1': {
                            'image': 'http://place_slug_1',
                            'carousel_settings': {'items': []},
                        },
                    },
                ),
            ),
            id='full config',
        ),
        pytest.param(
            [
                {
                    'id': '1_places_collection',
                    'payload': {'title': 'Рестораны'},
                    'type': 'places_list',
                    'size': 7,
                },
            ],
            marks=(
                ultima_layout(False),
                configs.ultima_places(
                    {
                        'place0': {
                            'image': 'http://place_slug_0',
                            'carousel_settings': {'items': []},
                        },
                        'place1': {
                            'image': 'http://place_slug_1',
                            'carousel_settings': {'items': []},
                        },
                    },
                ),
            ),
            id='full config and disabled',
        ),
        pytest.param(
            [
                {
                    'id': '1_places_collection',
                    'payload': {'title': 'Рестораны'},
                    'type': 'places_carousel',
                    'size': 7,
                },
            ],
            marks=(
                ultima_layout(True, 'carousel'),
                configs.ultima_places(
                    {
                        'place0': {
                            'image': 'http://place_slug_0',
                            'carousel_settings': {'items': []},
                        },
                        'place1': {
                            'image': 'http://place_slug_1',
                            'carousel_settings': {'items': []},
                        },
                    },
                ),
            ),
            id='full config carousel',
        ),
        pytest.param(
            [
                {
                    'id': '1_places_collection_0',
                    'payload': {'title': 'Рестораны'},
                    'type': 'places_list',
                    'size': 2,
                },
                {
                    'id': '1_places_collection_separator_1',
                    'payload': {},
                    'type': 'separator',
                },
                {
                    'id': '1_places_collection_1',
                    'payload': {},
                    'type': 'ultima_places_list',
                    'size': 1,
                },
                {
                    'id': '1_places_collection_separator_2',
                    'payload': {},
                    'type': 'separator',
                },
                {
                    'id': '1_places_collection_2',
                    'payload': {},
                    'type': 'places_list',
                    'size': 4,
                },
            ],
            marks=(
                ultima_layout(True),
                configs.ultima_places(
                    {
                        'place1': {
                            'image': 'http://place_slug_1',
                            'carousel_settings': {'items': []},
                        },
                    },
                ),
            ),
            id='partial config',
        ),
        pytest.param(
            [
                {
                    'id': '1_places_collection',
                    'payload': {'title': 'Рестораны'},
                    'type': 'places_list',
                    'size': 7,
                },
            ],
            marks=ultima_layout(True),
            id='no config',
        ),
    ],
)
async def test_widget_group(
        taxi_eats_layout_constructor, mockserver, expected,
):
    def section(widget_type: str) -> str:
        if widget_type == 'places_list':
            return 'places_lists'
        if widget_type == 'ultima_places_list':
            return 'ultima_places_list'
        if widget_type == 'places_carousel':
            return 'places_carousels'

        assert False, f'unknown type {type}'
        return ''

    @mockserver.json_handler(CATALOG_FOR_LC_PATH)
    def catalog(request):
        assert_request_block(
            request.json,
            'open',
            {
                'id': 'open',
                'type': 'open',
                'disable_filters': False,
                'round_eta_to_hours': False,
            },
        )

        places = build_places(1, False)  # 1 default
        places += build_places(2, True)  # 2 ultima
        places += build_places(3, False)  # 3 default
        places += build_places(1, True)  # 1 ultima

        return {
            'blocks': [{'id': 'open', 'type': 'open', 'list': places}],
            'filters': {},
            'sort': {},
            'timepicker': [],
        }

    response = await taxi_eats_layout_constructor.post(
        LC_LAYOUT_PATH, headers=LC_LAYOUT_HEADERS, json=LC_LAYOUT_REQUEST,
    )

    assert response.status_code == 200
    assert catalog.times_called == 1

    data = response.json()

    assert len(data['layout']) == len(expected)

    for i, item in enumerate(data['layout']):
        expected_item = expected[i]

        assert item['id'] == expected_item['id']
        assert item['payload'] == expected_item['payload']
        assert item['type'] == expected_item['type']

        if item['type'] == 'separator':
            continue

        for data_item in data['data'][section(item['type'])]:
            if data_item['id'] == expected_item['id']:
                assert (
                    len(data_item['payload']['places'])
                    == expected_item['size']
                )
