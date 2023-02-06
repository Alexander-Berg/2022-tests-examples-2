INSERT INTO eats_restapp_menu.menu_content(place_id, menu_hash, menu_json)
VALUES (109151, 'some_hash', '
{
    "categories": [
        {
            "id": "103263",
            "name": "Завтрак",
            "sortOrder": 130,
            "available": true
        },
        {
            "id": "103265",
            "name": "Закуски",
            "sortOrder": 160,
            "available": true
        }
    ],
    "items": [
        {
            "id": "1234583",
            "categoryId": "103263",
            "name": "Сухофрукты",
            "description": "",
            "price": 100.0,
            "vat": 0,
            "measure": 35.0,
            "measureUnit": "г",
            "sortOrder": 100,
            "modifierGroups": [],
            "images": [
                {
                    "url": "https://testing.eda.tst.yandex.net/images/1370147/36ca994761eb1fd00066ac634c96e0d9.jpg"
                }
            ],
            "available": false,
            "menuItemId": 37660163
        },
        {
            "id": "1234595",
            "categoryId": "103263",
            "name": "Сметана 20%",
            "description": "",
            "price": 100.0,
            "vat": 0,
            "measure": 50.0,
            "measureUnit": "г",
            "sortOrder": 100,
            "modifierGroups": [],
            "images": [
                {
                    "url": "https://testing.eda.tst.yandex.net/images/1368744/9d2253f1d40f86ff4e525e998f49dfca.jpg"
                }
            ],
            "available": false,
            "menuItemId": 37660168
        }
    ],
    "lastChange": "2021-08-20T13:47:28.48964+00:00"
}
'),
(109151, 'base_hash', '{"categories": [], "items": []}');

INSERT INTO eats_restapp_menu.menu_revisions(place_id, revision, base_revision, origin, status, menu_hash, created_at)
VALUES (109151, 'OTk5LjE1Nzc5MDk3MDEwMDAuWFla', 'base_revision_hash', 'user_generated', 'processing', 'some_hash', '2021-04-04T04:04:04.000+00:00'::TIMESTAMPTZ),
(109151, 'base_revision_hash', NULL, 'external', 'not_applicable', 'base_hash', '2021-04-04T04:04:04.000+00:00'::TIMESTAMPTZ);
