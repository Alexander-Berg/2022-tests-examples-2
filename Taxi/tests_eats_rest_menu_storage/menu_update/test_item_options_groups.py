import datetime as dt
import typing

import psycopg2
import psycopg2.tz
import pytest
import pytz

from tests_eats_rest_menu_storage import models
from tests_eats_rest_menu_storage.menu_update import handler

BRAND_ID = 1
PLACE_ID = 1

OLD_UPDATED_AT = '2020-01-01T01:01:01+0300'

UPDATED_AT = '2021-01-01T01:01:01+0300'
UPDATED_AT = '2021-01-01T01:01:01+0300'

NEW_UPDATED_AT = '2022-01-01T01:01:01+0300'
UPDATED_AT_2 = '2021-07-07T07:07:07+0300'
UPDATED_AT_3 = '2021-01-01T01:01:02+0300'
UPDATED_AT_4 = '2021-01-01T01:01:00+0300'
DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S%z'


@pytest.mark.parametrize(
    'update_items, brand_options_groups, place_options_groups',
    [
        pytest.param(
            [
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
                            name='option group name 1',
                            legacy_id=1,
                            sort=10,
                            updated_at=UPDATED_AT,
                        ),
                    ],
                ),
            ],
            {
                (
                    'option_group_1',  # origin_id
                    'option group name 1',  # name
                    None,  # min_selected_options
                    None,  # max_selected_options
                ),
            },
            {
                (
                    'option_group_1',  # brand_origin_id
                    'item_1',  # item_origin_id
                    'option_group_1',  # origin_id
                    False,  # is_required
                    1,  # legacy_id
                    None,  # name
                    10,  # sort
                    None,  # min_selected_options
                    None,  # max_selected_options
                    False,  # deleted
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
                ),
            },
            id='single options group',
        ),
        pytest.param(
            [
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
                            name='option group name 1',
                            legacy_id=1,
                            sort=10,
                            updated_at=UPDATED_AT,
                        ),
                    ],
                ),
                handler.UpdateItem(
                    origin_id='item_2',
                    name='name2',
                    adult=False,
                    price='15.7',
                    available=True,
                    category_origin_ids=['category_2'],
                    options_groups=[
                        handler.UpdateOptionsGroup(
                            origin_id='option_group_1',
                            name='option group name 1',
                            legacy_id=1,
                            sort=10,
                            updated_at=UPDATED_AT,
                        ),
                    ],
                ),
            ],
            {
                (
                    'option_group_1',  # origin_id
                    'option group name 1',  # name
                    None,  # min_selected_options
                    None,  # max_selected_options
                ),
            },
            {
                (
                    'option_group_1',  # brand_origin_id
                    'item_1',  # item_origin_id
                    'option_group_1',  # origin_id
                    False,  # is_required
                    1,  # legacy_id
                    None,  # name
                    10,  # sort
                    None,  # min_selected_options
                    None,  # max_selected_options
                    False,  # deleted
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
                ),
                (
                    'option_group_1',  # brand_origin_id
                    'item_2',  # item_origin_id
                    'option_group_1',  # origin_id
                    False,  # is_required
                    1,  # legacy_id
                    None,  # name
                    10,  # sort
                    None,  # min_selected_options
                    None,  # max_selected_options
                    False,  # deleted
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
                ),
            },
            id='single brand options group with multiple place groups',
        ),
    ],
)
async def test_options_groups_insert(
        update_menu_handler,
        place_menu_db,
        sql_get_brand_item_option_groups,
        sql_get_place_item_option_groups,
        update_items: typing.List[handler.UpdateItem],
        brand_options_groups: set,
        place_options_groups: set,
):
    place_menu_db(place_id=PLACE_ID, brand_id=BRAND_ID)
    response = await update_menu_handler(
        place_id=PLACE_ID, categories=[], items=update_items,
    )
    assert response.status_code == 200

    actual_brand_option_groups = sql_get_brand_item_option_groups(BRAND_ID)
    assert brand_options_groups == actual_brand_option_groups

    actual_place_option_groups = sql_get_place_item_option_groups(PLACE_ID)
    assert place_options_groups == actual_place_option_groups


async def test_options_groups_update(
        update_menu_handler,
        place_menu_db,
        sql_get_brand_item_option_groups,
        sql_get_place_item_option_groups,
):
    db = place_menu_db(place_id=PLACE_ID, brand_id=BRAND_ID)
    category_id = db.add_category(
        models.PlaceMenuCategory(
            brand_menu_category_id='',
            place_id=PLACE_ID,
            origin_id='category_1',
        ),
    )
    item_id = db.add_item(
        category_id,
        models.PlaceMenuItem(
            place_id=PLACE_ID,
            brand_menu_item_id='',
            origin_id='item_1',
            name='item 1',
        ),
    )
    db.add_option_group(
        models.PlaceMenuItemOptionGroup(
            brand_menu_item_option_group='',
            place_menu_item_id=item_id,
            origin_id='option_group_1',
            name='option group 1',
            sort=10,
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
                        name='new option group name 1',
                        is_required=True,
                        legacy_id=1,
                        sort=10,
                        updated_at=UPDATED_AT,
                    ),
                ],
            ),
        ],
    )
    assert response.status_code == 200

    # брендовые данные не должны были поменяться
    expected_brand_option_groups = {
        (
            'option_group_1',  # origin_id
            'option group 1',  # name
            None,  # min_selected_options
            None,  # max_selected_options
        ),
    }
    actual_brand_option_groups = sql_get_brand_item_option_groups(BRAND_ID)
    assert expected_brand_option_groups == actual_brand_option_groups

    # плейовые данные должны были обновиться
    expected_place_option_groups = {
        (
            'option_group_1',  # brand_origin_id
            'item_1',  # item_origin_id
            'option_group_1',  # origin_id
            True,  # is_required
            1,  # legacy_id
            'new option group name 1',  # name
            10,  # sort
            None,  # min_selected_options
            None,  # max_selected_options
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
    actual_place_option_groups = sql_get_place_item_option_groups(PLACE_ID)
    assert expected_place_option_groups == actual_place_option_groups


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
        sql_get_place_item_option_groups,
        item_updated_at,
):
    """
    Тест проверяет, что группы не обновляются более старыми версиями
    вне зависимости от того, обновляется ли сам айтем или нет.
    Итого 8 вариантов: 2 варианта - айтем обновляется или нет,
    и 4 подварианта:
        0. В запросе поле updated_at пустое (поле опциональное)
        1. В запросе поле updated_at есть, но такой группы нет
        2. В запросе поле updated_at есть, и оно больше, чем у существующей
            группы
        3. В запросе поле updated_at есть, и оно меньше, чему у существующей
            группы
    """

    db = place_menu_db(place_id=PLACE_ID, brand_id=BRAND_ID)
    category_id = db.add_category(
        models.PlaceMenuCategory(
            brand_menu_category_id='',
            place_id=PLACE_ID,
            origin_id='category_1',
        ),
    )
    item_id = db.add_item(
        category_id,
        models.PlaceMenuItem(
            place_id=PLACE_ID,
            brand_menu_item_id='',
            origin_id='item_1',
            name='item 1',
            updated_at=item_updated_at,
        ),
    )
    db.add_option_group(
        models.PlaceMenuItemOptionGroup(
            brand_menu_item_option_group='',
            place_menu_item_id=item_id,
            origin_id='option_group_1',
            name='option group name 1',
            sort=11,
            updated_at=UPDATED_AT,
        ),
    )
    db.add_option_group(
        models.PlaceMenuItemOptionGroup(
            brand_menu_item_option_group='',
            place_menu_item_id=item_id,
            origin_id='option_group_3',
            name='option group name 3',
            sort=13,
            updated_at=UPDATED_AT,
        ),
    )
    db.add_option_group(
        models.PlaceMenuItemOptionGroup(
            brand_menu_item_option_group='',
            place_menu_item_id=item_id,
            origin_id='option_group_4',
            name='option group name 4',
            sort=14,
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
                        name='option group name 1',
                        is_required=True,
                        legacy_id=1,
                        sort=11,
                    ),
                    handler.UpdateOptionsGroup(
                        origin_id='option_group_2',
                        name='option group name 2',
                        is_required=True,
                        legacy_id=1,
                        sort=12,
                        updated_at=UPDATED_AT_2,
                    ),
                    handler.UpdateOptionsGroup(
                        origin_id='option_group_3',
                        name='new option group name 3',
                        is_required=True,
                        legacy_id=1,
                        sort=13,
                        updated_at=UPDATED_AT_3,
                    ),
                    handler.UpdateOptionsGroup(
                        origin_id='option_group_4',
                        name='new option group name 4',
                        is_required=True,
                        legacy_id=1,
                        sort=14,
                        updated_at=UPDATED_AT_4,
                    ),
                ],
            ),
        ],
    )

    assert response.status_code == 200

    actual_option_groups = sql_get_place_item_option_groups(PLACE_ID)
    assert len(actual_option_groups) == 4

    sorted_actual_inner_options = sorted(
        actual_option_groups, key=lambda x: x[6],
    )  # sorted by "origin_id" field
    updated_at_1 = sorted_actual_inner_options[0][10]
    assert (
        dt.datetime.now(tz=pytz.timezone('Europe/Moscow')) - updated_at_1
    ).min < dt.timedelta(minutes=1)
    assert (
        sorted_actual_inner_options[1][10].strftime(DATETIME_FORMAT)
        == UPDATED_AT_2
    )
    assert (
        sorted_actual_inner_options[2][10].strftime(DATETIME_FORMAT)
        == UPDATED_AT_3
    )
    assert sorted_actual_inner_options[2][5] == 'new option group name 3'
    assert (
        sorted_actual_inner_options[3][10].strftime(DATETIME_FORMAT)
        == UPDATED_AT
    )
    assert sorted_actual_inner_options[3][5] == 'option group name 4'


@pytest.mark.now(UPDATED_AT)
@pytest.mark.pgsql('eats_rest_menu_storage', files=[])
async def test_item_option_group_update_with_same_name(
        update_menu_handler,
        place_menu_db,
        sql_get_brand_item_option_groups,
        sql_get_place_item_option_groups,
):
    """
    Проверяем что если пришла группа опций с таким же именем,
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

    name = 'group_1'

    group = models.PlaceMenuItemOptionGroup(
        brand_menu_item_option_group='',
        place_menu_item_id=item_id,
        legacy_id=1,
        origin_id='group_1',
        name=name,
        updated_at=OLD_UPDATED_AT,
    )

    db.add_option_group(group)

    request_item = handler.UpdateItem(
        origin_id='item_1',
        name='name1',
        category_origin_ids=['category_1'],
        options_groups=[
            handler.UpdateOptionsGroup(
                legacy_id=1,
                origin_id='group_2',
                name=name,
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
                'group_1',  # origin_id
                name,  # name
                None,  # min_selected_options
                None,  # max_selected_options
            ),
        ],
    )
    actual_brand_inner_options = sql_get_brand_item_option_groups(BRAND_ID)
    assert actual_brand_inner_options == expected_brand_inner_options

    expected_place_inner_options = set(
        [
            (
                'group_1',  # brand_origin_id
                'item_1',  # item_origin_id
                'group_1',  # origin_id
                False,  # is_required
                1,  # legacy_id
                name,  # name
                None,  # sort
                None,  # min_selected_options
                None,  # max_selected_options
                True,  # deleted
                models.pg_time(UPDATED_AT),  # updated_at
            ),
            (
                'group_1',  # brand_origin_id
                'item_1',  # item_origin_id
                'group_2',  # origin_id
                False,  # is_required
                1,  # legacy_id
                None,  # name
                None,  # sort
                None,  # min_selected_options
                None,  # max_selected_options
                False,  # deleted
                models.pg_time(UPDATED_AT),  # updated_at
            ),
        ],
    )
    actual_place_inner_options = sql_get_place_item_option_groups(PLACE_ID)

    assert actual_place_inner_options == expected_place_inner_options


@pytest.mark.now(UPDATED_AT)
@pytest.mark.pgsql('eats_rest_menu_storage', files=[])
async def test_item_option_group_change_brand_entity(
        update_menu_handler,
        place_menu_db,
        sql_get_brand_item_option_groups,
        sql_get_place_item_option_groups,
):
    """
    Проверяет случай, когда группа меняет ссылку на
    брендовую сущность.
    Изначально в бренде 1 группа с origin_1 и именем name_1
    Делаем первый запрос где создаем в плейсе
    группу с origin_2 и именем name_2. Эта граппа должна ссылаться
    на уже существующую группу.
    Посылаем запрос с origin_2 и именем name_2. Это должно создать
    новую бренд-сущность и привязать айтем к ней.
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
    item_id = db.add_item(
        category_id,
        models.PlaceMenuItem(
            place_id=PLACE_ID,
            brand_menu_item_id='',
            origin_id=f'item_1',
            name='item_1',
        ),
    )
    group = models.PlaceMenuItemOptionGroup(
        brand_menu_item_option_group='',
        place_menu_item_id=item_id,
        legacy_id=1,
        origin_id=f'origin_1',
        name=f'name_1',
        updated_at=OLD_UPDATED_AT,
    )
    db.add_option_group(group)

    for name in ('name_1', 'name_2'):
        request_item = handler.UpdateItem(
            origin_id='item_1',
            name='name1',
            category_origin_ids=['category_1'],
            options_groups=[
                handler.UpdateOptionsGroup(
                    legacy_id=2,
                    origin_id='origin_2',
                    name=name,
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
                'origin_1',  # origin_id
                'name_1',  # name
                None,  # min_selected_options
                None,  # max_selected_options
            ),
            (
                'origin_2',  # origin_id
                'name_2',  # name
                None,  # min_selected_options
                None,  # max_selected_options
            ),
        ],
    )
    actual_brand_inner_options = sql_get_brand_item_option_groups(BRAND_ID)
    assert actual_brand_inner_options == expected_brand_inner_options

    expected_place_inner_options = set(
        [
            (
                'origin_1',  # brand_origin_id
                'item_1',  # item_origin_id
                'origin_1',  # origin_id
                False,  # is_required
                1,  # legacy_id
                'name_1',  # name
                None,  # sort
                None,  # min_selected_options
                None,  # max_selected_options
                True,  # deleted
                models.pg_time(UPDATED_AT),  # updated_at
            ),
            (
                'origin_2',  # brand_origin_id
                'item_1',  # item_origin_id
                'origin_2',  # origin_id
                False,  # is_required
                2,  # legacy_id
                None,  # name
                None,  # sort
                None,  # min_selected_options
                None,  # max_selected_options
                False,  # deleted
                models.pg_time(UPDATED_AT),  # updated_at
            ),
        ],
    )
    actual_place_inner_options = sql_get_place_item_option_groups(PLACE_ID)

    assert actual_place_inner_options == expected_place_inner_options
