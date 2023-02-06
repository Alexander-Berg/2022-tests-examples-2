import pytest

from testsuite.utils import ordered_object

from tests_eats_rest_menu_storage import definitions
from tests_eats_rest_menu_storage import models
import tests_eats_rest_menu_storage.menu_get.menu_response as menu_response

PLACE_ID = 1
BRAND_ID = 1
HANDLER = '/internal/v1/menu'
REQUEST = {'place_id': '1', 'shipping_types': ['delivery']}


@pytest.mark.pgsql('eats_rest_menu_storage', files=['fill_data.sql'])
async def test_menu_required_fields_category(
        taxi_eats_rest_menu_storage, eats_rest_menu_storage,
):
    """
        В этом тесте проверяется что все опциональные поля
        обрабатываются правильно и не возникает std::bad_optional
    """
    brand_ids = eats_rest_menu_storage.insert_brand_menu_categories(
        [
            models.BrandMenuCategory(
                brand_id=BRAND_ID,
                origin_id='origin_id_1',
                name='brand_name_1',
            ),
        ],
    )

    uuid = brand_ids[(BRAND_ID, 'origin_id_1')]

    eats_rest_menu_storage.insert_place_menu_categories(
        [
            models.PlaceMenuCategory(
                brand_menu_category_id=uuid,
                place_id=PLACE_ID,
                origin_id='origin_id_1',
                name='category_name_1',
            ),
        ],
    )

    expected_response = menu_response.MenuResponse(
        categories=[
            menu_response.Category(
                id=uuid,
                origin_id='origin_id_1',
                name='category_name_1',
                available=True,
            ),
        ],
    )

    response = await taxi_eats_rest_menu_storage.post(HANDLER, json=REQUEST)

    assert response.status_code == 200
    ordered_object.assert_eq(
        expected_response.as_dict(),
        response.json(),
        ['categories', 'categories.parent_ids', 'categories.pictures'],
    )


@pytest.mark.pgsql('eats_rest_menu_storage', files=['fill_data.sql'])
async def test_menu_all_fields_category(
        taxi_eats_rest_menu_storage, eats_rest_menu_storage,
):
    """
        В этом тесте проверяется что все поля отдаются правильно
    """
    brand_ids = eats_rest_menu_storage.insert_brand_menu_categories(
        [
            models.BrandMenuCategory(  # coalesce c полем name
                brand_id=BRAND_ID,
                origin_id='origin_id_1',
                name='brand_name_1',
            ),
            models.BrandMenuCategory(
                brand_id=BRAND_ID,
                origin_id='origin_id_2',
                name='brand_name_2',
            ),
        ],
    )

    ids = eats_rest_menu_storage.insert_place_menu_categories(
        [
            models.PlaceMenuCategory(
                brand_menu_category_id=brand_ids[(BRAND_ID, 'origin_id_1')],
                place_id=PLACE_ID,
                origin_id='origin_id_1',
            ),
            models.PlaceMenuCategory(
                brand_menu_category_id=brand_ids[(BRAND_ID, 'origin_id_2')],
                place_id=PLACE_ID,
                origin_id='origin_id_2',
                sort=20,
                legacy_id=2,
                name='category_name_2',
                synced_schedule=False,
                schedule=[{'day': 1, 'from': 0, 'to': 10}],
            ),
        ],
    )

    eats_rest_menu_storage.insert_category_relations(
        [
            models.CategoryRelation(
                place_id=1,
                category_id=ids[(PLACE_ID, 'origin_id_2')],
                parent_id=ids[(PLACE_ID, 'origin_id_1')],
            ),
        ],
    )
    eats_rest_menu_storage.insert_category_pictures(
        [
            models.CategoryPicture(
                place_menu_category_id=ids[(PLACE_ID, 'origin_id_2')],
                picture_id=1,
            ),
            models.CategoryPicture(
                place_menu_category_id=ids[(PLACE_ID, 'origin_id_2')],
                picture_id=2,
            ),
        ],
    )

    expected_response = menu_response.MenuResponse(
        categories=[
            menu_response.Category(
                id=brand_ids[(BRAND_ID, 'origin_id_1')],
                origin_id='origin_id_1',
                name='brand_name_1',
                available=True,
            ),
            menu_response.Category(
                id=brand_ids[(BRAND_ID, 'origin_id_2')],
                origin_id='origin_id_2',
                sort=20,
                legacy_id=2,
                name='category_name_2',
                pictures=[
                    definitions.Picture(url='url2', ratio=0.5),
                    definitions.Picture(url='url1', ratio=1),
                ],
                parent_ids=[brand_ids[(BRAND_ID, 'origin_id_1')]],
                available=False,  # из-за расписания
                schedule=[{'day': 1, 'from': 0, 'to': 10}],
            ),
        ],
    )

    response = await taxi_eats_rest_menu_storage.post(HANDLER, json=REQUEST)

    assert response.status_code == 200
    ordered_object.assert_eq(
        expected_response.as_dict(),
        response.json(),
        ['categories', 'categories.parent_ids', 'categories.pictures'],
    )


async def test_menu_categories_status(
        taxi_eats_rest_menu_storage, eats_rest_menu_storage, place_menu_db,
):
    db = place_menu_db(place_id=PLACE_ID, brand_id=BRAND_ID)
    db.add_category(
        models.PlaceMenuCategory(  # доступна потому что нет статуса
            brand_menu_category_id='',
            place_id=PLACE_ID,
            origin_id='origin_id_1',
        ),
    )
    category_2_id = db.add_category(
        models.PlaceMenuCategory(  # не доступна по статусу
            brand_menu_category_id='',
            place_id=PLACE_ID,
            origin_id='origin_id_2',
        ),
    )
    category_3_id = db.add_category(
        models.PlaceMenuCategory(  # удалена и доступна по статусу
            brand_menu_category_id='',
            place_id=PLACE_ID,
            origin_id='origin_id_3',
            deleted_at=models.DELETED_AT,
        ),
    )
    category_4_id = db.add_category(
        models.PlaceMenuCategory(  # доступна по статусу
            brand_menu_category_id='',
            place_id=PLACE_ID,
            origin_id='origin_id_4',
        ),
    )

    eats_rest_menu_storage.insert_category_statuses(
        [
            models.PlaceMenuCategoryStatus(
                place_menu_category_id=category_2_id,
                active=False,
                deleted=False,
            ),
            models.PlaceMenuCategoryStatus(
                place_menu_category_id=category_3_id,
                active=True,
                deleted=True,
            ),
            models.PlaceMenuCategoryStatus(
                place_menu_category_id=category_4_id,
                active=True,
                deleted=True,
            ),
        ],
    )

    response = await taxi_eats_rest_menu_storage.post(HANDLER, json=REQUEST)

    assert response.status_code == 200

    categories = list(
        sorted(response.json()['categories'], key=lambda x: x['origin_id']),
    )

    assert categories[0]['available'] is True
    assert categories[1]['available'] is False
    assert categories[2]['available'] is True


@pytest.mark.parametrize(
    'synced_schedule',
    (pytest.param(False, id='false'), pytest.param(True, id='true')),
)
async def test_return_synced_schedule(
        taxi_eats_rest_menu_storage, place_menu_db, synced_schedule,
):
    """
        В этом тесте проверяется что все поля отдаются правильно
    """
    schedule = [{'day': 1, 'from': 0, 'to': 10}]

    db = place_menu_db(BRAND_ID, PLACE_ID)
    db.add_category(
        models.PlaceMenuCategory(
            brand_menu_category_id='',
            place_id=PLACE_ID,
            origin_id='category_1',
            name='category_1',
            synced_schedule=synced_schedule,
            schedule=schedule,
        ),
    )

    response = await taxi_eats_rest_menu_storage.post(HANDLER, json=REQUEST)

    assert response.status_code == 200
    category = response.json()['categories'][0]

    if synced_schedule:
        assert 'schedule' not in category
    else:
        assert category['schedule'] == schedule
