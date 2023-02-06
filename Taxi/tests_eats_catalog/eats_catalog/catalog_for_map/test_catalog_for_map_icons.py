from dateutil import parser
import pytest

from eats_catalog import category
from eats_catalog import experiments
from eats_catalog import storage
from . import test_catalog_for_map as defs


@category.main(
    [
        category.MainCategory(place_id=1, name='Завтраки'),
        category.MainCategory(place_id=4, name='Детское меню'),
        category.MainCategory(place_id=50, name='Завтраки'),
        category.MainCategory(place_id=None, name='Завтраки'),
    ],
)
@pytest.mark.now('2021-01-01T12:00:00+03:00')
@pytest.mark.config(PLACE_CATEGORY_TO_ICON=defs.PLACE_CATEGORY_TO_ICON)
@experiments.ENABLE_FAVORITES
@experiments.SHOW_PLACE_CATEGORIES
async def test_catalog_for_map_icons(
        taxi_eats_catalog,
        mockserver,
        eats_catalog_storage,
        load_json,
        yt_apply,
):
    eats_catalog_storage.add_place(
        storage.Place(
            slug='open',
            place_id=1,
            brand=storage.Brand(brand_id=1),
            price_category=storage.PriceCategory(value=0),
            new_rating=storage.NewRating(rating=3.7, count=190),
            # custom icon lunch.jpg
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

    # Default icon for this place because it is not in cache
    eats_catalog_storage.add_place(
        storage.Place(
            slug='open_same_brand',
            place_id=3,
            brand=storage.Brand(brand_id=1),
            new_rating=storage.NewRating(rating=4.9, count=20),
            price_category=storage.PriceCategory(value=0),
            location=storage.Location(lon=37.5416, lat=55.2129),
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

    eats_catalog_storage.add_place(
        storage.Place(
            slug='open_another_brand',
            place_id=50,
            brand=storage.Brand(brand_id=151, slug='another_coffee_boy'),
            new_rating=storage.NewRating(rating=4.9, count=50),
            price_category=storage.PriceCategory(value=0),
            location=storage.Location(lon=37.4916, lat=55.8519),
            timing=storage.PlaceTiming(
                preparation=22 * 60, extra_preparation=10 * 60,
            ),
            # default.jpg icon, main category not found on the list
            categories=[storage.Category(321, 'Детское меню')],
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(
            zone_id=15,
            place_id=50,
            shipping_type=storage.ShippingType.Pickup,
            working_intervals=[
                storage.WorkingInterval(
                    start=parser.parse('2021-01-01T10:00:00+03:00'),
                    end=parser.parse('2021-01-01T14:00:00+03:00'),
                ),
            ],
        ),
    )

    @mockserver.json_handler(defs.REACTIONS_URL)
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

    response_json = response.json()

    assert (
        response_json['places'][0]['map_pin']['icon']['uri']
        == 'assets//default.jpg'
    )
    assert (
        response_json['places'][1]['map_pin']['icon']['uri']
        == 'assets://lunch.jpg'
    )
    assert (
        response_json['places'][2]['map_pin']['icon']['uri']
        == 'assets//default.jpg'
    )
