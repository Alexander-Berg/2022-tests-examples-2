import datetime as dt
import decimal

from dateutil import parser
import psycopg2
import pytest
import pytz

from tests_eats_rest_menu_storage import definitions
from tests_eats_rest_menu_storage import models
from tests_eats_rest_menu_storage.menu_update import handler

HANDLER = '/internal/v1/update/menu'
BRAND_ID = 1
PLACE_ID = 1

REACTIVATE_AT = parser.parse(timestr='2022-01-11T14:58:46+03:00')


@pytest.mark.pgsql('eats_rest_menu_storage', files=['fill_data.sql'])
@pytest.mark.parametrize(
    'transactional_items_update',
    (
        pytest.param(
            False,
            marks=pytest.mark.config(
                EATS_REST_MENU_STORAGE_MENU_UPDATER_SETTINGS={
                    'transactional_items_update': False,
                },
            ),
            id='false',
        ),
        pytest.param(
            True,
            marks=pytest.mark.config(
                EATS_REST_MENU_STORAGE_MENU_UPDATER_SETTINGS={
                    'transactional_items_update': True,
                },
            ),
            id='true',
        ),
    ),
)
async def test_items_update(
        taxi_eats_rest_menu_storage,
        load_json,
        sql_get_brand_menu_items,
        sql_get_place_menu_items,
        sql_get_item_stocks,
        sql_get_item_statuses,
        transactional_items_update,
):
    expected_brand_menu_items = sql_get_brand_menu_items(BRAND_ID)
    response = await taxi_eats_rest_menu_storage.post(
        HANDLER, json=load_json('request.json'),
    )

    assert response.status_code == 200

    expected_brand_menu_items.add(
        ('item_origin_id_6', 'name6', False, 'description6', 50.0, 'ml'),
    )
    assert sql_get_brand_menu_items(BRAND_ID) == expected_brand_menu_items

    timezone_info = psycopg2.tz.FixedOffsetTimezone(offset=180, name=None)
    updated_at = dt.datetime(2021, 1, 1, 1, 1, 1, tzinfo=timezone_info)
    updated_at_1 = dt.datetime(2020, 1, 1, 1, 1, 1, tzinfo=timezone_info)

    expected_place_menu_items = [
        (
            'item_origin_id_1',
            BRAND_ID,
            'item_origin_id_1',
            'name1',
            None,
            None,
            None,
            None,
            100,
            '{delivery,pickup}',
            1,
            True,
            True,
            False,
            None,
            updated_at_1,
        ),
        (
            'item_origin_id_2',
            BRAND_ID,
            'item_origin_id_2',
            'new_name2',
            False,
            None,
            1.0,
            None,
            2,
            '{delivery}',
            20,
            False,
            False,
            True,
            'short_name_22',
            updated_at,
        ),
        (
            'item_origin_id_3',
            BRAND_ID,
            'item_origin_id_3',
            'name3',
            None,
            None,
            None,
            None,
            3,
            '{delivery}',
            30,
            True,
            True,
            False,
            'new_short_name_3',
            updated_at,
        ),
        (
            'item_origin_id_4',
            BRAND_ID,
            'item_origin_id_4',
            'new_name4',
            False,
            'new_description4',
            None,
            'l',
            4,
            '{delivery,pickup}',
            40,
            True,
            False,
            True,
            None,
            updated_at,
        ),
        (
            'item_origin_id_5',
            BRAND_ID,
            'item_origin_id_5',
            'name5',
            None,
            None,
            None,
            None,
            5,
            '{delivery,pickup}',
            50,
            False,
            True,
            False,
            'short_name_5',
            updated_at,
        ),
        (
            'item_origin_id_6',
            BRAND_ID,
            'item_origin_id_6',
            'name6',
            None,
            None,
            None,
            None,
            6,
            '{delivery,pickup}',
            60,
            False,
            False,
            False,
            None,
            updated_at,
        ),
    ]
    assert (
        sorted(sql_get_place_menu_items(PLACE_ID), key=lambda x: x[2])
        == expected_place_menu_items
    )

    assert sql_get_item_stocks(PLACE_ID) == {
        ('item_origin_id_1', 10, False),
        ('item_origin_id_2', 20, False),
    }

    assert sql_get_item_statuses(with_updated_at=True) == {
        ('item_origin_id_1', True, None, None, False, updated_at_1),
        ('item_origin_id_2', False, None, REACTIVATE_AT, True, updated_at),
        ('item_origin_id_3', True, None, None, False, updated_at),
        ('item_origin_id_4', True, None, None, True, updated_at),
        ('item_origin_id_5', False, None, REACTIVATE_AT, False, updated_at),
        ('item_origin_id_6', False, None, None, False, updated_at),
    }


@pytest.mark.pgsql('eats_rest_menu_storage', files=['fill_data.sql'])
async def test_item_prices_update(
        taxi_eats_rest_menu_storage, load_json, sql_get_place_menu_item_prices,
):
    response = await taxi_eats_rest_menu_storage.post(
        HANDLER, json=load_json('request.json'),
    )

    assert response.status_code == 200

    expected_place_menu_item_prices = {
        (
            'item_origin_id_2',
            decimal.Decimal('10.5000'),
            decimal.Decimal('9.6000'),
            decimal.Decimal('10.1000'),
            True,
        ),
        ('item_origin_id_3', decimal.Decimal('15.7000'), None, None, False),
        ('item_origin_id_4', decimal.Decimal('100.0000'), None, 10.5, True),
        (
            'item_origin_id_5',
            decimal.Decimal('150.1000'),
            decimal.Decimal('100.2000'),
            None,
            False,
        ),
        ('item_origin_id_6', decimal.Decimal('40.0000'), None, None, False),
        ('item_origin_id_1', decimal.Decimal('10.0000'), None, None, False),
    }
    assert (
        sql_get_place_menu_item_prices(PLACE_ID)
        == expected_place_menu_item_prices
    )


@pytest.mark.pgsql('eats_rest_menu_storage', files=['fill_data.sql'])
async def test_item_pictures_update(
        taxi_eats_rest_menu_storage,
        load_json,
        sql_get_place_menu_item_pictures,
):
    response = await taxi_eats_rest_menu_storage.post(
        HANDLER, json=load_json('request.json'),
    )

    assert response.status_code == 200

    expected_item_pictures = {
        ('item_origin_id_2', 'url2', 0.5, True),
        ('item_origin_id_3', 'url3', None, False),
        ('item_origin_id_3', 'url2', 0.5, False),
        ('item_origin_id_4', 'url4', None, True),
        ('item_origin_id_4', 'url5', None, True),
        ('item_origin_id_1', 'url1', 1.0, False),
        ('item_origin_id_2', 'url3', 1.0, True),
    }
    assert sql_get_place_menu_item_pictures(PLACE_ID) == expected_item_pictures


@pytest.mark.pgsql('eats_rest_menu_storage', files=['fill_data.sql'])
async def test_item_stocks_update(
        taxi_eats_rest_menu_storage,
        load_json,
        sql_get_item_stocks,
        eats_rest_menu_storage,
):

    print(sql_get_item_stocks(PLACE_ID))

    response = await taxi_eats_rest_menu_storage.post(
        HANDLER, json=load_json('stocks_request.json'),
    )

    assert response.status_code == 200

    assert sql_get_item_stocks(PLACE_ID) == {
        ('item_origin_id_1', 10, False),
        ('item_origin_id_2', 40, False),
        ('item_origin_id_7', 42, False),
        ('item_origin_id_8', 1000, False),
    }


@pytest.mark.pgsql('eats_rest_menu_storage', files=[])
async def test_item_category_from_db(
        update_menu_handler, place_menu_db, sql_get_item_categories,
):
    """
    Проверяем, что если пришел айтем, а его категории нет в запросе,
    но есть в базе, то запись в place_menu_item_categories все равно
    создастся
    """
    category_origin_id = 'category_1'
    item_origin_id = 'item_1'

    db = place_menu_db(place_id=PLACE_ID, brand_id=BRAND_ID)
    db.add_category(
        models.PlaceMenuCategory(
            brand_menu_category_id='',
            place_id=PLACE_ID,
            origin_id=category_origin_id,
            name='category_1',
        ),
    )

    request_item = handler.UpdateItem(
        origin_id=item_origin_id,
        name='name1',
        adult=False,
        price='15.7',
        available=True,
        category_origin_ids=[category_origin_id],
    )

    response = await update_menu_handler(
        place_id=PLACE_ID, categories=[], items=[request_item],
    )

    assert response.status_code == 200

    assert sql_get_item_categories(PLACE_ID) == {
        (
            category_origin_id,  # category_origin_id
            item_origin_id,  # item_origin_id
            False,  # deleted
        ),
    }


async def test_update_with_compare_updated_at(
        eats_rest_menu_storage, update_menu_handler, sql_get_place_menu_items,
):
    """
    Тест проверяет, что айтемы не обновляются более старыми версиями.
    Есть 4 возможных варианта:
        0. В запросе поле updated_at пустое (поле опциональное)
        1. В запросе поле updated_at есть, но такого айтема нет
        2. В запросе поле updated_at есть, и оно больше, чем у существующего
            айтема
        3. В запросе поле updated_at есть, и оно меньше, чем у существующего
            айтема
    """

    updated_at = '2021-01-01T01:01:01+0300'
    datetime_format = '%Y-%m-%dT%H:%M:%S%z'

    # brands
    eats_rest_menu_storage.insert_brands([BRAND_ID])

    # places
    eats_rest_menu_storage.insert_places(
        [models.Place(place_id=PLACE_ID, brand_id=BRAND_ID, slug='slug1')],
    )

    # items
    item_uuids = eats_rest_menu_storage.insert_brand_menu_items(
        [
            models.BrandMenuItem(
                brand_id=BRAND_ID,
                origin_id='item_origin_id_1',
                name='brand_name_1',
            ),
            models.BrandMenuItem(
                brand_id=BRAND_ID,
                origin_id='item_origin_id_2',
                name='brand_name_2',
            ),
            models.BrandMenuItem(
                brand_id=BRAND_ID,
                origin_id='item_origin_id_3',
                name='brand_name_3',
            ),
        ],
    )

    eats_rest_menu_storage.insert_place_menu_items(
        [
            models.PlaceMenuItem(
                place_id=PLACE_ID,
                brand_menu_item_id=item_uuids[(BRAND_ID, 'item_origin_id_1')],
                origin_id='item_origin_id_1',
                name='item_name_1',
                sort=111,
                updated_at=updated_at,
            ),
            models.PlaceMenuItem(
                place_id=PLACE_ID,
                brand_menu_item_id=item_uuids[(BRAND_ID, 'item_origin_id_2')],
                origin_id='item_origin_id_3',
                name='item_name_3',
                sort=333,
                updated_at=updated_at,
            ),
            models.PlaceMenuItem(
                place_id=PLACE_ID,
                brand_menu_item_id=item_uuids[(BRAND_ID, 'item_origin_id_3')],
                origin_id='item_origin_id_4',
                name='item_name_4',
                sort=444,
                updated_at=updated_at,
            ),
        ],
    )

    updated_at_2 = '2021-07-07T07:07:07+0300'
    updated_at_3 = '2021-01-01T01:01:02+0300'
    updated_at_4 = '2021-01-01T01:01:00+0300'

    response = await update_menu_handler(
        place_id=PLACE_ID,
        categories=[],
        items=[
            handler.UpdateItem(
                origin_id='item_origin_id_1',
                name='item_name_1',
                available=False,
                sort=111,
            ),
            handler.UpdateItem(
                origin_id='item_origin_id_2',
                name='item_name_2',
                available=True,
                sort=222,
                updated_at=updated_at_2,
            ),
            handler.UpdateItem(
                origin_id='item_origin_id_3',
                name='item_name_3',
                available=False,
                sort=334,
                updated_at=updated_at_3,
            ),
            handler.UpdateItem(
                origin_id='item_origin_id_4',
                name='item_name_4',
                available=True,
                sort=445,
                updated_at=updated_at_4,
            ),
        ],
    )

    assert response.status_code == 200

    actual_items = sql_get_place_menu_items(PLACE_ID)
    assert len(actual_items) == 4

    sorted_actual_items = sorted(
        actual_items, key=lambda x: x[8],
    )  # sorted by "sort" field
    updated_at_1 = sorted_actual_items[0][15]
    assert (
        dt.datetime.now(tz=pytz.timezone('Europe/Moscow')) - updated_at_1
    ).min < dt.timedelta(minutes=1)
    assert sorted_actual_items[1][15].strftime(datetime_format) == updated_at_2
    assert sorted_actual_items[2][15].strftime(datetime_format) == updated_at_3
    assert sorted_actual_items[2][8] == 334
    assert sorted_actual_items[3][15].strftime(datetime_format) == updated_at
    assert sorted_actual_items[3][8] == 444


async def test_update_nutrients(
        place_menu_db, database, update_menu_handler, testpoint,
):
    """
    Актуальный айтем - айтем без updated_at
    Неактуальный айтем - у айтема updated_at меньше, чём в базe
    Тест проверяет, что КБЖУ обновляется в случаях:
        1. В запросе пришёл актуальный айтем
        2. В запросе пришёл неактуальный айтем, но с КБЖУ, а в базе нет КБЖУ
        3. В запросе пришёл неактуальный айтем, но в КБЖУ есть поле updated_at,
            в базе у КБЖУ нет поля updated_at
        4. В запросе пришёл неактуальный айтем, но более новое КБЖУ
    """

    actual_datetime = '2021-01-01T01:01:01+00:00'
    non_actual_datetime = '2020-01-01T01:01:01+00:00'

    item_origin_id_1 = 'item_origin_id_1'
    item_origin_id_2 = 'item_origin_id_2'
    item_origin_id_3 = 'item_origin_id_3'
    item_origin_id_4 = 'item_origin_id_4'

    db = place_menu_db(place_id=PLACE_ID, brand_id=BRAND_ID)
    db.add_category(
        models.PlaceMenuCategory(
            brand_menu_category_id='',
            place_id=1,
            origin_id='category_origin_id_1',
        ),
    )
    db.add_item(
        category_id=1,
        item=models.PlaceMenuItem(
            place_id=1,
            brand_menu_item_id='',
            origin_id=item_origin_id_1,
            name='name1',
            nutrients=models.Nutrients(
                calories='1',
                proteins='1',
                fats='1',
                carbohydrates='1',
                deleted=False,
            ),
        ),
    )
    db.add_item(
        category_id=1,
        item=models.PlaceMenuItem(
            place_id=1,
            brand_menu_item_id='',
            origin_id=item_origin_id_2,
            name='name2',
            updated_at=actual_datetime,
        ),
    )
    db.add_item(
        category_id=1,
        item=models.PlaceMenuItem(
            place_id=1,
            brand_menu_item_id='',
            origin_id=item_origin_id_3,
            name='name3',
            updated_at=actual_datetime,
            nutrients=models.Nutrients(
                calories='3',
                proteins='3',
                fats='3',
                carbohydrates='3',
                deleted=False,
            ),
        ),
    )
    db.add_item(
        category_id=1,
        item=models.PlaceMenuItem(
            place_id=1,
            brand_menu_item_id='',
            origin_id=item_origin_id_4,
            name='name4',
            updated_at=actual_datetime,
            nutrients=models.Nutrients(
                calories='4',
                proteins='4',
                fats='4',
                carbohydrates='4',
                updated_at=non_actual_datetime,
                deleted=False,
            ),
        ),
    )

    @testpoint('eats_rest_menu_storage::outdated_item_has_nutrients')
    def point1(arg):
        pass

    @testpoint('eats_rest_menu_storage::outdated_item_has_new_nutrients')
    def point2(arg):
        pass

    new_nutrients_1 = models.Nutrients(
        calories='1.1',
        proteins='1.1',
        fats='1.1',
        carbohydrates='1.1',
        deleted=True,
    )
    new_nutrients_2 = models.Nutrients(
        calories='2.2',
        proteins='2.2',
        fats='2.2',
        carbohydrates='2.2',
        deleted=True,
    )
    new_nutrients_3 = models.Nutrients(
        calories='3.3',
        proteins='3.3',
        fats='3.3',
        carbohydrates='3.3',
        updated_at=non_actual_datetime,
        deleted=True,
    )
    new_nutrients_4 = models.Nutrients(
        calories='4.4',
        proteins='4.4',
        fats='4.4',
        carbohydrates='4.4',
        updated_at=actual_datetime,
        deleted=True,
    )

    response = await update_menu_handler(
        place_id=PLACE_ID,
        categories=[],
        items=[
            handler.UpdateItem(
                origin_id=item_origin_id_1,
                name='name1',
                adult=True,
                price='15.7',
                available=True,
                nutrients=new_nutrients_1,
            ),
            handler.UpdateItem(
                origin_id=item_origin_id_2,
                name='name2',
                adult=True,
                price='16.7',
                available=False,
                updated_at=non_actual_datetime,
                nutrients=new_nutrients_2,
            ),
            handler.UpdateItem(
                origin_id=item_origin_id_3,
                name='name3',
                adult=False,
                price='17.7',
                available=True,
                updated_at=non_actual_datetime,
                nutrients=new_nutrients_3,
            ),
            handler.UpdateItem(
                origin_id=item_origin_id_4,
                name='name4',
                adult=False,
                price='18.7',
                available=False,
                updated_at=non_actual_datetime,
                nutrients=new_nutrients_4,
            ),
        ],
    )

    assert response.status_code == 200

    cursor = database.cursor()
    cursor.execute(
        """
    SELECT
        nutrients
    FROM
        eats_rest_menu_storage.place_menu_items
    WHERE
        origin_id IN (%s, %s, %s, %s)
    ORDER BY origin_id
    """,
        (
            item_origin_id_1,
            item_origin_id_2,
            item_origin_id_3,
            item_origin_id_4,
        ),
    )

    assert point1.times_called == 2
    assert point2.times_called == 1

    rows = cursor.fetchall()
    assert len(rows) == 4
    assert rows[0][0] == new_nutrients_1.as_dict()
    assert rows[1][0] == new_nutrients_2.as_dict()
    assert rows[2][0] == new_nutrients_3.as_dict()
    assert rows[3][0] == new_nutrients_4.as_dict()


async def test_update_item_picture(
        place_menu_db, update_menu_handler, sql_get_place_menu_item_pictures,
):
    """
    Проверяем, что если картинка айтема не изменилась
    в таблице pictures не будет новой записи
    """

    item_origin_id = 'item_origin_id_1'
    picture_url = 'url1'

    db = place_menu_db(place_id=PLACE_ID, brand_id=BRAND_ID)
    db.add_category(
        models.PlaceMenuCategory(
            brand_menu_category_id='',
            place_id=1,
            origin_id='category_origin_id_1',
        ),
    )
    db.add_item(
        category_id=1,
        item=models.PlaceMenuItem(
            place_id=1,
            brand_menu_item_id='',
            origin_id=item_origin_id,
            name='name1',
        ),
        picture=models.Picture(url=picture_url, ratio=None),
    )

    response = await update_menu_handler(
        place_id=PLACE_ID,
        categories=[],
        items=[
            handler.UpdateItem(
                origin_id=item_origin_id,
                name='name1',
                adult=True,
                price='15.7',
                available=True,
                pictures=[definitions.Picture(url=picture_url, ratio=None)],
            ),
        ],
    )

    assert response.status_code == 200

    db_pictures = sql_get_place_menu_item_pictures(PLACE_ID)
    assert db_pictures == set(
        [
            (
                item_origin_id,  # origin_id
                picture_url,  # url
                None,  # ratio
                False,  # deleted
            ),
        ],
    )


async def test_deleted_at_update(
        place_menu_db, update_menu_handler, sql_get_place_menu_items,
):
    """
    Проверяем, что если в базе лежит айтем с большим updated_at
    но меньшим deleted_at чем пришедший updated_at, обновление будет
    произведено
    """
    deleted_at = '2022-06-01T02:37:51+03:00'
    updated_at = '2022-06-01T02:38:06+03:00'
    new_updated_at = '2022-06-01T02:37:56+03:00'

    item_origin_id = 'item_origin_id_1'

    db = place_menu_db(place_id=PLACE_ID, brand_id=BRAND_ID)
    db.add_category(
        models.PlaceMenuCategory(
            brand_menu_category_id='',
            place_id=1,
            origin_id='category_origin_id_1',
        ),
    )
    db.add_item(
        category_id=1,
        item=models.PlaceMenuItem(
            place_id=1,
            brand_menu_item_id='',
            origin_id=item_origin_id,
            name='name1',
            deleted_at=deleted_at,
            updated_at=updated_at,
        ),
    )

    response = await update_menu_handler(
        place_id=PLACE_ID,
        categories=[],
        items=[
            handler.UpdateItem(
                origin_id=item_origin_id,
                name='name1',
                adult=True,
                price='15.7',
                available=True,
                updated_at=new_updated_at,
            ),
        ],
    )

    assert response.status_code == 200
    db_item = next(iter(sql_get_place_menu_items(PLACE_ID)))
    assert db_item[0] == item_origin_id  # origin_id
    assert db_item[15] == parser.parse(timestr=new_updated_at)  # updated_at
    assert not db_item[13]  # deleted


async def test_updated_at_skip_picture(
        place_menu_db, update_menu_handler, sql_get_place_menu_item_pictures,
):
    """
    Проверяем, если пришел айтем с меньшим updated_at,
    его картинка не будет обновлена
    """

    db_updated_at = '2022-06-02T02:37:56+03:00'
    updated_at = '2022-06-01T02:38:06+03:00'

    item_origin_id = 'item_origin_id_1'
    picture_url = 'my_url'

    db = place_menu_db(place_id=PLACE_ID, brand_id=BRAND_ID)
    db.add_category(
        models.PlaceMenuCategory(
            brand_menu_category_id='',
            place_id=1,
            origin_id='category_origin_id_1',
        ),
    )
    db.add_item(
        category_id=1,
        item=models.PlaceMenuItem(
            place_id=1,
            brand_menu_item_id='',
            origin_id=item_origin_id,
            name='name1',
            updated_at=db_updated_at,
        ),
        picture=models.Picture(url=picture_url, ratio=None),
    )

    response = await update_menu_handler(
        place_id=PLACE_ID,
        categories=[],
        items=[
            handler.UpdateItem(
                origin_id=item_origin_id,
                name='name1',
                adult=True,
                price='15.7',
                available=True,
                updated_at=updated_at,
                deleted_at=updated_at,
            ),
        ],
    )

    assert response.status_code == 200
    db_item_picture = next(iter(sql_get_place_menu_item_pictures(PLACE_ID)))
    assert db_item_picture[0] == item_origin_id  # origin_id
    assert db_item_picture[1] == picture_url  # url
    assert not db_item_picture[3]  # deleted


async def test_only_legacy_id_changed(
        place_menu_db, update_menu_handler, sql_get_place_menu_items,
):
    """
    Проверяем что если у айтема изменился только
    legacy_id, он будет обновлен в базе
    """

    old_updated_at = '2022-06-01T02:38:06+03:00'
    updated_at = '2022-06-01T03:38:06+03:00'

    item_origin_id = 'item_origin_id_1'

    place_menu_db(place_id=PLACE_ID, brand_id=BRAND_ID)

    response = await update_menu_handler(
        place_id=PLACE_ID,
        categories=[],
        items=[
            handler.UpdateItem(
                origin_id=item_origin_id,
                name='name1',
                legacy_id=1,
                ordinary=True,
                choosable=True,
                adult=False,
                sort=100,
                updated_at=old_updated_at,
            ),
        ],
    )

    assert response.status_code == 200
    db_item = next(iter(sql_get_place_menu_items(PLACE_ID)))
    assert db_item[10] == 1  # legacy_id

    response = await update_menu_handler(
        place_id=PLACE_ID,
        categories=[],
        items=[
            handler.UpdateItem(
                origin_id=item_origin_id,
                name='name1',
                legacy_id=2,
                ordinary=True,
                choosable=True,
                adult=False,
                sort=100,
                updated_at=updated_at,
            ),
        ],
    )

    assert response.status_code == 200
    db_item = next(iter(sql_get_place_menu_items(PLACE_ID)))
    assert db_item[10] == 2  # legacy_id
