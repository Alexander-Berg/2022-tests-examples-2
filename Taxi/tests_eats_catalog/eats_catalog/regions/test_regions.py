from dateutil import parser
import pytest

from eats_catalog import experiments
from eats_catalog import storage

MOSCOW_BBOX = [35.918658, 54.805858, 39.133684, 56.473673]
MOSCOW_CENTER = [37.642806, 55.724266]

REGIONS = [
    {
        'bbox': MOSCOW_BBOX,
        'center': MOSCOW_CENTER,
        'genitive': 'Moscow',
        'id': 1,
        'isAvailable': True,
        'isDefault': True,
        'name': 'Moscow',
        'slug': 'moscow',
        'sort': 1,
        'timezone': 'Europe/Moscow',
        'yandexRegionIds': [],
        'country': {'code': 'RU', 'id': 35, 'name': 'Российская Федерация'},
    },
    {
        'bbox': [59.845338, 56.590871, 61.213136, 57.057719],
        'center': [60.597465, 56.838011],
        'genitive': 'Ekaterinburg',
        'id': 9,
        'isAvailable': True,
        'isDefault': False,
        'name': 'Ekaterinburg',
        'slug': 'ekaterinburg',
        'sort': 100,
        'timezone': 'Asia/Yekaterinburg',
        'yandexRegionIds': [],
        'country': {'code': 'RU', 'id': 35, 'name': 'Российская Федерация'},
    },
]


@pytest.mark.now('2021-08-07T17:40:00+03:00')
@pytest.mark.eats_regions_cache(REGIONS)
@pytest.mark.parametrize(
    'is_bbox_search',
    [
        pytest.param(
            False,
            marks=pytest.mark.config(
                EATS_CATALOG_REGIONS={
                    'show_empty_regions': False,
                    'search_by_bbox': False,
                },
            ),
            id='search by point',
        ),
        pytest.param(
            True,
            marks=pytest.mark.config(
                EATS_CATALOG_REGIONS={
                    'show_empty_regions': False,
                    'search_by_bbox': True,
                },
            ),
            id='search by bounding box',
        ),
    ],
)
async def test_regions(v1_regions, eats_catalog_storage, is_bbox_search):
    eats_catalog_storage.add_place(
        storage.Place(
            slug='moscow',
            place_id=1,
            quick_filters=storage.QuickFilters(
                general=[
                    storage.QuickFilter(quick_filter_id=1),
                    storage.QuickFilter(quick_filter_id=3),
                    storage.QuickFilter(quick_filter_id=5),
                ],
            ),
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(
            zone_id=1,
            place_id=1,
            working_intervals=[
                storage.WorkingInterval(
                    start=parser.parse('2021-08-07T10:00:00+03:00'),
                    end=parser.parse('2021-08-07T20:00:00+03:00'),
                ),
            ],
        ),
    )

    eats_catalog_storage.add_place(
        storage.Place(
            slug='other_moscow',
            place_id=2,
            quick_filters=storage.QuickFilters(
                general=[
                    storage.QuickFilter(quick_filter_id=3),
                    storage.QuickFilter(quick_filter_id=7),
                    storage.QuickFilter(quick_filter_id=13),
                ],
            ),
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(
            zone_id=2,
            place_id=2,
            working_intervals=[
                storage.WorkingInterval(
                    start=parser.parse('2021-08-07T10:00:00+03:00'),
                    end=parser.parse('2021-08-07T20:00:00+03:00'),
                ),
            ],
            polygon=storage.Polygon(),
        ),
    )

    eats_catalog_storage.add_place(
        storage.Place(
            slug='ekat',
            place_id=3,
            quick_filters=storage.QuickFilters(
                general=[
                    storage.QuickFilter(quick_filter_id=1),
                    storage.QuickFilter(quick_filter_id=3),
                    storage.QuickFilter(quick_filter_id=7),
                ],
            ),
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(
            zone_id=3,
            place_id=3,
            working_intervals=[
                storage.WorkingInterval(
                    start=parser.parse('2021-08-07T10:00:00+03:00'),
                    end=parser.parse('2021-08-07T20:00:00+03:00'),
                ),
            ],
            polygon=storage.Polygon(
                [
                    [60.57998657226562, 56.82643576192022],
                    [60.62187194824219, 56.82643576192022],
                    [60.62187194824219, 56.851975784517116],
                    [60.57998657226562, 56.851975784517116],
                    [60.57998657226562, 56.82643576192022],
                ],
            ),
        ),
    )

    eats_catalog_storage.add_place(
        storage.Place(
            slug='ekat_not_matching',
            place_id=4,
            quick_filters=storage.QuickFilters(
                general=[
                    storage.QuickFilter(quick_filter_id=3),
                    storage.QuickFilter(quick_filter_id=9),
                    storage.QuickFilter(quick_filter_id=13),
                ],
            ),
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(
            zone_id=4,
            place_id=4,
            working_intervals=[
                storage.WorkingInterval(
                    start=parser.parse('2021-08-07T10:00:00+03:00'),
                    end=parser.parse('2021-08-07T20:00:00+03:00'),
                ),
            ],
            polygon=storage.Polygon([[1, 1], (2, 1), (2, 2), (1, 2)]),
        ),
    )

    def search(request):
        if not is_bbox_search:
            point = request.json['geo_point']
            if point == MOSCOW_CENTER:
                return {
                    'ids': [
                        {'place_id': 1, 'zone_ids': [1]},
                        {'place_id': 2, 'zone_ids': [2]},
                    ],
                }
            return {'ids': [{'place_id': 3, 'zone_ids': [3]}]}

        assert 'bounding_box' in request.json
        assert request.json['shipping_type'] == 'delivery'

        print(request.json)
        if request.json['bounding_box'] == [
                [35.918658, 54.805858],
                [39.133684, 56.473673],
        ]:
            return {
                'places': [
                    {'id': 1, 'zone_ids': [1]},
                    {'id': 2, 'zone_ids': [2]},
                ],
            }
        return {'places': [{'id': 3, 'zone_ids': [3]}]}

    eats_catalog_storage.overide_search(search)

    response = await v1_regions()

    assert response.status == 200

    if is_bbox_search:
        assert eats_catalog_storage.search_bbox_times_called == 2
        assert eats_catalog_storage.search_times_called == 0
    else:
        assert eats_catalog_storage.search_bbox_times_called == 0

    data = response.json()

    order = [region['id'] for region in data['payload']]
    assert order == [1, 9]

    data = response.json()
    assert data == {
        'payload': [
            {
                'id': 1,
                'name': 'Moscow',
                'slug': 'moscow',
                'prepositional': 'Moscow',
                'isDefault': True,
                'countryId': 35,
                'bounding_box': MOSCOW_BBOX,
                'quickFilters': [
                    {
                        'id': 5,
                        'name': 'Суши',
                        'slug': 'sushi',
                        'genitive': 'суши и роллов',
                        'pictureUri': '/images/1368744.png',
                        'photoUri': '/images/1387779-{w}x{h}.jpg',
                        'promoPhotoUri': '/images/1387779-{w}x{h}.png',
                    },
                    {
                        'id': 3,
                        'name': 'Бургеры',
                        'slug': 'burger',
                        'genitive': 'бургеров',
                        'pictureUri': '/images/1370147.png',
                        'photoUri': '/images/1387779-{w}x{h}.jpg',
                        'promoPhotoUri': '/images/1380157-{w}x{h}.png',
                    },
                    {
                        'id': 7,
                        'name': 'Пицца',
                        'slug': 'pizza',
                        'genitive': 'пиццы',
                        'pictureUri': '/images/1370147.png',
                        'photoUri': '/images/1380157-{w}x{h}.jpg',
                        'promoPhotoUri': '/images/1387779-{w}x{h}.png',
                    },
                    {
                        'id': 13,
                        'name': 'Вегги',
                        'slug': 'vegetarian',
                        'genitive': 'вегетарианских блюд',
                        'pictureUri': '/images/1387779.png',
                        'photoUri': '/images/1387779-{w}x{h}.jpg',
                        'promoPhotoUri': '/images/1368744-{w}x{h}.png',
                    },
                ],
            },
            {
                'id': 9,
                'name': 'Ekaterinburg',
                'slug': 'ekaterinburg',
                'prepositional': 'Ekaterinburg',
                'isDefault': False,
                'countryId': 35,
                'bounding_box': [59.845338, 56.590871, 61.213136, 57.057719],
                'quickFilters': [
                    {
                        'id': 3,
                        'name': 'Бургеры',
                        'slug': 'burger',
                        'genitive': 'бургеров',
                        'pictureUri': '/images/1370147.png',
                        'photoUri': '/images/1387779-{w}x{h}.jpg',
                        'promoPhotoUri': '/images/1380157-{w}x{h}.png',
                    },
                    {
                        'id': 7,
                        'name': 'Пицца',
                        'slug': 'pizza',
                        'genitive': 'пиццы',
                        'pictureUri': '/images/1370147.png',
                        'photoUri': '/images/1380157-{w}x{h}.jpg',
                        'promoPhotoUri': '/images/1387779-{w}x{h}.png',
                    },
                ],
            },
        ],
    }


@pytest.mark.now('2021-08-12T19:04:00+03:00')
@pytest.mark.eats_regions_cache(REGIONS)
@pytest.mark.parametrize(
    'expected_order',
    [
        pytest.param([1], id='hide empty regions'),
        pytest.param(
            [1, 9],
            marks=pytest.mark.config(
                EATS_CATALOG_REGIONS={'show_empty_regions': True},
            ),
            id='show empty regions',
        ),
    ],
)
async def test_region_without_places(
        v1_regions, eats_catalog_storage, expected_order,
):
    def search(request):
        point = request.json['geo_point']
        if point == MOSCOW_CENTER:
            return {
                'ids': [
                    {'place_id': 1, 'zone_ids': [1]},
                    {'place_id': 2, 'zone_ids': [2]},
                ],
            }

        return {'ids': []}

    eats_catalog_storage.overide_search(search)
    eats_catalog_storage.add_place(
        storage.Place(
            slug='moscow',
            place_id=1,
            quick_filters=storage.QuickFilters(general=[]),
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(
            zone_id=1,
            place_id=1,
            working_intervals=[
                storage.WorkingInterval(
                    start=parser.parse('2021-08-12T00:00+03:00'),
                    end=parser.parse('2021-08-12T20:00:00+03:00'),
                ),
            ],
        ),
    )

    response = await v1_regions()
    assert response.status == 200

    data = response.json()

    for region in data['payload']:
        assert region['countryId'] == 35, 'countryId must be filled'

    order = [region['id'] for region in data['payload']]
    assert order == expected_order


@experiments.DISABLE_PREORDER
@pytest.mark.now('2022-02-14T09:35:00+03:00')
@pytest.mark.eats_regions_cache(
    [
        {
            'bbox': MOSCOW_BBOX,
            'center': [37.642806, 55.724266],
            'genitive': 'Moscow',
            'id': 1,
            'isAvailable': True,
            'isDefault': True,
            'name': 'Moscow',
            'slug': 'moscow',
            'sort': 1,
            'timezone': 'Europe/Moscow',
            'yandexRegionIds': [],
            'country': {
                'code': 'RU',
                'id': 35,
                'name': 'Российская Федерация',
            },
        },
    ],
)
async def test_region_with_preorder_disabled(v1_regions, eats_catalog_storage):
    """
    EDACAT-2474: проверяет, что в случае отключения предзаказа ручка
    по-прежнему возвращает список быстрых фильтров для региона
    """

    eats_catalog_storage.add_place(
        storage.Place(
            slug='moscow',
            place_id=1,
            quick_filters=storage.QuickFilters(
                general=[
                    storage.QuickFilter(quick_filter_id=1),
                    storage.QuickFilter(quick_filter_id=3),
                    storage.QuickFilter(quick_filter_id=5),
                ],
            ),
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(
            zone_id=1,
            place_id=1,
            working_intervals=[
                storage.WorkingInterval(
                    start=parser.parse('2022-02-14T08:00:00+03:00'),
                    end=parser.parse('2022-02-14T22:00:00+03:00'),
                ),
            ],
        ),
    )

    response = await v1_regions()
    assert response.status == 200

    data = response.json()
    assert len(data['payload']) == 1
    assert data['payload'][0]['quickFilters']
