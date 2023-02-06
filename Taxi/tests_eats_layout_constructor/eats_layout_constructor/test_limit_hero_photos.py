import pytest

from testsuite.utils import matching

# from static/test_limit_hero_photos/pg_eats_layout_constructor.sqp
HERO_PHOTOS_LIMIT = 2

DEFAULT_HERO_PHOTOS_LIMIT = 1


def get_photos(photos_count):
    return list([{'uri': f'/image_{photo}'} for photo in range(photos_count)])


def get_place_payload(num, photos_count, with_context: bool = False):
    return {
        'slug': f'id_{num}',
        'name': f'name_{num}',
        'media': {'photos': get_photos(photos_count)},
        'layout': [],
        'data': {},
        'context': matching.any_string if with_context else None,
    }


def get_places(place_count, photos_count):
    return list(
        [
            {
                'meta': {'place_id': place, 'brand_id': place},
                'payload': get_place_payload(place, photos_count),
            }
            for place in range(place_count)
        ],
    )


@pytest.mark.now('2020-05-07T11:30:00+0300')
@pytest.mark.experiments3(filename='eats_layout_places_carousels.json')
@pytest.mark.parametrize(
    'places_count,photos_count',
    [
        # 2 places with 1 photos for each place, expect no changes
        (2, 1),
        # 2 places with 3 photos for each place, expect only first two
        # photos for each place
        (2, 3),
        (6, 6),
    ],
)
@pytest.mark.config(
    EATS_LAYOUT_CONSTRUCTOR_EXPERIMENT_SETTINGS={
        'check_experiment': True,
        'refresh_period_ms': 1000,
        'experiment_name': 'eats_layout_template',
    },
)
async def test_limit_hero_photos(
        taxi_eats_layout_constructor, mockserver, places_count, photos_count,
):
    @mockserver.json_handler('/eats-catalog/internal/v1/catalog-for-layout')
    def _catalog(request):

        catalog_response = {
            'filters': {},
            'sort': {},
            'timepicker': [],
            'blocks': [],
        }
        for place_type in ('new', 'open'):
            catalog_response['blocks'].append(
                {
                    'id': place_type,
                    'type': place_type,
                    'list': get_places(places_count, photos_count),
                },
            )
        return catalog_response

    expected_photos_count = min(photos_count, HERO_PHOTOS_LIMIT)
    expected_layout = {
        'layout': [
            {
                'id': '1_places_carousel',
                'payload': {'title': 'Карусель'},
                'type': 'places_carousel',
            },
            {
                'id': '2_places_list',
                'payload': {'title': 'Список'},
                'type': 'places_list',
            },
        ],
        'data': {
            'places_carousels': [
                {
                    'id': '1_places_carousel',
                    'template_name': 'Widget template 1',
                    'payload': {
                        'places': [
                            get_place_payload(
                                place, expected_photos_count, True,
                            )
                            for place in range(places_count)
                        ],
                    },
                },
            ],
            'places_lists': [
                {
                    'id': '2_places_list',
                    'template_name': 'Widget template 2',
                    'payload': {
                        'places': [
                            get_place_payload(
                                place, expected_photos_count, True,
                            )
                            for place in range(places_count)
                        ],
                    },
                },
            ],
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
        json={'location': {'latitude': 0.0, 'longitude': 0.0}},
    )

    assert response.status_code == 200
    assert response.json() == expected_layout


@pytest.mark.now('2020-05-07T11:30:00+0300')
@pytest.mark.experiments3(filename='eats_layout_places_carousels.json')
@pytest.mark.parametrize('places_count,photos_count', [(2, 3)])
@pytest.mark.config(
    EATS_LAYOUT_CONSTRUCTOR_EXPERIMENT_SETTINGS={
        'check_experiment': True,
        'refresh_period_ms': 1000,
        'experiment_name': 'eats_layout_template',
    },
)
async def test_default_limit(
        taxi_eats_layout_constructor, mockserver, places_count, photos_count,
):
    @mockserver.json_handler('/eats-catalog/internal/v1/catalog-for-layout')
    def _catalog(request):

        catalog_response = {
            'filters': {},
            'sort': {},
            'timepicker': [],
            'blocks': [],
        }
        for place_type in ('new', 'open'):
            catalog_response['blocks'].append(
                {
                    'id': place_type,
                    'type': place_type,
                    'list': get_places(places_count, photos_count=3),
                },
            )
        return catalog_response

    expected_layout = {
        'layout': [
            {
                'id': '3_places_carousel',
                'payload': {'title': 'Карусель'},
                'type': 'places_carousel',
            },
            {
                'id': '4_places_list',
                'payload': {'title': 'Список'},
                'type': 'places_list',
            },
        ],
        'data': {
            'places_carousels': [
                {
                    'id': '3_places_carousel',
                    'template_name': 'Widget template 1',
                    'payload': {
                        'places': [
                            get_place_payload(
                                place, DEFAULT_HERO_PHOTOS_LIMIT, True,
                            )
                            for place in range(places_count)
                        ],
                    },
                },
            ],
            'places_lists': [
                {
                    'id': '4_places_list',
                    'template_name': 'Widget template 2',
                    'payload': {
                        'places': [
                            get_place_payload(
                                place, DEFAULT_HERO_PHOTOS_LIMIT, True,
                            )
                            for place in range(places_count)
                        ],
                    },
                },
            ],
        },
    }

    response = await taxi_eats_layout_constructor.post(
        'eats/v1/layout-constructor/v1/layout',
        headers={
            'x-device-id': 'dev_id',
            'x-platform': 'ios_app',  # another layout without limit
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
    assert response.json() == expected_layout
