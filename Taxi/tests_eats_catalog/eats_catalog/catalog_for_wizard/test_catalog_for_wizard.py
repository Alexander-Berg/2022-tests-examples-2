from dateutil import parser
import pytest

from eats_catalog import configs
from eats_catalog import storage


@pytest.mark.now('2021-10-13T14:32:00+03:00')
async def test_catalog_for_wizard(catalog_for_wizard, eats_catalog_storage):
    for place_id in range(1, 5):
        eats_catalog_storage.add_place(
            storage.Place(
                slug=f'place_{place_id}',
                name=f'Place {place_id}',
                place_id=place_id,
                brand=storage.Brand(brand_id=place_id),
                quick_filters=storage.QuickFilters(
                    general=[],
                    wizard=[
                        storage.QuickFilter(
                            quick_filter_id=17, slug='desert', name='Десерты',
                        ),
                        storage.QuickFilter(
                            quick_filter_id=21,
                            slug='breakfast',
                            name='Завтраки',
                        ),
                        storage.QuickFilter(
                            quick_filter_id=9,
                            slug='healthy',
                            name='Здоровая еда',
                        ),
                        storage.QuickFilter(
                            quick_filter_id=56, slug='coffe', name='Кофе',
                        ),
                        storage.QuickFilter(
                            quick_filter_id=61, slug='lunch', name='Ланчи',
                        ),
                    ],
                ),
            ),
        )
        eats_catalog_storage.add_zone(
            storage.Zone(
                zone_id=place_id,
                place_id=place_id,
                working_intervals=[
                    storage.WorkingInterval(
                        start=parser.parse('2021-10-13T10:00:00+03:00'),
                        end=parser.parse('2021-10-13T17:00:00+03:00'),
                    ),
                ],
            ),
        )

    response = await catalog_for_wizard(limit=3)

    assert response.status_code == 200

    data = response.json()

    assert data['payload'] == [
        {
            'id': 'AQEBbAn5oGczE0AZAAAAAAAAAA',
            'name': 'Place 1',
            'priceCategory': '₽₽₽',
            'picture': 'https://avatars.mds.yandex.net/get-eda/h/214x140',
            'tags': ['Завтраки'],
            'url': 'https://eda.yandex.ru/restaurant/place_1',
            'deliveryTime': {'min': 25, 'max': 35},
            'rating': 4.8,
        },
        {
            'id': 'AQECbAn5oGczE0AZAAAAAAAAAA',
            'name': 'Place 2',
            'priceCategory': '₽₽₽',
            'picture': 'https://avatars.mds.yandex.net/get-eda/h/214x140',
            'tags': ['Завтраки'],
            'url': 'https://eda.yandex.ru/restaurant/place_2',
            'deliveryTime': {'min': 25, 'max': 35},
            'rating': 4.8,
        },
        {
            'id': 'AQEDbAn5oGczE0AZAAAAAAAAAA',
            'name': 'Place 3',
            'priceCategory': '₽₽₽',
            'picture': 'https://avatars.mds.yandex.net/get-eda/h/214x140',
            'tags': ['Завтраки'],
            'url': 'https://eda.yandex.ru/restaurant/place_3',
            'deliveryTime': {'min': 25, 'max': 35},
            'rating': 4.8,
        },
    ]

    assert data['meta']['count'] == 4
    assert data['meta']['hasMore']
    assert set(data['meta']['quickFilters']) == set([9, 17, 21])

    cursor = data['payload'][-1]['id']
    response = await catalog_for_wizard(limit=1, after=cursor)

    assert response.status_code == 200

    data = response.json()

    assert data['payload'] == [
        {
            'id': 'AQEEbAn5oGczE0AZAAAAAAAAAA',
            'name': 'Place 4',
            'priceCategory': '₽₽₽',
            'picture': 'https://avatars.mds.yandex.net/get-eda/h/214x140',
            'tags': ['Завтраки'],
            'url': 'https://eda.yandex.ru/restaurant/place_4',
            'deliveryTime': {'min': 25, 'max': 35},
            'rating': 4.8,
        },
    ]

    assert data['meta']['count'] == 4
    assert not data['meta']['hasMore']
    assert set(data['meta']['quickFilters']) == set([9, 17, 21])

    # Past the end
    cursor = data['payload'][-1]['id']
    response = await catalog_for_wizard(limit=100, after=cursor)

    assert response.status_code == 200

    data = response.json()
    assert data['payload'] == []

    assert data['meta']['count'] == 4
    assert not data['meta']['hasMore']
    assert set(data['meta']['quickFilters']) == set([9, 17, 21])


@pytest.mark.now('2021-10-13T14:32:00+03:00')
async def test_by_eta(catalog_for_wizard, eats_catalog_storage):
    max_preparation = 50

    for place_id in range(1, 5):
        eats_catalog_storage.add_place(
            storage.Place(
                slug=f'place_{place_id}',
                name=f'Place {place_id}',
                place_id=place_id,
                brand=storage.Brand(brand_id=place_id),
                timing=storage.PlaceTiming(
                    average_preparation=(max_preparation - place_id * 10) * 60,
                ),
            ),
        )
        eats_catalog_storage.add_zone(
            storage.Zone(
                zone_id=place_id,
                place_id=place_id,
                working_intervals=[
                    storage.WorkingInterval(
                        start=parser.parse('2021-10-13T10:00:00+03:00'),
                        end=parser.parse('2021-10-13T17:00:00+03:00'),
                    ),
                ],
            ),
        )

    response = await catalog_for_wizard()
    assert response.status_code == 200

    data = response.json()
    names = [place['name'] for place in data['payload']]
    times = [place['deliveryTime']['min'] for place in data['payload']]

    assert names == ['Place 4', 'Place 3', 'Place 2', 'Place 1']
    assert times == [25, 35, 45, 55]

    response = await catalog_for_wizard(after=data['payload'][-2]['id'])
    assert response.status_code == 200

    data = response.json()
    names = [place['name'] for place in data['payload']]

    assert names == ['Place 1']


@pytest.mark.now('2021-10-13T14:32:00+03:00')
@configs.wizard_settings(
    default_position={'longitude': 37.591503, 'latitude': 55.802998},
)
async def test_by_rating(catalog_for_wizard, eats_catalog_storage):

    for place_id in range(1, 5):
        eats_catalog_storage.add_place(
            storage.Place(
                slug=f'place_{place_id}',
                name=f'Place {place_id}',
                place_id=place_id,
                brand=storage.Brand(brand_id=place_id),
                new_rating=storage.NewRating(rating=place_id % 2),
            ),
        )
        eats_catalog_storage.add_zone(
            storage.Zone(
                zone_id=place_id,
                place_id=place_id,
                working_intervals=[
                    storage.WorkingInterval(
                        start=parser.parse('2021-10-13T10:00:00+03:00'),
                        end=parser.parse('2021-10-13T17:00:00+03:00'),
                    ),
                ],
            ),
        )

    response = await catalog_for_wizard(lon=None, lat=None)
    assert response.status_code == 200

    data = response.json()
    names = [place['name'] for place in data['payload']]
    ratings = [place['rating'] for place in data['payload']]

    assert ratings == [1, 1, 0, 0]
    assert names == ['Place 1', 'Place 3', 'Place 2', 'Place 4']

    response = await catalog_for_wizard(
        lon=None, lat=None, after=data['payload'][-2]['id'],
    )
    assert response.status_code == 200

    data = response.json()
    names = [place['name'] for place in data['payload']]

    assert names == ['Place 4']


@pytest.mark.now('2021-10-13T14:32:00+03:00')
@pytest.mark.parametrize(
    ['filter_id', 'place_names'],
    [
        pytest.param(1, set(['Place 1', 'Place 3']), id='enabled'),
        pytest.param(
            2,
            set(['Place 1', 'Place 2', 'Place 3', 'Place 4']),
            id='disabled',
        ),
    ],
)
async def test_filter(
        mockserver,
        catalog_for_wizard,
        eats_catalog_storage,
        filter_id,
        place_names,
):
    @mockserver.json_handler('/eats-core/v1/export/quick-filters')
    def _eats_core(_):
        return {
            'payload': [
                {
                    'categoryId': None,
                    'genitive': 'специальные предложения и акции',
                    'id': 1,
                    'isEnabled': False,
                    'isWizardEnabled': True,
                    'name': 'Акции',
                    'photoURI': '',
                    'pictureURI': '/images/1370147.png',
                    'promoPhotoURI': '',
                    'slug': 'akcii',
                    'sort': 10000,
                },
                {
                    'categoryId': None,
                    'genitive': 'специальные предложения и акции',
                    'id': 2,
                    'isEnabled': True,
                    'isWizardEnabled': False,
                    'name': 'Акции',
                    'photoURI': '',
                    'pictureURI': '/images/1370147.png',
                    'promoPhotoURI': '',
                    'slug': 'akcii',
                    'sort': 10000,
                },
            ],
        }

    for place_id in range(1, 5):
        eats_catalog_storage.add_place(
            storage.Place(
                slug=f'place_{place_id}',
                name=f'Place {place_id}',
                place_id=place_id,
                brand=storage.Brand(brand_id=place_id),
                new_rating=storage.NewRating(rating=place_id % 2),
                quick_filters=storage.QuickFilters(
                    general=[],
                    wizard=[
                        storage.QuickFilter(
                            quick_filter_id=place_id % 2,
                            slug='filter',
                            name='filter',
                        ),
                    ],
                ),
            ),
        )
        eats_catalog_storage.add_zone(
            storage.Zone(
                zone_id=place_id,
                place_id=place_id,
                working_intervals=[
                    storage.WorkingInterval(
                        start=parser.parse('2021-10-13T10:00:00+03:00'),
                        end=parser.parse('2021-10-13T17:00:00+03:00'),
                    ),
                ],
            ),
        )

    response = await catalog_for_wizard(quick_filter_id=filter_id)
    assert response.status_code == 200

    data = response.json()
    names = set(place['name'] for place in data['payload'])

    assert names == place_names
