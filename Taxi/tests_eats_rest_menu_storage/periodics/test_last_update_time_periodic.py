import datetime as dt

import pytest
import pytz

from tests_eats_rest_menu_storage import models


BRAND_ID = 1
PLACE_ID = 1
SLUG = 'slug1'

DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S%z'

CATEGORY_UPDATED_AT = dt.datetime(
    2021, 1, 1, 1, 1, 1, tzinfo=pytz.timezone('Europe/Moscow'),
)
ITEM_UPDATED_AT = dt.datetime(2021, 2, 2, 2, 2, 2, tzinfo=pytz.UTC)
INNER_OPTION_UPDATED_AT = dt.datetime(2021, 4, 4, 4, 4, 4, tzinfo=pytz.UTC)
OPTION_GROUP_UPDATED_AT = dt.datetime(
    2021, 9, 9, 9, 9, 9, tzinfo=pytz.timezone('Asia/Tokyo'),
)
OPTION_UPDATED_AT = dt.datetime(2021, 6, 6, 6, 6, 6, tzinfo=pytz.UTC)
STOCK_UPDATED_AT = dt.datetime(2021, 7, 7, 7, 7, 7, tzinfo=pytz.UTC)
CATEGORY_STATUS_UPDATED_AT = dt.datetime(
    2021, 10, 10, 10, 10, 11, tzinfo=pytz.timezone('Europe/Moscow'),
)
ITEM_STATUS_UPDATED_AT = dt.datetime(2021, 10, 10, 10, 11, 10, tzinfo=pytz.UTC)
OPTION_STATUS_UPDATED_AT = dt.datetime(
    2021, 11, 11, 10, 11, 12, tzinfo=pytz.timezone('Europe/Samara'),
)

PERIODIC = 'last-update-time-periodic'
METRIC = 'last_update_time_statistic'


def load_fixtures(eats_rest_menu_storage):
    # brands
    eats_rest_menu_storage.insert_brands([BRAND_ID, BRAND_ID + 1])

    # places
    eats_rest_menu_storage.insert_places(
        [models.Place(place_id=PLACE_ID, brand_id=BRAND_ID, slug=SLUG)],
    )

    # categories
    category_uuids = eats_rest_menu_storage.insert_brand_menu_categories(
        [
            models.BrandMenuCategory(
                brand_id=BRAND_ID,
                origin_id='category_origin_id_1',
                name='category_name_1',
            ),
            models.BrandMenuCategory(
                brand_id=(BRAND_ID + 1),
                origin_id='category_origin_id_2',
                name='category_name_2',
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
                updated_at=(
                    CATEGORY_UPDATED_AT - dt.timedelta(seconds=1)
                ).strftime(DATETIME_FORMAT),
            ),
            models.PlaceMenuCategory(
                brand_menu_category_id=category_uuids[
                    (BRAND_ID + 1, 'category_origin_id_2')
                ],
                place_id=PLACE_ID,
                origin_id='category_origin_id_2',
                updated_at=CATEGORY_UPDATED_AT.strftime(DATETIME_FORMAT),
            ),
        ],
    )

    # items
    item_uuids = eats_rest_menu_storage.insert_brand_menu_items(
        [
            models.BrandMenuItem(
                brand_id=BRAND_ID, origin_id='item_origin_id_1',
            ),
            models.BrandMenuItem(
                brand_id=BRAND_ID, origin_id='item_origin_id_2',
            ),
        ],
    )
    eats_rest_menu_storage.insert_place_menu_items(
        [
            models.PlaceMenuItem(
                place_id=PLACE_ID,
                brand_menu_item_id=item_uuids[(BRAND_ID, 'item_origin_id_1')],
                origin_id='item_origin_id_1',
                updated_at=ITEM_UPDATED_AT.strftime(DATETIME_FORMAT),
            ),
            models.PlaceMenuItem(
                place_id=PLACE_ID,
                brand_menu_item_id=item_uuids[(BRAND_ID, 'item_origin_id_2')],
                origin_id='item_origin_id_2',
                updated_at=(ITEM_UPDATED_AT - dt.timedelta(days=1)).strftime(
                    DATETIME_FORMAT,
                ),
            ),
        ],
    )

    # inner options
    inner_option_uuids = eats_rest_menu_storage.insert_brand_inner_options(
        [
            models.BrandMenuItemInnerOption(
                brand_id=BRAND_ID, origin_id='inner_option_origin_id_1',
            ),
            models.BrandMenuItemInnerOption(
                brand_id=BRAND_ID, origin_id='inner_option_origin_id_2',
            ),
        ],
    )
    eats_rest_menu_storage.insert_item_inner_options(
        [
            models.PlaceMenuItemInnerOption(
                brand_menu_item_inner_option=inner_option_uuids[
                    (BRAND_ID, 'inner_option_origin_id_1')
                ],
                place_menu_item_id=1,
                origin_id='inner_option_origin_id_1',
                updated_at=(
                    INNER_OPTION_UPDATED_AT - dt.timedelta(minutes=3)
                ).strftime(DATETIME_FORMAT),
            ),
            models.PlaceMenuItemInnerOption(
                brand_menu_item_inner_option=inner_option_uuids[
                    (BRAND_ID, 'inner_option_origin_id_2')
                ],
                place_menu_item_id=2,
                origin_id='inner_option_origin_id_2',
                updated_at=INNER_OPTION_UPDATED_AT.strftime(DATETIME_FORMAT),
            ),
        ],
    )

    # option groups
    option_group_uuids = eats_rest_menu_storage.insert_brand_option_groups(
        [
            models.BrandMenuItemOptionGroup(
                brand_id=BRAND_ID,
                origin_id='option_group_origin_id_1',
                name='option_group_name_1',
            ),
            models.BrandMenuItemOptionGroup(
                brand_id=BRAND_ID,
                origin_id='option_group_origin_id_2',
                name='option_group_name_2',
            ),
        ],
    )
    eats_rest_menu_storage.insert_item_option_groups(
        [
            models.PlaceMenuItemOptionGroup(
                brand_menu_item_option_group=option_group_uuids[
                    (BRAND_ID, 'option_group_origin_id_1')
                ],
                place_menu_item_id=1,
                origin_id='option_group_origin_id_1',
                updated_at=OPTION_GROUP_UPDATED_AT.strftime(DATETIME_FORMAT),
            ),
            models.PlaceMenuItemOptionGroup(
                brand_menu_item_option_group=option_group_uuids[
                    (BRAND_ID, 'option_group_origin_id_2')
                ],
                place_menu_item_id=2,
                origin_id='option_group_origin_id_2',
                updated_at=(
                    OPTION_GROUP_UPDATED_AT - dt.timedelta(minutes=10)
                ).strftime(DATETIME_FORMAT),
            ),
        ],
    )

    # options
    option_uuids = eats_rest_menu_storage.insert_brand_menu_item_options(
        [
            models.BrandMenuItemOption(
                brand_id=BRAND_ID,
                origin_id='option_origin_id_1',
                name='option_name_1',
            ),
            models.BrandMenuItemOption(
                brand_id=BRAND_ID,
                origin_id='option_origin_id_2',
                name='option_name_2',
            ),
        ],
    )
    eats_rest_menu_storage.insert_place_menu_item_options(
        [
            models.PlaceMenuItemOption(
                brand_menu_item_option=option_uuids[
                    (BRAND_ID, 'option_origin_id_1')
                ],
                place_menu_item_option_group_id=1,
                origin_id='option_origin_id_1',
                updated_at=(
                    OPTION_UPDATED_AT - dt.timedelta(hours=3)
                ).strftime(DATETIME_FORMAT),
            ),
            models.PlaceMenuItemOption(
                brand_menu_item_option=option_uuids[
                    (BRAND_ID, 'option_origin_id_2')
                ],
                place_menu_item_option_group_id=2,
                origin_id='option_origin_id_2',
                updated_at=OPTION_UPDATED_AT.strftime(DATETIME_FORMAT),
            ),
        ],
    )

    # stocks
    eats_rest_menu_storage.insert_place_menu_item_stocks(
        [
            models.PlaceMenuItemStock(
                place_menu_item_id=1,
                stock=10,
                updated_at=STOCK_UPDATED_AT.strftime(DATETIME_FORMAT),
            ),
            models.PlaceMenuItemStock(
                place_menu_item_id=2,
                stock=11,
                updated_at=(STOCK_UPDATED_AT - dt.timedelta(days=2)).strftime(
                    DATETIME_FORMAT,
                ),
            ),
        ],
    )

    # category statuses
    eats_rest_menu_storage.insert_category_statuses(
        [
            models.PlaceMenuCategoryStatus(
                place_menu_category_id=1,
                active=True,
                updated_at=(
                    CATEGORY_STATUS_UPDATED_AT - dt.timedelta(seconds=11)
                ).strftime(DATETIME_FORMAT),
            ),
            models.PlaceMenuCategoryStatus(
                place_menu_category_id=2,
                active=False,
                updated_at=CATEGORY_STATUS_UPDATED_AT.strftime(
                    DATETIME_FORMAT,
                ),
            ),
        ],
    )

    # item statuses
    eats_rest_menu_storage.insert_place_menu_item_statuses(
        [
            models.PlaceMenuItemStatus(
                place_menu_item_id=1,
                active=False,
                updated_at=ITEM_STATUS_UPDATED_AT.strftime(DATETIME_FORMAT),
            ),
            models.PlaceMenuItemStatus(
                place_menu_item_id=2,
                active=True,
                updated_at=(
                    ITEM_STATUS_UPDATED_AT - dt.timedelta(weeks=1)
                ).strftime(DATETIME_FORMAT),
            ),
        ],
    )

    # item option statuses
    eats_rest_menu_storage.insert_item_option_statuses(
        [
            models.PlaceMenuItemOptionStatus(
                place_menu_item_option_id=1,
                active=True,
                updated_at=OPTION_STATUS_UPDATED_AT.strftime(DATETIME_FORMAT),
            ),
            models.PlaceMenuItemOptionStatus(
                place_menu_item_option_id=2,
                active=False,
                updated_at=OPTION_STATUS_UPDATED_AT.strftime(DATETIME_FORMAT),
            ),
        ],
    )


@pytest.mark.config(
    EATS_REST_MENU_STORAGE_LAST_UPDATE_TIME_SETTINGS={
        'enabled': False,
        'period': 100,
    },
)
@pytest.mark.suspend_periodic_tasks(PERIODIC)
async def test_metric_storaging_disabled(
        eats_rest_menu_storage,
        testpoint,
        taxi_eats_rest_menu_storage,
        taxi_eats_rest_menu_storage_monitor,
):
    load_fixtures(eats_rest_menu_storage)

    @testpoint('eats_rest_menu_storage::last-update-time-periodic')
    def point(arg):
        pass

    await taxi_eats_rest_menu_storage.run_periodic_task(PERIODIC)
    metrics = await taxi_eats_rest_menu_storage_monitor.get_metrics()

    assert metrics[METRIC]['category_last_update_time'] == 0
    assert metrics[METRIC]['item_last_update_time'] == 0
    assert metrics[METRIC]['inner_option_last_update_time'] == 0
    assert metrics[METRIC]['option_group_last_update_time'] == 0
    assert metrics[METRIC]['option_last_update_time'] == 0
    assert metrics[METRIC]['stock_last_update_time'] == 0
    assert metrics[METRIC]['category_status_last_update_time'] == 0
    assert metrics[METRIC]['item_status_last_update_time'] == 0
    assert metrics[METRIC]['option_status_last_update_time'] == 0

    assert point.times_called == 0


@pytest.mark.config(
    EATS_REST_MENU_STORAGE_LAST_UPDATE_TIME_SETTINGS={
        'enabled': True,
        'period': 100,
    },
)
@pytest.mark.suspend_periodic_tasks(PERIODIC)
async def test_metric_storaging_enabled(
        eats_rest_menu_storage,
        taxi_eats_rest_menu_storage,
        taxi_eats_rest_menu_storage_monitor,
):
    load_fixtures(eats_rest_menu_storage)

    await taxi_eats_rest_menu_storage.run_periodic_task(PERIODIC)
    metrics = await taxi_eats_rest_menu_storage_monitor.get_metrics()

    assert (
        metrics[METRIC]['category_last_update_time']
        == CATEGORY_UPDATED_AT.timestamp()
    )
    assert (
        metrics[METRIC]['item_last_update_time'] == ITEM_UPDATED_AT.timestamp()
    )
    assert (
        metrics[METRIC]['inner_option_last_update_time']
        == INNER_OPTION_UPDATED_AT.timestamp()
    )
    assert (
        metrics[METRIC]['option_group_last_update_time']
        == OPTION_GROUP_UPDATED_AT.timestamp()
    )
    assert (
        metrics[METRIC]['option_last_update_time']
        == OPTION_UPDATED_AT.timestamp()
    )
    assert (
        metrics[METRIC]['stock_last_update_time']
        == STOCK_UPDATED_AT.timestamp()
    )
    assert (
        metrics[METRIC]['category_status_last_update_time']
        == CATEGORY_STATUS_UPDATED_AT.timestamp()
    )
    assert (
        metrics[METRIC]['item_status_last_update_time']
        == ITEM_STATUS_UPDATED_AT.timestamp()
    )
    assert (
        metrics[METRIC]['option_status_last_update_time']
        == OPTION_STATUS_UPDATED_AT.timestamp()
    )
