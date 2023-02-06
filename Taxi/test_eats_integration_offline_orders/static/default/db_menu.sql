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
            "image": null,
            "image_path": null
          },
          "menu_item_id__2": {
            "id": "menu_item_id__2",
            "category_id": "menu_category_id__1",
            "title": "Манник",
            "price": 900.9,
            "description": "Из манки",
            "volume": null,
            "weight": null,
            "image": "https://avatars.mds.yandex.net/get-inplace/6209012/2a0000018004509ad9687bd9d9539a01415e/orig",
            "image_path": "/get-inplace/6209012/2a0000018004509ad9687bd9d9539a01415e"
          }
        },
        "categories": {"menu_category_id__1": {"id": "menu_category_id__1", "title": "Десерты"}}
    }'::jsonb,
    '{
        "menu_item_id__2": {
          "image": "https://avatars.mds.yandex.net/get-inplace/6209012/2a0000018004509ad9687bd9d9539a01415e/orig",
          "image_path": "/get-inplace/6209012/2a0000018004509ad9687bd9d9539a01415e"
        }
    }'::jsonb
);
