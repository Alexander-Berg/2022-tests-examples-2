# pylint: disable=C0302
import typing

from dateutil import parser
import pytest

from eats_catalog import experiments
from eats_catalog import storage
from . import layout_utils

EATS_CUSTOMER_SLOTS = (
    '/eats-customer-slots/api/v1/places/calculate-delivery-time'
)


UMLAAS_RESPONSE_SORT_ALL = {
    'exp_list': [],
    'request_id': '',
    'provider': '',
    'available_blocks': [],
    'result': [
        {
            'id': 4,
            'relevance': 11.0,
            'type': 'ranking',
            'predicted_times': {'min': 5, 'max': 15},
            'blocks': [],
        },
        {
            'id': 3,
            'relevance': 10.0,
            'type': 'ranking',
            'predicted_times': {'min': 30, 'max': 40},
            'blocks': [],
        },
        {
            'id': 2,
            'relevance': 9.0,
            'type': 'ranking',
            'predicted_times': {'min': 30, 'max': 30},
            'blocks': [],
        },
        {
            'id': 1,
            'relevance': 8.0,
            'type': 'ranking',
            'predicted_times': {'min': 30, 'max': 40},
            'blocks': [],
        },
    ],
}

UMLAAS_RESPONSE_SORT_HALF = {
    'exp_list': [],
    'request_id': '',
    'provider': '',
    'available_blocks': [],
    'result': [
        {
            'id': 4,
            'relevance': 11.0,
            'type': 'ranking',
            'predicted_times': {'min': 5, 'max': 15},
            'blocks': [],
        },
        {
            'id': 2,
            'relevance': 10.0,
            'type': 'ranking',
            'predicted_times': {'min': 30, 'max': 40},
            'blocks': [],
        },
    ],
}

UMLAAS_RESPONSE_SORT_ONE = {
    'exp_list': [],
    'request_id': '',
    'provider': '',
    'available_blocks': [],
    'result': [
        {
            'id': 2,
            'relevance': 11.0,
            'type': 'ranking',
            'predicted_times': {'min': 5, 'max': 15},
            'blocks': [],
        },
    ],
}

UMLAAS_RESPONSE_SORT_NONE = {
    'exp_list': [],
    'request_id': '',
    'provider': '',
    'available_blocks': [],
    'result': [
        {
            'id': 1,
            'relevance': 11.0,
            'type': 'ranking',
            'predicted_times': {'min': 5, 'max': 15},
            'blocks': [],
        },
        {
            'id': 2,
            'relevance': 10.0,
            'type': 'ranking',
            'predicted_times': {'min': 30, 'max': 40},
            'blocks': [],
        },
        {
            'id': 3,
            'relevance': 9.0,
            'type': 'ranking',
            'predicted_times': {'min': 30, 'max': 30},
            'blocks': [],
        },
        {
            'id': 4,
            'relevance': 8.0,
            'type': 'ranking',
            'predicted_times': {'min': 30, 'max': 40},
            'blocks': [],
        },
    ],
}

UMLAAS_RESPONSE_SORT_NONE_ONE = {
    'exp_list': [],
    'request_id': '',
    'provider': '',
    'available_blocks': [],
    'result': [
        {
            'id': 1,
            'relevance': 11.0,
            'type': 'ranking',
            'predicted_times': {'min': 5, 'max': 15},
            'blocks': [],
        },
    ],
}

UMLAAS_RESPONSE_EMPTY = {
    'exp_list': [],
    'request_id': '',
    'provider': '',
    'available_blocks': [],
    'result': [],
}


DISABLE_UMLAAS = experiments.ranking_fallback(disable_umlaas=True)


@pytest.mark.parametrize(
    'umlaas_response, places_response_expected, umlaas_times_called',
    [
        pytest.param(UMLAAS_RESPONSE_SORT_ALL, [4, 3, 2, 1], 1, id='sort all'),
        pytest.param(
            UMLAAS_RESPONSE_SORT_HALF, [4, 2, 3, 1], 1, id='sort half',
        ),
        pytest.param(UMLAAS_RESPONSE_SORT_ONE, [2, 4, 3, 1], 1, id='sort one'),
        pytest.param(
            UMLAAS_RESPONSE_SORT_NONE, [1, 2, 3, 4], 1, id='sort none',
        ),
        pytest.param(
            UMLAAS_RESPONSE_SORT_NONE_ONE, [1, 4, 3, 2], 1, id='sort none one',
        ),
        pytest.param(UMLAAS_RESPONSE_EMPTY, [4, 3, 2, 1], 1, id='empty'),
        pytest.param(
            UMLAAS_RESPONSE_SORT_ALL,
            [4, 3, 2, 1],
            0,
            marks=DISABLE_UMLAAS,
            id='disable umlaas',
        ),
    ],
)
@pytest.mark.now('2021-08-17T13:04:00+03:00')
async def test_layout_ml(
        catalog_for_layout,
        mockserver,
        eats_catalog_storage,
        umlaas_response,
        places_response_expected,
        umlaas_times_called,
):
    schedule = [
        storage.WorkingInterval(
            start=parser.parse('2021-08-10T19:04:00+03:00'),
            end=parser.parse('2021-08-17T23:04:00+03:00'),
        ),
    ]

    for place_id in range(1, 5):
        eats_catalog_storage.add_place(
            storage.Place(
                place_id=place_id, brand=storage.Brand(brand_id=place_id),
            ),
        )
        eats_catalog_storage.add_zone(
            storage.Zone(
                zone_id=place_id,
                place_id=place_id,
                working_intervals=schedule,
            ),
        )

    @mockserver.json_handler('/umlaas-eats/umlaas-eats/v1/catalog')
    def umlaas_eats(request):
        assert request.method == 'POST'
        return umlaas_response

    response = await catalog_for_layout(
        blocks=[{'id': 'any', 'type': 'any', 'disable_filters': False}],
    )

    assert eats_catalog_storage.search_times_called == 1
    assert umlaas_eats.times_called == umlaas_times_called
    assert response.status_code == 200
    blocks_list = layout_utils.find_block('any', response.json())

    places_response = []
    for place in blocks_list:
        places_response.append(place['meta']['place_id'])

    assert places_response == places_response_expected


@experiments.USE_DELIVERY_SLOTS
@pytest.mark.now('2021-03-27T21:00:00+03:00')
@pytest.mark.regions_settings(file='regions_settings.json')
async def test_layout_block_compilation_type(
        catalog_for_layout, eats_catalog_storage, mockserver,
):
    """
    EDACAT-156: тест проверяет корректность сортировки завдений при помощи
    блоков сортировки из ручки /umlaas-eats/v1/catalog
    """

    schedule = [
        storage.WorkingInterval(
            start=parser.parse('2021-03-27T10:00:00+03:00'),
            end=parser.parse('2021-03-27T23:00:00+03:00'),
        ),
    ]

    for place_id in range(1, 3):
        eats_catalog_storage.add_place(
            storage.Place(
                place_id=place_id, brand=storage.Brand(brand_id=place_id),
            ),
        )
        eats_catalog_storage.add_zone(
            storage.Zone(
                zone_id=place_id,
                place_id=place_id,
                working_intervals=schedule,
            ),
        )

    # Добавляем магазин для проверки корректности передачи слотов
    eats_catalog_storage.add_place(
        storage.Place(
            place_id=3,
            brand=storage.Brand(brand_id=3),
            business=storage.Business.Shop,
            features=storage.Features(
                shop_picking_type=storage.ShopPickingType.ShopPicking,
            ),
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(zone_id=3, place_id=3, working_intervals=schedule),
    )

    # Добавляем маркетплейс для проверки корректности отправки данных
    eats_catalog_storage.add_place(
        storage.Place(
            place_id=5,
            brand=storage.Brand(brand_id=5),
            place_type=storage.PlaceType.Marketplace,
            timing=storage.PlaceTiming(
                preparation=60 * 60,
                extra_preparation=60 * 60,
                average_preparation=60 * 60,
            ),
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(
            zone_id=5,
            place_id=5,
            timing=storage.ZoneTimings(market_avg_time=40 * 60),
            working_intervals=schedule,
        ),
    )

    @mockserver.json_handler(EATS_CUSTOMER_SLOTS)
    def eats_customer_slots(request):
        return {
            'places': [
                {
                    'place_id': '3',
                    'short_text': 'short_delivery_slot_text',
                    'full_text': 'full_delivery_slot_text',
                    'delivery_eta': 42,
                    'slots_availability': True,
                    'asap_availability': False,
                },
            ],
        }

    @mockserver.json_handler('/eats-core-promo/server/api/v1/promo/active')
    def _active(_):
        return {
            'cursor': '',
            'promos': [
                {
                    'id': 3,
                    'name': 'Бесплатные тесты 3',
                    'description': 'При написании фичи, тесты в подарок 3',
                    'type': {
                        'id': 3,
                        'name': 'Тесты в подарок 3',
                        'picture': 'http://istock/harold',
                        'detailed_picture': 'http://istock/pepe',
                    },
                    'places': [
                        {'id': 1, 'disabled_by_surge': False},
                        {'id': 3, 'disabled_by_surge': False},
                    ],
                },
            ],
        }

    @mockserver.json_handler('/umlaas-eats/umlaas-eats/v1/catalog')
    def umlaas_eats(request):

        assert {
            'request_id': 'hello',
            'ranking_at': '2021-03-27T18:00:00+00:00',
            'user_agent': 'Python/3.7 aiohttp/3.5.4',
            'location': {'lon': 37.591503, 'lat': 55.802998},
            'places': [
                {
                    'id': 3,
                    'eta_minutes_min': 25,
                    'eta_minutes_max': 35,
                    'is_new': False,
                    'is_available': True,
                    'courier_type': 'pedestrian',
                    'time_to_delivery': 23.0,
                    'delivery_time_offset': -10,
                    'delivery_fee': {'thresholds': []},
                    'slot': {
                        'is_asap_available': False,
                        'is_slot_available': True,
                    },
                },
                {
                    'id': 2,
                    'eta_minutes_min': 25,
                    'eta_minutes_max': 35,
                    'is_new': False,
                    'is_available': True,
                    'courier_type': 'pedestrian',
                    'time_to_delivery': 23.0,
                    'delivery_time_offset': -10,
                    'delivery_fee': {'thresholds': []},
                },
                {
                    'id': 1,
                    'eta_minutes_min': 25,
                    'eta_minutes_max': 35,
                    'is_new': False,
                    'is_available': True,
                    'courier_type': 'pedestrian',
                    'time_to_delivery': 23.0,
                    'delivery_time_offset': -10,
                    'delivery_fee': {'thresholds': []},
                },
                {
                    'id': 5,
                    'eta_minutes_min': 40,
                    'eta_minutes_max': 40,
                    'is_new': False,
                    'is_available': True,
                    'time_to_delivery': 40.0,
                    'delivery_time_offset': 0,
                    'delivery_fee': {'thresholds': []},
                },
            ],
        } == request.json

        return {
            'exp_list': [],
            'request_id': '',
            'provider': '',
            'available_blocks': ['test_1', 'test_2'],
            'result': [
                {
                    'id': 2,
                    'relevance': 1,
                    'type': 'ranking',
                    'predicted_times': {'min': 10, 'max': 20},
                    'blocks': [
                        {'block_id': 'test_1', 'relevance': -10.22232321},
                    ],
                },
                {
                    'id': 3,
                    'relevance': 100,
                    'type': 'ranking',
                    'predicted_times': {'min': 15, 'max': 25},
                    'blocks': [{'block_id': 'promo', 'relevance': 0.2}],
                },
                {
                    'id': 1,
                    'relevance': 50,
                    'type': 'ranking',
                    'predicted_times': {'min': 20, 'max': 30},
                    'blocks': [
                        {'block_id': 'test_1', 'relevance': 3.14},
                        {'block_id': 'promo', 'relevance': 1.0 / 3.0},
                    ],
                },
                {
                    'id': 5,
                    'relevance': -20,
                    'type': 'ranking',
                    'predicted_times': {'min': 40, 'max': 40},
                    'blocks': [],
                },
            ],
        }

    response = await catalog_for_layout(
        blocks=[
            {'id': 'just_any', 'type': 'any', 'disable_filters': False},
            {
                'id': 'open_compilation_1',
                'type': 'open',
                'compilation_type': 'test_1',
                'disable_filters': False,
            },
            {
                'id': 'promo',
                'type': 'promo',
                'compilation_type': 'test_2',  # Изменится на promo
                'disable_filters': False,
            },
            {
                'id': 'open_compilation_unknown',
                'type': 'open',
                'compilation_type': 'test_unknown',
                'disable_filters': False,
            },
        ],
    )

    assert eats_customer_slots.times_called == 1
    assert umlaas_eats.times_called == 1
    assert response.status == 200

    data = response.json()

    assert len(data['blocks']) == 3

    assert_place_order(data, 'just_any', [3, 1, 2, 5])
    assert_place_order(data, 'open_compilation_1', [1, 2])
    assert_place_order(data, 'promo', [1, 3])


def assert_place_order(response, block_id, order):
    for block in response['blocks']:
        if block['id'] != block_id:
            continue

        actual = [place['meta']['place_id'] for place in block['list']]
        assert order == actual, 'unexpected order in block {}'.format(block_id)

        return

    pytest.fail('block with id {} not found', block_id)


@pytest.mark.parametrize(
    'limit, expected_size',
    [pytest.param(1, 1), pytest.param(5, 5), pytest.param(None, 10)],
)
async def test_ml_limit(
        catalog_for_layout,
        eats_catalog_storage,
        mockserver,
        taxi_config,
        limit,
        expected_size,
):
    if limit is not None:
        taxi_config.set_values(
            {'EATS_CATALOG_UMLAAS_CATALOG': {'limit': limit}},
        )
    else:
        taxi_config.set_values({'EATS_CATALOG_UMLAAS_CATALOG': {}})

    schedule = [
        storage.WorkingInterval(
            start=parser.parse('2021-08-17T19:04:00+03:00'),
            end=parser.parse('2021-08-17T21:04:00+03:00'),
        ),
    ]

    for place_id in range(1, 11):
        eats_catalog_storage.add_place(
            storage.Place(
                place_id=place_id, brand=storage.Brand(brand_id=place_id),
            ),
        )
        eats_catalog_storage.add_zone(
            storage.Zone(
                zone_id=place_id,
                place_id=place_id,
                working_intervals=schedule,
            ),
        )

    @mockserver.json_handler('/umlaas-eats/umlaas-eats/v1/catalog')
    def umlaas_eats(request):
        assert len(request.json['places']) == expected_size
        return {}

    response = await catalog_for_layout(
        blocks=[{'id': 'any', 'type': 'any', 'disable_filters': False}],
    )

    assert umlaas_eats.times_called == 1
    assert response.status == 200
    layout_utils.find_block('any', response.json())


@pytest.mark.now('2021-04-12T21:00:00+03:00')
@pytest.mark.regions_settings(file='regions_settings.json')
async def test_predictions(
        catalog_for_layout, eats_catalog_storage, prediction,
):

    prediction_request = {
        'predicting_at': '2021-04-12T18:00:00+00:00',
        'server_time': '2021-04-12T18:00:00+00:00',
        'user_location': {'lat': 55.802998, 'lon': 37.591503},
        'requested_times': [],
    }

    for place_id in range(1, 5):
        eats_catalog_storage.add_place(
            storage.Place(
                place_id=place_id,
                brand=storage.Brand(brand_id=1),
                business=storage.Business.Store,
                new_rating=storage.NewRating(rating=4.8002, show=True),
            ),
        )
        eats_catalog_storage.add_zone(
            storage.Zone(
                zone_id=place_id,
                place_id=place_id,
                working_intervals=[
                    storage.WorkingInterval(
                        start=parser.parse('2021-04-12T20:00:00+03:00'),
                        end=parser.parse('2021-04-12T23:00:00+03:00'),
                    ),
                ],
            ),
        )

        prediction_request['requested_times'].append(
            {
                'id': place_id,
                'place': {
                    'id': place_id,
                    'time_to_delivery': 10,
                    'average_preparation_time': 12.0,
                    'place_increment': 0.0,
                    'region_delivery_time_offset': 10.0,
                    'zone_id': place_id,
                    'brand_id': 1,
                    'is_fast_food': False,
                    'average_user_rating': 4.8002,
                    'shown_rating': 4.8002,
                    'price_category': 1,
                    'location': {'lat': 55.8129, 'lon': 37.5916},
                    'delivery_type': 'native',
                    'courier_type': 'pedestrian',
                },
                'default_times': {
                    'total_time': 22.0,
                    'cooking_time': 12.0,
                    'delivery_time': 10.0,
                    'boundaries': {'min': 22, 'max': 32},
                },
            },
        )
        prediction.set_place_time(place_id, place_id * 10, place_id * 10 + 25)

    prediction.expected_request = prediction_request

    response = await catalog_for_layout(
        blocks=[{'id': 'open', 'type': 'open', 'disable_filters': False}],
    )

    assert prediction.times_called == 1
    assert response.status == 200
    block = layout_utils.find_block('open', response.json())

    assert len(block) == 1
    assert (
        block[0]['payload']['data']['features']['delivery']['text']
        == '10\u2009–\u200935 мин'
    )


@pytest.mark.parametrize(
    'gzip',
    [
        pytest.param(False, id='without gzip'),
        pytest.param(
            False,
            marks=(
                pytest.mark.config(
                    EATS_CATALOG_UMLAAS_CATALOG={
                        'base_url': {'$mockserver': '/umlaas-eats'},
                        'compression': {
                            'enabled': True,
                            'level': 2,
                            'place_threshold': 5,
                        },
                    },
                )
            ),
            id='without gzip by threshold',
        ),
        pytest.param(
            True,
            marks=(
                pytest.mark.config(
                    EATS_CATALOG_UMLAAS_CATALOG={
                        'base_url': {'$mockserver': '/umlaas-eats'},
                        'compression': {
                            'enabled': True,
                            'level': 2,
                            'place_threshold': 0,
                        },
                    },
                )
            ),
            id='with gzip',
        ),
    ],
)
@pytest.mark.now('2021-03-27T21:00:00+03:00')
async def test_gzip(
        catalog_for_layout, eats_catalog_storage, mockserver, gzip,
):
    for place_id in range(1, 4):
        eats_catalog_storage.add_place(
            storage.Place(
                place_id=place_id, brand=storage.Brand(brand_id=place_id),
            ),
        )
        eats_catalog_storage.add_zone(
            storage.Zone(
                zone_id=place_id,
                place_id=place_id,
                working_intervals=[
                    storage.WorkingInterval(
                        start=parser.parse('2021-03-27T10:00:00+03:00'),
                        end=parser.parse('2021-03-27T23:00:00+03:00'),
                    ),
                ],
            ),
        )

    @mockserver.json_handler('/umlaas-eats/umlaas-eats/v1/catalog')
    def umlaas_eats(request):
        if gzip:
            assert request.headers['Content-Encoding'] == 'gzip'

        assert 'X-Ya-Service-Ticket' in request.headers
        assert (
            request.headers['Content-Type']
            == 'application/json; charset=utf-8'
        )

        assert request.json['request_id'] == 'hello'
        assert request.json['ranking_at'] == '2021-03-27T18:00:00+00:00'
        assert request.json['user_agent'] == 'Python/3.7 aiohttp/3.5.4'
        assert request.json['location'] == {'lon': 37.591503, 'lat': 55.802998}
        assert len(request.json['places']) == 3

        return {}

    response = await catalog_for_layout(
        blocks=[{'id': 'just_any', 'type': 'any', 'disable_filters': False}],
    )

    assert umlaas_eats.times_called == 1
    assert response.status == 200

    block = layout_utils.find_block('just_any', response.json())
    assert len(block) == 3


@pytest.mark.now('2020-05-21T14:12:00+03:00')
@pytest.mark.parametrize(
    'expected_order',
    [
        pytest.param([3, 2, 1], id='default'),
        pytest.param(
            [1, 3, 2], marks=(experiments.SHOP_FIRST), id='shop first',
        ),
    ],
)
async def test_layout_place_sort(
        catalog_for_layout, eats_catalog_storage, mockserver, expected_order,
):
    """
    EDACAT-1016: проверяет, что заведения отправляются в umlaas-eats в порядке
    соответствующем локальной сортировке, а не в порядке, в котором заведения
    пришли из eats-catalog-storage.
    Так же проверяется, что ETA в выдаче переопределяется значением из ответа
    umlaas-eats
    """

    # Добавляем ресторан с доставкой такси
    eats_catalog_storage.add_place(
        storage.Place(
            slug='taxi_delivery',
            place_id=1,
            brand=storage.Brand(brand_id=1),
            timing=storage.PlaceTiming(preparation=15 * 60),
            business=storage.Business.Shop,
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(
            place_id=1,
            zone_id=1,
            couriers_type=storage.CouriersType.YandexTaxi,
            working_intervals=[
                storage.WorkingInterval(
                    start=parser.parse('2020-05-21T10:00:00+03:00'),
                    end=parser.parse('2020-05-21T18:00:00+03:00'),
                ),
            ],
        ),
    )

    # Добавляем ресторан с пешей доставкой, но того же бренда
    # что и первый - после локальной сортировки он должен быть выше
    # чем первый
    eats_catalog_storage.add_place(
        storage.Place(
            slug='pedestrian_delivery',
            place_id=2,
            brand=storage.Brand(brand_id=1),
            timing=storage.PlaceTiming(preparation=30 * 60),
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(
            place_id=2,
            zone_id=2,
            couriers_type=storage.CouriersType.Pedestrian,
            working_intervals=[
                storage.WorkingInterval(
                    start=parser.parse('2020-05-21T10:00:00+03:00'),
                    end=parser.parse('2020-05-21T18:00:00+03:00'),
                ),
            ],
        ),
    )

    # Добавляем ресторан, у которого доставка будет быстрее чем у второго
    # поэтому в конечной сортивке он должен быть выше всех
    eats_catalog_storage.add_place(
        storage.Place(
            slug='fastest',
            place_id=3,
            brand=storage.Brand(brand_id=2),
            timing=storage.PlaceTiming(preparation=15 * 60),
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(
            place_id=3,
            zone_id=3,
            couriers_type=storage.CouriersType.Pedestrian,
            working_intervals=[
                storage.WorkingInterval(
                    start=parser.parse('2020-05-21T10:00:00+03:00'),
                    end=parser.parse('2020-05-21T18:00:00+03:00'),
                ),
            ],
        ),
    )

    @mockserver.json_handler('/umlaas-eats/umlaas-eats/v1/catalog')
    def _umlaas_eats(request):
        order = [place['id'] for place in request.json['places']]

        assert order == expected_order

        return {
            'exp_list': [],
            'request_id': '',
            'provider': '',
            'available_blocks': [],
            'result': [
                {
                    'id': 3,
                    'relevance': 1.0,
                    'type': 'ranking',
                    'predicted_times': {'min': 5, 'max': 15},
                    'blocks': [],
                },
                {
                    'id': 2,
                    'relevance': 0.5,
                    'type': 'ranking',
                    'predicted_times': {'min': 60, 'max': 100},
                    'blocks': [],
                },
                {
                    'id': 1,
                    'relevance': 0.1,
                    'type': 'ranking',
                    'predicted_times': {'min': 30, 'max': 30},
                    'blocks': [],
                },
            ],
        }

    response = await catalog_for_layout(
        blocks=[{'id': 'open', 'type': 'open', 'disable_filters': False}],
    )

    assert response.status_code == 200
    block = layout_utils.find_block('open', response.json())

    expected = [
        {'id': 3, 'eta': '5\u2009–\u200915 мин'},
        {'id': 2, 'eta': '60\u2009–\u2009100 мин'},
    ]

    index = 0
    for place in block:
        assert place['meta']['place_id'] == expected[index]['id']

        eta_text = place['payload']['data']['features']['delivery']['text']
        assert eta_text == expected[index]['eta']

        index = index + 1


@pytest.mark.now('2021-08-17T20:46:00+03:00')
async def test_no_schedule(
        catalog_for_layout, eats_catalog_storage, mockserver,
):

    eats_catalog_storage.add_place(
        storage.Place(
            slug='pickup',
            place_id=1,
            brand=storage.Brand(brand_id=1),
            timing=storage.PlaceTiming(preparation=15 * 60),
            business=storage.Business.Shop,
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(
            place_id=1,
            zone_id=1,
            shipping_type=storage.ShippingType.Pickup,
            working_intervals=[
                storage.WorkingInterval(
                    start=parser.parse('2021-08-17T10:46:00+03:00'),
                    end=parser.parse('2021-08-17T23:46:00+03:00'),
                ),
            ],
        ),
    )

    @mockserver.json_handler('/umlaas-eats/umlaas-eats/v1/catalog')
    def umlaas_eats(_):
        pass

    response = await catalog_for_layout(
        blocks=[{'id': 'any', 'type': 'any', 'disable_filters': False}],
    )

    assert umlaas_eats.times_called == 0
    assert response.status_code == 200


@pytest.mark.now('2021-11-01T15:27:00+03:00')
async def test_plus(catalog_for_layout, eats_catalog_storage, mockserver):
    """
    Тест проверяет, что процент кешбека Плюс правильно передается в
    ручку ранжирования umlaas-eats
    """

    @mockserver.json_handler(
        '/eats-plus/internal/eats-plus/v1/presentation/cashback/places-list',
    )
    def eats_plus(_):
        return {
            'cashback': [
                {'place_id': 1, 'cashback': 1.1},
                {'place_id': 2, 'cashback': 22.22},
                {'place_id': 3, 'cashback': 333},
            ],
        }

    for i in range(1, 5):
        eats_catalog_storage.add_place(
            storage.Place(
                slug=f'place_{i}', place_id=i, brand=storage.Brand(brand_id=i),
            ),
        )
        eats_catalog_storage.add_zone(
            storage.Zone(
                place_id=i,
                zone_id=i,
                working_intervals=[
                    storage.WorkingInterval(
                        start=parser.parse('2020-11-01T10:00:00+03:00'),
                        end=parser.parse('2020-11-01T18:00:00+03:00'),
                    ),
                ],
            ),
        )

    @mockserver.json_handler('/umlaas-eats/umlaas-eats/v1/catalog')
    def umlaas_eats(request):
        plus: typing.Dict[int, typing.Optional[float]] = {}
        for place in request.json['places']:
            if 'plus' in place:
                plus[place['id']] = place['plus']['cashback_percent']
            else:
                plus[place['id']] = None

        assert plus == {1: 1.1, 2: 22.22, 3: 333, 4: None}

        return {
            'exp_list': [],
            'request_id': '',
            'provider': '',
            'available_blocks': [],
            'result': [],
        }

    response = await catalog_for_layout(
        blocks=[{'id': 'any', 'type': 'any', 'disable_filters': False}],
    )

    assert eats_plus.times_called == 1
    assert umlaas_eats.times_called == 1
    assert response.status_code == 200
