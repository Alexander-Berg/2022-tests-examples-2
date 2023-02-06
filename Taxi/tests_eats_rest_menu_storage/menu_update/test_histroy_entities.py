import pytest

from tests_eats_rest_menu_storage.menu_update import handler


HANDLER = '/internal/v1/update/menu'
BRAND_ID = 1
PLACE_ID = 1
NOW = '2021-03-30T12:55:00+00:00'


@pytest.mark.now(NOW)
@pytest.mark.pgsql('eats_rest_menu_storage', files=[])
async def test_history_items(
        update_menu_handler, place_menu_db, sql_get_place_menu_items,
):
    """
    Проверяет, что если приходят два
    айтема с одинаковым origin_id,
    возьмется тот, у которого нет
    deteled_at
    """

    place_menu_db(place_id=PLACE_ID, brand_id=BRAND_ID)

    response = await update_menu_handler(
        place_id=PLACE_ID,
        categories=[],
        items=[
            handler.UpdateItem(origin_id='item_1', name='item_1'),
            handler.UpdateItem(
                origin_id='item_1', name='deleted_item_1', deleted_at=NOW,
            ),
        ],
    )

    assert response.status_code == 200

    db_item = next(iter(sql_get_place_menu_items(PLACE_ID)))
    assert db_item[0] == 'item_1'  # origin_id
    assert db_item[2] == 'item_1'  # name
    assert not db_item[13]  # deleted
