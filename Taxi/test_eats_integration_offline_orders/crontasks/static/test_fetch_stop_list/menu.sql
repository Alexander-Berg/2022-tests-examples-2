INSERT INTO menu (place_id, menu, stop_list)
VALUES (
    'place_id__1',
    '{
        "items":{
          "menu_item_id__1": {
             "id": "menu_item_id__1", "category_id": "menu_category_id__1", "title": "Булочка", "price": "100.00", "description": "с изюмом", "measure": "50", "measureUnit": "гр", "images": ["http://images-storage.com/image/1"]
          }
        },
        "categories": {"menu_category_id__1": {"id": "menu_category_id__1", "title": "Выпечка"}}
    }'::jsonb,
    '{}'::jsonb
);
