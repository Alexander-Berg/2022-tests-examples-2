import base64
import json

from dateutil import parser
# pylint: disable=import-error
from eats_analytics import eats_analytics
import pytest

from eats_catalog import storage
from ..catalog_for_layout import layout_utils


def encode_place_context(context: dict) -> str:
    out: str = json.dumps(context, separators=(',', ':'))
    return base64.standard_b64encode(out.encode('utf-8')).decode('utf-8')


@pytest.mark.now('2021-01-01T12:00:00+03:00')
async def test_layout(taxi_eats_catalog, eats_catalog_storage):

    eats_catalog_storage.add_place(
        storage.Place(
            slug='open', place_id=3, brand=storage.Brand(brand_id=1),
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(
            zone_id=10,
            place_id=3,
            working_intervals=[
                storage.WorkingInterval(
                    start=parser.parse('2021-01-01T10:00:00+03:00'),
                    end=parser.parse('2021-01-01T14:00:00+03:00'),
                ),
                storage.WorkingInterval(
                    start=parser.parse('2021-01-02T10:00:00+03:00'),
                    end=parser.parse('2021-01-02T14:00:00+03:00'),
                ),
            ],
        ),
    )

    eats_catalog_storage.add_place(
        storage.Place(
            slug='open_same_brand',
            place_id=1,
            brand=storage.Brand(brand_id=1),
            price_category=storage.PriceCategory(value=0),
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(
            zone_id=11,
            place_id=1,
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

    response = await taxi_eats_catalog.post(
        '/eats-catalog/v1/layout',
        headers={
            'x-device-id': 'test_simple',
            'x-request-id': 'hello',
            'x-platform': 'superapp_taxi_web',
            'x-app-version': '1.12.0',
            'X-Eats-Session': 'blablabla',
            'cookie': 'just a cookie',
        },
        json={'location': {'longitude': 37.591503, 'latitude': 55.802998}},
    )

    assert eats_catalog_storage.search_times_called == 1
    assert response.status_code == 200
    photo = '/images/1387779/71876d2d734cf1c006ba-{w}x{h}.jpg'
    places = [
        {
            'name': 'Тестовое заведение 1293',
            'slug': 'open',
            'availability': {'is_available': True},
            'media': {'photos': [{'uri': photo}]},
            'brand': {
                'slug': 'coffee_boy_euocq',
                'name': 'COFFEE BOY',
                'business': 'restaurant',
            },
            'analytics': (
                layout_utils.MatchingAnalyticsContext(
                    eats_analytics.AnalyticsContext(
                        item_id='3',
                        item_name='Тестовое заведение 1293',
                        item_slug='open',
                        item_type=eats_analytics.ItemType.PLACE,
                        place_eta=eats_analytics.DeliveryEta(min=25, max=35),
                        place_business=eats_analytics.Business.RESTAURANT,
                    ),
                )
            ),
            'data': {
                'meta': [],
                'actions': [],
                'features': {
                    'delivery': {
                        'icons': ['asset://native_delivery'],
                        'text': '25\u2009–\u200935 мин',
                    },
                },
            },
            'layout': [],
            'context': encode_place_context(
                {
                    'place_id': 3,
                    'widget': {'id': '1_places_list', 'type': 'places_list'},
                },
            ),
        },
        {
            'name': 'Тестовое заведение 1293',
            'slug': 'closed',
            'availability': {'is_available': False},
            'media': {'photos': [{'uri': photo}]},
            'brand': {
                'slug': 'coffee_boy_euocq',
                'name': 'COFFEE BOY',
                'business': 'restaurant',
            },
            'analytics': (
                layout_utils.MatchingAnalyticsContext(
                    eats_analytics.AnalyticsContext(
                        item_id='2',
                        item_name='Тестовое заведение 1293',
                        item_slug='closed',
                        item_type=eats_analytics.ItemType.PLACE,
                        place_eta=eats_analytics.DeliveryEta(min=25, max=35),
                        place_business=eats_analytics.Business.RESTAURANT,
                    ),
                )
            ),
            'data': {
                'meta': [],
                'actions': [],
                'features': {
                    'delivery': {
                        'icons': ['asset://native_delivery'],
                        'text': 'Закрыто',
                    },
                },
            },
            'layout': [],
            'context': encode_place_context(
                {
                    'place_id': 2,
                    'widget': {'id': '1_places_list', 'type': 'places_list'},
                },
            ),
        },
    ]
    assert response.json() == {
        'data': {
            'places_lists': [
                {
                    'id': '1_places_list',
                    'template_name': 'PLACES_LIST',
                    'payload': {'places': places},
                },
            ],
        },
        'layout': [
            {'id': '1_places_list', 'type': 'places_list', 'payload': {}},
        ],
    }
