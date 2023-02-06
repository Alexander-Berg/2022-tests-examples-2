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
            "available": true,
            "id": "101",
            "categoryId": "103263",
            "name": "Продукт1",
            "price": 100.0,
            "vat": 0,
            "measure": 35.0,
            "measureUnit": "г",
            "sortOrder": 100,
            "modifierGroups": [],
            "images": [
                {
                    "url": "https://testing.eda.tst.yandex.net/images/1370147/36ca994761eb1fd00066ac634c96e0d1.jpg"
                }
            ],
            "thumbnails": [
                {
                    "url": "https://testing.eda.tst.yandex.net/images/1370147/36ca994761eb1fd00066ac634c96e0d1-80x80.jpg"
                }
            ]
        },
        {
            "available": true,
            "id": "102",
            "categoryId": "103263",
            "name": "Продукт2",
            "price": 100.0,
            "vat": 0,
            "measure": 35.0,
            "measureUnit": "г",
            "sortOrder": 100,
            "modifierGroups": [],
            "images": [
                {
                    "url": "https://testing.eda.tst.yandex.net/images/1370147/36ca994761eb1fd00066ac634c96e0d2.jpg"
                }
            ],
            "thumbnails": [
                {
                    "url": "https://testing.eda.tst.yandex.net/images/1370147/36ca994761eb1fd00066ac634c96e0d2-80x80.jpg"
                }
            ]
        },
        {
            "available": true,
            "id": "103",
            "categoryId": "103263",
            "name": "Продукт3",
            "price": 100.0,
            "vat": 0,
            "measure": 35.0,
            "measureUnit": "г",
            "sortOrder": 100,
            "modifierGroups": [],
            "images": [
                {
                    "url": "https://testing.eda.tst.yandex.net/images/1370147/36ca994761eb1fd00066ac634c96e0d3.jpg"
                }
            ],
            "thumbnails": [
                {
                    "url": "https://testing.eda.tst.yandex.net/images/1370147/36ca994761eb1fd00066ac634c96e0d3-80x80.jpg"
                }
            ]
        },
        {
            "available": true,
            "id": "104",
            "categoryId": "103263",
            "name": "Продукт4",
            "price": 100.0,
            "vat": 0,
            "measure": 35.0,
            "measureUnit": "г",
            "sortOrder": 100,
            "modifierGroups": [],
            "images": [
                {
                    "url": "https://testing.eda.tst.yandex.net/images/1370147/36ca994761eb1fd00066ac634c96e0d4.jpg"
                }
            ],
            "thumbnails": [
                {
                    "url": "https://testing.eda.tst.yandex.net/images/1370147/36ca994761eb1fd00066ac634c96e0d4-80x80.jpg"
                }
            ]
        },
        {
            "available": true,
            "id": "105",
            "categoryId": "103263",
            "name": "Продукт5",
            "price": 100.0,
            "vat": 0,
            "measure": 35.0,
            "measureUnit": "г",
            "sortOrder": 100,
            "modifierGroups": [],
            "images": [
                {
                    "url": "https://testing.eda.tst.yandex.net/images/1370147/36ca994761eb1fd00066ac634c96e0d5.jpg"
                }
            ],
            "thumbnails": [
                {
                    "url": "https://testing.eda.tst.yandex.net/images/1370147/36ca994761eb1fd00066ac634c96e0d5-80x80.jpg"
                }
            ]
        },
        {
            "available": true,
            "id": "106",
            "categoryId": "103263",
            "name": "Продукт6",
            "price": 100.0,
            "vat": 0,
            "measure": 35.0,
            "measureUnit": "г",
            "sortOrder": 100,
            "modifierGroups": [],
            "images": [
                {
                    "url": "https://testing.eda.tst.yandex.net/images/1370147/36ca994761eb1fd00066ac634c96e0d6.jpg"
                }
            ],
            "thumbnails": [
                {
                    "url": "https://testing.eda.tst.yandex.net/images/1370147/36ca994761eb1fd00066ac634c96e0d6-80x80.jpg"
                }
            ]
        },
        {
            "available": true,
            "id": "107",
            "categoryId": "103263",
            "name": "Продукт7",
            "price": 100.0,
            "vat": 0,
            "measure": 35.0,
            "measureUnit": "г",
            "sortOrder": 100,
            "modifierGroups": [],
            "images": [
                {
                    "url": "https://testing.eda.tst.yandex.net/images/1370147/36ca994761eb1fd00066ac634c96e0d7.jpg"
                }
            ],
            "thumbnails": [
                {
                    "url": "https://testing.eda.tst.yandex.net/images/1370147/36ca994761eb1fd00066ac634c96e0d7-80x80.jpg"
                }
            ]
        }
    ],
    "lastChange": "2021-08-20T13:47:28.48964+00:00"
}
'),
(109151, 'base_hash', '{"categories": [], "items": []}');

INSERT INTO eats_restapp_menu.menu_revisions(place_id, revision, base_revision, origin, status, menu_hash, created_at)
VALUES (109151, 'OTk5LjE1Nzc5MDk3MDEwMDAuWFla', 'base_revision_hash', 'user_generated', 'processing', 'some_hash', '2021-04-04T04:04:04.000+00:00'::TIMESTAMPTZ),
(109151, 'base_revision_hash', NULL, 'external', 'not_applicable', 'base_hash', '2021-04-04T04:04:04.000+00:00'::TIMESTAMPTZ);

INSERT INTO eats_restapp_menu.pictures(place_id, origin_id, avatarnica_identity, status)
VALUES
    (109151, '101', '1370147/36ca994761eb1fd00066ac634c96e0d1', 'uploaded'),
    (109151, '102', '1370147/36ca994761eb1fd00066ac634c96e0d2', 'moderation'),
    (109151, '103', '1370147/36ca994761eb1fd00066ac634c96e0d3', 'approved'),
    (109151, '104', '1370147/36ca994761eb1fd00066ac634c96e0d4', 'rejected'),
    (109151, '105', '1370147/36ca994761eb1fd00066ac634c96e0d5', 'deleted'),
    (109151, '106', '1370147/36ca994761eb1fd00066ac634c96e0d6', 'permanently_deleted');
