# pylint: disable=too-many-lines

import datetime as dt
import decimal
import typing

from dateutil import parser
import psycopg2
import pytest
import pytz

from tests_eats_rest_menu_storage import models
from tests_eats_rest_menu_storage.menu_update import handler

HANDLER = '/internal/v1/update/menu'
BRAND_ID = 1
PLACE_ID = 1

NOW = '2021-03-30T12:55:00+00:00'
REACTIVATE_AT = '2022-01-11T14:58:46+03:00'

OLD_UPDATED_AT = '2020-01-01T01:01:01+0300'
UPDATED_AT = '2021-01-01T01:01:01+0300'
NEW_UPDATED_AT = '2022-01-01T01:01:01+0300'
UPDATED_AT_2 = '2021-07-07T07:07:07+0300'
UPDATED_AT_3 = '2021-01-01T01:01:02+0300'
UPDATED_AT_4 = '2021-01-01T01:01:00+0300'
DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S%z'

REQUEST_ITEM = handler.UpdateItem(
    origin_id='item_1',
    name='name1',
    adult=False,
    price='15.7',
    available=True,
    category_origin_ids=['category_1'],
    options_groups=[
        handler.UpdateOptionsGroup(
            origin_id='option_group_1',
            name='option_group_1',
            options=[
                handler.UpdateOption(
                    origin_id='option_1',
                    name='option_1',
                    available=True,
                    price='300',
                    promo_price='80',
                    vat='20',
                    updated_at=NEW_UPDATED_AT,
                ),
                handler.UpdateOption(
                    origin_id='option_2',
                    name='option_2',
                    available=False,
                    reactivate_at=REACTIVATE_AT,
                    price='400',
                    updated_at=NEW_UPDATED_AT,
                ),
                handler.UpdateOption(
                    origin_id='option_3',
                    name='option_3',
                    available=False,
                    price='0',
                    deleted_at=NOW,
                    updated_at=NEW_UPDATED_AT,
                ),
            ],
        ),
    ],
)


def make_three_option_menu(place_menu_db) -> typing.Tuple[int, int, int]:
    """
    Создает меню с 1 айтемом, в котором 1 группа
    и 2 опции
    """
    category_id = place_menu_db.add_category(
        models.PlaceMenuCategory(
            brand_menu_category_id='',
            place_id=PLACE_ID,
            origin_id='category_1',
            name='category_1',
        ),
    )
    item_id = place_menu_db.add_item(
        category_id,
        models.PlaceMenuItem(
            place_id=PLACE_ID,
            brand_menu_item_id='',
            origin_id='item_1',
            name='item_1',
        ),
    )
    group_id = place_menu_db.add_option_group(
        models.PlaceMenuItemOptionGroup(
            brand_menu_item_option_group='',
            place_menu_item_id=item_id,
            origin_id='option_group_1',
            name='option_group_1',
        ),
    )
    one_option_id = place_menu_db.add_option(
        models.PlaceMenuItemOption(
            brand_menu_item_option='',
            place_menu_item_option_group_id=group_id,
            origin_id='option_1',
            name='option_1',
            updated_at='2020-01-01T01:01:01.000+03:00',
        ),
    )
    two_option_id = place_menu_db.add_option(
        models.PlaceMenuItemOption(
            brand_menu_item_option='',
            place_menu_item_option_group_id=group_id,
            origin_id='option_2',
            name='option_2',
            updated_at='2020-01-01T01:01:01.000+03:00',
        ),
    )
    three_option_id = place_menu_db.add_option(
        models.PlaceMenuItemOption(
            brand_menu_item_option='',
            place_menu_item_option_group_id=group_id,
            origin_id='option_3',
            name='option_3',
            updated_at='2020-01-01T01:01:01.000+03:00',
        ),
    )
    return (one_option_id, two_option_id, three_option_id)


@pytest.mark.pgsql('eats_rest_menu_storage', files=[])
async def test_item_options_update(
        update_menu_handler,
        place_menu_db,
        sql_get_place_item_options,
        sql_get_brand_item_options,
):
    """
    Проверяем обновления опций.
    Изначально в базе айтем с 1 группой и 1 опцией
    Проверяем, что при запросе с этой опцией и новой
    новая появится в базе, записи о существующей обновятся
    """

    db = place_menu_db(place_id=PLACE_ID, brand_id=BRAND_ID)
    category_id = db.add_category(
        models.PlaceMenuCategory(
            brand_menu_category_id='',
            place_id=PLACE_ID,
            origin_id='category_1',
            name='category_1',
        ),
    )
    item_id = db.add_item(
        category_id,
        models.PlaceMenuItem(
            place_id=PLACE_ID,
            brand_menu_item_id='',
            origin_id='item_1',
            name='item_1',
        ),
    )
    group_id = db.add_option_group(
        models.PlaceMenuItemOptionGroup(
            brand_menu_item_option_group='',
            place_menu_item_id=item_id,
            origin_id='option_group_1',
            name='option_group_1',
        ),
    )
    db.add_option(
        models.PlaceMenuItemOption(
            brand_menu_item_option='',
            place_menu_item_option_group_id=group_id,
            origin_id='option_1',
            name='option_1',
            updated_at=OLD_UPDATED_AT,
        ),
    )

    response = await update_menu_handler(
        place_id=PLACE_ID,
        categories=[],
        items=[
            handler.UpdateItem(
                origin_id='item_1',
                name='name1',
                adult=False,
                price='15.7',
                available=True,
                category_origin_ids=['category_1'],
                options_groups=[
                    handler.UpdateOptionsGroup(
                        origin_id='option_group_1',
                        name='option_group_1',
                        options=[
                            handler.UpdateOption(
                                origin_id='option_1',
                                name='my_opt',
                                available=True,
                                legacy_id=1,
                                multiplier=2,
                                min_amount=10,
                                max_amount=20,
                                sort=200,
                                updated_at=UPDATED_AT,
                            ),
                            handler.UpdateOption(
                                origin_id='option_2',
                                name='option_2',
                                available=True,
                                legacy_id=2,
                                min_amount=10,
                                max_amount=20,
                                sort=2,
                                updated_at=UPDATED_AT,
                            ),
                        ],
                    ),
                ],
            ),
        ],
    )

    assert response.status_code == 200

    expected_place_options = {
        (
            1,  # id
            'option_1',  # brand.origin_id
            'option_group_1',  # group_origin_id
            'item_1',  # item_origin_id
            'option_1',  # place.origin_id
            1,  # legacy_id
            'my_opt',  # name
            2,  # multiplier
            10,  # min_amount
            20,  # max_amount
            200,  # sort
            False,  # deleted
            dt.datetime(
                2021,
                1,
                1,
                1,
                1,
                1,
                tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=180, name=None),
            ),
        ),
        (
            2,  # id
            'option_2',  # brand.origin_id
            'option_group_1',  # group_origin_id
            'item_1',  # item_origin_id
            'option_2',  # place.origin_id
            2,  # legacy_id
            None,  # name
            None,  # multiplier
            None,  # min_amount
            None,  # max_amount
            None,  # sort
            False,  # deleted
            dt.datetime(
                2021,
                1,
                1,
                1,
                1,
                1,
                tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=180, name=None),
            ),
        ),
    }
    assert sql_get_place_item_options(PLACE_ID) == expected_place_options

    expected_brand_options = {
        (
            'option_1',  # origin_id
            'option_1',  # name
            1,  # multiplier
            None,  # min_amount
            None,  # max_amount
            None,  # sort
        ),
        (
            'option_2',  # origin_id
            'option_2',  # name
            1,  # multiplier
            10,  # min_amount
            20,  # max_amount
            2,  # sort
        ),
    }
    assert sql_get_brand_item_options(BRAND_ID) == expected_brand_options


@pytest.mark.pgsql('eats_rest_menu_storage', files=[])
async def test_item_option_prices_update(
        update_menu_handler,
        place_menu_db,
        eats_rest_menu_storage,
        sql_get_item_option_prices,
):
    """
    Проверяем обновления цен опций.
    Изначально в базе айтем с 1 группой и 3 опциями
    цена 1й - 100,
    цена второй - 200
    Проверяем что после запроса становится
    300 и 400 соответственно
    третья опция удалена
    """

    db = place_menu_db(place_id=PLACE_ID, brand_id=BRAND_ID)
    one_option_id, two_option_id, three_option_id = make_three_option_menu(db)
    eats_rest_menu_storage.insert_item_option_prices(
        [
            models.PlaceMenuItemOptionPrice(
                place_menu_item_option_id=one_option_id,
                price=decimal.Decimal('100'),
                promo_price=decimal.Decimal('90'),
                vat=decimal.Decimal('10'),
            ),
            models.PlaceMenuItemOptionPrice(
                place_menu_item_option_id=two_option_id,
                price=decimal.Decimal('200'),
            ),
            models.PlaceMenuItemOptionPrice(
                place_menu_item_option_id=three_option_id,
                price=decimal.Decimal('300'),
            ),
        ],
    )

    response = await update_menu_handler(
        place_id=PLACE_ID, categories=[], items=[REQUEST_ITEM],
    )

    assert response.status_code == 200

    expected_item_option_prices = {
        (
            'item_1',  # item_origin_id
            'option_group_1',  # group_origin_id
            'option_1',  # origin_id
            decimal.Decimal('300.0000'),  # price
            decimal.Decimal('80.0000'),  # promo_price
            decimal.Decimal('20.0000'),  # vat
            False,  # deleted
        ),
        (
            'item_1',  # item_origin_id
            'option_group_1',  # group_origin_id
            'option_2',  # origin_id
            decimal.Decimal('400.0000'),  # price
            None,  # promo_price
            None,  # vat
            False,  # deleted
        ),
        (
            'item_1',  # item_origin_id
            'option_group_1',  # group_origin_id
            'option_3',  # origin_id
            decimal.Decimal('0.0000'),  # price
            None,  # promo_price
            None,  # vat
            True,  # deleted
        ),
    }
    assert sql_get_item_option_prices(PLACE_ID) == expected_item_option_prices


@pytest.mark.now(NOW)
@pytest.mark.pgsql('eats_rest_menu_storage', files=[])
async def test_item_option_statuses_update(
        update_menu_handler,
        place_menu_db,
        eats_rest_menu_storage,
        sql_get_option_statuses,
):
    """
    Проверяем обновления стоплистов опций.
    Изначально в базе айтем с 1 группой и 3 опциями
    одна available: false, вторая available: true
    пытаемся первую сделать доступной, а вторую нет
    третью удаляем
    """

    db = place_menu_db(place_id=PLACE_ID, brand_id=BRAND_ID)
    one_option_id, two_option_id, three_option_id = make_three_option_menu(db)
    eats_rest_menu_storage.insert_item_option_statuses(
        [
            models.PlaceMenuItemOptionStatus(
                place_menu_item_option_id=one_option_id, active=False,
            ),
            models.PlaceMenuItemOptionStatus(
                place_menu_item_option_id=two_option_id, active=True,
            ),
            models.PlaceMenuItemOptionStatus(
                place_menu_item_option_id=three_option_id, active=True,
            ),
        ],
    )

    response = await update_menu_handler(
        place_id=PLACE_ID, categories=[], items=[REQUEST_ITEM],
    )

    assert response.status_code == 200

    timezone_info = psycopg2.tz.FixedOffsetTimezone(offset=180, name=None)
    updated_at = dt.datetime(2022, 1, 1, 1, 1, 1, tzinfo=timezone_info)

    assert sql_get_option_statuses(with_updated_at=True) == set(
        [
            (
                one_option_id,  # id
                'option_1',  # origin_id
                True,  # active
                None,  # deactivated_at
                None,  # reactivate_at
                False,  # deleted
                updated_at,
            ),
            (
                two_option_id,  # id
                'option_2',  # origin_id
                False,  # active
                parser.parse(timestr=NOW),  # deactivated_at
                parser.parse(timestr=REACTIVATE_AT),  # reactivate_at
                False,  # deleted
                updated_at,
            ),
            (
                three_option_id,  # id
                'option_3',  # origin_id
                False,  # active
                parser.parse(timestr=NOW),  # deactivated_at
                None,  # reactivate_at
                True,  # deleted
                updated_at,
            ),
        ],
    )


@pytest.mark.parametrize(
    'item_updated_at, group_updated_at',
    [
        pytest.param(
            NEW_UPDATED_AT,
            NEW_UPDATED_AT,
            id='database_item_and_group_outdated',
        ),
        pytest.param(
            NEW_UPDATED_AT, OLD_UPDATED_AT, id='request_group_outdated',
        ),
        pytest.param(
            OLD_UPDATED_AT, NEW_UPDATED_AT, id='request_item_outdated',
        ),
        pytest.param(
            OLD_UPDATED_AT,
            OLD_UPDATED_AT,
            id='request_item_and_group_outdated',
        ),
    ],
)
async def test_update_with_compare_updated_at(
        update_menu_handler,
        place_menu_db,
        sql_get_place_item_options,
        item_updated_at,
        group_updated_at,
):
    """
    Тест проверяет, что опции не обновляются более старыми версиями
    вне зависимости от того, обновляется ли сам айтем или группа.
    Итого 16 вариантов: 4 варианта - айтем с группой обновляются или нет,
    и 4 подварианта:
        0. В запросе поле updated_at пустое (поле опциональное)
        1. В запросе поле updated_at есть, но такой опции нет
        2. В запросе поле updated_at есть, и оно больше, чем у существующей
            опции
        3. В запросе поле updated_at есть, и оно меньше, чем у существующей
            опции
    """

    db = place_menu_db(place_id=PLACE_ID, brand_id=BRAND_ID)
    category_id = db.add_category(
        models.PlaceMenuCategory(
            brand_menu_category_id='',
            place_id=PLACE_ID,
            origin_id='category_1',
            name='category_1',
        ),
    )
    item_id = db.add_item(
        category_id,
        models.PlaceMenuItem(
            place_id=PLACE_ID,
            brand_menu_item_id='',
            origin_id='item_1',
            name='item_1',
            updated_at=item_updated_at,
        ),
    )
    group_id = db.add_option_group(
        models.PlaceMenuItemOptionGroup(
            brand_menu_item_option_group='',
            place_menu_item_id=item_id,
            origin_id='option_group_1',
            updated_at=group_updated_at,
        ),
    )
    db.add_option(
        models.PlaceMenuItemOption(
            brand_menu_item_option='',
            place_menu_item_option_group_id=group_id,
            origin_id='option_origin_id_1',
            updated_at=UPDATED_AT,
        ),
    )
    db.add_option(
        models.PlaceMenuItemOption(
            brand_menu_item_option='',
            place_menu_item_option_group_id=group_id,
            origin_id='option_origin_id_3',
            updated_at=UPDATED_AT,
        ),
    )
    db.add_option(
        models.PlaceMenuItemOption(
            brand_menu_item_option='',
            place_menu_item_option_group_id=group_id,
            origin_id='option_origin_id_4',
            updated_at=UPDATED_AT,
        ),
    )

    response = await update_menu_handler(
        place_id=PLACE_ID,
        categories=[],
        items=[
            handler.UpdateItem(
                origin_id='item_1',
                name='name1',
                adult=False,
                price='15.7',
                available=True,
                category_origin_ids=['category_1'],
                updated_at=UPDATED_AT,
                options_groups=[
                    handler.UpdateOptionsGroup(
                        origin_id='option_group_1',
                        name='option_group_1',
                        updated_at=UPDATED_AT,
                        options=[
                            handler.UpdateOption(
                                origin_id='option_origin_id_1',
                                name='option name 1',
                            ),
                            handler.UpdateOption(
                                origin_id='option_origin_id_2',
                                name='option name 2',
                                updated_at=UPDATED_AT_2,
                            ),
                            handler.UpdateOption(
                                origin_id='option_origin_id_3',
                                name='option name 3',
                                deleted_at=UPDATED_AT_3,
                                updated_at=UPDATED_AT_3,
                            ),
                            handler.UpdateOption(
                                origin_id='option_origin_id_4',
                                name='option name 4',
                                deleted_at=UPDATED_AT_4,
                                updated_at=UPDATED_AT_4,
                            ),
                        ],
                    ),
                ],
            ),
        ],
    )

    assert response.status_code == 200

    actual_options = sql_get_place_item_options(PLACE_ID)
    assert len(actual_options) == 4

    sorted_actual_options = sorted(
        actual_options, key=lambda x: x[4],
    )  # sorted by "origin_id" field
    # index 11 - deleted
    # index 12 - updated_at
    updated_at_1 = sorted_actual_options[0][12]
    assert (
        dt.datetime.now(tz=pytz.timezone('Europe/Moscow')) - updated_at_1
    ).min < dt.timedelta(minutes=1)
    assert (
        sorted_actual_options[1][12].strftime(DATETIME_FORMAT) == UPDATED_AT_2
    )
    assert (
        sorted_actual_options[2][12].strftime(DATETIME_FORMAT) == UPDATED_AT_3
    )
    assert sorted_actual_options[2][11] is True
    assert sorted_actual_options[3][12].strftime(DATETIME_FORMAT) == UPDATED_AT
    assert sorted_actual_options[3][11] is False


@pytest.mark.now(UPDATED_AT)
@pytest.mark.pgsql('eats_rest_menu_storage', files=[])
async def test_item_options_update_with_same_name(
        update_menu_handler,
        place_menu_db,
        sql_get_brand_item_options,
        sql_get_place_item_options,
):
    """
    Проверяем что если пришла опция с таким же именем,
    но другим origin_id она все равно будет дедуплицирована
    в бренде
    """

    db = place_menu_db(place_id=PLACE_ID, brand_id=BRAND_ID)
    category_id = db.add_category(
        models.PlaceMenuCategory(
            brand_menu_category_id='',
            place_id=PLACE_ID,
            origin_id='category_1',
            name='category_1',
        ),
    )
    item_id = db.add_item(
        category_id,
        models.PlaceMenuItem(
            place_id=PLACE_ID,
            brand_menu_item_id='',
            origin_id='item_1',
            name='item_1',
        ),
    )

    group_id = db.add_option_group(
        models.PlaceMenuItemOptionGroup(
            brand_menu_item_option_group='',
            place_menu_item_id=item_id,
            origin_id='option_group_1',
        ),
    )

    name = 'option_name'

    option = models.PlaceMenuItemOption(
        brand_menu_item_option='',
        place_menu_item_option_group_id=group_id,
        origin_id='option_1',
        legacy_id=1,
        name=name,
        updated_at=OLD_UPDATED_AT,
    )

    db.add_option(option)

    request_item = handler.UpdateItem(
        origin_id='item_1',
        name='name1',
        category_origin_ids=['category_1'],
        options_groups=[
            handler.UpdateOptionsGroup(
                legacy_id=1,
                origin_id='option_group_1',
                name='option_group_1',
                options=[
                    handler.UpdateOption(
                        origin_id='option_2',
                        name=name,
                        available=True,
                        legacy_id=1,
                        sort=200,
                        updated_at=UPDATED_AT,
                    ),
                ],
                updated_at=UPDATED_AT,
            ),
        ],
    )

    response = await update_menu_handler(
        place_id=PLACE_ID, categories=[], items=[request_item],
    )

    assert response.status_code == 200

    expected_brand_options = {
        (
            'option_1',  # origin_id
            name,  # name
            1,  # multiplier
            None,  # min_amount
            None,  # max_amount
            None,  # sort
        ),
    }
    assert sql_get_brand_item_options(BRAND_ID) == expected_brand_options

    expected_place_options = {
        (
            1,  # id
            'option_1',  # brand.origin_id
            'option_group_1',  # group_origin_id
            'item_1',  # item_origin_id
            'option_1',  # place.origin_id
            1,  # legacy_id
            name,  # name
            None,  # multiplier
            None,  # min_amount
            None,  # max_amount
            None,  # sort
            True,  # deleted
            models.pg_time(UPDATED_AT),  # updated_at
        ),
        (
            3,  # id
            'option_1',  # brand.origin_id
            'option_group_1',  # group_origin_id
            'item_1',  # item_origin_id
            'option_2',  # place.origin_id
            1,  # legacy_id
            None,  # name
            None,  # multiplier
            None,  # min_amount
            None,  # max_amount
            200,  # sort
            False,  # deleted
            models.pg_time(UPDATED_AT),  # updated_at
        ),
    }
    assert sql_get_place_item_options(PLACE_ID) == expected_place_options


@pytest.mark.now(UPDATED_AT)
@pytest.mark.pgsql('eats_rest_menu_storage', files=[])
async def test_item_options_update_with_same_name_and_diff_group(
        update_menu_handler,
        place_menu_db,
        sql_get_brand_item_options,
        sql_get_place_item_options,
):
    """
    Проверяем что если пришла опция с таким же именем,
    но другим origin_id и в другой группе она будет дедуплицирована
    в бренде
    """

    db = place_menu_db(place_id=PLACE_ID, brand_id=BRAND_ID)
    category_id = db.add_category(
        models.PlaceMenuCategory(
            brand_menu_category_id='',
            place_id=PLACE_ID,
            origin_id='category_1',
            name='category_1',
        ),
    )
    item_id = db.add_item(
        category_id,
        models.PlaceMenuItem(
            place_id=PLACE_ID,
            brand_menu_item_id='',
            origin_id='item_1',
            name='item_1',
        ),
    )

    group_id = db.add_option_group(
        models.PlaceMenuItemOptionGroup(
            brand_menu_item_option_group='',
            place_menu_item_id=item_id,
            origin_id='option_group_1',
        ),
    )

    name = 'option_name'

    option = models.PlaceMenuItemOption(
        brand_menu_item_option='',
        place_menu_item_option_group_id=group_id,
        origin_id='option_1',
        legacy_id=1,
        name=name,
        updated_at=OLD_UPDATED_AT,
    )

    db.add_option(option)

    request_item = handler.UpdateItem(
        origin_id='item_1',
        name='name1',
        category_origin_ids=['category_1'],
        options_groups=[
            handler.UpdateOptionsGroup(
                legacy_id=1,
                origin_id='option_group_2',
                name='option_group_2',
                options=[
                    handler.UpdateOption(
                        origin_id='option_2',
                        name=name,
                        available=True,
                        legacy_id=1,
                        sort=200,
                        updated_at=UPDATED_AT,
                    ),
                ],
                updated_at=UPDATED_AT,
            ),
        ],
    )

    response = await update_menu_handler(
        place_id=PLACE_ID, categories=[], items=[request_item],
    )

    assert response.status_code == 200

    expected_brand_options = {
        (
            'option_1',  # origin_id
            name,  # name
            1,  # multiplier
            None,  # min_amount
            None,  # max_amount
            None,  # sort
        ),
    }
    assert sql_get_brand_item_options(BRAND_ID) == expected_brand_options

    expected_place_options = {
        (
            1,  # id
            'option_1',  # brand.origin_id
            'option_group_1',  # group_origin_id
            'item_1',  # item_origin_id
            'option_1',  # place.origin_id
            1,  # legacy_id
            name,  # name
            None,  # multiplier
            None,  # min_amount
            None,  # max_amount
            None,  # sort
            False,  # deleted
            models.pg_time(OLD_UPDATED_AT),  # updated_at
        ),  # не было обновлено
        (
            2,  # id
            'option_1',  # brand.origin_id
            'option_group_2',  # group_origin_id
            'item_1',  # item_origin_id
            'option_2',  # place.origin_id
            1,  # legacy_id
            None,  # name
            None,  # multiplier
            None,  # min_amount
            None,  # max_amount
            200,  # sort
            False,  # deleted
            models.pg_time(UPDATED_AT),  # updated_at
        ),
    }
    assert sql_get_place_item_options(PLACE_ID) == expected_place_options


@pytest.mark.now(UPDATED_AT)
@pytest.mark.pgsql('eats_rest_menu_storage', files=[])
async def test_affect_row_second_time(
        update_menu_handler,
        place_menu_db,
        eats_rest_menu_storage,
        sql_get_brand_item_options,
        sql_get_place_item_options,
):
    """
    Проверяет, что если на вход erms приходят опции с одинаковым именем
    в рамках группы, они будут схлопнуты до одной
    (С максимальным updated_at)
    """

    db = place_menu_db(place_id=PLACE_ID, brand_id=BRAND_ID)
    category_id = db.add_category(
        models.PlaceMenuCategory(
            brand_menu_category_id='',
            place_id=PLACE_ID,
            origin_id=f'category_1',
            name='category_1',
        ),
    )
    db.add_item(
        category_id,
        models.PlaceMenuItem(
            place_id=PLACE_ID,
            brand_menu_item_id='',
            origin_id=f'item_1',
            name='item_1',
        ),
    )

    eats_rest_menu_storage.insert_brand_menu_item_options(
        [
            models.BrandMenuItemOption(
                brand_id=BRAND_ID, origin_id='1', name='frozen',
            ),
            models.BrandMenuItemOption(
                brand_id=BRAND_ID, origin_id='2', name='ready',
            ),
        ],
    )

    request_item = handler.UpdateItem(
        origin_id='item_1',
        name='name1',
        category_origin_ids=['category_1'],
        options_groups=[
            handler.UpdateOptionsGroup(
                legacy_id=1,
                origin_id='option_group_1',
                name='name_1',
                options=[
                    handler.UpdateOption(
                        origin_id='1',
                        name='frozen',
                        price='0.0',
                        updated_at=UPDATED_AT,
                    ),
                    handler.UpdateOption(
                        origin_id='2',
                        name='ready',
                        price='0.0',
                        updated_at=OLD_UPDATED_AT,
                    ),
                    handler.UpdateOption(
                        origin_id='3',
                        name='frozen',
                        price='0.0',
                        updated_at=OLD_UPDATED_AT,
                    ),
                    handler.UpdateOption(
                        origin_id='4',
                        name='ready',
                        price='0.0',
                        updated_at=UPDATED_AT,
                    ),
                ],
                updated_at=UPDATED_AT,
            ),
        ],
    )

    response = await update_menu_handler(
        place_id=PLACE_ID, categories=[], items=[request_item],
    )

    assert response.status_code == 200

    expected_brand_options = {
        (
            '1',  # origin_id
            'frozen',  # name
            1,  # multiplier
            None,  # min_amount
            None,  # max_amount
            None,  # sort
        ),
        (
            '2',  # origin_id
            'ready',  # name
            1,  # multiplier
            None,  # min_amount
            None,  # max_amount
            None,  # sort
        ),
    }
    assert sql_get_brand_item_options(BRAND_ID) == expected_brand_options

    expected_place_options = {
        (
            1,  # id
            '2',  # brand.origin_id
            'option_group_1',  # group_origin_id
            'item_1',  # item_origin_id
            '4',  # place.origin_id
            None,  # legacy_id
            None,  # name
            None,  # multiplier
            None,  # min_amount
            None,  # max_amount
            None,  # sort
            False,  # deleted
            models.pg_time(UPDATED_AT),  # updated_at
        ),
        (
            2,  # id
            '1',  # brand.origin_id
            'option_group_1',  # group_origin_id
            'item_1',  # item_origin_id
            '1',  # place.origin_id
            None,  # legacy_id
            None,  # name
            None,  # multiplier
            None,  # min_amount
            None,  # max_amount
            None,  # sort
            False,  # deleted
            models.pg_time(UPDATED_AT),  # updated_at
        ),
    }
    assert sql_get_place_item_options(PLACE_ID) == expected_place_options


@pytest.mark.now(UPDATED_AT)
@pytest.mark.pgsql('eats_rest_menu_storage', files=[])
async def test_same_origin_diff_name(
        update_menu_handler,
        place_menu_db,
        sql_get_brand_item_options,
        sql_get_place_item_options,
):
    """
    Проверяем, что опции с одним origin_id,
    но разным именем и группами корректно вставляются
    """

    db = place_menu_db(place_id=PLACE_ID, brand_id=BRAND_ID)
    category_id = db.add_category(
        models.PlaceMenuCategory(
            brand_menu_category_id='',
            place_id=PLACE_ID,
            origin_id=f'category_1',
            name='category_1',
        ),
    )
    db.add_item(
        category_id,
        models.PlaceMenuItem(
            place_id=PLACE_ID,
            brand_menu_item_id='',
            origin_id=f'item_1',
            name='item_1',
        ),
    )

    request_item = handler.UpdateItem(
        origin_id='item_1',
        name='name1',
        category_origin_ids=['category_1'],
        options_groups=[
            handler.UpdateOptionsGroup(
                legacy_id=1,
                origin_id='option_group_1',
                name='name_1',
                options=[
                    handler.UpdateOption(
                        origin_id='1', name='Соус', updated_at=UPDATED_AT,
                    ),
                ],
            ),
            handler.UpdateOptionsGroup(
                legacy_id=2,
                origin_id='option_group_2',
                name='name_2',
                options=[
                    handler.UpdateOption(
                        origin_id='1', name='Без соуса', updated_at=UPDATED_AT,
                    ),
                    handler.UpdateOption(
                        origin_id='3', name='Соус', updated_at=UPDATED_AT,
                    ),
                ],
                updated_at=UPDATED_AT,
            ),
        ],
    )

    response = await update_menu_handler(
        place_id=PLACE_ID, categories=[], items=[request_item],
    )

    assert response.status_code == 200

    expected_brand_options = {
        (
            '3',  # origin_id
            'Соус',  # name
            1,  # multiplier
            None,  # min_amount
            None,  # max_amount
            None,  # sort
        ),
        (
            '1',  # origin_id
            'Без соуса',  # name
            1,  # multiplier
            None,  # min_amount
            None,  # max_amount
            None,  # sort
        ),
    }
    assert sql_get_brand_item_options(BRAND_ID) == expected_brand_options

    expected_place_options = {
        (
            3,  # id
            '3',  # brand.origin_id
            'option_group_1',  # group_origin_id
            'item_1',  # item_origin_id
            '1',  # place.origin_id
            None,  # legacy_id
            None,  # name
            None,  # multiplier
            None,  # min_amount
            None,  # max_amount
            None,  # sort
            False,  # deleted
            models.pg_time(UPDATED_AT),  # updated_at
        ),
        (
            1,  # id
            '3',  # brand.origin_id
            'option_group_2',  # group_origin_id
            'item_1',  # item_origin_id
            '3',  # place.origin_id
            None,  # legacy_id
            None,  # name
            None,  # multiplier
            None,  # min_amount
            None,  # max_amount
            None,  # sort
            False,  # deleted
            models.pg_time(UPDATED_AT),  # updated_at
        ),
        (
            2,  # id
            '1',  # brand.origin_id
            'option_group_2',  # group_origin_id
            'item_1',  # item_origin_id
            '1',  # place.origin_id
            None,  # legacy_id
            None,  # name
            None,  # multiplier
            None,  # min_amount
            None,  # max_amount
            None,  # sort
            False,  # deleted
            models.pg_time(UPDATED_AT),  # updated_at
        ),
    }
    assert sql_get_place_item_options(PLACE_ID) == expected_place_options
