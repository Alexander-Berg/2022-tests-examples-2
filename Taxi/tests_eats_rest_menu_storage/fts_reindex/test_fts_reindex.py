from tests_eats_rest_menu_storage import models

BRAND_ID = 1
PLACE_ID = 1


async def test_fts_reindex(taxi_eats_rest_menu_storage, stq, place_menu_db):
    """
    Проверяем что через stq задачу force_fts_update
    можно форсированно поставить задачи в
    очередь поиска на обновление
    """

    db = place_menu_db(BRAND_ID, PLACE_ID)
    category_id = db.add_category(
        models.PlaceMenuCategory(
            brand_menu_category_id='',
            place_id=PLACE_ID,
            origin_id='category_1',
            name='category_1',
        ),
    )

    item = models.PlaceMenuItem(
        place_id=PLACE_ID,
        brand_menu_item_id='',
        origin_id='item_1',
        name='item_1',
    )

    # deleted не будет отправлен
    deleted_item = models.PlaceMenuItem(
        place_id=PLACE_ID,
        brand_menu_item_id='',
        origin_id='item_2',
        name='item_2',
        deleted_at=models.DELETED_AT,
    )

    db.add_item(category_id, item)
    db.add_item(category_id, deleted_item)

    response = await taxi_eats_rest_menu_storage.post(
        '/admin/v1/fts-reindex', json={'place_ids': [str(PLACE_ID)]},
    )

    assert response.status == 200

    queue = stq.eats_full_text_search_indexer_update_rest_place

    kwargs = queue.next_call()['kwargs']
    assert kwargs['place_id'] == str(PLACE_ID)
    assert kwargs['updated'] == [item.brand_menu_item_id]


async def test_fts_reindex_fail(taxi_eats_rest_menu_storage):
    """
    Проверяет ошибку постановки задач
    """

    response = await taxi_eats_rest_menu_storage.post(
        '/admin/v1/fts-reindex', json={'place_ids': ['non_int_value']},
    )

    assert response.status == 400
