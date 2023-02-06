INSERT INTO menu (place_id, menu, updates)
VALUES (
    '3',
    '{
        "items":{
          "menu_item_id__1": {
             "id": "menu_item_id__1", "category_id": "menu_category_id__1", "title": "Булочка", "price": "100.00", "description": "с изюмом"
          }
        },
        "categories": {"menu_category_id__1": {"id": "menu_category_id__1", "title": "Выпечка"}}
    }'::jsonb,
    '{}'
)
       ;
