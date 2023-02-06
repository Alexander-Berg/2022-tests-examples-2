import dataclasses
import typing

from dateutil import parser
import pytest

from eats_catalog import configs
from eats_catalog import experiments
from eats_catalog import storage
from . import places_utils


ENABLE_OVERRIDES = pytest.mark.config(
    EATS_CATALOG_OVERRIDES={
        '1': {
            'color': {'light': '#000000', 'dark': '#FFFFFF'},
            'logo': {
                'light': [{'size': 'small', 'url': 'light_url'}],
                'dark': [{'size': 'small', 'url': 'dark_url'}],
            },
        },
    },
)


def create_quick_filter(filter_id: int, slug: str) -> storage.QuickFilter:
    return storage.QuickFilter(quick_filter_id=filter_id, slug=slug, name=slug)


def create_core_quick_filter(quick_filter: storage.QuickFilter) -> dict:
    return {
        'id': quick_filter.quick_filter_id,
        'name': quick_filter.name,
        'slug': quick_filter.slug,
        'genitive': quick_filter.name,
        'sort': 100,
        'isEnabled': True,
        'isWizardEnabled': False,
    }


@pytest.mark.now('2021-03-15T15:00:00+00:00')
async def test_places(eats_catalog_storage, internal_places):
    open_places = []
    closed_places = []

    for place_id in range(10):
        slug = 'open_{}'.format(place_id)
        open_places.append(slug)
        places_utils.create_place(eats_catalog_storage, place_id, slug, False)

    for place_id in range(11, 20):
        slug = 'closed_{}'.format(place_id)
        closed_places.append(slug)
        places_utils.create_place(eats_catalog_storage, place_id, slug, True)

    response = await internal_places(
        [
            {'id': 'open', 'type': 'open'},
            {'id': 'closed', 'type': 'closed'},
            {'id': 'any', 'type': 'any'},
        ],
    )

    assert response.status_code == 200

    data = response.json()

    open_block = places_utils.find_block('open', data)
    for slug in open_places:
        places_utils.find_place_by_slug(slug, open_block)
    for slug in closed_places:
        places_utils.assert_no_slug(slug, open_block)

    closed_block = places_utils.find_block('closed', data)
    for slug in closed_places:
        places_utils.find_place_by_slug(slug, closed_block)
    for slug in open_places:
        places_utils.assert_no_slug(slug, closed_block)

    any_block = places_utils.find_block('any', data)
    for slug in closed_places:
        places_utils.find_place_by_slug(slug, any_block)
    for slug in open_places:
        places_utils.find_place_by_slug(slug, any_block)


@pytest.mark.now('2021-03-15T15:00:00+00:00')
async def test_places_single(eats_catalog_storage, internal_places):
    open_places = []
    closed_places = []

    for place_id in range(10):
        slug = 'open_{}'.format(place_id)
        open_places.append(slug)
        places_utils.create_place(eats_catalog_storage, place_id, slug, False)

    for place_id in range(11, 20):
        slug = 'closed_{}'.format(place_id)
        closed_places.append(slug)
        places_utils.create_place(eats_catalog_storage, place_id, slug, True)

    place_id = 1
    brand_id = 15

    response = await internal_places(
        [
            {
                'id': 'by_place',
                'type': 'any',
                'condition': {
                    'type': 'eq',
                    'init': {
                        'arg_name': 'place_id',
                        'arg_type': 'int',
                        'value': place_id,
                    },
                },
            },
            {
                'id': 'by_brand',
                'type': 'any',
                'condition': {
                    'type': 'eq',
                    'init': {
                        'arg_name': 'brand_id',
                        'arg_type': 'int',
                        'value': brand_id,
                    },
                },
            },
        ],
    )

    assert response.status_code == 200

    data = response.json()

    by_place_block = places_utils.find_block('by_place', data)
    places_utils.check_block_with_single_place(
        str(place_id), None, by_place_block,
    )

    by_brand_block = places_utils.find_block('by_brand', data)
    places_utils.check_block_with_single_place(
        None, str(brand_id), by_brand_block,
    )


@pytest.mark.now('2021-12-20T12:00:00+00:00')
@pytest.mark.parametrize('no_data', [False, True])
@pytest.mark.parametrize(
    'filters, filters_v2, expected_place_ids',
    [
        pytest.param(
            None, None, ['5', '4', '3', '2', '1'], id='no filters in request',
        ),
        pytest.param(
            [{'slug': 'burger', 'type': 'quickfilter'}],
            None,
            ['5', '4', '3', '2', '1'],
            id='filters_v1: common filter for all places',
        ),
        pytest.param(
            [{'slug': 'pizza', 'type': 'quickfilter'}],
            None,
            ['5', '4', '3', '2'],
            id='filters_v1: only pizza places',
        ),
        pytest.param(
            [{'slug': 'steak', 'type': 'quickfilter'}],
            None,
            ['5'],
            id='filters_v1: only steak places',
        ),
        pytest.param(
            [{'slug': 'unexpected', 'type': 'quickfilter'}],
            None,
            [],
            id='filters_v1: unexpected filter respond with no places',
        ),
        pytest.param(
            None,
            {
                'groups': [
                    {
                        'type': 'and',
                        'filters': [{'slug': 'steak', 'type': 'quickfilter'}],
                    },
                ],
            },
            ['5'],
            id='filters_v2: only steak places',
        ),
    ],
)
async def test_filters(
        eats_catalog_storage,
        internal_places,
        mockserver,
        filters: typing.Optional[list],
        filters_v2: typing.Optional[dict],
        expected_place_ids: typing.List[str],
        no_data: bool,
):
    """
    EDACAT-2247: проверят, что рестораны фильтруются быстрыми фильтрами.
    """

    burger_filter = create_quick_filter(filter_id=1, slug='burger')
    pizza_filter = create_quick_filter(filter_id=2, slug='pizza')
    sushi_filter = create_quick_filter(filter_id=3, slug='sushi')
    vegan_filter = create_quick_filter(filter_id=4, slug='vegan')
    steak_filter = create_quick_filter(filter_id=5, slug='steak')
    unexpected_filter = create_quick_filter(filter_id=6, slug='unexpected')
    quick_filters = [
        burger_filter,
        pizza_filter,
        sushi_filter,
        vegan_filter,
        steak_filter,
        unexpected_filter,
    ]

    @mockserver.json_handler('/eats-core/v1/export/quick-filters')
    def _core_quick_filters(request):
        payload = []
        for quick_filter in quick_filters:
            payload.append(create_core_quick_filter(quick_filter))

        return {'payload': payload}

    @dataclasses.dataclass
    class Place:
        place_id: int
        quick_filters: typing.List[storage.QuickFilter]

    places: typing.List[Place] = [
        Place(place_id=1, quick_filters=[burger_filter]),
        Place(place_id=2, quick_filters=[burger_filter, pizza_filter]),
        Place(
            place_id=3,
            quick_filters=[burger_filter, pizza_filter, sushi_filter],
        ),
        Place(
            place_id=4,
            quick_filters=[
                burger_filter,
                pizza_filter,
                sushi_filter,
                vegan_filter,
            ],
        ),
        Place(
            place_id=5,
            quick_filters=[
                burger_filter,
                pizza_filter,
                sushi_filter,
                vegan_filter,
                steak_filter,
            ],
        ),
    ]

    schedule = storage.WorkingInterval(
        start=parser.parse('2021-12-20T10:00:00+00:00'),
        end=parser.parse('2021-12-20T22:00:00+00:00'),
    )
    for place in places:
        place_id: int = place.place_id
        eats_catalog_storage.add_place(
            storage.Place(
                place_id=place_id,
                brand=storage.Brand(brand_id=place_id),
                slug=f'place_{place_id}',
                quick_filters=storage.QuickFilters(
                    general=place.quick_filters,
                ),
            ),
        )
        eats_catalog_storage.add_zone(
            storage.Zone(
                zone_id=place_id,
                place_id=place_id,
                working_intervals=[schedule],
            ),
        )

    block = {'id': 'open', 'type': 'open', 'no_data': no_data}
    location = {'longitude': 37.591503, 'latitude': 55.802998}

    response = await internal_places(
        blocks=[block],
        location=location,
        filters=filters,
        filters_v2=filters_v2,
    )
    assert response.status_code == 200

    block_id: str = str(block['id'])

    stats = places_utils.find_block_stats(block_id, response.json())
    assert stats['places_count'] == len(expected_place_ids)

    if no_data or not expected_place_ids:
        places_utils.assert_no_block_or_empty(block_id, response.json())
        return

    response_places = places_utils.find_block(block_id, response.json())

    assert len(expected_place_ids) == len(response_places)
    for expected_place_id, actual_place in zip(
            expected_place_ids, response_places,
    ):
        actual_place_id: int = actual_place['id']
        assert expected_place_id == actual_place_id


@pytest.mark.parametrize('enable_deduplication', [True, False])
@pytest.mark.parametrize(
    'surge_calls, ranking_calls',
    [
        pytest.param(1, 1, id='no experiment'),
        pytest.param(
            0,
            0,
            marks=(
                experiments.internal_places_deps_control(
                    disable_surge=True, disable_ranking=True,
                )
            ),
            id='all disabled',
        ),
        pytest.param(
            1,
            0,
            marks=(
                experiments.internal_places_deps_control(
                    disable_surge=False, disable_ranking=True,
                )
            ),
            id='ranking disabled',
        ),
        pytest.param(
            0,
            1,
            marks=(
                experiments.internal_places_deps_control(
                    disable_surge=True, disable_ranking=False,
                )
            ),
            id='surge disabled',
        ),
    ],
)
async def test_deps_control(
        internal_places,
        eats_catalog_storage,
        mockserver,
        surge,
        surge_calls,
        ranking_calls,
        enable_deduplication,
):
    def add_place_and_zone(
            eats_catalog_storage,
            place_id,
            business=storage.Business.Restaurant,
            couriers_type=storage.CouriersType.Pedestrian,
    ):
        place = storage.Place(
            place_id=place_id,
            slug=f'place_{place_id}',
            brand=storage.Brand(brand_id=place_id),
            business=business,
        )
        zone = storage.Zone(
            zone_id=place_id, place_id=place_id, couriers_type=couriers_type,
        )
        eats_catalog_storage.add_place(place)
        eats_catalog_storage.add_zone(zone)

    # если передаётся параметр дедубликации,
    # конфиг disable_ranking игнорируется
    if enable_deduplication:
        ranking_calls = 1

    add_place_and_zone(eats_catalog_storage, 1)
    add_place_and_zone(
        eats_catalog_storage, 2, couriers_type=storage.CouriersType.Vehicle,
    )
    add_place_and_zone(
        eats_catalog_storage, 3, couriers_type=storage.CouriersType.YandexTaxi,
    )
    add_place_and_zone(eats_catalog_storage, 4, business=storage.Business.Shop)
    add_place_and_zone(
        eats_catalog_storage, 5, business=storage.Business.Store,
    )

    @mockserver.json_handler('/umlaas-eats/umlaas-eats/v1/catalog')
    def ranking(request):
        return {
            'exp_list': [],
            'request_id': '',
            'provider': '',
            'available_blocks': [],
            'result': [],
        }

    response = await internal_places(
        enable_deduplication=enable_deduplication,
        blocks=[{'id': 'any', 'type': 'any', 'disable_filters': False}],
    )
    assert response.status_code == 200

    assert surge.times_called == surge_calls
    assert ranking.times_called == ranking_calls


@pytest.mark.now('2021-12-23T10:00:00+00:00')
@configs.eats_catalog_offer(empty_delivery_time_interval=30)
@pytest.mark.parametrize(
    'delivery_time, offer_match_time',
    (
        pytest.param('2021-12-23T10:29:00+00:00', None, id='asap'),
        pytest.param(
            '2021-12-23T10:30:00+00:00',
            '2021-12-23T10:30:00+00:00',
            id='preorder',
        ),
    ),
)
async def test_get_offer(
        internal_places,
        eats_catalog_storage,
        offers,
        delivery_time,
        offer_match_time,
):
    """
    Проверяем что если время в запросе попадает
    в интервал от сейчас до времени из конфига
    EATS_CATALOG_OFFERS, то в оферы уйдет null
    """
    eats_catalog_storage.add_place(
        storage.Place(
            place_id=1, timing=storage.PlaceTiming(average_preparation=60),
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(
            place_id=1,
            zone_id=1,
            working_intervals=[
                storage.WorkingInterval(
                    start=parser.parse('2021-12-23T09:00:00+00:00'),
                    end=parser.parse('2021-12-23T19:00:00+00:00'),
                ),
            ],
        ),
    )

    expected_request = {
        'need_prolong': True,
        'parameters': {'location': [37.591503, 55.802998]},
        'session_id': 'blablabla',
    }

    if offer_match_time:
        expected_request['parameters'].update(
            {'delivery_time': offer_match_time},
        )

    offers.match_request(expected_request)

    offers.match_response(
        status=404, body={'code': 'NOT_FOUND', 'message': 'not_found'},
    )

    response = await internal_places(
        blocks=[{'id': 'any', 'type': 'any', 'disable_filters': False}],
        time=delivery_time,
        headers={
            'x-device-id': 'test_simple',
            'x-platform': 'superapp_taxi_web',
            'x-app-version': '1.12.0',
            'X-Eats-User': 'user_id=123',
            'X-Eats-Session': 'blablabla',
        },
    )

    assert response.status_code == 200
    assert offers.match_times_called == 1
    assert offers.set_times_called == 1


ENABLE_DEDUPLICATION = experiments.enable_deduplication(
    consumer='eats-catalog-internal-places',
)


@pytest.mark.now('2022-05-14T01:54:40+03:00')
@experiments.internal_places_deps_control(
    disable_surge=True, disable_ranking=False,
)
@pytest.mark.parametrize(
    'expected_place_id',
    [
        pytest.param(3, id='old deduplication'),
        pytest.param(
            3,
            marks=ENABLE_DEDUPLICATION,
            id='new deduplication default config',
        ),
        pytest.param(
            4,
            marks=(
                ENABLE_DEDUPLICATION,
                experiments.deduplication(
                    priority_tag='best_place',
                    rules=['available', 'priority_tag'],
                    consumer='eats-catalog-internal-places',
                ),
            ),
            id='new deduplication available with tag',
        ),
        pytest.param(
            6,
            marks=(
                ENABLE_DEDUPLICATION,
                experiments.deduplication(
                    rules=['with_less_eta'],
                    consumer='eats-catalog-internal-places',
                ),
            ),
            id='new deduplication with_less_eta',
        ),
        pytest.param(
            5,
            marks=(
                ENABLE_DEDUPLICATION,
                experiments.deduplication(
                    rules=['available', 'with_less_eta'],
                    consumer='eats-catalog-internal-places',
                ),
            ),
            id='new deduplication available with_less_eta',
        ),
    ],
)
async def test_deduplication(
        eats_catalog_storage, internal_places, expected_place_id,
):
    schedule_enabled = [
        storage.WorkingInterval(
            start=parser.parse('2022-05-13T20:50:00+03:00'),
            end=parser.parse('2022-05-14T03:30:00+03:00'),
        ),
    ]
    schedule_disabled = [
        storage.WorkingInterval(
            start=parser.parse('2022-05-13T20:50:00+03:00'),
            end=parser.parse('2022-05-13T21:30:00+03:00'),
        ),
        storage.WorkingInterval(
            start=parser.parse('2022-05-14T02:50:00+03:00'),
            end=parser.parse('2022-05-14T03:30:00+03:00'),
        ),
    ]

    def add_place(
            place: storage.Place,
            enabled: bool = True,
            pedestrian: bool = True,
    ):
        couriers_type = storage.CouriersType.Pedestrian
        if not pedestrian:
            couriers_type = storage.CouriersType.YandexTaxi

        schedule = schedule_enabled
        if not enabled:
            schedule = schedule_disabled

        eats_catalog_storage.add_place(place)
        eats_catalog_storage.add_zone(
            storage.Zone(
                place_id=place['id'],
                zone_id=place['id'],
                working_intervals=schedule,
                couriers_type=couriers_type,
            ),
        )

    add_place(
        storage.Place(
            place_id=1,
            timing=storage.PlaceTiming(average_preparation=15 * 60),
            brand=storage.Brand(brand_id=1),
            tags=['best_place'],
        ),
        enabled=False,
    )

    add_place(
        storage.Place(
            place_id=2,
            timing=storage.PlaceTiming(average_preparation=60 * 60),
            brand=storage.Brand(brand_id=1),
        ),
    )

    add_place(
        storage.Place(
            place_id=3,
            timing=storage.PlaceTiming(average_preparation=20 * 60),
            brand=storage.Brand(brand_id=1),
        ),
    )

    add_place(
        storage.Place(
            place_id=4,
            timing=storage.PlaceTiming(average_preparation=60 * 60),
            brand=storage.Brand(brand_id=1),
            tags=['best_place'],
        ),
    )

    add_place(
        storage.Place(
            place_id=5,
            timing=storage.PlaceTiming(average_preparation=20 * 60),
            brand=storage.Brand(brand_id=1),
        ),
        pedestrian=False,
    )

    add_place(
        storage.Place(
            place_id=6,
            timing=storage.PlaceTiming(average_preparation=5 * 60),
            brand=storage.Brand(brand_id=1),
        ),
        enabled=False,
        pedestrian=False,
    )

    response = await internal_places(
        blocks=[{'id': 'any', 'type': 'any', 'disable_filters': False}],
        headers={
            'x-device-id': 'test_simple',
            'x-platform': 'superapp_taxi_web',
            'x-app-version': '1.12.0',
            'X-Eats-User': 'user_id=123',
            'X-Eats-Session': 'blablabla',
        },
    )

    assert response.status_code == 200

    response_places = places_utils.find_block('any', response.json())
    assert len(response_places) == 1

    response_place_ids = [place['id'] for place in response_places]
    assert str(expected_place_id) == response_place_ids[0]


@pytest.mark.parametrize(
    ('logos', 'logo_exist'),
    [
        pytest.param(
            [
                {'theme': 'dark', 'size': 'small'},
                {'theme': 'light', 'size': 'small'},
            ],
            True,
            id='Logos_exist',
        ),
        pytest.param(
            [{'theme': 'dark', 'size': 'small'}], False, id='Logos_not_exist',
        ),
        pytest.param([], False, id='Logos_empty'),
    ],
)
@pytest.mark.parametrize(
    ('colors', 'color_exist'),
    [
        pytest.param(
            [
                {'theme': 'dark', 'color': '#FFFFFF'},
                {'theme': 'light', 'color': '#000000'},
            ],
            True,
            id='Colors_exist',
        ),
        pytest.param(
            [{'theme': 'dark', 'color': '#FFFFFF'}],
            False,
            id='Colors_not_exist',
        ),
        pytest.param([], False, id='Colors_empty'),
    ],
)
@pytest.mark.now('2021-01-01T12:00:00+03:00')
async def test_internal_places_brand_colors_logos(
        internal_places,
        eats_catalog_storage,
        logos,
        colors,
        logo_exist,
        color_exist,
):
    """
        Проверка выдачи названия бренда, цветов и лого бренда при их наличии
        без перегрузки конфигом
    """
    brand_logos = [storage.BrandUILogo(**logo) for logo in logos]
    brand_backgrounds = [
        storage.BrandUIBackground(**color) for color in colors
    ]
    place_id = 1
    places_utils.create_place(
        eats_catalog_storage,
        place_id,
        'place_slug',
        False,
        storage.Features(
            brand_ui_logos=brand_logos, brand_ui_backgrounds=brand_backgrounds,
        ),
    )

    response = await internal_places(
        [
            {
                'id': 'by_place',
                'type': 'any',
                'condition': {
                    'type': 'eq',
                    'init': {
                        'arg_name': 'place_id',
                        'arg_type': 'int',
                        'value': place_id,
                    },
                },
            },
        ],
    )
    assert response.status_code == 200

    place = places_utils.find_place_by_slug(
        'place_slug', response.json()['blocks'][0]['list'],
    )
    brand = place['brand']

    assert brand['name'] == 'Тестовое заведение 1293'
    if color_exist:
        assert brand['color'] == {'light': '#000000', 'dark': '#FFFFFF'}
    else:
        assert 'color' not in brand

    expected_logos = {
        'dark': [
            {
                'size': 'small',
                'logo_url': (
                    'https://avatars.mds.yandex.net/get-eda/aaaaaa/214x140'
                ),
            },
        ],
        'light': [
            {
                'logo_url': (
                    'https://avatars.mds.yandex.net/get-eda/aaaaaa/214x140'
                ),
                'size': 'small',
            },
        ],
    }
    if logo_exist:
        assert brand['logo'] == expected_logos
    else:
        assert 'logo' not in brand


@pytest.mark.now('2021-01-01T12:00:00+03:00')
@ENABLE_OVERRIDES
async def test_internal_places_colors_logos_overriden(
        internal_places, eats_catalog_storage,
):
    """
        При наличии перегрузки цветов и лого экспериментом,
        выдаётся значение из конфига
    """
    brand_logos = [
        storage.BrandUILogo(theme='dark', size='small'),
        storage.BrandUILogo(theme='light', size='small'),
        storage.BrandUILogo(size='medium'),
    ]
    brand_backgrounds = [
        storage.BrandUIBackground('light', '#111000'),
        storage.BrandUIBackground('dark', '#FFFF00'),
    ]

    place_id = 1
    places_utils.create_place(
        eats_catalog_storage,
        place_id,
        'place_slug',
        False,
        storage.Features(
            brand_ui_logos=brand_logos, brand_ui_backgrounds=brand_backgrounds,
        ),
    )

    response = await internal_places(
        [
            {
                'id': 'by_place',
                'type': 'any',
                'condition': {
                    'type': 'eq',
                    'init': {
                        'arg_name': 'place_id',
                        'arg_type': 'int',
                        'value': place_id,
                    },
                },
            },
        ],
    )
    assert response.status_code == 200

    place = places_utils.find_place_by_slug(
        'place_slug', response.json()['blocks'][0]['list'],
    )
    brand = place['brand']

    assert brand['color'] == {'light': '#000000', 'dark': '#FFFFFF'}

    assert brand['logo'] == {
        'dark': [
            {
                'logo_url': (
                    'https://avatars.mds.yandex.net/get-eda/aaaaaa/214x140'
                ),
                'size': 'medium',
            },
            {'size': 'small', 'logo_url': 'dark_url'},
        ],
        'light': [{'logo_url': 'light_url', 'size': 'small'}],
    }


@pytest.mark.now('2021-01-01T12:00:00+03:00')
@pytest.mark.parametrize(
    'enable_overrides',
    [
        pytest.param(True, marks=ENABLE_OVERRIDES, id='Overrides enabled'),
        pytest.param(False, id='Overrides disabled'),
    ],
)
async def test_internal_places_empty_colors_logos_overriden(
        internal_places, eats_catalog_storage, enable_overrides,
):
    """
        Проверка на отсутствие лого и цвета в ответе.
        При наличии перегрузки цветов и лого конфигом,
         выдаётся значение из конфига иначе, поля отсутствуют
    """
    features = storage.Features(brand_ui_logos=[], brand_ui_backgrounds=[])

    place_id = 1
    places_utils.create_place(
        eats_catalog_storage, place_id, 'place_slug', False, features,
    )

    response = await internal_places(
        [
            {
                'id': 'by_place',
                'type': 'any',
                'condition': {
                    'type': 'eq',
                    'init': {
                        'arg_name': 'place_id',
                        'arg_type': 'int',
                        'value': place_id,
                    },
                },
            },
        ],
    )
    assert response.status_code == 200

    place = places_utils.find_place_by_slug(
        'place_slug', response.json()['blocks'][0]['list'],
    )
    brand = place['brand']

    if not enable_overrides:
        assert 'logo' not in brand
        assert 'color' not in brand
        return

    assert brand['color'] == {'light': '#000000', 'dark': '#FFFFFF'}

    assert brand['logo'] == {
        'dark': [{'size': 'small', 'logo_url': 'dark_url'}],
        'light': [{'logo_url': 'light_url', 'size': 'small'}],
    }
