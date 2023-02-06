import datetime as dt
import typing

from dateutil import parser
import psycopg2
import psycopg2.tz
import pytest
import pytz

from testsuite.utils import matching

from tests_eats_rest_menu_storage import models
from tests_eats_rest_menu_storage import sql
from tests_eats_rest_menu_storage.menu_update import handler

HANDLER = '/internal/v1/update/menu'
BRAND_ID = 1
PLACE_ID = 1

REACTIVATE_AT = parser.parse(timestr='2022-01-11T14:58:46+03:00')
TZINFO = psycopg2.tz.FixedOffsetTimezone(offset=180, name=None)
CREATED_AT = dt.datetime(2020, 1, 1, 1, 1, 1, tzinfo=TZINFO)
UPDATED_AT = dt.datetime(2021, 1, 1, 1, 1, 1, tzinfo=TZINFO)
DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S%z'

# TODO(udalovmax):
#
# Здесь не хватает тестов, т.к. большая часть из них требует фикстур для
# вставки данных в БД.
#
# 1. Добавить тест на удаление связи категорий.
# 2. Добавить тест на апдейт категории.
# 3. Добавить тест на апдейт категории, который не затрагивает существующие
#    категории.
# 4. Добавить тест на добавление/обновление изображений категорий.


@pytest.fixture(name='setup_brand_and_place')
def _setup_brand_and_place(database):
    sql.insert_brand(database, BRAND_ID)
    sql.insert_place(
        database,
        models.Place(
            place_id=PLACE_ID, brand_id=BRAND_ID, slug=f'place_{PLACE_ID}',
        ),
    )


@pytest.mark.parametrize(
    'update_categories, expected_place_categories, expected_brand_categories',
    [
        pytest.param([], [], [], id='empty categories'),
        pytest.param(
            [
                handler.UpdateCategory(
                    origin_id='1',
                    name='testsuite',
                    available=False,
                    updated_at=UPDATED_AT.strftime(DATETIME_FORMAT),
                ),
            ],
            [
                models.PlaceMenuCategory(
                    brand_menu_category_id=matching.any_string,
                    place_id=PLACE_ID,
                    origin_id='1',
                    category_id='1',
                    name=None,
                    updated_at=UPDATED_AT.strftime(DATETIME_FORMAT),
                ),
            ],
            [
                models.BrandMenuCategory(
                    brand_id=BRAND_ID, origin_id='1', name='testsuite',
                ),
            ],
            id='insert single category',
        ),
        pytest.param(
            [
                handler.UpdateCategory(
                    origin_id='1',
                    name='testsuite_1',
                    available=False,
                    updated_at=UPDATED_AT.strftime(DATETIME_FORMAT),
                ),
                handler.UpdateCategory(
                    origin_id='2',
                    name='testsuite_2',
                    deleted_at=UPDATED_AT.strftime(DATETIME_FORMAT),
                    available=False,
                    updated_at=UPDATED_AT.strftime(DATETIME_FORMAT),
                ),
            ],
            [
                models.PlaceMenuCategory(
                    brand_menu_category_id=matching.any_string,
                    place_id=PLACE_ID,
                    origin_id='1',
                    category_id='1',
                    name=None,
                    updated_at=UPDATED_AT.strftime(DATETIME_FORMAT),
                ),
                models.PlaceMenuCategory(
                    brand_menu_category_id=matching.any_string,
                    place_id=PLACE_ID,
                    origin_id='2',
                    category_id='2',
                    name=None,
                    deleted_at=UPDATED_AT.strftime(DATETIME_FORMAT),
                    updated_at=UPDATED_AT.strftime(DATETIME_FORMAT),
                ),
            ],
            [
                models.BrandMenuCategory(
                    brand_id=BRAND_ID, origin_id='1', name='testsuite_1',
                ),
                models.BrandMenuCategory(
                    brand_id=BRAND_ID, origin_id='2', name='testsuite_2',
                ),
            ],
            id='insert two categories',
        ),
    ],
)
async def test_insert_categories(
        update_menu_handler,
        setup_brand_and_place,
        database,
        update_categories: typing.List[handler.UpdateCategory],
        expected_place_categories: typing.List[models.PlaceMenuCategory],
        expected_brand_categories: typing.List[models.BrandMenuCategory],
):
    """
    Проверяет, что переданные категории добавились в БД.
    """

    response = await update_menu_handler(
        place_id=PLACE_ID, categories=update_categories, items=[],
    )
    assert response.status_code == 200

    response_data = response.json()
    assert 'categories' in response_data
    assert len(response_data['categories']) == len(update_categories)

    actual_place_categories = sql.get_place_menu_categories(database, PLACE_ID)
    assert sorted(expected_place_categories) == sorted(actual_place_categories)

    actual_brand_categories = sql.get_brand_menu_categories(database, BRAND_ID)
    assert sorted(expected_brand_categories) == sorted(actual_brand_categories)


@pytest.mark.parametrize(
    'update_categories, expected_relations',
    [
        pytest.param([], [], id='no relations in empty database'),
        pytest.param(
            [
                handler.UpdateCategory(
                    origin_id='1', name='testsuite', available=False,
                ),
            ],
            [],
            id='no relations inserted when no parent origin id was provided',
        ),
        pytest.param(
            [
                handler.UpdateCategory(
                    origin_id='1', name='testsuite_1', available=False,
                ),
                handler.UpdateCategory(
                    origin_id='2',
                    name='testsuite_2',
                    parent_origin_id='1',
                    available=False,
                ),
            ],
            [models.CategoryRelation(place_id=1, category_id=2, parent_id=1)],
            id='relation inserted when parent origin id was provided',
        ),
        pytest.param(
            [
                handler.UpdateCategory(
                    origin_id='1', name='testsuite_1', available=False,
                ),
                handler.UpdateCategory(
                    origin_id='2',
                    name='testsuite_2',
                    parent_origin_id='1',
                    available=False,
                ),
                handler.UpdateCategory(
                    origin_id='3',
                    name='testsuite_3',
                    parent_origin_id='1',
                    available=False,
                ),
                handler.UpdateCategory(
                    origin_id='4',
                    name='testsuite_4',
                    parent_origin_id='2',
                    available=False,
                ),
                handler.UpdateCategory(
                    origin_id='5',
                    name='testsuite_5',
                    parent_origin_id='4',
                    available=False,
                ),
            ],
            [
                models.CategoryRelation(
                    place_id=1, category_id=2, parent_id=1,
                ),
                models.CategoryRelation(
                    place_id=1, category_id=3, parent_id=1,
                ),
                models.CategoryRelation(
                    place_id=1, category_id=4, parent_id=2,
                ),
                models.CategoryRelation(
                    place_id=1, category_id=5, parent_id=4,
                ),
            ],
            id='compound relationship inserted',
        ),
    ],
)
async def test_update_category_relations(
        update_menu_handler,
        setup_brand_and_place,
        update_categories: typing.List[handler.UpdateCategory],
        expected_relations: typing.List[models.CategoryRelation],
        sql_get_place_category_relation,
):
    response = await update_menu_handler(
        place_id=PLACE_ID, categories=update_categories, items=[],
    )
    assert response.status_code == 200

    actual_relations = sql_get_place_category_relation(PLACE_ID)
    assert sorted(actual_relations) == sorted(expected_relations)


async def test_update_category_do_not_change_brand_category(
        update_menu_handler, setup_brand_and_place, database,
):
    """
    EDACAT-2405: тест проверяет, что при обновлении категории, ее
    бренд-категория не меняется.
    """

    brand_category = models.BrandMenuCategory(
        brand_id=BRAND_ID, origin_id='testsuite_1', name='testsuite_1',
    )
    brand_category_id = sql.insert_brand_menu_category(
        database, brand_category,
    )

    sql.insert_place_menu_category(
        database,
        models.PlaceMenuCategory(
            brand_menu_category_id=brand_category_id,
            place_id=PLACE_ID,
            category_id='1',
            origin_id=brand_category.origin_id,
            sort=111,
            name='started',
            updated_at=CREATED_AT.strftime(DATETIME_FORMAT),
        ),
    )

    place_category = models.PlaceMenuCategory(
        brand_menu_category_id=brand_category_id,
        place_id=PLACE_ID,
        category_id='1',
        origin_id=brand_category.origin_id,
        name='testsuite_2',
        updated_at=UPDATED_AT.strftime(DATETIME_FORMAT),
    )

    response = await update_menu_handler(
        place_id=PLACE_ID,
        categories=[
            handler.UpdateCategory(
                origin_id=place_category.origin_id,
                name=place_category.name or '',
                available=False,
                updated_at=UPDATED_AT.strftime(DATETIME_FORMAT),
            ),
        ],
        items=[],
    )
    assert response.status_code == 200

    actual_place_categories = sql.get_place_menu_categories(database, PLACE_ID)
    assert len(actual_place_categories) == 1
    assert place_category == actual_place_categories[0]

    actual_brand_categories = sql.get_brand_menu_categories(database, BRAND_ID)
    assert len(actual_brand_categories) == 1
    assert brand_category == actual_brand_categories[0]


@pytest.mark.pgsql('eats_rest_menu_storage', files=['fill_data.sql'])
async def test_item_categories_update(
        taxi_eats_rest_menu_storage, load_json, sql_get_item_categories,
):
    """
    TODO:
    Этот тест нужнается в проверке логики
    и рефакторинге
    """

    response = await taxi_eats_rest_menu_storage.post(
        HANDLER, json=load_json('request.json'),
    )

    assert response.status_code == 200

    # Тут нет category_origin_id_3 и category_origin_id_4, потому
    # что они пришли с deleted_at, привязывать новый айтем
    # к удаленной категории пока кажется неправильно
    expected_item_categories = {
        ('category_origin_id_2', 'item_origin_id_2', False),
        ('category_origin_id_2', 'item_origin_id_4', False),
        ('category_origin_id_1', 'item_origin_id_1', False),
        ('category_origin_id_2', 'item_origin_id_3', True),
        ('category_origin_id_10', 'item_origin_id_3', False),
    }
    assert sql_get_item_categories(PLACE_ID) == expected_item_categories


@pytest.mark.pgsql('eats_rest_menu_storage', files=['fill_data.sql'])
async def test_item_categories_statuses_update(
        taxi_eats_rest_menu_storage, load_json, sql_get_category_statuses,
):
    """
    TODO:
    Этот тест нужнается в проверке логики
    и рефакторинге
    """

    response = await taxi_eats_rest_menu_storage.post(
        HANDLER, json=load_json('request.json'),
    )

    assert response.status_code == 200

    updated_at_1 = dt.datetime(2020, 1, 1, 1, 1, 1, tzinfo=TZINFO)
    updated_at = dt.datetime(2021, 1, 1, 1, 1, 1, tzinfo=TZINFO)
    expected_categories_statuses = {
        ('category_origin_id_1', True, None, None, False, updated_at_1),
        ('category_origin_id_2', True, None, REACTIVATE_AT, False, updated_at),
        ('category_origin_id_3', True, None, None, True, updated_at),
        ('category_origin_id_4', True, None, REACTIVATE_AT, True, updated_at),
        ('category_origin_id_5', True, None, None, False, updated_at),
        ('category_origin_id_9', True, None, None, False, updated_at),
        ('category_origin_id_10', True, None, None, False, updated_at),
    }

    assert (
        sql_get_category_statuses(with_updated_at=True)
        == expected_categories_statuses
    )


async def test_update_with_compare_updated_at(
        eats_rest_menu_storage, update_menu_handler, database,
):
    """
    Тест проверяет, что категории не обновляются более старыми версиями.
    Есть 4 возможных варианта:
        0. В запросе поле updated_at пустое (поле опциональное)
        1. В запросе поле updated_at есть, но такой категории нет
        2. В запросе поле updated_at есть, и оно больше, чем у существующей
            категории
        3. В запросе поле updated_at есть, и оно меньше, чем у существующей
            категории
    """

    # brands
    eats_rest_menu_storage.insert_brands([BRAND_ID])

    # places
    eats_rest_menu_storage.insert_places(
        [models.Place(place_id=PLACE_ID, brand_id=BRAND_ID, slug='slug1')],
    )

    category_uuids = eats_rest_menu_storage.insert_brand_menu_categories(
        [
            models.BrandMenuCategory(
                brand_id=BRAND_ID,
                origin_id='category_origin_id_1',
                name='category name 1',
            ),
        ],
    )

    eats_rest_menu_storage.insert_place_menu_categories(
        [
            models.PlaceMenuCategory(
                brand_menu_category_id=category_uuids[
                    (BRAND_ID, 'category_origin_id_1')
                ],
                place_id=PLACE_ID,
                origin_id='category_origin_id_1',
                sort=111,
                updated_at=UPDATED_AT.strftime(DATETIME_FORMAT),
            ),
            models.PlaceMenuCategory(
                brand_menu_category_id=category_uuids[
                    (BRAND_ID, 'category_origin_id_1')
                ],
                place_id=PLACE_ID,
                origin_id='category_origin_id_3',
                sort=333,
                updated_at=UPDATED_AT.strftime(DATETIME_FORMAT),
            ),
            models.PlaceMenuCategory(
                brand_menu_category_id=category_uuids[
                    (BRAND_ID, 'category_origin_id_1')
                ],
                place_id=PLACE_ID,
                origin_id='category_origin_id_4',
                sort=444,
                updated_at=UPDATED_AT.strftime(DATETIME_FORMAT),
            ),
        ],
    )

    updated_at_2 = dt.datetime(2021, 7, 7, 7, 7, 7, tzinfo=TZINFO)
    updated_at_3 = dt.datetime(2021, 1, 1, 1, 1, 2, tzinfo=TZINFO)
    updated_at_4 = dt.datetime(2021, 1, 1, 1, 1, 0, tzinfo=TZINFO)

    response = await update_menu_handler(
        place_id=PLACE_ID,
        categories=[
            handler.UpdateCategory(
                origin_id='category_origin_id_1',
                name='category name 1',
                available=False,
                sort=111,
            ),
            handler.UpdateCategory(
                origin_id='category_origin_id_2',
                name='category name 2',
                available=True,
                sort=222,
                updated_at=updated_at_2.strftime(DATETIME_FORMAT),
            ),
            handler.UpdateCategory(
                origin_id='category_origin_id_3',
                name='category name 3',
                available=False,
                sort=334,
                updated_at=updated_at_3.strftime(DATETIME_FORMAT),
            ),
            handler.UpdateCategory(
                origin_id='category_origin_id_4',
                name='category name 4',
                available=True,
                sort=445,
                updated_at=updated_at_4.strftime(DATETIME_FORMAT),
            ),
        ],
        items=[],
    )

    assert response.status_code == 200

    actual_categories = sql.get_place_menu_categories(database, PLACE_ID)
    assert len(actual_categories) == 4

    sorted_actual_categories = sorted(actual_categories, key=lambda x: x.sort)
    updated_at_1 = dt.datetime.strptime(
        sorted_actual_categories[0].updated_at, '%Y-%m-%dT%H:%M:%S%z',
    )
    assert (
        dt.datetime.now(tz=pytz.timezone('Europe/Moscow')) - updated_at_1
    ).min < dt.timedelta(minutes=1)
    assert sorted_actual_categories[1].updated_at == updated_at_2.strftime(
        DATETIME_FORMAT,
    )
    assert sorted_actual_categories[2].updated_at == updated_at_3.strftime(
        DATETIME_FORMAT,
    )
    assert sorted_actual_categories[2].sort == 334
    assert sorted_actual_categories[3].updated_at == UPDATED_AT.strftime(
        DATETIME_FORMAT,
    )
    assert sorted_actual_categories[3].sort == 444


async def test_deleted_at_update(place_menu_db, update_menu_handler, database):
    """
    Проверяем, что если в базе лежит категория с большим updated_at
    но меньшим deleted_at чем пришедший updated_at, обновление будет
    произведено
    """

    deleted_at = '2022-06-01T02:37:51+03:00'
    updated_at = '2022-06-01T02:38:06+03:00'
    new_updated_at = '2022-06-01T02:37:56+03:00'

    category_origin_id = 'category_origin_id_1'

    db = place_menu_db(place_id=PLACE_ID, brand_id=BRAND_ID)
    db.add_category(
        models.PlaceMenuCategory(
            brand_menu_category_id='',
            place_id=1,
            origin_id=category_origin_id,
            deleted_at=deleted_at,
            updated_at=updated_at,
        ),
    )

    response = await update_menu_handler(
        place_id=PLACE_ID,
        categories=[
            handler.UpdateCategory(
                origin_id=category_origin_id,
                name='name1',
                available=True,
                updated_at=new_updated_at,
            ),
        ],
        items=[],
    )

    assert response.status_code == 200
    db_category = next(iter(sql.get_place_menu_categories(database, PLACE_ID)))
    assert db_category.origin_id == category_origin_id  # origin_id
    assert db_category.updated_at == '2022-06-01T02:37:56+0300'  # updated_at
    assert not db_category.deleted_at  # deleted
