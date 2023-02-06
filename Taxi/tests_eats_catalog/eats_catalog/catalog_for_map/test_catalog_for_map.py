import math

from dateutil import parser
import pytest

from eats_catalog import category
from eats_catalog import experiments
from eats_catalog import storage
from eats_catalog import translations
from . import utils

REACTIONS_URL = (
    '/eats-user-reactions/eats-user-reactions/v1/favourites/find-by-eater'
)

TEXT_COLOR = [
    {'theme': 'light', 'value': '#NO0000'},
    {'theme': 'dark', 'value': '#NO0000'},
]
ICON_COLOR = [
    {'theme': 'light', 'value': '#NO0001'},
    {'theme': 'dark', 'value': '#NO0001'},
]


MAP_PIN_COLORS = {
    'pin_text': TEXT_COLOR,
    'pin_icon': ICON_COLOR,
    'badge_text': TEXT_COLOR,
    'badge_icon': ICON_COLOR,
}

PIN_SIZE_RANGES = {
    'adjacent_min_gap': 1.0,
    'hidden': {'min': 0, 'max': 14},
    'small': {'min': 11, 'max': 15},
    'medium': {'min': 13, 'max': 16},
    'large': {'min': 15, 'max': 17},
}
PREVIOUS_TYPE = dict(
    zip(list(PIN_SIZE_RANGES.keys())[1:], list(PIN_SIZE_RANGES.keys())[:-1]),
)

PLACE_SCORE_FORMULA = {
    '__default__': {
        'rating_min': 3.7844,
        'rating_max': 5,
        'count_min': 1,
        'count_max': 200,
        'count_threshold': 201,
        'left_formula': {
            'rating_mean': 4.668,
            'rating_std': 0.2408,
            'count_mean': 146.8327,
            'count_std': 60.5249,
            'intercept': 0.3908,
            'r1': 0.2668,
            'c1': 0.0695,
            'r2': 0.0519,
            'rc': 0.0602,
            'c2': -0.0147,
            'r3': 0.0022,
            'r2c': 0.0142,
            'rc2': -0.0145,
            'c3': 0.009,
            'r4': 0,
            'r3c': 0,
            'r2c2': 0,
            'rc3': 0,
            'c4': 0,
        },
        'right_formula': {
            'mean': 0,
            'std': 1,
            'intercept': 0,
            'x1': 0,
            'x2': 0,
            'x3': 0,
            'x4': 0,
        },
    },
    '1': {
        'rating_min': 3.1839,
        'rating_max': 5,
        'count_min': 1,
        'count_max': 200,
        'count_threshold': 200,
        'left_formula': {
            'rating_mean': 4.6621,
            'rating_std': 0.3563,
            'count_mean': 49.4074,
            'count_std': 54.2363,
            'intercept': 0.24275,
            'r1': 0.16238,
            'c1': 0.19748,
            'r2': 0.07737,
            'rc': 0.11888,
            'c2': -0.09358,
            'r3': 0.02372,
            'r2c': 0.02834,
            'rc2': -0.04083,
            'c3': 0.01534,
            'r4': 0.00269769,
            'r3c': 0.00269161,
            'r2c2': -0.00415742,
            'rc3': 0.004427948,
            'c4': -0.00017866,
        },
        'right_formula': {
            'mean': 4.7672,
            'std': 0.1861,
            'intercept': 0.5464278,
            'x1': 0.2930459,
            'x2': 0.0882626,
            'x3': 0.0117345,
            'x4': 0.0005628,
        },
    },
}

FAVORITES_FORMULA = {'favorites_scale': 2.0, 'favorites_bias': 0.0}

MAP_PIN_BADGE_ICONS = {'favorites': 'assets://favorites.jpg'}

ZOOM_CONSTRAINTS = {
    'percent_extra_size': 40,
    'min_zoom_level': 8,
    'max_zoom_level': 21,
}

PLACES_CLUSTERING = {
    'min_intercluster_distance': 30,
    'min_points_in_cluster': 2,
    'bucket_side_length': 1000,
}

MAP_RESPONSE_LIMITS = {
    'max_found_places': 200,
    'max_map_pins': 100,
    'max_clustered_points': 1000,
    'sorting_distance_gap': 100,
}

PLACE_CATEGORY_TO_ICON = {
    '123': 'assets://lunch.jpg',
    '321': 'assets://kids.jpg',
    '__default__': 'assets//default.jpg',
}


HEADERS = {
    'x-device-id': 'test_simple',
    'x-request-id': 'hello',
    'x-platform': 'superapp_taxi_web',
    'x-app-version': '1.12.0',
    'cookie': 'just a cookie',
    'x-eats-user': 'user_id=333',
    'X-Eats-Session': 'blablabla',
}


@pytest.mark.config(EATS_CATALOG_ZOOM_CONSTRAINT=ZOOM_CONSTRAINTS)
async def test_empty_response(taxi_eats_catalog, eats_catalog_storage):
    bounding_box = [37, 55, 38, 56]
    response = await taxi_eats_catalog.post(
        '/internal/v1/catalog-for-map',
        headers=HEADERS,
        json={
            'bounding_box': bounding_box,
            'location': {'latitude': 55, 'longitude': 37},
            'zoom': 10,
        },
    )

    assert eats_catalog_storage.search_bbox_times_called == 1
    assert response.status_code == 200

    zoom_range = {'max': ZOOM_CONSTRAINTS['max_zoom_level'], 'min': 9.51}
    response_json = response.json()

    assert utils.objects_approx_equal(response_json['zoom_range'], zoom_range)
    del response_json['zoom_range']

    assert response_json == {
        'bounding_box': [36.8, 54.8, 38.2, 56.2],
        'filters': {'list': []},
        'filters_v2': {'list': [], 'meta': {'selected_count': 0}},
        'places': [],
        'clusters': [],
        'timepicker': [],
    }


@pytest.mark.config(EATS_CATALOG_ZOOM_CONSTRAINT=ZOOM_CONSTRAINTS)
async def test_entire_world_response(taxi_eats_catalog, eats_catalog_storage):
    bounding_box = [37, 55, 38, 56]
    response = await taxi_eats_catalog.post(
        '/internal/v1/catalog-for-map',
        headers=HEADERS,
        json={
            'bounding_box': bounding_box,
            'location': {'latitude': 55, 'longitude': 37},
            'zoom': ZOOM_CONSTRAINTS['min_zoom_level'] - 1,
        },
    )

    assert eats_catalog_storage.search_bbox_times_called == 0
    assert response.status_code == 200

    assert response.json() == {
        'bounding_box': [-180.0, -90.0, 180.0, 90.0],
        'filters': {'list': []},
        'filters_v2': {'list': [], 'meta': {'selected_count': 0}},
        'places': [],
        'clusters': [],
        'timepicker': [],
        'zoom_range': {'max': ZOOM_CONSTRAINTS['min_zoom_level'], 'min': 0.0},
    }


BASIC_TRANSLATIONS = {
    'c4l.place_category.1': 'Завтраки',
    'c4l.place_category.123': 'Завтраки',
    'c4l.place_category.321': 'Детское меню',
}

TRANSLATIONS = {
    'map.pin.places_cluster_subtitle': 'Подзаголовок в кластере',
    'map.pin.places_cluster_title': 'Заголовок в кластере',
    'map.place_view.preparation_time': 'Готовят %(n_minutes)s минут',
    **BASIC_TRANSLATIONS,
}


@category.main(
    [
        category.MainCategory(place_id=1, name='Завтраки'),
        category.MainCategory(place_id=4, name='Детское меню'),
        category.MainCategory(place_id=50, name='Завтраки'),
        category.MainCategory(place_id=None, name='Завтраки'),
    ],
)
@pytest.mark.parametrize(
    'tanker_keys_present',
    [
        pytest.param(
            True,
            marks=[translations.eats_catalog_ru(TRANSLATIONS)],
            id='keys_present_in_keyset',
        ),
        pytest.param(
            False,
            marks=[translations.eats_catalog_ru(BASIC_TRANSLATIONS)],
            id='keys_absent_in_keyset',
        ),
    ],
)
@pytest.mark.now('2021-01-01T12:00:00+03:00')
@pytest.mark.config(EATS_CATALOG_MAP_PIN_COLORS=MAP_PIN_COLORS)
@pytest.mark.config(EATS_CATALOG_PIN_SIZE_RANGES=PIN_SIZE_RANGES)
@pytest.mark.config(EATS_CATALOG_ZOOM_CONSTRAINT=ZOOM_CONSTRAINTS)
@pytest.mark.config(EATS_CATALOG_PLACES_CLUSTERING=PLACES_CLUSTERING)
@pytest.mark.config(EATS_CATALOG_MAP_PIN_BADGE_ICONS=MAP_PIN_BADGE_ICONS)
@pytest.mark.config(PLACE_CATEGORY_TO_ICON=PLACE_CATEGORY_TO_ICON)
@experiments.ENABLE_FAVORITES
@experiments.SHOW_PLACE_CATEGORIES
@pytest.mark.experiments3(
    is_config=True,
    match={'predicate': {'init': {}, 'type': 'true'}, 'enabled': True},
    name='eats_catalog_badge',
    consumers=['eats-catalog-layout-badge'],
    clauses=[
        {
            'title': 'All',
            'value': {'text': 'Беееейдж'},
            'predicate': {
                'type': 'eq',
                'init': {
                    'arg_name': 'place_id',
                    'arg_type': 'int',
                    'value': 3,
                },
            },
        },
        {
            'title': 'Wrong',
            'value': {'text': 'Wrong place'},
            'predicate': {
                'type': 'eq',
                'init': {
                    'arg_name': 'place_id',
                    'arg_type': 'int',
                    'value': 1,
                },
            },
        },
    ],
    default_value={'text': 'Wrong text'},
)
async def test_catalog_for_map(
        taxi_eats_catalog,
        mockserver,
        eats_catalog_storage,
        load_json,
        tanker_keys_present,
        yt_apply,
):
    eats_catalog_storage.add_place(
        storage.Place(
            slug='open',
            place_id=1,
            brand=storage.Brand(brand_id=1),
            price_category=storage.PriceCategory(value=0),
            new_rating=storage.NewRating(show=True, rating=4.7, count=190),
            # custom icon lunch.jpg, since restaurant has a single category
            categories=[storage.Category(123, 'Завтраки')],
            location=storage.Location(lon=37.5916, lat=55.8129),
            address=storage.Address(short='Moscow'),
            timing=storage.PlaceTiming(
                preparation=5 * 60, extra_preparation=1 * 60,
            ),
            features=storage.Features(
                brand_ui_backgrounds=[
                    storage.BrandUIBackground(theme='light'),
                    storage.BrandUIBackground(theme='dark'),
                ],
                brand_ui_logos=[
                    storage.BrandUILogo(theme='light', url='http://light'),
                    storage.BrandUILogo(theme='dark', url='http://dark'),
                ],
            ),
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(
            zone_id=10,
            place_id=1,
            shipping_type=storage.ShippingType.Pickup,
            working_intervals=[
                storage.WorkingInterval(
                    start=parser.parse('2021-01-01T10:00:00+03:00'),
                    end=parser.parse('2021-01-01T14:00:00+03:00'),
                ),
            ],
        ),
    )

    # Omit place with the same brand and position as 1,
    # but different address, since it has `marketplace` type
    eats_catalog_storage.add_place(
        storage.Place(
            slug='open_same_brand_and_position',
            place_id=8,
            brand=storage.Brand(brand_id=1),
            new_rating=storage.NewRating(show=True, rating=4.7, count=190),
            location=storage.Location(lon=37.5916, lat=55.8129),
            address=storage.Address(short='Moscow, str.'),
            timing=storage.PlaceTiming(
                preparation=22 * 60, extra_preparation=0,
            ),
            place_type=storage.PlaceType.Marketplace,
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(
            zone_id=18,
            place_id=8,
            shipping_type=storage.ShippingType.Pickup,
            working_intervals=[
                storage.WorkingInterval(
                    start=parser.parse('2021-01-01T10:00:00+03:00'),
                    end=parser.parse('2021-01-01T14:00:00+03:00'),
                ),
            ],
        ),
    )

    # Places 3 and 4 share the same location
    centroid = storage.Location(lon=37.5, lat=55.8)

    eats_catalog_storage.add_place(
        storage.Place(
            slug='open_same_brand',
            place_id=3,
            brand=storage.Brand(brand_id=1),
            new_rating=storage.NewRating(show=True, rating=4.9, count=20),
            price_category=storage.PriceCategory(value=0),
            location=centroid,
            address=storage.Address(short='Varadero'),
            timing=storage.PlaceTiming(
                preparation=22 * 60, extra_preparation=0,
            ),
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(
            zone_id=11,
            place_id=3,
            shipping_type=storage.ShippingType.Pickup,
            working_intervals=[
                storage.WorkingInterval(
                    start=parser.parse('2021-01-01T10:00:00+03:00'),
                    end=parser.parse('2021-01-01T14:00:00+03:00'),
                ),
            ],
        ),
    )

    # Omit restaurant with the same brand and address,
    # albeit different position, as place #4,
    # but having lower score than 4
    eats_catalog_storage.add_place(
        storage.Place(
            slug='duplicate_same_brand',
            place_id=30,
            brand=storage.Brand(brand_id=1),
            new_rating=storage.NewRating(show=True, rating=4.5, count=20),
            price_category=storage.PriceCategory(value=0),
            location=storage.Location(lon=37.0, lat=55.0),
            address=storage.Address(short='Varadero'),
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(
            zone_id=15,
            place_id=30,
            shipping_type=storage.ShippingType.Pickup,
            working_intervals=[
                storage.WorkingInterval(
                    start=parser.parse('2021-01-01T10:00:00+03:00'),
                    end=parser.parse('2021-01-01T14:00:00+03:00'),
                ),
            ],
        ),
    )

    eats_catalog_storage.add_place(
        storage.Place(
            slug='open_favorite_brand',
            place_id=4,
            brand=storage.Brand(brand_id=101, slug='best_brand_ever'),
            new_rating=storage.NewRating(show=True, rating=4.9, count=50),
            price_category=storage.PriceCategory(value=0),
            location=centroid,
            timing=storage.PlaceTiming(
                preparation=22 * 60, extra_preparation=10 * 60,
            ),
            # kids icon
            categories=[
                storage.Category(123, 'Завтраки'),
                storage.Category(321, 'Детское меню'),
            ],
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(
            zone_id=14,
            place_id=4,
            shipping_type=storage.ShippingType.Pickup,
            working_intervals=[
                storage.WorkingInterval(
                    start=parser.parse('2021-01-01T10:00:00+03:00'),
                    end=parser.parse('2021-01-01T14:00:00+03:00'),
                ),
            ],
        ),
    )

    eats_catalog_storage.add_place(
        storage.Place(
            slug='closed', place_id=2, brand=storage.Brand(brand_id=2),
        ),
    )

    @mockserver.json_handler(REACTIONS_URL)
    def eats_user_reactions(request):
        assert request.json == {
            'eater_id': '333',
            'subject_namespaces': ['catalog_brand'],
            'pagination': {'limit': 1000},
        }
        return {
            'reactions': [
                {
                    'subject': {'namespace': 'catalog_brand', 'id': '101'},
                    'created_at': '2020-12-01T12:00:00+00:00',
                },
                {
                    'subject': {'namespace': 'catalog_brand', 'id': '2'},
                    'created_at': '2020-12-01T12:00:00+00:00',
                },
            ],
            'pagination': {'cursor': 'cursor', 'has_more': False},
        }

    bounding_box = [37, 55, 38, 56]

    response = await taxi_eats_catalog.post(
        '/internal/v1/catalog-for-map',
        headers={
            'x-device-id': 'test_simple',
            'x-request-id': 'hello',
            'x-platform': 'superapp_taxi_web',
            'x-app-version': '1.12.0',
            'cookie': 'just a cookie',
            'x-eats-user': 'user_id=333',
            'X-Eats-Session': 'blablabla',
        },
        json={
            'bounding_box': bounding_box,
            'location': {'latitude': 55, 'longitude': 37},
            'zoom': 15,
        },
    )

    assert eats_catalog_storage.search_bbox_times_called == 1
    assert eats_user_reactions.times_called == 1
    assert response.status_code == 200

    zoom_range = {'max': ZOOM_CONSTRAINTS['max_zoom_level'], 'min': 14.51}
    place_id_to_levels = {
        1: {'large': 15.52, 'medium': 14.05, 'small': 12.57},
        4: {'large': 15.27, 'medium': 13.55, 'small': 11.82},
        3: {'large': 15.81, 'medium': 14.61, 'small': 13.42},
    }

    response_json = response.json()

    assert utils.objects_approx_equal(response_json['zoom_range'], zoom_range)
    del response_json['zoom_range']

    for place in response_json['places']:
        place_id = place['place']['meta']['place_id']
        assert utils.objects_approx_equal(
            place['map_pin']['types_min_zoom_levels'],
            place_id_to_levels[place_id],
        )
        del place['map_pin']['types_min_zoom_levels']

    cluster = response_json['clusters'][0]
    assert set(cluster['place_slugs']) == {
        'open_same_brand',
        'open_favorite_brand',
    }
    del cluster['place_slugs']
    assert cluster['map_pin']['score'] == max(
        response_json['places'][1]['map_pin']['score'],
        response_json['places'][0]['map_pin']['score'],
    )
    assert utils.objects_approx_equal(
        cluster['map_pin']['types_min_zoom_levels'], {'small': 11.824},
    )
    del cluster['map_pin']['types_min_zoom_levels']

    cluster_loc = cluster['map_pin']['location']
    assert [cluster_loc['longitude'], cluster_loc['latitude']] == centroid[
        'geo_point'
    ]

    expected_json = load_json('expected_catalog_for_map_response.json')
    if not tanker_keys_present:
        expected_json['clusters'][0]['title'] = 'Здесь несколько ресторанов'
        del expected_json['clusters'][0]['subtitle']
        for place in expected_json['places']:
            del place['place']['payload']['data']['features']['badge']

    assert response_json == expected_json


@pytest.mark.now('2021-01-01T12:00:00+03:00')
@pytest.mark.config(EATS_CATALOG_PIN_SIZE_RANGES=PIN_SIZE_RANGES)
@experiments.ENABLE_FAVORITES
@pytest.mark.parametrize(
    'favorites_scale,favorites_bias',
    [
        pytest.param(2, 0.1, id='scale_and_shift'),
        pytest.param(0, 1, id='increase_up_to_max'),
    ],
)
async def test_increase_favorites_priority(
        taxi_eats_catalog,
        mockserver,
        eats_catalog_storage,
        taxi_config,
        favorites_scale,
        favorites_bias,
):
    taxi_config.set_values(
        dict(
            EATS_CATALOG_FAVORITES_FORMULA={
                'favorites_scale': favorites_scale,
                'favorites_bias': favorites_bias,
            },
            EATS_CATALOG_PLACE_FORMULA_BY_REGION=PLACE_SCORE_FORMULA,
        ),
    )
    ordinary_id, favorite_id = 1, 2
    new_rating = storage.NewRating(show=True, rating=4.7, count=100)

    eats_catalog_storage.add_place(
        storage.Place(
            slug='not_favorite_place',
            place_id=ordinary_id,
            brand=storage.Brand(brand_id=ordinary_id),
            price_category=storage.PriceCategory(value=0),
            new_rating=new_rating,
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(
            zone_id=10 + ordinary_id,
            place_id=ordinary_id,
            shipping_type=storage.ShippingType.Pickup,
            working_intervals=[
                storage.WorkingInterval(
                    start=parser.parse('2021-01-01T10:00:00+03:00'),
                    end=parser.parse('2021-01-01T14:00:00+03:00'),
                ),
            ],
        ),
    )

    eats_catalog_storage.add_place(
        storage.Place(
            slug='favorite_place',
            place_id=favorite_id,
            brand=storage.Brand(brand_id=favorite_id),
            price_category=storage.PriceCategory(value=0),
            new_rating=new_rating,
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(
            zone_id=10 + favorite_id,
            place_id=favorite_id,
            shipping_type=storage.ShippingType.Pickup,
            working_intervals=[
                storage.WorkingInterval(
                    start=parser.parse('2021-01-01T10:00:00+03:00'),
                    end=parser.parse('2021-01-01T14:00:00+03:00'),
                ),
            ],
        ),
    )

    @mockserver.json_handler(REACTIONS_URL)
    def eats_user_reactions(request):
        assert request.json == {
            'eater_id': '333',
            'subject_namespaces': ['catalog_brand'],
            'pagination': {'limit': 1000},
        }
        return {
            'reactions': [
                {
                    'subject': {
                        'namespace': 'catalog_brand',
                        'id': str(favorite_id),
                    },
                    'created_at': '2020-12-01T12:00:00+00:00',
                },
            ],
            'pagination': {'cursor': 'cursor', 'has_more': False},
        }

    response = await taxi_eats_catalog.post(
        '/internal/v1/catalog-for-map',
        headers={
            'x-device-id': 'test_simple',
            'x-request-id': 'hello',
            'x-platform': 'superapp_taxi_web',
            'x-app-version': '1.12.0',
            'cookie': 'just a cookie',
            'x-eats-user': 'user_id=333',
            'x-yataxi-session': 'eats:blablabla',
        },
        json={
            'bounding_box': [37, 55, 38, 56],
            'location': {'latitude': 55, 'longitude': 37},
            'zoom': 15,
        },
    )

    assert eats_catalog_storage.search_bbox_times_called == 1
    assert eats_user_reactions.times_called == 1
    assert response.status_code == 200

    response_json = response.json()
    id_to_place = {
        place['place']['meta']['place_id']: place
        for place in response_json['places']
    }

    ordinary_score = id_to_place[ordinary_id]['map_pin']['score'] / 1000
    favorite_score = id_to_place[favorite_id]['map_pin']['score'] / 1000
    assert favorite_score > ordinary_score
    expected_score = min(1, ordinary_score * favorites_scale + favorites_bias)
    assert math.isclose(favorite_score, expected_score, abs_tol=2e-2)

    for type_, level in id_to_place[favorite_id]['map_pin'][
            'types_min_zoom_levels'
    ].items():
        zmin = PIN_SIZE_RANGES[type_]['min']
        zmax = PIN_SIZE_RANGES[PREVIOUS_TYPE[type_]]['max']
        assert zmin <= level <= zmax
        assert math.isclose(
            favorite_score * (zmax - zmin), zmax - level, abs_tol=3e-3,
        )


@pytest.mark.now('2021-01-01T12:00:00+03:00')
@pytest.mark.config(EATS_CATALOG_MAP_RESPONSE_LIMITS=MAP_RESPONSE_LIMITS)
@pytest.mark.config(
    EATS_CATALOG_PLACES_CLUSTERING={
        'min_intercluster_distance': 30,
        'min_points_in_cluster': 2,
        'bucket_side_length': 100000,
    },
)
async def test_sort_places_in_response(
        taxi_eats_catalog, eats_catalog_storage,
):
    # place_id: {rating, position}
    places = {
        1: (
            4.5,
            [37.5, 55.7],
        ),  # 1 and 2 have the same rating, still 1 is closer to the user
        2: (4.5, [37.6, 55.7]),
        3: (
            4.0,
            [37.41, 55.61],
        ),  # 3 and 4 are the same distance away from user,
        # but 4 has higher rating than 3
        4: (4.9, [37.41, 55.61]),
        5: (
            4.5,
            [37, 55],
        ),  # places 6 and 5 are located at different distances from user
        # because of Mercator projection error
        6: (4.4, [37.8, 56.2]),
        # 7, 8, 9 are equally distant from user up to 100m precision,
        # threfore they are sorted by score
        7: (4.0, [36.9, 55]),
        8: (5.0, [36.9001, 55.0001]),
        9: (4.5, [36.9002, 55.0002]),
    }

    for id_, (rating, (lon, lat)) in places.items():
        eats_catalog_storage.add_place(
            storage.Place(
                slug=f'{id_}',
                place_id=id_,
                brand=storage.Brand(brand_id=id_),
                price_category=storage.PriceCategory(value=0),
                new_rating=storage.NewRating(rating=rating, count=100),
                location=storage.Location(lon=lon, lat=lat),
            ),
        )
        eats_catalog_storage.add_zone(
            storage.Zone(
                zone_id=1000 + id_,
                place_id=id_,
                shipping_type=storage.ShippingType.Pickup,
                working_intervals=[
                    storage.WorkingInterval(
                        start=parser.parse('2021-01-01T10:00:00+03:00'),
                        end=parser.parse('2021-01-01T14:00:00+03:00'),
                    ),
                ],
            ),
        )

    response = await taxi_eats_catalog.post(
        '/internal/v1/catalog-for-map',
        headers={
            'x-device-id': 'test_simple',
            'x-request-id': 'hello',
            'x-platform': 'superapp_taxi_web',
            'x-app-version': '1.12.0',
            'cookie': 'just a cookie',
            'x-eats-user': 'user_id=333',
            'x-yataxi-session': 'eats:blablabla',
        },
        json={
            'bounding_box': [37, 55, 38, 57],
            'location': {'longitude': 37.4, 'latitude': 55.6},
            'zoom': 15,
        },
    )

    assert eats_catalog_storage.search_bbox_times_called == 1
    assert response.status_code == 200

    response_json = response.json()
    assert [
        place['place']['meta']['place_id'] for place in response_json['places']
    ] == [4, 3, 1, 2, 6, 5, 8, 9, 7]


@pytest.mark.now('2021-01-01T12:00:00+03:00')
@pytest.mark.config(EATS_CATALOG_PLACE_FORMULA_BY_REGION=PLACE_SCORE_FORMULA)
@pytest.mark.config(EATS_CATALOG_FAVORITES_FORMULA=FAVORITES_FORMULA)
@experiments.ENABLE_FAVORITES
@pytest.mark.parametrize(
    'region_id, rating, count, score, is_favorite',
    [
        pytest.param(1, 4.5, 100, 266, False, id='moscow_left_tail'),
        pytest.param(1, 4.5, 200, 275, False, id='moscow_right_tail'),
        # For regions, not stated in config, default formula is used
        pytest.param(2, 4.5, 100, 196, False, id='non_existing_region'),
        pytest.param(
            2, 4.5, 100, 391, True, id='non_existing_region_favorite',
        ),
    ],
)
async def test_place_score_formula_by_region(
        taxi_eats_catalog,
        mockserver,
        eats_catalog_storage,
        region_id,
        rating,
        count,
        is_favorite,
        score,
):
    place_id, brand_id = 1, 11
    eats_catalog_storage.add_place(
        storage.Place(
            place_id=place_id,
            brand=storage.Brand(brand_id=brand_id),
            new_rating=storage.NewRating(rating=rating, count=count),
            price_category=storage.PriceCategory(value=0),
            location=storage.Location(lon=37.5, lat=55.8),
            region=storage.Region(region_id=region_id),
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(
            place_id=place_id,
            shipping_type=storage.ShippingType.Pickup,
            working_intervals=[
                storage.WorkingInterval(
                    start=parser.parse('2021-01-01T10:00:00+03:00'),
                    end=parser.parse('2021-01-01T14:00:00+03:00'),
                ),
            ],
        ),
    )

    @mockserver.json_handler(REACTIONS_URL)
    def eats_user_reactions(request):
        assert request.json == {
            'eater_id': '333',
            'subject_namespaces': ['catalog_brand'],
            'pagination': {'limit': 1000},
        }
        return {
            'reactions': (
                [
                    {
                        'subject': {
                            'namespace': 'catalog_brand',
                            'id': f'{brand_id}',
                        },
                        'created_at': '2020-12-01T12:00:00+00:00',
                    },
                ]
                if is_favorite
                else []
            ),
            'pagination': {'cursor': 'cursor', 'has_more': False},
        }

    response = await taxi_eats_catalog.post(
        '/internal/v1/catalog-for-map',
        headers={
            'x-device-id': 'test_simple',
            'x-request-id': 'hello',
            'x-platform': 'superapp_taxi_web',
            'x-app-version': '1.12.0',
            'cookie': 'just a cookie',
            'x-eats-user': 'user_id=333',
            'X-Eats-Session': 'blablabla',
        },
        json={
            'bounding_box': [37, 55, 38, 56],
            'location': {'latitude': 55, 'longitude': 37},
            'zoom': 15,
        },
    )

    assert eats_catalog_storage.search_bbox_times_called == 1
    assert eats_user_reactions.times_called == 1
    assert response.status_code == 200

    response_json = response.json()
    assert len(response_json['places']) == 1
    assert response_json['places'][0]['map_pin']['score'] == score


@pytest.mark.now('2021-01-01T12:00:00+03:00')
@pytest.mark.parametrize(
    'place_ids, chunks, max_places_in_request',
    [
        pytest.param(
            [0, 1, 2, 3, 4, 5, 6], [[0, 1, 2, 3], [4, 5, 6]], 4, id='multiple',
        ),
        pytest.param(
            [0, 1, 2, 3, 4, 5, 6],
            [[0, 1, 2, 3, 4, 5, 6]],
            10,
            id='limit_excceds_size',
        ),
        pytest.param([0, 1, 2], [[0], [1], [2]], 1, id='limit_equals_1'),
    ],
)
async def test_batch_eats_plus_requests(
        taxi_eats_catalog,
        eats_catalog_storage,
        mockserver,
        taxi_config,
        place_ids,
        chunks,
        max_places_in_request,
):
    taxi_config.set_values(
        dict(
            EATS_CATALOG_EATS_PLUS_SETTINGS={
                'max_places_in_request': max_places_in_request,
            },
        ),
    )

    number_of_requests = len(chunks)

    for id_ in place_ids:
        eats_catalog_storage.add_place(
            storage.Place(
                place_id=id_,
                brand=storage.Brand(brand_id=id_),
                location=storage.Location(lon=37.5, lat=55.8),
            ),
        )
        eats_catalog_storage.add_zone(
            storage.Zone(
                zone_id=id_,
                place_id=id_,
                shipping_type=storage.ShippingType.Pickup,
                working_intervals=[
                    storage.WorkingInterval(
                        start=parser.parse('2021-03-15T10:00:00+03:00'),
                        end=parser.parse('2021-03-15T22:00:00+03:00'),
                    ),
                ],
            ),
        )

    @mockserver.json_handler(
        '/eats-plus/internal/eats-plus/v1/presentation/cashback/places-list',
    )
    def eats_plus(request):
        place_ids = request.json['place_ids']
        # raises IndexError if place_ids have not been found in chunks
        nonlocal chunks
        chunks.pop(chunks.index(place_ids))
        return {
            'cashback': [
                {'place_id': id_, 'cashback': 7.8210} for id_ in place_ids
            ],
        }

    response = await taxi_eats_catalog.post(
        '/internal/v1/catalog-for-map',
        headers={
            'x-device-id': 'test_simple',
            'x-request-id': 'hello',
            'x-platform': 'superapp_taxi_web',
            'x-app-version': '1.12.0',
            'cookie': 'just a cookie',
            'x-eats-user': 'user_id=333',
            'X-Eats-Session': 'blablabla',
        },
        json={
            'bounding_box': [37, 55, 38, 56],
            'location': {'latitude': 55, 'longitude': 37},
            'zoom': 15,
        },
    )

    assert response.status_code == 200

    assert eats_plus.times_called == number_of_requests
    assert not chunks
