from dateutil import parser
import pytest

from eats_catalog import category
from eats_catalog import experiments
from eats_catalog import storage
from eats_catalog import translations
from . import test_catalog_for_map as defs
from . import utils


@category.main(
    [
        category.MainCategory(place_id=1, name='Завтраки'),
        category.MainCategory(place_id=4, name='Детское меню'),
        category.MainCategory(place_id=50, name='Завтраки'),
        category.MainCategory(place_id=None, name='Завтраки'),
    ],
)
@pytest.mark.now('2021-01-01T12:00:00+03:00')
@translations.eats_catalog_ru(defs.TRANSLATIONS)
@pytest.mark.config(EATS_CATALOG_MAP_PIN_COLORS=defs.MAP_PIN_COLORS)
@pytest.mark.config(EATS_CATALOG_PIN_SIZE_RANGES=defs.PIN_SIZE_RANGES)
@pytest.mark.config(EATS_CATALOG_ZOOM_CONSTRAINT=defs.ZOOM_CONSTRAINTS)
@pytest.mark.config(EATS_CATALOG_PLACES_CLUSTERING=defs.PLACES_CLUSTERING)
@pytest.mark.config(EATS_CATALOG_MAP_PIN_BADGE_ICONS=defs.MAP_PIN_BADGE_ICONS)
@pytest.mark.config(PLACE_CATEGORY_TO_ICON=defs.PLACE_CATEGORY_TO_ICON)
@experiments.ENABLE_FAVORITES
@experiments.SHOW_PLACE_CATEGORIES
@pytest.mark.experiments3(filename='eats_asset_to_image_tag.json')
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
async def test_catalog_for_superapp_map(
        taxi_eats_catalog,
        mockserver,
        eats_catalog_storage,
        load_json,
        taxi_config,
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
            # default icon, since restaurant has multiple categories
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

    taxi_config.set_values(
        {
            'EATS_CATALOG_MAP_SHORTCUT': load_json(
                'eats_catalog_map_shortcut.json',
            ),
        },
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
        '/internal/v1/catalog-for-superapp-map',
        headers=defs.HEADERS,
        json={
            'bounding_box': bounding_box,
            'location': {'latitude': 55, 'longitude': 37},
            'zoom': 15,
            'image_size_hint': 240,
        },
    )

    assert eats_catalog_storage.search_bbox_times_called == 1
    assert eats_user_reactions.times_called == 1
    assert response.status_code == 200

    assert utils.purge_object_of_uuids(response.json()) == load_json(
        'expected_superapp_map_response.json',
    )
