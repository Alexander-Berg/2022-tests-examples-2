from dateutil import parser
import pytest

from testsuite.utils import matching

from eats_catalog import configs
from eats_catalog import experiments
from eats_catalog import storage
from . import utils


@pytest.mark.now('2021-01-01T12:00:00+03:00')
@configs.eats_catalog_rating_meta()
@experiments.TOP_RATING_TAG
@pytest.mark.parametrize(
    'expected_meta',
    [
        pytest.param(
            {
                'top_no_rating': {
                    'id': matching.UuidString(),
                    'type': 'rating',
                    'payload': {
                        'description': {
                            'color': [
                                {'theme': 'light', 'value': '#TOP000'},
                                {'theme': 'dark', 'value': '#TOP000'},
                            ],
                            'text': 'Рекомендуем',
                        },
                        'icon': {'color': [], 'uri': 'asset://flame'},
                        'icon_url': 'asset://flame',
                        'title': 'Рекомендуем',
                        'color': [
                            {'theme': 'light', 'value': '#TOP000'},
                            {'theme': 'dark', 'value': '#TOP000'},
                        ],
                    },
                },
                'top_with_rating': {
                    'id': matching.UuidString(),
                    'type': 'rating',
                    'payload': {
                        'description': {
                            'color': [
                                {'theme': 'light', 'value': '#TOP000'},
                                {'theme': 'dark', 'value': '#TOP000'},
                            ],
                            'text': '4.9',
                        },
                        'icon': {'color': [], 'uri': 'asset://flame'},
                        'icon_url': 'asset://flame',
                        'title': '4.9',
                        'color': [
                            {'theme': 'light', 'value': '#TOP000'},
                            {'theme': 'dark', 'value': '#TOP000'},
                        ],
                    },
                },
            },
            id='top enabled',
        ),
        pytest.param(
            {
                'top_no_rating': {
                    'id': matching.UuidString(),
                    'type': 'rating',
                    'payload': {
                        'description': {
                            'color': [
                                {'theme': 'light', 'value': '#NO0000'},
                                {'theme': 'dark', 'value': '#NO0000'},
                            ],
                            'text': 'Мало оценок',
                        },
                        'icon': {
                            'color': [
                                {'theme': 'light', 'value': '#NO0000'},
                                {'theme': 'dark', 'value': '#NO0000'},
                            ],
                            'uri': 'asset://no_rating_star',
                        },
                        'icon_url': 'asset://no_rating_star',
                        'title': 'Мало оценок',
                        'color': [
                            {'theme': 'light', 'value': '#NO0000'},
                            {'theme': 'dark', 'value': '#NO0000'},
                        ],
                    },
                },
                'top_with_rating': {
                    'id': matching.UuidString(),
                    'type': 'rating',
                    'payload': {
                        'description': {
                            'color': [
                                {'theme': 'light', 'value': '#NEW000'},
                                {'theme': 'dark', 'value': '#NEW000'},
                            ],
                            'text': 'Новый',
                        },
                        'icon': {
                            'color': [],
                            'uri': 'asset://rating_star_new',
                        },
                        'icon_url': 'asset://rating_star_new',
                        'title': 'Новый',
                        'color': [
                            {'theme': 'light', 'value': '#NEW000'},
                            {'theme': 'dark', 'value': '#NEW000'},
                        ],
                    },
                },
            },
            marks=experiments.DISABLE_TOP,
            id='top disabled',
        ),
    ],
)
async def test_rating_meta_top(
        taxi_eats_catalog, eats_catalog_storage, mockserver, expected_meta,
):
    eats_catalog_storage.add_place(
        storage.Place(
            slug='top_no_rating',
            place_id=1,
            brand=storage.Brand(brand_id=1),
            new_rating=storage.NewRating(show=False, count=201),
            location=storage.Location(lon=37.5916, lat=55.8129),
            price_category=storage.PriceCategory(value=0),
            address=storage.Address(city='Varadero'),
            tags=['top_rating'],
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(
            zone_id=11,
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

    eats_catalog_storage.add_place(
        storage.Place(
            slug='top_with_rating',
            place_id=5,
            brand=storage.Brand(brand_id=5),
            launched_at=parser.parse('2021-04-01T13:30:00+00:00'),  # new
            new_rating=storage.NewRating(show=True, rating=4.92, count=201),
            location=storage.Location(lon=37.59, lat=55.81),
            tags=['top_rating'],
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(
            zone_id=15,
            place_id=5,
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
            'X-Eats-Session': 'blablabla',
        },
        json={
            'bounding_box': [37, 55, 38, 56],
            'location': {'latitude': 55, 'longitude': 37},
            'zoom': 15,
        },
    )

    assert response.status_code == 200

    for place_slug, expected in expected_meta.items():
        place, map_pin = utils.find_place_by_slug(response.json(), place_slug)
        assert (
            utils.find_meta_in_place(place, 'rating') == expected
        ), place_slug
        assert utils.find_meta_in_map_pin(map_pin, 'rating') == expected
