INSERT INTO eats_restapp_menu.menu_content(place_id, menu_hash, menu_json)
VALUES (109151, 'same_hash', '
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
                    "url": "https://testing.eda.tst.yandex.net/images/1370147/36ca994761eb1fd00066ac634c96e0d9.jpeg"
                }
            ],
            "thumbnails": [
                {
                    "url": "https://testing.eda.tst.yandex.net/images/1370147/36ca994761eb1fd00066ac634c96e0d9-80x80.jpeg"
                }
            ],
            "reactivatedAt": null,
            "available": true,
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
                    "url": "https://testing.eda.tst.yandex.net/images/1368744/9d2253f1d40f86ff4e525e998f49dfca.jpeg"
                }
            ],
            "thumbnails": [
                {
                    "url": "https://testing.eda.tst.yandex.net/images/1368744/9d2253f1d40f86ff4e525e998f49dfca-80x80.jpeg"
                }
            ],
            "reactivatedAt": null,
            "available": true,
            "menuItemId": 37660168
        }
    ]
  }
');

INSERT INTO eats_restapp_menu.menu_revisions(place_id, revision, origin, status, menu_hash)
VALUES (109151, 'OTk5LjE1Nzc5MDk3MDEwMDAuWFla', 'user_generated', 'applied', 'same_hash');
