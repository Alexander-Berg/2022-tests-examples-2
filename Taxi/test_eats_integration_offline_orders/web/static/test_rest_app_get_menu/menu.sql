INSERT INTO menu (place_id, menu, updates)
VALUES (
    '1',
    '{
        "items":{
          "menu_item_id__1": {
             "id": "menu_item_id__1", "category_id": "menu_category_id__1", "title": "Булочка", "price": "100.00", "description": "с изюмом"
          }
        },
        "categories": {"menu_category_id__1": {"id": "menu_category_id__1", "title": "Выпечка"}}
    }'::jsonb,
    '{
        "categories": { "menu_category_id__1":{"sort_order": 160}},
        "items": {
            "menu_item_id__1": {
                "original_avatar_image_id": "1/image",
                "vat": 10,
                "measure": 200.0,
                "measure_unit": "Грамм",
                "sort_order": 150,
                "restapp_image_ids": ["1/image1", "1/image2"],
                "nutrients": {
                    "calories": "1.0",
                    "proteins": "2.3",
                    "fats": "3.6",
                    "carbohydrates": "50"
                }
            }
        }
    }'::jsonb
),
(
    '2',
    '{
        "items":{
          "menu_item_id__1": {
             "id": "menu_item_id__1", "category_id": "menu_category_id__1", "title": "Булочка", "price": "100.00", "description": "с изюмом"
          }
        },
        "categories": {"menu_category_id__1": {"id": "menu_category_id__1", "title": "Выпечка"}}
    }'::jsonb,
    '{
        "items": {
            "menu_item_id__1": {
                "original_avatar_image_id": "1/image",
                "vat": 10,
                "measure": 200.0,
                "measure_unit": "Грамм",
                "sort_order": 150
            }
        }
    }'::jsonb
),
(
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
