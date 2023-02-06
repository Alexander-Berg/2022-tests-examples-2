INSERT INTO menu (place_id, menu, updates)
VALUES (
    'place_id__1',
    '{
        "items":{
          "menu_item_id__1": {
             "id": "menu_item_id__1", "category_id": "menu_category_id__1",
             "title": "Булочка", "price": "100.00", "description": "с изюмом", "measure": "50", "measureUnit": "гр",
             "original_avatar_image_id": "2/img_id1", "refresh_image_hash": "0", "original_image_url": "some_first_url"
          },
        "menu_item_id__2": {
             "id": "menu_item_id__2", "category_id": "menu_category_id__1",
             "title": "Булочка", "price": "100.00", "description": "с изюмом", "measure": "50", "measureUnit": "гр",
             "original_avatar_image_id": "1/img_id0", "refresh_image_hash": "2", "original_image_url": "some_url"
          },
        "menu_item_id__3": {
             "id": "menu_item_id__3", "category_id": "menu_category_id__1",
             "title": "Булочка", "price": "100.00", "description": "с изюмом", "measure": "50", "measureUnit": "гр",
             "original_avatar_image_id": "2/img_id3", "refresh_image_hash": "0", "original_image_url": "some_other_url"
          },
        "menu_item_id__5": {
             "id": "menu_item_id__5", "category_id": "menu_category_id__1",
             "title": "Булочка", "price": "100.00", "description": "с изюмом", "measure": "50", "measureUnit": "гр",
             "original_avatar_image_id": "3/img_id4", "refresh_image_hash": "0", "original_image_url": "some_other_url"
          }
        },
        "categories": {"menu_category_id__1": {"id": "menu_category_id__1", "title": "Выпечка"}}
    }'::jsonb,
    '{}'
),
(
    'place_id__3',
    '{
        "items":{
          "menu_item_id__1": {
             "id": "menu_item_id__1", "category_id": "menu_category_id__1",
             "title": "Булочка", "price": "100.00", "description": "с изюмом", "measure": "50", "measureUnit": "г",
             "original_avatar_image_id": "1/img_id", "refresh_image_hash": "1", "original_image_url": "some_first_url"
          }
        },
        "categories": {"menu_category_id__1": {"id": "menu_category_id__1", "title": "Выпечка"}}
    }'::jsonb,
    '{}'
);
