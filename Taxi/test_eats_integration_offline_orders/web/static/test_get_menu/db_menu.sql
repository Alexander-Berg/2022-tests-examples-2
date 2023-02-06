INSERT INTO menu (place_id, menu, updates)
VALUES (
    'place_id__1',
    '{
        "items":{
          "menu_item_id__1": {
            "id": "menu_item_id__1",
            "category_id": "menu_category_id__1",
            "title": "Торт Наполеон",
            "price": 1000,
            "description": "Французский полководец",
            "volume": null,
            "weight": null,
            "original_avatar_image_id": "1/img_1"
          },
          "menu_item_id__2": {
            "id": "menu_item_id__2",
            "category_id": "menu_category_id__1",
            "title": "не манник",
            "price": 900.9,
            "description": "без никто",
            "volume": null,
            "weight": null,
            "original_avatar_image_id": "1/img_2"
          }
        },
        "categories": {"menu_category_id__1": {"id": "menu_category_id__1", "title": "Десерты"}}
    }'::jsonb,
    '{
        "items":{
            "menu_item_id__2": {
                "restapp_image_ids": ["1/img_3"],
                "title": "Манник",
                "description": "Из манки"
            }
        }
    }'::jsonb
);
