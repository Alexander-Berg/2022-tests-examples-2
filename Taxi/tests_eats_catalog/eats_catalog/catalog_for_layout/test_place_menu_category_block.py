from dateutil import parser
import pytest

from eats_catalog import storage
from . import layout_utils


WITH_CATEGORY_SLUG = 'with_category'
WITHOUT_CATEGORY_SLUG = 'without_category'
CATEGORY = 'my_category'
ANOTHER_CATEGORY = 'another_my_category'
PLACE_MENU_CATEGORY_TAG = 'my_category_tag'
PHOTOS = ['photo1']
LAVKA_DEEPLINK = f'eda.yandex://lavka?link=?category={CATEGORY}'
RETAIL_DEEPLINK = f'eda.yandex://shop/{WITH_CATEGORY_SLUG}?category={CATEGORY}'


@pytest.mark.now('2021-03-15T15:00:00+03:00')
@pytest.mark.config(
    EATS_CATALOG_PLACE_MENU_CATEGORY={
        'tags': {
            PLACE_MENU_CATEGORY_TAG: {
                'brand_categories': [
                    {'brand_id': 1, 'category': CATEGORY, 'photos': PHOTOS},
                ],
            },
        },
    },
)
@pytest.mark.parametrize(
    'available_categories',
    (
        pytest.param([], id='no available categories'),
        pytest.param([CATEGORY], id='category available'),
    ),
)
async def test_grocery_menu_category_block(
        catalog_for_layout,
        eats_catalog_storage,
        available_categories,
        mockserver,
):
    """
    Проверяем логику работы блока с диплинками на
    категории
    Проверяем, что в блок попадают только заведения
    из конфига с категориями
    Проверяем, что если категория недоступна в лавке,
    блок не формируется
    """

    lat = 55.802998
    lon = 37.591503

    eats_catalog_storage.add_place(
        storage.Place(
            place_id=1,
            brand=storage.Brand(brand_id=1),
            business=storage.Business.Store,
            slug=WITH_CATEGORY_SLUG,
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(
            zone_id=1,
            place_id=1,
            working_intervals=[
                storage.WorkingInterval(
                    start=parser.parse('2021-03-15T10:00:00+03:00'),
                    end=parser.parse('2021-03-15T22:00:00+03:00'),
                ),
            ],
        ),
    )

    eats_catalog_storage.add_place(
        storage.Place(
            place_id=2,
            brand=storage.Brand(brand_id=2),
            business=storage.Business.Shop,
            slug=WITHOUT_CATEGORY_SLUG,
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(
            zone_id=2,
            place_id=2,
            working_intervals=[
                storage.WorkingInterval(
                    start=parser.parse('2021-03-15T10:00:00+03:00'),
                    end=parser.parse('2021-03-15T22:00:00+03:00'),
                ),
            ],
        ),
    )

    @mockserver.json_handler(
        '/grocery-api/lavka/v1/api/v1/virtual-categories-availability',
    )
    def grocery_api(request):
        assert request.json['position']['location'] == [lon, lat]
        assert request.json['virtual_categories'] == [CATEGORY]
        return {'available_virtual_categories': available_categories}

    block_id = 'place_menu_category_block'

    response = await catalog_for_layout(
        blocks=[
            {
                'id': block_id,
                'type': 'place-menu-category',
                'place_menu_category_tag': PLACE_MENU_CATEGORY_TAG,
                'disable_filters': False,
            },
        ],
    )

    assert grocery_api.times_called == 1
    assert response.status == 200
    data = response.json()

    if available_categories:
        block = layout_utils.find_block(block_id, data)
        place = layout_utils.find_place_by_slug(WITH_CATEGORY_SLUG, block)

        assert place['payload']['link']['deeplink'] == LAVKA_DEEPLINK
        assert place['payload']['media']['photos'] == list(
            {'uri': photo} for photo in PHOTOS
        )

        layout_utils.assert_no_slug(WITHOUT_CATEGORY_SLUG, block)
    else:
        layout_utils.assert_no_block_or_empty(block_id, data)


@pytest.mark.now('2021-03-15T15:00:00+03:00')
@pytest.mark.config(
    EATS_CATALOG_PLACE_MENU_CATEGORY={
        'tags': {
            PLACE_MENU_CATEGORY_TAG: {
                'brand_categories': [
                    {'brand_id': 2, 'category': ANOTHER_CATEGORY},
                    {
                        'brand_id': 2,
                        'category': CATEGORY,
                        'photos': PHOTOS,
                        'priority': 100,
                    },
                ],
            },
        },
    },
)
@pytest.mark.parametrize(
    'available_categories',
    (
        pytest.param([], id='no available categories'),
        pytest.param([CATEGORY], id='category available'),
        pytest.param(
            [CATEGORY, ANOTHER_CATEGORY], id='both category available',
        ),
    ),
)
async def test_retail_menu_category_block(
        catalog_for_layout,
        eats_catalog_storage,
        available_categories,
        mockserver,
):
    """
    Проверяем логику работы блока с диплинками на
    категории
    Проверяем, что в блок попадают только заведения
    из конфига с категориями
    Проверяем, что если категория недоступна в номенклатуре,
    блок не формируется
    """

    eats_catalog_storage.add_place(
        storage.Place(
            place_id=1,
            brand=storage.Brand(brand_id=1),
            business=storage.Business.Store,
            slug=WITHOUT_CATEGORY_SLUG,
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(
            zone_id=1,
            place_id=1,
            working_intervals=[
                storage.WorkingInterval(
                    start=parser.parse('2021-03-15T10:00:00+03:00'),
                    end=parser.parse('2021-03-15T22:00:00+03:00'),
                ),
            ],
        ),
    )

    shop_id = 2
    eats_catalog_storage.add_place(
        storage.Place(
            place_id=shop_id,
            brand=storage.Brand(brand_id=2),
            business=storage.Business.Shop,
            slug=WITH_CATEGORY_SLUG,
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(
            zone_id=2,
            place_id=2,
            working_intervals=[
                storage.WorkingInterval(
                    start=parser.parse('2021-03-15T10:00:00+03:00'),
                    end=parser.parse('2021-03-15T22:00:00+03:00'),
                ),
            ],
        ),
    )

    @mockserver.json_handler('/eats-nomenclature/v1/places/categories')
    def nomenclature(request):
        req = request.json

        assert len(req['places_categories']) == 1
        assert req['places_categories'][0]['place_id'] == shop_id
        req_categories = req['places_categories'][0]['categories']
        assert sorted(req_categories) == sorted([CATEGORY, ANOTHER_CATEGORY])

        return {
            'places_categories': [
                {'place_id': shop_id, 'categories': available_categories},
            ],
        }

    block_id = 'place_menu_category_block'

    response = await catalog_for_layout(
        blocks=[
            {
                'id': block_id,
                'type': 'place-menu-category',
                'place_menu_category_tag': PLACE_MENU_CATEGORY_TAG,
                'disable_filters': False,
            },
        ],
    )

    assert nomenclature.times_called == 1
    assert response.status == 200
    data = response.json()

    if available_categories:
        block = layout_utils.find_block(block_id, data)
        place = layout_utils.find_place_by_slug(WITH_CATEGORY_SLUG, block)

        assert place['payload']['link']['deeplink'] == RETAIL_DEEPLINK
        assert place['payload']['media']['photos'] == list(
            {'uri': photo} for photo in PHOTOS
        )

        layout_utils.assert_no_slug(WITHOUT_CATEGORY_SLUG, block)
    else:
        layout_utils.assert_no_block_or_empty(block_id, data)
