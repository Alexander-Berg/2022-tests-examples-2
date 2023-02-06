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
                    "approved": false,
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
            "modifierGroups": [
                {
                    "id": "kzgxvz3g-lsesvny8wc-lrf53ugye5",
                    "name": "Q",
                    "modifiers": [
                        {
                            "id": "kzgxw1g6-ll5fwjou7v-u3bb2u2w88c",
                            "name": "W",
                            "price": "0",
                            "min_amount": 0,
                            "max_amount": 1,
                            "available": true,
                            "sort": 100,
                            "multiplier": 1
                        },
                        {
                            "id": "kzgxw3uo-bjjsuf6o7tc-guo5kqc3f4o",
                            "name": "E",
                            "price": "0",
                            "min_amount": 0,
                            "max_amount": 1,
                            "available": true,
                            "sort": 100,
                            "multiplier": 1
                        }
                    ],
                    "min_selected_options": 1,
                    "max_selected_options": 1,
                    "sort": 100,
                    "is_required": true
                },
                {
                    "id": "NOT_USED",
                    "name": "Kubik",
                    "modifiers": [
                        {
                            "id": "kzgxw1g6-ll5fwjou7v-u3bb2u2w88c",
                            "name": "W",
                            "price": "0",
                            "min_amount": 0,
                            "max_amount": 1,
                            "available": true,
                            "sort": 100,
                            "multiplier": 1
                        }                        
                    ],
                    "min_selected_options": 0,
                    "max_selected_options": 1,
                    "sort": 100,
                    "is_required": false
                }
            ],
            "images": [],
            "reactivatedAt": null,
            "available": true,
            "menuItemId": 37660168
        },
        {
            "id": "ku85h1at-6qral15uslr-f8qcpsdqyy",
            "categoryId": "ku85gpo2-bkcvawgl8ds-rnpvkubhjao",
            "name": "Салат осенний плюс",
            "description": "Салат, руккола, оливковое масло изменено",
            "price": 225.5,
            "vat": -1,
            "measure": 250.0,
            "measureUnit": "г",
            "sortOrder": 0,
            "modifierGroups": [],
            "images": [
                {
                    "approved": true,
                    "url": "https://testing.eda.tst.yandex.net/images/69745/27ea048fe061e09623c83aabaac8b618.jpeg"
                }
            ],
            "thumbnails": [
                {
                    "url": "https://testing.eda.tst.yandex.net/images/69745/27ea048fe061e09623c83aabaac8b618-80x80.jpeg"
                }
            ],
            "available": true,
            "menuItemId": 468437207,
            "nutrients": {
                "calories": "150",
                "proteins": "10",
                "fats": "10",
                "carbohydrates": "10",
                "is_deactivated": false
            }
        }
    ]
  }
');

INSERT INTO eats_restapp_menu.menu_revisions(place_id, revision, origin, status, menu_hash)
VALUES (109151, 'OTk5LjE1Nzc5MDk3MDEwMDAuWFla', 'user_generated', 'applied', 'same_hash');

INSERT INTO eats_restapp_menu.pictures(place_id, origin_id, avatarnica_identity, status)
VALUES
    (109151, '1234583', '1370147/36ca994761eb1fd00066ac634c96e0d9', 'moderation'),
    (109151, '1234595', '1368744/9d2253f1d40f86ff4e525e998f49dfca', 'moderation'),
    (109151, 'ku85h1at-6qral15uslr-f8qcpsdqyy', '69745/27ea048fe061e09623c83aabaac8b618', 'approved');
