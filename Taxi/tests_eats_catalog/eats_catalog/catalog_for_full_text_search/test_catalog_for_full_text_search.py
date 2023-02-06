from dateutil import parser
import pytest

from eats_catalog import configs
from eats_catalog import experiments
from eats_catalog import storage
from eats_catalog import translations
from . import search_utils


TRANSLATIONS = {'c4l.place_category.1': 'Завтраки'}


@pytest.mark.now('2021-07-05T14:14:00+03:00')
@experiments.USE_UMLAAS
@experiments.currency_sign('π')
@configs.eats_catalog_rating_meta()
@pytest.mark.parametrize(
    'by_region',
    [
        pytest.param(False, id='by location'),
        pytest.param(
            True,
            marks=(
                pytest.mark.eats_regions_cache(
                    [
                        {
                            'bbox': [
                                35.918658,
                                54.805858,
                                39.133684,
                                56.473673,
                            ],
                            'center': [37.591503, 55.802998],
                            'genitive': 'Moscow',
                            'id': 1,
                            'isAvailable': True,
                            'isDefault': True,
                            'name': 'Moscow',
                            'slug': 'moscow',
                            'sort': 1,
                            'timezone': 'Europe/Moscow',
                            'yandexRegionIds': [213, 216],
                            'country': {
                                'code': 'RU',
                                'id': 35,
                                'name': 'Российская Федерация',
                            },
                        },
                    ],
                )
            ),
            id='by region',
        ),
    ],
)
@translations.eats_catalog_ru(TRANSLATIONS)
async def test_delivery(
        mockserver,
        catalog_for_full_text_search,
        eats_catalog_storage,
        by_region,
):
    open_schedule = [
        storage.WorkingInterval(
            start=parser.parse('2021-07-05T10:00:00+03:00'),
            end=parser.parse('2021-07-05T18:00:00+03:00'),
        ),
    ]

    eats_catalog_storage.add_place(
        storage.Place(
            slug='delivery_open', place_id=1, brand=storage.Brand(brand_id=1),
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(zone_id=1, place_id=1, working_intervals=open_schedule),
    )

    eats_catalog_storage.add_place(
        storage.Place(
            slug='delivery_closed',
            place_id=2,
            brand=storage.Brand(brand_id=2),
            launched_at=parser.parse('2021-07-06T10:00:00+03:00'),  # new
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(
            zone_id=2,
            place_id=2,
            working_intervals=[
                storage.WorkingInterval(
                    start=parser.parse('2021-07-05T10:00:00+03:00'),
                    end=parser.parse('2021-07-05T13:00:00+03:00'),
                ),
            ],
        ),
    )

    eats_catalog_storage.add_place(
        storage.Place(
            slug='open_pickup_only',
            place_id=3,
            brand=storage.Brand(brand_id=3),
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(
            zone_id=3,
            place_id=3,
            shipping_type=storage.ShippingType.Pickup,
            working_intervals=open_schedule,
        ),
    )

    @mockserver.json_handler('/umlaas-eats/umlaas-eats/v1/catalog')
    def umlaas_eats(request):
        return {}

    if by_region:
        response = await catalog_for_full_text_search(
            shipping_type=storage.ShippingType.Delivery,
            longitude=None,
            latitude=None,
            region_id=1,
        )
    else:

        response = await catalog_for_full_text_search(
            shipping_type=storage.ShippingType.Delivery,
        )

    assert umlaas_eats.times_called == 1
    assert response.status == 200
    assert response.json() == {
        'blocks': [
            {
                'id': 'any',
                'stats': {'places_count': 2},
                'list': [
                    {
                        'availability': {
                            'available_to': '2021-07-05T18:00:00+03:00',
                            'is_available': True,
                        },
                        'brand': {'id': 1, 'slug': 'coffee_boy_euocq'},
                        'business': 'restaurant',
                        'currency': {'code': 'RUB', 'sign': '₽'},
                        'delivery': {'text': '25\u2009–\u200935 мин'},
                        'id': 1,
                        'name': 'Тестовое заведение 1293',
                        'picture': {
                            'ratio': 1.33,
                            'uri': (
                                '/images/1387779/'
                                '71876d2d734cf1c006ba-{w}x{h}.jpg'
                            ),
                        },
                        'price_category': {'name': 'πππ'},
                        'rating': {
                            'icon': {
                                'color': {
                                    'dark': '#GOOD00',
                                    'light': '#GOOD00',
                                },
                                'uri': 'asset://rating_star',
                            },
                            'text': '4.8 (123)',
                        },
                        'slug': 'delivery_open',
                        'tags': [{'name': 'Завтраки'}],
                    },
                    {
                        'availability': {'is_available': False},
                        'brand': {'id': 2, 'slug': 'coffee_boy_euocq'},
                        'business': 'restaurant',
                        'currency': {'code': 'RUB', 'sign': '₽'},
                        'delivery': {'text': 'Закрыто'},
                        'id': 2,
                        'name': 'Тестовое заведение 1293',
                        'picture': {
                            'ratio': 1.33,
                            'uri': (
                                '/images/1387779/'
                                '71876d2d734cf1c006ba-{w}x{h}.jpg'
                            ),
                        },
                        'price_category': {'name': 'πππ'},
                        'rating': {
                            'icon': {'uri': 'asset://rating_star_new'},
                            'text': 'Новый',
                        },
                        'slug': 'delivery_closed',
                        'tags': [{'name': 'Завтраки'}],
                    },
                ],
            },
        ],
    }


@pytest.mark.now('2021-07-05T14:14:00+03:00')
@experiments.USE_UMLAAS
@experiments.currency_sign('π')
@translations.eats_catalog_ru(TRANSLATIONS)
async def test_pickup(
        mockserver, catalog_for_full_text_search, eats_catalog_storage,
):
    open_schedule = [
        storage.WorkingInterval(
            start=parser.parse('2021-07-05T10:00:00+03:00'),
            end=parser.parse('2021-07-05T18:00:00+03:00'),
        ),
    ]

    eats_catalog_storage.add_place(
        storage.Place(
            slug='delivery_open', place_id=1, brand=storage.Brand(brand_id=1),
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(zone_id=1, place_id=1, working_intervals=open_schedule),
    )

    eats_catalog_storage.add_place(
        storage.Place(
            slug='open_pickup_only',
            place_id=3,
            brand=storage.Brand(brand_id=3),
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(
            zone_id=3,
            place_id=3,
            shipping_type=storage.ShippingType.Pickup,
            working_intervals=open_schedule,
        ),
    )

    @mockserver.json_handler('/umlaas-eats/umlaas-eats/v1/catalog')
    def umlaas_eats(request):
        return {}

    response = await catalog_for_full_text_search(
        shipping_type=storage.ShippingType.Pickup,
        blocks=[{'id': 'any', 'type': 'any'}],
    )

    assert umlaas_eats.times_called == 0
    assert response.status == 200
    assert response.json() == {
        'blocks': [
            {
                'id': 'any',
                'stats': {'places_count': 1},
                'list': [
                    {
                        'availability': {
                            'available_to': '2021-07-05T18:00:00+03:00',
                            'is_available': True,
                        },
                        'brand': {'id': 3, 'slug': 'coffee_boy_euocq'},
                        'business': 'restaurant',
                        'currency': {'code': 'RUB', 'sign': '₽'},
                        'delivery': {'text': '1.1 км'},
                        'id': 3,
                        'name': 'Тестовое заведение 1293',
                        'picture': {
                            'ratio': 1.33,
                            'uri': (
                                '/images/1387779/'
                                '71876d2d734cf1c006ba-{w}x{h}.jpg'
                            ),
                        },
                        'price_category': {'name': 'πππ'},
                        'rating': {
                            'icon': {
                                'color': {
                                    'dark': '#FAC220',
                                    'light': '#FAC220',
                                },
                                'uri': 'asset://rating_star',
                            },
                            'text': '4.8 (123)',
                        },
                        'slug': 'open_pickup_only',
                        'tags': [{'name': 'Завтраки'}],
                    },
                ],
            },
        ],
    }


@pytest.mark.parametrize(
    'expected_ids',
    [
        pytest.param({2, 4, 6}, id='no filter'),
        pytest.param(
            {1, 6},
            marks=(
                experiments.filter_source_response(
                    place_ids=[2], brand_ids=[2],
                )
            ),
            id='filter',
        ),
    ],
)
async def test_filter_source_response(
        catalog_for_full_text_search, eats_catalog_storage, expected_ids,
):
    """
    Проверяет применение эксперимента filter_source_response, который
    отфильтровывает заведения из выдачи при поиске
    """
    brand_id = 0
    for i in range(1, 7):
        brand_id += i % 2
        eats_catalog_storage.add_place(
            storage.Place(
                slug=f'place_{i}',
                place_id=i,
                brand=storage.Brand(brand_id=brand_id),
            ),
        )
        eats_catalog_storage.add_zone(
            storage.Zone(
                zone_id=i,
                place_id=i,
                shipping_type=storage.ShippingType.Delivery,
            ),
        )

    response = await catalog_for_full_text_search(
        shipping_type=storage.ShippingType.Delivery,
        blocks=[{'id': 'any', 'type': 'any', 'disable_filters': False}],
    )

    assert response.status_code == 200
    block = search_utils.find_block('any', response.json())

    place_ids = {place['id'] for place in block}

    assert expected_ids == place_ids


@experiments.DISABLE_ADVERTS
async def test_adverts_off_in_fts_any_blocks(
        catalog_for_full_text_search, eats_catalog_storage, yabs,
):
    """
    Проверяет, что эксперимент, отключающий рекламу, работает (любые блоки)
    """

    working_intervals = [
        storage.WorkingInterval(
            start=parser.parse('2022-03-21T09:00:00+03:00'),
            end=parser.parse('2022-03-21T23:00:00+03:00'),
        ),
    ]

    place_id: str = 1
    eats_catalog_storage.add_place(
        storage.Place(
            slug=f'place_{place_id}',
            place_id=place_id,
            brand=storage.Brand(brand_id=place_id),
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(
            zone_id=place_id,
            place_id=place_id,
            working_intervals=working_intervals,
        ),
    )

    response = await catalog_for_full_text_search(
        blocks=[
            {'id': 'adverts', 'type': 'open', 'advert_settings': {}},
            {'id': 'any', 'type': 'any'},
            {'id': 'any', 'type': 'open'},
        ],
    )
    assert response.status_code == 200
    assert yabs.times_called == 0

    blocks = response.json()['blocks']
    for block in blocks:
        for place in block['list']:
            assert 'advertisement' not in place
