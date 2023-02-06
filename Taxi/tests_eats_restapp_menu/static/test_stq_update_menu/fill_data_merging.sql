INSERT INTO eats_restapp_menu.menu_content(place_id, menu_hash, menu_json)
VALUES (109151, 'some_hash', '
{
    "categories": [
        {
            "id": "103263",
            "parentId": null,
            "name": "Завтрак",
            "sortOrder": 130,
            "reactivatedAt": null,
            "available": true
        },
        {
            "id": "103265",
            "parentId": null,
            "name": "Закуски",
            "sortOrder": 160,
            "reactivatedAt": null,
            "available": true
        }
    ],
    "items": [
        {
            "id": "1234583",
            "categoryId": "103263",
            "name": "Сухофрукты",
            "description": "",
            "price": 100,
            "vat": 0,
            "measure": 35,
            "measureUnit": "г",
            "sortOrder": 100,
            "modifierGroups": [],
            "images": [
                {
                    "url": "https://testing.eda.tst.yandex.net/images/1370147/36ca994761eb1fd00066ac634c96e0d9.jpg"
                }
            ],
            "thumbnails": [
                {
                    "url": "https://testing.eda.tst.yandex.net/images/1370147/36ca994761eb1fd00066ac634c96e0d9-80x80.jpg"
                }
            ],
            "reactivatedAt": "2021-08-13T21:00:00+00:00",
            "available": false,
            "menuItemId": 37660163
        },
        {
            "id": "1234595",
            "categoryId": "103263",
            "name": "Сметана 20%",
            "description": "",
            "price": 100,
            "vat": 0,
            "measure": 50,
            "measureUnit": "г",
            "sortOrder": 100,
            "modifierGroups": [],
            "images": [
                {
                    "url": "https://testing.eda.tst.yandex.net/images/1368744/9d2253f1d40f86ff4e525e998f49dfca.jpg"
                }
            ],
            "thumbnails": [
                {
                    "url": "https://testing.eda.tst.yandex.net/images/1368744/9d2253f1d40f86ff4e525e998f49dfca-80x80.jpg"
                }
            ],
            "available": true,
            "menuItemId": 37660168
        }
    ]
  }
'),
(109151, 'some_hash2', '
{
    "categories": [
        {
            "id": "103263",
            "parentId": null,
            "name": "Завтрак",
            "sortOrder": 130,
            "reactivatedAt": null,
            "available": true
        },
        {
            "id": "103265",
            "parentId": null,
            "name": "Закуски и прочее",
            "sortOrder": 160,
            "reactivatedAt": null,
            "available": true
        }
    ],
    "items": [
        {
            "id": "1234583",
            "categoryId": "103263",
            "name": "Сухофрукты",
            "description": "",
            "price": 123,
            "vat": 20,
            "measure": 35,
            "measureUnit": "г",
            "sortOrder": 100,
            "modifierGroups": [],
            "images": [
                {
                    "url": "https://testing.eda.tst.yandex.net/images/1370147/36ca994761eb1fd00066ac634c96e0d9.jpg"
                }
            ],
            "thumbnails": [
                {
                    "url": "https://testing.eda.tst.yandex.net/images/1370147/36ca994761eb1fd00066ac634c96e0d9-80x80.jpg"
                }
            ],
            "reactivatedAt": "2021-08-13T21:00:00+00:00",
            "available": false,
            "menuItemId": 37660163
        },
        {
            "id": "1234595",
            "categoryId": "103263",
            "name": "Сметана 20%",
            "description": "",
            "price": 100,
            "vat": 0,
            "measure": 50,
            "measureUnit": "г",
            "sortOrder": 100,
            "modifierGroups": [],
            "images": [
                {
                    "url": "https://testing.eda.tst.yandex.net/images/1368744/9d2253f1d40f86ff4e525e998f49dfca.jpg"
                }
            ],
            "thumbnails": [
                {
                    "url": "https://testing.eda.tst.yandex.net/images/1368744/9d2253f1d40f86ff4e525e998f49dfca-80x80.jpg"
                }
            ],
            "reactivatedAt": "2021-09-02T21:00:00+00:00",
            "available": false,
            "menuItemId": 37660168
        }
    ]
  }
');

INSERT INTO eats_restapp_menu.menu_revisions(place_id, revision, base_revision, author_id, origin, status, menu_hash, created_at)
VALUES
    (109151, 'OTk5LjE1Nzc5MDk3MDEwMDAuWFla', NULL, NULL, 'external', 'not_applicable', 'some_hash', '2021-01-01T04:04:04.000+00:00'::TIMESTAMPTZ),
    (109151, 'OTk5LjE1Nzc5MDk3MDEwMDAuWFlu', 'OTk5LjE1Nzc5MDk3MDEwMDAuWFla', 765, 'user_generated', 'processing', 'some_hash2', '2021-04-04T04:04:04.000+00:00'::TIMESTAMPTZ);
