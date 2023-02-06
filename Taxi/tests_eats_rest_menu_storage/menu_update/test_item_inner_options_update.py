import datetime as dt

import psycopg2
import pytest
import pytz

from tests_eats_rest_menu_storage import models
from tests_eats_rest_menu_storage.menu_update import handler

HANDLER = '/internal/v1/update/menu'
BRAND_ID = 1
PLACE_ID = 1

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
    inner_options=[
        handler.UpdateInnerOption(
            name='new_inner_1',
            origin_id='inner_1',
            group_name='new_gn_inner_1',
            group_origin_id='new_go_inner_1',
            legacy_id=1,
            min_amount=1,
            max_amount=10,
            updated_at=UPDATED_AT,
        ),
        handler.UpdateInnerOption(
            name='inner_2',
            legacy_id=2,
            origin_id='inner_2',
            group_name='gn_inner_2',
            group_origin_id='go_inner_2',
            deleted_at='2021-01-11T11:58:46+00:00',
            updated_at=UPDATED_AT,
        ),
        handler.UpdateInnerOption(
            name='inner_3',
            origin_id='inner_3',
            group_name='gn_inner_3',
            group_origin_id='go_inner_3',
            legacy_id=3,
            updated_at=UPDATED_AT,
        ),
    ],
)


@pytest.mark.pgsql('eats_rest_menu_storage', files=[])
async def test_item_inner_options_update(
        update_menu_handler,
        place_menu_db,
        sql_get_brand_item_inner_options,
        sql_get_place_item_inner_options,
):
    """
    Проверяем обновление внутренних опций, изначально в
    базе 1 категория, 1 айтем  с 2 внутреннеми опциямм.
    Делаем запрос в котором обновляем айтем
    первую опцию переименовываем,
    вторую удаляем,
    третью добавляем
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

    db.add_inner_option(
        models.PlaceMenuItemInnerOption(
            brand_menu_item_inner_option='',
            place_menu_item_id=item_id,
            origin_id='inner_1',
            name='inner_1',
            group_name='gn_inner_1',
            group_origin_id='go_inner_1',
            legacy_id=1,
            min_amount=2,
            max_amount=20,
            updated_at=OLD_UPDATED_AT,
        ),
    )

    db.add_inner_option(
        models.PlaceMenuItemInnerOption(
            brand_menu_item_inner_option='',
            place_menu_item_id=item_id,
            origin_id='inner_2',
            legacy_id=2,
            name='inner_2',
            group_name='gn_inner_2',
            group_origin_id='go_inner_2',
            updated_at=OLD_UPDATED_AT,
        ),
    )

    response = await update_menu_handler(
        place_id=PLACE_ID, categories=[], items=[REQUEST_ITEM],
    )

    assert response.status_code == 200

    expected_brand_inner_options = set(
        [
            (
                'inner_3',  # origin_id
                'inner_3',  # name
                'gn_inner_3',  # group_name
                'go_inner_3',  # group_origin_id
                None,  # min_amount
                None,  # max_amount
            ),
            (
                'inner_2',  # origin_id
                'inner_2',  # name
                'gn_inner_2',  # group_name
                'go_inner_2',  # group_origin_id
                None,  # min_amount
                None,  # max_amount
            ),
            (
                'inner_1',  # origin_id
                'inner_1',  # name
                'gn_inner_1',  # group_name
                'go_inner_1',  # group_origin_id
                None,  # min_amount
                None,  # max_amount
            ),
        ],
    )
    actual_brand_inner_options = sql_get_brand_item_inner_options(BRAND_ID)
    assert actual_brand_inner_options == expected_brand_inner_options

    expected_place_inner_options = set(
        [
            (
                'inner_3',  # bmiio.origin_id
                1,  # place_menu_item_id
                'item_1',  # item.origin_id
                'inner_3',  # origin_id
                3,  # legacy_id
                None,  # name
                None,  # group_name
                None,  # group_origin_id
                None,  # min_amount
                None,  # max_amount
                False,  # is_deleted
                dt.datetime(
                    2021,
                    1,
                    1,
                    1,
                    1,
                    1,
                    tzinfo=psycopg2.tz.FixedOffsetTimezone(
                        offset=180, name=None,
                    ),
                ),
            ),  # запись появилась, все поля null, так как ссылаются на brand
            (
                'inner_2',  # bmiio.origin_id
                1,  # place_menu_item_id
                'item_1',  # item.origin_id
                'inner_2',  # origin_id
                2,  # legacy_id
                None,  # name
                None,  # group_name
                None,  # group_origin_id
                None,  # min_amount
                None,  # max_amount
                True,  # is_deleted
                dt.datetime(
                    2021,
                    1,
                    1,
                    1,
                    1,
                    1,
                    tzinfo=psycopg2.tz.FixedOffsetTimezone(
                        offset=180, name=None,
                    ),
                ),
            ),  # is_deleted == True
            (
                'inner_1',  # bmiio.origin_id
                1,  # place_menu_item_id
                'item_1',  # item.origin_id
                'inner_1',  # origin_id
                1,  # legacy_id
                'new_inner_1',  # name
                'new_gn_inner_1',  # group_name
                'new_go_inner_1',  # group_origin_id
                1,  # min_amount
                10,  # max_amount
                False,  # is_deleted
                dt.datetime(
                    2021,
                    1,
                    1,
                    1,
                    1,
                    1,
                    tzinfo=psycopg2.tz.FixedOffsetTimezone(
                        offset=180, name=None,
                    ),
                ),
            ),  # переименовались поля, обновились min_amount/max_amount
        ],
    )
    actual_place_inner_options = sql_get_place_item_inner_options(PLACE_ID)
    assert actual_place_inner_options == expected_place_inner_options


@pytest.mark.parametrize(
    'item_updated_at',
    [
        pytest.param(NEW_UPDATED_AT, id='database_item_outdated'),
        pytest.param(OLD_UPDATED_AT, id='request_item_outdated'),
    ],
)
async def test_update_with_compare_updated_at(
        update_menu_handler,
        place_menu_db,
        sql_get_place_item_inner_options,
        item_updated_at,
):
    """
    Тест проверяет, что внутрение опции не обновляются более старыми версиями
    вне зависимости от того, обновляется ли сам айтем или нет.
    Итого 8 вариантов: 2 варианта - айтем обновляется или нет,
    и 4 подварианта:
        0. В запросе поле updated_at пустое (поле опциональное)
        1. В запросе поле updated_at есть, но такой внутренней опции нет
        2. В запросе поле updated_at есть, и оно больше, чем у существующей
            внутренней опции
        3. В запросе поле updated_at есть, и оно меньше, чем у существующей
            внутренней опции
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
            updated_at=UPDATED_AT,
        ),
    )

    db.add_inner_option(
        models.PlaceMenuItemInnerOption(
            brand_menu_item_inner_option='',
            place_menu_item_id=item_id,
            origin_id='inner_1',
            name='inner_1',
            group_name='gn_inner_1',
            group_origin_id='go_inner_1',
            updated_at=UPDATED_AT,
        ),
    )
    db.add_inner_option(
        models.PlaceMenuItemInnerOption(
            brand_menu_item_inner_option='',
            place_menu_item_id=item_id,
            origin_id='inner_3',
            name='inner_3',
            group_name='gn_inner_3',
            group_origin_id='go_inner_3',
            updated_at=UPDATED_AT,
        ),
    )
    db.add_inner_option(
        models.PlaceMenuItemInnerOption(
            brand_menu_item_inner_option='',
            place_menu_item_id=item_id,
            origin_id='inner_4',
            name='inner_4',
            group_name='gn_inner_4',
            group_origin_id='go_inner_4',
            updated_at=UPDATED_AT,
        ),
    )

    request = handler.UpdateItem(
        origin_id='item_1',
        name='name1',
        adult=False,
        price='15.7',
        available=True,
        category_origin_ids=['category_1'],
        updated_at=item_updated_at,
        inner_options=[
            handler.UpdateInnerOption(
                name='inner_1',
                origin_id='inner_1',
                group_name='gn_inner_1',
                group_origin_id='go_inner_1',
            ),
            handler.UpdateInnerOption(
                name='inner_2',
                origin_id='inner_2',
                group_name='gn_inner_2',
                group_origin_id='go_inner_2',
                updated_at=UPDATED_AT_2,
            ),
            handler.UpdateInnerOption(
                name='inner_3',
                origin_id='inner_3',
                group_name='gn_inner_3',
                group_origin_id='go_inner_3',
                deleted_at=UPDATED_AT_3,
                updated_at=UPDATED_AT_3,
            ),
            handler.UpdateInnerOption(
                name='inner_4',
                origin_id='inner_4',
                group_name='gn_inner_4',
                group_origin_id='go_inner_4',
                deleted_at=UPDATED_AT_4,
                updated_at=UPDATED_AT_4,
            ),
        ],
    )

    response = await update_menu_handler(
        place_id=PLACE_ID, categories=[], items=[request],
    )

    assert response.status_code == 200

    actual_inner_options = sql_get_place_item_inner_options(PLACE_ID)
    assert len(actual_inner_options) == 4

    sorted_actual_inner_options = sorted(
        actual_inner_options, key=lambda x: x[0],
    )  # sorted by "origin_id" field
    # index 10 - deleted
    # index 11 - updated_at
    updated_at_1 = sorted_actual_inner_options[0][11]
    assert (
        dt.datetime.now(tz=pytz.timezone('Europe/Moscow')) - updated_at_1
    ).min < dt.timedelta(minutes=1)
    assert (
        sorted_actual_inner_options[1][11].strftime(DATETIME_FORMAT)
        == UPDATED_AT_2
    )
    assert (
        sorted_actual_inner_options[2][11].strftime(DATETIME_FORMAT)
        == UPDATED_AT_3
    )
    assert sorted_actual_inner_options[2][10] is True
    assert (
        sorted_actual_inner_options[3][11].strftime(DATETIME_FORMAT)
        == UPDATED_AT
    )
    assert sorted_actual_inner_options[3][10] is False


@pytest.mark.now(UPDATED_AT)
@pytest.mark.pgsql('eats_rest_menu_storage', files=[])
async def test_item_inner_options_update_with_same_name(
        update_menu_handler,
        place_menu_db,
        sql_get_brand_item_inner_options,
        sql_get_place_item_inner_options,
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

    option_name = 'inner_1'

    inner_option = models.PlaceMenuItemInnerOption(
        brand_menu_item_inner_option='',
        place_menu_item_id=item_id,
        origin_id='inner_1',
        name=option_name,
        group_name='group_name',
        group_origin_id='group_origin_id',
        legacy_id=1,
        min_amount=1,
        max_amount=10,
        updated_at=OLD_UPDATED_AT,
    )

    db.add_inner_option(inner_option)

    request_item = handler.UpdateItem(
        origin_id='item_1',
        name='name1',
        category_origin_ids=['category_1'],
        inner_options=[
            handler.UpdateInnerOption(
                name=option_name,
                origin_id='inner_2',
                group_name='group_name',
                group_origin_id='group_origin_id',
                legacy_id=1,
                min_amount=2,
                max_amount=20,
                updated_at=UPDATED_AT,
            ),
        ],
    )

    response = await update_menu_handler(
        place_id=PLACE_ID, categories=[], items=[request_item],
    )

    assert response.status_code == 200

    expected_brand_inner_options = set(
        [
            (
                'inner_1',  # origin_id
                option_name,  # name
                'group_name',  # group_name
                'group_origin_id',  # group_origin_id
                None,  # min_amount
                None,  # max_amount
            ),
        ],
    )
    actual_brand_inner_options = sql_get_brand_item_inner_options(BRAND_ID)
    assert actual_brand_inner_options == expected_brand_inner_options

    expected_place_inner_options = set(
        [
            (
                'inner_1',  # bmiio.origin_id
                1,  # place_menu_item_id
                'item_1',  # item.origin_id
                'inner_1',  # origin_id
                1,  # legacy_id
                'inner_1',  # name
                'group_name',  # group_name
                'group_origin_id',  # group_origin_id
                1,  # min_amount
                10,  # max_amount
                True,  # is_deleted
                models.pg_time(UPDATED_AT),  # updated_at
            ),
            (
                'inner_1',  # bmiio.origin_id
                1,  # place_menu_item_id
                'item_1',  # item.origin_id
                'inner_2',  # origin_id
                1,  # legacy_id
                None,  # name
                None,  # group_name
                None,  # group_origin_id
                2,  # min_amount
                20,  # max_amount
                False,  # is_deleted
                models.pg_time(UPDATED_AT),  # updated_at
            ),
        ],
    )
    actual_place_inner_options = sql_get_place_item_inner_options(PLACE_ID)

    assert actual_place_inner_options == expected_place_inner_options
