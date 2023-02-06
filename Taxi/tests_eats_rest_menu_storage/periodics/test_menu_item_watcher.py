import datetime as dt

import pytest

from tests_eats_rest_menu_storage import models

BRAND_ID = 1
PLACE_ID = 1

UPDATED_AT = '2021-01-02T01:01:01.000+00:00'
CURSOR_UPDATED_AT = '2021-01-01T01:01:01.000+00:00'

LOCAL_TIMEZONE = dt.datetime.now(dt.timezone.utc).astimezone().tzinfo


@pytest.mark.parametrize(
    'stq_flag, stq_calls',
    [
        pytest.param(
            False,
            0,
            marks=pytest.mark.config(
                EATS_REST_MENU_STORAGE_MENU_UPDATER_SETTINGS={
                    'stq_enabled': False,
                },
            ),
            id='stq_disabled',
        ),
        pytest.param(
            True,
            1,
            marks=pytest.mark.config(
                EATS_REST_MENU_STORAGE_MENU_UPDATER_SETTINGS={
                    'stq_enabled': True,
                },
            ),
            id='stq_enabled',
        ),
        pytest.param(
            False,
            2,
            marks=pytest.mark.config(
                EATS_REST_MENU_STORAGE_MENU_UPDATER_SETTINGS={
                    'stq_enabled': True,
                    'items_watcher_limit': 1,
                },
            ),
            id='multiple_calls',
        ),
    ],
)
async def test_items_stq_task(
        taxi_eats_rest_menu_storage,
        stq,
        testpoint,
        sql_origin_id_uuid_mapping,
        place_menu_db,
        menu_item_watcher,
        stq_flag,
        stq_calls,
):
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
            place_id=PLACE_ID,
            brand_menu_item_id='',
            origin_id='item_origin_id_1',
            name='name1',
            deleted_at=models.DELETED_AT,
            updated_at=UPDATED_AT,
        ),
    )

    db.add_item(
        category_id=1,
        item=models.PlaceMenuItem(
            place_id=PLACE_ID,
            brand_menu_item_id='',
            origin_id='item_origin_id_2',
            name='name2',
            updated_at=UPDATED_AT,
        ),
    )

    menu_item_watcher.set(CURSOR_UPDATED_AT, 0)

    origin_id_uuid_mapping = sql_origin_id_uuid_mapping(
        table_name='place_menu_items',
    )

    print('HERE')
    print(origin_id_uuid_mapping['item_origin_id_2'])

    @testpoint('eats_rest_menu_storage::menu-item-watcher-periodic')
    def handle_finished(arg):
        pass

    await taxi_eats_rest_menu_storage.run_distlock_task('menu-item-watcher')
    assert handle_finished.has_calls

    assert (
        stq.eats_full_text_search_indexer_update_rest_place.times_called
        == stq_calls
    )

    if stq_flag:
        stq_call = (
            stq.eats_full_text_search_indexer_update_rest_place.next_call()
        )
        assert (
            stq_call['queue']
            == 'eats_full_text_search_indexer_update_rest_place'
        )
        assert stq_call['kwargs']['place_id'] == str(PLACE_ID)
        assert stq_call['kwargs']['deleted'] == [
            origin_id_uuid_mapping['item_origin_id_1'],
        ]
        assert stq_call['kwargs']['updated'] == [
            origin_id_uuid_mapping['item_origin_id_2'],
        ]


@pytest.mark.now('2022-01-01T12:00:00+00:00')
@pytest.mark.config(
    EATS_REST_MENU_STORAGE_LB_SETTINGS={
        'updated_menu_items_logging_enabled': True,
    },
)
async def test_log_updated_items(
        taxi_eats_rest_menu_storage,
        place_menu_db,
        testpoint,
        menu_item_watcher,
):
    """
    Проверяем, что обновленные блюда логируются в LB.
    """

    @testpoint('log-updated-menu-item')
    def log_item(data):
        def set_local_timezone(value):
            return (
                dt.datetime.fromisoformat(value)
                .astimezone(LOCAL_TIMEZONE)
                .isoformat()
            )

        assert data == {
            'doc': {
                'item_legacy_id': 1,
                'name': 'new item',
                'place_id': PLACE_ID,
                'updated_at': '2022-01-01T12:00:00+0000',
            },
            'timestamp': set_local_timezone('2022-01-01T15:00:00+03:00'),
        }

    category_origin_id = 'category_1'

    db = place_menu_db(place_id=PLACE_ID, brand_id=BRAND_ID)
    db.add_category(
        models.PlaceMenuCategory(
            brand_menu_category_id='',
            place_id=PLACE_ID,
            origin_id=category_origin_id,
            name='category_1',
        ),
    )

    db.add_item(
        category_id=1,
        item=models.PlaceMenuItem(
            place_id=PLACE_ID,
            brand_menu_item_id='',
            origin_id='item_1',
            legacy_id=1,
            name='new item',
            adult=False,
            updated_at=UPDATED_AT,
        ),
    )

    menu_item_watcher.set(CURSOR_UPDATED_AT, 0)

    await taxi_eats_rest_menu_storage.run_distlock_task('menu-item-watcher')

    assert log_item.times_called == 1
